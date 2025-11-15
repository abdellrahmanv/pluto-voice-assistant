# Pluto Simple - Additional Scenarios

## Current Changes

### Updated Greeting Response
**When you say:** "Hey Pluto"  
**Pluto responds:** "Hey, I'm Pluto—an AI-powered welcoming robot. How can I assist you today?"

## Add More Scenarios

Here are some ideas you can add to `simple_agent.py`:

### Math Operations
```python
elif "calculate" in user_input or "plus" in user_input:
    # Extract numbers and do simple math
    self.speak("I can do basic math. Try: what is 5 plus 3?")
```

### Reminders
```python
elif "remind me" in user_input:
    self.speak("Reminder feature coming soon!")
```

### Music Control
```python
elif "play music" in user_input:
    self.speak("Playing your favorite music!")
    # Add code to control music player
```

### Home Automation
```python
elif "turn on light" in user_input:
    self.speak("Turning on the lights")
    # Add GPIO control for Raspberry Pi
    
elif "turn off light" in user_input:
    self.speak("Turning off the lights")
```

### Fun Responses
```python
elif "sing a song" in user_input:
    self.speak("La la la la la! I'm not a great singer but I tried!")

elif "tell me a fact" in user_input:
    self.speak("Did you know? The first computer bug was an actual moth!")
```

### System Info (Raspberry Pi)
```python
elif "temperature" in user_input and "cpu" in user_input:
    # For Raspberry Pi
    import os
    temp = os.popen("vcgencmd measure_temp").readline()
    self.speak(f"CPU temperature is {temp}")
```

## Scenario States

You can add states to track conversation flow:

```python
def __init__(self):
    self.state = "IDLE"
    self.context = {}  # Store conversation context

def handle_scenario(self, user_input):
    # Multi-turn conversation
    if self.state == "ASKING_NAME":
        self.context['user_name'] = user_input
        self.speak(f"Nice to meet you, {user_input}!")
        self.state = "IDLE"
        return
    
    if "my name is" in user_input:
        self.state = "ASKING_NAME"
        self.speak("What's your name?")
```

## Tips
1. Keep patterns simple and specific
2. Test voice commands in quiet environment
3. Add logging to debug recognition
4. Use states for multi-turn conversations
5. Add error handling for edge cases
