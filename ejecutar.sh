#!/bin/bash

# Detectar el directorio del script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Función para detectar si corre en terminal
is_terminal() {
    [ -t 0 ]
}

# Si no estamos en terminal, intentar lanzar una
if ! is_terminal; then
    echo "No se detectó terminal. Intentando lanzar una..."
    
    # Lista de terminales comunes en orden de preferencia
    TERMINALS=("alacritty" "kitty" "gnome-terminal" "konsole" "xfce4-terminal" "xterm" "urxvt" "termite")
    
    for term in "${TERMINALS[@]}"; do
        if command -v "$term" &> /dev/null; then
            case "$term" in
                "gnome-terminal"|"xfce4-terminal"|"konsole")
                    "$term" -- "$0"
                    ;;
                "alacritty"|"kitty"|"termite")
                    "$term" -e "$0"
                    ;;
                "xterm"|"urxvt")
                    "$term" -e "$0"
                    ;;
            esac
            exit 0
        fi
    done
    
    # Si llegamos aquí, intentar notify-send si existe
    if command -v notify-send &> /dev/null; then
        notify-send "Error" "No se encontró una terminal compatible para ejecutar el programa."
    fi
    exit 1
fi

echo "========================================================"
echo "   INICIANDO YOUTUBE MUSIC DOWNLOADER PRO++ v4.0"
echo "========================================================"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 no está instalado."
    echo "Por favor instala python con: sudo pacman -S python"
    read -p "Presiona Enter para salir..."
    exit 1
fi

# Configurar entorno virtual
VENV_DIR="venv"

# Función para probar si podemos ejecutar binarios en este directorio
can_execute_here() {
    local test_file=".test_exec"
    touch "$test_file"
    chmod +x "$test_file" 2>/dev/null
    local res=1
    if [ -x "$test_file" ]; then
        res=0
    fi
    rm -f "$test_file"
    return $res
}

# Verificar si el venv existe pero está roto (falta activate)
if [ -d "$VENV_DIR" ] && [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "⚠️ Entorno virtual detectado pero incompleto. Recreando..."
    rm -rf "$VENV_DIR"
fi

# Determinar dónde crear el venv
USE_LOCAL_VENV=0

if [ ! -d "$VENV_DIR" ]; then
    echo "🔨 Creando entorno virtual..."
    
    # Intentar crear en el directorio actual con copias (para evitar symlinks en USB)
    # y verificar si se puede ejecutar
    if can_execute_here; then
        python3 -m venv --copies "$VENV_DIR"
        if [ $? -eq 0 ] && [ -f "$VENV_DIR/bin/activate" ]; then
            echo "✅ Entorno virtual creado en USB."
        else
            echo "⚠️ No se pudo crear venv en USB (posiblemente sistema de archivos no compatible)."
            rm -rf "$VENV_DIR"
            USE_LOCAL_VENV=1
        fi
    else
        echo "⚠️ El dispositivo USB parece no permitir ejecución (noexec)."
        USE_LOCAL_VENV=1
    fi
fi

# Si falló en USB o se detectó noexec, usar directorio local en HOME
if [ "$USE_LOCAL_VENV" -eq 1 ]; then
    VENV_DIR="$HOME/.cache/dow-pro-venv"
    echo "🔄 Usando entorno virtual local en: $VENV_DIR"
    
    if [ ! -d "$VENV_DIR" ] || [ ! -f "$VENV_DIR/bin/activate" ]; then
        rm -rf "$VENV_DIR"
        mkdir -p "$(dirname "$VENV_DIR")"
        python3 -m venv "$VENV_DIR"
        if [ $? -ne 0 ]; then
            echo "[ERROR] No se pudo crear el entorno virtual ni en USB ni en local."
            read -p "Presiona Enter para salir..."
            exit 1
        fi
    fi
fi

# Activar entorno virtual
source "$VENV_DIR/bin/activate"

# Instalar dependencias
echo "📦 Verificando dependencias..."
pip install --upgrade pip &> /dev/null
pip install yt-dlp mutagen requests Pillow &> /dev/null

if [ $? -ne 0 ]; then
    echo "[ERROR] Falló la instalación de dependencias."
    echo "Intenta ejecutar: sudo pacman -S python-pip"
    read -p "Presiona Enter para salir..."
    exit 1
fi

# Verificar archivo principal
if [ ! -f Principal.py ]; then
    echo "[ERROR] No se encuentra el archivo Principal.py"
    read -p "Presiona Enter para salir..."
    exit 1
fi

# Ejecutar programa
python Principal.py

# Pausa al finalizar si hubo error o cierre inesperado
if [ $? -ne 0 ]; then
    echo ""
    echo "El programa se cerró con errores."
    read -p "Presiona Enter para salir..."
fi
