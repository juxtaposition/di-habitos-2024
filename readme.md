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

Iniciar el crontab:

bashCopypython manage.py crontab add
Comandos útiles para manejar crontab:
bashCopy# Ver trabajos programados
python manage.py crontab show

# Eliminar trabajos programados
python manage.py crontab remove

# Reiniciar trabajos programados
python manage.py crontab remove
python manage.py crontab add