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

        current_year = datetime.now().year
        junior_year = current_year - 15
        nachwuchs_year = current_year - 12

        merged["Jahrgang"] = pd.to_numeric(merged.get("Jahrgang_start"), errors="coerce")
        merged["Geschlecht"] = merged.get("Geschlecht_start")
        merged["Clubmitglied"] = merged.get("Clubmitglied_start")

        def bestimme_kategorie(row):
            jahrgang = row["Jahrgang"]
            geschlecht = row["Geschlecht"]
            club = row["Clubmitglied"]
            if club != "Ja":
                return "Gäste Herren" if geschlecht == "Männlich" else "Gäste Damen"
            if geschlecht == "Männlich":
                if jahrgang == junior_year:
                    return "Junioren"
                if jahrgang == nachwuchs_year:
                    return "Nachwuchs Knaben"
                return "Herren"
            else:
                if jahrgang == junior_year:
                    return "Juniorinnen"
                if jahrgang == nachwuchs_year:
                    return "Nachwuchs Mädchen"
                return "Damen"

        merged["Kategorie"] = merged.apply(bestimme_kategorie, axis=1)

        kategorie_order = [
            "Herren",
            "Junioren",
            "Nachwuchs Knaben",
            "Gäste Herren",
            "Damen",
            "Juniorinnen",
            "Nachwuchs Mädchen",
            "Gäste Damen",
        ]

        merged["Kategorie"] = pd.Categorical(
            merged["Kategorie"], categories=kategorie_order, ordered=True
        )
        merged = merged.sort_values(["Kategorie", "Rennzeit"])
        merged["Rang"] = merged.groupby("Kategorie").cumcount() + 1

        rangliste = merged[
            [
                "Kategorie",
                "Rang",
                "Vorname_ziel",
                "Nachname_ziel",
                "Jahrgang",
                "Wohnort_ziel",
                "Rennzeit",
            ]
        ]
        rangliste.columns = [
            "Kategorie",
            "Rang",
            "Vorname",
            "Nachname",
            "Jahrgang",
            "Wohnort",
            "Rennzeit",
        ]

        rangliste.to_csv(AUSGABE_DATEI, sep=';', index=False, encoding="utf-8-sig")
        self.anzeige.delete("1.0", "end")
        anzeige_text = ""
        for kat in kategorie_order:
            df_kat = rangliste[rangliste["Kategorie"] == kat]
            if df_kat.empty:
                continue
            anzeige_text += f"{kat}\n"
            anzeige_text += (
                df_kat.drop(columns=["Kategorie"]).to_string(index=False) + "\n\n"
            )
        self.anzeige.insert("1.0", anzeige_text.strip())
