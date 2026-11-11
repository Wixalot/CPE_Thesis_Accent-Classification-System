# ui/frame_result.py
import customtkinter as ctk
from .theme import *

class ResultFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=BG_COLOR, corner_radius=0)
        self.controller = controller

        # --- The Centering Container ---
        self.center_container = ctk.CTkFrame(self, fg_color="transparent")
        self.center_container.place(relx=0.5, rely=0.5, anchor="center")

        # --- Subtitle Label ---
        self.title_label = ctk.CTkLabel(
            self.center_container,
            text="ANALYSIS COMPLETE",
            font=(FONT_FAMILY, 24, "bold"),
            text_color=TEXT_COLOR
        )
        self.title_label.pack(pady=(0, 5))

        # --- Horizontal Separator ---
        self.separator = ctk.CTkFrame(
            self.center_container,
            height=2,
            fg_color=BORDER_COLOR
        )
        self.separator.pack(fill="x", pady=(0, 20), padx=20) 

        # --- Result Output Label ---
        self.result_label = ctk.CTkLabel(
            self.center_container,
            text="DETECTING...", # Default state before AI finishes
            font=(FONT_FAMILY, 48, "bold"),
            text_color=TEXT_COLOR
        )
        self.result_label.pack(pady=(0, 30))

        # --- Try Again Button ---
        self.retry_btn = ctk.CTkButton(
            self.center_container,
            text="TRY AGAIN",
            font=(FONT_FAMILY, 24, "bold"),
            fg_color=BTN_BG,
            hover_color=BTN_HOVER,
            text_color=TEXT_COLOR,
            border_color=BORDER_COLOR,
            border_width=BTN_BORDER_WIDTH,
            corner_radius=BTN_RADIUS,
            command=lambda: self.controller.show_frame("HomeFrame")
        )
        self.retry_btn.pack(pady=(0, 0))

        # --- Dynamic Scaling Listener ---
        # add="+" ensures we don't overwrite Home or Recording bindings
        self.controller.bind("<Configure>", self.dynamic_resize, add="+")

    def dynamic_resize(self, event):
        """Automatically scales elements based on the master window resolution."""
        if event.widget == self.controller:
            width = event.width
            height = event.height

            # Scale Texts
            new_title_size = max(12, min(40, int(width * 0.035)))
            new_result_size = max(24, min(72, int(width * 0.06))) # Makes the accent result massive
            
            self.title_label.configure(font=(FONT_FAMILY, new_title_size, "bold"))
            self.result_label.configure(font=(FONT_FAMILY, new_result_size, "bold"))

            # Scale Button
            new_btn_font = max(10, min(24, int(width * 0.03)))
            new_btn_w = max(80, min(150, int(width * 0.18)))
            new_btn_h = max(30, min(60, int(height * 0.12)))
            
            self.retry_btn.configure(
                font=(FONT_FAMILY, new_btn_font, "bold"),
                width=new_btn_w, height=new_btn_h
            )

    def update_result(self, predicted_accent):
        """Public method called by the AI to inject the final prediction."""
        self.result_label.configure(text=predicted_accent.upper())