# audio/capture.py
import sounddevice as sd
import soundfile as sf
import numpy as np
import threading
import queue
from datetime import datetime
from pathlib import Path

# ==============================================================================
# HARDWARE CONFIGURATION
# Set to 2 for the current macOS testing setup.
# When reverting/deploying to the Raspberry Pi with a USB microphone, update this
# index or set to None to use system default input.
# ==============================================================================
DEFAULT_AUDIO_DEVICE = 2

class AudioRecorder:
    def __init__(self, ui_queue, device=DEFAULT_AUDIO_DEVICE, sample_rate=48000, chunk_size=1024, save_dir=None):
        self.ui_queue = ui_queue
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.device = device
        
        # Permanent recordings archive directory
        if save_dir is None:
            base_dir = Path(__file__).resolve().parent.parent
            self.save_dir = base_dir / "recordings"
        else:
            self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        self.stream = None
        self.is_recording = False
        self.audio_frames = []
        self.timer = None
        self.last_saved_file = None

    def audio_callback(self, indata, frames, time_info, status):
        """This runs continuously in the background while recording."""
        if self.is_recording:
            # 1. Save the raw NumPy chunk for uncompressed WAV persistence
            self.audio_frames.append(indata.copy())
            
            # 2. Calculate the volume amplitude for the UI wave (RMS calculation)
            amplitude = np.linalg.norm(indata) * 10 
            
            # 3. Drop it in the queue for the Main UI thread to pick up
            try:
                self.ui_queue.put_nowait(amplitude)
            except queue.Full:
                pass

    def start_recording(self, stop_callback):
        """Starts the microphone and the 10-second watchdog timer."""
        self.is_recording = True
        self.audio_frames = []
        
        # Start the sounddevice input stream with fallback if device index is unavailable
        try:
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                blocksize=self.chunk_size,
                device=self.device,
                callback=self.audio_callback
            )
            self.stream.start()
        except Exception as e:
            print(f"Warning: Audio device {self.device} unavailable ({e}). Falling back to system default input.")
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                blocksize=self.chunk_size,
                device=None,
                callback=self.audio_callback
            )
            self.stream.start()

        # Start the strict 10-second Watchdog Timer
        self.timer = threading.Timer(10.0, stop_callback)
        self.timer.start()

    def stop_recording(self):
        """
        Safely shuts down the microphone and timer.
        Archives the raw audio into an uncompressed 16-bit PCM WAV file,
        and returns the absolute file path for standardized downstream loading.
        """
        self.is_recording = False
        if self.timer:
            self.timer.cancel()
            self.timer = None
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception as e:
                print(f"Error closing audio stream: {e}")
            self.stream = None
            
        # Combine all tiny chunks into one contiguous 1D array
        if self.audio_frames:
            full_audio = np.concatenate(self.audio_frames, axis=0).flatten()
            
            # Generate timestamped archive filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = self.save_dir / f"recording_{timestamp}.wav"
            
            # Save strictly as uncompressed 16-bit PCM WAV at native sample rate
            sf.write(str(file_path), full_audio, self.sample_rate, subtype='PCM_16')
            print(f"🎙️ Live recording saved permanently to: {file_path}")
            
            self.last_saved_file = str(file_path)
            return str(file_path)
            
        return None
