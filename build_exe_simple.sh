#!/bin/bash
# Diyargezen EXE Builder - Basit Shell Script
# Linux/Mac için (cross-platform build için)

echo "========================================"
echo "Diyargezen EXE Builder"
echo "========================================"
echo ""

# PyInstaller kurulu mu kontrol et
if ! python -c "import PyInstaller" 2>/dev/null; then
    echo "PyInstaller bulunamadı! Kuruluyor..."
    pip install pyinstaller
    if [ $? -ne 0 ]; then
        echo "HATA: PyInstaller kurulamadı!"
        exit 1
    fi
fi

echo ""
echo "EXE oluşturuluyor..."
echo ""

# PyInstaller'ı çalıştır
pyinstaller --clean Diyargezen.spec

if [ $? -ne 0 ]; then
    echo ""
    echo "========================================"
    echo "HATA: EXE oluşturulamadı!"
    echo "========================================"
    exit 1
else
    echo ""
    echo "========================================"
    echo "Başarılı! EXE dosyası oluşturuldu."
    echo "========================================"
    echo ""
    echo "EXE dosyası: dist/Diyargezen.exe"
    echo ""
fi





# Diyargezen EXE Builder - Basit Shell Script
# Linux/Mac için (cross-platform build için)

echo "========================================"
echo "Diyargezen EXE Builder"
echo "========================================"
echo ""

# PyInstaller kurulu mu kontrol et
if ! python -c "import PyInstaller" 2>/dev/null; then
    echo "PyInstaller bulunamadı! Kuruluyor..."
    pip install pyinstaller
    if [ $? -ne 0 ]; then
        echo "HATA: PyInstaller kurulamadı!"
        exit 1
    fi
fi

echo ""
echo "EXE oluşturuluyor..."
echo ""

# PyInstaller'ı çalıştır
pyinstaller --clean Diyargezen.spec

if [ $? -ne 0 ]; then
    echo ""
    echo "========================================"
    echo "HATA: EXE oluşturulamadı!"
    echo "========================================"
    exit 1
else
    echo ""
    echo "========================================"
    echo "Başarılı! EXE dosyası oluşturuldu."
    echo "========================================"
    echo ""
    echo "EXE dosyası: dist/Diyargezen.exe"
    echo ""
fi







# Diyargezen EXE Builder - Basit Shell Script
# Linux/Mac için (cross-platform build için)

echo "========================================"
echo "Diyargezen EXE Builder"
echo "========================================"
echo ""

# PyInstaller kurulu mu kontrol et
if ! python -c "import PyInstaller" 2>/dev/null; then
    echo "PyInstaller bulunamadı! Kuruluyor..."
    pip install pyinstaller
    if [ $? -ne 0 ]; then
        echo "HATA: PyInstaller kurulamadı!"
        exit 1
    fi
fi

echo ""
echo "EXE oluşturuluyor..."
echo ""

# PyInstaller'ı çalıştır
pyinstaller --clean Diyargezen.spec

if [ $? -ne 0 ]; then
    echo ""
    echo "========================================"
    echo "HATA: EXE oluşturulamadı!"
    echo "========================================"
    exit 1
else
    echo ""
    echo "========================================"
    echo "Başarılı! EXE dosyası oluşturuldu."
    echo "========================================"
    echo ""
    echo "EXE dosyası: dist/Diyargezen.exe"
    echo ""
fi





# Diyargezen EXE Builder - Basit Shell Script
# Linux/Mac için (cross-platform build için)

echo "========================================"
echo "Diyargezen EXE Builder"
echo "========================================"
echo ""

# PyInstaller kurulu mu kontrol et
if ! python -c "import PyInstaller" 2>/dev/null; then
    echo "PyInstaller bulunamadı! Kuruluyor..."
    pip install pyinstaller
    if [ $? -ne 0 ]; then
        echo "HATA: PyInstaller kurulamadı!"
        exit 1
    fi
fi

echo ""
echo "EXE oluşturuluyor..."
echo ""

# PyInstaller'ı çalıştır
pyinstaller --clean Diyargezen.spec

if [ $? -ne 0 ]; then
    echo ""
    echo "========================================"
    echo "HATA: EXE oluşturulamadı!"
    echo "========================================"
    exit 1
else
    echo ""
    echo "========================================"
    echo "Başarılı! EXE dosyası oluşturuldu."
    echo "========================================"
    echo ""
    echo "EXE dosyası: dist/Diyargezen.exe"
    echo ""
fi











