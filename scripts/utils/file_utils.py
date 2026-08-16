"""
Datei-Hilfsfunktionen für die Pipeline.
"""

from pathlib import Path
from typing import List, Optional


def ensure_directory(directory: str) -> Path:
    """
    Stelle sicher, dass ein Verzeichnis existiert.
    
    Args:
        directory: Pfad zum Verzeichnis
        
    Returns:
        Path-Objekt des Verzeichnisses
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_screenshots(directory: str = 'screenshots') -> List[Path]:
    """
    Hole alle Screenshots aus dem Verzeichnis (sortiert nach Zeit).
    
    Args:
        directory: Screenshot-Verzeichnis
        
    Returns:
        Liste von Path-Objekten, sortiert nach Dateiname
    """
    screenshot_dir = Path(directory)
    
    if not screenshot_dir.exists():
        return []
    
    # Finde alle JPG-Dateien
    screenshots = sorted(screenshot_dir.glob('screenshot_*.jpg'))
    return screenshots


def cleanup_old_files(directory: str, keep_count: int = 100) -> int:
    """
    Lösche alte Dateien und behalte nur die neuesten.
    
    Args:
        directory: Zu bereinigende Verzeichnis
        keep_count: Anzahl beizubehaltendes Dateien
        
    Returns:
        Anzahl gelöschter Dateien
    """
    dir_path = Path(directory)
    
    if not dir_path.exists():
        return 0
    
    files = sorted(dir_path.glob('*'), key=lambda p: p.stat().st_mtime)
    
    deleted = 0
    if len(files) > keep_count:
        for file_path in files[:-keep_count]:
            file_path.unlink()
            deleted += 1
    
    return deleted
