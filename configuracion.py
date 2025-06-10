import json
import os
from pathlib import Path

class ConfiguracionManager:
    def __init__(self):
        # Crear directorio de configuración en el home del usuario
        self.config_dir = Path.home() / '.config' / 'quien-se-come-recursos'
        self.config_file = self.config_dir / 'config.json'
        self.create_config_dir()
        self.configuracion_default = {
            'umbrales': {
                'cpu_porcentaje': 50,
                'memoria_mb': 500
            },
            'interfaz': {
                'tema': 'claro',  # 'claro', 'oscuro', 'sistema'
                'ventana_ancho': 800,
                'ventana_alto': 600,
                'mostrar_iconos_procesos': True,
                'tamaño_fuente': 9
            },
            'monitoreo': {
                'intervalo_actualizacion': 3,
                'mostrar_notificaciones': True,
                'procesos_excluidos': ['System Idle Process', 'kernel_task'],
                'auto_minimizar_bandeja': True
            },
            'alertas': {
                'sonido_habilitado': True,
                'nivel_minimo_alerta': 'media',
                'duracion_notificacion': 5000
            },
            'logs': {
                'habilitar_logs': True,
                'nivel_log': 'INFO',
                'dias_retencion': 30,
                'archivo_log': str(self.config_dir / 'monitor.log')
            }
        }
    
    def create_config_dir(self):
        """Crea el directorio de configuración si no existe"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            print(f"Directorio de configuración: {self.config_dir}")
        except Exception as e:
            print(f"Error creando directorio de configuración: {e}")
    
    def cargar_configuracion(self):
        """Carga la configuración desde el archivo, usa defaults si no existe"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_cargada = json.load(f)
                
                # Fusionar con defaults para añadir nuevas opciones
                configuracion = self.configuracion_default.copy()
                self._fusionar_config(configuracion, config_cargada)
                
                print("Configuración cargada exitosamente")
                return configuracion
            else:
                print("Archivo de configuración no encontrado, usando valores por defecto")
                self.guardar_configuracion(self.configuracion_default)
                return self.configuracion_default.copy()
        
        except Exception as e:
            print(f"Error cargando configuración: {e}")
            print("Usando configuración por defecto")
            return self.configuracion_default.copy()
    
    def guardar_configuracion(self, configuracion):
        """Guarda la configuración al archivo"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(configuracion, f, indent=4, ensure_ascii=False)
            print("Configuración guardada exitosamente")
            return True
        except Exception as e:
            print(f"Error guardando configuración: {e}")
            return False
    
    def _fusionar_config(self, base, nueva):
        """Fusiona configuración nueva con la base, manteniendo estructura"""
        for key, value in nueva.items():
            if key in base:
                if isinstance(base[key], dict) and isinstance(value, dict):
                    self._fusionar_config(base[key], value)
                else:
                    base[key] = value
            else:
                base[key] = value
    
    def obtener_valor(self, configuracion, seccion, clave, default=None):
        """Obtiene un valor específico de la configuración"""
        try:
            return configuracion.get(seccion, {}).get(clave, default)
        except:
            return default
    
    def establecer_valor(self, configuracion, seccion, clave, valor):
        """Establece un valor específico en la configuración"""
        if seccion not in configuracion:
            configuracion[seccion] = {}
        configuracion[seccion][clave] = valor
    
    def resetear_configuracion(self):
        """Resetea la configuración a valores por defecto"""
        try:
            self.guardar_configuracion(self.configuracion_default)
            print("Configuración reseteada a valores por defecto")
            return True
        except Exception as e:
            print(f"Error reseteando configuración: {e}")
            return False
    
    def exportar_configuracion(self, archivo_destino):
        """Exporta la configuración actual a un archivo"""
        try:
            config_actual = self.cargar_configuracion()
            with open(archivo_destino, 'w', encoding='utf-8') as f:
                json.dump(config_actual, f, indent=4, ensure_ascii=False)
            print(f"Configuración exportada a: {archivo_destino}")
            return True
        except Exception as e:
            print(f"Error exportando configuración: {e}")
            return False
    
    def importar_configuracion(self, archivo_origen):
        """Importa configuración desde un archivo"""
        try:
            with open(archivo_origen, 'r', encoding='utf-8') as f:
                config_importada = json.load(f)
            
            if self.guardar_configuracion(config_importada):
                print(f"Configuración importada desde: {archivo_origen}")
                return True
            return False
        except Exception as e:
            print(f"Error importando configuración: {e}")
            return False

# Funciones de conveniencia para usar desde otros módulos
def cargar_config():
    """Función de conveniencia para cargar configuración"""
    manager = ConfiguracionManager()
    return manager.cargar_configuracion(), manager

def guardar_config(configuracion):
    """Función de conveniencia para guardar configuración"""
    manager = ConfiguracionManager()
    return manager.guardar_configuracion(configuracion)
