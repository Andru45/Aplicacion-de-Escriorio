"""
Configuración centralizada de constantes para PharmGest
"""

# --- UMBRALES DE STOCK ---
STOCK_CRITICO = 20  # Menos de 20 unidades (aprox 2 cajas)
STOCK_BAJO = 50     # Menos de 50 unidades (aprox 5 cajas)

# --- COLORES DEL SEMÁFORO DE STOCK ---
COLOR_STOCK_CRITICO = "#ffcccc"  # Rojo suave
COLOR_STOCK_BAJO = "#fff4cc"     # Amarillo suave
COLOR_TEXT = "black"

# --- CONFIGURACIÓN DE FECHA DE VENCIMIENTO ---
DIAS_VENCIMIENTO_ADVERTENCIA = 90  # Días antes del vencimiento para mostrar advertencia

# --- LÍMITES DE PAGINACIÓN ---
MAX_RESULTS_PER_PAGE = 100  # Máximo de registros a mostrar sin paginación

# --- FORMATO DE PRECIOS ---
PRICE_DECIMALS = 2  # Decimales para mostrar precios
