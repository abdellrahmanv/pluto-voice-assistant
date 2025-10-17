"""
Agent State Manager
Manages the reflex agent's conversation states and transitions
"""

import time
from enum import Enum
from typing import Optional, Dict


class AgentState(Enum):
    """Agent states for reflex behavior"""
    IDLE = "idle"                          # No face detected, waiting
    FACE_DETECTED = "face_detected"        # Face seen, counting frames before lock
    LOCKED_IN = "locked_in"                # Locked onto a face, initiating greeting
    GREETING = "greeting"                  # Playing greeting message
    LISTENING = "listening"                # Waiting for user speech
    PROCESSING = "processing"              # LLM generating response
    RESPONDING = "responding"              # TTS playing response
    FACE_LOST = "face_lost"                # Locked face disappeared


class AgentStateManager:
    """Manages agent state transitions and behavior"""
    
    def __init__(self):
        """Initialize state manager"""
        self.current_state = AgentState.IDLE
        self.locked_face_id = None
        self.state_entry_time = time.time()
        self.conversation_count = 0
        self.total_interactions = 0
        
        # State transition history (for debugging)
        self.state_history = []
        self.max_history_len = 50
        
        print("🧠 Agent State Manager initialized")
        print(f"   Initial state: {self.current_state.value}")
        
    def transition(self, new_state: AgentState, reason: str = "") -> bool:
        """
        Transition to a new state
        
        Args:
            new_state: Target state
            reason: Reason for transition (for logging)
            
        Returns:
            True if transition was valid, False otherwise
        """
        # Check if transition is valid
        if not self._is_valid_transition(self.current_state, new_state):
            print(f"⚠️  Invalid state transition: {self.current_state.value} → {new_state.value}")
            return False
            
        # Log transition
        old_state = self.current_state
        self.current_state = new_state
        self.state_entry_time = time.time()
        
        # Add to history
        self.state_history.append({
            'from': old_state.value,
            'to': new_state.value,
            'timestamp': self.state_entry_time,
            'reason': reason
        })
        
        # Trim history
        if len(self.state_history) > self.max_history_len:
            self.state_history = self.state_history[-self.max_history_len:]
            
        # Log transition
        print(f"🔄 State: {old_state.value} → {new_state.value}")
        if reason:
            print(f"   Reason: {reason}")
            
        return True
        
    def _is_valid_transition(self, from_state: AgentState, to_state: AgentState) -> bool:
        """
        Check if state transition is valid
        
        Valid transitions:
        - IDLE → FACE_DETECTED (face appears)
        - FACE_DETECTED → LOCKED_IN (lock confirmed)
        - FACE_DETECTED → IDLE (false positive)
        - LOCKED_IN → GREETING (initiate conversation)
        - GREETING → LISTENING (greeting complete)
        - LISTENING → PROCESSING (speech detected)
        - PROCESSING → RESPONDING (LLM response ready)
        - RESPONDING → LISTENING (TTS complete, wait for next input)
        - Any state → FACE_LOST (face disappears)
        - FACE_LOST → IDLE (timeout expired)
        """
        valid_transitions = {
            AgentState.IDLE: [AgentState.FACE_DETECTED],
            AgentState.FACE_DETECTED: [AgentState.LOCKED_IN, AgentState.IDLE, AgentState.FACE_LOST],
            AgentState.LOCKED_IN: [AgentState.GREETING, AgentState.FACE_LOST],
            AgentState.GREETING: [AgentState.LISTENING, AgentState.FACE_LOST],
            AgentState.LISTENING: [AgentState.PROCESSING, AgentState.FACE_LOST],
            AgentState.PROCESSING: [AgentState.RESPONDING, AgentState.FACE_LOST],
            AgentState.RESPONDING: [AgentState.LISTENING, AgentState.FACE_LOST],
            AgentState.FACE_LOST: [AgentState.IDLE, AgentState.LOCKED_IN]  # Can recover
        }
        
        return to_state in valid_transitions.get(from_state, [])
        
    def lock_face(self, face_id: float) -> None:
        """
        Lock onto a face
        
        Args:
            face_id: Unique face identifier
        """
        self.locked_face_id = face_id
        self.total_interactions += 1
        print(f"🔒 Locked onto face ID: {face_id:.2f}")
        print(f"   Total interactions: {self.total_interactions}")
        
    def unlock_face(self) -> None:
        """Unlock current face"""
        if self.locked_face_id:
            print(f"🔓 Unlocked face ID: {self.locked_face_id:.2f}")
            self.locked_face_id = None
            self.conversation_count = 0
        
    def is_locked(self) -> bool:
        """Check if agent is locked onto a face"""
        return self.locked_face_id is not None
        
    def increment_conversation(self) -> None:
        """Increment conversation turn count"""
        self.conversation_count += 1
        
    def should_listen(self) -> bool:
        """
        Check if agent should be listening for speech
        
        Returns:
            True if agent should activate STT
        """
        return self.current_state in [
            AgentState.LISTENING,
            AgentState.PROCESSING,  # Keep listening during processing
        ]
        
    def should_greet(self) -> bool:
        """
        Check if agent should send greeting
        
        Returns:
            True if agent should greet
        """
        return self.current_state == AgentState.LOCKED_IN
        
    def time_in_state(self) -> float:
        """Get time spent in current state (seconds)"""
        return time.time() - self.state_entry_time
        
    def get_state_info(self) -> Dict:
        """
        Get current state information
        
        Returns:
            Dict with state details
        """
        return {
            'state': self.current_state.value,
            'locked': self.is_locked(),
            'locked_face_id': self.locked_face_id,
            'time_in_state': self.time_in_state(),
            'conversation_count': self.conversation_count,
            'total_interactions': self.total_interactions,
            'should_listen': self.should_listen(),
            'should_greet': self.should_greet()
        }
        
    def reset(self) -> None:
        """Reset to idle state"""
        print("🔄 Resetting agent state to IDLE")
        self.current_state = AgentState.IDLE
        self.unlock_face()
        self.state_entry_time = time.time()
        
    def __repr__(self) -> str:
        """String representation"""
        return f"AgentState({self.current_state.value}, locked={self.is_locked()})"
