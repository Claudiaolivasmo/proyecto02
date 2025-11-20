import pygame
import pygame_menu

pygame.init()

class LaberintoGame:
    def __init__(self):
        self.WIDTH, self.HEIGHT = 800, 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Escape del Laberinto")

        self.player_name = ""
        # Primero crear el game loop y luego el menú, porque el menú
        # usa `app.game_loop` en sus callbacks.
        self.game_loop = GameLoop(self)
        self.menu = MainMenu(self) #pasamos la app al menu

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

        #botones
        self.menu.add.button("Modo Escapa", self.app.game_loop.start_escape_mode)
        self.menu.add.button("Modo Cazado", self.app.game_loop.start_hunter_mode)
        self.menu.add.button("Salir",pygame_menu.events.EXIT)
    def show(self):
        self.menu.mainloop(self.app.screen)

    def show_scores(self):
        # Aquí iría la lógica para mostrar las puntuaciones
        print("Mostrando puntuaciones...")

#game loop
class GameLoop:
    def __init__(self, app):
        self.app = app

    def start_escape_mode(self):
        print("Iniciando Modo Escapa...")
        print("Jugador:", self.app.player_name)
        self.run_game_loop(mode="escape")
        # Aquí iría la lógica del juego para el modo escapa

    def start_hunter_mode(self):
        print("Iniciando Modo Cazado...")
        print("Jugador:", self.app.player_name)
        self.run_game_loop(mode="Cazador")

    def run_game_loop(self, mode):
        #Aquí estará el juego Real. Por ahora un loop básico
        running = True
        clock = pygame.time.Clock()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                #Fondo negro por el momento
                self.app.screen.fill((0, 0, 0))

                #Texto temporal para distinguir modos
                font = pygame.font.Font(None, 40)
                text = font.render(f"Modo: {mode}", True, (255, 255, 255))
                self.app.screen.blit(text,(300,250))

                pygame.display.update()
                clock.tick(60)


#Ejecución principal
if __name__ == "__main__":
    app = LaberintoGame()
    app.run()