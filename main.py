import customtkinter as ctk
from tkinter import ttk
import tkinter as tk
from PIL import Image, ImageTk
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

def show_splash(duration: int = 2000) -> None:
    splash = tk.Tk()
    splash.overrideredirect(True)
    splash.iconbitmap("vcm_start.ico")

    image = Image.open("vcm_start.ico")
    photo = ImageTk.PhotoImage(image)
    label = tk.Label(splash, image=photo)
    label.image = photo
    label.pack(padx=0, pady=0)

    text = tk.Label(splash, text="developed by Joel Zahner 2025", font=("Arial", 10))
    text.pack()

    splash.update_idletasks()
    width = splash.winfo_width()
    height = splash.winfo_height()
    x = (splash.winfo_screenwidth() // 2) - (width // 2)
    y = (splash.winfo_screenheight() // 2) - (height // 2)
    splash.geometry(f"+{x}+{y}")

    splash.after(duration, splash.destroy)
    splash.mainloop()

class VeloApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("VCM Zeitmessung")
        self.geometry("1000x600")
        self.iconbitmap("vcm.ico")

        # Layout-Konfiguration
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Content Frame
        self.content = ctk.CTkFrame(self)
        self.content.grid(row=0, column=0, sticky="nswe")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        # Zentrales Menü
        self.menu_buttons = {
            "RFID-Zuordnung": self.show_rfid,
            "Anmeldung": self.show_person,
            "Startzeit Flach": self.show_start_flach,
            "Startzeit Berg": self.show_start_berg,
            "Zielzeit Flach": self.show_ziel_flach,
            "Zielzeit Berg": self.show_ziel_berg,
            "Rangliste": self.show_rangliste,
        }

        self.menu_frame = ctk.CTkFrame(self.content)
        self.menu_frame.pack(expand=True)
        self.menu_frame.grid_columnconfigure((0, 1), weight=1)

        for i, (label, func) in enumerate(self.menu_buttons.items()):
            btn = ctk.CTkButton(self.menu_frame, text=label, command=func, height=60)
            btn.grid(row=i // 2, column=i % 2, padx=10, pady=10, sticky="nsew")

        self.current_frame = None

    def clear_content(self):
        if self.current_frame:
            self.current_frame.destroy()

    # Platzhalterfunktionen für jede Seite
    def show_rfid(self):
        self.menu_frame.pack_forget()
        self.clear_content()
        self.current_frame = RFIDZuordnungFrame(self.content)
        self.current_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def show_person(self):
        self.menu_frame.pack_forget()
        self.clear_content()
        self.current_frame = anmeldungFrame(self.content)
        self.current_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def show_start_flach(self):
        self.menu_frame.pack_forget()
        self.clear_content()
        self.current_frame = StartzeitFlachErfassungFrame(self.content)
        self.current_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def show_start_berg(self):
        self.menu_frame.pack_forget()
        self.clear_content()
        self.current_frame = StartzeitBergErfassungFrame(self.content)
        self.current_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def show_ziel_flach(self):
        self.menu_frame.pack_forget()
        self.clear_content()
        self.current_frame = ZielzeitFlachErfassungFrame(self.content)
        self.current_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def show_ziel_berg(self):
        self.menu_frame.pack_forget()
        self.clear_content()
        self.current_frame = ZielzeitBergErfassungFrame(self.content)
        self.current_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def show_rangliste(self):
        self.menu_frame.pack_forget()
        self.clear_content()
        self.current_frame = RanglisteFrame(self.content)
        self.current_frame.pack(fill="both", expand=True, padx=20, pady=20)


if __name__ == "__main__":
    show_splash()
    app = VeloApp()
    app.mainloop()
