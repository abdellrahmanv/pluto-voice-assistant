"""
🪐 Pluto Simple - Scenario-Based Voice Agent
No LLM, just STT → Scenarios → TTS

Simple voice assistant with predefined conversation scenarios
"""

try:
    import speech_recognition as sr
except ImportError:
    print("❌ ERROR: SpeechRecognition not installed!")
    print("   Install with: pip3 install SpeechRecognition")
    print("   Or run: sudo ./setup_pi.sh")
    exit(1)

try:
    import pyttsx3
except ImportError:
    print("❌ ERROR: pyttsx3 not installed!")
    print("   Install with: pip3 install pyttsx3")
    print("   Or run: sudo ./setup_pi.sh")
    exit(1)

import time
import sys

class SimpleAgent:
    def __init__(self):
        print("🔧 Checking audio devices...")
        
        # Check microphone
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            mic_found = False
            print("\n🎤 Available microphones:")
            for i in range(p.get_device_count()):
                info = p.get_device_info_by_index(i)
                if info['maxInputChannels'] > 0:
                    print(f"   [{i}] {info['name']}")
                    mic_found = True
            p.terminate()
            
            if not mic_found:
                print("❌ No microphone detected!")
                print("   Run: ./test_audio.sh for diagnostics")
                sys.exit(1)
        except Exception as e:
            print(f"⚠️  Could not check microphones: {e}")
        
        # Initialize TTS
        print("\n🔊 Initializing text-to-speech...")
        self.tts = pyttsx3.init()
        
        # Make voice more natural and human-like
        self.tts.setProperty('rate', 175)     # Speed (150-200 is natural, default was too slow)
        self.tts.setProperty('volume', 1.0)   # Full volume
        
        # Try to use a better voice (female/male)
        voices = self.tts.getProperty('voices')
        if len(voices) > 1:
            # Use second voice if available (often better quality)
            self.tts.setProperty('voice', voices[1].id)
        
        # Initialize STT
        print("🎙️ Initializing speech recognition...")
        self.recognizer = sr.Recognizer()
        
        try:
            self.microphone = sr.Microphone()
            print("✅ Audio system ready")
        except Exception as e:
            print(f"❌ Failed to initialize microphone: {e}")
            print("\n💡 Run: chmod +x test_audio.sh && ./test_audio.sh")
            sys.exit(1)
        
        # Scenario states
        self.state = "IDLE"
        self.name = "Pluto"
        
        print("🪐 Pluto Simple Agent Initialized")
    
    def speak(self, text):
        """Text to speech"""
        print(f"🔊 Pluto: {text}")
        self.tts.say(text)
        self.tts.runAndWait()
    
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
        print("🪐 PLUTO SIMPLE AGENT - Scenario-Based Assistant")
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
