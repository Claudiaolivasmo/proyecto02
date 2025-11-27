import pygame
import sys
from main import (
    generar_mapa, 
    Jugador, 
    crear_enemigos_iniciales,
    mover_jugador,
    mover_enemigos,
    hay_colision_con_enemigo,
    calcular_puntaje,
    recuperar_energia_jugador,
    CONFIGS_DIFICULTAD,
    DIFICULTAD_FACIL,
    ANCHO_MAPA,
    ALTO_MAPA,
    CAMINO,
    LIANA,
    TUNEL,
    MURO,
    Camino,
    Liana,
    Tunel,
    Muro
)


class ModoEscape:
    """
    Clase para el modo Escape con representación gráfica en Pygame.
    Genera el mapa y prepara la estructura para que adjuntes las imágenes.
    """
    
    def __init__(self, screen, jugador_nombre, dificultad=DIFICULTAD_FACIL):
        self.screen = screen
        self.jugador_nombre = jugador_nombre
        self.dificultad = dificultad
        self.config = CONFIGS_DIFICULTAD[dificultad]
        
        # Generar mapa usando la función de main.py
        self.mapa, self.inicio, self.salida = generar_mapa(ANCHO_MAPA, ALTO_MAPA)
        
        # Crear jugador
        fila_ini, col_ini = self.inicio
        self.jugador = Jugador(jugador_nombre, fila_ini, col_ini, self.config)
        
        # Crear enemigos
        self.enemigos = crear_enemigos_iniciales(
            self.mapa, 
            self.config.cant_enemigos, 
            self.jugador, 
            self.salida
        )
        
        # Contadores
        self.movimientos = 0
        self.turnos = 0
        
        # Dimensiones de la pantalla
        self.WIDTH = 800
        self.HEIGHT = 600
        
        # Calcular tamaño de celda
        self.CELL_SIZE = min(
            (self.WIDTH - 100) // ANCHO_MAPA,
            (self.HEIGHT - 150) // ALTO_MAPA
        )
        
        # Offset para centrar el mapa
        self.offset_x = (self.WIDTH - (ANCHO_MAPA * self.CELL_SIZE)) // 2
        self.offset_y = 100
        
        # Estado del juego
        self.juego_terminado = False
        self.mensaje_final = ""
        self.puntaje_final = 0
        
        # Fuentes
        self.font_medium = pygame.font.Font(None, 30)
        self.font_small = pygame.font.Font(None, 24)
        
        # Colores
        self.COLOR_BG = (20, 20, 40)
        self.COLOR_TEXT = (255, 255, 255)
        self.COLOR_SUCCESS = (100, 255, 100)
        self.COLOR_DANGER = (255, 100, 100)
        
        # ============================================
        # AQUÍ VAN TUS IMÁGENES
        # ============================================
        # Cuando tengas las imágenes, reemplaza None con:
        # pygame.image.load("ruta/a/tu/imagen.png")
        # y ajusta el tamaño con:
        # pygame.transform.scale(imagen, (self.CELL_SIZE, self.CELL_SIZE))
        
        self.imagen_camino = None  # Imagen para CAMINO
        self.imagen_liana = None    # Imagen para LIANA
        self.imagen_tunel = None    # Imagen para TÚNEL
        self.imagen_muro = None     # Imagen para MURO
        self.imagen_jugador = None  # Imagen para el jugador
        self.imagen_enemigo = None  # Imagen para enemigos
        self.imagen_salida = None   # Imagen para la salida
        
    def cargar_imagenes(self):
        """
        Método para cargar todas las imágenes del terreno.
        """
        try:
            # Obtener la ruta del directorio donde está este archivo
            import os
            base_dir = os.path.dirname(os.path.abspath(__file__))
            terreno_dir = os.path.join(base_dir, "data", "terreno")
            
            # Cargar imágenes del mapa desde data/terreno
            self.imagen_camino = pygame.image.load(os.path.join(terreno_dir, "camino.png"))
            self.imagen_camino = pygame.transform.scale(self.imagen_camino, (self.CELL_SIZE, self.CELL_SIZE))
            
            self.imagen_liana = pygame.image.load(os.path.join(terreno_dir, "liana3.png"))
            self.imagen_liana = pygame.transform.scale(self.imagen_liana, (self.CELL_SIZE, self.CELL_SIZE))
            
            self.imagen_tunel = pygame.image.load(os.path.join(terreno_dir, "tunel3.png"))
            self.imagen_tunel = pygame.transform.scale(self.imagen_tunel, (self.CELL_SIZE, self.CELL_SIZE))
            
            self.imagen_muro = pygame.image.load(os.path.join(terreno_dir, "muro.png"))
            self.imagen_muro = pygame.transform.scale(self.imagen_muro, (self.CELL_SIZE, self.CELL_SIZE))
            
            print("✓ Imágenes del terreno cargadas correctamente")
            
        except (pygame.error, FileNotFoundError) as e:
            print(f"⚠️ Error al cargar imágenes del terreno: {e}")
            print("Se usarán colores en su lugar.")
        
        # Jugador, enemigo y salida se mantienen como círculos/rectángulos por ahora
        # Puedes agregar sus imágenes más adelante si las tienes
    
    def dibujar_celda(self, fila, col, casilla):
        """
        Dibuja una celda del mapa según su tipo.
        Si no hay imagen, dibuja un rectángulo de color.
        """
        x = self.offset_x + col * self.CELL_SIZE
        y = self.offset_y + fila * self.CELL_SIZE
        
        # Determinar qué dibujar según el tipo de casilla
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
        """Dibuja todo el mapa con todas las casillas"""
        for fila in range(len(self.mapa)):
            for col in range(len(self.mapa[0])):
                self.dibujar_celda(fila, col, self.mapa[fila][col])
    
    def dibujar_entidades(self):
        """Dibuja al jugador, enemigos y la salida"""
        # Dibujar salida
        salida_x = self.offset_x + self.salida[1] * self.CELL_SIZE
        salida_y = self.offset_y + self.salida[0] * self.CELL_SIZE
        
        if self.imagen_salida:
            self.screen.blit(self.imagen_salida, (salida_x, salida_y))
        else:
            pygame.draw.rect(self.screen, (255, 215, 0), 
                           (salida_x, salida_y, self.CELL_SIZE, self.CELL_SIZE))
            texto_salida = self.font_small.render("🚪", True, self.COLOR_TEXT)
            self.screen.blit(texto_salida, (salida_x + 5, salida_y + 5))
        
        # Dibujar enemigos
        for enemigo in self.enemigos:
            if enemigo.vivo:
                enemigo_x = self.offset_x + enemigo.columna * self.CELL_SIZE
                enemigo_y = self.offset_y + enemigo.fila * self.CELL_SIZE
                
                if self.imagen_enemigo:
                    self.screen.blit(self.imagen_enemigo, (enemigo_x, enemigo_y))
                else:
                    pygame.draw.circle(self.screen, (255, 0, 0),
                                     (enemigo_x + self.CELL_SIZE // 2, 
                                      enemigo_y + self.CELL_SIZE // 2),
                                     self.CELL_SIZE // 3)
        
        # Dibujar jugador
        jugador_x = self.offset_x + self.jugador.columna * self.CELL_SIZE
        jugador_y = self.offset_y + self.jugador.fila * self.CELL_SIZE
        
        if self.imagen_jugador:
            self.screen.blit(self.imagen_jugador, (jugador_x, jugador_y))
        else:
            pygame.draw.circle(self.screen, (0, 150, 255),
                             (jugador_x + self.CELL_SIZE // 2, 
                              jugador_y + self.CELL_SIZE // 2),
                             self.CELL_SIZE // 3)
    
    def dibujar_ui(self):
        """Dibuja la información del jugador (energía, movimientos, etc.)"""
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
        """Maneja los eventos de teclado para mover al jugador"""
        if self.juego_terminado:
            return False
        
        if evento.type == pygame.KEYDOWN:
            direccion = None
            
            if evento.key == pygame.K_w or evento.key == pygame.K_UP:
                direccion = "arriba"
            elif evento.key == pygame.K_s or evento.key == pygame.K_DOWN:
                direccion = "abajo"
            elif evento.key == pygame.K_a or evento.key == pygame.K_LEFT:
                direccion = "izquierda"
            elif evento.key == pygame.K_d or evento.key == pygame.K_RIGHT:
                direccion = "derecha"
            elif evento.key == pygame.K_ESCAPE:
                return False  # Salir del modo
            
            if direccion:
                # Intentar mover al jugador
                se_movio = mover_jugador(self.jugador, direccion, self.mapa, self.config, correr=False)
                
                if se_movio:
                    self.movimientos += 1
                    self.turnos += 1
                    
                    # Verificar si llegó a la salida
                    if self.jugador.fila == self.salida[0] and self.jugador.columna == self.salida[1]:
                        self.puntaje_final = calcular_puntaje(self.movimientos, self.config)
                        self.mensaje_final = "¡GANASTE! Has llegado a la salida"
                        self.juego_terminado = True
                        return True
                    
                    # Mover enemigos según velocidad
                    if self.turnos % self.config.vel_enemigos == 0:
                        mover_enemigos(self.enemigos, self.jugador, self.mapa)
                    
                    # Verificar colisión con enemigos
                    if hay_colision_con_enemigo(self.jugador, self.enemigos):
                        self.puntaje_final = 0
                        self.mensaje_final = "PERDISTE: Un cazador te atrapó"
                        self.juego_terminado = True
                        return True
                    
                    # Recuperar energía pasiva
                    recuperar_energia_jugador(self.jugador, self.config)
        
        return True  # Continuar jugando
    
    def dibujar(self):
        """Dibuja toda la escena del juego"""
        self.screen.fill(self.COLOR_BG)
        
        if not self.juego_terminado:
            self.dibujar_mapa()
            self.dibujar_entidades()
            self.dibujar_ui()
        else:
            # Pantalla de fin de juego
            self.dibujar_mapa()
            self.dibujar_entidades()
            
            # Overlay semi-transparente
            overlay = pygame.Surface((self.WIDTH, self.HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            # Mensaje final
            font_grande = pygame.font.Font(None, 60)
            color = self.COLOR_SUCCESS if "GANASTE" in self.mensaje_final else self.COLOR_DANGER
            mensaje = font_grande.render(self.mensaje_final, True, color)
            self.screen.blit(mensaje, (self.WIDTH // 2 - mensaje.get_width() // 2, self.HEIGHT // 2 - 50))
            
            # Puntaje
            puntaje_text = self.font_medium.render(f"Puntaje: {self.puntaje_final}", 
                                                   True, self.COLOR_TEXT)
            self.screen.blit(puntaje_text, 
                           (self.WIDTH // 2 - puntaje_text.get_width() // 2, self.HEIGHT // 2 + 20))
            
            # Instrucción
            inst = self.font_small.render("Presiona ESC para volver al menú", 
                                         True, (200, 200, 200))
            self.screen.blit(inst, (self.WIDTH // 2 - inst.get_width() // 2, self.HEIGHT // 2 + 80))
    
    def obtener_resultado(self):
        """Devuelve el puntaje final para guardar en el registro"""
        return self.puntaje_final
