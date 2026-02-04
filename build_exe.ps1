$ErrorActionPreference = "Stop"
if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
  Write-Host "PyInstaller not found. Installing..."
  pip install pyinstaller
}
pyinstaller --noconsole --onefile --name codexOfflineVideo avatar_app_ultimate.py
Write-Host "Build complete. See dist/codexOfflineVideo.exe"
