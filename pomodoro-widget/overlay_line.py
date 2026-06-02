"""
Overlay Ligne - Barre pleine largeur pour le timer Pomodoro
Fenêtre transparente toujours au premier plan
"""

import sys
import tkinter as tk
from typing import Optional

from timer import Phase


def get_active_screen_dimensions():
    """
    Récupère les dimensions de l'écran ACTIF où l'application est en cours d'exécution.
    Cela évite les problèmes avec les sessions RDP et les écrans multiples.
    
    Returns:
        tuple: (width, height) de l'écran actif
    """
    root = tk.Tk()
    root.withdraw()  # Cacher la fenêtre temporaire
    
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    
    root.destroy()
    return width, height


class LineOverlay:
    """
    Overlay en forme de ligne (barre fine) sur toute la largeur de l'écran
    """
    
    def __init__(self, position: str = "top"):
        """
        Initialise l'overlay ligne
        
        Args:
            position: Position de la barre ('top' ou 'bottom')
        """
        self.position = position
        self.root: Optional[tk.Tk] = None
        self.canvas: Optional[tk.Canvas] = None
        self.green_bar: Optional[int] = None
        self.red_bar: Optional[int] = None
        
        # Couleurs
        self.green_color = "#00C853"
        self.red_color = "#D50000"
        # Utiliser une couleur presque noire pour éviter les problèmes avec la taskbar
        # (le black pur peut causer des artefacts avec certaines configurations Windows)
        self.bg_color = "#000001"  # Couleur transparente (presque noir)
        
        # Dimensions
        self.height = 8
        self.width = 0
    
    def create_window(self) -> None:
        """Crée la fenêtre overlay"""
        if self.root is not None:
            return
        
        # Récupérer les dimensions de l'écran ACTIF où l'application s'exécute
        # Cela évite les problèmes avec les sessions RDP et les écrans multiples
        screen_width, screen_height = get_active_screen_dimensions()
        
        self.root = tk.Tk()
        self.root.overrideredirect(True)  # Pas de bordure
        
        # Positionner la fenêtre sur l'écran ACTIF uniquement
        # Largeur = largeur de l'écran ACTIF (pas tous les écrans combinés)
        self.width = screen_width
        
        # Positionner la fenêtre
        if self.position == "top":
            y_position = 0
        else:  # bottom
            y_position = screen_height - self.height
        
        # Configurer la fenêtre
        self.root.geometry(f"{self.width}x{self.height}+0+{y_position}")
        self.root.wm_attributes("-topmost", True)  # Toujours au premier plan
        self.root.wm_attributes("-transparentcolor", self.bg_color)  # Fond transparent
        self.root.wm_attributes("-disabled", True)  # Non cliquable
        self.root.wm_attributes("-toolwindow", True)  # Absente de la taskbar
        
        # Forcer au-dessus de la taskbar (Windows uniquement)
        if sys.platform == 'win32':
            self._force_topmost()
        
        # Créer le canvas
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height,
                               highlightthickness=0, bg=self.bg_color)
        self.canvas.pack()
        
        # Créer les barres verte et rouge
        self._create_bars()
        
        # Initialiser à 100% vert (progression = 0)
        self.update(0.0, Phase.WORK)
    
    def _force_topmost(self) -> None:
        """Force la fenêtre à être au-dessus de tout, y compris la taskbar (Windows)"""
        try:
            import ctypes
            
            HWND_TOPMOST = -1
            SWP_NOMOVE = 0x0002
            SWP_NOSIZE = 0x0001
            SWP_NOACTIVATE = 0x0010
            
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            ctypes.windll.user32.SetWindowPos(
                hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE
            )
        except:
            pass  # Ignorer les erreurs
    
    def _create_bars(self) -> None:
        """Crée les deux rectangles (vert et rouge) sur le canvas"""
        if self.canvas is None:
            return
        
        # Barre verte (fond, sera progressivement recouverte par le rouge)
        self.green_bar = self.canvas.create_rectangle(
            0, 0, self.width, self.height,
            fill=self.green_color, outline=self.green_color
        )
        
        # Barre rouge (superposée, largeur initiale = 0)
        self.red_bar = self.canvas.create_rectangle(
            0, 0, 0, self.height,
            fill=self.red_color, outline=self.red_color
        )
    
    def update(self, progress: float, phase: Phase) -> None:
        """
        Met à jour l'affichage de la barre selon la progression
        
        Args:
            progress: Progression de 0.0 (début) à 1.0 (fin)
            phase: Phase actuelle (WORK ou BREAK)
        """
        if self.canvas is None or self.green_bar is None or self.red_bar is None:
            return
        
        # Calculer la largeur de la barre rouge
        red_width = int(self.width * progress)
        
        if phase == Phase.WORK:
            # Phase WORK: vert -> rouge (remplissage de gauche à droite)
            # Barre verte: de progress à 1.0
            green_start = red_width
            green_end = self.width
            
            # Mettre à jour les barres
            self.canvas.coords(self.red_bar, 0, 0, red_width, self.height)
            self.canvas.coords(self.green_bar, green_start, 0, green_end, self.height)
            
        else:  # Phase.BREAK
            # Phase BREAK: rouge -> vert (remplissage de gauche à droite)
            # Ici, le rouge diminue et le vert augmente
            # Barre rouge: de 0 à (1.0 - progress)
            # Barre verte: de (1.0 - progress) à 1.0
            red_width = int(self.width * (1.0 - progress))
            green_start = red_width
            green_end = self.width
            
            self.canvas.coords(self.red_bar, 0, 0, red_width, self.height)
            self.canvas.coords(self.green_bar, green_start, 0, green_end, self.height)
    
    def set_position(self, position: str) -> None:
        """
        Change la position de la barre (top ou bottom)
        """
        if position not in ["top", "bottom"]:
            return
        
        self.position = position
        
        if self.root is not None:
            screen_height = self.root.winfo_screenheight()
            if position == "top":
                y_position = 0
            else:
                y_position = screen_height - self.height
            
            self.root.geometry(f"{self.width}x{self.height}+0+{y_position}")
            
            # Forcer à rester au-dessus
            if sys.platform == 'win32':
                self._force_topmost()
    
    def show(self) -> None:
        """Affiche la fenêtre"""
        if self.root is not None:
            self.root.deiconify()
    
    def hide(self) -> None:
        """Masque la fenêtre"""
        if self.root is not None:
            self.root.withdraw()
    
    def destroy(self) -> None:
        """Détruit la fenêtre"""
        if self.root is not None:
            self.root.destroy()
            self.root = None
            self.canvas = None
            self.green_bar = None
            self.red_bar = None
    
    def is_visible(self) -> bool:
        """Retourne True si la fenêtre est visible"""
        if self.root is None:
            return False
        return self.root.winfo_viewable()
