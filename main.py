'''
===================================
Proyecto 2 - Introducción a la programación

Mainor Martínez
Claudia Olivas

===================================
'''
import random
import json
import os

RUTA_ARCHIVO_JUGADORES = "jugadores.json"


# ====== CONSTANTES Y ESTRUCTURA BASE ======


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

# Mapa

ANCHO_MAPA = 15  # columnas
ALTO_MAPA  = 10  # filas



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

# ========== CLASES DE CASILLAS ============

class Casilla: # Clase base para cualquier tipo de casilla del mapa.

    def __init__(self, tipo, simbolo):
        self.tipo = tipo        # CAMINO, LIANA, TUNEL, MURO
        self.simbolo = simbolo  # Cómo se verá en la consola (de momento, sin pygame)

    def puede_pisar_jugador(self): # Por defecto, nadie puede pasar. Se redefine en las clases hijas. (Camino, Liana,etc)

        return False

    def puede_pisar_enemigo(self): # Por defecto, nadie puede pasar. Se redefine en las clases hijas. (Camino, Liana,etc)

        return False


class Camino(Casilla):
    def __init__(self):
        super().__init__(CAMINO, ".")  # punto = camino libre

    def puede_pisar_jugador(self):
        return True

    def puede_pisar_enemigo(self):
        return True


class Liana(Casilla): # Liana: solo los cazadores pueden pasar. Jugador NO puede pasar.

    def __init__(self):
        super().__init__(LIANA, "~")  # ~ para representar lianas

    def puede_pisar_jugador(self):
        return False

    def puede_pisar_enemigo(self):
        return True


class Tunel(Casilla): # Túnel: solo el jugador puede pasar. Enemigos NO pueden pasar.

    def __init__(self):
        super().__init__(TUNEL, "T")

    def puede_pisar_jugador(self):
        return True

    def puede_pisar_enemigo(self):
        return False


class Muro(Casilla): # Muro: nadie puede pasar.

    def __init__(self):
        super().__init__(MURO, "#")  # # para representar muro

    def puede_pisar_jugador(self):
        return False

    def puede_pisar_enemigo(self):
        return False


class Jugador:
    """
    Representa al jugador dentro del mapa.
    Guarda su posición, energía y puntaje.
    """

    def __init__(self, nombre, fila_inicial, columna_inicial, config_dificultad):
        # Identidad
        self.nombre = nombre

        # Posición en el mapa
        self.fila = fila_inicial
        self.columna = columna_inicial

        # Energía (según la dificultad)
        self.energia_max = config_dificultad.energia_max
        self.energia_actual = config_dificultad.energia_max

        # Otros atributos útiles
        self.puntaje = 0
        self.vivo = True

    def gastar_energia(self, cantidad):
        """
        Resta energía al jugador.
        Si la energía baja de 0, se deja en 0.
        """
        self.energia_actual -= cantidad
        if self.energia_actual < 0:
            self.energia_actual = 0

    def recuperar_energia(self, cantidad):
        """
        Suma energía al jugador.
        No puede pasar de energia_max.
        """
        self.energia_actual += cantidad
        if self.energia_actual > self.energia_max:
            self.energia_actual = self.energia_max

    def esta_sin_energia(self):
        """
        Devuelve True si el jugador no tiene energía.
        """
        return self.energia_actual <= 0



def crear_casilla_aleatoria(): # Crea una casilla aleatoria de cualquiera de los 4 tipos.

    tipo_random = random.randint(0, 3)

    if tipo_random == CAMINO:
        return Camino()
    elif tipo_random == LIANA:
        return Liana()
    elif tipo_random == TUNEL:
        return Tunel()
    else:
        return Muro()

