import json
import os
from datetime import datetime

SCORES_PATH = os.path.join('data', 'assets', 'scores.json')


class User:
    """Representa un usuario del juego"""
    def __init__(self, name):
        self.name = name
        self.best_escape = 0
        self.best_hunter = 0
        self.escape_history = []
        self.hunter_history = []
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def add_score(self, score, mode):
        """Añade un puntaje al historial del modo especificado"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        score_entry = {"score": score, "timestamp": timestamp}
        
        if mode.lower() == "escape":
            self.escape_history.append(score_entry)
            if score > self.best_escape:
                self.best_escape = score
        elif mode.lower() == "cazador":
            self.hunter_history.append(score_entry)
            if score > self.best_hunter:
                self.best_hunter = score

    def update_best_score(self, score, mode):
        """Actualiza el mejor puntaje si el nuevo es mayor"""
        if mode.lower() == "escape":
            if score > self.best_escape:
                self.best_escape = score
                return True
        elif mode.lower() == "cazador":
            if score > self.best_hunter:
                self.best_hunter = score
                return True
        return False

    def to_dict(self):
        """Convierte el usuario a diccionario para serializar a JSON"""
        return {
            "name": self.name,
            "best_escape": self.best_escape,
            "best_hunter": self.best_hunter,
            "escape_history": self.escape_history,
            "hunter_history": self.hunter_history,
            "created_at": self.created_at
        }

    @staticmethod
    def from_dict(data):
        """Crea un usuario desde un diccionario JSON"""
        user = User(data["name"])
        user.best_escape = data.get("best_escape", 0)
        user.best_hunter = data.get("best_hunter", 0)
        user.escape_history = data.get("escape_history", [])
        user.hunter_history = data.get("hunter_history", [])
        user.created_at = data.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return user


class DataManager:
    """Gestor central de datos: usuarios, puntuaciones e historial"""
    
    def __init__(self, file_path=SCORES_PATH):
        self.file_path = file_path
        # Asegurar que el directorio existe
        self._ensure_dir()
        # Crear archivo si no existe
        if not os.path.exists(self.file_path):
            self._create_file()
        self.data = self.load()

    def _ensure_dir(self):
        """Crea el directorio si no existe"""
        dirpath = os.path.dirname(self.file_path)
        if dirpath and not os.path.exists(dirpath):
            os.makedirs(dirpath, exist_ok=True)

    def _create_file(self):
        """Crea el archivo JSON con estructura base"""
        base_structure = {
            "players": [],
            "scores": {
                "escape": [],
                "cazador": []
            }
        }
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(base_structure, f, indent=4)

    def load(self):
        """Carga datos desde el archivo JSON"""
        if not os.path.exists(self.file_path):
            self._create_file()
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError):
            # Si está corrupto, reescribir estructura base
            self._create_file()
            return {
                "players": [],
                "scores": {"escape": [], "cazador": []}
            }

    def save(self):
        """Guarda datos en el archivo JSON"""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    # ==================== MÉTODOS DE USUARIO ====================

    def user_exists(self, name):
        """Verifica si un usuario ya existe"""
        return any(p["name"].lower() == name.lower() for p in self.data["players"])

    def register_player(self, name):
        """Registra un nuevo jugador (si no existe)"""
        if self.user_exists(name):
            return False  # Usuario ya existe
        
        new_user = User(name)
        self.data["players"].append(new_user.to_dict())
        self.save()
        return True

    def login_player(self, name):
        """Recupera un jugador existente"""
        for player_data in self.data["players"]:
            if player_data["name"].lower() == name.lower():
                return User.from_dict(player_data)
        return None

    def get_player(self, name):
        """Obtiene los datos de un jugador"""
        for player_data in self.data["players"]:
            if player_data["name"].lower() == name.lower():
                return player_data
        return None

    def update_player(self, name, user_obj):
        """Actualiza los datos de un jugador en el JSON"""
        for i, player_data in enumerate(self.data["players"]):
            if player_data["name"].lower() == name.lower():
                self.data["players"][i] = user_obj.to_dict()
                self.save()
                return True
        return False

    # ==================== MÉTODOS DE PUNTUACIÓN ====================

    def add_score(self, name, score, mode):
        """Añade un puntaje a un jugador"""
        user = self.login_player(name)
        if not user:
            return False
        
        user.add_score(score, mode)
        self.update_player(name, user)
        self._update_top5(name, score, mode)
        return True

    def _update_top5(self, name, score, mode):
        """Actualiza la lista Top 5 del modo especificado"""
        mode = mode.lower()
        if mode not in self.data["scores"]:
            self.data["scores"][mode] = []
        
        # Crear entrada de puntuación
        score_entry = {
            "name": name,
            "score": score,
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Añadir a la lista
        self.data["scores"][mode].append(score_entry)
        
        # Ordenar de mayor a menor y mantener solo Top 5
        self.data["scores"][mode] = sorted(
            self.data["scores"][mode],
            key=lambda s: s["score"],
            reverse=True
        )[:5]
        
        self.save()

    def get_top5(self, mode):
        """Obtiene el Top 5 de un modo"""
        mode = mode.lower()
        if mode not in self.data["scores"]:
            return []
        return self.data["scores"][mode]

    def get_history(self, name, mode):
        """Obtiene el historial de puntajes de un jugador en un modo"""
        user = self.login_player(name)
        if not user:
            return []
        
        if mode.lower() == "escape":
            return user.escape_history
        elif mode.lower() == "cazador":
            return user.hunter_history
        return []

    def get_all_players(self):
        """Obtiene lista de todos los jugadores"""
        return self.data["players"]
    
#