# Unicared Backend

Backend para la plataforma Unicared, construido con Django.

## 📋 Requisitos Previos

- **Python**: Versión 3.12 o superior.
- **Pip**: Gestor de paquetes de Python.
- **Virtualenv**: Para crear entornos virtuales aislados (recomendado).

## 🚀 Instalación y Ejecución

Sigue estos pasos para levantar el proyecto en tu entorno local:

### 1. Clonar el repositorio y navegar al directorio
(Si ya tienes el proyecto descargado, omite el clonado).

```bash
cd unicared-backend
```

### 2. Crear y activar un entorno virtual

Es altamente recomendable usar un entorno virtual para manejar las dependencias.

**En Windows:**
```powershell
python -m venv venv
.\venv\Scripts\Activate
```

**En macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crea un archivo llamado `.env` en la raíz del backend (`unicared-backend/`) y añade las siguientes variables. Puedes ajustar los valores según tu entorno local.

```env
# Clave secreta para desarrollo (NO usar en producción)
SECRET_KEY=django-insecure-tu-clave-secreta-aqui

# Activar modo depuración
DEBUG=True

# Base de datos (Opcional - por defecto usa SQLite)
# DATABASE_URL=

# Hosts permitidos (separados por coma si son varios, o ajusta en settings.py)
PRODUCTION_HOST=localhost
STAGING_HOST=localhost
```

### 5. Aplicar migraciones

Prepara la base de datos con las tablas necesarias:

```bash
python manage.py migrate
```

### 6. Crear un superusuario (Opcional)

Si deseas acceder al panel de administración de Django:

```bash
python manage.py createsuperuser
```

### 7. Ejecutar el servidor

```bash
python manage.py runserver
```

El backend estará disponible en: **http://localhost:8000**

## 🛠️ Estructura del Proyecto

- `core/`: Configuración principal del proyecto (settings, urls, wsgi).
- `teachers/`: Aplicación principal que contiene modelos y lógica de negocio.
- `manage.py`: Utilidad de línea de comandos de Django.
- `requirements.txt`: Lista de dependencias del proyecto.
