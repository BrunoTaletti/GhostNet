@echo off
setlocal EnableDelayedExpansion

:: 1. CONTROLE DE VERSAO
set VERSION_FILE=version.txt
if not exist %VERSION_FILE% echo 0.0.0> %VERSION_FILE%

for /f "tokens=1,2,3 delims=." %%a in (%VERSION_FILE%) do (
    set MAJOR=%%a
    set MINOR=%%b
    set PATCH=%%c
)
set /a PATCH+=1
set NEW_VERSION=%MAJOR%.%MINOR%.!PATCH!
echo !NEW_VERSION!> %VERSION_FILE%

echo ==========================================
echo [ GHOSTNET ] INICIANDO BUILD v!NEW_VERSION!
echo ==========================================

:: 2. LIMPEZA DE BUILDS ANTIGOS
echo [*] Limpando pastas temporarias...
rmdir /s /q build >nul 2>&1
rmdir /s /q dist >nul 2>&1

:: 3. INSTALANDO DEPENDENCIAS
echo [*] Verificando dependencias...
pip install -r requirements.txt >nul 2>&1

:: 4. COMPILACAO PYINSTALLER
echo [*] Compilando binarios...
pyinstaller ^
--name "GhostNet" ^
--onefile ^
--windowed ^
--noconsole ^
--icon "app-icon.ico" ^
--add-data "app-logo.png;." ^
--add-data "app-icon.ico;." ^
--add-data "version.txt;." ^
--clean --noconfirm main.py

:: 5. COMPILACAO DO INSTALADOR (INNO SETUP)
echo ==========================================
echo [*] Empacotando Instalador (Inno Setup)...
echo ==========================================

:: A flag /DMyAppVersion injeta a versao dinamicamente no .iss
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" /DMyAppVersion="!NEW_VERSION!" installer.iss

echo ==========================================
echo [ OK ] BUILD !NEW_VERSION! GERADO COM SUCESSO!
echo ==========================================
pause