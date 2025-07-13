import serial
import threading
import pandas as pd
import customtkinter as ctk
from datetime import datetime
import os
import serial.tools.list_ports
import winsound
import sys

# Konfiguration
BAUDRATE = 115200
TAG_MAPPING_FILE = "tag_mapping.csv"

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
        self.title("Zeitmessung VCM")
        self.geometry("500x200")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.serial_port = None
        self.serial_thread = None
        self.auto_selected_port = ""
        self.data = pd.DataFrame(columns=["Startnummer", "Name", "Datum", "Uhrzeit"])
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

        self.mode_combobox = ctk.CTkComboBox(self, values=["Zuordnen", "Messung"])
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
            df = pd.read_csv(TAG_MAPPING_FILE, sep=';', dtype=str)
            return {row['Tag']: (row['Startnummer'], row['Name']) for _, row in df.iterrows()}
        return {}

    def save_tag_mapping(self):
        df = pd.DataFrame([
            {'Tag': tag, 'Startnummer': startnr, 'Name': name}
            for tag, (startnr, name) in self.tag_name_dict.items()
        ])
        df.to_csv(TAG_MAPPING_FILE, index=False, sep=';')

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

        if mode == "Zuordnen":
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
                        self.assigning = True
                        startnummer, name = self.prompt_for_data(tag)
                        if name and startnummer:
                            self.tag_name_dict[tag] = (startnummer, name)
                            self.save_tag_mapping()
                            self.update_assignment_display(tag, startnummer, name)
                            self.update_counter_label()
                        self.assigning = False
        except serial.SerialException as e:
            print("Serieller Fehler:", e)

    def prompt_for_data(self, tag):
        startnr_prompt = ctk.CTkInputDialog(text=f"Startnummer für Tag {tag} eingeben:", title="RFID-Tag zuordnen")
        startnr = startnr_prompt.get_input()
        name_prompt = ctk.CTkInputDialog(text=f"Name für Tag {tag} eingeben:", title="RFID-Tag zuordnen")
        name = name_prompt.get_input()
        return startnr, name

    def update_assignment_display(self, tag, startnummer, name):
        self.table.insert("end", f"{tag} → {startnummer} | {name}\n")

    def update_counter_label(self):
        self.counter_label.configure(text=f"Zugeordnete Tags: {len(self.tag_name_dict)} / 200")

    def start_reading(self):
        os.makedirs("logs", exist_ok=True)
        timestamp_start = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        self.filename = os.path.join("logs", f"rfid_log_{timestamp_start}.csv")
        self.data.to_csv(self.filename, index=False, sep=';')

        self.serial_thread = threading.Thread(target=self.read_serial)
        self.serial_thread.daemon = True
        self.serial_thread.start()

    def read_serial(self):
        try:
            with serial.Serial(self.serial_port, BAUDRATE, timeout=1) as ser:
                while True:
                    line = ser.readline().decode("utf-8").strip()
                    if line:
                        tag = line.upper()
                        if tag not in self.gelesene_tags and tag in self.tag_name_dict:
                            now = datetime.now()
                            date_str = now.strftime("%Y-%m-%d")
                            time_str = now.strftime("%H:%M:%S.%f")[:-4]
                            startnummer, name = self.tag_name_dict[tag]

                            self.data.loc[len(self.data)] = [startnummer, name, date_str, time_str]
                            self.gelesene_tags.add(tag)

                            with open(self.filename, "a", newline="") as f:
                                f.write(f"{startnummer};  {name};  {date_str};  {time_str}\n")

                            winsound.Beep(2000, 300)

                            self.update_table()
        except serial.SerialException as e:
            print("Serieller Fehler:", e)

    def update_table(self):
        self.table.delete("1.0", "end")
        if not self.data.empty:
            text = self.data.to_string(index=False, col_space=12)
            self.table.insert("1.0", text)

if __name__ == "__main__":
    app = RFIDApp()
    app.mainloop()
