"""
Overlay Compteur - Mini-fenêtre avec affichage numérique MM:SS
Fenêtre draggable avec fond semi-transparent
"""

import tkinter as tk
from typing import Optional, Tuple

from timer import Phase
from screen_utils import get_screen_center


class CounterOverlay:
    """
    Overlay en forme de compteur numérique
    """
    
    def __init__(self):
        """Initialise l'overlay compteur"""
        self.root: Optional[tk.Tk] = None
        self.label: Optional[tk.Label] = None
        
        # Couleurs
        self.work_color = "#00C853"  # Vert
        self.break_color = "#2196F3"  # Bleu
        self.bg_color = "#000000"
        
        # Dimensions
        self.width = 120
        self.height = 40
        
        # Position - centré sur l'écran principal par défaut
        screen_center_x, screen_center_y = get_screen_center()
        self.x = screen_center_x - self.width // 2
        self.y = screen_center_y - self.height // 2
        
        # État du drag
        self.drag_start: Optional[Tuple[int, int]] = None
        self.window_start: Optional[Tuple[int, int]] = None
        
        # Visibilité
        self.visible = True
    
    def create_window(self) -> None:
        """Crée la fenêtre overlay compteur"""
        if self.root is not None:
            return
        
        self.root = tk.Tk()
        self.root.overrideredirect(True)  # Pas de bordure
        self.root.geometry(f"{self.width}x{self.height}+{self.x}+{self.y}")
        self.root.wm_attributes("-topmost", True)  # Toujours au premier plan
        self.root.wm_attributes("-alpha", 0.8)  # Fond semi-transparent
        self.root.wm_attributes("-transparentcolor", self.bg_color)
        
        # Créer le label
        self.label = tk.Label(
            self.root,
            text="25:00",
            font=("Courier New", 20, "bold"),
            fg=self.work_color,
            bg=self.bg_color
        )
        self.label.pack(expand=True, fill="both")
        
        # Configurer le drag
        self.label.bind("<Button-1>", self._on_drag_start)
        self.label.bind("<B1-Motion>", self._on_drag_motion)
        self.label.bind("<Double-Button-1>", self._on_double_click)
        
        # Initialiser l'affichage
        self.update(0.0, Phase.WORK, "25:00")
    
    def update(self, progress: float, phase: Phase, time_str: str) -> None:
        """
        Met à jour l'affichage du compteur
        
        Args:
            progress: Progression de 0.0 à 1.0 (non utilisée ici)
            phase: Phase actuelle (WORK ou BREAK)
            time_str: Temps restant au format MM:SS
        """
        if self.label is None:
            return
        
        # Mettre à jour la couleur selon la phase
        if phase == Phase.WORK:
            color = self.work_color
        else:
            color = self.break_color
        
        self.label.config(text=time_str, fg=color)
    
    def _on_drag_start(self, event) -> None:
        """Début du drag"""
        self.drag_start = (event.x_root, event.y_root)
        self.window_start = (self.root.winfo_x(), self.root.winfo_y())
    
    def _on_drag_motion(self, event) -> None:
        """Déplacement du drag"""
        if self.drag_start is None or self.window_start is None:
            return
        
        dx = event.x_root - self.drag_start[0]
        dy = event.y_root - self.drag_start[1]
        
        new_x = self.window_start[0] + dx
        new_y = self.window_start[1] + dy
        
        self.root.geometry(f"+{new_x}+{new_y}")
    
    def _on_double_click(self, event) -> None:
        """Double-clic pour masquer/afficher"""
        if self.visible:
            self.hide()
        else:
            self.show()
        self.visible = not self.visible
    
    def show(self) -> None:
        """Affiche la fenêtre"""
        if self.root is not None:
            self.root.deiconify()
            self.visible = True
    
    def hide(self) -> None:
        """Masque la fenêtre"""
        if self.root is not None:
            self.root.withdraw()
            self.visible = False
    
    def destroy(self) -> None:
        """Détruit la fenêtre"""
        if self.root is not None:
            self.root.destroy()
            self.root = None
            self.label = None
    
    def is_visible(self) -> bool:
        """Retourne True si la fenêtre est visible"""
        if self.root is None:
            return False
        return self.root.winfo_viewable() and self.visible
