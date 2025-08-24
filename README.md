#Zeitmessung VCM

##Benutzerinformationen

**Installation:** Lade "VCM-Zeitmessung-Setup.exe" herunter und installiere die App.
**Dateien:** die erzeugten Dateien befinden sich unter *C:\Users\...\AppData\Local\VCM_Zeitmessung\Datenbank*



##Create new version

**open Powershell on Windows**

cd *path of folder*

py -3.12 -m venv .venv

.\.venv\Scripts\Activate.ps1

pip install --upgrade pip wheel

pip install pyinstaller pyinstaller-hooks-contrib customtkinter pandas pyserial pillow openpyxl

pip freeze > requirements.txt

pyinstaller `
  --noconfirm --clean --noconsole `
  --name "VCM-Zeitmessung" `
  --icon vcm.ico `
  --add-data "vcm.ico;." `
  --add-data "vcm_start.ico;." `
  --hidden-import openpyxl `
  --hidden-import openpyxl.styles `
  --hidden-import openpyxl.worksheet.header_footer `
  main.py

**dowload "Inno Setup Compiler"**
https://jrsoftware.org/isinfo.php
  
**open "installer.iss" with inno Setup Compiler, change version number and save**
**click on "compile"**


