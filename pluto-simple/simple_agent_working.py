"""
🪐 Pluto Simple - WORKING VERSION
Fixed and tested for Raspberry Pi
"""

import speech_recognition as sr
import subprocess
import time
import os

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
        """Find a working microphone automatically"""
        print("🎤 Looking for microphone...")
        
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            
            # List all devices first
            device_found = False
            for i in range(p.get_device_count()):
                try:
                    info = p.get_device_info_by_index(i)
                    if info['maxInputChannels'] > 0:
                        print(f"   Found: [{i}] {info['name']}")
                        if not device_found:
                            # Use the first input device found
                            self.microphone = sr.Microphone(device_index=i)
                            print(f"✅ Using: [{i}] {info['name']}")
                            device_found = True
                except Exception as e:
                    continue
            
            p.terminate()
            
            if not device_found:
                print("⚠️  No input devices found, using default")
                self.microphone = sr.Microphone()
                
        except Exception as e:
            print(f"⚠️  PyAudio error: {e}, using default microphone")
            self.microphone = sr.Microphone()
    
    def speak(self, text):
        """Speak using Piper"""
        print(f"🔊 Pluto: {text}")
        
        try:
            # Try with Piper
            cmd = f'echo "{text}" | piper --model {self.piper_model} --output-raw | aplay -r 22050 -f S16_LE -t raw - 2>/dev/null'
            result = subprocess.run(cmd, shell=True, timeout=10)
            
            if result.returncode != 0:
                # Fallback to espeak
                subprocess.run(f'espeak "{text}"', shell=True)
        except:
            # Last resort fallback
            try:
                subprocess.run(f'espeak "{text}"', shell=True)
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
    try:
        agent = SimpleAgent()
        agent.run()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        print("\n💡 Try:")
        print("   1. Run: chmod +x test_audio.sh && ./test_audio.sh")
        print("   2. Check internet connection (needed for speech recognition)")
        print("   3. Make sure microphone is connected")
