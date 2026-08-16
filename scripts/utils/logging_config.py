"""
Zentrale Logging-Konfiguration für alle Pipeline-Module.
"""

import logging
from pathlib import Path


def get_logger(name: str) -> logging.Logger:
    """
    Erstelle einen Logger mit standardisierter Konfiguration.
    
    Args:
        name: Name des Loggers (üblicherweise __name__)
        
    Returns:
        logging.Logger: Konfigurierter Logger
    """
    logger = logging.getLogger(name)
    
    # Stelle sicher, dass logs-Verzeichnis existiert
    Path('logs').mkdir(parents=True, exist_ok=True)
    
    # Nur konfigurieren, wenn noch keine Handler vorhanden
    if not logger.handlers:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # File Handler
        fh = logging.FileHandler('logs/pipeline.log')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        
        # Console Handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
        logger.setLevel(logging.DEBUG)
    
    return logger
