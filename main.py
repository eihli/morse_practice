#!/usr/bin/env python3

import argparse
import time
import numpy as np
import sounddevice as sd
import random
from typing import List

# Morse code definitions
MORSE_CODE = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.', 
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..', 
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.', 
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 
    'Y': '-.--', 'Z': '--..', '0': '-----', '1': '.----', '2': '..---', 
    '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...', 
    '8': '---..', '9': '----.', '.': '.-.-.-', ',': '--..--', '?': '..--..', 
    '/': '-..-.', '-': '-....-', '(': '-.--.', ')': '-.--.-', ' ': ' '
}

# Morse timing parameters
DIT_DAH_WPM = 20  # Speed of individual dits/dahs
OVERALL_WPM = 10  # Overall effective speed considering extra spacing
TIMING_ADJUSTMENT = 1.0  # Adjustment factor to make dit/dah timing slightly longer (1.0 = normal, >1.0 = longer)

# Audio parameters
SAMPLE_RATE = 44100  # Hz
TONE_FREQ = 700      # Hz (standard Morse tone frequency)

# Exchange patterns - content parameters
activator_calls = ["KI5RCF", "N1ABC"]
hunter_calls = ["W1XYZ"]
signal_reports = ["599"]
names = ["JOHN"]
locations = ["CA", "WA"]
park_ids = ["K-1234"]

# Exchange patterns
exchange_patterns = [
    # Basic exchange
    [
        "CQ POTA DE {activator_call} {activator_call} K",
        "{hunter_call} DE {activator_call} GM UR {signal_report} {signal_report} NAME {name} {name} QTH {location} {location} AT PARK {park_id} {park_id} K",
        "{activator_call} DE {hunter_call} TU UR {signal_report} {signal_report} NAME IS BOB QTH NY 73 K",
        "{hunter_call} DE {activator_call} TU FOR CONTACT 73 K",
    ],

    # Alternate pattern
    [
        "CQ POTA {activator_call} {park_id} K",
        "{activator_call} DE {hunter_call} {hunter_call} K",
        "{hunter_call} GM UR {signal_report} FROM {park_id} {name} K",
        "R R TU {name} UR {signal_report} DE {hunter_call} 73",
        "73 TU {hunter_call} QRZ POTA DE {activator_call} K"
    ],
]

def compute_timings():
    """Compute all morse timing parameters based on Farnsworth method."""
    # Calculate dot duration from WPM
    # PARIS method: PARIS is 50 dot-units, and at X WPM, we send X PARIS per minute
    # So 1 WPM = 50 units per minute = 50 units per 60 seconds = 1.2 seconds per unit
    dot_duration = 60 / (50 * DIT_DAH_WPM) * TIMING_ADJUSTMENT  # seconds with adjustment
    
    # Standard morse timing relationships
    dash_duration = 3 * dot_duration
    intra_char_gap = dot_duration  # Gap between elements within a character
    
    # Calculate effective WPM and adjust inter-character and word gaps
    # Calculate standard inter-character gap (3 dots at DIT_DAH_WPM)
    std_inter_char_gap = 3 * dot_duration
    # Calculate standard word gap (7 dots at DIT_DAH_WPM)
    std_word_gap = 7 * dot_duration
    
    # Calculate how much we need to slow down by adding extra space
    slowdown_factor = DIT_DAH_WPM / OVERALL_WPM if OVERALL_WPM < DIT_DAH_WPM else 1
    
    # Only the gaps are extended in Farnsworth timing
    inter_char_gap = std_inter_char_gap * slowdown_factor
    word_gap = std_word_gap * slowdown_factor
    
    return {
        'dot': dot_duration,
        'dash': dash_duration,
        'intra_char_gap': intra_char_gap,
        'inter_char_gap': inter_char_gap,
        'word_gap': word_gap
    }

def generate_tone(duration, timing):
    """Generate a sine wave tone."""
    t = np.arange(0, duration, 1/SAMPLE_RATE)
    tone = 0.5 * np.sin(2 * np.pi * TONE_FREQ * t)
    sd.play(tone, SAMPLE_RATE, blocking=True)
    
def play_dot(timing):
    """Play a Morse code dot."""
    generate_tone(timing['dot'], timing)
    
def play_dash(timing):
    """Play a Morse code dash."""
    generate_tone(timing['dash'], timing)
    
def play_silence(duration):
    """Play silence for the specified duration."""
    time.sleep(duration)

def play_morse_char(char: str, timing: dict):
    """Play a single character in Morse code."""
    if char == ' ':
        # This is a word space - we don't play anything but wait
        return
        
    morse = MORSE_CODE.get(char.upper(), '')
    
    for i, symbol in enumerate(morse):
        if symbol == '.':
            play_dot(timing)
        elif symbol == '-':
            play_dash(timing)
            
        # Add intra-character gap if not the last element
        if i < len(morse) - 1:
            play_silence(timing['intra_char_gap'])

def play_morse_text(text: str, timing: dict, show_text: bool = False):
    """Play the entire text in Morse code, with optional text display."""
    words = text.split()
    
    for i, word in enumerate(words):
        # Play each character in the word
        for j, char in enumerate(word):
            play_morse_char(char, timing)
            
            # Add inter-character gap if not the last character in the word
            if j < len(word) - 1:
                play_silence(timing['inter_char_gap'])
        
        # After a word is completed and if show_text is True, print the word
        if show_text:
            print(word, end=' ', flush=True)
            
        # Add word gap if not the last word
        if i < len(words) - 1:
            play_silence(timing['word_gap'])
    
    if show_text:
        print()  # New line after the entire text

def format_exchange(exchange_pattern: List[str], variables: dict) -> List[str]:
    """Format the exchange pattern with the given variables."""
    formatted_exchange = []
    for message in exchange_pattern:
        formatted_message = message.format(**variables)
        formatted_exchange.append(formatted_message)
    return formatted_exchange

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='POTA Morse Code Practice')
    parser.add_argument('--show-text', action='store_true', 
                      help='Display text of each word after it plays')
    args = parser.parse_args()
    
    # Compute timing parameters
    timing = compute_timings()
    
    # Randomly select variables for the exchange
    variables = {
        'activator_call': random.choice(activator_calls),
        'hunter_call': random.choice(hunter_calls),
        'signal_report': random.choice(signal_reports),
        'name': random.choice(names),
        'location': random.choice(locations),
        'park_id': random.choice(park_ids)
    }
    
    # Run through each exchange pattern
    for pattern in exchange_patterns:
        formatted_exchange = format_exchange(pattern, variables)
        
        print("\n--- Starting new exchange pattern ---")
        if args.show_text:
            print("Text will be displayed as it's played.")
        else:
            print("Listening mode active (no text display).")
        
        # Play each message in the exchange
        for message in formatted_exchange:
            play_morse_text(message, timing, args.show_text)
            # Brief pause between messages
            play_silence(1.0)
            
        # Longer pause between exchange patterns
        play_silence(3.0)
        
    print("\nPractice session complete.")

if __name__ == "__main__":
    main() 