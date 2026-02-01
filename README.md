# PharmGest - Sistema de Gestión para Farmacias

PharmGest es una aplicación de escritorio para gestión de farmacias desarrollada con Python, PyQt6 y SQLAlchemy. Permite controlar inventario, realizar ventas en punto de venta (POS), gestionar lotes de productos y generar facturas en PDF.

## 📋 Requisitos Previos

Antes de descargar y ejecutar el proyecto, asegúrate de tener instalado:

- **Python 3.8 o superior**: [Descargar Python](https://www.python.org/downloads/)
- **Visual Studio Code**: [Descargar VS Code](https://code.visualstudio.com/)
- **Git**: [Descargar Git](https://git-scm.com/downloads)

## 📥 ¿Cómo Descargar el Proyecto en VS Code?

### Opción 1: Clonar directamente desde VS Code

1. **Abre Visual Studio Code**
2. Presiona `Ctrl+Shift+P` (o `Cmd+Shift+P` en Mac) para abrir la paleta de comandos
3. Escribe `Git: Clone` y selecciónalo
4. Pega la URL del repositorio:
   ```
   https://github.com/Andru45/Aplicacion-de-Escriorio.git
   ```
5. Selecciona la carpeta donde quieres guardar el proyecto
6. Cuando termine de clonar, haz clic en "Abrir" para abrir el proyecto

### Opción 2: Clonar usando la terminal

1. Abre una terminal (Command Prompt, PowerShell, o Terminal en Mac/Linux)
2. Navega a la carpeta donde quieres descargar el proyecto:
   ```bash
   cd C:\Users\TuUsuario\Documentos  # En Windows
   # o
   cd ~/Documents  # En Mac/Linux
   ```
3. Clona el repositorio:
   ```bash
   git clone https://github.com/Andru45/Aplicacion-de-Escriorio.git
   ```
4. Abre VS Code en la carpeta del proyecto:
   ```bash
   cd Aplicacion-de-Escriorio/PharmGest
   code .
   ```

### Opción 3: Descargar como ZIP

1. Ve al repositorio en GitHub: https://github.com/Andru45/Aplicacion-de-Escriorio
2. Haz clic en el botón verde "Code"
3. Selecciona "Download ZIP"
4. Extrae el archivo ZIP en tu carpeta preferida
5. Abre VS Code y selecciona `Archivo → Abrir Carpeta...` → Navega a la carpeta extraída y abre la carpeta **PharmGest**

> **Nota:** El repositorio contiene una carpeta llamada "PharmGest" donde está todo el código del proyecto. Asegúrate de abrir esa carpeta en VS Code.

## 🛠️ Configuración del Entorno

### 1. Crear y Activar el Entorno Virtual

Una vez que hayas clonado o descargado el repositorio, navega a la carpeta **PharmGest** dentro del proyecto:

```bash
cd Aplicacion-de-Escriorio/PharmGest
```

Es importante usar un entorno virtual para aislar las dependencias del proyecto:

**En Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**En Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Deberías ver `(venv)` al inicio de tu línea de comandos, indicando que el entorno virtual está activo.

### 2. Instalar Dependencias

Con el entorno virtual activado, instala las dependencias necesarias:

**Opción 1 - Usar requirements.txt (recomendado):**
```bash
pip install -r requirements.txt
```

**Opción 2 - Instalación manual:**
```bash
pip install PyQt6 SQLAlchemy reportlab
```

**Dependencias principales:**
- `PyQt6`: Framework de interfaz gráfica
- `SQLAlchemy`: ORM para gestión de base de datos
- `reportlab`: Generación de facturas en PDF

### 3. Inicializar la Base de Datos

Ejecuta los siguientes scripts para crear y poblar la base de datos:

```bash
# Crear la base de datos
python create_db.py

# Crear usuario vendedor de prueba
python create_seller.py

# Poblar con datos de ejemplo (opcional)
python seed_data.py
```

## 🚀 Ejecutar la Aplicación

Una vez configurado el entorno, asegúrate de estar en la carpeta **PharmGest** y ejecuta la aplicación:

```bash
# Si estás en la carpeta PharmGest
python src/pharmgest/main.py
```

O si estás en la raíz del repositorio:

```bash
cd PharmGest
python src/pharmgest/main.py
```

### Credenciales de Acceso

**Usuario Administrador:**
- Usuario: `admin`
- Contraseña: `admin123`

**Usuario Vendedor:**
- Usuario: `vendedor`
- Contraseña: `vendedor123`

## 🔧 Extensiones Recomendadas para VS Code

Para mejorar tu experiencia de desarrollo, instala estas extensiones en VS Code:

1. **Python** (Microsoft) - ID: `ms-python.python`
   - Soporte completo para Python
   
2. **Pylance** (Microsoft) - ID: `ms-python.vscode-pylance`
   - IntelliSense mejorado para Python
   
3. **Python Debugger** (Microsoft) - ID: `ms-python.debugpy`
   - Depuración de código Python

**Cómo instalar extensiones:**
1. Presiona `Ctrl+Shift+X` para abrir el panel de extensiones
2. Busca el nombre de la extensión
3. Haz clic en "Instalar"

## 📁 Estructura del Proyecto

```
Aplicacion-de-Escriorio/         # Repositorio raíz
└── PharmGest/                   # Carpeta principal del proyecto
    ├── src/pharmgest/           # Código fuente principal
    │   ├── main.py             # Punto de entrada de la aplicación
    │   ├── config/             # Configuraciones (BD, logging, settings)
    │   ├── database/           # Modelos de base de datos
    │   ├── services/           # Servicios (generación de facturas)
    │   └── ui/                 # Interfaz gráfica (widgets y diálogos)
    ├── facturas/               # Carpeta donde se guardan las facturas PDF
    ├── logs/                   # Registros de la aplicación
    ├── requirements.txt        # Dependencias del proyecto
    ├── create_db.py            # Script para crear la base de datos
    ├── create_seller.py        # Script para crear usuario vendedor
    ├── seed_data.py            # Script para datos de ejemplo
    └── pharmgest.db            # Base de datos SQLite (se crea automáticamente)
```

## 💡 Funcionalidades Principales

- **Gestión de Inventario**: Control de productos, categorías y lotes con fechas de vencimiento
- **Punto de Venta (POS)**: Interfaz rápida para realizar ventas
- **Productos Fraccionables**: Soporte para productos que se venden por caja o unidad suelta
- **Control de Stock**: Sistema de alertas visuales (rojo/amarillo) para stock bajo o crítico
- **Roles de Usuario**: Administrador y Vendedor con permisos diferenciados
- **Historial de Ventas**: Consulta de ventas realizadas con filtros por fecha
- **Generación de Facturas**: Facturas en PDF con toda la información de la venta

## 🐛 Solución de Problemas Comunes

### Error: "No module named 'PyQt6'"
**Solución:** Asegúrate de que el entorno virtual esté activado y ejecuta:
```bash
pip install PyQt6
```

### Error: "No such file or directory: pharmgest.db"
**Solución:** Ejecuta el script de creación de base de datos:
```bash
python create_db.py
```

### Error al abrir VS Code con `code .`
**Solución:** Asegúrate de que VS Code esté en tu PATH. En Windows, reinstala VS Code marcando "Agregar a PATH". En Mac, abre VS Code y usa `Cmd+Shift+P` → "Shell Command: Install 'code' command in PATH".

## 📝 Desarrollo

### Actualizar el Esquema de la Base de Datos

Si modificas los modelos en `database/models.py`:

```bash
python src/pharmgest/update_db_schema.py
```

### Ver Logs de la Aplicación

Los logs se guardan en la carpeta `logs/` con información detallada de la ejecución.

## 🤝 Contribuir

Si deseas contribuir al proyecto:

1. Haz un fork del repositorio
2. Crea una rama para tu funcionalidad (`git checkout -b feature/nueva-funcionalidad`)
3. Haz commit de tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Haz push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es de código abierto. Consulta el archivo LICENSE para más detalles.

## 📧 Soporte

Si tienes problemas o preguntas:
- Abre un issue en GitHub
- Revisa la documentación en `.github/copilot-instructions.md`

---

**¡Listo! Ahora puedes descargar, configurar y ejecutar PharmGest en VS Code.** 🎉
