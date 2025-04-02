# Morse Code Practice for POTA

A simple command-line Python program to practice Morse code exchanges specifically for Parks on the Air (POTA) events, using Farnsworth timing.

## Features

- Generates audible Morse code for typical POTA exchange patterns
- Uses Farnsworth timing (configurable character and overall speed)
- Optional text display as words are played
- Standard 700Hz tone

## Requirements

- Python 3.6+
- Dependencies: numpy, sounddevice
- PortAudio library (system dependency)

## Installation

1. Clone this repository

2. Install PortAudio (system dependency):
   
   On Debian/Ubuntu:
   ```
   sudo apt-get install libportaudio2 portaudio19-dev
   ```
   
   On Fedora/RHEL:
   ```
   sudo dnf install portaudio portaudio-devel
   ```
   
   On macOS (using Homebrew):
   ```
   brew install portaudio
   ```

3. Install required Python dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the program with:

```
python main.py [--show-text]
```

Options:
- `--show-text`: Display the text of each word after it plays in Morse code

## Configuration

You can modify the following settings directly in the `main.py` file:

- `DIT_DAH_WPM`: Speed of individual dits/dahs (default: 20 WPM)
- `OVERALL_WPM`: Overall effective speed considering extra spacing (default: 10 WPM)
- Exchange patterns and content parameters (calls, reports, etc.)
