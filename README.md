# 🐸 ¿Quién se come los recursos?

Un monitor de recursos del sistema en tiempo real para identificar procesos que consumen excesivamente CPU y memoria.

![Monitor de Recursos](img/vitamina.png)

## 📋 Descripción

Este programa es una herramienta de monitoreo de sistema que te ayuda a identificar qué procesos están consumiendo demasiados recursos (CPU y memoria) en tu computadora. Es especialmente útil cuando tu sistema se vuelve lento y necesitas encontrar rápidamente el culpable.

![about-quiensecome](https://github.com/user-attachments/assets/34415df1-b17e-4fe0-a417-46edeaa18fb4)

### ¿Para qué sirve?

- **Detectar procesos problemáticos**: Identifica automáticamente procesos que superan umbrales de CPU y memoria
- **Monitoreo en tiempo real**: Actualización continua cada 3 segundos con información detallada
- **Notificaciones inteligentes**: Te avisa con información específica del proceso y permite acción directa mediante clic
- **Selección automática**: Al hacer clic en una notificación, abre la aplicación y selecciona automáticamente el proceso problemático
- **Gestión completa de procesos**: Permite cerrar, reiniciar o pausar procesos directamente desde la interfaz
- **Ejecución en segundo plano**: Se minimiza a la bandeja del sistema para monitoreo continuo sin interrupciones

## ✨ Características

### 🎯 Monitoreo Inteligente
- **Umbrales configurables**: Define límites personalizados de CPU (%) y memoria (MB)
- **Filtrado automático**: Excluye procesos del sistema como "System Idle Process"
- **Detección de anomalías**: Filtra valores de CPU inválidos o anómalos

### 🖥️ Interfaz Dual con Selección Inteligente
- **Pestaña "Procesos en alerta"**: Muestra solo los procesos que superan los umbrales
- **Pestaña "Todos los procesos"**: Vista completa de todos los procesos del sistema
- **Selección automática por PID**: Capacidad de localizar y seleccionar automáticamente un proceso específico
- **Navegación programática**: Cambio automático entre pestañas según la acción requerida
- **Menú contextual**: Clic derecho para acciones rápidas (cerrar, reiniciar, pausar)

### 🔧 Gestión de Procesos
- **Cerrar proceso**: Termina procesos problemáticos
- **Reiniciar proceso**: Reinicia procesos manteniendo sus parámetros
- **Pausar/Continuar**: Suspende temporalmente procesos sin cerrarlos

### 🔔 Sistema de Notificaciones Inteligentes (MEJORADO v0.1.2)
- **Notificaciones detalladas**: Incluyen información específica del proceso (PID, nombre, CPU, memoria)
- **Clic para seleccionar**: Al hacer clic en una notificación, la aplicación se abre automáticamente y selecciona el proceso problemático
- **Navegación automática**: Cambia automáticamente a la pestaña "Todos los procesos" para mostrar el proceso
- **Integración completa**: Restaura la ventana desde la bandeja y enfoca el proceso de forma inmediata
- **Acción directa**: Permite tomar medidas inmediatas sobre el proceso causante del problema

### 🎨 Sistema de Temas Completo (NUEVO v0.1.2)
- **Tres temas disponibles**: Claro, Oscuro y Sistema
- **Detección automática**: Se adapta al tema del sistema operativo
- **Configuración visual mejorada**: Ventana de configuración con vista previa detallada de colores
- **Botones funcionales**: "Cancelar", "Aplicar" y "Aplicar y Cerrar" completamente operativos
- **Tamaño optimizado**: Ventana redimensionable (500x450) para mostrar todo el contenido
- **Persistencia**: Guarda la preferencia de tema entre sesiones
- **Vista previa completa**: Muestra elementos de interfaz y colores de alertas

### 📝 Sistema de Configuración Persistente (NUEVO v0.1.2)
- **Configuración JSON**: Almacenamiento en `~/.config/quien-se-come-recursos/`
- **Exportar/Importar**: Funcionalidad completa de backup de configuración
- **Valores por defecto**: Configuración inteligente para primera ejecución
- **Validación**: Verificación automática de configuración válida
- **GUI integrada**: Ventana de configuración con controles visuales

### 📋 Sistema de Logging Completo (NUEVO v0.1.2)
- **Niveles configurables**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Archivo de logs**: Rotación automática y retención configurable
- **Visor integrado**: GUI para ver, filtrar y buscar en logs
- **Estadísticas**: Información detallada sobre eventos registrados
- **Exportar logs**: Funcionalidad para guardar logs filtrados

### 📖 Sistema de Menús Mejorado
- **Menú Archivo**: 
  - **Salir**: Cierra completamente la aplicación (incluye icono de bandeja)
- **Menú Configuración** (NUEVO):
  - **Preferencias...**: Configuración general de umbrales, monitoreo y logs
  - **Temas...**: Selección y vista previa de temas
  - **Exportar/Importar configuración**: Gestión de backups
  - **Resetear a valores por defecto**: Restauración de configuración
- **Menú Herramientas** (NUEVO):
  - **Ver Logs...**: Visor completo de logs con filtros
  - **Limpiar Logs antiguos**: Mantenimiento de archivos de log
- **Menú Opciones**: 
  - **About...**: Ventana informativa mejorada con enlaces al repositorio GitHub

## 🚀 Instalación y Uso

### Requisitos del Sistema
- **Python 3.8+**
- **Ubuntu/Linux** (principalmente, aunque compatible con Windows)
- **Entorno gráfico** con soporte para bandeja del sistema

### Instalación Automática

1. **Clona o descarga** este repositorio
2. **Ejecuta el script principal**:
   ```bash
   python3 run_app.py
   ```

El script automáticamente:
- Verifica la versión de Python (requiere 3.8+)
- Comprueba dependencias del sistema
- Crea un entorno virtual Python
- Instala todas las dependencias necesarias
- Ejecuta la aplicación con verificaciones completas

### Dependencias

Las siguientes librerías se instalan automáticamente:

```
plyer          # Notificaciones del sistema
psutil         # Información de procesos y sistema
tk             # Interfaz gráfica Tkinter
pystray        # Integración con bandeja del sistema
pillow         # Manejo de imágenes
dbus-python    # Comunicación con D-Bus (Linux)
```

## 🎮 Cómo Usar

### Configuración Inicial
1. **Ejecuta** `python3 run_app.py`
2. **Ajusta los umbrales** en la pestaña "Procesos en alerta":
   - **CPU (%)**: Porcentaje máximo de CPU permitido (por defecto: 50%)
   - **Memoria (MB)**: Memoria máxima permitida en megabytes (por defecto: 500 MB)

### Monitoreo en Tiempo Real con Notificaciones Inteligentes
- La aplicación actualiza automáticamente cada **3 segundos**
- Los procesos que superan los umbrales aparecen en la pestaña "Procesos en alerta"
- Recibirás **notificaciones detalladas del sistema** con información específica del proceso:
  - **PID del proceso**
  - **Nombre del proceso**
  - **Porcentaje de CPU actual**
  - **Memoria utilizada en MB**

### Acción Inmediata desde Notificaciones Inteligentes
1. **Haz clic en cualquier notificación de proceso problemático**
2. **La aplicación se abre automáticamente** (si estaba minimizada)
3. **Cambia automáticamente** a la pestaña "Todos los procesos"
4. **Selecciona y enfoca** el proceso problemático específico
5. **Toma acción inmediata** usando los botones o menú contextual

> **🎯 Funcionalidad Destacada**: Las notificaciones no son solo informativas, sino que permiten **acción directa inmediata**. Un simple clic te lleva directamente al proceso problemático para que puedas gestionarlo sin búsquedas manuales.

### Gestión de Procesos
1. **Selecciona un proceso** en cualquiera de las pestañas
2. **Usa los botones** o el **menú contextual** (clic derecho):
   - **Cerrar Proceso**: Termina el proceso inmediatamente
   - **Reiniciar Proceso**: Cierra y vuelve a abrir el proceso
   - **Pausar/Continuar**: Suspende o reanuda la ejecución

### Bandeja del Sistema
- **Cerrar ventana**: La aplicación se minimiza a la bandeja del sistema
- **Clic en icono de bandeja**: Restaura la ventana principal
- **Clic derecho en icono**: Menú con opciones "Mostrar ventana" y "Salir"
- **Menú Archivo > Salir**: Cierra completamente la aplicación

### Configuración de Temas
- **Acceso**: Menú **Configuración > Temas...**
- **Vista previa en tiempo real**: Selecciona un tema y ve los cambios inmediatamente
- **Tres opciones disponibles**:
  - **Tema Claro**: Interfaz tradicional con colores claros
  - **Tema Oscuro**: Interfaz moderna con colores oscuros para reducir fatiga visual
  - **Tema del Sistema**: Se adapta automáticamente al tema de tu sistema operativo
- **Botones de acción**: "Cancelar", "Aplicar" (sin cerrar) y "Aplicar y Cerrar"

### Ventana About
- **Acceso**: Menú **Opciones > About...**
- **Información del proyecto**: Versión, descripción y características
- **Enlace al repositorio**: Acceso directo al código fuente en GitHub
- **Diseño mejorado**: Interfaz clara con icono de la aplicación

## 🛠️ Estructura del Proyecto

```
recursos/
├── monitor_gui.py              # Aplicación principal con menús y lógica
├── configuracion.py            # Sistema de configuración persistente (NUEVO v0.1.2)
├── temas.py                    # Sistema de temas claro/oscuro/sistema (NUEVO v0.1.2)
├── sistema_logs.py             # Sistema de logging completo (NUEVO v0.1.2)
├── ventana_alertas.py          # Pestaña de procesos en alerta
├── ventana_todos_procesos.py   # Pestaña de todos los procesos
├── ventana_about.py            # Ventana About con info del proyecto
├── run_app.py                  # Script de instalación y ejecución con verificaciones
├── requirements.txt            # Dependencias Python (incluye dbus-python)
├── README.md                   # Este archivo
└── img/
    ├── vitamina.png           # Icono de la aplicación (formato PNG)
    └── vitamina.ico           # Icono para Windows (formato ICO)
```

### Archivos Principales

- **`monitor_gui.py`**: Archivo principal que contiene la lógica de monitoreo, interfaz principal, sistema de menús e integración completa con todos los sistemas
- **`configuracion.py`**: Sistema de configuración persistente con almacenamiento JSON, exportar/importar y valores por defecto
- **`temas.py`**: Sistema de gestión de temas (claro/oscuro/sistema) con detección automática y aplicación visual
- **`sistema_logs.py`**: Sistema completo de logging con archivo, visor GUI, filtros y estadísticas
- **`ventana_about.py`**: Módulo separado para la ventana About, incluye enlace clickeable al repositorio de GitHub
- **`run_app.py`**: Script automático con verificaciones completas del sistema, manejo de entorno virtual y ejecución robusta
- **`requirements.txt`**: Lista de dependencias incluyendo `dbus-python` para eliminar warnings en Linux

## 🔧 Configuración Avanzada

### Personalizar Umbrales
Los umbrales por defecto están definidos en `monitor_gui.py`:
```python
DEFAULT_CPU = 50    # 50% CPU
DEFAULT_MEM = 500   # 500 MB memoria
```

### Intervalo de Actualización
Para cambiar la frecuencia de actualización, modifica esta línea en `monitor_gui.py`:
```python
time.sleep(3)  # Cambia 3 por el número de segundos deseado
```

## 🐛 Solución de Problemas

### El icono no aparece en la bandeja
- **GNOME/Ubuntu**: Instala la extensión "AppIndicator Support"
- **KDE**: Asegúrate de que el widget "System Tray" esté habilitado
- **Funcionalidad mejorada**: El clic en el icono ahora restaura correctamente la ventana principal

### Warning de python-dbus
```bash
sudo apt-get install python3-dbus
```
**Nota**: Este problema está resuelto automáticamente ya que `dbus-python` está incluido en `requirements.txt`

### Permisos insuficientes
Algunos procesos del sistema requieren permisos de administrador para ser gestionados.

### La ventana About no muestra el enlace de GitHub
- Verifica que el archivo `ventana_about.py` está presente
- El enlace aparece en un frame etiquetado como "Código Fuente"
- Si el problema persiste, revisa la consola para mensajes de debug

## 📝 Historial de Versiones

### Versión 0.1.2 (Actual) - ACTUALIZACIÓN MAYOR
#### 🔔 Sistema de Notificaciones Inteligentes (NUEVO)
- ✅ **NUEVO**: Notificaciones detalladas con información específica del proceso (PID, nombre, CPU, memoria)
- ✅ **NUEVO**: Funcionalidad de clic en notificación para selección automática de proceso
- ✅ **NUEVO**: Apertura y restauración automática de ventana desde notificaciones
- ✅ **NUEVO**: Navegación automática a pestaña "Todos los procesos" al hacer clic en notificación
- ✅ **NUEVO**: Selección y enfoque automático del proceso problemático específico
- ✅ **NUEVO**: Seguimiento del último proceso problemático para acción inmediata

#### 🔧 Sistemas Principales Añadidos
- ✅ **NUEVO**: Sistema de configuración persistente completo (`configuracion.py`)
  - Configuración JSON en `~/.config/quien-se-come-recursos/`
  - Exportar/importar configuración con backup automático
  - Validación y valores por defecto inteligentes
- ✅ **NUEVO**: Sistema de temas con soporte claro/oscuro/sistema (`temas.py`)
  - Detección automática del tema del sistema operativo
  - Ventana de configuración con vista previa de colores mejorada
  - Tamaño optimizado (500x450) con botones funcionales
  - Persistencia de preferencias entre sesiones
- ✅ **NUEVO**: Sistema de logging completo (`sistema_logs.py`)
  - Archivo de logs con rotación y retención configurable
  - Visor GUI integrado con filtros y búsqueda
  - Niveles configurables y estadísticas detalladas

#### 🎨 Interfaz y Menús Mejorados
- ✅ **NUEVO**: Menú "Configuración" con ventana GUI completa y scrollable
- ✅ **NUEVO**: Menú "Herramientas" con visor de logs y mantenimiento
- ✅ **MEJORADO**: Sistema de bandeja del sistema - clic restaura correctamente la ventana
- ✅ **MEJORADO**: Ventana About con frame destacado y enlace al repositorio GitHub
- ✅ **CORREGIDO**: Ventana de configuración de tema con botones visibles y tamaño adecuado
- ✅ **MEJORADO**: Selección automática de procesos por PID en lista de todos los procesos

#### 🔧 Funcionalidades Técnicas Avanzadas
- ✅ **NUEVO**: Métodos de cambio programático entre pestañas (`cambiar_a_todos_procesos()`, `cambiar_a_procesos_alerta()`)
- ✅ **NUEVO**: Función de selección de proceso por PID (`seleccionar_proceso_por_pid()`)
- ✅ **NUEVO**: Sistema de seguimiento de procesos problemáticos (`ultimo_proceso_problematico`)
- ✅ **NUEVO**: Flujo completo de restauración y selección automática (`abrir_y_seleccionar_proceso()`)
- ✅ **CORREGIDO**: Eliminado warning de D-Bus en Linux (`dbus-python` en requirements.txt)
- ✅ **Corregido**: Eliminado warning de D-Bus en Linux (`dbus-python` en requirements.txt)
- ✅ **Añadido**: Script de verificación completo (`run_app_v2.py`)
- ✅ **Mejorado**: Modularización del código en archivos separados
- ✅ **Añadido**: Configuración visual para umbrales, intervalos y logging
- ✅ **Integrado**: Logging en todas las operaciones de monitoreo y alertas

### Versión 0.1.1
- ✅ **Básico**: Funcionalidad de monitoreo de procesos
- ✅ **Básico**: Umbrales configurables de CPU y memoria
- ✅ **Básico**: Gestión de procesos (cerrar/pausar/reiniciar)
- ✅ **Básico**: Integración básica con bandeja del sistema

## 📄 Licencia

Este proyecto es de código abierto. Siéntete libre de usarlo, modificarlo y distribuirlo.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Si encuentras bugs o tienes ideas para mejoras:

1. Visita el **repositorio en GitHub**: https://github.com/sapoclay/notificador-recursos/
2. Abre un **Issue** describiendo el problema o sugerencia
3. Haz un **Fork** del repositorio
4. Crea una **Pull Request** con tus cambios

## 👨‍💻 Autor

Creado por entreunosyceros con ☕ y 🚬 para optimizar tu sistema.

**Repositorio**: https://github.com/sapoclay/notificador-recursos/

---

### 🚀 **Destacado en v0.1.2**: 
**Sistema de Notificaciones Inteligentes** - Las notificaciones ahora incluyen información específica del proceso y permiten acción directa. Un simple clic en la notificación abre la aplicación, selecciona automáticamente el proceso problemático y te permite gestionarlo inmediatamente. ¡Sin búsquedas manuales!

*"Cuando tu equipo va lent, ¡encuentra quién se come los recursos!"* 🐸
