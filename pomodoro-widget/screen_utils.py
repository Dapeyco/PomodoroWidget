"""
Utilitaires pour la gestion des écrans multi-moniteurs
Permet de détecter l'écran principal et tous les écrans disponibles
"""

import sys
import tkinter as tk
from typing import Optional, Tuple, List


def get_all_screens() -> List[Tuple[int, int, int, int]]:
    """
    Récupère les dimensions de TOUS les écrans (multi-écrans).
    Retourne une liste de tuples (x, y, width, height) pour chaque écran.
    
    Sur Windows: utilise ctypes pour obtenir les infos des écrans
    Sur autres plateformes: utilise tkinter
    
    Returns:
        List of (x, y, width, height) tuples for each screen
    """
    screens = []
    
    if sys.platform == 'win32':
        try:
            import ctypes
            from ctypes import wintypes
            
            # Définir les types et constantes Windows
            class RECT(ctypes.Structure):
                _fields_ = [
                    ("left", wintypes.LONG),
                    ("top", wintypes.LONG),
                    ("right", wintypes.LONG),
                    ("bottom", wintypes.LONG),
                ]
            
            class MONITORINFO(ctypes.Structure):
                _fields_ = [
                    ("cbSize", wintypes.DWORD),
                    ("rcMonitor", RECT),
                    ("rcWork", RECT),
                    ("dwFlags", wintypes.DWORD),
                ]
            
            # Fonction pour énumérer les écrans
            def enum_monitor_callback(hMonitor, hdcMonitor, lprcMonitor, dwData):
                mi = MONITORINFO()
                mi.cbSize = ctypes.sizeof(MONITORINFO)
                ctypes.windll.user32.GetMonitorInfoW(hMonitor, ctypes.byref(mi))
                
                rect = mi.rcMonitor
                x = rect.left
                y = rect.top
                width = rect.right - rect.left
                height = rect.bottom - rect.top
                screens.append((x, y, width, height))
                return 1
            
            # Type de callback
            MONITORENUMPROC = ctypes.WINFUNCTYPE(
                wintypes.BOOL, wintypes.HMONITOR, wintypes.HDC, ctypes.POINTER(RECT), wintypes.LPARAM
            )
            
            # Appeler EnumDisplayMonitors
            ctypes.windll.user32.EnumDisplayMonitors(
                None, None, MONITORENUMPROC(enum_monitor_callback), 0
            )
        except Exception:
            # Fallback si ctypes échoue
            pass
    
    # Si pas d'écrans détectés ou pas Windows, utiliser tkinter
    if not screens:
        root = tk.Tk()
        root.withdraw()
        
        try:
            screens.append((0, 0, root.winfo_screenwidth(), root.winfo_screenheight()))
        except:
            screens.append((0, 0, root.winfo_screenwidth(), root.winfo_screenheight()))
        
        root.destroy()
    
    return screens


def get_primary_screen_dimensions() -> Tuple[int, int]:
    """
    Récupère les dimensions de l'ÉCRAN PRINCIPAL.
    L'écran principal est celui qui contient la barre des tâches (x=0, y=0).
    
    Returns:
        tuple: (width, height) de l'écran principal
    """
    screens = get_all_screens()
    
    if not screens:
        # Fallback
        return (1920, 1080)
    
    # L'écran principal est généralement celui avec x=0, y=0
    # ou le premier dans la liste
    primary_screen = screens[0]
    
    # Vérifier si un écran commence à (0, 0) - c'est généralement le principal
    for screen in screens:
        x, y, width, height = screen
        if x == 0 and y == 0:
            primary_screen = screen
            break
    
    return (primary_screen[2], primary_screen[3])


def get_primary_screen_geometry() -> Tuple[int, int, int, int]:
    """
    Récupère la géométrie complète de l'écran principal (x, y, width, height).
    
    Returns:
        tuple: (x, y, width, height) de l'écran principal
    """
    screens = get_all_screens()
    
    if not screens:
        return (0, 0, 1920, 1080)
    
    # L'écran principal est généralement celui avec x=0, y=0
    primary_screen = screens[0]
    
    for screen in screens:
        x, y, width, height = screen
        if x == 0 and y == 0:
            primary_screen = screen
            break
    
    return primary_screen


def get_screen_center(screen_geometry: Optional[Tuple[int, int, int, int]] = None) -> Tuple[int, int]:
    """
    Calcule le centre d'un écran.
    
    Args:
        screen_geometry: Tuple (x, y, width, height) ou None pour l'écran principal
    
    Returns:
        tuple: (x_center, y_center)
    """
    if screen_geometry is None:
        screen_geometry = get_primary_screen_geometry()
    
    x, y, width, height = screen_geometry
    return (x + width // 2, y + height // 2)


def get_screen_at_position(x: int, y: int) -> Optional[Tuple[int, int, int, int]]:
    """
    Trouve l'écran qui contient les coordonnées (x, y).
    
    Args:
        x: Coordonnée X
        y: Coordonnée Y
    
    Returns:
        Tuple (x, y, width, height) de l'écran ou None
    """
    screens = get_all_screens()
    for screen in screens:
        sx, sy, sw, sh = screen
        if sx <= x < sx + sw and sy <= y < sy + sh:
            return screen
    return None
