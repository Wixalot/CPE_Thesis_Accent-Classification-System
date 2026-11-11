# ui/frame_recording.py
import customtkinter as ctk
import tkinter as tk
import queue
import math
import time
import os
import librosa
from .theme import *
from audio.capture import AudioRecorder 
from ml_core.inference import AccentClassifier

class RecordingFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=BG_COLOR, corner_radius=0)
        self.controller = controller
        
        # --- Audio Architecture ---
        self.ui_queue = queue.Queue(maxsize=100)
        self.recorder = AudioRecorder(self.ui_queue)
        self.classifier = AccentClassifier() # Initialize
        self.is_active = False
        self.record_start_time = None
        self.counter_job = None

        # --- The Centering Container ---
        self.center_container = ctk.CTkFrame(self, fg_color="transparent")
        self.center_container.place(relx=0.5, rely=0.5, anchor="center")

        # --- Title Label ---
        self.title_label = ctk.CTkLabel(
            self.center_container, text="ACCENT CLASSIFICATION",
            font=(FONT_FAMILY, 24, "bold"), text_color=TEXT_COLOR
        )
        self.title_label.pack(pady=(0, 5))

        # --- Horizontal Separator ---
        self.separator = ctk.CTkFrame(self.center_container, height=2, fg_color=BORDER_COLOR)
        self.separator.pack(fill="x", pady=(0, 20), padx=20) 

        # --- Recording Status ---
        self.status_label = ctk.CTkLabel(
            self.center_container, text="RECORDING",
            font=(FONT_FAMILY, 28, "bold"), text_color=TEXT_COLOR
        )
        self.status_label.pack(pady=(0, 15))

        # --- Waveform Canvas ---
        self.wave_canvas = tk.Canvas(
            self.center_container, bg=BG_COLOR, highlightthickness=2,
            highlightbackground=BORDER_COLOR, highlightcolor=BORDER_COLOR
        )
        self.wave_canvas.pack(pady=(0, 30))
        
        self.baseline = self.wave_canvas.create_line(
            0, 0, 0, 0, fill=TEXT_COLOR, width=2, tags="wave_line"
        )

        # --- Stop Button ---
        self.stop_btn = ctk.CTkButton(
            self.center_container, text="STOP", font=(FONT_FAMILY, 24, "bold"),
            fg_color=BTN_BG, hover_color=BTN_HOVER, text_color=TEXT_COLOR,
            border_color=BORDER_COLOR, border_width=BTN_BORDER_WIDTH,
            corner_radius=BTN_RADIUS, command=self.stop_task
        )
        self.stop_btn.pack(pady=(0, 0))

        # --- Dynamic Scaling Listener ---
        self.controller.bind("<Configure>", self.dynamic_resize, add="+")

    # --- NEW: Audio Control Logic ---
    
    def start_task(self):
        """Triggered when this frame is brought to the front."""
        self.is_active = True
        self.record_start_time = time.monotonic()
        self.phase = 0.0  # NEW: Tracks the horizontal scrolling of the wave
        
        while not self.ui_queue.empty():
            self.ui_queue.get_nowait()
            
        self.recorder.start_recording(stop_callback=self.stop_task)
        self.print_record_counter()
        self.update_waveform()

    def print_record_counter(self):
        if not self.is_active or self.record_start_time is None:
            return

        elapsed_seconds = int(time.monotonic() - self.record_start_time)
        print(f"Recording time: {elapsed_seconds}s")

        self.counter_job = self.after(1000, self.print_record_counter)

    def stop_task(self):
        """Triggered either manually by the STOP button, or automatically at 10 seconds."""
        if not self.is_active: return
        self.is_active = False

        if self.counter_job is not None:
            self.after_cancel(self.counter_job)
            self.counter_job = None
        self.record_start_time = None
        
        # Stop the mic, archive to an uncompressed WAV, and get the file path
        saved_file_path = self.recorder.stop_recording()
        
        # Flatten the line back to zero
        canvas_w = self.wave_canvas.winfo_width()
        canvas_h = self.wave_canvas.winfo_height()
        self.wave_canvas.coords(self.baseline, 0, canvas_h/2, canvas_w, canvas_h/2)
        
        # --- THE REAL AI ROUTING LOGIC (Standardized at 22,050 Hz identical to UploadFrame) ---
        result_screen = self.controller.frames["ResultFrame"]
        
        if saved_file_path and os.path.exists(saved_file_path):
            try:
                # 1. Load the recorded file strictly at 22,050 Hz to match training and upload pipeline
                audio_data, _ = librosa.load(saved_file_path, sr=22050, mono=True)
                
                # 2. Feed it directly to the AI with scores
                final_prediction, class_scores = self.classifier.predict_with_scores(
                    audio_data,
                    sample_rate=22050,
                )
                print(f"Loaded live recording from: {saved_file_path}")
                print("Live class scores:")
                for label, score in class_scores.items():
                    print(f"  {label}: {score:.6f}")
                print(f"Chosen class: {final_prediction}")
            except Exception as e:
                print(f"Error processing live recording: {e}")
                final_prediction = "ERROR: PROCESSING FAILED"
        else:
            final_prediction = "NO AUDIO DETECTED"
        
        # 3. Inject the real prediction into the screen
        result_screen.update_result(f"{final_prediction} ACCENT")
        
        # 4. Bring the Result Screen to the front
        self.controller.show_frame("ResultFrame")

    def update_waveform(self):
        """The UI Loop: Checks the queue and animates the line with tapered edges."""
        if not self.is_active: return

        try:
            amplitude = self.ui_queue.get_nowait()
            
            canvas_w = self.wave_canvas.winfo_width()
            canvas_h = self.wave_canvas.winfo_height()
            center_y = canvas_h / 2
            
            # Advance the phase slightly every frame to create smooth scrolling
            self.phase += 0.5 
            
            coords = []
            # Increased to 100 for a much smoother, high-resolution line
            points = 100 
            
            for i in range(points):
                # Calculate progress from 0.0 (left edge) to 1.0 (right edge)
                progress = i / (points - 1)
                x = progress * canvas_w
                
                # THE ENVELOPE: Creates the "Voice Recorder" pinch
                # math.sin(progress * math.pi) creates a dome shape (0 at edges, 1 in middle)
                envelope = math.pow(math.sin(progress * math.pi), 3)
                
                # THE NEW MATH: We multiply the final height by our envelope
                y = center_y + math.sin((i * 4.5) + self.phase) * (amplitude * (canvas_h / 512)) * envelope
                
                coords.extend([x, y])

                
                
            self.wave_canvas.coords(self.baseline, *coords)
            
        except queue.Empty:
            pass

        self.after(5, self.update_waveform)

    # ... (Keep your exact dynamic_resize method here, unchanged) ...
    def dynamic_resize(self, event):
        if event.widget == self.controller:
            width = event.width
            height = event.height
            new_title_size = max(12, min(40, int(width * 0.035)))
            new_status_size = max(14, min(48, int(width * 0.045)))
            self.title_label.configure(font=(FONT_FAMILY, new_title_size, "bold"))
            self.status_label.configure(font=(FONT_FAMILY, new_status_size, "bold"))
            canvas_w = max(200, min(600, int(width * 0.6)))
            canvas_h = max(80, min(200, int(height * 0.25)))
            self.wave_canvas.configure(width=canvas_w, height=canvas_h)
            self.wave_canvas.coords(self.baseline, 0, canvas_h/2, canvas_w, canvas_h/2)
            new_btn_font = max(10, min(24, int(width * 0.03)))
            new_btn_w = max(80, min(150, int(width * 0.18)))
            new_btn_h = max(30, min(60, int(height * 0.12)))
            self.stop_btn.configure(font=(FONT_FAMILY, new_btn_font, "bold"), width=new_btn_w, height=new_btn_h)