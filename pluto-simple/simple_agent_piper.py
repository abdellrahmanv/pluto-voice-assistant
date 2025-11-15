"""
🪐 Pluto Simple - With Piper TTS (NATURAL OFFLINE VOICE)
Natural human voice without internet!
Uses the same Piper TTS as full Pluto
"""

try:
    import speech_recognition as sr
except ImportError:
    print("❌ ERROR: SpeechRecognition not installed!")
    print("   Run: sudo ./setup_pi.sh")
    exit(1)

import subprocess
import time
import os

class SimpleAgent:
    def __init__(self):
        # Initialize STT
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Piper model path - check multiple locations
        possible_paths = [
            "../models/en_US-lessac-medium.onnx",  # In models/ directly
            "../models/piper/en_US-lessac-medium.onnx",  # In models/piper/
            "models/en_US-lessac-medium.onnx",
            "models/piper/en_US-lessac-medium.onnx",
            os.path.expanduser("~/.local/share/piper/voices/en_US-lessac-medium.onnx"),
            "en_US-lessac-medium.onnx"
        ]
        
        self.piper_model = None
        for path in possible_paths:
            if os.path.exists(path):
                self.piper_model = path
                print(f"✅ Found Piper model at: {path}")
                break
        
        if not self.piper_model:
            print("❌ Could not find Piper model!")
            print("   Looked in:")
            for path in possible_paths:
                print(f"     - {path}")
            print("\n   Make sure you have Piper model from main Pluto!")
            exit(1)
        
        # Scenario states
        self.state = "IDLE"
        self.name = "Pluto"
        
        print("🪐 Pluto Simple Agent Initialized (Piper TTS - Natural Voice)")
    
    def speak(self, text):
        """Text to speech using Piper (natural offline voice!)"""
        print(f"🔊 Pluto: {text}")
        try:
            # Use Piper TTS (same as full Pluto)
            cmd = f'echo "{text}" | piper --model {self.piper_model} --output-raw | aplay -r 22050 -f S16_LE -t raw -'
            subprocess.run(cmd, shell=True, check=True, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"❌ TTS Error: {e}")
            print("   Make sure Piper is installed and model exists")
    
    def listen(self):
        """Listen for voice input"""
        with self.microphone as source:
            print("\n🎤 Listening...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                text = self.recognizer.recognize_google(audio)
                print(f"👤 You said: {text}")
                return text.lower()
            except sr.WaitTimeoutError:
                return None
            except sr.UnknownValueError:
                print("❌ Could not understand audio")
                return None
            except Exception as e:
                print(f"❌ Error: {e}")
                return None
    
    def handle_scenario(self, user_input):
        """Handle different conversation scenarios"""
        
        if not user_input:
            return
        
        # Scenario 1: Wake up / Greeting
        if "hey pluto" in user_input or "hello pluto" in user_input:
            self.state = "GREETED"
            self.speak("Hey, I'm Pluto—an AI-powered welcoming robot. How can I assist you today?")
        
        # Scenario 2: Introduction
        elif "introduce yourself" in user_input or "who are you" in user_input:
            self.speak(f"I'm {self.name}, a scenario-based voice assistant. "
                      "I can respond to specific voice commands. "
                      "I don't use complex AI, just simple pattern matching. "
                      "Try saying things like: what time is it, tell me a joke, or goodbye!")
        
        # Scenario 3: What's your name
        elif "what is your name" in user_input or "your name" in user_input:
            self.speak(f"My name is {self.name}. Nice to meet you!")
        
        # Scenario 4: Time
        elif "time" in user_input:
            current_time = time.strftime("%I:%M %p")
            self.speak(f"The current time is {current_time}")
        
        # Scenario 5: Date
        elif "date" in user_input or "today" in user_input:
            current_date = time.strftime("%B %d, %Y")
            self.speak(f"Today is {current_date}")
        
        # Scenario 6: How are you
        elif "how are you" in user_input:
            self.speak("I'm doing great! Thanks for asking. How are you?")
        
        # Scenario 7: Tell a joke
        elif "joke" in user_input:
            self.speak("Why did the robot go on a diet? Because it had too many bytes!")
        
        # Scenario 8: Weather (mock)
        elif "weather" in user_input:
            self.speak("I don't have access to real weather data, but I hope it's nice where you are!")
        
        # Scenario 9: Help
        elif "help" in user_input or "what can you do" in user_input:
            self.speak("I can tell you the time, date, jokes, and respond to greetings. "
                      "Try saying: what time is it, introduce yourself, tell me a joke, or goodbye.")
        
        # Scenario 10: Thank you
        elif "thank you" in user_input or "thanks" in user_input:
            self.speak("You're welcome! Happy to help!")
        
        # Scenario 11: Goodbye
        elif "goodbye" in user_input or "bye" in user_input or "exit" in user_input:
            self.speak("Goodbye! It was nice talking to you. See you later!")
            return "EXIT"
        
        # Unknown command
        else:
            self.speak("I'm not sure how to respond to that. Try saying 'help' to see what I can do.")
    
    def run(self):
        """Main loop"""
        print("\n" + "="*60)
        print("🪐 PLUTO SIMPLE - Natural Voice Edition (Piper TTS)")
        print("="*60)
        self.speak("Hello! Say 'Hey Pluto' to wake me up!")
        print("\n💡 Try saying: 'Hey Pluto', then ask me to introduce myself")
        print("   or say 'help' to see what I can do")
        print("   Say 'goodbye' or 'exit' to quit\n")
        
        while True:
            user_input = self.listen()
            
            if user_input:
                result = self.handle_scenario(user_input)
                if result == "EXIT":
                    break
            
            time.sleep(0.5)

if __name__ == "__main__":
    try:
        agent = SimpleAgent()
        agent.run()
    except KeyboardInterrupt:
        print("\n\n⏸️  Agent stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
