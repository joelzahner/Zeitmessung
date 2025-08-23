import customtkinter as ctk
from tkinter import ttk
import os

from seiten.rfid_zuordnung import RFIDZuordnungFrame
from seiten.personenanmeldung import PersonenanmeldungFrame
from seiten.startzeit_erfassung import StartzeitErfassungFrame
from seiten.zielzeit_erfassung import ZielzeitErfassungFrame
from seiten.rangliste import RanglisteFrame


# GUI-Initialisierung
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class VeloApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("VCM Zeitmessung")
        self.geometry("1000x600")
        self.iconbitmap("vcm.ico")

        # Layout-Konfiguration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nswe")
        self.sidebar.grid_rowconfigure(6, weight=1)

        self.toggle_button = ctk.CTkButton(self.sidebar, text="☰", command=self.toggle_sidebar)
        self.toggle_button.grid(row=0, column=0, padx=10, pady=10)

        self.menu_buttons = {
            "RFID-Zuordnung": self.show_rfid,
            "Personenanmeldung": self.show_person,
            "Startzeit": self.show_start,
            "Zielzeit": self.show_ziel,
            "Rangliste": self.show_rangliste
        }

        self.menu_widgets = {}
        for i, (label, func) in enumerate(self.menu_buttons.items(), start=1):
            btn = ctk.CTkButton(self.sidebar, text=label, command=func)
            btn.grid(row=i, column=0, padx=10, pady=5, sticky="ew")
            self.menu_widgets[label] = btn

        # Content Frame
        self.content = ctk.CTkFrame(self)
        self.content.grid(row=0, column=1, sticky="nswe")

        self.current_frame = None

    def toggle_sidebar(self):
        if self.sidebar.winfo_ismapped():
            self.sidebar.grid_remove()
        else:
            self.sidebar.grid()

    def clear_content(self):
        if self.current_frame:
            self.current_frame.destroy()

    # Platzhalterfunktionen für jede Seite
    def show_rfid(self):
        self.clear_content()
        self.current_frame = RFIDZuordnungFrame(self.content)
        self.current_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def show_person(self):
        self.clear_content()
        self.current_frame = PersonenanmeldungFrame(self.content)
        self.current_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def show_start(self):
        self.clear_content()
        self.current_frame = StartzeitErfassungFrame(self.content)
        self.current_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def show_ziel(self):
        self.clear_content()
        self.current_frame = ZielzeitErfassungFrame(self.content)
        self.current_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def show_rangliste(self):
        self.clear_content()
        self.current_frame = RanglisteFrame(self.content)
        self.current_frame.pack(fill="both", expand=True, padx=20, pady=20)


if __name__ == "__main__":
    app = VeloApp()
    app.mainloop()
