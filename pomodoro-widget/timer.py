"""
Logique du timer Pomodoro
Gère les états WORK/BREAK et les callbacks de progression
"""

import threading
import time
import sys
from enum import Enum, auto
from typing import Callable, Optional


class Phase(Enum):
    """États du timer Pomodoro"""
    WORK = auto()
    BREAK = auto()


class PomodoroTimer:
    """
    Timer Pomodoro avec gestion des phases WORK/BREAK
    """
    
    def __init__(self, work_minutes: int = 25, break_minutes: int = 5):
        """
        Initialise le timer
        
        Args:
            work_minutes: Durée de la phase de travail en minutes
            break_minutes: Durée de la phase de pause en minutes
        """
        self.work_minutes = work_minutes
        self.break_minutes = break_minutes
        
        # État courant
        self.current_phase: Optional[Phase] = None
        self.is_running = False
        self.is_paused = False
        
        # Temps restant en secondes
        self.remaining_seconds = 0
        self.total_seconds = 0
        
        # Callbacks
        self.on_tick: Optional[Callable[[float, Phase], None]] = None
        self.on_phase_change: Optional[Callable[[Phase], None]] = None
        self.on_complete: Optional[Callable[[], None]] = None
        
        # Thread du timer
        self._timer_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # Verrou pour la sécurité thread
        self._lock = threading.Lock()
    
    def start(self) -> None:
        """Démarre le timer depuis le début (phase WORK)"""
        with self._lock:
            if self.is_running and not self.is_paused:
                return  # Déjà en cours
            
            self._stop_event.clear()
            self.is_running = True
            self.is_paused = False
            self.current_phase = Phase.WORK
            self.total_seconds = self.work_minutes * 60
            self.remaining_seconds = self.total_seconds
            
        # Démarrer le thread
        if self._timer_thread is None or not self._timer_thread.is_alive():
            self._timer_thread = threading.Thread(target=self._run, daemon=True)
            self._timer_thread.start()
        
        # Notifier le changement de phase
        if self.on_phase_change:
            self.on_phase_change(self.current_phase)
    
    def pause(self) -> None:
        """Met le timer en pause"""
        with self._lock:
            if not self.is_running or self.is_paused:
                return
            self.is_paused = True
    
    def resume(self) -> None:
        """Reprend le timer après une pause"""
        with self._lock:
            if not self.is_running or not self.is_paused:
                return
            self.is_paused = False
    
    def skip_phase(self) -> None:
        """Passe à la phase suivante immédiatement"""
        with self._lock:
            if not self.is_running:
                return
            
            # Changer de phase
            if self.current_phase == Phase.WORK:
                self.current_phase = Phase.BREAK
                self.total_seconds = self.break_minutes * 60
            else:
                self.current_phase = Phase.WORK
                self.total_seconds = self.work_minutes * 60
            
            self.remaining_seconds = self.total_seconds
            
            # Notifier le changement de phase
            if self.on_phase_change:
                self.on_phase_change(self.current_phase)
    
    def stop(self) -> None:
        """Arrête complètement le timer"""
        with self._lock:
            self._stop_event.set()
            self.is_running = False
            self.is_paused = False
            self.current_phase = None
            self.remaining_seconds = 0
    
    def _run(self) -> None:
        """Boucle principale du timer (exécutée dans un thread séparé)"""
        while not self._stop_event.is_set():
            with self._lock:
                if not self.is_running:
                    break
                if self.is_paused:
                    time.sleep(0.1)
                    continue
                
                # Mettre à jour le temps restant
                self.remaining_seconds -= 1
                
                # Calculer la progression (0.0 à 1.0)
                if self.total_seconds > 0:
                    progress = 1.0 - (self.remaining_seconds / self.total_seconds)
                else:
                    progress = 1.0
                
                # Notifier le tick
                if self.on_tick and self.current_phase:
                    self.on_tick(progress, self.current_phase)
                
                # Vérifier si la phase est terminée
                if self.remaining_seconds <= 0:
                    self._phase_complete()
            
            time.sleep(1)
    
    def _phase_complete(self) -> None:
        """Gère la fin d'une phase"""
        # Jouer un son de notification (Windows uniquement)
        try:
            if sys.platform == 'win32':
                import winsound
                # Fréquence différente selon la phase
                if self.current_phase == Phase.WORK:
                    frequency = 1000  # Son aigu pour la fin du travail
                else:
                    frequency = 500   # Son grave pour la fin de la pause
                
                # Bip court
                winsound.Beep(frequency, 200)
        except:
            pass  # Ignorer les erreurs de son
        
        # Changer de phase
        if self.current_phase == Phase.WORK:
            self.current_phase = Phase.BREAK
            self.total_seconds = self.break_minutes * 60
        else:
            self.current_phase = Phase.WORK
            self.total_seconds = self.work_minutes * 60
        
        self.remaining_seconds = self.total_seconds
        
        # Notifier le changement de phase
        if self.on_phase_change:
            self.on_phase_change(self.current_phase)
        
        # Notifier la fin de cycle (optionnel)
        if self.on_complete:
            self.on_complete()
    
    def update_durations(self, work_minutes: int, break_minutes: int) -> None:
        """
        Met à jour les durées de travail et de pause
        Si le timer est en cours, cela prendra effet à la prochaine phase
        """
        with self._lock:
            self.work_minutes = work_minutes
            self.break_minutes = break_minutes
            
            # Si le timer est en cours, mettre à jour la durée actuelle
            if self.is_running and self.current_phase:
                if self.current_phase == Phase.WORK:
                    self.total_seconds = work_minutes * 60
                else:
                    self.total_seconds = break_minutes * 60
    
    def get_current_time_str(self) -> str:
        """Retourne le temps restant au format MM:SS"""
        with self._lock:
            if self.current_phase is None:
                return "00:00"
            
            minutes = self.remaining_seconds // 60
            seconds = self.remaining_seconds % 60
            return f"{minutes:02d}:{seconds:02d}"
    
    def get_progress(self) -> float:
        """Retourne la progression actuelle (0.0 à 1.0)"""
        with self._lock:
            if self.total_seconds == 0:
                return 1.0
            return 1.0 - (self.remaining_seconds / self.total_seconds)
    
    def get_phase(self) -> Optional[Phase]:
        """Retourne la phase actuelle"""
        with self._lock:
            return self.current_phase
    
    def is_active(self) -> bool:
        """Retourne True si le timer est en cours d'exécution"""
        with self._lock:
            return self.is_running and not self.is_paused
