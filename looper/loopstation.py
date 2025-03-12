import pyaudio
import numpy as np
import threading
import time
import keyboard
from datetime import datetime
from pydub import AudioSegment  # Add this import for MP3 handling
import os  # new import

class LoopStation:
    def __init__(self, bpm=120, beats_per_loop=16, sample_rate=44100):
        self.bpm = bpm
        self.beats_per_loop = beats_per_loop
        self.sample_rate = sample_rate
        self.loop_duration = 60 / self.bpm * self.beats_per_loop  # in seconds
        self.loop_samples = int(self.loop_duration * self.sample_rate)
        
        # Initialize PyAudio
        self.p = pyaudio.PyAudio()
        
        # Create tracks (initially empty)
        self.tracks = [
            np.zeros(self.loop_samples, dtype=np.float32),
            np.zeros(self.loop_samples, dtype=np.float32),
            np.zeros(self.loop_samples, dtype=np.float32)
        ]
        
        # Track states
        self.track_active = [False, False, False]
        self.is_recording = False
        self.current_track = 0
        self.is_running = True
        self.position = 0
        
        # Create metronome sounds
        self.click_high = self.load_metronome(pitch_shift=1.2) 
        self.click_low = self.load_metronome(pitch_shift=1)
        self.metronome_enabled = True  # Added metronome toggle
        
        # Open audio stream
        self.stream = self.p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=self.sample_rate,
            output=True,
            input=True,
            stream_callback=self.audio_callback,
            frames_per_buffer=1024
        )
    
    def load_metronome(self, pitch_shift=1.0):
        """Load metronome.mp3 from a relative path and apply optional pitch shift"""
        # use relative path based on this file's directory
        metronome_path = os.path.join(os.path.dirname(__file__), 'audio', 'metronome.mp3')
        audio = AudioSegment.from_mp3(metronome_path)
        
        if pitch_shift != 1.0:
            # Change the frame rate to shift pitch without changing duration
            audio = audio._spawn(audio.raw_data, overrides={
                'frame_rate': int(audio.frame_rate * pitch_shift)
            }).set_frame_rate(self.sample_rate)
        
        # Convert to numpy array
        samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
        
        # Normalize to float32 range (-1.0 to 1.0)
        samples = samples / (2.0**(8 * audio.sample_width - 1))
        
        # Add a bit of padding
        padding = np.zeros(int(self.sample_rate * 0.05), dtype=np.float32)
        return np.concatenate([samples, padding]).astype(np.float32)
    
    def audio_callback(self, in_data, frame_count, time_info, status):
        """Audio callback function for PyAudio stream"""
        input_data = np.frombuffer(in_data, dtype=np.float32)
        
        # Calculate current position in loop
        output_data = np.zeros(frame_count, dtype=np.float32)
        
        # Add active tracks to output
        for i in range(3):
            if self.track_active[i]:
                start_idx = self.position % self.loop_samples
                end_idx = start_idx + frame_count
                
                if end_idx <= self.loop_samples:
                    # Regular case - no wrapping around loop end
                    output_data += self.tracks[i][start_idx:end_idx]
                else:
                    # Handle wrapping around the end of the loop
                    first_part = self.tracks[i][start_idx:self.loop_samples]
                    second_part = self.tracks[i][0:end_idx-self.loop_samples]
                    output_data[:len(first_part)] += first_part
                    output_data[len(first_part):] += second_part
        
        # Add metronome clicks if enabled
        if self.metronome_enabled:
            samples_per_beat = int(self.sample_rate * 60 / self.bpm)
            current_beat = (self.position // samples_per_beat) % self.beats_per_loop
            beat_position = self.position % samples_per_beat
            if current_beat == 0 and beat_position < len(self.click_high):
                output_data[:min(frame_count, len(self.click_high)-beat_position)] += self.click_high[beat_position:beat_position+frame_count]
            elif beat_position < len(self.click_low):
                output_data[:min(frame_count, len(self.click_low)-beat_position)] += self.click_low[beat_position:beat_position+frame_count]
        
        # Record to current track if we're recording
        if self.is_recording:
            start_idx = self.position % self.loop_samples
            end_idx = start_idx + frame_count
            
            if end_idx <= self.loop_samples:
                # Regular case - no wrapping around loop end
                self.tracks[self.current_track][start_idx:end_idx] = input_data
            else:
                # Handle wrapping around the end of the loop
                first_part_len = self.loop_samples - start_idx
                self.tracks[self.current_track][start_idx:self.loop_samples] = input_data[:first_part_len]
                self.tracks[self.current_track][0:end_idx-self.loop_samples] = input_data[first_part_len:]
        
        # Update position
        self.position += frame_count
        
        return (output_data.tobytes(), pyaudio.paContinue)
    
    def start_recording(self, track_num):
        """Start recording to the specified track"""
        if not self.is_recording:
            self.current_track = track_num
            # Clear the track before recording
            self.tracks[track_num] = np.zeros(self.loop_samples, dtype=np.float32)
            self.is_recording = True
            print(f"Started recording on track {track_num + 1}")
    
    def stop_recording(self):
        """Stop recording"""
        if self.is_recording:
            self.is_recording = False
            self.track_active[self.current_track] = True
            print(f"Stopped recording on track {self.current_track + 1}")
    
    def toggle_track(self, track_num):
        """Toggle a track on/off"""
        self.track_active[track_num] = not self.track_active[track_num]
        status = "on" if self.track_active[track_num] else "off"
        print(f"Track {track_num + 1} turned {status}")
    
    def toggle_metronome(self):
        self.metronome_enabled = not self.metronome_enabled
        print("Metronome turned", "on" if self.metronome_enabled else "off")
    
    def change_bpm(self, new_bpm):
        """Change the BPM (keeping the same number of beats)"""
        self.bpm = new_bpm
        self.loop_duration = 60 / self.bpm * self.beats_per_loop
        print(f"BPM changed to {new_bpm}")
    
    def clear_recordings(self):
        """Clear all recordings from the tracks"""
        for i in range(3):
            self.tracks[i] = np.zeros(self.loop_samples, dtype=np.float32)
            self.track_active[i] = False
        print("All recordings cleared")

    def shutdown(self):
        """Clean shutdown of the loop station"""
        self.is_running = False
        time.sleep(0.2)  # Give time for threads to exit
        
        if self.stream.is_active():
            self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        print("Loop station shut down")