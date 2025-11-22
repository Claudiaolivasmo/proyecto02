'''
===================================
Proyecto 2 - Introducción a la programación

Mainor Martínez
Claudia Olivas

===================================
'''

import json
import os

RUTA_ARCHIVO_JUGADORES = "jugadores.json"

# ==========================================
# ====== CONSTANTES Y ESTRUCTURA BASE ======
# ==========================================

# Tipos de casilla
CAMINO = 0
LIANA  = 1
TUNEL  = 2
MURO   = 3

# Modos de juego
MODO_ESCAPA  = 1
MODO_CAZADOR = 2

# Dificultades
DIFICULTAD_FACIL   = "facil"
DIFICULTAD_MEDIA   = "media"
DIFICULTAD_DIFICIL = "dificil"


class ConfigDificultad:
    def __init__(self, nombre, vel_enemigos, cant_enemigos,
                 energia_max, consumo_correr, recuperacion_pasiva):
        self.nombre = nombre
        self.vel_enemigos = vel_enemigos
        self.cant_enemigos = cant_enemigos
        self.energia_max = energia_max
        self.consumo_correr = consumo_correr
        self.recuperacion_pasiva = recuperacion_pasiva


CONFIGS_DIFICULTAD = {
    DIFICULTAD_FACIL: ConfigDificultad(
        DIFICULTAD_FACIL,
        vel_enemigos=2,
        cant_enemigos=2,
        energia_max=120,
        consumo_correr=4,
        recuperacion_pasiva=3
    ),
    DIFICULTAD_MEDIA: ConfigDificultad(
        DIFICULTAD_MEDIA,
        vel_enemigos=1,
        cant_enemigos=3,
        energia_max=100,
        consumo_correr=5,
        recuperacion_pasiva=2
    ),
    DIFICULTAD_DIFICIL: ConfigDificultad(
        DIFICULTAD_DIFICIL,
        vel_enemigos=1,
        cant_enemigos=4,
        energia_max=80,
        consumo_correr=6,
        recuperacion_pasiva=1
    ),
}


# ======= REGISTRO DE JUGADORES ============


class RegistroJugadores:
    """
    Clase sencilla para guardar jugadores y sus puntajes.

    Cada jugador tiene:
    - partidas_jugadas
    - mejor_puntaje
    """

    def __init__(self, ruta_archivo=RUTA_ARCHIVO_JUGADORES):
        self.ruta = ruta_archivo
        self.jugadores = {}   # Diccionario con todos los jugadores
        self.cargar_desde_archivo()

    # ---------------------------------------------------
    # Cargar y guardar archivo
    # ---------------------------------------------------
    def cargar_desde_archivo(self):
        if os.path.exists(self.ruta):
            try:
                with open(self.ruta, "r") as archivo:
                    self.jugadores = json.load(archivo)
            except:
                self.jugadores = {}
        else:
            self.jugadores = {}

    def guardar_en_archivo(self):
        with open(self.ruta, "w") as archivo:
            json.dump(self.jugadores, archivo, indent=2)

    # ---------------------------------------------------
    # Funciones de manejo de jugadores
    # ---------------------------------------------------
    def crear_jugador_si_no_existe(self, nombre):
        """
        Si el jugador NO existe en el diccionario, lo crea con valores iniciales.
        """
        if nombre not in self.jugadores:
            self.jugadores[nombre] = {
                "partidas_jugadas": 0,
                "mejor_puntaje": 0
            }
            self.guardar_en_archivo()

    def registrar_partida(self, nombre, puntaje):
        """
        Actualiza las estadísticas del jugador:
        - suma 1 partida jugada
        - actualiza mejor puntaje si el nuevo es mayor
        """
        self.crear_jugador_si_no_existe(nombre)

        jugador = self.jugadores[nombre]
        jugador["partidas_jugadas"] += 1

        if puntaje > jugador["mejor_puntaje"]:
            jugador["mejor_puntaje"] = puntaje

        self.guardar_en_archivo()

    def obtener_datos_jugador(self, nombre):
        """Devuelve el diccionario del jugador o None si no existe."""
        return self.jugadores.get(nombre)

    def obtener_todos_los_jugadores(self):
        """Devuelve una lista con todos los nombres de jugadores registrados."""
        return list(self.jugadores.keys())


