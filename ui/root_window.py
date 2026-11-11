# ui/root_window.py
import customtkinter as ctk
from .theme import BG_COLOR
from .frame_home import HomeFrame
from .frame_recording import RecordingFrame
from .frame_result import ResultFrame
from .frame_upload import UploadFrame

class AccentClassifierApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Setup ---
        self.title("Accent Classification")
        self.geometry("800x480")
        self.configure(fg_color=BG_COLOR)
        
        # Lock the grid layout to take up the whole screen
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Frame Dictionary ---
        self.frames = {}

        for F in (HomeFrame, RecordingFrame, ResultFrame, UploadFrame):
            page_name = F.__name__
            frame = F(parent=self, controller=self)
            self.frames[page_name] = frame
            
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("HomeFrame")

    def show_frame(self, page_name):
        """Brings the requested frame to the front."""
        frame = self.frames[page_name]
        frame.tkraise()
        
        # If the user navigated to the Recording screen, start the mic!
        if page_name == "RecordingFrame":
            frame.start_task()