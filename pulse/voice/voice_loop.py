"""
Voice interaction loop.
"""

import time
import threading
from pulse.core.brain import Brain
from pulse.config import PulseConfig
from pulse.voice.stt import WhisperSTT
from pulse.voice.tts import Pyttsx3TTS, ElevenLabsTTS

class VoiceLoop:
    """
    Manages the Listen -> Think -> Speak loop.
    """
    
    def __init__(self, brain: Brain, config: PulseConfig):
        self.brain = brain
        self.config = config
        self.running = False
        self.thread = None
        
        # Initialize engines
        print("Initializing Speech Engines...")
        self.stt = WhisperSTT(model_size=config.whisper_model_size)
        self.tts = None # Lazy init in loop for thread safety
            
        print(f"Voice ready. Wake words: {config.wake_words}")

    def start(self):
        """Start the voice loop in a background thread."""
        if self.running:
            return
        
        self.running = True
        self._run_loop()

    def stop(self):
        """Stop the voice loop."""
        self.running = False
        if self.thread:
            self.thread.join()

    def _run_loop(self):
        """Main interaction loop."""
        print("Creating Pulse Voice Loop...")
        
        print(f"Active wake words: {self.config.wake_words}")
        
        # Initialize TTS here to ensure it runs in the same thread as the loop
        if not self.tts:
            if self.config.tts_engine == "elevenlabs":
                self.tts = ElevenLabsTTS(api_key=self.config.elevenlabs_api_key)
            elif self.config.tts_engine == "system":
                from pulse.voice.tts import SystemTTS
                self.tts = SystemTTS()
            else:
                self.tts = Pyttsx3TTS()
        
        # Continuous conversation state
        conversation_active = False
        last_interaction_time = 0
        CONVERSATION_TIMEOUT = 20  # Seconds to keep listening after a response
        
        while self.running:
            try:
                # Decide whether to listen for wake word or just listen for command
                listen_directly = False
                
                if conversation_active:
                    # check timeout
                    if time.time() - last_interaction_time > CONVERSATION_TIMEOUT:
                        print("Conversation timed out. Waiting for wake word.")
                        conversation_active = False
                        self.tts.speak("I'll be here if you need me.", blocking=True)
                    else:
                        listen_directly = True
                
                if not listen_directly:
                    print("\nWaiting for wake word...")
                    if self.stt.listen_for_wake_words(self.config.wake_words):
                        print(f"Wake word detected!")
                        self.tts.speak("Yes?", blocking=True)
                        listen_directly = True
                        conversation_active = True
                        last_interaction_time = time.time()
                
                if listen_directly:
                    # Listen for command
                    print("Listening for command...")
                    user_command = self.stt.listen(timeout=10)
                    
                    if user_command:
                        print(f"User: {user_command}")
                        last_interaction_time = time.time() # Update interaction time
                        
                        # Check for exit commands
                        if user_command.lower() in ["stop", "exit", "bye", "goodbye", "sleep"]:
                            print("Ending conversation.")
                            self.tts.speak("Goodbye.", blocking=True)
                            conversation_active = False
                            continue

                        # Think & Speak
                        print("Pulse Thinking...")
                        # Use explicit system prompt for voice to keep responses focused
                        system_prompt = "You are Groot, a helpful voice assistant. Give brief, accurate, and direct answers. Keep responses conversational but precise. Avoid unnecessary elaboration."
                        response = self.brain.think(user_command, system_prompt=system_prompt)
                        print(f"Pulse: {response}")
                        
                        # Speak response (blocking to ensure it completes)
                        try:
                            self.tts.speak(response, blocking=True)
                        except Exception as e:
                            print(f"TTS Error: {e}")
                        
                        # Ready for next turn immediately
                        
                    else:
                        print("User: [no transcription captured]")
                        # Silence handling
                        if conversation_active:
                             # If we are in active conversation and hear nothing, 
                             # we might just wait (loop around) and check timeout.
                             # But let's verify if we should prompt or just silently wait.
                             # For now, silently wait until timeout.
                             pass
                        else:
                             # Should effectively not happen due to structure, but safety:
                             print("No command heard.")
                
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                self.stop()
                break
            except Exception as e:
                print(f"Error in voice loop: {e}")
                time.sleep(1)
