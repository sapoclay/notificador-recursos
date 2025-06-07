# 🐸 ¿Quién se come los recursos?

Un monitor de recursos del sistema en tiempo real para identificar procesos que consumen excesivamente CPU y memoria.

![Monitor de Recursos](img/vitamina.png)

## 📋 Descripción

Este programa es una herramienta de monitoreo de sistema que te ayuda a identificar qué procesos están consumiendo demasiados recursos (CPU y memoria) en tu computadora. Es especialmente útil cuando tu sistema se vuelve lento y necesitas encontrar rápidamente el culpable.

![about-quiensecome](https://github.com/user-attachments/assets/34415df1-b17e-4fe0-a417-46edeaa18fb4)

### ¿Para qué sirve?

- **Detectar procesos problemáticos**: Identifica automáticamente procesos que superan umbrales de CPU y memoria
- **Monitoreo en tiempo real**: Actualización continua cada 3 segundos
- **Notificaciones de alerta**: Te avisa cuando hay procesos consumiendo recursos excesivos
- **Gestión de procesos**: Permite cerrar, reiniciar o pausar procesos directamente desde la interfaz
- **Ejecución en segundo plano**: Se minimiza a la bandeja del sistema para monitoreo continuo

## ✨ Características

### 🎯 Monitoreo Inteligente
- **Umbrales configurables**: Define límites personalizados de CPU (%) y memoria (MB)
- **Filtrado automático**: Excluye procesos del sistema como "System Idle Process"
- **Detección de anomalías**: Filtra valores de CPU inválidos o anómalos

### 🖥️ Interfaz Dual
- **Pestaña "Procesos en alerta"**: Muestra solo los procesos que superan los umbrales
- **Pestaña "Todos los procesos"**: Vista completa de todos los procesos del sistema
- **Menú contextual**: Clic derecho para acciones rápidas

### 🔧 Gestión de Procesos
- **Cerrar proceso**: Termina procesos problemáticos
- **Reiniciar proceso**: Reinicia procesos manteniendo sus parámetros
- **Pausar/Continuar**: Suspende temporalmente procesos sin cerrarlos

### 🔔 Sistema de Notificaciones
- **Alertas del sistema**: Notificaciones cuando hay nuevos procesos en alerta
- **Integración con bandeja**: Icono en la bandeja del sistema para acceso rápido

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
- Crea un entorno virtual Python
- Instala todas las dependencias necesarias
- Ejecuta la aplicación

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

### Monitoreo en Tiempo Real
- La aplicación actualiza automáticamente cada **3 segundos**
- Los procesos que superan los umbrales aparecen en la pestaña "Procesos en alerta"
- Recibirás **notificaciones del sistema** cuando se detecten nuevos procesos problemáticos

### Gestión de Procesos
1. **Selecciona un proceso** en cualquiera de las pestañas
2. **Usa los botones** o el **menú contextual** (clic derecho):
   - **Cerrar Proceso**: Termina el proceso inmediatamente
   - **Reiniciar Proceso**: Cierra y vuelve a abrir el proceso
   - **Pausar/Continuar**: Suspende o reanuda la ejecución

### Bandeja del Sistema
- **Cerrar ventana**: La aplicación se minimiza a la bandeja del sistema
- **Clic derecho en icono**: Menú con opciones "Mostrar ventana" y "Salir"
- **Menú Archivo > Salir**: Cierra completamente la aplicación

## 🛠️ Estructura del Proyecto

```
recursos/
├── monitor_gui.py              # Aplicación principal
├── run_app.py                  # Script de instalación y ejecución
├── ventana_alertas.py          # Pestaña de procesos en alerta
├── ventana_todos_procesos.py   # Pestaña de todos los procesos
├── ventana_about.py            # Ventana About/Acerca de
├── requirements.txt            # Dependencias Python
├── README.md                   # Este archivo
└── img/
    ├── vitamina.png           # Icono de la aplicación
    └── vitamina.ico           # Icono para Windows
```

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

### Warning de python-dbus
```bash
sudo apt-get install python3-dbus
```

### Permisos insuficientes
Algunos procesos del sistema requieren permisos de administrador para ser gestionados.

## 📄 Licencia

Este proyecto es de código abierto. Siéntete libre de usarlo, modificarlo y distribuirlo.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Si encuentras bugs o tienes ideas para mejoras:

1. Abre un **Issue** describiendo el problema o sugerencia
2. Haz un **Fork** del repositorio
3. Crea una **Pull Request** con tus cambios

## 👨‍💻 Autor

Creado con ❤️ para ayudar a identificar procesos problemáticos en el sistema.

---

*"Cuando tu computadora va lenta, ¡encuentra quién se come los recursos!"* 🐸
