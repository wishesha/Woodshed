import librosa
import os
import time
import math
import pyaudio
import wave

audio_path = "src\Audio_Files\\"
CHUNK = 512
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

def record_audio():
    stop_recording = False
    p = pyaudio.PyAudio()
    input("Press Enter to Begin Recording: ")
    try:
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True)
        input("Recording in Progress, Press Ctrl+C to Stop:")
        frames = []
        while not stop_recording:
            try:
                data = p.read(CHUNK)
                frames.add(data)
            except IOError as e:
                print(f"overload Error")
                continue
    except IOError:
        print("Recording Failed")
        frames = []
    



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
    detect_tempo(audio_path)

if __name__ == "__main__":  
    main()