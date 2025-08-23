import customtkinter as ctk
import pandas as pd
import os
from datetime import datetime, timedelta
from tkinter import messagebox

TABELLEN_ORDNER = "Datenbank"
AUSGABE_DATEI = os.path.join(TABELLEN_ORDNER, "Rangliste.csv")

class RanglisteFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.label = ctk.CTkLabel(self, text="Ranglistenerstellung", font=("Arial", 20))
        self.label.grid(row=0, column=0, pady=10)

        self.generieren_button = ctk.CTkButton(self, text="Rangliste generieren", command=self.generiere_rangliste)
        self.generieren_button.grid(row=1, column=0, pady=10)

        self.anzeige = ctk.CTkTextbox(self)
        self.anzeige.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)

    def generiere_rangliste(self):
        start_files = [f for f in os.listdir(TABELLEN_ORDNER) if f.startswith("Zeitmessung_Start")]
        ziel_files = [f for f in os.listdir(TABELLEN_ORDNER) if f.startswith("Zeitmessung_Ziel")]

        if not start_files or not ziel_files:
            messagebox.showerror("Fehler", "Start- oder Zielzeit-Datei(en) fehlen.")
            return

        start_df = pd.read_csv(os.path.join(TABELLEN_ORDNER, start_files[-1]), sep=';', encoding="utf-8-sig", dtype=str)
        ziel_df = pd.read_csv(os.path.join(TABELLEN_ORDNER, ziel_files[-1]), sep=';', encoding="utf-8-sig", dtype=str)

        merged = pd.merge(start_df, ziel_df, on="Startnummer", suffixes=("_start", "_ziel"))

        def berechne_zeit_formatiert(row):
            try:
                t1 = datetime.strptime(row["Startzeit"], "%H:%M:%S.%f")
                t2 = datetime.strptime(row["Zielzeit"], "%H:%M:%S.%f")
                delta = t2 - t1
                if delta < timedelta(0):
                    return None
                total_seconds = delta.total_seconds()
                minutes = int(total_seconds // 60)
                seconds = int(total_seconds % 60)
                hundredths = int((total_seconds - int(total_seconds)) * 100)
                return f"{minutes:02}:{seconds:02}:{hundredths:02}"
            except Exception:
                return None

        merged["Rennzeit"] = merged.apply(berechne_zeit_formatiert, axis=1)
        merged = merged.dropna(subset=["Rennzeit"])
        merged = merged.sort_values(by="Rennzeit").reset_index(drop=True)
        merged["Rang"] = merged.index + 1

        rangliste = merged[["Rang", "Vorname_ziel", "Nachname_ziel", "Jahrgang_ziel", "Wohnort_ziel", "Rennzeit"]]
        rangliste.columns = ["Rang", "Vorname", "Nachname", "Jahrgang", "Wohnort", "Rennzeit"]

        rangliste.to_csv(AUSGABE_DATEI, sep=';', index=False, encoding="utf-8-sig")
        self.anzeige.delete("1.0", "end")
        self.anzeige.insert("1.0", rangliste.to_string(index=False))
