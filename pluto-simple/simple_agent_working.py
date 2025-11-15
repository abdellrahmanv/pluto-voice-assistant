"""
🪐 Pluto Simple - WORKING VERSION
Fixed and tested for Raspberry Pi
"""

import speech_recognition as sr
import subprocess
import time
import os
import sys
from datetime import datetime

class Logger:
    """Dual output to console and log file"""
    def __init__(self, log_file):
        self.terminal = sys.stdout
        self.log = open(log_file, 'a', encoding='utf-8')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log.write(f"\n{'='*60}\n")
        self.log.write(f"🪐 NEW RUN: {timestamp}\n")
        self.log.write(f"{'='*60}\n")
        self.log.flush()
    
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()
    
    def flush(self):
        self.terminal.flush()
        self.log.flush()

class SimpleAgent:
    def __init__(self):
        print("🪐 Pluto Simple - Starting up...")
        
        # Find Piper model
        self.piper_model = self.find_piper_model()
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = None
        
        # Find working microphone
        self.find_microphone()
        
        self.state = "IDLE"
        self.name = "Pluto"
        
        print("✅ Pluto is ready!")
    
    def find_piper_model(self):
        """Find Piper model automatically"""
        paths = [
            "../models/en_US-lessac-medium.onnx",
            "models/en_US-lessac-medium.onnx",
            os.path.expanduser("~/.local/share/piper/voices/en_US-lessac-medium.onnx")
        ]
        
        for path in paths:
            if os.path.exists(path):
                print(f"✅ Found Piper at: {path}")
                return path
        
        print("⚠️  Piper model not found, will try system command")
        return "en_US-lessac-medium.onnx"  # Try system-wide
    
    def find_microphone(self):
        """Lock to USB card 3 for microphone"""
        print("🎤 Initializing USB card 3 for microphone...")
        
        try:
            # LOCK TO USB CARD 3 - Microphone
            self.microphone = sr.Microphone(device_index=3)
            print("✅ Microphone locked to USB card 3")
                
        except Exception as e:
            print(f"❌ Failed to initialize USB card 3: {e}")
            print("   Make sure your USB microphone is connected to card 3")
            # Fallback but still try to initialize
            self.microphone = sr.Microphone()
    
    def speak(self, text):
        """Speak using Piper on USB card 3 speakers"""
        print(f"🔊 Pluto: {text}")
        
        try:
            # Use Piper with USB card 3 for audio output
            cmd = f'echo "{text}" | piper --model {self.piper_model} --output-raw | aplay -D plughw:3,0 -r 22050 -f S16_LE -t raw - 2>/dev/null'
            result = subprocess.run(cmd, shell=True, timeout=10)
            
            if result.returncode != 0:
                # Fallback to espeak on USB card 3
                subprocess.run(f'espeak "{text}" --stdout | aplay -D plughw:3,0 2>/dev/null', shell=True)
        except:
            # Last resort fallback
            try:
                subprocess.run(f'espeak "{text}" --stdout | aplay -D plughw:3,0 2>/dev/null', shell=True)
            except:
                print("   (TTS unavailable)")
    
    def listen(self):
        """Listen for voice"""
        if not self.microphone:
            print("❌ No microphone available")
            return None
            
        try:
            with self.microphone as source:
                print("\n🎤 Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                
                try:
                    text = self.recognizer.recognize_google(audio)
                    print(f"👤 You: {text}")
                    return text.lower()
                except sr.UnknownValueError:
                    print("❌ Didn't catch that")
                    return None
                except sr.RequestError as e:
                    print(f"❌ Speech recognition error: {e}")
                    return None
        except sr.WaitTimeoutError:
            return None
        except Exception as e:
            print(f"❌ Listen error: {e}")
            return None
    
    def handle_scenario(self, user_input):
        """Handle scenarios"""
        if not user_input:
            return
        
        # Wake up
        if "hey pluto" in user_input or "hello pluto" in user_input:
            self.speak("Hey! I'm Pluto. How can I help you?")
        
        # Introduction
        elif "introduce" in user_input or "who are you" in user_input:
            self.speak("I'm Pluto, a simple voice assistant. I respond to commands like: what time is it, tell me a joke, or goodbye.")
        
        # Name
        elif "your name" in user_input:
            self.speak("My name is Pluto!")
        
        # Time
        elif "time" in user_input:
            current_time = time.strftime("%I:%M %p")
            self.speak(f"It's {current_time}")
        
        # Date
        elif "date" in user_input or "today" in user_input:
            current_date = time.strftime("%B %d")
            self.speak(f"Today is {current_date}")
        
        # How are you
        elif "how are you" in user_input:
            self.speak("I'm great! How are you?")
        
        # Joke
        elif "joke" in user_input:
            self.speak("Why did the robot cross the road? To charge its batteries on the other side!")
        
        # Help
        elif "help" in user_input:
            self.speak("Say: hey pluto, what time is it, tell me a joke, or goodbye")
        
        # Thanks
        elif "thank" in user_input:
            self.speak("You're welcome!")
        
        # Goodbye
        elif "bye" in user_input or "exit" in user_input:
            self.speak("Goodbye! See you later!")
            return "EXIT"
        
        # Unknown
        else:
            self.speak("I'm not sure about that. Say help to see what I can do.")
    
    def run(self):
        """Main loop"""
        print("\n" + "="*60)
        print("🪐 PLUTO SIMPLE - Say 'Hey Pluto' to start!")
        print("="*60 + "\n")
        
        self.speak("Hello! Say Hey Pluto to wake me up!")
        
        while True:
            try:
                user_input = self.listen()
                if user_input:
                    result = self.handle_scenario(user_input)
                    if result == "EXIT":
                        break
                time.sleep(0.3)
            except KeyboardInterrupt:
                print("\n\n⏸️  Stopping...")
                self.speak("Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(1)

if __name__ == "__main__":
    # Setup logging
    log_file = "pluto_run.log"
    sys.stdout = Logger(log_file)
    sys.stderr = sys.stdout
    
    print(f"📝 Logging to: {log_file}")
    print("   You can share this file to debug errors!\n")
    
    try:
        agent = SimpleAgent()
        agent.run()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        print("\n📋 Full error details:")
        traceback.print_exc()
        print("\n💡 Try:")
        print("   1. Run: chmod +x test_audio.sh && ./test_audio.sh")
        print("   2. Check internet connection (needed for speech recognition)")
        print("   3. Make sure microphone is connected")
        print(f"\n📝 Full log saved to: {log_file}")
