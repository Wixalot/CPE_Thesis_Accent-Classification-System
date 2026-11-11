# ui/frame_upload.py
import customtkinter as ctk
from tkinter import filedialog
import librosa
from .theme import *
from ml_core.inference import AccentClassifier

class UploadFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=BG_COLOR, corner_radius=0)
        self.controller = controller
        
        # Initialize the AI Brain for this specific screen
        self.classifier = AccentClassifier()

        # --- The Centering Container ---
        self.center_container = ctk.CTkFrame(self, fg_color="transparent")
        self.center_container.place(relx=0.5, rely=0.5, anchor="center")

        # --- Title Label ---
        self.title_label = ctk.CTkLabel(
            self.center_container,
            text="UPLOAD A WAV FILE",
            font=(FONT_FAMILY, 24, "bold"),
            text_color=TEXT_COLOR
        )
        self.title_label.pack(pady=(0, 5))

        # --- Horizontal Separator ---
        self.separator = ctk.CTkFrame(self.center_container, height=2, fg_color=BORDER_COLOR)
        self.separator.pack(fill="x", pady=(0, 20), padx=20) 

        # --- Circular Upload Button (Arrow) ---
        self.upload_btn = ctk.CTkButton(
            self.center_container,
            text="↓",
            font=(FONT_FAMILY, 48, "bold"),
            width=100, height=100,
            corner_radius=50, # width/2 creates a perfect circle
            fg_color="transparent",
            hover_color=BTN_HOVER,
            text_color=TEXT_COLOR,
            border_color=BORDER_COLOR,
            border_width=3,
            command=self.browse_file
        )
        self.upload_btn.pack(pady=(10, 30))

        # --- Dynamic Scaling Listener ---
        self.controller.bind("<Configure>", self.dynamic_resize, add="+")

    def browse_file(self):
        """Opens the OS file picker restricted to .wav files."""
        file_path = filedialog.askopenfilename(
            title="Select a WAV file",
            filetypes=[("WAV Audio", "*.wav")]
        )
        if file_path:
            self.process_upload(file_path)

    def process_upload(self, file_path):
        """Loads the file, feeds it to the AI, and transitions the screen."""
        try:
            # 1. Load the file strictly at 22050 Hz to match your training data perfectly
            audio_data, _ = librosa.load(file_path, sr=22050, mono=True)
            
            # 2. Feed it directly to the AI with scores
            final_prediction, class_scores = self.classifier.predict_with_scores(audio_data, sample_rate=22050)
            print("Live class scores:")
            for label, score in class_scores.items():
                print(f"  {label}: {score:.6f}")
            print(f"Chosen class: {final_prediction}")
            
            # 3. Route to Result Screen
            result_screen = self.controller.frames["ResultFrame"]
            result_screen.update_result(f"{final_prediction} ACCENT")
            self.controller.show_frame("ResultFrame")
            
        except Exception as e:
            print(f"Error processing uploaded file: {e}")

    def dynamic_resize(self, event):
        """Scales the circle button and text."""
        if event.widget == self.controller:
            width = event.width
            
            new_title_size = max(12, min(40, int(width * 0.035)))
            self.title_label.configure(font=(FONT_FAMILY, new_title_size, "bold"))
            
            # Scale the circular button mathematically
            btn_size = max(80, min(150, int(width * 0.15)))
            self.upload_btn.configure(
                width=btn_size, height=btn_size, 
                corner_radius=btn_size // 2,
                font=(FONT_FAMILY, int(btn_size * 0.5), "bold")
            )