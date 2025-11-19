'''
===================================
Proyecto 2 - Introducción a la programación

Mainor Martinez
Claudia Olivas

===================================

'''

# # ====== CONSTANTES Y ESTRUCTURA BASE ======


# ====== Tipos de casilla ======
CAMINO = 0
LIANA  = 1
TUNEL  = 2
MURO   = 3

# ====== Modos de juego ======
MODO_ESCAPA  = 1
MODO_CAZADOR = 2

# ====== Dificultades ======
DIFICULTAD_FACIL   = "facil"
DIFICULTAD_MEDIA   = "media"
DIFICULTAD_DIFICIL = "dificil"


class ConfigDificultad:
    def __init__(self, nombre, vel_enemigos, cant_enemigos,
                 energia_max, consumo_correr, recuperacion_pasiva):
        self.nombre = nombre
        self.vel_enemigos = vel_enemigos      # cada cuántos 'ticks' se mueven
        self.cant_enemigos = cant_enemigos
        self.energia_max = energia_max
        self.consumo_correr = consumo_correr  # por movimiento
        self.recuperacion_pasiva = recuperacion_pasiva  # por turno caminando


CONFIGS_DIFICULTAD = {
    DIFICULTAD_FACIL: ConfigDificultad(DIFICULTAD_FACIL,
                                       vel_enemigos=2,
                                       cant_enemigos=2,
                                       energia_max=120,
                                       consumo_correr=4,
                                       recuperacion_pasiva=3),
    DIFICULTAD_MEDIA: ConfigDificultad(DIFICULTAD_MEDIA,
                                       vel_enemigos=1,
                                       cant_enemigos=3,
                                       energia_max=100,
                                       consumo_correr=5,
                                       recuperacion_pasiva=2),
    DIFICULTAD_DIFICIL: ConfigDificultad(DIFICULTAD_DIFICIL,
                                         vel_enemigos=1,
                                         cant_enemigos=4,
                                         energia_max=80,
                                         consumo_correr=6,
                                         recuperacion_pasiva=1),
}
