"""
Conversation memory management with local SQLite storage.
Encryption support is included but optional if cryptography is not installed.
"""

import json
import sqlite3
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from pulse.exceptions import StorageError

try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


@dataclass
class Message:
    """Single message in a conversation."""
    role: str
    content: str
    timestamp: float = 0.0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        return cls(**data)


class Memory:
    """
    Persistent conversation memory backed by SQLite.
    Supports encryption for privacy if 'cryptography' package is installed.
    """

    def __init__(self, db_path: str, encryption_key: Optional[str] = None):
        self.db_path = db_path
        self.cipher = None
        
        # Setup encryption if key provided and lib available
        if encryption_key and CRYPTO_AVAILABLE:
            try:
                # Ensure key is valid base64 url-safe
                self.cipher = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)
            except Exception as e:
                print(f"Warning: Invalid encryption key, disabling encryption. Error: {e}")
        elif encryption_key and not CRYPTO_AVAILABLE:
            print("Warning: 'cryptography' module not found. Storage will be unencrypted.")

        self._init_db()

    def _init_db(self):
        """Initialize SQLite database schema."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        timestamp REAL NOT NULL,
                        metadata TEXT
                    )
                """)
                conn.commit()
        except sqlite3.Error as e:
            raise StorageError(f"Failed to initialize database: {e}")

    def _encrypt(self, text: str) -> str:
        """Encrypt text if cipher is available."""
        if self.cipher:
            return self.cipher.encrypt(text.encode()).decode()
        return text

    def _decrypt(self, text: str) -> str:
        """Decrypt text if cipher is available."""
        if self.cipher:
            try:
                return self.cipher.decrypt(text.encode()).decode()
            except Exception:
                return "[Decryption Failed]"
        return text

    def add(self, role: str, content: str, metadata: Dict[str, Any] = None) -> Message:
        """Add a message to memory."""
        msg = Message(role=role, content=content, metadata=metadata)
        
        try:
            encrypted_content = self._encrypt(msg.content)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO messages (role, content, timestamp, metadata) VALUES (?, ?, ?, ?)",
                    (
                        msg.role, 
                        encrypted_content, 
                        msg.timestamp, 
                        json.dumps(msg.metadata)
                    )
                )
                conn.commit()
            return msg
        except sqlite3.Error as e:
            raise StorageError(f"Failed to save message: {e}")

    def get_history(self, limit: int = 100) -> List[Message]:
        """Retrieve recent conversation history."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT role, content, timestamp, metadata FROM messages ORDER BY timestamp DESC LIMIT ?", 
                    (limit,)
                )
                rows = cursor.fetchall()
                
                messages = []
                for row in rows:
                    content = self._decrypt(row['content'])
                    metadata = json.loads(row['metadata']) if row['metadata'] else {}
                    messages.append(Message(
                        role=row['role'],
                        content=content,
                        timestamp=row['timestamp'],
                        metadata=metadata
                    ))
                # Return in chronological order for UI/context consumers
                return list(reversed(messages))
        except sqlite3.Error as e:
            raise StorageError(f"Failed to retrieve history: {e}")

    def get_context_string(self, limit: int = 50) -> str:
        """Get history formatted as a context string for LLM."""
        msgs = self.get_history(limit)
        return "\n".join([f"{m.role.upper()}: {m.content}" for m in msgs])

    def clear(self):
        """Clear all memory."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM messages")
                conn.commit()
        except sqlite3.Error as e:
            raise StorageError(f"Failed to clear memory: {e}")