def generar_mapa(ancho=ANCHO_MAPA, alto=ALTO_MAPA):
    """
    Genera un mapa con al menos un camino válido desde la columna 0 hasta la última.
    Devuelve:
    - mapa: matriz de casillas
    - inicio: posición del jugador
    - salida: posición final
    """


    # 1. Crear matriz llena de MUROS

    mapa = []

    for f in range(alto):
        fila_nueva = []
        for c in range(ancho):
            fila_nueva.append(Muro())  # todo empieza como muro
        mapa.append(fila_nueva)


    # 2. Elegir la fila donde inicia el jugador

    fila_jugador = random.randint(0, alto - 1)
    columna_jugador = 0

    inicio = (fila_jugador, columna_jugador)

    mapa[fila_jugador][columna_jugador] = Camino()  # primer camino


    # 3. Crear el camino garantizado hasta la última columna

    fila_actual = fila_jugador
    columna_actual = columna_jugador

    while columna_actual < ancho - 1:


        opciones = ["derecha"]

        if fila_actual > 0:
            opciones.append("arriba")
        if fila_actual < alto - 1:
            opciones.append("abajo")

        movimiento = random.choice(opciones)

        if movimiento == "derecha":
            columna_actual += 1
        elif movimiento == "arriba":
            fila_actual -= 1
        elif movimiento == "abajo":
            fila_actual += 1

        # marcar el camino
        mapa[fila_actual][columna_actual] = Camino()

    salida = (fila_actual, columna_actual)


    # 4. Rellenar todo lo que NO es camino con casillas aleatorias

    for f in range(alto):
        for c in range(ancho):

            if isinstance(mapa[f][c], Camino):
                continue

            mapa[f][c] = crear_casilla_aleatoria()

    return mapa, inicio, salida




def mover_jugador(jugador, direccion, mapa, config_dificultad, correr=False):
    """
    Intenta mover al jugador en una dirección.
    - jugador: objeto Jugador
    - direccion: string ("arriba", "abajo", "izquierda", "derecha")
    - mapa: matriz de casillas
    - config_dificultad: para consumo de energía
    - correr: si True, gasta más energía

    Devuelve:
    - True si se movió
    - False si no se movió (por muro, túnel, etc.)
    """

    # Movimientos posibles
    if direccion == "arriba":
        nueva_fila = jugador.fila - 1
        nueva_col = jugador.columna
    elif direccion == "abajo":
        nueva_fila = jugador.fila + 1
        nueva_col = jugador.columna
    elif direccion == "izquierda":
        nueva_fila = jugador.fila
        nueva_col = jugador.columna - 1
    elif direccion == "derecha":
        nueva_fila = jugador.fila
        nueva_col = jugador.columna + 1
    else:
        return False  # dirección no válida

    # Evitar moverse fuera del mapa
    filas = len(mapa)
    columnas = len(mapa[0])

    if nueva_fila < 0 or nueva_fila >= filas:
        return False
    if nueva_col < 0 or nueva_col >= columnas:
        return False

    # Revisar si puede pisar la casilla
    casilla_destino = mapa[nueva_fila][nueva_col]
    if not casilla_destino.puede_pisar_jugador():
        return False  # No puede entrar (muro, liana, etc.)

    # Consumo de energía
    if correr:
        jugador.gastar_energia(config_dificultad.consumo_correr)
    else:
        jugador.gastar_energia(1)  # caminar consume poco

    if jugador.esta_sin_energia():
        print("⚠️ El jugador no tiene energía suficiente para moverse.")
        return False

    # Si todo es válido → actualizar posición
    jugador.fila = nueva_fila
    jugador.columna = nueva_col
    return True


def recuperar_energia_jugador(jugador, config_dificultad):
    jugador.recuperar_energia(config_dificultad.recuperacion_pasiva)



# ======= REGISTRO DE JUGADORES ============

def mostrar_mapa_consola(mapa, jugador, salida):
    """
    Muestra el mapa en consola.
    - 🤠 = jugador (posición actual)
    - 🚪 = salida
    - El resto según el tipo de casilla
    """
    for f in range(len(mapa)):
        linea = ""
        for c in range(len(mapa[0])):

            # Jugador
            if f == jugador.fila and c == jugador.columna:
                linea += "🤠"
                continue

            # Salida
            if (f, c) == salida:
                linea += "🚪"
                continue

            celda = mapa[f][c]

            if isinstance(celda, Camino):
                linea += "  "      # espacio
            elif isinstance(celda, Muro):
                linea += "██"      # bloque
            elif isinstance(celda, Liana):
                linea += "🌿"
            elif isinstance(celda, Tunel):
                linea += "░░"
            else:
                linea += "??"

        print(linea)


