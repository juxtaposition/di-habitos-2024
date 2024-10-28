# Proyecto Django de Hábitos 2024

Este es un proyecto Django que le da seguimiento a habitos que quiere establecer el usuario.

## Requisitos previos

- Python 3.x
- pip (gestor de paquetes de Python)
- virtualenv (recomendado)

## Configuración del entorno

1. Clona el repositorio:
   ```
   git clone https://github.com/juxtaposition/di-habitos-2024/tree/develoment
   cd di-habitos-2024
   ```

2. Crea y activa un entorno virtual:
   ```
   python -m venv venv
   source venv/bin/activate  # En Unix o MacOS
   venv\Scripts\activate     # En Windows
   ```

3. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

4. Configura las variables de entorno:
   - Copia el archivo `.env.example` a `.env` y edita las variables según sea necesario.

5. Aplica las migraciones:
   ```
   python manage.py migrate
   ```

## Ejecutar el proyecto

1. Asegúrate de que el entorno virtual esté activado.

2. Ejecuta el servidor de desarrollo:
   ```
   python manage.py runserver
   ```

3. Abre un navegador y visita `http://127.0.0.1:8000`

## Configuración de Notificaciones

El proyecto utiliza django-crontab para manejar las notificaciones automáticas de hábitos. Para configurar el sistema de notificaciones, sigue estos pasos:

1. Asegúrate de que django-crontab esté instalado:
   ```bash
   pip install django-crontab
   ```

2. Inicia el servicio de cron para las notificaciones:
   ```bash
   python manage.py crontab add
   ```

### Comandos útiles para gestionar notificaciones

- Ver trabajos programados activos:
  ```bash
  python manage.py crontab show
  ```

- Eliminar todos los trabajos programados:
  ```bash
  python manage.py crontab remove
  ```

- Reiniciar los trabajos programados:
  ```bash
  python manage.py crontab remove
  python manage.py crontab add
  ```

### Frecuencia de las Notificaciones

Las notificaciones se generan según la frecuencia configurada para cada hábito:

- **Hábitos Diarios**: 
  - Notificación inicial a las 8:00 AM
  - Recordatorios distribuidos durante el día según el número de repeticiones
  - Notificación de urgencia a las 8:00 PM si hay repeticiones pendientes

- **Hábitos Semanales**:
  - Notificación inicial los lunes
  - Recordatorios distribuidos durante la semana
  - Notificación final los domingos

- **Hábitos Mensuales**:
  - Notificación al inicio del mes
  - Recordatorios semanales
  - Notificación de urgencia al final del mes

### Solución de problemas

Si las notificaciones no aparecen:
1. Verifica que el cron está activo con `python manage.py crontab show`
2. Revisa los logs del sistema para errores
3. Reinicia el servicio de cron con los comandos mencionados arriba

**Nota**: Yo lo hice en Mac pero en Windows, es posible que haya que configurar el Programador de Tareas de Windows o usar una alternativa como Windows Task Scheduler.