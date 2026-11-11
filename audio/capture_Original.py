# audio/capture.py
import sounddevice as sd
import numpy as np
import threading
import queue

class AudioRecorder:
    def __init__(self, ui_queue):
        self.ui_queue = ui_queue
        self.sample_rate = 16000
        self.chunk_size = 1024
        
        # We leave device=None so it automatically uses your Mac's default mic, 
        # and eventually the Raspberry Pi's default USB mic.
        self.device = None 
        
        self.stream = None
        self.is_recording = False
        self.audio_frames = []
        self.timer = None

    def audio_callback(self, indata, frames, time, status):
        """This runs continuously in the background while recording."""
        if self.is_recording:
            # 1. Save the raw NumPy data for your SVM model later
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
        
        # Start the sounddevice input stream
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            blocksize=self.chunk_size,
            device=self.device,
            callback=self.audio_callback
        )
        self.stream.start()

        # Start the strict 10-second Watchdog Timer
        self.timer = threading.Timer(10.0, stop_callback)
        self.timer.start()

    def stop_recording(self):
        """Safely shuts down the microphone and timer."""
        self.is_recording = False
        if self.timer:
            self.timer.cancel()
        if self.stream:
            self.stream.stop()
            self.stream.close()
            
        # Combine all the tiny chunks into one massive NumPy array ready for extraction
        if self.audio_frames:
            full_audio = np.concatenate(self.audio_frames, axis=0)
            return full_audio
        return None