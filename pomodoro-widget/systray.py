"""
Icône Systray pour PomodoroWidget
Gère l'icône dynamique et le menu contextuel
"""

import sys
from typing import Optional, Callable, Dict
from enum import Enum

import pystray
from PIL import Image, ImageDraw

from timer import PomodoroTimer, Phase


class SystrayIcon:
    """
    Icône systray avec menu contextuel pour contrôler le timer Pomodoro
    """
    
    def __init__(self, timer: PomodoroTimer, overlays: Dict[str, any], config: Dict):
        """
        Initialise l'icône systray
        
        Args:
            timer: Instance du timer Pomodoro
            overlays: Dictionnaire des overlays disponibles
            config: Configuration actuelle
        """
        self.timer = timer
        self.overlays = overlays
        self.config = config
        
        # État
        self.is_running = False
        self.current_display_mode = config.get("display_mode", "line")
        self.current_line_position = config.get("line_position", "top")
        
        # Callbacks pour les actions
        self.on_settings: Optional[Callable[[], None]] = None
        self.on_quit: Optional[Callable[[], None]] = None
        
        # Icône
        self.icon: Optional[pystray.Icon] = None
        
        # Créer l'icône initiale
        self._create_icon()
    
    def _create_icon(self, progress: float = 0.0, phase: Optional[Phase] = None) -> Image.Image:
        """
        Crée une icône 64x64 avec remplissage progressif
        
        Args:
            progress: Progression de 0.0 à 1.0
            phase: Phase actuelle (WORK ou BREAK)
        
        Returns:
            Image PIL de l'icône
        """
        size = 64
        icon = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        dc = ImageDraw.Draw(icon)
        
        # Couleur selon la phase
        if phase == Phase.WORK:
            fill_color = (255, 0, 0)  # Rouge
            bg_color = (0, 200, 83)  # Vert
        else:
            fill_color = (0, 200, 83)  # Vert
            bg_color = (255, 0, 0)  # Rouge
        
        # Dessiner le fond (carré)
        dc.rectangle([(0, 0), (size, size)], fill=bg_color)
        
        # Dessiner la progression (remplissage de gauche à droite)
        fill_width = int(size * progress)
        if fill_width > 0:
            dc.rectangle([(0, 0), (fill_width, size)], fill=fill_color)
        
        # Ajouter une bordure pour la visibilité
        dc.rectangle([(0, 0), (size - 1, size - 1)], outline=(255, 255, 255), width=1)
        
        return icon
    
    def _update_icon_image(self, progress: float, phase: Optional[Phase]) -> None:
        """
        Met à jour l'image de l'icône
        Doit être appelé depuis le thread principal
        """
        if self.icon is None:
            return
        
        try:
            icon_image = self._create_icon(progress, phase)
            self.icon.icon = icon_image
        except Exception as e:
            print(f"Erreur lors de la mise à jour de l'icône: {e}")
    

    
    def start(self) -> None:
        """Démarre l'icône systray"""
        if self.icon is not None:
            return
        
        # Créer l'icône initiale
        initial_icon = self._create_icon(0.0, None)
        
        # Créer le menu
        menu = self._create_menu()
        
        # Démarrer l'icône
        self.icon = pystray.Icon("PomodoroWidget", initial_icon, "Pomodoro Widget", menu)
        
        # Démarrer la boucle principale de pystray
        # Note: On utilise run_detached pour ne pas bloquer
        # La mise à jour de l'icône est désactivée pour éviter les problèmes de thread
        # (pystray a des limitations avec les mises à jour fréquentes depuis des threads)
        self.icon.run_detached()
    
    def _create_menu(self) -> pystray.Menu:
        """Crée le menu contextuel"""
        return pystray.Menu(
            pystray.MenuItem(
                "▶ Démarrer",
                lambda: self._on_start()
            ),
            pystray.MenuItem(
                "⏸ Pause",
                lambda: self._on_pause()
            ),
            pystray.MenuItem(
                "⏭ Passer la phase",
                lambda: self._on_skip()
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Mode : Ligne",
                lambda: self._set_display_mode("line"),
                checked=lambda item: self.current_display_mode == "line"
            ),
            pystray.MenuItem(
                "Mode : Cercle",
                lambda: self._set_display_mode("circle"),
                checked=lambda item: self.current_display_mode == "circle"
            ),
            pystray.MenuItem(
                "Mode : Compteur",
                lambda: self._set_display_mode("counter"),
                checked=lambda item: self.current_display_mode == "counter"
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Position : Haut",
                lambda: self._set_line_position("top"),
                checked=lambda item: self.current_line_position == "top",
                visible=lambda item: self.current_display_mode == "line"
            ),
            pystray.MenuItem(
                "Position : Bas",
                lambda: self._set_line_position("bottom"),
                checked=lambda item: self.current_line_position == "bottom",
                visible=lambda item: self.current_display_mode == "line"
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "⚙ Paramètres",
                lambda: self._on_settings()
            ),
            pystray.MenuItem(
                "✕ Quitter",
                lambda: self._on_quit()
            )
        )
    
    def _on_start(self) -> None:
        """Démarre le timer"""
        if not self.timer.is_active():
            self.timer.start()
            self._show_current_overlay()
    
    def _on_pause(self) -> None:
        """Met le timer en pause ou le reprend"""
        if self.timer.is_active():
            self.timer.pause()
        else:
            self.timer.resume()
    
    def _on_skip(self) -> None:
        """Passe à la phase suivante"""
        self.timer.skip_phase()
    
    def _set_display_mode(self, mode: str) -> None:
        """Change le mode d'affichage"""
        self.current_display_mode = mode
        self.config["display_mode"] = mode
        
        # Masquer l'overlay actuel
        self._hide_all_overlays()
        
        # Afficher le nouvel overlay si le timer est actif
        if self.timer.is_active():
            self._show_current_overlay()
    
    def _set_line_position(self, position: str) -> None:
        """Change la position de la ligne"""
        self.current_line_position = position
        self.config["line_position"] = position
        
        # Mettre à jour l'overlay ligne
        if "line" in self.overlays:
            self.overlays["line"].set_position(position)
    
    def _show_current_overlay(self) -> None:
        """Affiche l'overlay correspondant au mode actuel"""
        if self.current_display_mode in self.overlays:
            overlay = self.overlays[self.current_display_mode]
            if not overlay.is_visible():
                overlay.show()
    
    def _hide_all_overlays(self) -> None:
        """Masque tous les overlays"""
        for overlay in self.overlays.values():
            overlay.hide()
    
    def _on_settings(self) -> None:
        """Ouvre la fenêtre de paramètres"""
        if self.on_settings:
            self.on_settings()
    
    def _on_quit(self) -> None:
        """Quitte l'application"""
        self._stop_update.set()
        
        # Arrêter le timer
        self.timer.stop()
        
        # Détruire tous les overlays
        for overlay in self.overlays.values():
            overlay.destroy()
        
        # Arrêter l'icône
        if self.icon is not None:
            self.icon.stop()
        
        if self.on_quit:
            self.on_quit()
    
    def stop(self) -> None:
        """Arrête l'icône systray"""
        if self.icon is not None:
            self.icon.stop()
            self.icon = None
    
    def update_config(self, config: Dict) -> None:
        """Met à jour la configuration"""
        self.config = config
        self.current_display_mode = config.get("display_mode", "line")
        self.current_line_position = config.get("line_position", "top")
