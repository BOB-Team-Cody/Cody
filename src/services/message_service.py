"""
Message service for real-time workflow progress tracking.
"""

import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from threading import Lock
from collections import defaultdict

from ..models.analysis_models import RefactoringSession
from ..utils.logging_utils import setup_logger

logger = setup_logger(__name__)


class MessageService:
    """Service for managing real-time messages and session progress."""
    
    def __init__(self):
        """Initialize message service."""
        self._sessions: Dict[str, RefactoringSession] = {}
        self._session_messages: Dict[str, List[str]] = defaultdict(list)
        self._lock = Lock()
        logger.info("Message service initialized")
    
    def create_session(self, project_path: str) -> str:
        """Create a new refactoring session.
        
        Args:
            project_path: Path to the project being refactored
            
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        
        with self._lock:
            session = RefactoringSession(
                id=session_id,
                project_path=project_path,
                status="running",
                start_time=datetime.now().isoformat(),
                current_step="Initializing",
                progress_percentage=0
            )
            self._sessions[session_id] = session
            self._session_messages[session_id] = []
        
        logger.info(f"Created refactoring session: {session_id}")
        self.add_message(session_id, "🚀 Refactoring session started")
        return session_id
    
    def add_message(self, session_id: str, message: str) -> None:
        """Add a message to a session.
        
        Args:
            session_id: Session ID
            message: Message to add
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        with self._lock:
            if session_id in self._session_messages:
                self._session_messages[session_id].append(formatted_message)
                # Update session messages
                if session_id in self._sessions:
                    self._sessions[session_id].messages = self._session_messages[session_id].copy()
        
        logger.debug(f"Session {session_id}: {message}")
    
    def update_progress(self, session_id: str, step: str, progress: int) -> None:
        """Update session progress.
        
        Args:
            session_id: Session ID
            step: Current step description
            progress: Progress percentage (0-100)
        """
        with self._lock:
            if session_id in self._sessions:
                self._sessions[session_id].current_step = step
                self._sessions[session_id].progress_percentage = min(100, max(0, progress))
        
        self.add_message(session_id, f"📊 {step} ({progress}%)")
    
    def complete_session(self, session_id: str, success: bool = True) -> None:
        """Mark a session as completed.
        
        Args:
            session_id: Session ID
            success: Whether the session completed successfully
        """
        with self._lock:
            if session_id in self._sessions:
                self._sessions[session_id].status = "completed" if success else "failed"
                self._sessions[session_id].end_time = datetime.now().isoformat()
                self._sessions[session_id].progress_percentage = 100 if success else 0
        
        status_msg = "✅ Refactoring completed successfully" if success else "❌ Refactoring failed"
        self.add_message(session_id, status_msg)
        logger.info(f"Session {session_id} completed with status: {'success' if success else 'failure'}")
    
    def get_session(self, session_id: str) -> Optional[RefactoringSession]:
        """Get session information.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session information or None if not found
        """
        with self._lock:
            return self._sessions.get(session_id)
    
    def get_session_messages(self, session_id: str) -> List[str]:
        """Get all messages for a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            List of messages
        """
        with self._lock:
            return self._session_messages.get(session_id, []).copy()
    
    def get_latest_messages(self, session_id: str, since: int = 0) -> List[str]:
        """Get messages since a specific index.
        
        Args:
            session_id: Session ID
            since: Starting index (exclusive)
            
        Returns:
            List of new messages
        """
        with self._lock:
            messages = self._session_messages.get(session_id, [])
            return messages[since:] if since < len(messages) else []
    
    def cleanup_old_sessions(self, max_age_hours: int = 24) -> None:
        """Clean up old sessions.
        
        Args:
            max_age_hours: Maximum age in hours before cleanup
        """
        current_time = time.time()
        cutoff_time = current_time - (max_age_hours * 3600)
        
        with self._lock:
            sessions_to_remove = []
            for session_id, session in self._sessions.items():
                # Parse start time and check age
                try:
                    session_time = datetime.fromisoformat(session.start_time).timestamp()
                    if session_time < cutoff_time:
                        sessions_to_remove.append(session_id)
                except ValueError:
                    # Invalid timestamp, remove it
                    sessions_to_remove.append(session_id)
            
            for session_id in sessions_to_remove:
                del self._sessions[session_id]
                if session_id in self._session_messages:
                    del self._session_messages[session_id]
        
        if sessions_to_remove:
            logger.info(f"Cleaned up {len(sessions_to_remove)} old sessions")


# Global message service instance
message_service = MessageService()