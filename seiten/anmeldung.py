import customtkinter as ctk
import pandas as pd
import os
from tkinter import messagebox

CSV_PATH = os.path.join("Datenbank", "Anmeldung.csv")
SPALTEN = [
    "Startnummer",
    "Vorname",
    "Nachname",
    "Jahrgang",
    "Wohnort",
    "Geschlecht",
    "Clubmitglied",
]

class anmeldungFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        os.makedirs("Datenbank", exist_ok=True)
        self.daten = self.lade_csv()

        self.label = ctk.CTkLabel(self, text="Anmeldung", font=("Arial", 20))
        self.label.grid(row=0, column=0, pady=10)

        self.tabelle = ctk.CTkTextbox(self, height=400)
        self.tabelle.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.update_tabelle()

        self.hinzufuegen_button = ctk.CTkButton(self, text="Neue Person hinzufügen", command=self.neue_person)
        self.hinzufuegen_button.grid(row=2, column=0, pady=10)

    def lade_csv(self):
        if os.path.exists(CSV_PATH):
            df = pd.read_csv(CSV_PATH, sep=";", dtype=str, encoding="utf-8-sig")
            for col in SPALTEN:
                if col not in df.columns:
                    df[col] = ""
            return df[SPALTEN]
        return pd.DataFrame(columns=SPALTEN)

    def speichere_csv(self):
        self.daten.to_csv(CSV_PATH, sep=';', index=False, encoding="utf-8-sig")

    def update_tabelle(self):
        self.tabelle.delete("1.0", "end")
        if self.daten.empty:
            self.tabelle.insert("1.0", "Noch keine Personen erfasst.")
        else:
            self.tabelle.insert("1.0", self.daten.to_string(index=False))

    def neue_person(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Neue Person")
        popup.geometry("400x350")

        eintraege = {}
        for i, feld in enumerate(SPALTEN):
            label = ctk.CTkLabel(popup, text=feld + ":")
            label.grid(row=i, column=0, padx=10, pady=5, sticky="e")

            if feld == "Geschlecht":
                var = ctk.StringVar(value="")
                rb_m = ctk.CTkRadioButton(popup, text="Männlich", variable=var, value="Männlich")
                rb_m.grid(row=i, column=1, padx=10, pady=5, sticky="w")
                rb_w = ctk.CTkRadioButton(popup, text="Weiblich", variable=var, value="Weiblich")
                rb_w.grid(row=i, column=2, padx=10, pady=5, sticky="w")
                eintraege[feld] = var
            elif feld == "Clubmitglied":
                var = ctk.StringVar(value="")
                rb_ja = ctk.CTkRadioButton(popup, text="Ja", variable=var, value="Ja")
                rb_ja.grid(row=i, column=1, padx=10, pady=5, sticky="w")
                rb_nein = ctk.CTkRadioButton(popup, text="Nein", variable=var, value="Nein")
                rb_nein.grid(row=i, column=2, padx=10, pady=5, sticky="w")
                eintraege[feld] = var
            else:
                entry = ctk.CTkEntry(popup)
                entry.grid(row=i, column=1, padx=10, pady=5, sticky="w")
                eintraege[feld] = entry

        def speichern():
            werte = {feld: eintraege[feld].get().strip() for feld in SPALTEN}

            if not all(werte.values()):
                messagebox.showerror("Fehler", "Alle Felder müssen ausgefüllt sein.")
                return

            if werte["Startnummer"] in self.daten["Startnummer"].values:
                messagebox.showerror("Fehler", f"Startnummer {werte['Startnummer']} ist bereits vergeben.")
                return

            # Formatierung
            werte["Vorname"] = werte["Vorname"].capitalize()
            werte["Nachname"] = werte["Nachname"].capitalize()
            werte["Wohnort"] = werte["Wohnort"].capitalize()

            self.daten.loc[len(self.daten)] = werte
            self.speichere_csv()
            self.update_tabelle()
            popup.destroy()

        speichern_button = ctk.CTkButton(popup, text="Speichern", command=speichern)
        speichern_button.grid(row=len(SPALTEN), column=0, columnspan=2, pady=10)

        popup.grab_set()
        popup.wait_window()
