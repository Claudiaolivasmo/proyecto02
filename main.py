import pygame
import os
from data.data_manager import DataManager

pygame.init()

# Constantes
WIDTH, HEIGHT = 800, 600
FONT_LARGE = pygame.font.Font(None, 50)
FONT_MEDIUM = pygame.font.Font(None, 35)
FONT_SMALL = pygame.font.Font(None, 25)
COLORS = {
    'BG': (20, 20, 40),
    'BUTTON': (0, 120, 200),
    'BUTTON_HOVER': (0, 180, 255),
    'TEXT': (255, 255, 255),
    'ERROR': (255, 100, 100),
    'SUCCESS': (100, 255, 100),
}


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Escape del Laberinto")
        self.data_manager = DataManager()
        self.clock = pygame.time.Clock()
        self.player_name = ""
        self.current_screen = "registro"
        self.running = True

        # Variables para el registro
        self.input_name = ""
        self.input_active = False
        self.error_msg = ""
        self.error_timer = 0

        # Variables para modo juego
        self.selected_difficulty = None
        self.selected_mode = None

    def run(self):
        """Loop principal del juego"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()

    def handle_events(self):
        """Manejo de eventos globales"""
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.current_screen == "registro":
                self.handle_registro_events(event, mouse_pos)
            elif self.current_screen == "menu_principal":
                self.handle_menu_principal_events(event, mouse_pos)
            elif self.current_screen == "modo_escape":
                self.handle_dificultad_events(event, mouse_pos, "escape")
            elif self.current_screen == "modo_cazador":
                self.handle_dificultad_events(event, mouse_pos, "cazador")
            elif self.current_screen == "puntajes":
                self.handle_puntajes_events(event, mouse_pos)

    def handle_registro_events(self, event, mouse_pos):
        """Eventos de la pantalla de registro"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Detectar clic en caja de entrada
            input_box = pygame.Rect(WIDTH // 2 - 150, 250, 300, 50)
            if input_box.collidepoint(mouse_pos):
                self.input_active = True
            else:
                self.input_active = False

            # Botón REGISTRARSE
            btn_registrar = pygame.Rect(WIDTH // 2 - 200, 350, 150, 50)
            if btn_registrar.collidepoint(mouse_pos):
                self.register_player()

            # Botón INICIAR SESIÓN
            btn_login = pygame.Rect(WIDTH // 2 + 50, 350, 150, 50)
            if btn_login.collidepoint(mouse_pos):
                self.login_player()

        if event.type == pygame.KEYDOWN and self.input_active:
            if event.key == pygame.K_BACKSPACE:
                self.input_name = self.input_name[:-1]
            elif event.key == pygame.K_RETURN:
                self.register_player()
            elif len(self.input_name) < 15 and event.unicode.isprintable():
                self.input_name += event.unicode

    def handle_menu_principal_events(self, event, mouse_pos):
        """Eventos del menú principal"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Botones del menú
            btn_escape = pygame.Rect(WIDTH // 2 - 150, 150, 300, 60)
            btn_cazador = pygame.Rect(WIDTH // 2 - 150, 240, 300, 60)
            btn_puntajes = pygame.Rect(WIDTH // 2 - 150, 330, 300, 60)
            btn_salir = pygame.Rect(WIDTH // 2 - 150, 420, 300, 60)

            if btn_escape.collidepoint(mouse_pos):
                self.current_screen = "modo_escape"
            elif btn_cazador.collidepoint(mouse_pos):
                self.current_screen = "modo_cazador"
            elif btn_puntajes.collidepoint(mouse_pos):
                self.current_screen = "puntajes"
            elif btn_salir.collidepoint(mouse_pos):
                self.running = False

    def handle_dificultad_events(self, event, mouse_pos, modo):
        """Eventos de selección de dificultad"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            btn_facil = pygame.Rect(WIDTH // 2 - 150, 180, 300, 60)
            btn_medio = pygame.Rect(WIDTH // 2 - 150, 270, 300, 60)
            btn_dificil = pygame.Rect(WIDTH // 2 - 150, 360, 300, 60)
            btn_atras = pygame.Rect(WIDTH // 2 - 150, 450, 300, 60)

            if btn_facil.collidepoint(mouse_pos):
                self.play_game(modo, "facil")
                self.current_screen = "menu_principal"
            elif btn_medio.collidepoint(mouse_pos):
                self.play_game(modo, "medio")
                self.current_screen = "menu_principal"
            elif btn_dificil.collidepoint(mouse_pos):
                self.play_game(modo, "dificil")
                self.current_screen = "menu_principal"
            elif btn_atras.collidepoint(mouse_pos):
                self.current_screen = "menu_principal"

        # Presionar ESC para volver
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.current_screen = "menu_principal"

    def handle_puntajes_events(self, event, mouse_pos):
        """Eventos de la pantalla de puntajes"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            btn_atras = pygame.Rect(WIDTH // 2 - 150, 500, 300, 60)
            if btn_atras.collidepoint(mouse_pos):
                self.current_screen = "menu_principal"

        # Presionar ESC para volver
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.current_screen = "menu_principal"

    def register_player(self):
        """Registrar un nuevo jugador"""
        if not self.input_name:
            self.error_msg = "Por favor ingresa un nombre."
            self.error_timer = pygame.time.get_ticks()
            return

        if len(self.input_name) < 2:
            self.error_msg = "El nombre debe tener al menos 2 caracteres."
            self.error_timer = pygame.time.get_ticks()
            return

        if not self.input_name.isalpha():
            self.error_msg = "El nombre solo puede contener letras."
            self.error_timer = pygame.time.get_ticks()
            return

        # Intentar registrar
        if self.data_manager.register_player(self.input_name):
            self.player_name = self.input_name
            self.error_msg = f"¡Bienvenido, {self.input_name}!"
            self.error_timer = pygame.time.get_ticks()
            pygame.time.delay(1000)
            self.current_screen = "menu_principal"
            self.input_name = ""
        else:
            self.error_msg = "Este nombre ya existe. Intenta otro."
            self.error_timer = pygame.time.get_ticks()

    def login_player(self):
        """Iniciar sesión con un jugador existente"""
        if not self.input_name:
            self.error_msg = "Por favor ingresa un nombre."
            self.error_timer = pygame.time.get_ticks()
            return

        user = self.data_manager.login_player(self.input_name)
        if user:
            self.player_name = self.input_name
            self.error_msg = f"¡Bienvenido de vuelta, {self.input_name}!"
            self.error_timer = pygame.time.get_ticks()
            pygame.time.delay(1000)
            self.current_screen = "menu_principal"
            self.input_name = ""
        else:
            self.error_msg = "Jugador no encontrado. Regístrate primero."
            self.error_timer = pygame.time.get_ticks()

    def play_game(self, modo, dificultad):
        """Simular la partida y pedir puntuación"""
        # Mostrar pantalla de juego (placeholder)
        playing = True
        score = 0
        input_score = ""

        while playing:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    playing = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # Presionar ESPACIO para terminar el juego
                        playing = False

            self.screen.fill(COLORS['BG'])
            title = FONT_LARGE.render(f"Modo: {modo.upper()} - {dificultad.upper()}", True, COLORS['TEXT'])
            instr = FONT_SMALL.render("Presiona ESPACIO para terminar", True, (150, 150, 150))
            self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 100))
            self.screen.blit(instr, (WIDTH // 2 - instr.get_width() // 2, HEIGHT // 2 + 50))
            pygame.display.flip()
            self.clock.tick(60)

        # Pedir puntuación
        self.ask_for_score(modo, dificultad)

    def ask_for_score(self, modo, dificultad):
        """Pantalla para ingresar la puntuación"""
        asking = True
        input_score = ""

        while asking:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    asking = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        # Guardar puntuación
                        try:
                            score = int(input_score) if input_score else 0
                            if score > 0:
                                self.data_manager.add_score(self.player_name, score, modo)
                        except ValueError:
                            pass
                        asking = False
                    elif event.key == pygame.K_BACKSPACE:
                        input_score = input_score[:-1]
                    elif event.unicode.isdigit():
                        input_score += event.unicode

            self.screen.fill(COLORS['BG'])
            title = FONT_LARGE.render("Ingresa tu puntuación", True, COLORS['TEXT'])
            input_text = FONT_MEDIUM.render(f"Puntos: {input_score}", True, COLORS['TEXT'])
            instr = FONT_SMALL.render("Presiona ENTER para guardar", True, (150, 150, 150))

            self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 100))
            self.screen.blit(input_text, (WIDTH // 2 - input_text.get_width() // 2, HEIGHT // 2))
            self.screen.blit(instr, (WIDTH // 2 - instr.get_width() // 2, HEIGHT // 2 + 100))

            pygame.display.flip()
            self.clock.tick(60)

    def update(self):
        """Actualizar lógica del juego"""
        mouse_pos = pygame.mouse.get_pos()
        # Aquí iría la lógica de hover de botones si es necesario

    def draw(self):
        """Dibujar la pantalla actual"""
        self.screen.fill(COLORS['BG'])

        if self.current_screen == "registro":
            self.draw_registro()
        elif self.current_screen == "menu_principal":
            self.draw_menu_principal()
        elif self.current_screen == "modo_escape":
            self.draw_dificultad("MODO ESCAPA")
        elif self.current_screen == "modo_cazador":
            self.draw_dificultad("MODO CAZADOR")
        elif self.current_screen == "puntajes":
            self.draw_puntajes()

        pygame.display.flip()

    def draw_registro(self):
        """Dibujar pantalla de registro"""
        # Título
        title = FONT_LARGE.render("Acceso al Juego", True, COLORS['TEXT'])
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        # Mensaje de error/éxito
        if self.error_msg and pygame.time.get_ticks() - self.error_timer < 2000:
            color = COLORS['SUCCESS'] if "Bienvenido" in self.error_msg else COLORS['ERROR']
            error = FONT_SMALL.render(self.error_msg, True, color)
            self.screen.blit(error, (WIDTH // 2 - error.get_width() // 2, 120))

        # Caja de entrada
        label = FONT_MEDIUM.render("Nombre:", True, COLORS['TEXT'])
        self.screen.blit(label, (WIDTH // 2 - 300, 220))

        input_box = pygame.Rect(WIDTH // 2 - 150, 250, 300, 50)
        pygame.draw.rect(self.screen, (100, 100, 100), input_box, border_radius=5)
        pygame.draw.rect(self.screen, (0, 200, 255) if self.input_active else (100, 100, 100), input_box, 2, border_radius=5)

        input_text = FONT_MEDIUM.render(self.input_name, True, COLORS['TEXT'])
        self.screen.blit(input_text, (input_box.x + 10, input_box.y + 10))

        # Botón REGISTRARSE
        btn_registrar = pygame.Rect(WIDTH // 2 - 200, 350, 150, 50)
        pygame.draw.rect(self.screen, COLORS['BUTTON'], btn_registrar, border_radius=5)
        registrar_text = FONT_SMALL.render("REGISTRARSE", True, COLORS['TEXT'])
        self.screen.blit(registrar_text, (btn_registrar.x + 10, btn_registrar.y + 10))

        # Botón INICIAR SESIÓN
        btn_login = pygame.Rect(WIDTH // 2 + 50, 350, 150, 50)
        pygame.draw.rect(self.screen, COLORS['BUTTON'], btn_login, border_radius=5)
        login_text = FONT_SMALL.render("INICIAR SESIÓN", True, COLORS['TEXT'])
        self.screen.blit(login_text, (btn_login.x + 10, btn_login.y + 10))

    def draw_menu_principal(self):
        """Dibujar menú principal"""
        # Título con nombre del jugador
        title = FONT_LARGE.render("Escape del Laberinto", True, COLORS['TEXT'])
        player_label = FONT_MEDIUM.render(f"Jugador: {self.player_name}", True, (100, 200, 255))
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))
        self.screen.blit(player_label, (WIDTH // 2 - player_label.get_width() // 2, 100))

        # Botones
        self.draw_button(WIDTH // 2 - 150, 150, 300, 60, "Modo Escapa")
        self.draw_button(WIDTH // 2 - 150, 240, 300, 60, "Modo Cazador")
        self.draw_button(WIDTH // 2 - 150, 330, 300, 60, "Puntajes")
        self.draw_button(WIDTH // 2 - 150, 420, 300, 60, "Salir")

    def draw_dificultad(self, titulo):
        """Dibujar pantalla de selección de dificultad"""
        title = FONT_LARGE.render(titulo, True, COLORS['TEXT'])
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        label = FONT_MEDIUM.render("Selecciona dificultad:", True, COLORS['TEXT'])
        self.screen.blit(label, (WIDTH // 2 - label.get_width() // 2, 120))

        self.draw_button(WIDTH // 2 - 150, 180, 300, 60, "⭐ Fácil")
        self.draw_button(WIDTH // 2 - 150, 270, 300, 60, "⭐⭐ Medio")
        self.draw_button(WIDTH // 2 - 150, 360, 300, 60, "⭐⭐⭐ Difícil")
        self.draw_button(WIDTH // 2 - 150, 450, 300, 60, "← Atrás")

    def draw_puntajes(self):
        """Dibujar pantalla de puntajes"""
        title = FONT_LARGE.render("Top 5 - Puntajes", True, COLORS['TEXT'])
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))

        # Recargar datos
        self.data_manager.reload()

        # Top 5 Escape
        escape_label = FONT_MEDIUM.render("=== MODO ESCAPA ===", True, (100, 200, 255))
        self.screen.blit(escape_label, (WIDTH // 2 - escape_label.get_width() // 2, 100))

        top_escape = self.data_manager.get_top5("escape")
        for i, score in enumerate(top_escape):
            score_text = FONT_SMALL.render(f"{i + 1}. {score['nombre']}: {score['score']} pts", True, COLORS['TEXT'])
            self.screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 150 + i * 30))

        if not top_escape:
            no_scores = FONT_SMALL.render("Sin puntuaciones aún", True, COLORS['ERROR'])
            self.screen.blit(no_scores, (WIDTH // 2 - no_scores.get_width() // 2, 150))

        # Botón Atrás
        self.draw_button(WIDTH // 2 - 150, 500, 300, 60, "← Atrás")

    def draw_button(self, x, y, width, height, text):
        """Dibujar un botón"""
        rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, COLORS['BUTTON'], rect, border_radius=5)
        button_text = FONT_MEDIUM.render(text, True, COLORS['TEXT'])
        self.screen.blit(button_text, (rect.x + width // 2 - button_text.get_width() // 2,
                                       rect.y + height // 2 - button_text.get_height() // 2))


if __name__ == "__main__":
    game = Game()
    game.run()
