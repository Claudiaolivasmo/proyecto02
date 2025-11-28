import pygame
import sys

# Importar toda la lógica del juego desde main.py
# Aquí NO se crea lógica nueva, solo se usa lo que ya existe
from main import (
    generar_mapa,  # Función que genera la matriz del mapa
    Jugador,  # Clase del jugador con posición y energía
    crear_enemigos_en_camino,  # Crea los enemigos en el camino principal
    mover_jugador,  # Función que valida y ejecuta movimientos
    mover_enemigos,  # Mueve a los enemigos hacia el jugador
    Bomba,  # Clase de bomba
    colocar_bomba,  # Función para colocar bombas
    explotar_bomba,  # Función para explotar bombas
    procesar_bombas_y_respawn,  # Procesa explosiones y respawn
    DEMORA_EXPLOSION_BOMBA,  # Turnos antes de explotar
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
        # Ahora devuelve: mapa, posición inicial, posición de salida, camino_principal
        self.mapa, self.inicio, self.salida, self.camino_principal = generar_mapa(ANCHO_MAPA, ALTO_MAPA)
        
        # LLAMADA A MAIN.PY: crear el jugador en la posición inicial
        fila_ini, col_ini = self.inicio
        self.jugador = Jugador(jugador_nombre, fila_ini, col_ini, self.config)
        
        # LLAMADA A MAIN.PY: crear enemigos en el camino principal
        self.enemigos = crear_enemigos_en_camino(
            self.camino_principal, 
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
        self.imagen_salida = None
        
        # Sprites del jugador con animación
        self.jugador_sprites = {
            'down': [],
            'up': [],
            'left': [],
            'right': []
        }
        self.jugador_direccion = 'down'  # Dirección actual
        self.jugador_frame = 0.0  # Frame actual de animación (float para animación suave)
        self.frame_speed = 0.15  # Velocidad de cambio de frames
        
        # Sprites de enemigos (cazadores) con animación
        self.enemigo_sprites = {
            'down': [],
            'up': [],
            'left': [],
            'right': []
        }
        # Guardar la dirección de cada enemigo (índice del enemigo -> dirección)
        self.enemigo_direcciones = {}
        self.enemigo_frames = {}
        
        # Sistema de movimiento continuo (NO por celdas)
        self.velocidad_jugador = 2  # Píxeles por frame que se mueve
        self.pos_pixel_x = col_ini * self.CELL_SIZE  # Posición exacta en píxeles
        self.pos_pixel_y = fila_ini * self.CELL_SIZE
        self.moviendo = False  # Si actualmente está en movimiento
        
        # Sistema de bombas
        self.bombas = []  # Lista de bombas colocadas
        self.ultimo_turno_bomba = -999  # Último turno en que se colocó una bomba
        self.enemigos_por_respawnear = []  # Enemigos que reaparecerán
        self.bomba_sprites = []  # Sprites de la bomba (6 frames)
        self.explosion_sprites = []  # Sprites de explosión (10 frames)
        self.explosiones_activas = []  # Lista de explosiones en pantalla: [(fila, col, frame, frame_counter)]
        self.espacio_presionado = False  # Para detectar solo una vez al presionar ESPACIO
        
        # Sistema de animación de barra de energía
        self.energia_visual = float(self.jugador.energia_actual)  # Energía que se muestra (animada)
        self.velocidad_animacion_energia = 2.0  # Velocidad de animación de la barra
        
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
        
        # Cargar sprites de enemigos (cazadores)
        try:
            import os
            base_dir = os.path.dirname(os.path.abspath(__file__))
            cazador_dir = os.path.join(base_dir, "data", "cazador")
            
            # Cargar sprites de cada dirección (3 frames por dirección)
            for i in range(3):
                # Abajo
                sprite = pygame.image.load(os.path.join(cazador_dir, f"w_down_{i}.png"))
                sprite = pygame.transform.scale(sprite, (self.CELL_SIZE, self.CELL_SIZE))
                self.enemigo_sprites['down'].append(sprite)
                
                # Arriba - manejo especial para el archivo con nombre diferente
                if i == 2:
                    # El tercer frame tiene un nombre diferente: w_ups_2.png
                    sprite = pygame.image.load(os.path.join(cazador_dir, "w_ups_2.png"))
                else:
                    sprite = pygame.image.load(os.path.join(cazador_dir, f"w_up_{i}.png"))
                sprite = pygame.transform.scale(sprite, (self.CELL_SIZE, self.CELL_SIZE))
                self.enemigo_sprites['up'].append(sprite)
                
                # Izquierda
                sprite = pygame.image.load(os.path.join(cazador_dir, f"w_left_{i}.png"))
                sprite = pygame.transform.scale(sprite, (self.CELL_SIZE, self.CELL_SIZE))
                self.enemigo_sprites['left'].append(sprite)
                
                # Derecha
                sprite = pygame.image.load(os.path.join(cazador_dir, f"w_right_{i}.png"))
                sprite = pygame.transform.scale(sprite, (self.CELL_SIZE, self.CELL_SIZE))
                self.enemigo_sprites['right'].append(sprite)
            
            # Inicializar dirección y frame para cada enemigo
            for i, enemigo in enumerate(self.enemigos):
                self.enemigo_direcciones[i] = 'down'
                self.enemigo_frames[i] = 0
            
            print("✓ Sprites de cazadores cargados correctamente")
            
        except (pygame.error, FileNotFoundError) as e:
            print(f"⚠️ Error al cargar sprites de cazadores: {e}")
            print("Se usarán círculos rojos en su lugar.")
        
        # Cargar sprites de bombas y explosiones
        try:
            import os
            base_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Cargar sprites de bombas (6 frames)
            bomb_dir = os.path.join(base_dir, "data", "bomb")
            for i in range(1, 7):
                sprite = pygame.image.load(os.path.join(bomb_dir, f"bomb{i}.png"))
                sprite = pygame.transform.scale(sprite, (self.CELL_SIZE, self.CELL_SIZE))
                self.bomba_sprites.append(sprite)
            
            # Cargar sprites de explosiones (10 frames)
            explosion_dir = os.path.join(base_dir, "data", "explotions")
            for i in range(1, 11):
                sprite = pygame.image.load(os.path.join(explosion_dir, f"Explosion{i}.png"))
                sprite = pygame.transform.scale(sprite, (self.CELL_SIZE, self.CELL_SIZE))
                self.explosion_sprites.append(sprite)
            
            print("✓ Sprites de bombas y explosiones cargados correctamente")
            
        except (pygame.error, FileNotFoundError) as e:
            print(f"⚠️ Error al cargar sprites de bombas/explosiones: {e}")
        
        # TODO: Agregar imagen para salida si la tienes
    
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
        for idx, enemigo in enumerate(self.enemigos):
            if enemigo.vivo:  # Solo dibujar enemigos que siguen vivos
                enemigo_x = self.offset_x + enemigo.columna * self.CELL_SIZE
                enemigo_y = self.offset_y + enemigo.fila * self.CELL_SIZE
                
                # Si hay sprites de cazadores, usarlos
                if self.enemigo_sprites['down']:
                    # Obtener dirección y frame de este enemigo
                    direccion = self.enemigo_direcciones.get(idx, 'down')
                    frame = self.enemigo_frames.get(idx, 0)
                    
                    # Dibujar sprite animado del cazador
                    sprite_actual = self.enemigo_sprites[direccion][int(frame) % 3]
                    self.screen.blit(sprite_actual, (enemigo_x, enemigo_y))
                else:
                    # Fallback: círculo rojo
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
            sprite_actual = self.jugador_sprites[self.jugador_direccion][int(self.jugador_frame)]
            self.screen.blit(sprite_actual, (jugador_x, jugador_y))
        else:
            # Fallback: círculo azul si no hay sprites
            pygame.draw.circle(self.screen, (0, 150, 255),
                             (jugador_x + self.CELL_SIZE // 2, 
                              jugador_y + self.CELL_SIZE // 2),
                             self.CELL_SIZE // 3)
        
        # === DIBUJAR BOMBAS ===
        for bomba in self.bombas:
            if not bomba.explotada:
                bomba_x = self.offset_x + bomba.columna * self.CELL_SIZE
                bomba_y = self.offset_y + bomba.fila * self.CELL_SIZE
                
                # Animación de la bomba (6 frames, ciclar)
                tiempo_desde_colocada = self.turnos - bomba.turno_colocada
                frame_bomba = (tiempo_desde_colocada * 2) % len(self.bomba_sprites) if self.bomba_sprites else 0
                
                if self.bomba_sprites:
                    self.screen.blit(self.bomba_sprites[frame_bomba], (bomba_x, bomba_y))
                else:
                    # Fallback: círculo negro con borde rojo
                    pygame.draw.circle(self.screen, (0, 0, 0),
                                     (bomba_x + self.CELL_SIZE // 2, 
                                      bomba_y + self.CELL_SIZE // 2),
                                     self.CELL_SIZE // 3)
                    pygame.draw.circle(self.screen, (255, 0, 0),
                                     (bomba_x + self.CELL_SIZE // 2, 
                                      bomba_y + self.CELL_SIZE // 2),
                                     self.CELL_SIZE // 3, 2)
        
        # === DIBUJAR EXPLOSIONES ===
        for explosion in self.explosiones_activas:
            fila, columna, frame, _ = explosion
            exp_x = self.offset_x + columna * self.CELL_SIZE
            exp_y = self.offset_y + fila * self.CELL_SIZE
            
            if self.explosion_sprites and frame < len(self.explosion_sprites):
                self.screen.blit(self.explosion_sprites[frame], (exp_x, exp_y))
            else:
                # Fallback: círculo naranja brillante
                pygame.draw.circle(self.screen, (255, 150, 0),
                                 (exp_x + self.CELL_SIZE // 2, 
                                  exp_y + self.CELL_SIZE // 2),
                                 self.CELL_SIZE // 2)
    
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
        
        # Barra de energía con animación
        energia_text = self.font_small.render("Energía:", True, self.COLOR_TEXT)
        self.screen.blit(energia_text, (10, 70))
        
        # Animar la barra de energía suavemente
        if self.energia_visual < self.jugador.energia_actual:
            self.energia_visual += self.velocidad_animacion_energia
            if self.energia_visual > self.jugador.energia_actual:
                self.energia_visual = self.jugador.energia_actual
        elif self.energia_visual > self.jugador.energia_actual:
            self.energia_visual -= self.velocidad_animacion_energia
            if self.energia_visual < self.jugador.energia_actual:
                self.energia_visual = self.jugador.energia_actual
        
        # Configuración de la barra
        barra_x = 90
        barra_y = 72
        barra_ancho = 200
        barra_alto = 20
        
        # Fondo de la barra (gris oscuro)
        pygame.draw.rect(self.screen, (40, 40, 40), 
                        (barra_x, barra_y, barra_ancho, barra_alto))
        
        # Calcular porcentaje y ancho de la barra
        porcentaje_energia = self.energia_visual / self.jugador.energia_max
        ancho_energia = int(barra_ancho * porcentaje_energia)
        
        # Color según porcentaje (gradiente)
        if porcentaje_energia > 0.6:
            color_energia = (100, 255, 100)  # Verde
        elif porcentaje_energia > 0.3:
            color_energia = (255, 200, 0)  # Amarillo/naranja
        else:
            color_energia = (255, 100, 100)  # Rojo
        
        # Dibujar barra de energía actual
        if ancho_energia > 0:
            pygame.draw.rect(self.screen, color_energia, 
                            (barra_x, barra_y, ancho_energia, barra_alto))
        
        # Borde de la barra
        pygame.draw.rect(self.screen, (200, 200, 200), 
                        (barra_x, barra_y, barra_ancho, barra_alto), 2)
        
        # Texto con números
        energia_num = self.font_small.render(
            f"{int(self.energia_visual)}/{int(self.jugador.energia_max)}", 
            True, self.COLOR_TEXT
        )
        self.screen.blit(energia_num, (barra_x + barra_ancho + 10, 70))
        
        # Movimientos
        mov_text = self.font_small.render(f"Movimientos: {self.movimientos}", 
                                         True, self.COLOR_TEXT)
        self.screen.blit(mov_text, (self.WIDTH - 200, 45))
        
        # Instrucciones
        inst_text = self.font_small.render("WASD: Mover | ESPACIO: Bomba | ESC: Salir", 
                                          True, (150, 150, 150))
        self.screen.blit(inst_text, (self.WIDTH - 350, 70))
        
        # Mostrar bombas disponibles
        bombas_activas = len([b for b in self.bombas if not b.explotada])
        bombas_text = self.font_small.render(f"Bombas: {bombas_activas}/3", 
                                            True, self.COLOR_TEXT)
        self.screen.blit(bombas_text, (10, 95))
    
    def update(self, keys):
        """
        Actualiza el jugador cada frame (movimiento continuo).
        Similar al ejemplo que proporcionaste.
        """
        if self.juego_terminado:
            return
        
        moviendo = False
        nueva_fila = self.jugador.fila
        nueva_columna = self.jugador.columna
        
        # Detectar movimiento y dirección
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.pos_pixel_y -= self.velocidad_jugador
            self.jugador_direccion = "up"
            moviendo = True
            # Calcular nueva celda basada en posición de píxeles
            nueva_fila = int((self.pos_pixel_y + self.CELL_SIZE // 2) / self.CELL_SIZE)
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.pos_pixel_y += self.velocidad_jugador
            self.jugador_direccion = "down"
            moviendo = True
            nueva_fila = int((self.pos_pixel_y + self.CELL_SIZE // 2) / self.CELL_SIZE)
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.pos_pixel_x -= self.velocidad_jugador
            self.jugador_direccion = "left"
            moviendo = True
            nueva_columna = int((self.pos_pixel_x + self.CELL_SIZE // 2) / self.CELL_SIZE)
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.pos_pixel_x += self.velocidad_jugador
            self.jugador_direccion = "right"
            moviendo = True
            nueva_columna = int((self.pos_pixel_x + self.CELL_SIZE // 2) / self.CELL_SIZE)
        
        # Validar límites y colisiones con muros
        if moviendo:
            # Verificar si la nueva posición es válida
            if (0 <= nueva_fila < ALTO_MAPA and 0 <= nueva_columna < ANCHO_MAPA):
                casilla = self.mapa[nueva_fila][nueva_columna]
                
                # Verificar si el jugador puede pisar esta casilla
                if not casilla.puede_pisar_jugador():
                    # No puede pasar (Muro o Liana), retroceder
                    if keys[pygame.K_w] or keys[pygame.K_UP]:
                        self.pos_pixel_y += self.velocidad_jugador
                    elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
                        self.pos_pixel_y -= self.velocidad_jugador
                    elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
                        self.pos_pixel_x += self.velocidad_jugador
                    elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                        self.pos_pixel_x -= self.velocidad_jugador
                else:
                    # Actualizar celda del jugador si cambió
                    if nueva_fila != self.jugador.fila or nueva_columna != self.jugador.columna:
                        self.jugador.fila = nueva_fila
                        self.jugador.columna = nueva_columna
                        self.movimientos += 1
                        self.turnos += 1
                        
                        # Gastar energía al moverse
                        self.jugador.gastar_energia(self.config.consumo_correr)
                        
                        # Verificar si se quedó sin energía
                        if self.jugador.energia_actual <= 0:
                            self.puntaje_final = 0
                            self.mensaje_final = "PERDISTE: Te quedaste sin energía"
                            self.juego_terminado = True
                            return
                        
                        # Verificar victoria
                        if self.jugador.fila == self.salida[0] and self.jugador.columna == self.salida[1]:
                            self.puntaje_final = calcular_puntaje(self.movimientos, self.config)
                            self.mensaje_final = "¡GANASTE! Has llegado a la salida"
                            self.juego_terminado = True
                            return
                        
                        # Mover enemigos
                        if self.turnos % self.config.vel_enemigos == 0:
                            posiciones_anteriores = [(e.fila, e.columna) for e in self.enemigos]
                            mover_enemigos(self.enemigos, self.jugador, self.mapa)
                            
                            # Actualizar animación de enemigos
                            for idx, enemigo in enumerate(self.enemigos):
                                if enemigo.vivo:
                                    fila_ant, col_ant = posiciones_anteriores[idx]
                                    if enemigo.columna > col_ant:
                                        self.enemigo_direcciones[idx] = 'right'
                                    elif enemigo.columna < col_ant:
                                        self.enemigo_direcciones[idx] = 'left'
                                    elif enemigo.fila > fila_ant:
                                        self.enemigo_direcciones[idx] = 'down'
                                    elif enemigo.fila < fila_ant:
                                        self.enemigo_direcciones[idx] = 'up'
                                    
                                    if (enemigo.fila, enemigo.columna) != (fila_ant, col_ant):
                                        self.enemigo_frames[idx] = (self.enemigo_frames.get(idx, 0) + 1) % 3
                        
                        # Verificar colisión con enemigos
                        if hay_colision_con_enemigo(self.jugador, self.enemigos):
                            self.puntaje_final = 0
                            self.mensaje_final = "PERDISTE: Un cazador te atrapó"
                            self.juego_terminado = True
                            return
                        
                        # Recuperar energía después de moverse
                        recuperar_energia_jugador(self.jugador, self.config)
        
        # Animar sprite mientras se mueve
        if moviendo:
            self.jugador_frame += self.frame_speed
            if self.jugador_frame >= len(self.jugador_sprites[self.jugador_direccion]):
                self.jugador_frame = 0
        else:
            self.jugador_frame = 0  # Frame quieto
        
        # Detectar tecla ESPACIO para colocar bomba (solo una vez al presionar)
        if keys[pygame.K_SPACE] and not self.espacio_presionado:
            self.espacio_presionado = True
            se_coloco, self.ultimo_turno_bomba = colocar_bomba(
                self.bombas,
                self.jugador,
                self.mapa,
                self.turnos,
                self.ultimo_turno_bomba
            )
        elif not keys[pygame.K_SPACE]:
            self.espacio_presionado = False
        
        # Actualizar bombas y explosiones
        self.actualizar_bombas()
    
    def actualizar_bombas(self):
        """
        Revisa todas las bombas activas:
        - Si un enemigo pisa una bomba, explota inmediatamente
        - Si llegaron al tiempo de explosión, las hace explotar
        - Gestiona respawn de enemigos después de 10 turnos
        - Actualiza animaciones de explosiones activas
        """
        # Guardar posiciones de bombas que van a explotar ANTES de procesarlas
        bombas_a_explotar = []
        for bomba in self.bombas:
            if not bomba.explotada:
                # Verificar si debe explotar por tiempo
                if self.turnos - bomba.turno_colocada >= DEMORA_EXPLOSION_BOMBA:
                    bombas_a_explotar.append((bomba.fila, bomba.columna))
                # O si un enemigo está encima
                else:
                    for enemigo in self.enemigos:
                        if enemigo.vivo and enemigo.fila == bomba.fila and enemigo.columna == bomba.columna:
                            if (bomba.fila, bomba.columna) not in bombas_a_explotar:
                                bombas_a_explotar.append((bomba.fila, bomba.columna))
                            break
        
        # Usar la función completa de main.py que maneja todo
        procesar_bombas_y_respawn(
            self.bombas,
            self.enemigos,
            self.jugador,
            self.mapa,
            self.salida,
            self.turnos,
            self.enemigos_por_respawnear
        )
        
        # Agregar explosiones visuales para las bombas que explotaron
        for fila, columna in bombas_a_explotar:
            ya_existe = any(exp[0] == fila and exp[1] == columna 
                          for exp in self.explosiones_activas)
            if not ya_existe:
                self.explosiones_activas.append([fila, columna, 0, 0])
        
        # Actualizar animaciones de explosiones
        explosiones_a_eliminar = []
        for i, explosion in enumerate(self.explosiones_activas):
            explosion[3] += 1  # Incrementar contador de frames
            if explosion[3] >= 2:  # Cada 2 frames, avanzar animación (más rápido)
                explosion[3] = 0
                explosion[2] += 1  # Siguiente frame
                if explosion[2] >= len(self.explosion_sprites):
                    explosiones_a_eliminar.append(i)
        
        # Eliminar explosiones terminadas
        for i in reversed(explosiones_a_eliminar):
            self.explosiones_activas.pop(i)
    
    def manejar_eventos(self, evento):
        """
        Solo maneja eventos de salida ahora.
        El movimiento se hace con keys en update().
        """
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                return False
        return True
                    

    
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
        
        # Dibujar juego normalmente
        self.dibujar_mapa()
        self.dibujar_entidades()
        self.dibujar_ui()
    
    def obtener_resultado(self):
        """
        Devuelve el puntaje final del jugador.
        Lo usa main_menu.py para guardarlo en el sistema de puntajes.
        """
        return self.puntaje_final
