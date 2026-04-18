@echo off
setlocal enabledelayedexpansion
echo [GhostNet] Iniciando Build...

:: 1. Script Python inline para auto-incrementar o version.txt
echo import sys > bump.py
echo v = open("version.txt", "r").read().strip().split('.') >> bump.py
echo v[-1] = str(int(v[-1]) + 1) >> bump.py
echo new_v = '.'.join(v) >> bump.py
echo open("version.txt", "w").write(new_v) >> bump.py
echo print(new_v) >> bump.py

:: Executa e pega a nova versão
for /f "delims=" %%i in ('python bump.py') do set NEW_VERSION=%%i
del bump.py

echo Nova versao: !NEW_VERSION!

:: 2. Compilando com PyInstaller
:: Nota: Adicione --noconsole para esconder o terminal no fundo da interface grafica
:: Ajustamos para incluir o app-logo.png, app-icon.ico e o version.txt no pacote
echo [GhostNet] Gerando executavel...
pyinstaller --noconfirm --onedir --windowed --icon "app-icon.ico" --add-data "app-logo.png;." --add-data "app-icon.ico;." --add-data "version.txt;."  "main.py"

echo.
echo [GhostNet] Build !NEW_VERSION! finalizado!
echo O proximo passo e rodar seu script do Inno Setup apontando para a pasta 'dist/main'.
pause