# ==========================================
# ============= MENÚS Y MAIN ===============
# ==========================================

def registrar_jugador(registro):
    """
    Pide el nombre del jugador por consola.
    En la versión final, el nombre vendrá desde la interfaz Pygame.
    """
    while True:
        nombre = input("Ingrese su nombre de jugador: ").strip()
        if nombre == "":
            print("El nombre no puede estar vacío. Intente de nuevo.")
        else:
            registro.crear_jugador_si_no_existe(nombre)
            print(f"\nBienvenido(a), {nombre}!\n")
            return nombre


def menu_dificultad():
    """
    Menú de selección de dificultad.
    Devuelve la clave de dificultad (facil, media, dificil).
    """
    print("\nSeleccione la dificultad:")
    print("1. Fácil")
    print("2. Media")
    print("3. Difícil")

    while True:
        opcion = input("Opción: ").strip()
        if opcion == "1":
            return DIFICULTAD_FACIL
        elif opcion == "2":
            return DIFICULTAD_MEDIA
        elif opcion == "3":
            return DIFICULTAD_DIFICIL
        else:
            print("Opción inválida. Intente de nuevo.")


def menu_modo():
    """
    Menú de selección del modo de juego.
    Devuelve MODO_ESCAPA o MODO_CAZADOR.
    """
    print("\nSeleccione el modo de juego:")
    print("1. Modo ESCAPA")
    print("2. Modo CAZADOR")

    while True:
        opcion = input("Opción: ").strip()
        if opcion == "1":
            return MODO_ESCAPA
        elif opcion == "2":
            return MODO_CAZADOR
        else:
            print("Opción inválida. Intente de nuevo.")


def iniciar_modo_escapa(nombre_jugador, clave_dificultad):
    """
    Por ahora solo muestra un mensaje.
    Más adelante se conectará con la lógica del modo ESCAPA y Pygame.
    """
    config = CONFIGS_DIFICULTAD[clave_dificultad]
    print("\n=== MODO ESCAPA ===")
    print(f"Jugador: {nombre_jugador}")
    print(f"Dificultad: {config.nombre}")
    print("TODO: implementar lógica del modo ESCAPA.\n")


def iniciar_modo_cazador(nombre_jugador, clave_dificultad):
    """
    Por ahora solo muestra un mensaje.
    Más adelante se conectará con la lógica del modo CAZADOR y Pygame.
    """
    config = CONFIGS_DIFICULTAD[clave_dificultad]
    print("\n=== MODO CAZADOR ===")
    print(f"Jugador: {nombre_jugador}")
    print(f"Dificultad: {config.nombre}")
    print("TODO: implementar lógica del modo CAZADOR.\n")


def mostrar_historial(registro):
    """
    Muestra todos los jugadores y sus estadísticas básicas.
    """
    print("\n=== Historial de jugadores ===")
    nombres = registro.obtener_todos_los_jugadores()

    if len(nombres) == 0:
        print("Aún no hay jugadores registrados.")
        return

    for nombre in nombres:
        datos = registro.obtener_datos_jugador(nombre)
        print(f"- {nombre}: {datos['partidas_jugadas']} partidas, "
              f"mejor puntaje = {datos['mejor_puntaje']}")


def main():
    registro = RegistroJugadores()

    print("===================================")
    print(" Proyecto 2 - Introducción a la programación")
    print(" Mainor Martínez & Claudia Olivas")
    print("===================================\n")

    # Registro obligatorio del jugador antes de jugar
    nombre_jugador = registrar_jugador(registro)

    while True:
        print("============== MENÚ PRINCIPAL ==============")
        print("1. Jugar")
        print("2. Ver historial de jugadores")
        print("3. Salir")

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            # Elegir dificultad y modo
            clave_dificultad = menu_dificultad()
            modo = menu_modo()

            if modo == MODO_ESCAPA:
                iniciar_modo_escapa(nombre_jugador, clave_dificultad)
            elif modo == MODO_CAZADOR:
                iniciar_modo_cazador(nombre_jugador, clave_dificultad)

        elif opcion == "2":
            mostrar_historial(registro)

        elif opcion == "3":
            print("\nGracias por jugar. ¡Hasta luego!\n")
            break

        else:
            print("Opción inválida. Intente de nuevo.\n")


if __name__ == "__main__":
    main()
