import os
import io
import tkinter as tk
from tkinter import messagebox
import numpy as np
import pyaudio
from pydub import AudioSegment
import speech_recognition as sr

# Initialize required variables
letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
current_letter_index = 0
CHUNK_SIZE = 1024
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=CHUNK_SIZE)

# Set up the GUI window
window = tk.Tk()
window.title("Letter Pronunciation Trainer")

canvas = tk.Canvas(window, width=300, height=300)
canvas.pack(pady=100)

# Label to display the current letter
letter_label = tk.Label(window, font=('Arial', 100))

# Center the label on the canvas
canvas.create_window(150, 150, window=letter_label)

def get_volume():
    # Read a chunk of audio and compute RMS
    data = np.frombuffer(stream.read(CHUNK_SIZE, exception_on_overflow=False), dtype=np.int16)
    rms = np.sqrt(np.maximum(np.mean(data**2), 0))
    print(rms)
    scale_factor = 300  # You can adjust this value to make the effect more or less pronounced
    circle_radius = 100 + (rms / 3000) * scale_factor

    # Ensure circle_radius is finite and valid
    if np.isfinite(circle_radius):
        canvas.coords(circle, 150-circle_radius, 150-circle_radius, 150+circle_radius, 150+circle_radius)

    # Continue updating the circle
    window.after(50, get_volume)


def record_and_recognize():
    global current_letter_index

    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.realpath(__file__))

    # Build the full path to the wav file
    wav_path = os.path.join(script_dir, "word.wav")

    # Recording audio
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source, timeout=5, phrase_time_limit=5)  # Listen for a maximum of 5 seconds

    # Combine prerecorded audio with the recorded audio 
    test_audio = AudioSegment.from_wav(wav_path)

    with sr.AudioFile(wav_path) as source:
        test_audio_data = r.record(source)
        print(r.recognize_google(audio_data=test_audio_data))

    user_audio = AudioSegment.from_wav(io.BytesIO(audio.get_wav_data()))
    combined_audio = test_audio + user_audio

    combined_audio.export("temp_combined_audio.wav", format="wav")
    with sr.AudioFile("temp_combined_audio.wav") as source:
        combined_recognition = r.record(source)

    os.remove("temp_combined_audio.wav")

    # Recognizing the spoken letter
    try:
        recognized_text = r.recognize_google(audio_data=combined_recognition).upper().strip()
        print(f"Recognized text: {recognized_text}")

        # Strip the "TEST" part
        recognized_text = recognized_text.replace("TEST", "").strip()
        print(f"Stripped text: {recognized_text}")

        # Check if recognized text matches the current letter or its phonetic sound
        acceptable_responses = {
            "A": ["A", "AY"],
            "B": ["B", "BE", "BEE"],
            # You can add more phonetic variations for other letters as needed.
        }

        if recognized_text in acceptable_responses.get(letters[current_letter_index], [letters[current_letter_index]]):
            current_letter_index += 1
            if current_letter_index >= len(letters):
                messagebox.showinfo("Success", "All letters recognized!")
                window.quit()
            else:
                letter_label.config(text=letters[current_letter_index])
        else:
            messagebox.showwarning("Try Again", f"Expected {letters[current_letter_index]}, but heard {recognized_text}.")

    except sr.UnknownValueError as e:
        print(e)  # This will print the exception details to the terminal
        messagebox.showerror("Error", "Could not recognize the audio!")

# Display the first letter
letter_label.config(text=letters[current_letter_index])

# Create a circle on the canvas
circle = canvas.create_oval(50, 50, 250, 250, outline='blue', width=2)

# Button to start the recording and recognition process
start_button = tk.Button(window, text="Start Listening", command=record_and_recognize)
start_button.pack(pady=20)

# Start volume meter
get_volume()

window.mainloop()
