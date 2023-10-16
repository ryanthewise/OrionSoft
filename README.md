# OrionSoft Phonics Trainer
## Ryan Black    Last Updated: 15 OCT 2023

## Description
The **OrionSoft Phonics Trainer** is a GUI application designed to help users (toddlers) improve their pronunciation of English letters. The user is prompted to pronounce a series of letters, which the application then attempts to recognize using Google's Web Speech API. If the pronunciation is correct, the user advances to the next letter. If incorrect, the user receives feedback on what the system recognized.

## Features
- Real-time volume visualization
- Integration with Google Web Speech API for speech recognition
- Feedback system to inform users about the correctness of their pronunciation
- Simple and intuitive GUI

## Requirements
- Python 3.x
- Libraries:
  - tkinter
  - numpy
  - pyaudio
  - pydub (with ffmpeg)
  - speech_recognition

```bash
pip install numpy pyaudio pydub SpeechRecognition
```

## Setup & Installation
- Clone the repository
- Install the required libraries
- Run the application

## Usage
- Run the application
- ️Click "Start Listening".
- Pronounce the letter that appears on the screen.
- If the system recognizes the letter, you will advance to the next letter.

## Known Issues
- The application might encounter issues with audio recognition in noisy environments or with unclear pronunciations.
- Ensure you have a stable internet connection since the Google Web Speech API requires it.

## Contributing
If you'd like to contribute to this project, please submit a pull request with your changes.

## License
This project is open-source. Feel free to use, modify, and distribute as you see fit.