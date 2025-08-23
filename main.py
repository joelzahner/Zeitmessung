import customtkinter as ctk
from tkinter import ttk
import os

from seiten.rfid_zuordnung import RFIDZuordnungFrame
from seiten.anmeldung import anmeldungFrame
from seiten.startzeit_flach import StartzeitFlachErfassungFrame
from seiten.startzeit_berg import StartzeitBergErfassungFrame
from seiten.zielzeit_flach import ZielzeitFlachErfassungFrame
from seiten.zielzeit_berg import ZielzeitBergErfassungFrame
from seiten.rangliste import RanglisteFrame
from openpyxl.worksheet.header_footer import HeaderFooter


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
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=7)
        self.sidebar.grid(row=0, column=0, sticky="nswe")
        self.sidebar.grid_rowconfigure(7, weight=1)

        self.menu_buttons = {
            "RFID-Zuordnung": self.show_rfid,
            "Anmeldung": self.show_person,
            "Startzeit Flach": self.show_start_flach,
            "Startzeit Berg": self.show_start_berg,
            "Zielzeit Flach": self.show_ziel_flach,
            "Zielzeit Berg": self.show_ziel_berg,
            "Rangliste": self.show_rangliste,
        }

        self.menu_widgets = {}
        for i, (label, func) in enumerate(self.menu_buttons.items(), start=0):
            btn = ctk.CTkButton(self.sidebar, text=label, command=func)
            btn.grid(row=i, column=0, padx=10, pady=5, sticky="ew")
            self.menu_widgets[label] = btn

        # Content Frame
        self.content = ctk.CTkFrame(self)
        self.content.grid(row=0, column=1, sticky="nswe")

        self.current_frame = None

    def clear_content(self):
        if self.current_frame:
            self.current_frame.destroy()

    # Platzhalterfunktionen für jede Seite
    def show_rfid(self):
        self.sidebar.grid_remove()
        self.clear_content()
        self.current_frame = RFIDZuordnungFrame(self.content)
        self.current_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def show_person(self):
        self.sidebar.grid_remove()
        self.clear_content()
        self.current_frame = anmeldungFrame(self.content)
        self.current_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def show_start_flach(self):
        self.sidebar.grid_remove()
        self.clear_content()
        self.current_frame = StartzeitFlachErfassungFrame(self.content)
        self.current_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def show_start_berg(self):
        self.sidebar.grid_remove()
        self.clear_content()
        self.current_frame = StartzeitBergErfassungFrame(self.content)
        self.current_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def show_ziel_flach(self):
        self.sidebar.grid_remove()
        self.clear_content()
        self.current_frame = ZielzeitFlachErfassungFrame(self.content)
        self.current_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def show_ziel_berg(self):
        self.sidebar.grid_remove()
        self.clear_content()
        self.current_frame = ZielzeitBergErfassungFrame(self.content)
        self.current_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def show_rangliste(self):
        self.sidebar.grid_remove()
        self.clear_content()
        self.current_frame = RanglisteFrame(self.content)
        self.current_frame.pack(fill="both", expand=True, padx=20, pady=20)


if __name__ == "__main__":
    app = VeloApp()
    app.mainloop()
