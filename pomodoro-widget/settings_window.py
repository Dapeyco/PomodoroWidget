"""
Fenêtre de configuration pour PomodoroWidget
Fenêtre tkinter standard pour modifier les paramètres
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Dict


class SettingsWindow:
    """
    Fenêtre de configuration pour modifier les paramètres du Pomodoro
    """
    
    def __init__(self, config: Dict, on_save: Optional[Callable[[Dict], None]] = None):
        """
        Initialise la fenêtre de configuration
        
        Args:
            config: Configuration actuelle
            on_save: Callback appelé lors de l'enregistrement
        """
        self.config = config.copy()
        self.on_save = on_save
        
        # Fenêtre principale
        self.root: Optional[tk.Tk] = None
        
        # Variables tkinter
        self.work_minutes_var: Optional[tk.StringVar] = None
        self.break_minutes_var: Optional[tk.StringVar] = None
        self.display_mode_var: Optional[tk.StringVar] = None
        self.line_position_var: Optional[tk.StringVar] = None
        self.autostart_var: Optional[tk.BooleanVar] = None
    
    def create_window(self) -> None:
        """Crée et affiche la fenêtre de configuration"""
        if self.root is not None:
            self.root.deiconify()
            return
        
        self.root = tk.Tk()
        self.root.title("Paramètres - Pomodoro Widget")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Initialiser les variables
        self.work_minutes_var = tk.StringVar(value=str(self.config.get("work_minutes", 25)))
        self.break_minutes_var = tk.StringVar(value=str(self.config.get("break_minutes", 5)))
        self.display_mode_var = tk.StringVar(value=self.config.get("display_mode", "line"))
        self.line_position_var = tk.StringVar(value=self.config.get("line_position", "top"))
        self.autostart_var = tk.BooleanVar(value=self.config.get("autostart", False))
        
        # Créer l'interface
        self._create_widgets()
        
        # Protocole de fermeture
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _create_widgets(self) -> None:
        """Crée tous les widgets de la fenêtre"""
        if self.root is None:
            return
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Section Durées
        duration_frame = ttk.LabelFrame(main_frame, text="Durées (minutes)", padding="10")
        duration_frame.pack(fill="x", pady=5)
        
        # Durée de travail
        work_frame = ttk.Frame(duration_frame)
        work_frame.pack(fill="x", pady=2)
        
        ttk.Label(work_frame, text="Travail:").pack(side="left")
        work_entry = ttk.Entry(work_frame, textvariable=self.work_minutes_var, width=5)
        work_entry.pack(side="left", padx=5)
        
        # Durée de pause
        break_frame = ttk.Frame(duration_frame)
        break_frame.pack(fill="x", pady=2)
        
        ttk.Label(break_frame, text="Pause:").pack(side="left")
        break_entry = ttk.Entry(break_frame, textvariable=self.break_minutes_var, width=5)
        break_entry.pack(side="left", padx=5)
        
        # Boutons présets
        presets_frame = ttk.Frame(duration_frame)
        presets_frame.pack(fill="x", pady=5)
        
        ttk.Button(presets_frame, text="25/5", command=lambda: self._set_preset(25, 5)).pack(side="left", padx=2)
        ttk.Button(presets_frame, text="90/15", command=lambda: self._set_preset(90, 15)).pack(side="left", padx=2)
        
        # Section Mode d'affichage
        display_frame = ttk.LabelFrame(main_frame, text="Mode d'affichage", padding="10")
        display_frame.pack(fill="x", pady=5)
        
        # Choix du mode
        mode_frame = ttk.Frame(display_frame)
        mode_frame.pack(fill="x")
        
        ttk.Radiobutton(mode_frame, text="Ligne", variable=self.display_mode_var, value="line").pack(side="left", padx=5)
        ttk.Radiobutton(mode_frame, text="Cercle", variable=self.display_mode_var, value="circle").pack(side="left", padx=5)
        ttk.Radiobutton(mode_frame, text="Compteur", variable=self.display_mode_var, value="counter").pack(side="left", padx=5)
        
        # Section Position de la ligne (visible seulement si mode ligne)
        position_frame = ttk.LabelFrame(main_frame, text="Position de la ligne", padding="10")
        position_frame.pack(fill="x", pady=5)
        
        pos_frame = ttk.Frame(position_frame)
        pos_frame.pack(fill="x")
        
        ttk.Radiobutton(pos_frame, text="Haut", variable=self.line_position_var, value="top").pack(side="left", padx=5)
        ttk.Radiobutton(pos_frame, text="Bas", variable=self.line_position_var, value="bottom").pack(side="left", padx=5)
        
        # Option de démarrage automatique
        autostart_frame = ttk.Frame(main_frame)
        autostart_frame.pack(fill="x", pady=5)
        
        ttk.Checkbutton(autostart_frame, text="Démarrer automatiquement au lancement",
                       variable=self.autostart_var).pack(side="left")
        
        # Boutons de validation
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=10)
        
        ttk.Button(button_frame, text="Enregistrer", command=self._on_save).pack(side="right", padx=5)
        ttk.Button(button_frame, text="Annuler", command=self._on_close).pack(side="right", padx=5)
    
    def _set_preset(self, work: int, break_min: int) -> None:
        """Applique un preset de durée"""
        self.work_minutes_var.set(str(work))
        self.break_minutes_var.set(str(break_min))
    
    def _on_save(self) -> None:
        """Enregistre la configuration"""
        try:
            # Valider et récupérer les valeurs
            work_minutes = int(self.work_minutes_var.get())
            break_minutes = int(self.break_minutes_var.get())
            
            if work_minutes <= 0 or break_minutes <= 0:
                tk.messagebox.showerror("Erreur", "Les durées doivent être supérieures à 0")
                return
            
            # Mettre à jour la configuration
            self.config["work_minutes"] = work_minutes
            self.config["break_minutes"] = break_minutes
            self.config["display_mode"] = self.display_mode_var.get()
            self.config["line_position"] = self.line_position_var.get()
            self.config["autostart"] = self.autostart_var.get()
            
            # Appeler le callback
            if self.on_save:
                self.on_save(self.config)
            
            # Fermer la fenêtre
            self._on_close()
            
        except ValueError:
            tk.messagebox.showerror("Erreur", "Veuillez entrer des nombres valides")
    
    def _on_close(self) -> None:
        """Fermer la fenêtre"""
        if self.root is not None:
            self.root.withdraw()
    
    def show(self) -> None:
        """Affiche la fenêtre"""
        if self.root is None:
            self.create_window()
        else:
            self.root.deiconify()
            self.root.lift()
    
    def hide(self) -> None:
        """Masque la fenêtre"""
        if self.root is not None:
            self.root.withdraw()
    
    def destroy(self) -> None:
        """Détruit la fenêtre"""
        if self.root is not None:
            self.root.destroy()
            self.root = None
    
    def update_config(self, config: Dict) -> None:
        """Met à jour la configuration affichée"""
        self.config = config.copy()
        
        if self.work_minutes_var:
            self.work_minutes_var.set(str(config.get("work_minutes", 25)))
        if self.break_minutes_var:
            self.break_minutes_var.set(str(config.get("break_minutes", 5)))
        if self.display_mode_var:
            self.display_mode_var.set(config.get("display_mode", "line"))
        if self.line_position_var:
            self.line_position_var.set(config.get("line_position", "top"))
        if self.autostart_var:
            self.autostart_var.set(config.get("autostart", False))
