import pygame
import pygame_menu

pygame.init()

class LaberintoGame:
    def __init__(self):
        self.WIDTH, self.HEIGHT = 800, 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Escape del Laberinto")

        self.player_name = ""
        self.menu = MainMenu(self) #pasamos la app al menu
        self.game_loop = GameLoop(self)

    def run(self):
        "Inicia el menú principal"
        self.menu.show()

    def set_player_name(self, name):
        self.player_name = name
        print(f"Nombre del jugador establecido a: {self.player_name}")



# Clase para el menú principal
class MainMenu:
    def __init__(self, app):
        self.app = app  #Referencia a la aplicación principal
        self.menu = pygame_menu.Menu(
            "Escapa del Laberinto",
            app.WIDTH,
            app.HEIGHT,
            theme=pygame_menu.themes.THEME_BLUE
        )

        #campo de texto
        self.menu.add.text_input("Nombre: ", onchange=self.app.set_player_name)

class GameLoop:
    pass  # Aquí iría la lógica del juego