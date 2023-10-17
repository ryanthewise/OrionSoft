import os
import io
import threading
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
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
window.configure(bg='#2c2c2c')

# Set window to full screen
window.attributes('-fullscreen', True)

canvas = tk.Canvas(window, width=1200, height=1200, bg='#2c2c2c', highlightthickness=0)
canvas.pack(pady=0)

# Create text directly on the canvas
letter_text = canvas.create_text(600, 600, text=letters[current_letter_index], font=('Arial', 200 ))

def initialize_globals():
    global prev_magnitudes
    prev_magnitudes = np.zeros_like(get_spectrum(np.zeros(CHUNK_SIZE, dtype=np.int16)))

def get_spectrum(data):
    start_freq = 1200  # 80 Hz
    end_freq = 2500  # 3 kHz

    start_idx = int(start_freq / (44100 / 1024))
    end_idx = int(end_freq / (44100 / 1024))
    
    # Compute FFT and magnitudes
    spectrum = np.abs(np.fft.rfft(data, n=1024)[start_idx:end_idx])
    magnitudes = np.abs(spectrum)
    return magnitudes

def rgba_to_hex(rgba):
    return "#{:02x}{:02x}{:02x}".format(int(rgba[0]*255), int(rgba[1]*255), int(rgba[2]*255))

def get_color_from_intensity(intensity, max_intensity):
    # Normalize intensity between 0 and 1
    norm_intensity = intensity / max_intensity
    # Interpolate colors from green (low) to red (high)
    color = plt.cm.RdYlGn(1.0 - norm_intensity)
    return rgba_to_hex(color)

def get_volume():
    global prev_magnitudes

    # Read a chunk of audio and compute FFT magnitudes
    data = np.frombuffer(stream.read(CHUNK_SIZE, exception_on_overflow=False), dtype=np.int16)
    magnitudes = get_spectrum(data)
    num_bars = len(magnitudes)

    angle_gap = 2 * np.pi / num_bars

    max_magnitude = np.max(magnitudes)
    normalized_magnitudes = magnitudes / max_magnitude * 150  # Normalize and scale

    rise_decay_factor = 0.8  # Adjust this value to control the speed at which bars rise. Closer to 1 means slower rise.
    fall_decay_factor = 0.98  # Adjust this value to control the decay speed. Closer to 1 means slower decay.

    blended_magnitudes = np.zeros_like(prev_magnitudes)

    # Apply rise decay factor when the new magnitude is greater than the previous, otherwise apply fall decay factor
    for i in range(len(prev_magnitudes)):
        if normalized_magnitudes[i] > prev_magnitudes[i]:
            blended_magnitudes[i] = rise_decay_factor * prev_magnitudes[i] + (1 - rise_decay_factor) * normalized_magnitudes[i]
        else:
            blended_magnitudes[i] = fall_decay_factor * prev_magnitudes[i] + (1 - fall_decay_factor) * normalized_magnitudes[i]

    canvas.delete('spectrum')  # Remove previous bars

    center_x, center_y = canvas.winfo_width() / 2, canvas.winfo_height() / 2    # Center of the canvas

    scale_factor = 3.5  # Adjust this value to change the overall size of the spectrum

    for i, mag in enumerate(blended_magnitudes):
        start_angle = i * angle_gap
        end_angle = (i + 1) * angle_gap

        start_outer_x = center_x + scale_factor * mag * np.cos(start_angle)
        start_outer_y = center_y + scale_factor * mag * np.sin(start_angle)

        end_outer_x = center_x + scale_factor * mag * np.cos(end_angle)
        end_outer_y = center_y + scale_factor * mag * np.sin(end_angle)

        color = get_color_from_intensity(mag, 170)  # Max magnitude is scaled to 170

        # Create a bar as a polygon using the start and end coordinates
        canvas.create_polygon(center_x, center_y, start_outer_x, start_outer_y, end_outer_x, end_outer_y, fill=color, tags='spectrum')
    
    canvas.tag_lower('spectrum', letter_text)

    prev_magnitudes = blended_magnitudes

    window.after(20, get_volume)

def update_ui():
    global current_letter_index, r, combined_recognition  # Addressed scope issue
    
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
            # ... [rest of the dictionary]
        }

        if recognized_text in acceptable_responses.get(letters[current_letter_index], [letters[current_letter_index]]):
            current_letter_index += 1
            if current_letter_index >= len(letters):
                messagebox.showinfo("Success", "All letters recognized!")
                window.quit()
            else:
                canvas.itemconfig(letter_text, text=letters[current_letter_index])

        else:
            messagebox.showwarning("Try Again", f"Expected {letters[current_letter_index]}, but heard {recognized_text}.")

    except sr.UnknownValueError as e:
        print(e)  # This will print the exception details to the terminal
        messagebox.showerror("Error", "Could not recognize the audio!")
    except Exception as e:  # More comprehensive exception handling
        print(f"An error occurred: {e}")
        messagebox.showerror("Error", str(e))

def record_and_recognize():
    global current_letter_index, r, combined_recognition  # Addressed scope issue

    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.realpath(__file__))

    # Build the full path to the wav file
    wav_path = os.path.join(script_dir, "word.wav")

    # Recording audio
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source, timeout=2, phrase_time_limit=2)  # Listen for a maximum of 2 seconds

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

    window.after(0, update_ui)  # Schedule the UI update to run on the main thread
    
def start_recognition_thread():
    thread = threading.Thread(target=record_and_recognize)
    thread.start()  

initialize_globals()

# Display the first letter
canvas.itemconfig(letter_text, text=letters[current_letter_index])

# Button to start the recording and recognition process
start_button = tk.Button(window, text="Listen", font=('Arial', 50), command=start_recognition_thread)
start_button.pack(pady=20)

# Space bar to start recording
window.bind('<space>', lambda e: start_recognition_thread())

# ESC with "q" to quit
window.bind('<Escape>', lambda e: window.quit())
window.bind('q', lambda e: window.quit())

# Start volume meter
get_volume()

window.mainloop()
