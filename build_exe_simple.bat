@echo off
REM Diyargezen EXE Builder - Basit Batch Script
REM Windows için

echo ========================================
echo Diyargezen EXE Builder
echo ========================================
echo.

REM PyInstaller kurulu mu kontrol et
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller bulunamadi! Kuruluyor...
    pip install pyinstaller
    if errorlevel 1 (
        echo HATA: PyInstaller kurulamadi!
        pause
        exit /b 1
    )
)

echo.
echo EXE olusturuluyor...
echo.

REM PyInstaller'ı çalıştır
pyinstaller --clean Diyargezen.spec

if errorlevel 1 (
    echo.
    echo ========================================
    echo HATA: EXE olusturulamadi!
    echo ========================================
    pause
    exit /b 1
) else (
    echo.
    echo ========================================
    echo Basarili! EXE dosyasi olusturuldu.
    echo ========================================
    echo.
    echo EXE dosyasi: dist\Diyargezen.exe
    echo.
)

pause


