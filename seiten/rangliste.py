import customtkinter as ctk
import pandas as pd
import os
from datetime import datetime, timedelta
from tkinter import messagebox
from openpyxl.worksheet.header_footer import HeaderFooter

TABELLEN_ORDNER = "Datenbank"
AUSGABE_DATEI = os.path.join(TABELLEN_ORDNER, "Rangliste.xlsx")
DISTANZ_M = 8480  # Streckenlänge in Metern

KATEGORIEN_REIHENFOLGE = [
    "Herren",
    "Damen",
    "Junioren",
    "Juniorinnen",
    "Nachwuchs Knaben",
    "Nachwuchs Mädchen",
    "Gäste Herren",
    "Gäste Damen",
]

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

        start_df = pd.read_csv(
            os.path.join(TABELLEN_ORDNER, start_files[-1]),
            sep=";",
            encoding="utf-8-sig",
            dtype=str,
        )
        ziel_df = pd.read_csv(
            os.path.join(TABELLEN_ORDNER, ziel_files[-1]),
            sep=";",
            encoding="utf-8-sig",
            dtype=str,
        )

        merged = pd.merge(start_df, ziel_df, on="Startnummer", suffixes=("_start", "_ziel"))

        def berechne_zeit(row):
            try:
                t1 = datetime.strptime(row["Startzeit"], "%H:%M:%S.%f")
                t2 = datetime.strptime(row["Zielzeit"], "%H:%M:%S.%f")
                delta = t2 - t1
                if delta < timedelta(0):
                    return pd.Series([None, None])
                total_seconds = delta.total_seconds()
                minutes = int(total_seconds // 60)
                seconds = int(total_seconds % 60)
                hundredths = int((total_seconds - int(total_seconds)) * 100)
                formatted = f"{minutes:02}:{seconds:02}:{hundredths:02}"
                return pd.Series([formatted, total_seconds])
            except Exception:
                return pd.Series([None, None])

        merged[["Rennzeit", "Rennzeit_Sekunden"]] = merged.apply(berechne_zeit, axis=1)
        merged = merged.dropna(subset=["Rennzeit"])
        merged["km/h"] = (DISTANZ_M / merged["Rennzeit_Sekunden"]) * 3.6

        aktuelles_jahr = datetime.now().year
        junior_jahrgang = aktuelles_jahr - 15
        nachwuchs_jahrgang = aktuelles_jahr - 12

        def bestimme_kategorie(row):
            geschlecht = row.get("Geschlecht", "")
            club = row.get("Clubmitglied", "")
            jahrgang_str = row.get("Jahrgang_start") or row.get("Jahrgang_ziel") or "0"
            try:
                jahrgang = int(jahrgang_str)
            except ValueError:
                jahrgang = 0

            if club != "Ja":
                return "Gäste Herren" if geschlecht == "Männlich" else "Gäste Damen"

            if geschlecht == "Männlich":
                if jahrgang >= nachwuchs_jahrgang:
                    return "Nachwuchs Knaben"
                if jahrgang >= junior_jahrgang:
                    return "Junioren"
                return "Herren"
            else:
                if jahrgang >= nachwuchs_jahrgang:
                    return "Nachwuchs Mädchen"
                if jahrgang >= junior_jahrgang:
                    return "Juniorinnen"
                return "Damen"

        merged["Kategorie"] = merged.apply(bestimme_kategorie, axis=1)

        kategorien_dfs = {}
        for kat in KATEGORIEN_REIHENFOLGE:
            df_kat = merged[merged["Kategorie"] == kat].copy()
            if df_kat.empty:
                continue
            df_kat = df_kat.sort_values(by="Rennzeit_Sekunden").reset_index(drop=True)
            df_kat["Rang"] = df_kat.index + 1
            df_kat.rename(
                columns={
                    "Vorname_ziel": "Vorname",
                    "Nachname_ziel": "Nachname",
                    "Jahrgang_ziel": "Jahrgang",
                    "Wohnort_ziel": "Wohnort",
                },
                inplace=True,
            )
            df_kat["km/h"] = df_kat["km/h"].round(2)
            df_kat = df_kat[["Rang", "Vorname", "Nachname", "Jahrgang", "Wohnort", "Rennzeit", "km/h"]]
            kategorien_dfs[kat] = df_kat

        with pd.ExcelWriter(AUSGABE_DATEI, engine="openpyxl") as writer:
            startrow = 0
            for kat, df_kat in kategorien_dfs.items():
                df_kat.to_excel(writer, sheet_name="Rangliste", startrow=startrow + 1, index=False)
                sheet = writer.sheets["Rangliste"]
                sheet.cell(row=startrow + 1, column=1, value=kat)
                startrow += len(df_kat) + 3

            # Seitenlayout + Kopfzeile setzen
            ws = writer.sheets["Rangliste"]
            ws.sheet_view.view = "pageLayout"  # Seitenlayout

            h = ws.oddHeader
            h.left.text = "XX. Flachrennen"
            h.left.size = 20


        text_output = ""
        for kat, df_kat in kategorien_dfs.items():
            text_output += f"{kat}\n"
            text_output += df_kat.to_string(index=False)
            text_output += "\n\n"

        self.anzeige.delete("1.0", "end")
        self.anzeige.insert("1.0", text_output.strip())
