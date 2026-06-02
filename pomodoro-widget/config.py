"""
Configuration persistante pour PomodoroWidget
Stocke les parametres dans %APPDATA%\\PomodoroWidget\\config.json
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any


# Chemins de configuration
if sys.platform == 'win32':
    APPDATA = os.environ.get('APPDATA', os.path.expanduser('~/AppData/Roaming'))
    CONFIG_DIR = Path(APPDATA) / 'PomodoroWidget'
else:
    CONFIG_DIR = Path.home() / '.config' / 'PomodoroWidget'

CONFIG_FILE = CONFIG_DIR / 'config.json'

# Configuration par défaut
DEFAULT_CONFIG = {
    "work_minutes": 25,
    "break_minutes": 5,
    "display_mode": "line",
    "line_position": "top",
    "autostart": False
}


def ensure_config_dir():
    """Crée le répertoire de configuration s'il n'existe pas"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> Dict[str, Any]:
    """
    Charge la configuration depuis le fichier config.json
    Retourne la configuration par défaut si le fichier n'existe pas
    """
    ensure_config_dir()
    
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Fusionner avec les valeurs par défaut pour les clés manquantes
                for key, value in DEFAULT_CONFIG.items():
                    if key not in config:
                        config[key] = value
                return config
        except (json.JSONDecodeError, IOError):
            # Si le fichier est corrompu, retourner la config par défaut
            pass
    
    return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any]) -> None:
    """
    Sauvegarde la configuration dans config.json
    """
    ensure_config_dir()
    
    # Fusionner avec la config par défaut pour s'assurer que toutes les clés sont présentes
    full_config = DEFAULT_CONFIG.copy()
    full_config.update(config)
    
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(full_config, f, indent=4, ensure_ascii=False)


def get_config_path() -> str:
    """Retourne le chemin du fichier de configuration"""
    return str(CONFIG_FILE)
