import librosa
import os
import time
import math
import threading
from datetime import datetime
import sounddevice as sd
import numpy as np 

audio_path = "src\Audio_Files\\"
FORMAT = 'int16'
CHANNELS = 1
RATE = 44100

def wait_for_stop(stop_event):
    input("Recording in Progress, Press Enter to Stop:")
    stop_event.set()

def record_audio():
    frames = []
    stop_event = threading.Event()

    song_name = input("Name of Passage: ")

    def my_callback(indata, frame_count, time_info, status):
        frames.append(indata.copy())

    input("Press Enter to Begin Recording: ")
    try:
        print("Recording...")
        with sd.InputStream(samplerate=RATE, channels=CHANNELS, dtype=FORMAT, callback=my_callback):
            
            threading.Thread(target=wait_for_stop, args=(stop_event,)).start()
            while not stop_event.is_set():
                time.sleep(0.1)
    except IOError:
        print("Recording Failed")
        frames = []

    audio_data = np.concatenate(frames, axis=0)
    timestamp = datetime.now()
    formatted_time = timestamp.strftime("%Y-%m-%d_%H:%M")
    print(formatted_time)
    

def detect_tempo(audio_path):
    file = input("Enter Filename('.wav' only): ")
    audio_path += file
    try:
        file_size = os.path.getsize(audio_path)
        if file_size < 1000000:
             file_size = file_size/1000
             byte_type = "KB"
        else:
            file_size = file_size/1000000
            byte_type = "MB"
        start_time = time.perf_counter()
        print(f"Detected file: {file} of size {file_size} {byte_type}")
        y, sr = librosa.load(audio_path)
        if y.size == 0:
            raise ValueError("Audio file contains no data.")
    except OSError:
        print(f"{file} is not a valid file")
        raise SystemExit
    except Exception as e:
            print(f"Failed to load {file} \nError: {type(e).__name__} -- {e}")
            raise SystemExit
    
    
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, start_bpm=140, tightness=600)
    beat_times = librosa.frames_to_time(beats, sr=sr)
    end_time = time.perf_counter()
    compute_time = math.trunc((end_time - start_time) * 100) / 100
    
    print(f"time to complete: {compute_time} seconds")
    print(f"Estimated Tempo: {tempo}\nBeats: {len(beat_times)}")
    return tempo

def main():
    record_audio()
#    detect_tempo(audio_path)

if __name__ == "__main__":  
    main()