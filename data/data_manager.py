import json
from datetime import datetime
import os

SCORES_PATH = os.path.join('data','assets','scores.json')


#clase jugador
class Player:
    def __init__(self, name:str):
        self.name = name
    
    def to_dict(self):
        return {"name": self.name}
    

#clase Score (puntaje)


class Score:
    def __init__(self,name:str, points:int, date:str):
        self.name = name
        self.points = points
        self.date = date
        
    def to_dict(self):
        return {
            "name": self.name,
            "points": self.points,
            "date": self.date
        }
    
#TODO terminar métodos para manejar puntuaciones y jugadores de la clase DataManager
#clase principal para manejar datos
class DataManager:
    def __init__(self,file_path=SCORES_PATH):
        self.file_path = file_path
        

        #si no existe el archivo, crearlo
        if not os.path.exists(self.file_path):
            self._create_file()

        self.data = self.load()

    #crear archivo si no existe
    def create_file(self):
        base_structure = {     #estructura del del archivo json si no existe ningún dato
            "players": [],
            "scores": {
                "escape": [],
                "hunter": []
            }

        }
        with open(self.file_path, 'w') as f:
            json.dump(base_structure, f, indent=4)

    def save(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.data, f, indent=4)

    
    #registro de jugador
    def register_player(self, name:str):
        exists = any(p["name"] == name for p in self.data["players"])
        if not exists:
            new_player = Player(name)
            self.data["players"].append(new_player.to_dict())
            self.save()


    #Agregar puntajes por modo de juego
    def add_score(self, name:str, points:int, mode:str):
        date = datetime.now().strftime("%Y-%m-%d")
        new_score = Score(name, points, date)
        self.data["scores"][mode] == sorted(
            self.data["scores"][mode],
            key=lambda s: s["points"],
            reverse=True
        )

        #Mantener solo el top 5
        self.data["scores"][mode] = self.data["scores"][mode][:5]
        self.save()


        #Obtene el Top de un modo de juego
    def get_top (self, mode:str):
            return self.data["scores"][mode]
    
#TODO PROBAR LAS FUNCIONES DE ESTA CLASE