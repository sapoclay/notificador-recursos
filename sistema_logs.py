import logging
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from tkinter import filedialog

class SistemaLogs:
    def __init__(self, configuracion=None):
        self.configuracion = configuracion or {}
        self.log_config = self.configuracion.get('logs', {})
        
        # Configuración por defecto
        self.archivo_log = self.log_config.get('archivo_log', 
                                             str(Path.home() / '.config' / 'quien-se-come-recursos' / 'monitor.log'))
        self.nivel_log = self.log_config.get('nivel_log', 'INFO')
        self.dias_retencion = self.log_config.get('dias_retencion', 30)
        self.habilitar_logs = self.log_config.get('habilitar_logs', True)
        
        # Crear directorio de logs si no existe
        Path(self.archivo_log).parent.mkdir(parents=True, exist_ok=True)
        
        # Lock para thread safety (debe ir antes de configurar_logger)
        self.lock = threading.Lock()
        
        # Cache de logs recientes para mostrar en la GUI
        self.logs_recientes = []
        self.max_logs_cache = 1000
        
        # Configurar logger (al final porque usa self.lock)
        self.logger = logging.getLogger('MonitorRecursos')
        self.configurar_logger()
    
    def configurar_logger(self):
        """Configura el sistema de logging"""
        if not self.habilitar_logs:
            self.logger.setLevel(logging.CRITICAL + 1)  # Deshabilitar completamente
            return
        
        # Limpiar handlers existentes
        self.logger.handlers.clear()
        
        # Configurar nivel
        nivel_mapping = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        self.logger.setLevel(nivel_mapping.get(self.nivel_log, logging.INFO))
        
        # Formatter personalizado
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler para archivo
        try:
            file_handler = logging.FileHandler(self.archivo_log, encoding='utf-8')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            print(f"Error configurando archivo de log: {e}")
        
        # Handler para consola (opcional)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.ERROR)  # Solo errores en consola
        self.logger.addHandler(console_handler)
        
        # Log inicial
        self.log_info("Sistema de logs iniciado")
    
    def log_debug(self, mensaje):
        """Log nivel DEBUG"""
        self._log_con_cache('DEBUG', mensaje)
        if self.habilitar_logs:
            self.logger.debug(mensaje)
    
    def log_info(self, mensaje):
        """Log nivel INFO"""
        self._log_con_cache('INFO', mensaje)
        if self.habilitar_logs:
            self.logger.info(mensaje)
    
    def log_warning(self, mensaje):
        """Log nivel WARNING"""
        self._log_con_cache('WARNING', mensaje)
        if self.habilitar_logs:
            self.logger.warning(mensaje)
    
    def log_error(self, mensaje):
        """Log nivel ERROR"""
        self._log_con_cache('ERROR', mensaje)
        if self.habilitar_logs:
            self.logger.error(mensaje)
    
    def log_critical(self, mensaje):
        """Log nivel CRITICAL"""
        self._log_con_cache('CRITICAL', mensaje)
        if self.habilitar_logs:
            self.logger.critical(mensaje)
    
    def _log_con_cache(self, nivel, mensaje):
        """Añade el log al cache para la GUI"""
        with self.lock:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            entrada_log = {
                'timestamp': timestamp,
                'nivel': nivel,
                'mensaje': mensaje
            }
            
            self.logs_recientes.append(entrada_log)
            
            # Limitar tamaño del cache
            if len(self.logs_recientes) > self.max_logs_cache:
                self.logs_recientes = self.logs_recientes[-self.max_logs_cache:]
    
    def log_evento_proceso(self, accion, proceso_nombre, proceso_pid, detalle=""):
        """Log específico para eventos de procesos"""
        mensaje = f"Proceso: {accion} | {proceso_nombre} (PID: {proceso_pid})"
        if detalle:
            mensaje += f" | {detalle}"
        self.log_info(mensaje)
    
    def log_alerta_proceso(self, proceso_nombre, proceso_pid, cpu_uso, memoria_uso):
        """Log específico para alertas de procesos"""
        mensaje = f"ALERTA: {proceso_nombre} (PID: {proceso_pid}) - CPU: {cpu_uso}%, Memoria: {memoria_uso}MB"
        self.log_warning(mensaje)
    
    def log_cambio_configuracion(self, seccion, clave, valor_anterior, valor_nuevo):
        """Log para cambios de configuración"""
        mensaje = f"Config: {seccion}.{clave} cambiado de '{valor_anterior}' a '{valor_nuevo}'"
        self.log_info(mensaje)
    
    def limpiar_logs_antiguos(self):
        """Limpia logs más antiguos que dias_retencion"""
        try:
            if not os.path.exists(self.archivo_log):
                return
            
            fecha_limite = datetime.now() - timedelta(days=self.dias_retencion)
            lineas_validas = []
            
            with open(self.archivo_log, 'r', encoding='utf-8') as f:
                for linea in f:
                    try:
                        # Extraer timestamp de la línea
                        if ' | ' in linea:
                            timestamp_str = linea.split(' | ')[0]
                            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                            
                            if timestamp >= fecha_limite:
                                lineas_validas.append(linea)
                    except:
                        # Si no se puede parsear, mantener la línea
                        lineas_validas.append(linea)
            
            # Reescribir archivo con solo las líneas válidas
            with open(self.archivo_log, 'w', encoding='utf-8') as f:
                f.writelines(lineas_validas)
            
            self.log_info(f"Limpieza de logs completada. Retenidos {len(lineas_validas)} registros")
            
        except Exception as e:
            self.log_error(f"Error limpiando logs antiguos: {e}")
    
    def exportar_logs(self, archivo_destino, fecha_inicio=None, fecha_fin=None, nivel_minimo=None):
        """Exporta logs a un archivo con filtros opcionales"""
        try:
            logs_filtrados = []
            
            with open(self.archivo_log, 'r', encoding='utf-8') as f:
                for linea in f:
                    try:
                        incluir_linea = True
                        
                        if ' | ' in linea:
                            partes = linea.split(' | ')
                            if len(partes) >= 3:
                                timestamp_str = partes[0]
                                nivel = partes[1].strip()
                                
                                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                                
                                # Filtrar por fecha
                                if fecha_inicio and timestamp < fecha_inicio:
                                    incluir_linea = False
                                if fecha_fin and timestamp > fecha_fin:
                                    incluir_linea = False
                                
                                # Filtrar por nivel
                                if nivel_minimo:
                                    niveles_orden = {'DEBUG': 0, 'INFO': 1, 'WARNING': 2, 'ERROR': 3, 'CRITICAL': 4}
                                    if niveles_orden.get(nivel, 0) < niveles_orden.get(nivel_minimo, 0):
                                        incluir_linea = False
                        
                        if incluir_linea:
                            logs_filtrados.append(linea)
                            
                    except:
                        # Si no se puede parsear, incluir la línea
                        logs_filtrados.append(linea)
            
            # Escribir logs filtrados
            with open(archivo_destino, 'w', encoding='utf-8') as f:
                f.writelines(logs_filtrados)
            
            self.log_info(f"Logs exportados a: {archivo_destino} ({len(logs_filtrados)} registros)")
            return True
            
        except Exception as e:
            self.log_error(f"Error exportando logs: {e}")
            return False
    
    def obtener_estadisticas_logs(self):
        """Obtiene estadísticas de los logs"""
        try:
            stats = {
                'total_registros': 0,
                'por_nivel': {'DEBUG': 0, 'INFO': 0, 'WARNING': 0, 'ERROR': 0, 'CRITICAL': 0},
                'fecha_primer_log': None,
                'fecha_ultimo_log': None,
                'tamaño_archivo': 0
            }
            
            if not os.path.exists(self.archivo_log):
                return stats
            
            stats['tamaño_archivo'] = os.path.getsize(self.archivo_log)
            
            with open(self.archivo_log, 'r', encoding='utf-8') as f:
                for linea in f:
                    stats['total_registros'] += 1
                    
                    try:
                        if ' | ' in linea:
                            partes = linea.split(' | ')
                            if len(partes) >= 3:
                                timestamp_str = partes[0]
                                nivel = partes[1].strip()
                                
                                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                                
                                if stats['fecha_primer_log'] is None or timestamp < stats['fecha_primer_log']:
                                    stats['fecha_primer_log'] = timestamp
                                if stats['fecha_ultimo_log'] is None or timestamp > stats['fecha_ultimo_log']:
                                    stats['fecha_ultimo_log'] = timestamp
                                
                                if nivel in stats['por_nivel']:
                                    stats['por_nivel'][nivel] += 1
                    except:
                        continue
            
            return stats
            
        except Exception as e:
            self.log_error(f"Error obteniendo estadísticas: {e}")
            return {}
    
    def crear_ventana_logs(self, parent):
        """Crea ventana para visualizar logs"""
        ventana_logs = tk.Toplevel(parent)
        ventana_logs.title("Visor de Logs - Monitor de Recursos")
        ventana_logs.geometry("900x600")
        ventana_logs.transient(parent)
        
        # Frame principal
        frame_principal = ttk.Frame(ventana_logs, padding=10)
        frame_principal.pack(fill=tk.BOTH, expand=True)
        
        # Frame superior con controles
        frame_controles = ttk.Frame(frame_principal)
        frame_controles.pack(fill=tk.X, pady=(0, 10))
        
        # Filtros
        ttk.Label(frame_controles, text="Filtrar por nivel:").pack(side=tk.LEFT, padx=(0, 5))
        
        nivel_var = tk.StringVar(value="TODOS")
        combo_nivel = ttk.Combobox(frame_controles, textvariable=nivel_var, 
                                  values=["TODOS", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                                  state="readonly", width=10)
        combo_nivel.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botones
        ttk.Button(frame_controles, text="Actualizar", 
                  command=lambda: self._actualizar_vista_logs(text_logs, nivel_var.get())).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(frame_controles, text="Limpiar Cache", 
                  command=lambda: self._limpiar_cache_logs(text_logs)).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(frame_controles, text="Exportar...", 
                  command=lambda: self._exportar_logs_gui(parent)).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(frame_controles, text="Estadísticas", 
                  command=lambda: self._mostrar_estadisticas(parent)).pack(side=tk.LEFT, padx=(0, 5))
        
        # Área de texto para logs
        frame_logs = ttk.LabelFrame(frame_principal, text="Registros de Log", padding=5)
        frame_logs.pack(fill=tk.BOTH, expand=True)
        
        text_logs = scrolledtext.ScrolledText(frame_logs, wrap=tk.WORD, 
                                            font=("Consolas", 9))
        text_logs.pack(fill=tk.BOTH, expand=True)
        
        # Cargar logs iniciales
        self._actualizar_vista_logs(text_logs, "TODOS")
        
        # Auto-actualización cada 5 segundos
        def auto_actualizar():
            self._actualizar_vista_logs(text_logs, nivel_var.get())
            ventana_logs.after(5000, auto_actualizar)
        
        ventana_logs.after(5000, auto_actualizar)
    
    def _actualizar_vista_logs(self, text_widget, filtro_nivel):
        """Actualiza la vista de logs en el widget de texto"""
        with self.lock:
            logs_a_mostrar = self.logs_recientes.copy()
        
        # Filtrar por nivel si no es "TODOS"
        if filtro_nivel != "TODOS":
            logs_a_mostrar = [log for log in logs_a_mostrar if log['nivel'] == filtro_nivel]
        
        # Limpiar y actualizar
        text_widget.delete(1.0, tk.END)
        
        for log in logs_a_mostrar:
            linea = f"{log['timestamp']} | {log['nivel']:8s} | {log['mensaje']}\n"
            
            # Colorear según nivel
            text_widget.insert(tk.END, linea)
            
            # Configurar tags de color por nivel
            start_line = text_widget.index("end-2c linestart")
            end_line = text_widget.index("end-1c")
            
            if log['nivel'] == 'ERROR':
                text_widget.tag_add("error", start_line, end_line)
                text_widget.tag_config("error", foreground="red")
            elif log['nivel'] == 'CRITICAL':
                text_widget.tag_add("critical", start_line, end_line)
                text_widget.tag_config("critical", foreground="darkred", background="lightyellow")
            elif log['nivel'] == 'WARNING':
                text_widget.tag_add("warning", start_line, end_line)
                text_widget.tag_config("warning", foreground="orange")
            elif log['nivel'] == 'DEBUG':
                text_widget.tag_add("debug", start_line, end_line)
                text_widget.tag_config("debug", foreground="gray")
        
        # Scroll al final
        text_widget.see(tk.END)
    
    def _limpiar_cache_logs(self, text_widget):
        """Limpia el cache de logs en memoria"""
        with self.lock:
            self.logs_recientes.clear()
        text_widget.delete(1.0, tk.END)
        self.log_info("Cache de logs limpiado")
    
    def _exportar_logs_gui(self, parent):
        """Interfaz gráfica para exportar logs"""
        archivo = filedialog.asksaveasfilename(
            parent=parent,
            title="Exportar Logs",
            defaultextension=".log",
            filetypes=[("Archivos de Log", "*.log"), ("Archivos de Texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        
        if archivo:
            if self.exportar_logs(archivo):
                messagebox.showinfo("Éxito", f"Logs exportados correctamente a:\n{archivo}")
            else:
                messagebox.showerror("Error", "Error al exportar los logs")
    
    def _mostrar_estadisticas(self, parent):
        """Muestra ventana con estadísticas de logs"""
        stats = self.obtener_estadisticas_logs()
        
        ventana_stats = tk.Toplevel(parent)
        ventana_stats.title("Estadísticas de Logs")
        ventana_stats.geometry("400x300")
        ventana_stats.resizable(False, False)
        ventana_stats.transient(parent)
        ventana_stats.grab_set()
        
        frame = ttk.Frame(ventana_stats, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Estadísticas de Logs", font=("Arial", 14, "bold")).pack(pady=(0, 15))
        
        # Mostrar estadísticas
        ttk.Label(frame, text=f"Total de registros: {stats.get('total_registros', 0)}").pack(anchor=tk.W, pady=2)
        ttk.Label(frame, text=f"Tamaño del archivo: {stats.get('tamaño_archivo', 0)} bytes").pack(anchor=tk.W, pady=2)
        
        if stats.get('fecha_primer_log'):
            ttk.Label(frame, text=f"Primer log: {stats['fecha_primer_log'].strftime('%Y-%m-%d %H:%M:%S')}").pack(anchor=tk.W, pady=2)
        if stats.get('fecha_ultimo_log'):
            ttk.Label(frame, text=f"Último log: {stats['fecha_ultimo_log'].strftime('%Y-%m-%d %H:%M:%S')}").pack(anchor=tk.W, pady=2)
        
        ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        ttk.Label(frame, text="Registros por nivel:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        for nivel, cantidad in stats.get('por_nivel', {}).items():
            ttk.Label(frame, text=f"  {nivel}: {cantidad}").pack(anchor=tk.W, pady=1)
        
        ttk.Button(frame, text="Cerrar", command=ventana_stats.destroy).pack(pady=15)

# Función de conveniencia
def crear_sistema_logs(configuracion):
    """Crea y configura el sistema de logs"""
    return SistemaLogs(configuracion)
