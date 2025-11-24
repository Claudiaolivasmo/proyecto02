import pygame
import pygame_menu
from data.data_manager import DataManager


pygame.init()
#TODO Mejor visualmente el menu de registro y principal
class LaberintoGame:
    def __init__(self):
        self.WIDTH, self.HEIGHT = 800, 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Escape del Laberinto")

        self.player_name = ""
        self.data_manager = DataManager()  # Gestor de datos

        #Primero registro de jugador
        self.register_menu = RegisterMenu(self)
        # Primero crear el game loop y luego el menú, porque el menú
        # usa `app.game_loop` en sus callbacks.
        self.game_loop = GameLoop(self)
        self.difficulty_menu_escape = DifficultyMenuEscape(self, self.game_loop)
        self.difficulty_menu_hunter = DifficultyMenuHunter(self, self.game_loop)
        self.menu = MainMenu(self) #pasamos la app al menu

    def run(self):
        "Inicia el menú de registro"
        self.register_menu.show()

    def set_player_name(self, name):
        self.player_name = name

    def show_difficulty_escape(self):
        self.difficulty_menu_escape.show()

    def show_difficulty_hunter(self):
        self.difficulty_menu_hunter.show()


class RegisterMenu:
    def __init__(self, app):
        self.app = app
        self.input_name = ""
        self.error_msg = ""
        
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
            "Acceso al Juego",
            app.WIDTH,
            app.HEIGHT,
            theme=theme_registro,
        )
  
        self.menu.add.label("Bienvenido a Escape del Laberinto", font_size=28)
        self.menu.add.vertical_margin(10)
        
        # Mensaje de error/éxito dinámico
        self.error_label = self.menu.add.label("", font_size=18, font_color=(255, 100, 100))
        
        self.menu.add.vertical_margin(10)
        self.menu.add.label("Ingresa tu nombre:", font_size=22)
        
        # Input de nombre
        self.name_widget = self.menu.add.text_input(
            "Nombre: ",
            onchange=self._update_name,
            maxchar=15,
        )
        
        self.menu.add.vertical_margin(15)
        self.menu.add.button("✓ REGISTRARSE", self._register)
        self.menu.add.button("↳ INICIAR SESIÓN", self._login)

    def _update_name(self, value):
        """Actualiza el nombre mientras se escribe"""
        self.input_name = value.strip()

    def _register(self):
        """Registra un nuevo jugador"""
        if not self.input_name:
            self._show_error("Por favor ingresa un nombre.")
            return
        
        if len(self.input_name) < 2:
            self._show_error("El nombre debe tener al menos 2 caracteres.")
            return
        
        if not self.input_name.isalpha():
            self._show_error("El nombre solo puede contener letras.")
            return
        
        # Registrar en el sistema
        if self.app.data_manager.register_player(self.input_name):
            self.app.player_name = self.input_name
            self._show_success(f"¡Bienvenido, {self.input_name}!")
            pygame.time.delay(800)
            self.menu.disable()
            self.app.menu.show()
        else:
            self._show_error("Este nombre ya existe. Intenta otro.")

    def _login(self):
        """Inicia sesión con un jugador existente"""
        if not self.input_name:
            self._show_error("Por favor ingresa un nombre.")
            return
        
        # Buscar jugador
        user = self.app.data_manager.login_player(self.input_name)
        if user:
            self.app.player_name = self.input_name
            self._show_success(f"¡Bienvenido de vuelta, {self.input_name}!")
            pygame.time.delay(800)
            self.menu.disable()
            self.app.menu.show()
        else:
            self._show_error("Jugador no encontrado. Regístrate primero.")

    def _show_error(self, msg):
        """Muestra mensaje de error"""
        self.error_msg = msg
        try:
            self.error_label.set_title(msg)
        except Exception:
            pass

    def _show_success(self, msg):
        """Muestra mensaje de éxito"""
        self.error_msg = msg
        try:
            self.error_label.set_title(msg)
        except Exception:
            pass

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
        self.menu.add.label(lambda: f"Jugador: {self.app.player_name}", font_size=24, font_color=(100, 200, 255))
        self.menu.add.vertical_margin(20)

        self.menu.add.button("   Modo Escapa", self.app.show_difficulty_escape)
        self.menu.add.button("   Modo Cazador", self.app.show_difficulty_hunter)
        self.menu.add.button("   Ver Puntuaciones", self.show_top_scores)
        self.menu.add.button("   Configuración", self.app.game_loop.settings_mode)

        self.menu.add.vertical_margin(30)
        self.menu.add.button("Salir", pygame_menu.events.EXIT)


    def show(self):
        self.menu.mainloop(self.app.screen)

    def show_scores(self):
        # Aquí iría la lógica para mostrar las puntuaciones
        print("Mostrando puntuaciones...")

    def show_top_scores(self):
        """Muestra un menú con el Top 5 de cada modo"""
        top_escape = self.app.data_manager.get_top5("escape")
        top_hunter = self.app.data_manager.get_top5("cazador")
        
        theme_scores = pygame_menu.Theme(
            background_color=(30, 30, 30),
            title_background_color=(100, 100, 200),
            title_font_shadow=True,
            widget_font=pygame_menu.font.FONT_MUNRO,
            widget_font_size=20,
            title_font_size=50,
            widget_padding=10,
            selection_color=(200, 200, 0),
        )
        
        scores_menu = pygame_menu.Menu(
            "Puntuaciones - Top 5",
            self.app.WIDTH,
            self.app.HEIGHT,
            theme=theme_scores,
        )
        
        scores_menu.add.label("=== MODO ESCAPA ===", font_size=22, font_color=(100, 200, 255))
        if top_escape:
            for i, score in enumerate(top_escape, 1):
                scores_menu.add.label(
                    f"{i}. {score['name']}: {score['score']} pts",
                    font_size=18
                )
        else:
            scores_menu.add.label("Sin puntuaciones aún", font_size=18, font_color=(200, 100, 100))
        
        scores_menu.add.vertical_margin(20)
        scores_menu.add.label("=== MODO CAZADOR ===", font_size=22, font_color=(255, 150, 100))
        if top_hunter:
            for i, score in enumerate(top_hunter, 1):
                scores_menu.add.label(
                    f"{i}. {score['name']}: {score['score']} pts",
                    font_size=18
                )
        else:
            scores_menu.add.label("Sin puntuaciones aún", font_size=18, font_color=(200, 100, 100))
        
        scores_menu.add.vertical_margin(20)
        scores_menu.add.button("← Atrás", pygame_menu.events.BACK)
        
        scores_menu.mainloop(self.app.screen)

