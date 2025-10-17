"""
🪐 Project Pluto - Integration Tests
Test suite for voice assistant components
"""

import pytest
import queue
import time
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.config import AUDIO_CONFIG, QUEUE_CONFIG
from src.metrics_logger import MetricsLogger, PerformanceMetric


class TestMetricsLogger:
    """Test metrics collection and reporting"""
    
    def test_metric_creation(self):
        """Test creating performance metrics"""
        metric = PerformanceMetric(
            timestamp=time.time(),
            component='stt',
            metric_type='latency',
            value=150.0,
            unit='ms'
        )
        assert metric.component == 'stt'
        assert metric.value == 150.0
        
    def test_logger_initialization(self):
        """Test metrics logger setup"""
        logger = MetricsLogger(session_id="test_session")
        assert logger.session_id == "test_session"
        assert len(logger.metrics) == 0
        logger.close()
    
    def test_metric_logging(self):
        """Test logging metrics"""
        logger = MetricsLogger(session_id="test_metric_log")
        logger.log_metric('stt', 'latency', 100.0, 'ms')
        
        assert len(logger.metrics) == 1
        assert logger.metrics[0].value == 100.0
        logger.close()
    
    def test_statistics_calculation(self):
        """Test statistics computation"""
        logger = MetricsLogger(session_id="test_stats")
        
        logger.log_metric('stt', 'latency', 100.0, 'ms')
        logger.log_metric('stt', 'latency', 200.0, 'ms')
        logger.log_metric('stt', 'latency', 150.0, 'ms')
        
        stats = logger.get_statistics()
        
        assert 'stt' in stats
        assert 'latency' in stats['stt']
        assert stats['stt']['latency']['min'] == 100.0
        assert stats['stt']['latency']['max'] == 200.0
        assert stats['stt']['latency']['mean'] == 150.0
        
        logger.close()


class TestQueueCommunication:
    """Test queue-based worker communication"""
    
    def test_queue_creation(self):
        """Test queue initialization"""
        q = queue.Queue(maxsize=QUEUE_CONFIG["max_size"])
        assert q.empty()
        assert q.maxsize == QUEUE_CONFIG["max_size"]
    
    def test_queue_put_get(self):
        """Test basic queue operations"""
        q = queue.Queue()
        
        test_data = {'type': 'transcript', 'text': 'hello'}
        q.put(test_data)
        
        assert not q.empty()
        retrieved = q.get()
        assert retrieved == test_data
        assert q.empty()
    
    def test_queue_timeout(self):
        """Test queue timeout behavior"""
        q = queue.Queue()
        
        with pytest.raises(queue.Empty):
            q.get(timeout=0.1)
    
    def test_queue_full_behavior(self):
        """Test queue size limits"""
        q = queue.Queue(maxsize=2)
        
        q.put({'item': 1})
        q.put({'item': 2})
        
        # Queue should be full, this should timeout
        with pytest.raises(queue.Full):
            q.put({'item': 3}, timeout=0.1)


class TestWorkerMocks:
    """Test worker components with mocks"""
    
    @patch('src.workers.stt_worker.pyaudio.PyAudio')
    @patch('src.workers.stt_worker.Model')
    def test_stt_worker_initialization(self, mock_model, mock_pyaudio):
        """Test STT worker setup with mocks"""
        from src.workers.stt_worker import STTWorker
        
        output_q = queue.Queue()
        worker = STTWorker(output_q)
        
        assert worker.output_queue == output_q
        assert not worker.running
        assert worker.processing_count == 0
    
    @patch('requests.get')
    def test_llm_worker_server_check(self, mock_get):
        """Test LLM worker server connectivity check"""
        from src.workers.llm_worker import LLMWorker
        
        # Mock successful server response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'models': [{'name': 'qwen2.5:1.5b-instruct-q4_k_M'}]
        }
        mock_get.return_value = mock_response
        
        input_q = queue.Queue()
        output_q = queue.Queue()
        worker = LLMWorker(input_q, output_q)
        
        assert worker.initialize()
    
    @patch('subprocess.run')
    def test_tts_worker_piper_check(self, mock_run):
        """Test TTS worker Piper binary check"""
        from src.workers.tts_worker import TTSWorker
        
        # Mock successful Piper version check
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "1.0.0"
        mock_run.return_value = mock_result
        
        input_q = queue.Queue()
        worker = TTSWorker(input_q)
        
        assert worker.processing_count == 0


class TestPipelineFlow:
    """Test end-to-end pipeline flow"""
    
    def test_stt_to_llm_flow(self):
        """Test data flow from STT to LLM queue"""
        stt_to_llm = queue.Queue()
        
        # Simulate STT output
        transcript = {
            'type': 'transcript',
            'text': 'hello world',
            'timestamp': time.time(),
            'latency_ms': 150
        }
        stt_to_llm.put(transcript)
        
        # Simulate LLM retrieval
        received = stt_to_llm.get()
        
        assert received['type'] == 'transcript'
        assert received['text'] == 'hello world'
        assert 'latency_ms' in received
    
    def test_llm_to_tts_flow(self):
        """Test data flow from LLM to TTS queue"""
        llm_to_tts = queue.Queue()
        
        # Simulate LLM output
        response = {
            'type': 'response',
            'text': 'Hello! How can I help you?',
            'timestamp': time.time(),
            'latency_ms': 850
        }
        llm_to_tts.put(response)
        
        # Simulate TTS retrieval
        received = llm_to_tts.get()
        
        assert received['type'] == 'response'
        assert 'Hello' in received['text']
        assert 'latency_ms' in received
    
    def test_full_pipeline_simulation(self):
        """Test complete pipeline simulation"""
        stt_to_llm = queue.Queue()
        llm_to_tts = queue.Queue()
        
        # Stage 1: STT produces transcript
        stt_to_llm.put({'type': 'transcript', 'text': 'test query'})
        
        # Stage 2: LLM processes and produces response
        transcript = stt_to_llm.get()
        assert transcript['text'] == 'test query'
        
        llm_to_tts.put({'type': 'response', 'text': 'test response'})
        
        # Stage 3: TTS receives response
        response = llm_to_tts.get()
        assert response['text'] == 'test response'
        
        # All queues should be empty
        assert stt_to_llm.empty()
        assert llm_to_tts.empty()


class TestConfigurationValidation:
    """Test configuration settings"""
    
    def test_audio_config(self):
        """Test audio configuration values"""
        assert AUDIO_CONFIG["sample_rate"] == 16000
        assert AUDIO_CONFIG["channels"] == 1
        assert AUDIO_CONFIG["chunk_size"] > 0
        assert AUDIO_CONFIG["energy_threshold"] > 0
    
    def test_queue_config(self):
        """Test queue configuration"""
        assert QUEUE_CONFIG["max_size"] >= 10
        assert QUEUE_CONFIG["get_timeout"] > 0


class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_empty_queue_handling(self):
        """Test handling empty queue"""
        q = queue.Queue()
        
        try:
            q.get(timeout=0.1)
            assert False, "Should raise queue.Empty"
        except queue.Empty:
            pass  # Expected
    
    def test_metric_with_missing_data(self):
        """Test metric creation with minimal data"""
        metric = PerformanceMetric(
            timestamp=time.time(),
            component='test',
            metric_type='test_metric',
            value=0.0,
            unit='test'
        )
        assert metric is not None


# Test runner
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
