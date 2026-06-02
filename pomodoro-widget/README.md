# PomodoroWidget

Une application desktop légère pour Windows qui affiche un timer Pomodoro sous forme d'overlay toujours visible.

## Fonctionnalités

- **Mode Ligne** : Une fine barre colorée sur toute la largeur de l'écran, toujours au premier plan
- **Mode Cercle** : Une fenêtre ronde flottante avec arc animé
- **Mode Compteur** : Une mini-fenêtre avec affichage numérique MM:SS
- **Icône Systray** : Contrôle complet via menu contextuel
- **Configuration persistante** : Sauvegarde des paramètres dans `%APPDATA%\PomodoroWidget\config.json`

## Installation

### Prérequis
- Python 3.11 ou supérieur
- Windows (pour les fonctionnalités avancées comme le forçage au-dessus de la taskbar)

### Installation des dépendances

```bash
pip install pystray pillow
```

### Lancement

```bash
python main.py
```

## Utilisation

1. Lancez l'application avec `python main.py`
2. Une icône apparaît dans la barre des tâches (systray)
3. Clic droit sur l'icône pour accéder au menu:
   - **▶ Démarrer** : Lance le timer Pomodoro
   - **⏸ Pause** : Met en pause / reprend le timer
   - **⏭ Passer la phase** : Passe à la phase suivante immédiatement
   - **Mode** : Choisissez entre Ligne, Cercle ou Compteur
   - **Position** : Haut ou Bas (pour le mode Ligne)
   - **⚙ Paramètres** : Ouvre la fenêtre de configuration
   - **✕ Quitter** : Ferme l'application

### Configuration

Dans la fenêtre de paramètres, vous pouvez:
- Modifier les durées de travail et de pause (en minutes)
- Utiliser les présets **25/5** (Pomodoro classique) ou **90/15** (deep work)
- Choisir le mode d'affichage par défaut
- Configurer la position de la barre (haut ou bas)
- Activer le démarrage automatique

## Structure du projet

```
pomodoro-widget/
├── main.py              # Point d'entrée principal
├── overlay_line.py      # Overlay en forme de ligne (barre pleine largeur)
├── overlay_circle.py    # Overlay en forme de cercle animé
├── overlay_counter.py   # Overlay avec compteur numérique
├── systray.py           # Icône systray et menu contextuel
├── timer.py             # Logique du timer Pomodoro
├── config.py            # Configuration persistante
├── settings_window.py   # Fenêtre de configuration
└── README.md            # Documentation
```

## Personnalisation

Vous pouvez modifier les fichiers de configuration directement dans `%APPDATA%\PomodoroWidget\config.json`:

```json
{
  "work_minutes": 25,
  "break_minutes": 5,
  "display_mode": "line",
  "line_position": "top",
  "autostart": false
}
```

## Génération de l'exécutable (optionnel)

Pour créer un fichier `.exe` standalone:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name PomodoroWidget main.py
```

Le fichier `PomodoroWidget.exe` sera généré dans le dossier `dist/`.

## Technologie

- **Langage** : Python 3.11+
- **GUI** : tkinter (inclus dans Python)
- **Systray** : pystray + Pillow
- **Packaging** : pyinstaller (optionnel)

## Contributeurs

- Dapeyco

## Licence

Ce projet est sous licence MIT.
