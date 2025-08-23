import customtkinter as ctk
import pandas as pd
from datetime import datetime
import os
from tkinter import messagebox

ANMELDUNG_PATH = os.path.join("Datenbank", "Anmeldung.csv")
TABELLEN_ORDNER = "Datenbank"

class StartzeitErfassungFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)

        self.anmeldedaten = self.lade_anmeldedaten()
        self.index = 0

        self.startdaten = pd.DataFrame(columns=list(self.anmeldedaten.columns) + ["Startzeit"])
        os.makedirs(TABELLEN_ORDNER, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        self.filename = os.path.join(TABELLEN_ORDNER, f"Zeitmessung_Start_{timestamp}.csv")
        self.startdaten.to_csv(self.filename, index=False, sep=';', encoding="utf-8-sig")

        # GUI Elemente
        self.label = ctk.CTkLabel(self, text="", font=("Arial", 20))
        self.label.pack(pady=20)

        self.start_button = ctk.CTkButton(self, text="Start!", command=self.schreibe_startzeit, height=100, width=300)
        self.start_button.pack(pady=10)

        self.vorschau_label = ctk.CTkLabel(self, text="", font=("Arial", 16), text_color="gray")
        self.vorschau_label.pack(pady=10)

        self.zeige_naechste_person()

    def lade_anmeldedaten(self):
        if not os.path.exists(ANMELDUNG_PATH):
            messagebox.showerror("Fehler", f"Datei {ANMELDUNG_PATH} nicht gefunden.")
            return pd.DataFrame(columns=["Startnummer", "Vorname", "Nachname", "Jahrgang", "Wohnort"])
        return pd.read_csv(ANMELDUNG_PATH, sep=';', dtype=str, encoding="utf-8-sig")

    def zeige_naechste_person(self):
        if self.index < len(self.anmeldedaten):
            daten = self.anmeldedaten.iloc[self.index]
            text = "\n".join([f"{col}: {daten[col]}" for col in self.anmeldedaten.columns])
            self.label.configure(text=text)

            # Vorschau
            vorschau = []
            for i in range(1, 3):
                if self.index + i < len(self.anmeldedaten):
                    person = self.anmeldedaten.iloc[self.index + i]
                    vorschau.append(f"{person['Vorname']} {person['Nachname']}")
            self.vorschau_label.configure(text="Als Nächstes:\n" + "\n".join(vorschau) if vorschau else "")
        else:
            self.label.configure(text="Alle Personen wurden gestartet.")
            self.vorschau_label.configure(text="")
            self.start_button.configure(state="disabled")

    def schreibe_startzeit(self):
        if self.index < len(self.anmeldedaten):
            now = datetime.now().strftime("%H:%M:%S.%f")[:-4]  # Zeit auf Hundertstel
            daten = self.anmeldedaten.iloc[self.index].to_dict()
            daten["Startzeit"] = now
            self.startdaten.loc[len(self.startdaten)] = daten
            self.startdaten.to_csv(self.filename, index=False, sep=';', encoding="utf-8-sig")
            self.index += 1
            self.zeige_naechste_person()
