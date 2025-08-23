import customtkinter as ctk
import serial
import serial.tools.list_ports
import threading
import pandas as pd
from datetime import datetime
import os
from tkinter import messagebox
import winsound

CSV_MAPPING_PATH = os.path.join("Datenbank", "Zuordnung_RFID.csv")
TABELLEN_ORDNER = "Datenbank"
BAUDRATE = 115200

# Erfassung der Zielzeiten für das Flachrennen
class ZielzeitFlachErfassungFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.serial_port = None
        self.thread = None
        self.gelesene_tags = set()
        self.tag_mapping = self.lade_tag_mapping()
        self.personen_df = self.lade_personen()

        # Spaltenbreiten für eine übersichtliche Anzeige berechnen
        if self.personen_df.empty:
            self.spaltenbreiten = {"Startnummer": len("Startnummer"), "Vorname": len("Vorname"), "Nachname": len("Nachname")}
        else:
            self.spaltenbreiten = {
                col: max(self.personen_df[col].astype(str).map(len).max(), len(col))
                for col in ["Startnummer", "Vorname", "Nachname"]
            }

        self.data = pd.DataFrame(
            columns=["Startnummer", "Vorname", "Nachname", "Jahrgang", "Wohnort", "Datum", "Zielzeit"]
        )
        os.makedirs(TABELLEN_ORDNER, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        # Datei für das Flachrennen
        self.filename = os.path.join(
            TABELLEN_ORDNER, f"Zeitmessung_Ziel_Flach_{timestamp}.csv"
        )
        self.data.to_csv(self.filename, index=False, sep=';', encoding="utf-8-sig")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.label = ctk.CTkLabel(self, text="Zielzeit-Erfassung Flach", font=("Arial", 20))
        self.label.grid(row=0, column=0, pady=10)

        self.port_combobox = ctk.CTkComboBox(self, values=self.list_ports())
        self.port_combobox.set(self.auto_selected_port)
        self.port_combobox.grid(row=1, column=0, padx=10, pady=5)

        self.start_button = ctk.CTkButton(self, text="Starten", command=self.start_reading)
        self.start_button.grid(row=2, column=0, pady=10)

        self.anzeige = ctk.CTkTextbox(self)
        self.anzeige.grid(row=3, column=0, sticky="nsew", padx=10, pady=5)

    def list_ports(self):
        ports = serial.tools.list_ports.comports()
        port_list = [port.device for port in ports]
        self.auto_selected_port = ""
        for port in ports:
            if "USB" in port.description or "Arduino" in port.description or "Silicon" in port.description:
                self.auto_selected_port = port.device
                break
        else:
            if port_list:
                self.auto_selected_port = port_list[0]
        return port_list

    def lade_tag_mapping(self):
        if os.path.exists(CSV_MAPPING_PATH):
            df = pd.read_csv(CSV_MAPPING_PATH, sep=';', dtype=str, encoding="utf-8-sig")
            return {row["Tag"]: row["Startnummer"] for _, row in df.iterrows()}
        return {}

    def lade_personen(self):
        path = os.path.join("Datenbank", "Anmeldung.csv")
        if os.path.exists(path):
            return pd.read_csv(path, sep=';', dtype=str, encoding="utf-8-sig")
        return pd.DataFrame(columns=["Startnummer", "Vorname", "Nachname", "Jahrgang", "Wohnort"])

    def start_reading(self):
        port = self.port_combobox.get()
        if not port:
            messagebox.showerror("Fehler", "Kein COM-Port ausgewählt.")
            return

        self.serial_port = port
        self.anzeige.insert("1.0", f"Verbindung zu {port} hergestellt...\n")
        self.thread = threading.Thread(target=self.read_serial, daemon=True)
        self.thread.start()

    def read_serial(self):
        try:
            with serial.Serial(self.serial_port, BAUDRATE, timeout=1) as ser:
                while True:
                    line = ser.readline().decode("utf-8").strip()
                    if line:
                        if self.check_for_error(line):
                            continue
                        tag = line.upper()
                        if tag in self.gelesene_tags:
                            continue
                        if tag in self.tag_mapping:
                            startnummer = self.tag_mapping[tag]
                            person = self.personen_df[self.personen_df["Startnummer"] == startnummer]

                            if person.empty:
                                self.anzeige.insert("end", f"{startnummer} → Keine Personendaten gefunden\n")
                                self.anzeige.see("end")
                                continue

                            daten = person.iloc[0]  # Series
                            now = datetime.now()
                            date_str = now.strftime("%Y-%m-%d")
                            time_str = now.strftime("%H:%M:%S.%f")[:-4]

                            zeile = [
                                startnummer,
                                daten["Vorname"],
                                daten["Nachname"],
                                daten["Jahrgang"],
                                daten["Wohnort"],
                                date_str,
                                time_str
                            ]
                            self.data.loc[len(self.data)] = zeile
                            self.data.to_csv(self.filename, index=False, sep=';', encoding="utf-8-sig")

                            self.gelesene_tags.add(tag)
                            self.anzeige.insert(
                                "end",
                                f"{daten[0]:<{self.spaltenbreiten['Startnummer']}} "
                                f"{daten[1]:<{self.spaltenbreiten['Vorname']}} "
                                f"{daten[2]:<{self.spaltenbreiten['Nachname']}} {time_str}\n",
                            )
                            self.anzeige.see("end")
                            winsound.Beep(2000, 200)
        except serial.SerialException as e:
            messagebox.showerror("Serial Fehler", str(e))

    def check_for_error(self, line):
        errors = ["Module failed to respond", "Bad CRC", "High return loss", "Unknown error"]
        return any(err in line for err in errors)
