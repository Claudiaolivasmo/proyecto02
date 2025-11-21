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