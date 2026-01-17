"""
Configuración de logging para PharmGest
"""
import logging
import sys
from pathlib import Path

def setup_logging(log_level=logging.INFO):
    """
    Configura el sistema de logging para la aplicación
    """
    # Crear directorio de logs si no existe
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configurar formato
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Configurar handlers
    handlers = [
        logging.FileHandler(log_dir / "pharmgest.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
    
    # Configurar logging
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=handlers
    )
    
    return logging.getLogger(__name__)

# Crear logger principal
logger = logging.getLogger("pharmgest")
setup_logging()
