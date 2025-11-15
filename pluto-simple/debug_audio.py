#!/usr/bin/env python3
"""
Debug script to check PyAudio devices
"""

import sys

print("🔍 Checking PyAudio installation and devices...\n")

# Check if PyAudio is installed
try:
    import pyaudio
    print("✅ PyAudio is installed")
except ImportError as e:
    print(f"❌ PyAudio NOT installed: {e}")
    print("\nInstall with:")
    print("  sudo apt-get install python3-pyaudio")
    print("  OR")
    print("  pip3 install pyaudio --break-system-packages")
    sys.exit(1)

# Check for audio devices
print("\n📋 Listing ALL audio devices:\n")
try:
    p = pyaudio.PyAudio()
    device_count = p.get_device_count()
    print(f"Total devices found: {device_count}\n")
    
    input_devices = []
    
    for i in range(device_count):
        try:
            info = p.get_device_info_by_index(i)
            device_type = []
            
            if info['maxInputChannels'] > 0:
                device_type.append("INPUT")
                input_devices.append(i)
            if info['maxOutputChannels'] > 0:
                device_type.append("OUTPUT")
            
            type_str = "/".join(device_type) if device_type else "N/A"
            
            print(f"Device {i}: {info['name']}")
            print(f"  Type: {type_str}")
            print(f"  Input channels: {info['maxInputChannels']}")
            print(f"  Output channels: {info['maxOutputChannels']}")
            print(f"  Sample rate: {info['defaultSampleRate']}")
            print()
            
        except Exception as e:
            print(f"Device {i}: Error reading - {e}\n")
    
    p.terminate()
    
    print("="*60)
    if input_devices:
        print(f"✅ Found {len(input_devices)} input device(s): {input_devices}")
        print(f"\n💡 Use device_index={input_devices[0]} for microphone")
    else:
        print("❌ NO INPUT DEVICES FOUND!")
        print("\nCheck:")
        print("  1. Is USB microphone connected?")
        print("  2. Run: arecord -l")
        print("  3. Try replugging the USB device")
    
except Exception as e:
    print(f"❌ Error accessing PyAudio: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("🎤 Testing SpeechRecognition library:")
try:
    import speech_recognition as sr
    print("✅ SpeechRecognition installed")
    
    r = sr.Recognizer()
    print("\nTrying to create Microphone with device_index=3...")
    try:
        mic = sr.Microphone(device_index=3)
        print("✅ Microphone(device_index=3) created successfully!")
        print(f"   Type: {type(mic)}")
    except Exception as e:
        print(f"❌ Failed to create Microphone(device_index=3): {e}")
        
        # Try default
        print("\nTrying default Microphone()...")
        try:
            mic = sr.Microphone()
            print("✅ Default Microphone() created successfully!")
        except Exception as e2:
            print(f"❌ Even default Microphone() failed: {e2}")
            
except ImportError:
    print("❌ SpeechRecognition NOT installed")
    print("   Install: pip3 install SpeechRecognition --break-system-packages")
