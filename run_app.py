#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🐸 Monitor de Recursos del Sistema - Script de Instalación y Ejecución

Este script automatiza la instalación y ejecución de la aplicación
Monitor de Recursos con creación de entorno virtual y verificaciones.

Autor: sapoclay
Repositorio: https://github.com/sapoclay/notificador-recursos/
"""

import os
import sys
import platform
import subprocess
import venv
from pathlib import Path

def check_python_version():
    """Verifica que la versión de Python sea compatible"""
    print("🐍 Verificando versión de Python...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} no es compatible")
        print("   Se requiere Python 3.8 o superior")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} es compatible")
    return True

def is_venv_exists():
    """Verifica si el entorno virtual existe"""
    venv_dir = '.venv'
    return os.path.exists(venv_dir) and os.path.isdir(venv_dir)

def create_venv():
    """Crea el entorno virtual"""
    print("📦 Creando entorno virtual...")
    venv.create('.venv', with_pip=True)
    print("✅ Entorno virtual creado exitosamente")

def get_python_executable():
    """Obtiene la ruta del ejecutable Python del entorno virtual"""
    if platform.system().lower() == 'windows':
        return os.path.join('.venv', 'Scripts', 'python.exe')
    return os.path.join('.venv', 'bin', 'python')

def get_pip_executable():
    """Obtiene la ruta del ejecutable pip del entorno virtual"""
    if platform.system().lower() == 'windows':
        return os.path.join('.venv', 'Scripts', 'pip.exe')
    return os.path.join('.venv', 'bin', 'pip')

def install_requirements():
    """Instala las dependencias desde requirements.txt"""
    pip_exe = get_pip_executable()
    requirements_file = 'requirements.txt'
    
    print("🔧 Actualizando setuptools...")
    subprocess.run([pip_exe, 'install', '--upgrade', 'setuptools'], check=True)
    
    if not os.path.exists(requirements_file):
        print(f"❌ Error: {requirements_file} no encontrado")
        sys.exit(1)
    
    print("📋 Instalando dependencias desde requirements.txt...")
    subprocess.run([pip_exe, 'install', '-r', requirements_file], check=True)
    print("✅ Dependencias instaladas correctamente")

def check_system_requirements():
    """Verifica los requisitos del sistema"""
    print("🖥️  Verificando requisitos del sistema...")
    
    # Verificar sistema operativo
    os_name = platform.system()
    print(f"✅ Sistema operativo: {os_name}")
    
    # Verificar si hay entorno gráfico disponible
    if os_name == "Linux":
        display = os.environ.get('DISPLAY')
        wayland = os.environ.get('WAYLAND_DISPLAY')
        if not display and not wayland:
            print("⚠️  No se detectó entorno gráfico (DISPLAY/WAYLAND_DISPLAY)")
            print("   La aplicación podría no funcionar correctamente")
        else:
            print(f"✅ Entorno gráfico detectado")
    
    return True

def run_main_app():
    """Ejecuta la aplicación principal"""
    python_exe = get_python_executable()
    main_file = 'monitor_gui.py'
    
    if not os.path.exists(main_file):
        print(f"❌ Error: {main_file} no encontrado")
        sys.exit(1)
    
    print("🚀 Iniciando Monitor de Recursos...")
    subprocess.run([python_exe, main_file], check=True)

def show_app_info():
    """Muestra información sobre la aplicación"""
    print("=" * 60)
    print("🐸 MONITOR DE RECURSOS v0.1.2")
    print("=" * 60)
    print("Aplicación para monitorear procesos del sistema con interfaz gráfica")
    print("\n📋 CARACTERÍSTICAS:")
    print("   • Monitor en tiempo real de CPU y memoria")
    print("   • Sistema de alertas configurable")
    print("   • Icono en bandeja del sistema")
    print("   • Temas claro/oscuro/sistema")
    print("   • Configuración persistente")
    print("   • Sistema de logging completo")
    print("\n🔗 Repositorio: https://github.com/sapoclay/notificador-recursos/")
    print("=" * 60)

def main():
    """Función principal"""
    show_app_info()
    
    # Cambiar al directorio del script
    os.chdir(Path(__file__).parent)
    
    # Verificaciones previas
    if not check_python_version():
        sys.exit(1)
    
    if not check_system_requirements():
        sys.exit(1)
    
    # Gestión del entorno virtual
    if not is_venv_exists():
        create_venv()
    else:
        print("✅ Entorno virtual encontrado")
    
    try:
        # Instalar dependencias en el entorno virtual
        install_requirements()
        
        # Ejecutar la aplicación
        run_main_app()
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error durante la ejecución: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
