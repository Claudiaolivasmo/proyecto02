import json
import os

SCORES_PATH = os.path.join('data','assets','scores.json')

#TODO terminar todos los metodos de este archivo para manejar usuarios y puntuaciones
class User:
    def __init__(self, name):
        self.name = name
        self.best_escape = 0
        self.best_hunter = 0
        self.escape_history = []
        self.hunter_history = []

    def add_score(self, score, mode):
        pass

    def update_best_score(self, score, mode):
        pass


class User_manager:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.users = []

    def load_users(self):
        pass

    def save_users(self):
        pass

    def user_exists(self, name):
        pass

    def register_user(self, name):
        pass

    def login_user(self, name):
        pass

    def get_user(self, name):
        pass



class ScoreManager:
    def __init__(self,user_manager):
        self.user_manager = user_manager

    def add_score(self,name, score, mode):
        pass

    def get_top5(self, mode):
        pass
    def sort_scores(self, scores, mode):
        pass
    def get_history(self, name, mode):
        pass


class DataManager:
    def __init__(self,file_path):
        self.file_path = SCORES_PATH

    def load(self):
        pass
    def save(self,data):
        pass