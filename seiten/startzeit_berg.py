import customtkinter as ctk
import pandas as pd
from datetime import datetime
import os
from tkinter import messagebox

ANMELDUNG_PATH = os.path.join("Datenbank", "Anmeldung.csv")
TABELLEN_ORDNER = "Datenbank"

# Erfassung der Startzeiten für das Bergrennen
class StartzeitBergErfassungFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)

        self.anmeldedaten = self.lade_anmeldedaten()

        # DataFrame zum Speichern der Startzeiten
        self.startdaten = pd.DataFrame(
            columns=list(self.anmeldedaten.columns) + ["Startzeit"]
        )
        os.makedirs(TABELLEN_ORDNER, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        self.filename = os.path.join(
            TABELLEN_ORDNER, f"Zeitmessung_Start_Berg_{timestamp}.csv"
        )
        self.startdaten.to_csv(self.filename, index=False, sep=";", encoding="utf-8-sig")

        # GUI Elemente
        self.entry_label = ctk.CTkLabel(self, text="Startnummern (Komma getrennt)")
        self.entry_label.pack(pady=10)

        self.entry = ctk.CTkEntry(self, width=300)
        self.entry.pack(pady=10)

        self.start_button = ctk.CTkButton(
            self, text="Start!", command=self.schreibe_startzeit, height=100, width=300
        )
        self.start_button.pack(pady=10)

        self.info_label = ctk.CTkLabel(self, text="", font=("Arial", 16))
        self.info_label.pack(pady=10)

    def lade_anmeldedaten(self):
        if not os.path.exists(ANMELDUNG_PATH):
            messagebox.showerror("Fehler", f"Datei {ANMELDUNG_PATH} nicht gefunden.")
            return pd.DataFrame(columns=["Startnummer", "Vorname", "Nachname", "Jahrgang", "Wohnort"])
        return pd.read_csv(ANMELDUNG_PATH, sep=';', dtype=str, encoding="utf-8-sig")

    def schreibe_startzeit(self):
        startnummern_text = self.entry.get().strip()
        if not startnummern_text:
            messagebox.showerror("Fehler", "Bitte Startnummern eingeben.")
            return

        # Startnummern parsen (Komma oder Leerzeichen getrennt)
        raw_nums = [s.strip() for s in startnummern_text.replace(";", ",").split(",")]
        startnummern = [n for n in raw_nums if n]
        now = datetime.now().strftime("%H:%M:%S.%f")[:-4]

        gestartete = []
        nicht_gefunden = []
        for nummer in startnummern:
            person = self.anmeldedaten[self.anmeldedaten["Startnummer"] == nummer]
            if not person.empty:
                daten = person.iloc[0].to_dict()
                daten["Startzeit"] = now
                self.startdaten.loc[len(self.startdaten)] = daten
                gestartete.append(f"{nummer} {daten['Vorname']} {daten['Nachname']}")
            else:
                nicht_gefunden.append(nummer)

        self.startdaten.to_csv(self.filename, index=False, sep=";", encoding="utf-8-sig")
        self.entry.delete(0, ctk.END)

        info = "Gestartet:\n" + "\n".join(gestartete) if gestartete else ""
        if nicht_gefunden:
            info += ("\nNicht gefunden: " + ", ".join(nicht_gefunden))
        self.info_label.configure(text=info)
