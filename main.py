import pygame
import pygame_menu

pygame.init()
#TODO Mejor visualmente el menu de registro y principal
class LaberintoGame:
    def __init__(self):
        self.WIDTH, self.HEIGHT = 800, 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Escape del Laberinto")

        self.player_name = ""

        #Primero registro de jugador
        self.register_menu = RegisterMenu(self)
        # Primero crear el game loop y luego el menú, porque el menú
        # usa `app.game_loop` en sus callbacks.
        self.game_loop = GameLoop(self)
        self.menu = MainMenu(self) #pasamos la app al menu

    def run(self):
        "Inicia el menú principal"
        self.register_menu.show()

    def set_player_name(self, name):
        self.player_name = name
        print(f"Nombre del jugador establecido a: {self.player_name}")


class RegisterMenu:
    def __init__(self, app):
        self.app = app
        

        theme_registro = pygame_menu.Theme(
            background_color=(20, 20, 20),
            title_background_color=(0, 120, 200),
            title_font_shadow=True,
            widget_font=pygame_menu.font.FONT_MUNRO,
            widget_font_size=32,
            title_font_size=60,
            widget_padding=20,
            selection_color=(0, 200, 255),
        )

        self.menu = pygame_menu.Menu(
            "Registro de Jugador",
            app.WIDTH,
            app.HEIGHT,
            theme=theme_registro,
    )
  
        self.menu.add.label("Ingresa tu nombre para comenzar", font_size=28)
        self.menu.add.text_input(
            "Nombre: ",
            onchange=self.app.set_player_name,
            maxchar=12,
            
        )
        self.menu.add.button("Continuar ➤", self.validar_registro)


    def validar_registro(self):
        if self.app.player_name.strip() == "":
            print("Por favor, ingrese un nombre.")
        else:
            self.menu.disable()
            self.app.menu.show()

    def show(self):
        self.menu.mainloop(self.app.screen)

# Clase para el menú principal
class MainMenu:
    def __init__(self, app):
        self.app = app  #Referencia a la aplicación principal
        theme_main = pygame_menu.Theme(
            background_color=(15, 15, 45),
            title_background_color=(0, 100, 200),
            title_font_shadow=True,
            widget_font=pygame_menu.font.FONT_MUNRO,
            widget_font_size=32,
            title_font_size=65,
            widget_padding=18,
            selection_color=(255, 220, 0),
        )

        self.menu = pygame_menu.Menu(
            "Escape del Laberinto",
            app.WIDTH,
            app.HEIGHT,
            theme=theme_main,
        )

        #Botones del menú principal
        self.menu.add.label("Bienvenido, aventurero", font_size=30)
        self.menu.add.vertical_margin(20)

        self.menu.add.button("   Modo Escapa", self.app.game_loop.start_escape_mode)
        self.menu.add.button("   Modo Cazador", self.app.game_loop.start_hunter_mode)
        self.menu.add.button("   Configuración", self.app.game_loop.settings_mode)
        self.menu.add.button("   Puntuaciones", self.app.game_loop.top_scores_mode)

        self.menu.add.vertical_margin(30)
        self.menu.add.button("Salir", pygame_menu.events.EXIT)


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
    
    def settings_mode(self):
        print("Iniciando Modo Configuración...")
        print("Jugador:", self.app.player_name)
        self.run_game_loop(mode="Configuración")
    
    def top_scores_mode(self):
        print("Iniciando Modo Puntuaciones...")
        print("Jugador:", self.app.player_name)
        self.run_game_loop(mode="Puntuaciones")

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

#TODO clases pendientes de trabajar después
class Player:
    pass

class Enemy:
    pass

class Map:
    pass

class Hud:
    pass






#Ejecución principal
if __name__ == "__main__":
    app = LaberintoGame()
    app.run()