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

        # Buttons zum Bestätigen und Starten
        self.confirm_button = ctk.CTkButton(
            self, text="Nummern bestätigen", command=self.bestaetige_nummern
        )
        self.confirm_button.pack(pady=10)

        self.start_button = ctk.CTkButton(
            self,
            text="Start!",
            command=self.schreibe_startzeit,
            height=100,
            width=300,
            state=ctk.DISABLED,
        )
        self.start_button.pack(pady=10)

        self.info_label = ctk.CTkLabel(self, text="", font=("Arial", 16))
        self.info_label.pack(pady=10)

        self.bestaetigte_nummern = None

    def lade_anmeldedaten(self):
        if not os.path.exists(ANMELDUNG_PATH):
            messagebox.showerror("Fehler", f"Datei {ANMELDUNG_PATH} nicht gefunden.")
            return pd.DataFrame(columns=["Startnummer", "Vorname", "Nachname", "Jahrgang", "Wohnort"])
        return pd.read_csv(ANMELDUNG_PATH, sep=';', dtype=str, encoding="utf-8-sig")

    def bestaetige_nummern(self):
        startnummern_text = self.entry.get().strip()
        if not startnummern_text:
            messagebox.showerror("Fehler", "Bitte Startnummern eingeben.")
            return

        raw_nums = [s.strip() for s in startnummern_text.replace(";", ",").split(",")]
        startnummern = [n for n in raw_nums if n]

        bereits_gestartet = []
        nicht_gefunden = []
        for nummer in startnummern:
            if nummer in self.startdaten["Startnummer"].astype(str).values:
                bereits_gestartet.append(nummer)
            elif self.anmeldedaten[self.anmeldedaten["Startnummer"] == nummer].empty:
                nicht_gefunden.append(nummer)

        if bereits_gestartet or nicht_gefunden:
            meldung = []
            if nicht_gefunden:
                meldung.append("Nicht gefunden: " + ", ".join(nicht_gefunden))
            if bereits_gestartet:
                meldung.append("Bereits gestartet: " + ", ".join(bereits_gestartet))
            messagebox.showerror("Fehler", "\n".join(meldung))
            self.start_button.configure(state=ctk.DISABLED)
            self.bestaetigte_nummern = None
        else:
            self.bestaetigte_nummern = startnummern
            self.start_button.configure(state=ctk.NORMAL)
            self.entry.configure(state=ctk.DISABLED)

    def schreibe_startzeit(self):
        if not self.bestaetigte_nummern:
            messagebox.showerror("Fehler", "Bitte Startnummern bestätigen.")
            return

        now = datetime.now().strftime("%H:%M:%S.%f")[:-4]

        gestartete = []
        for nummer in self.bestaetigte_nummern:
            person = self.anmeldedaten[self.anmeldedaten["Startnummer"] == nummer]
            if not person.empty:
                daten = person.iloc[0].to_dict()
                daten["Startzeit"] = now
                self.startdaten.loc[len(self.startdaten)] = daten
                gestartete.append((nummer, daten["Vorname"], daten["Nachname"]))

        self.startdaten.to_csv(self.filename, index=False, sep=";", encoding="utf-8-sig")
        self.entry.configure(state=ctk.NORMAL)
        self.entry.delete(0, ctk.END)
        self.start_button.configure(state=ctk.DISABLED)
        self.bestaetigte_nummern = None

        if gestartete:
            spaltenbreiten = [max(len(str(row[i])) for row in gestartete) for i in range(3)]
            zeilen = [
                f"{nr:<{spaltenbreiten[0]}} {vn:<{spaltenbreiten[1]}} {nn:<{spaltenbreiten[2]}}"
                for nr, vn, nn in gestartete
            ]
            info = "Gestartet:\n" + "\n".join(zeilen)
        else:
            info = ""
        self.info_label.configure(text=info)
