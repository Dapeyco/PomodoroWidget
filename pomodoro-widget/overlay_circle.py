"""
Overlay Cercle - Timer Pomodoro en forme de cercle animé
Fenêtre ronde flottante et draggable
"""

import tkinter as tk
from typing import Optional, Tuple

from timer import Phase
from screen_utils import get_screen_center, get_primary_screen_geometry


class CircleOverlay:
    """
    Overlay en forme de cercle avec arc animé
    """
    
    def __init__(self):
        """Initialise l'overlay cercle"""
        self.root: Optional[tk.Tk] = None
        self.canvas: Optional[tk.Canvas] = None
        self.time_label: Optional[int] = None
        self.arc: Optional[int] = None
        
        # Couleurs
        self.work_color = "#00C853"  # Vert
        self.break_color = "#2196F3"  # Bleu
        self.bg_color = "#202020"
        self.text_color_work = "#00C853"
        self.text_color_break = "#2196F3"
        
        # Dimensions
        self.diameter = 80
        self.radius = self.diameter // 2
        
        # Position - centré sur l'écran principal par défaut
        screen_center_x, screen_center_y = get_screen_center()
        self.x = screen_center_x - self.diameter // 2
        self.y = screen_center_y - self.diameter // 2
        
        # État du drag
        self.drag_start: Optional[Tuple[int, int]] = None
        self.window_start: Optional[Tuple[int, int]] = None
    
    def create_window(self) -> None:
        """Crée la fenêtre overlay cercle"""
        if self.root is not None:
            return
        
        self.root = tk.Tk()
        self.root.overrideredirect(True)  # Pas de bordure
        self.root.geometry(f"{self.diameter}x{self.diameter}+{self.x}+{self.y}")
        self.root.wm_attributes("-topmost", True)  # Toujours au premier plan
        self.root.wm_attributes("-alpha", 0.9)  # Légèrement transparent
        
        # Créer le canvas
        self.canvas = tk.Canvas(self.root, width=self.diameter, height=self.diameter,
                               highlightthickness=0, bg=self.bg_color)
        self.canvas.pack()
        
        # Créer l'arc et le label de temps
        self._create_arc()
        self._create_time_label()
        
        # Initialiser l'affichage
        self.update(0.0, Phase.WORK, "25:00")
        
        # Configurer le drag
        self.canvas.bind("<Button-1>", self._on_drag_start)
        self.canvas.bind("<B1-Motion>", self._on_drag_motion)
    
    def _create_arc(self) -> None:
        """Crée l'arc circulaire"""
        if self.canvas is None:
            return
        
        # Coordonnées du rectangle englobant
        x0 = 5
        y0 = 5
        x1 = self.diameter - 5
        y1 = self.diameter - 5
        
        # Créer l'arc (initialement vide)
        self.arc = self.canvas.create_arc(
            x0, y0, x1, y1,
            start=0, extent=0,
            width=4, style=tk.ARC,
            outline=self.work_color
        )
    
    def _create_time_label(self) -> None:
        """Crée le label pour afficher le temps"""
        if self.canvas is None:
            return
        
        self.time_label = self.canvas.create_text(
            self.radius, self.radius,
            text="25:00",
            fill=self.text_color_work,
            font=("Courier New", 14, "bold")
        )
    
    def update(self, progress: float, phase: Phase, time_str: str) -> None:
        """
        Met à jour l'affichage du cercle
        
        Args:
            progress: Progression de 0.0 à 1.0
            phase: Phase actuelle (WORK ou BREAK)
            time_str: Temps restant au format MM:SS
        """
        if self.canvas is None or self.arc is None or self.time_label is None:
            return
        
        # Mettre à jour la couleur selon la phase
        if phase == Phase.WORK:
            color = self.work_color
            text_color = self.text_color_work
        else:
            color = self.break_color
            text_color = self.text_color_break
        
        # Mettre à jour l'arc (360 degrés = 1.0)
        extent = int(360 * progress)
        self.canvas.itemconfig(self.arc, extent=extent, outline=color)
        
        # Mettre à jour le texte
        self.canvas.itemconfig(self.time_label, text=time_str, fill=text_color)
    
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
            self.arc = None
            self.time_label = None
    
    def is_visible(self) -> bool:
        """Retourne True si la fenêtre est visible"""
        if self.root is None:
            return False
        return self.root.winfo_viewable()
