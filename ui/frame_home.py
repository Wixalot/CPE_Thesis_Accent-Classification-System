# ui/frame_home.py
import customtkinter as ctk

from .theme import *


class HomeFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=BG_COLOR, corner_radius=0)
        self.controller = controller

        # --- Centered Content Block ---
        self.center_container = ctk.CTkFrame(self, fg_color="transparent")
        self.center_container.place(relx=0.5, rely=0.5, anchor="center")

        # --- Title Label ---
        self.title_label = ctk.CTkLabel(
            self.center_container,
            text="ACCENT\nCLASSIFICATION",
            font=(FONT_FAMILY, 36, "bold"),
            text_color=TEXT_COLOR,
            justify="left",
        )
        self.title_label.grid(row=0, column=0, sticky="w")

        # --- Separator Line ---
        self.separator = ctk.CTkFrame(
            self.center_container,
            width=2,
            height=80,
            fg_color=BORDER_COLOR,
        )
        self.separator.grid(row=0, column=1, padx=20)

        # --- Button Column ---
        self.button_column = ctk.CTkFrame(self.center_container, fg_color="transparent")
        self.button_column.grid(row=0, column=2, padx=(20, 0), sticky="n")

        # --- Record Button ---
        self.record_btn = ctk.CTkButton(
            self.button_column,
            text="RECORD",
            font=(FONT_FAMILY, 24, "bold"),
            fg_color=BTN_BG,
            hover_color=BTN_HOVER,
            text_color=TEXT_COLOR,
            border_color=BORDER_COLOR,
            border_width=BTN_BORDER_WIDTH,
            corner_radius=BTN_RADIUS,
            width=180,
            height=60,
            command=lambda: self.controller.show_frame("RecordingFrame"),
        )
        self.record_btn.grid(row=0, column=0, pady=(0, 12))

        # --- Upload Button ---
        self.upload_btn = ctk.CTkButton(
            self.button_column,
            text="UPLOAD",
            font=(FONT_FAMILY, 24, "bold"),
            fg_color=BTN_BG,
            hover_color=BTN_HOVER,
            text_color=TEXT_COLOR,
            border_color=BORDER_COLOR,
            border_width=BTN_BORDER_WIDTH,
            corner_radius=BTN_RADIUS,
            width=180,
            height=60,
            command=lambda: self.controller.show_frame("UploadFrame"),
        )
        self.upload_btn.grid(row=1, column=0)

        # --- Dynamic Scaling Listener ---
        self.controller.bind("<Configure>", self.dynamic_resize)

    def dynamic_resize(self, event):
        """Automatically scales text and buttons based on window resolution."""
        if event.widget != self.controller:
            return

        width = event.width
        height = event.height

        new_title_size = max(12, min(72, int(width * 0.045)))
        self.title_label.configure(font=(FONT_FAMILY, new_title_size, "bold"))

        new_line_height = max(30, min(150, int(height * 0.16)))
        self.separator.configure(height=new_line_height)

        new_btn_font_size = max(10, min(24, int(width * 0.03)))
        new_btn_width = max(140, min(220, int(width * 0.20)))
        new_btn_height = max(30, min(60, int(height * 0.12)))

        self.record_btn.configure(
            font=(FONT_FAMILY, new_btn_font_size, "bold"),
            width=new_btn_width,
            height=new_btn_height,
        )
        self.upload_btn.configure(
            font=(FONT_FAMILY, new_btn_font_size, "bold"),
            width=new_btn_width,
            height=new_btn_height,
        )