#TODO mejorar visualmente los menús de dificultad y arreglar pequeños detalles 
# Menú de dificultad para Modo Escapa
class DifficultyMenuEscape:
    def __init__(self, app, game_loop):
        self.app = app
        self.game_loop = game_loop
        
        theme_difficulty = pygame_menu.Theme(
            background_color=(25, 25, 50),
            title_background_color=(0, 150, 200),
            title_font_shadow=True,
            widget_font=pygame_menu.font.FONT_MUNRO,
            widget_font_size=28,
            title_font_size=55,
            widget_padding=15,
            selection_color=(0, 220, 255),
        )

        self.menu = pygame_menu.Menu(
            "Modo Escapa - Dificultad",
            app.WIDTH,
            app.HEIGHT,
            theme=theme_difficulty,
        )

        self.menu.add.label("Selecciona la dificultad", font_size=26)
        self.menu.add.vertical_margin(15)

        self.menu.add.button("⭐ Fácil", lambda: self.game_loop.start_escape_mode_with_difficulty("facil"))
        self.menu.add.button("⭐⭐ Intermedio", lambda: self.game_loop.start_escape_mode_with_difficulty("intermedio"))
        self.menu.add.button("⭐⭐⭐ Difícil", lambda: self.game_loop.start_escape_mode_with_difficulty("dificil"))

        self.menu.add.vertical_margin(20)
        self.menu.add.button("← Atrás", pygame_menu.events.BACK)

    def show(self):
        self.menu.mainloop(self.app.screen)


# Menú de dificultad para Modo Cazador
class DifficultyMenuHunter:
    def __init__(self, app, game_loop):
        self.app = app
        self.game_loop = game_loop
        
        theme_difficulty = pygame_menu.Theme(
            background_color=(50, 25, 25),
            title_background_color=(200, 80, 0),
            title_font_shadow=True,
            widget_font=pygame_menu.font.FONT_MUNRO,
            widget_font_size=28,
            title_font_size=55,
            widget_padding=15,
            selection_color=(255, 150, 0),
        )

        self.menu = pygame_menu.Menu(
            "Modo Cazador - Dificultad",
            app.WIDTH,
            app.HEIGHT,
            theme=theme_difficulty,
        )

        self.menu.add.label("Selecciona la dificultad", font_size=26)
        self.menu.add.vertical_margin(15)

        self.menu.add.button("🔥 Fácil", lambda: self.game_loop.start_hunter_mode_with_difficulty("facil"))
        self.menu.add.button("🔥🔥 Intermedio", lambda: self.game_loop.start_hunter_mode_with_difficulty("intermedio"))
        self.menu.add.button("🔥🔥🔥 Difícil", lambda: self.game_loop.start_hunter_mode_with_difficulty("dificil"))

        self.menu.add.vertical_margin(20)
        self.menu.add.button("← Atrás", pygame_menu.events.BACK)

    def show(self):
        self.menu.mainloop(self.app.screen)


