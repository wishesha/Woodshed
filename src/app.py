import os
import json
import time
import math
from datetime import datetime
import streamlit as st
import librosa
import librosa.display
import matplotlib.pyplot as plt
import soundfile as sf
from audio_recorder_streamlit import audio_recorder

# File Paths
AUDIO_DIR = os.path.join("src", "Audio_Files")
METADATA_FILE = os.path.join(AUDIO_DIR, "metadata.json")

os.makedirs(AUDIO_DIR, exist_ok=True)

def load_metadata():
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_metadata(records):
    with open(METADATA_FILE, "w") as f:
        json.dump(records, f, indent=4)

def run_tempo_analysis(file_path):
    """Refactored version of your original detect_tempo function."""
    start_time = time.perf_counter()
    y, sr = librosa.load(file_path)
    
    if y.size == 0:
        raise ValueError("Audio file contains no data.")

    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, start_bpm=140, tightness=600)
    beat_times = librosa.frames_to_time(beats, sr=sr)
    end_time = time.perf_counter()
    compute_time = math.trunc((end_time - start_time) * 100) / 100

    # Ensure tempo is a standard scalar number
    if isinstance(tempo, (list, tuple, range)) or hasattr(tempo, "__len__"):
        tempo = float(tempo[0])
    else:
        tempo = float(tempo)

    return {
        "tempo": round(tempo, 2),
        "beat_count": len(beat_times),
        "compute_time": compute_time,
        "y": y,
        "sr": sr,
        "beat_times": beat_times
    }

# Streamlit App UI Configuration
st.set_page_config(page_title="Music Tempo Tracker", layout="wide")
st.title("Music Tempo Tracker")

# Sidebar - New Recording or File Upload
st.sidebar.header("Record or Upload")

tab1, tab2 = st.sidebar.tabs(["Microphone", "Upload File"])

audio_bytes = None
file_name_override = None

with tab1:
    st.write("Click the icon to start/stop recording:")
    recorded_audio = audio_recorder(text="", recording_color="#e8b62c", neutral_color="#6aa36f")
    if recorded_audio:
        audio_bytes = recorded_audio

with tab2:
    uploaded_file = st.file_uploader("Choose a WAV file", type=["wav"])
    if uploaded_file is not None:
        audio_bytes = uploaded_file.read()
        file_name_override = uploaded_file.name

# Form to metadata input on capture
if audio_bytes is not None:
    st.sidebar.subheader("Save Metadata")
    with st.sidebar.form("save_form"):
        passage_name = st.text_input("Passage Name", value="Practice Take")
        piece_name = st.text_input("Piece Name", value="Exercise #1")
        submit_button = st.form_submit_button("Process and Save Recording")

    if submit_button:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = file_name_override if file_name_override else f"rec_{timestamp}.wav"
        save_path = os.path.join(AUDIO_DIR, filename)

        # Save audio file to disk
        with open(save_path, "wb") as f:
            f.write(audio_bytes)

        # Run Tempo Detection Logic
        with st.spinner("Analyzing tempo..."):
            try:
                analysis = run_tempo_analysis(save_path)
                
                # Update JSON database
                records = load_metadata()
                new_entry = {
                    "id": timestamp,
                    "filename": filename,
                    "file_path": save_path,
                    "passage_name": passage_name,
                    "piece_name": piece_name,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "tempo": analysis["tempo"],
                    "beat_count": analysis["beat_count"],
                    "compute_time": analysis["compute_time"]
                }
                records.append(new_entry)
                save_metadata(records)
                st.sidebar.success(f"Saved and analyzed! Tempo: {analysis['tempo']} BPM")
            except Exception as e:
                st.sidebar.error(f"Error analyzing file: {e}")

# Main Layout - Display Saved History
st.header("Saved Recordings")
records = load_metadata()

if not records:
    st.info("No saved recordings found. Record audio or upload a file using the sidebar.")
else:
    # Build selection dropdown
    options = {f"{r['passage_name']} - {r['piece_name']} ({r['date']})": r for r in reversed(records)}
    selected_label = st.selectbox("Select a recording to view analysis:", list(options.keys()))
    selected_record = options[selected_label]

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Details")
        st.write(f"**Passage:** {selected_record['passage_name']}")
        st.write(f"**Piece:** {selected_record['piece_name']}")
        st.write(f"**Date:** {selected_record['date']}")
        st.write(f"**Estimated Tempo:** {selected_record['tempo']} BPM")
        st.write(f"**Total Beats Detected:** {selected_record['beat_count']}")
        st.write(f"**Processing Time:** {selected_record['compute_time']}s")
        
        if os.path.exists(selected_record['file_path']):
            st.audio(selected_record['file_path'])

    with col2:
        st.subheader("Waveform & Beat Analysis")
        if os.path.exists(selected_record['file_path']):
            y, sr = librosa.load(selected_record['file_path'])
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr, start_bpm=140, tightness=600)
            
            fig, ax = plt.subplots(figsize=(10, 4))
            librosa.display.waveshow(y, sr=sr, alpha=0.6, ax=ax)
            
            # Plot beat positions on waveform
            beat_times = librosa.frames_to_time(beats, sr=sr)
            ax.vlines(beat_times, -1, 1, color='r', alpha=0.75, linestyle='--', label='Detected Beats')
            ax.set(title=f"Waveform with Detected Beats ({selected_record['tempo']} BPM)")
            ax.legend(loc='upper right')
            
            st.pyplot(fig)
        else:
            st.warning("Audio file could not be found on disk.")