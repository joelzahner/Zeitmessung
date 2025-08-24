import customtkinter as ctk
import threading
import serial
import serial.tools.list_ports
import pandas as pd
import os
from tkinter import messagebox
from datetime import datetime

from paths import data_dir
DATA_DIR = data_dir()

BAUDRATE = 115200
CSV_PATH = os.path.join(DATA_DIR, "Zuordnung_RFID.csv")

class RFIDZuordnungFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.serial_port = None
        self.auto_selected_port = ""
        self.assigning = False
        self.tag_mapping = self.load_mapping()

        # UI Setup
        self.grid_columnconfigure(0, weight=1)

        self.info_label = ctk.CTkLabel(self, text="RFID-Zuordnung", font=("Arial", 20))
        self.info_label.pack(pady=10)

        self.port_combobox = ctk.CTkComboBox(self, values=self.list_serial_ports())
        self.port_combobox.set(self.auto_selected_port)
        self.port_combobox.pack(pady=5)

        self.start_button = ctk.CTkButton(self, text="Starten", command=self.start)
        self.start_button.pack(pady=10)

        self.output_box = ctk.CTkTextbox(self, height=300)
        self.output_box.pack(fill="both", expand=True, padx=10, pady=10)

        self.counter_label = ctk.CTkLabel(self, text=f"Zugeordnete Tags: {len(self.tag_mapping)}")
        self.counter_label.pack(pady=5)

        os.makedirs(DATA_DIR, exist_ok=True)

    def list_serial_ports(self):
        ports = serial.tools.list_ports.comports()
        port_list = [port.device for port in ports]
        for port in ports:
            if "USB" in port.description or "Arduino" in port.description or "Silicon" in port.description:
                self.auto_selected_port = port.device
                break
        else:
            self.auto_selected_port = port_list[0] if port_list else ""
        return port_list

    def load_mapping(self):
        if os.path.exists(CSV_PATH):
            df = pd.read_csv(CSV_PATH, sep=';', dtype=str, encoding="utf-8-sig")
            return {row['Tag']: row['Startnummer'] for _, row in df.iterrows()}
        return {}


    def save_mapping(self):
        df = pd.DataFrame([
            {'Tag': tag, 'Startnummer': startnummer}
            for tag, startnummer in self.tag_mapping.items()
        ])
        df.to_csv(CSV_PATH, index=False, sep=';', encoding="utf-8-sig")


    def start(self):
        port = self.port_combobox.get()
        if not port:
            messagebox.showerror("Fehler", "Kein COM-Port ausgewählt.")
            return
        self.serial_port = port
        self.output_box.insert("1.0", "Bereit: Halte einen RFID-Tag an das Lesegerät...\n")
        threading.Thread(target=self.read_serial_loop, daemon=True).start()

    def read_serial_loop(self):
        try:
            with serial.Serial(self.serial_port, BAUDRATE, timeout=1) as ser:
                while True:
                    if self.assigning:
                        continue
                    line = ser.readline().decode("utf-8").strip()
                    if line:
                        if self.check_for_error(line):
                            continue
                        tag = line.upper()
                        if tag in self.tag_mapping:
                            self.output_box.insert("end", f"{tag} bereits registriert\n")
                            self.output_box.see("end")
                            continue
                        self.assigning = True
                        ser.reset_input_buffer()
                        startnummer = self.show_formular(tag)
                        if startnummer:
                            self.tag_mapping[tag] = startnummer
                            self.save_mapping()
                            self.output_box.insert("end", f"{tag} → Startnummer {startnummer}\n")
                            self.counter_label.configure(text=f"Zugeordnete Tags: {len(self.tag_mapping)}")
                        self.assigning = False
        except serial.SerialException as e:
            messagebox.showerror("Serial Fehler", str(e))

    def show_formular(self, tag):
        form = ctk.CTkToplevel(self)
        form.title("Neue Zuordnung")
        form.geometry("400x300")
        fields = ["Startnummer"]
        entries = {}

        for i, field in enumerate(fields):
            label = ctk.CTkLabel(form, text=field)
            label.grid(row=i, column=0, padx=10, pady=5, sticky="e")
            entry = ctk.CTkEntry(form)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries[field] = entry

        result = {}

        def submit():
            for field in fields:
                value = entries[field].get().strip()
                if not value:
                    messagebox.showerror("Fehler", f"{field} darf nicht leer sein.")
                    return
                if field in ["Vorname", "Nachname", "Wohnort"]:
                    value = value.capitalize()
                result[field] = value

            # Duplikatsprüfung
            for _, existing in self.tag_mapping.items():
                if existing[0] == result["Startnummer"]:
                    messagebox.showerror("Fehler", f"Startnummer {result['Startnummer']} existiert bereits.")
                    return

            form.destroy()

        button = ctk.CTkButton(form, text="OK", command=submit)
        button.grid(row=len(fields), column=0, columnspan=2, pady=10)

        form.grab_set()
        form.wait_window()
        return result["Startnummer"] if result else None

    def check_for_error(self, line):
        errors = ["Module failed to respond", "Bad CRC", "High return loss", "Unknown error"]
        return any(err in line for err in errors)
