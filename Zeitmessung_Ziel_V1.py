import serial
import threading
import pandas as pd
import customtkinter as ctk
from datetime import datetime
import os
import serial.tools.list_ports
import winsound
import sys
from tkinter import messagebox

# Konfiguration
BAUDRATE = 115200
TAG_MAPPING_FILE = "Zuordnung RFID-Tag.csv"

# Hilfsfunktion für Ressourcenpfade (kompatibel mit PyInstaller)
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# GUI-Initialisierung
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class RFIDApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.iconbitmap(resource_path("vcm.ico"))
        self.title("Zeitmessung VCM Ziel")
        self.geometry("500x200")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.serial_port = None
        self.serial_thread = None
        self.auto_selected_port = ""
        self.data = pd.DataFrame(columns=["Startnummer", "Vorname", "Nachname", "Jahrgang", "Wohnort", "Datum", "Zielzeit"])
        self.gelesene_tags = set()
        self.tag_name_dict = self.load_tag_mapping()
        self.assigning = False

        # COM-Port Auswahl
        self.port_label = ctk.CTkLabel(self, text="Wähle COM-Port:")
        self.port_label.pack(pady=(10, 0))

        self.port_combobox = ctk.CTkComboBox(self, values=self.list_serial_ports())
        self.port_combobox.pack(pady=5)
        self.port_combobox.set(self.auto_selected_port)

        self.mode_label = ctk.CTkLabel(self, text="Modus wählen:")
        self.mode_label.pack(pady=(10, 0))

        self.mode_combobox = ctk.CTkComboBox(self, values=["Anmeldung", "Zeitmessung"])
        self.mode_combobox.pack(pady=5)

        self.start_button = ctk.CTkButton(self, text="Start", command=self.start_action)
        self.start_button.pack(pady=5)

        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.pack(fill="both", expand=True, padx=10, pady=(10, 5))

        self.table = ctk.CTkTextbox(self.table_frame, font=("Consolas", 12))
        self.table.pack(fill="both", expand=True)

        self.counter_label = ctk.CTkLabel(self, text="")

    def list_serial_ports(self):
        ports = serial.tools.list_ports.comports()
        port_list = [port.device for port in ports]
        for port in ports:
            if ("USB" in port.description or
                "Arduino" in port.description or
                "Silicon" in port.description):
                self.auto_selected_port = port.device
                break
        else:
            self.auto_selected_port = port_list[0] if port_list else ""
        return port_list

    def load_tag_mapping(self):
        if os.path.exists(TAG_MAPPING_FILE):
            df = pd.read_csv(TAG_MAPPING_FILE, sep=';', dtype=str, encoding="utf-8-sig")
            return {
                row['Tag']: (row['Startnummer'], row['Vorname'], row['Nachname'], row['Jahrgang'], row['Wohnort'])
                for _, row in df.iterrows()
            }
        return {}

    def save_tag_mapping(self):
        df = pd.DataFrame([
            {
                'Tag': tag,
                'Startnummer': startnr,
                'Vorname': vorname,
                'Nachname': nachname,
                'Jahrgang': jahrgang,
                'Wohnort': wohnort
            }
            for tag, (startnr, vorname, nachname, jahrgang, wohnort) in self.tag_name_dict.items()
        ])
        df.to_csv(TAG_MAPPING_FILE, index=False, sep=';', encoding="utf-8-sig")

    def start_action(self):
        self.serial_port = self.port_combobox.get()
        mode = self.mode_combobox.get()
        if not self.serial_port or not mode:
            return

        self.port_label.pack_forget()
        self.port_combobox.pack_forget()
        self.mode_label.pack_forget()
        self.mode_combobox.pack_forget()
        self.start_button.pack_forget()

        if mode == "Anmeldung":
            self.assign_tags()
            self.geometry("500x200")
        else:
            self.start_reading()
            self.geometry("800x600")

    def assign_tags(self):
        self.counter_label.pack()
        self.update_counter_label()
        self.table.insert("1.0", "Zuordnungsmodus: Halte einen RFID-Tag an das Lesegerät...\n")
        threading.Thread(target=self.read_and_assign_tags, daemon=True).start()

    def read_and_assign_tags(self):
        try:
            with serial.Serial(self.serial_port, BAUDRATE, timeout=1) as ser:
                while len(self.tag_name_dict) < 200:
                    if self.assigning:
                        continue
                    ser.reset_input_buffer()
                    line = ser.readline().decode("utf-8").strip()
                    if line:
                        tag = line.upper()
                        if self.check_for_error(line):
                            continue
                        self.assigning = True
                        data = self.show_assignment_form(tag)
                        if data:
                            self.tag_name_dict[tag] = data
                            self.save_tag_mapping()
                            self.update_assignment_display(tag, data)
                            self.update_counter_label()
                        self.assigning = False
        except serial.SerialException as e:
            print("Serieller Fehler:", e)

    def show_assignment_form(self, tag):
        form = ctk.CTkToplevel()
        form.title("RFID-Tag zuordnen")
        form.geometry("400x300")

        fields = ["Startnummer", "Vorname", "Nachname", "Jahrgang", "Wohnort"]
        entries = {}

        for i, field in enumerate(fields):
            label = ctk.CTkLabel(form, text=field + ":")
            label.grid(row=i, column=0, padx=10, pady=5, sticky="e")
            entry = ctk.CTkEntry(form)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries[field] = entry

        result = {}

        def on_submit():
            for field in fields:
                result[field] = entries[field].get().strip()

            # Prüfe auf doppelte Startnummer
            neue_startnummer = result["Startnummer"]
            for tag_data in self.tag_name_dict.values():
                if tag_data[0] == neue_startnummer:
                    messagebox.showerror("Fehler", f"Startnummer {neue_startnummer} ist bereits vergeben.")
                    return

            # Automatische Großschreibung bei Namen und Wohnort
            result["Vorname"] = result["Vorname"].capitalize()
            result["Nachname"] = result["Nachname"].capitalize()
            result["Wohnort"] = result["Wohnort"].capitalize()

            form.destroy()

        submit_button = ctk.CTkButton(form, text="OK", command=on_submit)
        submit_button.grid(row=len(fields), column=0, columnspan=2, pady=10)

        form.grab_set()
        form.wait_window()

        if all(result.values()):
            return tuple(result[field] for field in fields)
        return None

    def update_assignment_display(self, tag, data):
        self.table.insert("end", f"{tag} → {data[0]} | {data[1]} {data[2]}\n")

    def update_counter_label(self):
        self.counter_label.configure(text=f"Zugeordnete Tags: {len(self.tag_name_dict)} / 200")

    def start_reading(self):
        os.makedirs("Tabellen", exist_ok=True)
        timestamp_start = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        self.filename = os.path.join("Tabellen", f"Zeitmessung_Ziel_{timestamp_start}.csv")
        self.data.to_csv(self.filename, index=False, sep=';', encoding="utf-8-sig")

        self.serial_thread = threading.Thread(target=self.read_serial)
        self.serial_thread.daemon = True
        self.serial_thread.start()

    def read_serial(self):
        try:
            with serial.Serial(self.serial_port, BAUDRATE, timeout=1) as ser:
                while True:
                    line = ser.readline().decode("utf-8").strip()
                    if line:
                        if self.check_for_error(line):
                            continue
                        tag = line.upper()
                        if tag not in self.gelesene_tags and tag in self.tag_name_dict:
                            now = datetime.now()
                            date_str = now.strftime("%Y-%m-%d")
                            time_str = now.strftime("%H:%M:%S.%f")[:-4]
                            startnummer, vorname, nachname, jahrgang, wohnort = self.tag_name_dict[tag]

                            self.data.loc[len(self.data)] = [startnummer, vorname, nachname, jahrgang, wohnort, date_str, time_str]
                            self.gelesene_tags.add(tag)

                            with open(self.filename, "a", newline="", encoding="utf-8-sig") as f:
                                f.write(f"{startnummer};  {vorname};  {nachname};  {jahrgang};  {wohnort};  {date_str};  {time_str}\n")

                            winsound.Beep(2000, 300)

                            self.update_table()
        except serial.SerialException as e:
            print("Serieller Fehler:", e)

    def check_for_error(self, line):
        known_errors = [
            "Module failed to respond. Please check wiring.",
            "Bad CRC",
            "High return loss, check antenna!",
            "Unknown error"
        ]
        if line in known_errors:
            messagebox.showerror("Fehler vom RFID-Modul", line)
            return True
        return False

    def update_table(self):
        self.table.delete("1.0", "end")
        if not self.data.empty:
            text = self.data.to_string(index=False, col_space=12)
            self.table.insert("1.0", text)

if __name__ == "__main__":
    app = RFIDApp()
    app.mainloop()