def iniciar_modo_escapa(nombre_jugador, clave_dificultad):
    config = CONFIGS_DIFICULTAD[clave_dificultad]
    print("\n=== MODO ESCAPA ===")
    print(f"Jugador: {nombre_jugador}")
    print(f"Dificultad: {config.nombre}")

    mapa, inicio, salida = generar_mapa()
    fila_ini, col_ini = inicio

    jugador = Jugador(nombre_jugador, fila_ini, col_ini, config)

    # Primer dibujo del mapa
    os.system("cls")  # limpia la consola en Windows
    mostrar_mapa_consola(mapa, jugador, salida)
    print(f"\nEnergía: {jugador.energia_actual}/{jugador.energia_max}")
    print("\nUse comandos: w/a/s/d para moverse, x para salir.")

    while True:
        tecla = input("\nMovimiento: ").lower()

        if tecla == "x":
            break

        se_movio = False

        if tecla == "w":
            se_movio = mover_jugador(jugador, "arriba", mapa, config)
        elif tecla == "s":
            se_movio = mover_jugador(jugador, "abajo", mapa, config)
        elif tecla == "a":
            se_movio = mover_jugador(jugador, "izquierda", mapa, config)
        elif tecla == "d":
            se_movio = mover_jugador(jugador, "derecha", mapa, config)
        else:
            print("Tecla no válida. Use w/a/s/d o x para salir.")

        # Si se movió, mostramos el mapa actualizado
        if se_movio:
            os.system("cls")  # limpia la consola
            mostrar_mapa_consola(mapa, jugador, salida)
            print(f"\nEnergía: {jugador.energia_actual}/{jugador.energia_max}")
            print(f"Posición: ({jugador.fila}, {jugador.columna})")

            # ¿Llegó a la salida?
            if jugador.fila == salida[0] and jugador.columna == salida[1]:
                print("\n🎉 ¡Has llegado a la salida del laberinto! 🎉")
                break
        else:
            print("No te puedes mover en esa dirección.")


def iniciar_modo_cazador(nombre_jugador, clave_dificultad):
    config = CONFIGS_DIFICULTAD[clave_dificultad]
    print("\n=== MODO CAZADOR ===")
    print(f"Jugador: {nombre_jugador}")
    print(f"Dificultad: {config.nombre}")

    mapa, inicio, salida = generar_mapa()
    fila_ini, col_ini = inicio
    jugador = Jugador(nombre_jugador, fila_ini, col_ini, config)

    print("\nMapa generado (terminal):\n")
    mostrar_mapa_consola(mapa, jugador, salida)

    print("\nTODO: implementar lógica del modo CAZADOR.\n")


class RegistroJugadores:
    """
    Clase para guardar jugadores y sus puntajes.

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

    def obtener_datos_jugador(self, nombre): # Devuelve el diccionario del jugador o None si no existe.
        return self.jugadores.get(nombre)

    def obtener_todos_los_jugadores(self): # Devuelve una lista con todos los nombres de jugadores registrados.
        return list(self.jugadores.keys())


# ============= MENÚS Y MAIN ===============


def registrar_jugador(registro):

    while True:
        nombre = input("Ingrese su nombre de jugador: ").strip()
        if nombre == "":
            print("El nombre no puede estar vacío. Intente de nuevo.")
        else:
            registro.crear_jugador_si_no_existe(nombre)
            print(f"\nBienvenido(a), {nombre}!\n")
            return nombre


def menu_dificultad(): # Selección de dificultad

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


def menu_modo(): # Selección de modo

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


def mostrar_historial(registro): #     Muestra todos los jugadores y sus estadísticas básicas.

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