#game loop
class GameLoop:
    def __init__(self, app):
        self.app = app

    def start_escape_mode(self):
        print("Iniciando Modo Escapa...")
        print("Jugador:", self.app.player_name)
        self.run_game_loop(mode="escape", difficulty="normal")
        # Aquí iría la lógica del juego para el modo escapa

    def start_escape_mode_with_difficulty(self, difficulty):
        print("Iniciando Modo Escapa con dificultad:", difficulty)
        print("Jugador:", self.app.player_name)
        self.run_game_loop(mode="escape", difficulty=difficulty)

    def start_hunter_mode(self):
        print("Iniciando Modo Cazado...")
        print("Jugador:", self.app.player_name)
        self.run_game_loop(mode="cazador", difficulty="normal")

    def start_hunter_mode_with_difficulty(self, difficulty):
        print("Iniciando Modo Cazador con dificultad:", difficulty)
        print("Jugador:", self.app.player_name)
        self.run_game_loop(mode="cazador", difficulty=difficulty)
    
    def settings_mode(self):
        print("Iniciando Modo Configuración...")
        print("Jugador:", self.app.player_name)
        self.run_game_loop(mode="Configuración")
    
    def top_scores_mode(self):
        print("Iniciando Modo Puntuaciones...")
        print("Jugador:", self.app.player_name)
        self.run_game_loop(mode="Puntuaciones")

    def run_game_loop(self, mode, difficulty="normal"):
        """Loop del juego - aquí irá la lógica de juego real"""
        # Por ahora: mostrar pantalla con el modo y dificultad
        # Luego pedir puntuación y guardarla
        running = True
        clock = pygame.time.Clock()
        score = 0

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # Presionar ESPACIO para terminar el juego (simulación)
                        running = False
                
                #Fondo negro por el momento
                self.app.screen.fill((0, 0, 0))

                #Texto temporal para distinguir modos
                font = pygame.font.Font(None, 40)
                text = font.render(f"Modo: {mode} | Dificultad: {difficulty}", True, (255, 255, 255))
                self.app.screen.blit(text, (150, 250))
                
                # Instrucciones
                font_small = pygame.font.Font(None, 25)
                instr = font_small.render("Presiona ESPACIO para terminar", True, (150, 150, 150))
                self.app.screen.blit(instr, (200, 350))

                pygame.display.update()
                clock.tick(60)

        # Al terminar, pedir puntuación y guardar
        self._save_and_show_result(mode, difficulty)

    def _save_and_show_result(self, mode, difficulty):
        """Muestra un menú para ingresar puntuación y la guarda"""
        score_input = 0
        
        theme_result = pygame_menu.Theme(
            background_color=(40, 40, 60),
            title_background_color=(200, 100, 100),
            title_font_shadow=True,
            widget_font=pygame_menu.font.FONT_MUNRO,
            widget_font_size=28,
            title_font_size=50,
            widget_padding=15,
            selection_color=(255, 200, 100),
        )
        
        result_menu = pygame_menu.Menu(
            "Resultado del Juego",
            self.app.WIDTH,
            self.app.HEIGHT,
            theme=theme_result,
        )
        
        result_menu.add.label(f"Modo: {mode.capitalize()} | Dificultad: {difficulty}", font_size=22)
        result_menu.add.label(f"Jugador: {self.app.player_name}", font_size=20, font_color=(100, 200, 255))
        
        result_menu.add.vertical_margin(20)
        result_menu.add.label("Ingresa tu puntuación:", font_size=24)
        
        def update_score(value):
            nonlocal score_input
            try:
                score_input = int(value) if value else 0
            except ValueError:
                score_input = 0
        
        result_menu.add.text_input("Puntos: ", onchange=update_score, input_type=pygame_menu.widgets.PYGAME_INPUT_INT, maxchar=5)
        
        def save_score():
            if score_input > 0:
                self.app.data_manager.add_score(self.app.player_name, score_input, mode)
                result_menu.disable()
        
        result_menu.add.button("Guardar y Volver", save_score)
        result_menu.mainloop(self.app.screen)

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