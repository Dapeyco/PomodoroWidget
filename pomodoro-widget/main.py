"""
Point d'entrée principal de PomodoroWidget
Orchestre l'application complète
"""

import sys
import threading
import queue
import tkinter as tk
from typing import Dict, Optional, Callable, Any

from config import load_config, save_config
from timer import PomodoroTimer, Phase
from overlay_line import LineOverlay
from overlay_circle import CircleOverlay
from overlay_counter import CounterOverlay
from systray import SystrayIcon
from settings_window import SettingsWindow


class PomodoroApp:
    """
    Application principale PomodoroWidget
    Gère la coordination entre tous les composants
    """
    
    def __init__(self):
        """Initialise l'application"""
        # Charger la configuration
        self.config = load_config()
        
        # Créer le timer
        self.timer = PomodoroTimer(
            work_minutes=self.config.get("work_minutes", 25),
            break_minutes=self.config.get("break_minutes", 5)
        )
        
        # Créer les overlays (ne pas créer les fenêtres tkinter encore)
        self.overlays = {
            "line": LineOverlay(position=self.config.get("line_position", "top")),
            "circle": CircleOverlay(),
            "counter": CounterOverlay()
        }
        
        # File d'événements pour la communication entre threads
        self.event_queue = queue.Queue()
        
        # Créer l'icône systray
        self.systray = SystrayIcon(self.timer, self.overlays, self.config)
        
        # Créer la fenêtre de paramètres
        self.settings_window = SettingsWindow(self.config, on_save=self._on_config_save)
        
        # Configurer les callbacks
        self._setup_callbacks()
        
        # État de l'application
        self.running = False
        self.root: Optional[tk.Tk] = None
        self.main_thread: Optional[threading.Thread] = None
    
    def _setup_callbacks(self) -> None:
        """Configure les callbacks entre les composants"""
        # Callback de tick du timer
        self.timer.on_tick = self._on_timer_tick
        
        # Callback de changement de phase
        self.timer.on_phase_change = self._on_phase_change
        
        # Callback pour la fenêtre de paramètres
        self.systray.on_settings = self._on_settings_requested
        self.systray.on_quit = self._on_quit
    
    def _on_timer_tick(self, progress: float, phase: Phase) -> None:
        """
        Callback appelé à chaque tick du timer
        Met à jour l'overlay actuel via la file d'événements
        """
        # Envoyer l'événement à la boucle principale tkinter
        self.event_queue.put(('update_overlay', {
            'progress': progress,
            'phase': phase
        }))
    
    def _on_phase_change(self, phase: Phase) -> None:
        """
        Callback appelé lors du changement de phase
        """
        print(f"Changement de phase: {phase.name}")
        
        # Afficher une notification (optionnel)
        if phase == Phase.WORK:
            print("Phase de travail démarrée")
        else:
            print("Phase de pause démarrée")
    
    def _on_config_save(self, new_config: Dict) -> None:
        """
        Callback appelé lors de l'enregistrement de la configuration
        """
        # Mettre à jour la configuration
        self.config.update(new_config)
        
        # Sauvegarder dans le fichier
        save_config(self.config)
        
        # Mettre à jour le timer avec les nouvelles durées
        self.timer.update_durations(
            work_minutes=self.config.get("work_minutes", 25),
            break_minutes=self.config.get("break_minutes", 5)
        )
        
        # Mettre à jour l'icône systray
        self.systray.update_config(self.config)
        
        # Mettre à jour la position de la ligne
        if "line" in self.overlays:
            self.overlays["line"].set_position(self.config.get("line_position", "top"))
        
        print("Configuration enregistrée:", self.config)
    
    def _on_settings_requested(self) -> None:
        """Callback appelé lorsque les paramètres sont demandés"""
        # Envoyer l'événement pour afficher la fenêtre de paramètres
        self.event_queue.put(('show_settings', {}))
    
    def _on_quit(self) -> None:
        """Callback appelé lors de la fermeture de l'application"""
        self.running = False
        
        # Arrêter le timer
        self.timer.stop()
        
        # Détruire tous les overlays
        for overlay in self.overlays.values():
            overlay.destroy()
        
        # Détruire la fenêtre de paramètres
        self.settings_window.destroy()
        
        # Arrêter l'icône systray
        self.systray.stop()
        
        print("Application arrêtée")
        
        # Quitter
        sys.exit(0)
    
    def _process_events(self) -> None:
        """Traite les événements de la file dans le thread principal tkinter"""
        try:
            while not self.event_queue.empty():
                event_type, data = self.event_queue.get_nowait()
                
                if event_type == 'update_overlay':
                    self._process_overlay_update(data)
                elif event_type == 'show_settings':
                    self.settings_window.show()
                elif event_type == 'create_overlay':
                    self._create_overlay_window(data)
        except queue.Empty:
            pass
        
        # Rappeler cette fonction après un court délai
        if self.root is not None:
            self.root.after(100, self._process_events)
    
    def _process_overlay_update(self, data: Dict) -> None:
        """Met à jour l'overlay avec les données reçues"""
        try:
            progress = data.get('progress', 0.0)
            phase = data.get('phase', Phase.WORK)
            display_mode = self.config.get("display_mode", "line")
            
            if display_mode in self.overlays:
                overlay = self.overlays[display_mode]
                time_str = self.timer.get_current_time_str()
                
                # Créer la fenêtre si elle n'existe pas encore
                if overlay.root is None:
                    overlay.create_window()
                
                # Mettre à jour l'overlay
                if display_mode == "line":
                    overlay.update(progress, phase)
                elif display_mode == "circle":
                    overlay.update(progress, phase, time_str)
                elif display_mode == "counter":
                    overlay.update(progress, phase, time_str)
        except Exception as e:
            print(f"Erreur lors de la mise à jour de l'overlay: {e}")
    
    def _create_overlay_window(self, data: Dict) -> None:
        """Crée la fenêtre de l'overlay si elle n'existe pas"""
        display_mode = data.get('mode', self.config.get("display_mode", "line"))
        if display_mode in self.overlays:
            overlay = self.overlays[display_mode]
            if overlay.root is None:
                overlay.create_window()
                overlay.show()
    
    def start(self) -> None:
        """Démarre l'application"""
        self.running = True
        
        # Démarrer l'icône systray
        self.systray.start()
        
        # Démarrer automatiquement si configuré
        if self.config.get("autostart", False):
            self.timer.start()
        
        # Créer la fenêtre tkinter principale (cachée)
        self._create_main_window()
        
        print("PomodoroWidget démarré")
    
    def _create_main_window(self) -> None:
        """Crée une fenêtre principale cachée pour gérer les events tkinter"""
        # Créer une fenêtre principale cachée
        self.root = tk.Tk()
        self.root.withdraw()
        
        # Démarrer le traitement des événements
        self._process_events()
        
        # Démarrer la boucle principale tkinter
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"Erreur dans la boucle tkinter: {e}")
        finally:
            self.running = False


def main():
    """Point d'entrée de l'application"""
    # Vérifier les dépendances
    try:
        import pystray
        import PIL
    except ImportError as e:
        print(f"Erreur: dépendance manquante - {e}")
        print("Installez les dépendances avec: pip install pystray pillow")
        sys.exit(1)
    
    # Créer et démarrer l'application
    app = PomodoroApp()
    
    try:
        app.start()
    except KeyboardInterrupt:
        print("Interruption par l'utilisateur")
        app._on_quit()
    except Exception as e:
        print(f"Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        app._on_quit()


if __name__ == "__main__":
    main()
