"""
Speech-to-Text (STT) implementation.
"""

import threading
from abc import ABC, abstractmethod
from typing import Optional

from pulse.exceptions import VoiceError


class STTEngine(ABC):
    """Abstract base class for STT engines."""
    
    @abstractmethod
    def listen(self, timeout: int = 5) -> str:
        """Listen for audio and return transcribed text."""
        pass
    
    @abstractmethod
    def listen_for_wake_words(self, wake_words: list) -> bool:
        """Listen continuously for wake words."""
        pass


class WhisperSTT(STTEngine):
    """
    Local STT using OpenAI's Whisper model.
    """
    
    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        self._model = None
        self._lock = threading.Lock()
        
        # Lazy loading of heavy dependencies
        self._speech_recognition = None
        self._recognizer = None
        self._microphone = None

    def _ensure_initialized(self):
        """Initialize resources if not already done."""
        if self._speech_recognition:
            return

        try:
            import speech_recognition as sr
            self._speech_recognition = sr
            self._recognizer = sr.Recognizer()
            self._microphone = sr.Microphone()
            
            # Adjust for ambient noise
            with self._microphone as source:
                self._recognizer.adjust_for_ambient_noise(source, duration=1)
                
        except ImportError:
            raise VoiceError("SpeechRecognition is not installed. Run: pip install SpeechRecognition pyaudio")
        except OSError as e:
            raise VoiceError(f"Microphone access failed: {e}. Is PyAudio installed?")

    def listen(self, timeout: int = 10) -> str:
        """Capture audio and transcribe using Whisper."""
        self._ensure_initialized()
        
        try:
            with self._microphone as source:
                print("Listening...")
                # phrase_time_limit prevents infinite listening
                audio = self._recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            
            print("Transcribing...")
            # Use recognize_whisper (requires openai-whisper package installed)
            text = self._recognizer.recognize_whisper(
                audio, 
                model=self.model_size,
            )
            text = text.strip()
            if text:
                print(f"Transcribed: {text}")
            else:
                print("Transcribed: [empty]")
            return text
            
        except self._speech_recognition.WaitTimeoutError:
            print("Transcribed: [timeout waiting for speech]")
            return ""
        except self._speech_recognition.UnknownValueError:
            print("Transcribed: [unrecognized audio]")
            return ""
        except Exception as e:
            print(f"STT Error: {e}")
            print("Transcribed: [failed]")
            return ""

    def listen_for_wake_words(self, wake_words: list) -> bool:
        """
        Simple wake word detection for multiple words.
        Uses Google Speech Recognition for speed, falls back to Whisper.
        """
        self._ensure_initialized()
        
        try:
            with self._microphone as source:
                print("Listening for wake word...")
                audio = self._recognizer.listen(source, timeout=2, phrase_time_limit=3)
            
            # fast path
            try:
                text = self._recognizer.recognize_google(audio)
            except:
                 # If google fails or returns nothing, just return False to keep loop tight
                 return False

            if text:
                print(f"Heard (Google): {text}")
                text_lower = text.lower()
                for word in wake_words:
                    if word.lower() in text_lower:
                        return True
        except Exception:
            pass
            
        return False
