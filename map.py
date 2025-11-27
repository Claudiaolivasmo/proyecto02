import pygame
import sys

# Importar toda la lógica del juego desde main.py
# Aquí NO se crea lógica nueva, solo se usa lo que ya existe
from main import (
    generar_mapa,  # Función que genera la matriz del mapa
    Jugador,  # Clase del jugador con posición y energía
    crear_enemigos_iniciales,  # Crea los enemigos en posiciones válidas
    mover_jugador,  # Función que valida y ejecuta movimientos
    mover_enemigos,  # Mueve a los enemigos hacia el jugador
    hay_colision_con_enemigo,  # Detecta si el jugador chocó con enemigo
    calcular_puntaje,  # Calcula puntos según movimientos y dificultad
    recuperar_energia_jugador,  # Recupera energía pasiva del jugador
    CONFIGS_DIFICULTAD,  # Configuraciones de cada dificultad
    DIFICULTAD_FACIL,
    ANCHO_MAPA,
    ALTO_MAPA,
    CAMINO,
    LIANA,
    TUNEL,
    MURO,
    Camino,  # Clases de terreno
    Liana,
    Tunel,
    Muro
)


class ModoEscape:
    """
    Interfaz gráfica para el modo Escape.
    
    Esta clase NO hace lógica de jugabilidad, solo:
    - Dibuja el mapa en pantalla
    - Carga y muestra sprites
    - Captura teclas del usuario
    - Llama a las funciones de main.py para la lógica real
    """
    
    def __init__(self, screen, jugador_nombre, dificultad=DIFICULTAD_FACIL):
        # Pantalla de pygame donde se dibujará todo
        self.screen = screen
        self.jugador_nombre = jugador_nombre
        self.dificultad = dificultad
        self.config = CONFIGS_DIFICULTAD[dificultad]
        
        # LLAMADA A MAIN.PY: generar el mapa (matriz de terrenos)
        # Devuelve: mapa, posición inicial, posición de salida
        self.mapa, self.inicio, self.salida = generar_mapa(ANCHO_MAPA, ALTO_MAPA)
        
        # LLAMADA A MAIN.PY: crear el jugador en la posición inicial
        fila_ini, col_ini = self.inicio
        self.jugador = Jugador(jugador_nombre, fila_ini, col_ini, self.config)
        
        # LLAMADA A MAIN.PY: crear enemigos en posiciones aleatorias válidas
        self.enemigos = crear_enemigos_iniciales(
            self.mapa, 
            self.config.cant_enemigos, 
            self.jugador, 
            self.salida
        )
        
        # Contadores para estadísticas
        self.movimientos = 0
        self.turnos = 0
        
        # Configuración de pantalla
        self.WIDTH = 800
        self.HEIGHT = 600
        
        # Calcular el tamaño de cada celda para que el mapa quepa en pantalla
        self.CELL_SIZE = min(
            (self.WIDTH - 100) // ANCHO_MAPA,
            (self.HEIGHT - 150) // ALTO_MAPA
        )
        
        # Offset para centrar el mapa en la pantalla
        self.offset_x = (self.WIDTH - (ANCHO_MAPA * self.CELL_SIZE)) // 2
        self.offset_y = 100
        
        # Estado del juego
        self.juego_terminado = False
        self.mensaje_final = ""
        self.puntaje_final = 0
        
        # Fuentes para textos
        self.font_medium = pygame.font.Font(None, 30)
        self.font_small = pygame.font.Font(None, 24)
        
        # Colores usados en la interfaz
        self.COLOR_BG = (20, 20, 40)  # Fondo oscuro azulado
        self.COLOR_TEXT = (255, 255, 255)  # Texto blanco
        self.COLOR_SUCCESS = (100, 255, 100)  # Verde para mensajes de éxito
        self.COLOR_DANGER = (255, 100, 100)  # Rojo para peligro
        
        # Imágenes del terreno (se cargan en cargar_imagenes())
        self.imagen_camino = None
        self.imagen_liana = None
        self.imagen_tunel = None
        self.imagen_muro = None
        self.imagen_enemigo = None
        self.imagen_salida = None
        
        # Sprites del jugador con animación
        self.jugador_sprites = {
            'down': [],
            'up': [],
            'left': [],
            'right': []
        }
        self.jugador_direccion = 'down'  # Dirección actual
        self.jugador_frame = 0  # Frame actual de animación
        self.animation_speed = 8  # Velocidad de animación
        self.animation_counter = 0
        
        # Sistema de movimiento suave
        self.moviendo = False
        self.pos_pixel_x = col_ini * self.CELL_SIZE  # Posición en píxeles
        self.pos_pixel_y = fila_ini * self.CELL_SIZE
        self.target_x = self.pos_pixel_x  # Posición objetivo
        self.target_y = self.pos_pixel_y
        self.velocidad_movimiento = 8  # Píxeles por frame
        
    def cargar_imagenes(self):
        """
        Carga todas las imágenes del terreno desde la carpeta data/terreno.
        Las escala al tamaño de cada celda para que se vean bien.
        Si falla, se usan colores sólidos como respaldo.
        """
        try:
            # Obtener la ruta absoluta donde está este archivo
            import os
            base_dir = os.path.dirname(os.path.abspath(__file__))
            terreno_dir = os.path.join(base_dir, "data", "terreno")
            
            # Cargar cada imagen y escalarla
            self.imagen_camino = pygame.image.load(os.path.join(terreno_dir, "camino.png"))
            self.imagen_camino = pygame.transform.scale(self.imagen_camino, (self.CELL_SIZE, self.CELL_SIZE))
            
            self.imagen_liana = pygame.image.load(os.path.join(terreno_dir, "lianas_on_wall.png"))
            self.imagen_liana = pygame.transform.scale(self.imagen_liana, (self.CELL_SIZE, self.CELL_SIZE))
            
            self.imagen_tunel = pygame.image.load(os.path.join(terreno_dir, "tunel3.png"))
            self.imagen_tunel = pygame.transform.scale(self.imagen_tunel, (self.CELL_SIZE, self.CELL_SIZE))
            
            self.imagen_muro = pygame.image.load(os.path.join(terreno_dir, "muro.png"))
            self.imagen_muro = pygame.transform.scale(self.imagen_muro, (self.CELL_SIZE, self.CELL_SIZE))
            
            print("✓ Imágenes del terreno cargadas correctamente")
            
        except (pygame.error, FileNotFoundError) as e:
            print(f"⚠️ Error al cargar imágenes del terreno: {e}")
            print("Se usarán colores en su lugar.")
        
        # Cargar sprites del jugador
        try:
            import os
            base_dir = os.path.dirname(os.path.abspath(__file__))
            jugador_dir = os.path.join(base_dir, "data", "jugador")
            
            # Cargar sprites de cada dirección (4 frames por dirección)
            for i in range(4):
                # Abajo
                sprite = pygame.image.load(os.path.join(jugador_dir, f"walk_down_{i}.png"))
                sprite = pygame.transform.scale(sprite, (self.CELL_SIZE, self.CELL_SIZE))
                self.jugador_sprites['down'].append(sprite)
                
                # Arriba
                sprite = pygame.image.load(os.path.join(jugador_dir, f"walk_up_{i}.png"))
                sprite = pygame.transform.scale(sprite, (self.CELL_SIZE, self.CELL_SIZE))
                self.jugador_sprites['up'].append(sprite)
                
                # Izquierda
                sprite = pygame.image.load(os.path.join(jugador_dir, f"walk_left_{i}.png"))
                sprite = pygame.transform.scale(sprite, (self.CELL_SIZE, self.CELL_SIZE))
                self.jugador_sprites['left'].append(sprite)
                
                # Derecha
                sprite = pygame.image.load(os.path.join(jugador_dir, f"walk_right_{i}.png"))
                sprite = pygame.transform.scale(sprite, (self.CELL_SIZE, self.CELL_SIZE))
                self.jugador_sprites['right'].append(sprite)
            
            print("✓ Sprites del jugador cargados correctamente")
            
        except (pygame.error, FileNotFoundError) as e:
            print(f"⚠️ Error al cargar sprites del jugador: {e}")
            print("Se usará un círculo en su lugar.")
        
        # TODO: Agregar imágenes para enemigo y salida si las tienes
    
    def dibujar_celda(self, fila, col, casilla):
        """
        Dibuja una celda individual del mapa.
        
        Revisa el tipo de casilla (Camino, Liana, Tunel, Muro) y:
        - Si hay imagen cargada -> dibuja la imagen
        - Si no hay imagen -> dibuja un rectángulo de color
        """
        # Calcular la posición en píxeles de esta celda
        x = self.offset_x + col * self.CELL_SIZE
        y = self.offset_y + fila * self.CELL_SIZE
        
        # Dibujar según el tipo de terreno
        if isinstance(casilla, Camino):
            if self.imagen_camino:
                self.screen.blit(self.imagen_camino, (x, y))
            else:
                pygame.draw.rect(self.screen, (200, 200, 200), (x, y, self.CELL_SIZE, self.CELL_SIZE))
                
        elif isinstance(casilla, Liana):
            if self.imagen_liana:
                self.screen.blit(self.imagen_liana, (x, y))
            else:
                pygame.draw.rect(self.screen, (50, 150, 50), (x, y, self.CELL_SIZE, self.CELL_SIZE))
                
        elif isinstance(casilla, Tunel):
            if self.imagen_tunel:
                self.screen.blit(self.imagen_tunel, (x, y))
            else:
                pygame.draw.rect(self.screen, (100, 100, 150), (x, y, self.CELL_SIZE, self.CELL_SIZE))
                
        elif isinstance(casilla, Muro):
            if self.imagen_muro:
                self.screen.blit(self.imagen_muro, (x, y))
            else:
                pygame.draw.rect(self.screen, (60, 60, 60), (x, y, self.CELL_SIZE, self.CELL_SIZE))
        
        # Borde de la celda
        pygame.draw.rect(self.screen, (80, 80, 80), (x, y, self.CELL_SIZE, self.CELL_SIZE), 1)
    
    def dibujar_mapa(self):
        """
        Dibuja el mapa completo recorriendo todas las celdas.
        Llama a dibujar_celda() para cada posición.
        """
        for fila in range(len(self.mapa)):
            for col in range(len(self.mapa[0])):
                self.dibujar_celda(fila, col, self.mapa[fila][col])
    
    def actualizar_movimiento(self):
        """
        Actualiza el movimiento suave del jugador.
        Mueve gradualmente desde pos_pixel actual hacia target (destino).
        """
        if self.moviendo:
            # Calcular distancia al objetivo
            dx = self.target_x - self.pos_pixel_x
            dy = self.target_y - self.pos_pixel_y
            
            # Si está muy cerca, ajustar exactamente
            if abs(dx) < self.velocidad_movimiento and abs(dy) < self.velocidad_movimiento:
                self.pos_pixel_x = self.target_x
                self.pos_pixel_y = self.target_y
                self.moviendo = False
            else:
                # Mover hacia el objetivo
                if dx != 0:
                    self.pos_pixel_x += self.velocidad_movimiento if dx > 0 else -self.velocidad_movimiento
                if dy != 0:
                    self.pos_pixel_y += self.velocidad_movimiento if dy > 0 else -self.velocidad_movimiento
            
            # Animar mientras se mueve
            self.animation_counter += 1
            if self.animation_counter >= self.animation_speed:
                self.jugador_frame = (self.jugador_frame + 1) % 4
                self.animation_counter = 0
    
    def dibujar_entidades(self):
        """
        Dibuja todas las entidades del juego:
        - La salida (meta/puerta)
        - Los enemigos vivos
        - El jugador
        """
        # === DIBUJAR LA SALIDA ===
        salida_x = self.offset_x + self.salida[1] * self.CELL_SIZE
        salida_y = self.offset_y + self.salida[0] * self.CELL_SIZE
        
        if self.imagen_salida:
            self.screen.blit(self.imagen_salida, (salida_x, salida_y))
        else:
            pygame.draw.rect(self.screen, (255, 215, 0), 
                           (salida_x, salida_y, self.CELL_SIZE, self.CELL_SIZE))
            texto_salida = self.font_small.render("🚪", True, self.COLOR_TEXT)
            self.screen.blit(texto_salida, (salida_x + 5, salida_y + 5))
        
        # === DIBUJAR ENEMIGOS ===
        for enemigo in self.enemigos:
            if enemigo.vivo:  # Solo dibujar enemigos que siguen vivos
                enemigo_x = self.offset_x + enemigo.columna * self.CELL_SIZE
                enemigo_y = self.offset_y + enemigo.fila * self.CELL_SIZE
                
                if self.imagen_enemigo:
                    self.screen.blit(self.imagen_enemigo, (enemigo_x, enemigo_y))
                else:
                    pygame.draw.circle(self.screen, (255, 0, 0),
                                     (enemigo_x + self.CELL_SIZE // 2, 
                                      enemigo_y + self.CELL_SIZE // 2),
                                     self.CELL_SIZE // 3)
        
        # === DIBUJAR JUGADOR ===
        # Usar posición suave para movimiento fluido
        jugador_x = self.offset_x + self.pos_pixel_x
        jugador_y = self.offset_y + self.pos_pixel_y
        
        # Si hay sprites cargados, usar animación
        if self.jugador_sprites[self.jugador_direccion]:
            sprite_actual = self.jugador_sprites[self.jugador_direccion][self.jugador_frame]
            self.screen.blit(sprite_actual, (jugador_x, jugador_y))
        else:
            # Fallback: círculo azul si no hay sprites
            pygame.draw.circle(self.screen, (0, 150, 255),
                             (jugador_x + self.CELL_SIZE // 2, 
                              jugador_y + self.CELL_SIZE // 2),
                             self.CELL_SIZE // 3)
    
    def dibujar_ui(self):
        """
        Dibuja la interfaz de usuario (HUD):
        - Título del modo y dificultad
        - Nombre del jugador
        - Energía actual (verde si >30, rojo si <=30)
        - Contador de movimientos
        - Instrucciones de control
        """
        # Título
        titulo = self.font_medium.render(f"Modo Escape - {self.config.nombre.upper()}", 
                                        True, self.COLOR_TEXT)
        self.screen.blit(titulo, (10, 10))
        
        # Jugador
        nombre_text = self.font_small.render(f"Jugador: {self.jugador_nombre}", 
                                            True, self.COLOR_TEXT)
        self.screen.blit(nombre_text, (10, 45))
        
        # Energía
        energia_color = self.COLOR_SUCCESS if self.jugador.energia_actual > 30 else self.COLOR_DANGER
        energia_text = self.font_small.render(
            f"Energía: {self.jugador.energia_actual}/{self.jugador.energia_max}", 
            True, energia_color
        )
        self.screen.blit(energia_text, (10, 70))
        
        # Movimientos
        mov_text = self.font_small.render(f"Movimientos: {self.movimientos}", 
                                         True, self.COLOR_TEXT)
        self.screen.blit(mov_text, (self.WIDTH - 200, 45))
        
        # Instrucciones
        inst_text = self.font_small.render("WASD: Mover | ESC: Salir", 
                                          True, (150, 150, 150))
        self.screen.blit(inst_text, (self.WIDTH - 250, 70))
    
    def manejar_eventos(self, evento):
        """
        Captura las teclas presionadas y procesa el movimiento del jugador.
        
        IMPORTANTE: Este método NO valida el movimiento, solo:
        1. Detecta qué tecla presionó el usuario
        2. Llama a mover_jugador() de main.py (que tiene la lógica real)
        3. Si el movimiento fue exitoso, actualiza contadores y revisa victoria/derrota
        
        Returns:
            False si debe salir del juego, True si debe continuar
        """
        # No procesar eventos si el juego terminó o está en movimiento
        if self.juego_terminado or self.moviendo:
            return False if self.juego_terminado else True
        
        if evento.type == pygame.KEYDOWN:
            direccion = None
            direccion_sprite = None
            
            # Detectar qué tecla presionó
            if evento.key == pygame.K_w or evento.key == pygame.K_UP:
                direccion = "arriba"
                direccion_sprite = "up"
            elif evento.key == pygame.K_s or evento.key == pygame.K_DOWN:
                direccion = "abajo"
                direccion_sprite = "down"
            elif evento.key == pygame.K_a or evento.key == pygame.K_LEFT:
                direccion = "izquierda"
                direccion_sprite = "left"
            elif evento.key == pygame.K_d or evento.key == pygame.K_RIGHT:
                direccion = "derecha"
                direccion_sprite = "right"
            elif evento.key == pygame.K_ESCAPE:
                return False  # Salir del modo
            
            if direccion:
                # Actualizar dirección del sprite
                if direccion_sprite:
                    self.jugador_direccion = direccion_sprite
                
                # LLAMADA A MAIN.PY: intentar mover al jugador
                # Esta función valida si el movimiento es posible y actualiza la posición
                se_movio = mover_jugador(self.jugador, direccion, self.mapa, self.config, correr=False)
                
                if se_movio:
                    # El movimiento fue exitoso, iniciar animación suave
                    self.target_x = self.jugador.columna * self.CELL_SIZE
                    self.target_y = self.jugador.fila * self.CELL_SIZE
                    self.moviendo = True
                    self.animation_counter = 0
                    
                    self.movimientos += 1
                    self.turnos += 1
                    
                    # ¿Llegó a la salida? -> GANA
                    if self.jugador.fila == self.salida[0] and self.jugador.columna == self.salida[1]:
                        self.puntaje_final = calcular_puntaje(self.movimientos, self.config)
                        self.mensaje_final = "¡GANASTE! Has llegado a la salida"
                        self.juego_terminado = True
                        return True
                    
                    # Mover enemigos cada cierto número de turnos
                    if self.turnos % self.config.vel_enemigos == 0:
                        mover_enemigos(self.enemigos, self.jugador, self.mapa)
                    
                    # ¿Chocó con un enemigo? -> PIERDE
                    if hay_colision_con_enemigo(self.jugador, self.enemigos):
                        self.puntaje_final = 0
                        self.mensaje_final = "PERDISTE: Un cazador te atrapó"
                        self.juego_terminado = True
                        return True
                    
                    # LLAMADA A MAIN.PY: recuperar energía pasiva
                    recuperar_energia_jugador(self.jugador, self.config)
        
        return True  # Continuar jugando
    
    def dibujar(self):
        """
        Dibuja toda la escena del juego.
        
        Si el juego está activo:
            - Dibuja el mapa
            - Dibuja entidades (jugador, enemigos, salida)
            - Dibuja UI (energía, movimientos, etc.)
        
        Si el juego terminó:
            - Muestra pantalla de victoria/derrota
            - Muestra el puntaje
            - Muestra instrucción para volver al menú
        """
        self.screen.fill(self.COLOR_BG)
        
        # Actualizar movimiento suave del jugador
        self.actualizar_movimiento()
        
        if not self.juego_terminado:
            # Juego activo: dibujar todo normalmente
            self.dibujar_mapa()
            self.dibujar_entidades()
            self.dibujar_ui()
        else:
            # Juego terminado: mostrar pantalla final
            self.dibujar_mapa()
            self.dibujar_entidades()
            
            # Overlay oscuro semi-transparente
            overlay = pygame.Surface((self.WIDTH, self.HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            # Mensaje de victoria o derrota
            font_grande = pygame.font.Font(None, 60)
            color = self.COLOR_SUCCESS if "GANASTE" in self.mensaje_final else self.COLOR_DANGER
            mensaje = font_grande.render(self.mensaje_final, True, color)
            self.screen.blit(mensaje, (self.WIDTH // 2 - mensaje.get_width() // 2, self.HEIGHT // 2 - 50))
            
            # Mostrar puntaje final
            puntaje_text = self.font_medium.render(f"Puntaje: {self.puntaje_final}", 
                                                   True, self.COLOR_TEXT)
            self.screen.blit(puntaje_text, 
                           (self.WIDTH // 2 - puntaje_text.get_width() // 2, self.HEIGHT // 2 + 20))
            
            # Instrucción para salir
            inst = self.font_small.render("Presiona ESC para volver al menú", 
                                         True, (200, 200, 200))
            self.screen.blit(inst, (self.WIDTH // 2 - inst.get_width() // 2, self.HEIGHT // 2 + 80))
    
    def obtener_resultado(self):
        """
        Devuelve el puntaje final del jugador.
        Lo usa main_menu.py para guardarlo en el sistema de puntajes.
        """
        return self.puntaje_final
