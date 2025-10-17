#!/usr/bin/env python3
"""
Performance Testing Script for Pluto Vision System
Tests vision worker performance, latency, and resource usage on Raspberry Pi
"""

import sys
import time
import queue
import psutil
import argparse
from pathlib import Path
from typing import Dict, List
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from workers.vision_worker import VisionWorker


class PerformanceTester:
    """Test vision system performance"""
    
    def __init__(self):
        self.results = {
            'vision_fps': [],
            'vision_latency_ms': [],
            'face_detection_count': 0,
            'false_positive_count': 0,
            'cpu_percent': [],
            'memory_mb': [],
            'test_duration_s': 0
        }
    
    def test_vision_performance(self, duration_seconds: int = 60):
        """Test vision worker for specified duration"""
        print("="*70)
        print("🧪 VISION SYSTEM PERFORMANCE TEST")
        print("="*70)
        print(f"\nTest duration: {duration_seconds} seconds")
        print("Starting vision worker...\n")
        
        vision_queue = queue.Queue()
        worker = VisionWorker(vision_queue)
        
        try:
            worker.start()
            time.sleep(2)  # Warmup
            
            start_time = time.time()
            last_frame_time = start_time
            frame_count = 0
            
            print("Monitoring performance metrics...")
            print("│ Time │ FPS │ Events │ CPU% │ Memory MB │ Status │")
            print("├──────┼─────┼────────┼──────┼───────────┼────────┤")
            
            while time.time() - start_time < duration_seconds:
                current_time = time.time()
                
                # Process events
                try:
                    event = vision_queue.get(timeout=0.1)
                    frame_count += 1
                    
                    # Calculate frame latency
                    if last_frame_time:
                        frame_latency = (current_time - last_frame_time) * 1000
                        self.results['vision_latency_ms'].append(frame_latency)
                    
                    last_frame_time = current_time
                    
                    # Count detections
                    if event['type'] == 'face_detected':
                        self.results['face_detection_count'] += 1
                    
                except queue.Empty:
                    pass
                
                # Sample system metrics every second
                if int(current_time - start_time) % 1 == 0:
                    elapsed = current_time - start_time
                    fps = frame_count / elapsed if elapsed > 0 else 0
                    self.results['vision_fps'].append(fps)
                    
                    cpu = psutil.cpu_percent(interval=0.1)
                    self.results['cpu_percent'].append(cpu)
                    
                    memory = psutil.Process().memory_info().rss / 1024 / 1024
                    self.results['memory_mb'].append(memory)
                    
                    # Print status
                    status = "🟢 Detecting" if self.results['face_detection_count'] > 0 else "⚪ Scanning"
                    print(f"│ {int(elapsed):4d}s│ {fps:4.1f}│   {self.results['face_detection_count']:4d}│ {cpu:5.1f}│   {memory:7.1f}│ {status:6s}│")
            
            self.results['test_duration_s'] = time.time() - start_time
            
        finally:
            worker.stop()
            print("├──────┴─────┴────────┴──────┴───────────┴────────┤")
            print("Vision worker stopped\n")
    
    def test_greeting_latency(self):
        """Test face detection to greeting latency"""
        print("\n" + "="*70)
        print("🎯 GREETING LATENCY TEST")
        print("="*70)
        print("\nThis test requires the full system running.")
        print("Please run: python run.py")
        print("\nThen measure time from face appearance to greeting.")
        print("Expected: 1-2 seconds\n")
    
    def print_results(self):
        """Print test results"""
        print("\n" + "="*70)
        print("📊 TEST RESULTS SUMMARY")
        print("="*70)
        
        if self.results['vision_fps']:
            avg_fps = sum(self.results['vision_fps']) / len(self.results['vision_fps'])
            min_fps = min(self.results['vision_fps'])
            max_fps = max(self.results['vision_fps'])
            print(f"\n📹 Vision FPS:")
            print(f"   Average: {avg_fps:.2f} fps")
            print(f"   Min: {min_fps:.2f} fps")
            print(f"   Max: {max_fps:.2f} fps")
            print(f"   ✅ Target: >4 fps {'PASS' if avg_fps > 4 else '❌ FAIL'}")
        
        if self.results['vision_latency_ms']:
            avg_latency = sum(self.results['vision_latency_ms']) / len(self.results['vision_latency_ms'])
            min_latency = min(self.results['vision_latency_ms'])
            max_latency = max(self.results['vision_latency_ms'])
            print(f"\n⏱️  Vision Latency:")
            print(f"   Average: {avg_latency:.1f} ms")
            print(f"   Min: {min_latency:.1f} ms")
            print(f"   Max: {max_latency:.1f} ms")
            print(f"   ✅ Target: <100ms {'PASS' if avg_latency < 100 else '❌ FAIL'}")
        
        print(f"\n👤 Face Detections:")
        print(f"   Total: {self.results['face_detection_count']}")
        
        if self.results['cpu_percent']:
            avg_cpu = sum(self.results['cpu_percent']) / len(self.results['cpu_percent'])
            max_cpu = max(self.results['cpu_percent'])
            print(f"\n💻 CPU Usage:")
            print(f"   Average: {avg_cpu:.1f}%")
            print(f"   Peak: {max_cpu:.1f}%")
            print(f"   ✅ Target: <30% {'PASS' if avg_cpu < 30 else '⚠️  HIGH'}")
        
        if self.results['memory_mb']:
            avg_mem = sum(self.results['memory_mb']) / len(self.results['memory_mb'])
            max_mem = max(self.results['memory_mb'])
            print(f"\n💾 Memory Usage:")
            print(f"   Average: {avg_mem:.1f} MB")
            print(f"   Peak: {max_mem:.1f} MB")
            print(f"   ✅ Target: <100MB {'PASS' if avg_mem < 100 else '⚠️  HIGH'}")
        
        print(f"\n⏳ Test Duration: {self.results['test_duration_s']:.1f} seconds")
        
        # Overall assessment
        print("\n" + "="*70)
        print("🎯 OVERALL ASSESSMENT")
        print("="*70)
        
        issues = []
        if self.results['vision_fps'] and avg_fps < 4:
            issues.append("❌ FPS below target (4 fps)")
        if self.results['vision_latency_ms'] and avg_latency >= 100:
            issues.append("❌ Latency above target (100ms)")
        if self.results['cpu_percent'] and avg_cpu >= 30:
            issues.append("⚠️  CPU usage high (>30%)")
        if self.results['memory_mb'] and avg_mem >= 100:
            issues.append("⚠️  Memory usage high (>100MB)")
        
        if not issues:
            print("\n✅ All metrics within target ranges!")
            print("   Vision system is performing optimally on this hardware.")
        else:
            print("\n⚠️  Issues found:")
            for issue in issues:
                print(f"   {issue}")
            print("\n💡 Recommendations:")
            if avg_fps < 4:
                print("   • Increase frame_skip in VISION_CONFIG")
                print("   • Reduce camera resolution (currently 320x240)")
            if avg_latency >= 100:
                print("   • Check system load (other processes)")
                print("   • Verify YuNet INT8 model is loaded")
            if avg_cpu >= 30:
                print("   • Increase frame_skip to reduce processing load")
                print("   • Check for background processes")
        
        print()
    
    def save_results(self, filename: str = "vision_test_results.json"):
        """Save results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"📁 Results saved to: {filename}")


def main():
    parser = argparse.ArgumentParser(description='Test Pluto vision system performance')
    parser.add_argument(
        '--duration', '-d',
        type=int,
        default=60,
        help='Test duration in seconds (default: 60)'
    )
    parser.add_argument(
        '--save', '-s',
        action='store_true',
        help='Save results to JSON file'
    )
    
    args = parser.parse_args()
    
    tester = PerformanceTester()
    
    # Run vision performance test
    tester.test_vision_performance(duration_seconds=args.duration)
    
    # Print results
    tester.print_results()
    
    # Save if requested
    if args.save:
        tester.save_results()
    
    # Show greeting latency test info
    tester.test_greeting_latency()


if __name__ == "__main__":
    main()
