import json
import os
from datetime import datetime

SCORES_PATH = os.path.join('proyecto02', 'data', 'scores.json')


class User:
    """Representa un usuario del juego"""
    def __init__(self, name):
        self.nombre = name
        self.mejor_escapa = 0
        self.mejor_cazador = 0
        self.historial_escapa = []
        self.historial_cazador = []

    def add_score(self, score, mode):
        """Añade un puntaje al historial del modo especificado"""
        if mode.lower() == "escape":
            self.historial_escapa.append(score)
            if score > self.mejor_escapa:
                self.mejor_escapa = score
        elif mode.lower() == "cazador":
            self.historial_cazador.append(score)
            if score > self.mejor_cazador:
                self.mejor_cazador = score

    def update_best_score(self, score, mode):
        """Actualiza el mejor puntaje si el nuevo es mayor"""
        if mode.lower() == "escape":
            if score > self.mejor_escapa:
                self.mejor_escapa = score
                return True
        elif mode.lower() == "cazador":
            if score > self.mejor_cazador:
                self.mejor_cazador = score
                return True
        return False

    def to_dict(self):
        """Convierte el usuario a diccionario para serializar a JSON"""
        return {
            "nombre": self.nombre,
            "mejor_escapa": self.mejor_escapa,
            "mejor_cazador": self.mejor_cazador,
            "historial_escapa": self.historial_escapa,
            "historial_cazador": self.historial_cazador
        }

    @staticmethod
    def from_dict(data):
        """Crea un usuario desde un diccionario JSON"""
        user = User(data["nombre"])
        user.mejor_escapa = data.get("mejor_escapa", 0)
        user.mejor_cazador = data.get("mejor_cazador", 0)
        user.historial_escapa = data.get("historial_escapa", [])
        user.historial_cazador = data.get("historial_cazador", [])
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
            "usuarios": []
        }
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(base_structure, f, indent=4)

    def load(self):
        if not os.path.exists(self.file_path):
            self._create_file()

        with open(self.file_path, 'r', encoding='utf-8') as f:
            return json.load(f)


        # Normalizar distintas estructuras de JSON a la forma interna {'usuarios': [ ... ]}
        def normalize(data):
            # Caso ya normal
            if isinstance(data, dict):
                # Si ya tiene 'usuarios' y es lista
                if 'usuarios' in data and isinstance(data['usuarios'], list):
                    return data
                # Si tiene 'players' (inglés) como lista
                if 'players' in data and isinstance(data['players'], list):
                    return {'usuarios': data['players']}
                # Si el JSON es una lista de usuarios (archivo guardado como lista)
                if isinstance(data.get('data', None), list):
                    return {'usuarios': data['data']}
                # Si el archivo contiene usuarios indexados por nombre: {"juan": {...}, ...}
                if all(isinstance(v, dict) for v in data.values()):
                    # Construir lista si los diccionarios parecen usuarios (tienen 'nombre' o 'mejor_escapa')
                    sample = next(iter(data.values()))
                    if 'nombre' in sample or 'mejor_escapa' in sample:
                        usuarios = []
                        for v in data.values():
                            usuarios.append(v)
                        return {'usuarios': usuarios}
                # Si tiene 'scores' con top lists, no podemos reconstruir usuarios completos
                if 'scores' in data and isinstance(data['scores'], dict):
                    # Mantener scores, pero ensure key usuarios exists
                    data.setdefault('usuarios', [])
                    return data
                # Si el archivo es una lista en la raíz
            if isinstance(data, list):
                return {'usuarios': data}
            # Por defecto devolver estructura vacía
            return {'usuarios': []}

        normalized = normalize(loaded)
        # Escribir de vuelta la estructura normalizada para evitar futuros errores
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(normalized, f, indent=4, ensure_ascii=False)
        except Exception:
            pass
        return normalized

    def save(self):
        """Guarda datos en el archivo JSON"""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def reload(self):
        """Recarga los datos desde el archivo JSON (útil después de cambios externos)"""
        self.data = self.load()

    # ==================== MÉTODOS DE USUARIO ====================

    def user_exists(self, name):
        """Verifica si un usuario ya existe"""
        usuarios = self.data.get("usuarios", [])
        return any(p.get("nombre", "").lower() == name.lower() for p in usuarios)

    def register_player(self, name):
        """Registra un nuevo jugador (si no existe)"""
        if self.user_exists(name):
            return False  # Usuario ya existe
        
        new_user = User(name)
        self.data.setdefault("usuarios", []).append(new_user.to_dict())
        self.save()
        return True

    def login_player(self, name):
        """Recupera un jugador existente"""
        for player_data in self.data.get("usuarios", []):
            if player_data.get("nombre", "").lower() == name.lower():
                return User.from_dict(player_data)
        return None

    def get_player(self, name):
        """Obtiene los datos de un jugador"""
        for player_data in self.data.get("usuarios", []):
            if player_data.get("nombre", "").lower() == name.lower():
                return player_data
        return None

    def update_player(self, name, user_obj):
        """Actualiza los datos de un jugador en el JSON"""
        usuarios = self.data.get("usuarios", [])
        for i, player_data in enumerate(usuarios):
            if player_data.get("nombre", "").lower() == name.lower():
                usuarios[i] = user_obj.to_dict()
                self.data["usuarios"] = usuarios
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
        return True

    def get_top5(self, mode):
        """Obtiene el Top 5 de un modo ordenado por puntuación"""
        mode = mode.lower()
        top_scores = []
        
        for player in self.data.get("usuarios", []):
            if mode == "escape":
                best = player.get("mejor_escapa", 0)
            elif mode == "cazador":
                best = player.get("mejor_cazador", 0)
            else:
                best = 0
            
            if best > 0:
                top_scores.append({
                    "nombre": player["nombre"],
                    "score": best
                })
        
        # Ordenar de mayor a menor y retornar top 5
        top_scores = sorted(top_scores, key=lambda s: s["score"], reverse=True)
        return top_scores[:5]

    def get_history(self, name, mode):
        """Obtiene el historial de puntajes de un jugador en un modo"""
        user = self.login_player(name)
        if not user:
            return []
        
        if mode.lower() == "escape":
            return user.historial_escapa
        elif mode.lower() == "cazador":
            return user.historial_cazador
        return []

    def get_all_players(self):
        """Obtiene lista de todos los jugadores"""
        return self.data.get("usuarios", [])
    
if __name__ == "__main__":
    # Ejecución de diagnóstico local — no importar como paquete
    dm = DataManager()
    import json
    print("Ruta usada:", dm.file_path)
    print("Contenido actual del JSON:")
    print(json.dumps(dm.data, indent=2, ensure_ascii=False))
