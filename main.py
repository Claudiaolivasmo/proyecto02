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

# ====== BOMBAS (modo Escapa) ======

MAX_BOMBAS_ACTIVAS = 3           # máx. bombas colocadas al mismo tiempo
COOLDOWN_BOMBA_TURNOS = 5        # turnos entre colocar una y otra
DEMORA_EXPLOSION_BOMBA = 3       # turnos que tarda en explotar sola
RANGO_BOMBA = 1                  # radio de explosión (en casillas, estilo cruz sencilla)
RESPAWN_ENEMIGO_TURNOS = 10      # turnos para que el enemigo reviva
BONO_BOMBA = 50                  # puntos por enemigo eliminado con bomba




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


class Enemigo:
    
    """
    Representa a un cazador dentro del mapa.
    Solo puede pisar casillas permitidas para enemigo.
    """

    def __init__(self, fila_inicial, columna_inicial):
        self.fila = fila_inicial
        self.columna = columna_inicial
        self.vivo = True



class Bomba:
    """
    Bomba colocada por el jugador:
    - fila, columna: posición en el mapa
    - turno_colocada: en qué turno se puso
    - rango: cuántas casillas alcanza al explotar
    - explotada: ya explotó o no
    """
    def __init__(self, fila, columna, turno_colocada, rango=RANGO_BOMBA):
        self.fila = fila
        self.columna = columna
        self.turno_colocada = turno_colocada
        self.rango = rango
        self.explotada = False




def mover_enemigo_hacia_jugador(enemigo, jugador, mapa):
    """
    Mueve un enemigo un paso hacia el jugador, si es posible.
    Usa una lógica simple: intenta reducir la distancia en fila/columna.
    """
    mejor_fila = enemigo.fila
    mejor_col = enemigo.columna

    # Distancia actual
    dist_f = jugador.fila - enemigo.fila
    dist_c = jugador.columna - enemigo.columna

    # Lista de posibles movimientos (fila_delta, col_delta)
    movimientos = []

    # Si el jugador está arriba, probamos subir
    if dist_f < 0:
        movimientos.append((-1, 0))
    # Si está abajo, probamos bajar
    if dist_f > 0:
        movimientos.append((1, 0))
    # Si está a la izquierda, probamos izquierda
    if dist_c < 0:
        movimientos.append((0, -1))
    # Si está a la derecha, probamos derecha
    if dist_c > 0:
        movimientos.append((0, 1))

    # Si no hay preferencia (mismo lugar), no se mueve
    if len(movimientos) == 0:
        return

    filas = len(mapa)
    columnas = len(mapa[0])

    # Intentar movimientos en orden (el primero que sirva)
    for delta_f, delta_c in movimientos:
        nueva_f = enemigo.fila + delta_f
        nueva_c = enemigo.columna + delta_c

        # Bordes
        if nueva_f < 0 or nueva_f >= filas:
            continue
        if nueva_c < 0 or nueva_c >= columnas:
            continue

        casilla = mapa[nueva_f][nueva_c]
        if not casilla.puede_pisar_enemigo():
            continue

        # Movimiento válido
        enemigo.fila = nueva_f
        enemigo.columna = nueva_c
        return  # solo un paso


def mover_enemigo_huyendo_jugador(enemigo, jugador, mapa):
    """
    Mueve un enemigo un paso alejándose del jugador, si es posible.
    Intenta aumentar la distancia en fila/columna.
    """
    # Diferencias actuales
    dist_f = jugador.fila - enemigo.fila
    dist_c = jugador.columna - enemigo.columna

    movimientos = []

    # Si el jugador está arriba (dist_f < 0), el enemigo intenta ir abajo
    if dist_f < 0:
        movimientos.append((1, 0))
    # Si el jugador está abajo (dist_f > 0), intenta ir arriba
    if dist_f > 0:
        movimientos.append((-1, 0))
    # Si el jugador está a la izquierda (dist_c < 0), intenta ir derecha
    if dist_c < 0:
        movimientos.append((0, 1))
    # Si el jugador está a la derecha (dist_c > 0), intenta ir izquierda
    if dist_c > 0:
        movimientos.append((0, -1))

    # Si jugador y enemigo están en la misma fila y columna (raro), no hay preferencia
    if len(movimientos) == 0:
        return

    filas = len(mapa)
    columnas = len(mapa[0])

    for delta_f, delta_c in movimientos:
        nueva_f = enemigo.fila + delta_f
        nueva_c = enemigo.columna + delta_c

        if nueva_f < 0 or nueva_f >= filas:
            continue
        if nueva_c < 0 or nueva_c >= columnas:
            continue

        casilla = mapa[nueva_f][nueva_c]
        if not casilla.puede_pisar_enemigo():
            continue

        enemigo.fila = nueva_f
        enemigo.columna = nueva_c
        return  # solo un paso


def mover_enemigos_huyendo(enemigos, jugador, mapa):
    """
    Mueve todos los enemigos un paso alejándose del jugador.
    """
    for enemigo in enemigos:
        if enemigo.vivo:
            mover_enemigo_huyendo_jugador(enemigo, jugador, mapa)



def crear_enemigos_iniciales(mapa, cantidad, jugador, salida):
    """
    Crea 'cantidad' enemigos en posiciones aleatorias del mapa.
    No los coloca encima del jugador ni de la salida.
    Solo en casillas donde puede pisar enemigo.
    """
    enemigos = []

    filas = len(mapa)
    columnas = len(mapa[0])

    while len(enemigos) < cantidad:
        fila = random.randint(0, filas - 1)
        col = random.randint(0, columnas - 1)

        # Evitar jugador y salida
        if fila == jugador.fila and col == jugador.columna:
            continue
        if (fila, col) == salida:
            continue

        casilla = mapa[fila][col]
        if not casilla.puede_pisar_enemigo():
            continue

        enemigos.append(Enemigo(fila, col))

    return enemigos


def mover_enemigos(enemigos, jugador, mapa):
    """
    Mueve todos los enemigos un paso hacia el jugador.
    """
    for enemigo in enemigos:
        if enemigo.vivo:
            mover_enemigo_hacia_jugador(enemigo, jugador, mapa)

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

def hay_colision_con_enemigo(jugador, enemigos):
    """
    Devuelve True si algún enemigo está en la misma casilla que el jugador.
    """
    for enemigo in enemigos:
        if enemigo.vivo and enemigo.fila == jugador.fila and enemigo.columna == jugador.columna:
            return True
    return False

def colocar_bomba(bombas, jugador, mapa, turnos, ultimo_turno_bomba):
    """
    Intenta colocar una bomba en la posición actual del jugador.
    Reglas:
    - Máx. MAX_BOMBAS_ACTIVAS activas.
    - Cooldown de COOLDOWN_BOMBA_TURNOS turnos.
    Devuelve (se_coloco, nuevo_ultimo_turno_bomba).
    """
    # Límite de bombas
    if len([b for b in bombas if not b.explotada]) >= MAX_BOMBAS_ACTIVAS:
        print(f"⚠️ Ya tienes {MAX_BOMBAS_ACTIVAS} bombas activas.")
        return False, ultimo_turno_bomba

    # Cooldown
    if turnos - ultimo_turno_bomba < COOLDOWN_BOMBA_TURNOS:
        faltan = COOLDOWN_BOMBA_TURNOS - (turnos - ultimo_turno_bomba)
        print(f"⚠️ Debes esperar {faltan} turnos más para colocar otra bomba.")
        return False, ultimo_turno_bomba

    f = jugador.fila
    c = jugador.columna

    # No permitir doble bomba en la misma casilla
    for b in bombas:
        if not b.explotada and b.fila == f and b.columna == c:
            print("⚠️ Ya hay una bomba en esta casilla.")
            return False, ultimo_turno_bomba

    # La casilla ya es válida porque el jugador está parado ahí,
    # así que simplemente creamos la bomba.
    nueva_bomba = Bomba(f, c, turnos)
    bombas.append(nueva_bomba)
    print("💣 Has colocado una bomba.")
    return True, turnos


def explotar_bomba(bomba, enemigos, jugador, mapa, salida,
                   turnos, enemigos_por_respawnear):
    """
    Hace explotar una bomba:
    - Mata a enemigos en un rango en cruz.
    - Suma BONO_BOMBA por cada enemigo eliminado.
    - Agenda respawn para más adelante.
    """
    bomba.explotada = True
    print("💥 ¡Bomba explotó!")

    filas = len(mapa)
    columnas = len(mapa[0])

    # Celda central (donde está la bomba)
    posiciones_afectadas = [(bomba.fila, bomba.columna)]

    # Estilo cruz (como tu ejemplo de Pygame)
    direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for df, dc in direcciones:
        for i in range(1, bomba.rango + 1):
            nf = bomba.fila + df * i
            nc = bomba.columna + dc * i

            if nf < 0 or nf >= filas or nc < 0 or nc >= columnas:
                break  # fuera del mapa

            casilla = mapa[nf][nc]
            # Si es muro, la explosión no sigue más en esa dirección
            if isinstance(casilla, Muro):
                break

            posiciones_afectadas.append((nf, nc))

    # Matar enemigos que estén en posiciones afectadas
    for enemigo in enemigos:
        if not enemigo.vivo:
            continue
        if (enemigo.fila, enemigo.columna) in posiciones_afectadas:
            enemigo.vivo = False
            jugador.puntaje += BONO_BOMBA
            print(f"👹 Enemigo eliminado por bomba. +{BONO_BOMBA} puntos.")
            enemigos_por_respawnear.append({
                "enemigo": enemigo,
                "turno_muerte": turnos
            })


def procesar_bombas_y_respawn(bombas, enemigos, jugador, mapa, salida,
                              turnos, enemigos_por_respawnear):
    """
    - Si un enemigo se para encima de una bomba NO explotada → explota inmediato.
    - Si pasa el tiempo DEMORA_EXPLOSION_BOMBA → explota sola.
    - Gestiona respawn de enemigos después de RESPAWN_ENEMIGO_TURNOS.
    """

    # 1) Explosión inmediata si un enemigo pisa la bomba
    for bomba in bombas:
        if bomba.explotada:
            continue
        for enemigo in enemigos:
            if enemigo.vivo and enemigo.fila == bomba.fila and enemigo.columna == bomba.columna:
                explotar_bomba(bomba, enemigos, jugador, mapa, salida,
                               turnos, enemigos_por_respawnear)
                break  # ya explotó, no revisamos otros enemigos para esta bomba

    # 2) Explosión por tiempo (bomba "programada")
    for bomba in bombas:
        if bomba.explotada:
            continue
        if turnos - bomba.turno_colocada >= DEMORA_EXPLOSION_BOMBA:
            explotar_bomba(bomba, enemigos, jugador, mapa, salida,
                           turnos, enemigos_por_respawnear)

    # 3) Limpiar bombas explotadas (ya no se dibujan)
    bombas[:] = [b for b in bombas if not b.explotada]

    # 4) Respawn de enemigos
    restantes = []
    for info in enemigos_por_respawnear:
        enemigo = info["enemigo"]
        turno_muerte = info["turno_muerte"]

        if turnos - turno_muerte >= RESPAWN_ENEMIGO_TURNOS:
            # Respawnearlo en una casilla válida para enemigo
            filas = len(mapa)
            columnas = len(mapa[0])
            while True:
                f = random.randint(0, filas - 1)
                c = random.randint(0, columnas - 1)
                if (f, c) == (jugador.fila, jugador.columna):
                    continue
                if (f, c) == salida:
                    continue
                casilla = mapa[f][c]
                if not casilla.puede_pisar_enemigo():
                    continue
                enemigo.fila = f
                enemigo.columna = c
                enemigo.vivo = True
                print("👹 Un enemigo ha reaparecido en el mapa.")
                break
        else:
            restantes.append(info)

    enemigos_por_respawnear[:] = restantes


def calcular_puntaje(movimientos, config_dificultad):
    """
    Calcula el puntaje:
    - Base: 1000 - (movimientos * 10)  (mínimo 0)
    - Multiplicador según dificultad (más enemigos / velocidad => más puntos)
    """
    base = 1000 - movimientos * 10
    if base < 0:
        base = 0

    # Multiplicador por dificultad
    # Puedes ajustar estos valores si quieres
    if config_dificultad.nombre == DIFICULTAD_FACIL:
        mult_dif = 1.0
    elif config_dificultad.nombre == DIFICULTAD_MEDIA:
        mult_dif = 1.5
    else:  # dificil
        mult_dif = 2.0

    # Multiplicador adicional por cant_enemigos y "velocidad"
    extra = 1.0
    extra += (config_dificultad.cant_enemigos - 2) * 0.1  # más enemigos => más puntos
    extra += (1.0 / config_dificultad.vel_enemigos) * 0.2  # cuanto más seguidos se muevan, más recompensa

    puntaje = int(base * mult_dif * extra)
    if puntaje < 0:
        puntaje = 0

    return puntaje

def mostrar_mapa_consola(mapa, jugador, salida, enemigos, bombas=None):
    """
    Muestra el mapa en consola.
    - 🤠 = jugador
    - 👹 = enemigo
    - 🚪 = salida
    - 💣 = bomba
    """
    if bombas is None:
        bombas = []


        for f in range(len(mapa)):
            linea = ""
            for c in range(len(mapa[0])):

                # Jugador
                if f == jugador.fila and c == jugador.columna:
                    linea += "🤠"
                    continue

                # Enemigo (si hay alguno en esta casilla)
                hay_enemigo = False
                for enemigo in enemigos:
                    if enemigo.vivo and enemigo.fila == f and enemigo.columna == c:
                        linea += "👹"
                        hay_enemigo = True
                        break
                if hay_enemigo:
                    continue

                # Salida
                if (f, c) == salida:
                    linea += "🚪"
                    continue

                # Bomba (si hay)
                hay_bomba = False
                for bomba in bombas:
                    if (not bomba.explotada) and bomba.fila == f and bomba.columna == c:
                        linea += "💣"
                        hay_bomba = True
                        break
                if hay_bomba:
                    continue

                # Terreno
                celda = mapa[f][c]

                if isinstance(celda, Camino):
                    linea += "  "      # espacio
                elif isinstance(celda, Muro):
                    linea += "██"
                elif isinstance(celda, Liana):
                    linea += "🌿"
                elif isinstance(celda, Tunel):
                    linea += "░░"
                else:
                    linea += "??"

            print(linea)

# ======= REGISTRO DE JUGADORES ============

def iniciar_modo_escapa(nombre_jugador, clave_dificultad, registro):
    config = CONFIGS_DIFICULTAD[clave_dificultad]
    print("\n=== MODO ESCAPA ===")
    print(f"Jugador: {nombre_jugador}")
    print(f"Dificultad: {config.nombre}")

    mapa, inicio, salida = generar_mapa()
    fila_ini, col_ini = inicio

    jugador = Jugador(nombre_jugador, fila_ini, col_ini, config)

    # Crear enemigos iniciales
    enemigos = crear_enemigos_iniciales(mapa, config.cant_enemigos, jugador, salida)

    movimientos_jugador = 0  # cuenta de movimientos
    turnos = 0               # para velocidad de enemigos

        # Bombas y respawn de enemigos
    bombas = []  # lista de objetos Bomba
    enemigos_por_respawnear = []  # lista de dicts {"enemigo": obj, "turno_muerte": int}
    ultimo_turno_bomba = -COOLDOWN_BOMBA_TURNOS  # para poder poner una al inicio si quieres


    os.system("cls")  # limpiar pantalla en Windows
    mostrar_mapa_consola(mapa, jugador, salida, enemigos, bombas)
    print(f"\nEnergía: {jugador.energia_actual}/{jugador.energia_max}")
    print("\nUse comandos: w/a/s/d para moverse, b para bomba, x para salir.")


    while True:
        tecla = input("\nMovimiento: ").lower()

        if tecla == "x":
            print("Has salido del modo ESCAPA.")
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
        elif tecla == "b":
            # Colocar bomba en la casilla actual
            se_coloco, ultimo_turno_bomba = colocar_bomba(
                bombas, jugador, mapa, turnos, ultimo_turno_bomba
            )
            # Poner bomba NO cuenta como movimiento para puntaje ni avance de turnos
            # Si quisieras que sí cuente como "tiempo", podríamos incrementar turnos aquí.
            continue
        else:
            print("Tecla no válida. Use w/a/s/d, b para bomba o x para salir.")
            continue  # no se mueve ni coloca bomba

        if not se_movio:
            continue  # no hay turno si no se movió

        movimientos_jugador += 1
        turnos += 1


        # ¿Llegó a la salida antes que lo atrapen?
        if jugador.fila == salida[0] and jugador.columna == salida[1]:
            os.system("cls")
            mostrar_mapa_consola(mapa, jugador, salida, enemigos)
            print("\n🎉 ¡Has llegado a la salida del laberinto! 🎉")
            puntaje = calcular_puntaje(movimientos_jugador, config)
            print(f"\nTu puntaje: {puntaje}")
            registro.registrar_partida(nombre_jugador, puntaje, MODO_ESCAPA)
            break

        # Mover enemigos según la "velocidad" de la dificultad
        # En fácil (2) se mueven cada 2 turnos, en media/difícil (1) cada turno
        if turnos % config.vel_enemigos == 0:
            mover_enemigos(enemigos, jugador, mapa)

        # Procesar bombas (explosión por tiempo o si las pisan) y respawn de enemigos
        procesar_bombas_y_respawn(
            bombas, enemigos, jugador, mapa, salida,
            turnos, enemigos_por_respawnear
        )


        # ¿Algún enemigo lo atrapó?
        if hay_colision_con_enemigo(jugador, enemigos):
            os.system("cls")
            mostrar_mapa_consola(mapa, jugador, salida, enemigos)
            print("\n💀 Un cazador te ha atrapado. Has perdido. 💀")
            puntaje = 0  # puedes ajustar si quieres otra lógica
            print(f"\nTu puntaje: {puntaje}")
            registro.registrar_partida(nombre_jugador, puntaje, MODO_ESCAPA)
            break

        os.system("cls")
        mostrar_mapa_consola(mapa, jugador, salida, enemigos, bombas)
        print(f"\nEnergía: {jugador.energia_actual}/{jugador.energia_max}")
        print(f"Movimientos: {movimientos_jugador}")
        print(f"Bombas activas: {len(bombas)}")



def iniciar_modo_cazador(nombre_jugador, clave_dificultad, registro):
    config = CONFIGS_DIFICULTAD[clave_dificultad]
    print("\n=== MODO CAZADOR ===")
    print(f"Jugador: {nombre_jugador}")
    print(f"Dificultad: {config.nombre}")

    # Generar mapa y jugador
    mapa, inicio, salida = generar_mapa()
    fila_ini, col_ini = inicio
    jugador = Jugador(nombre_jugador, fila_ini, col_ini, config)

    # Crear las "presas" iniciales (usamos la misma función de enemigos)
    enemigos = crear_enemigos_iniciales(mapa, config.cant_enemigos, jugador, salida)

    movimientos_jugador = 0
    turnos = 0
    atrapados = 0
    total_enemigos = len(enemigos)

    os.system("cls")
    mostrar_mapa_consola(mapa, jugador, salida, enemigos)
    print(f"\nEnergía: {jugador.energia_actual}/{jugador.energia_max}")
    print(f"Enemigos restantes: {total_enemigos - atrapados}")
    print("\nUse comandos: w/a/s/d para moverse, x para salir.")

    while True:
        tecla = input("\nMovimiento: ").lower()

        if tecla == "x":
            print("Has salido del modo CAZADOR.")
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

        if not se_movio:
            continue

        movimientos_jugador += 1
        turnos += 1

        # 1) Revisar si el jugador atrapó a algún enemigo
        for enemigo in enemigos:
            if enemigo.vivo and enemigo.fila == jugador.fila and enemigo.columna == jugador.columna:
                enemigo.vivo = False
                atrapados += 1
                print("🎯 ¡Has atrapado a un enemigo!")

        # 2) ¿Ya atrapó a todos?
        if atrapados == total_enemigos:
            os.system("cls")
            mostrar_mapa_consola(mapa, jugador, salida, enemigos)
            print("\n🎉 ¡Has atrapado a todos los enemigos! 🎉")
            puntaje = calcular_puntaje(movimientos_jugador, config)
            print(f"\nTu puntaje en modo CAZADOR: {puntaje}")
            registro.registrar_partida(nombre_jugador, puntaje, MODO_CAZADOR)
            break

        # 3) Mover enemigos huyendo, según velocidad configurada
        if turnos % config.vel_enemigos == 0:
            mover_enemigos_huyendo(enemigos, jugador, mapa)

        # 4) Recuperar algo de energía (si quieres que funcione igual que en escapa)
        recuperar_energia_jugador(jugador, config)

        # 5) Si el jugador se queda sin energía, pierde
        if jugador.esta_sin_energia():
            os.system("cls")
            mostrar_mapa_consola(mapa, jugador, salida, enemigos)
            print("\n💀 Te has quedado sin energía. Has perdido en modo CAZADOR. 💀")
            puntaje = 0
            print(f"\nTu puntaje: {puntaje}")
            registro.registrar_partida(nombre_jugador, puntaje, MODO_CAZADOR)
            break

        # 6) Redibujar el mapa
        os.system("cls")
        mostrar_mapa_consola(mapa, jugador, salida, enemigos)
        print(f"\nEnergía: {jugador.energia_actual}/{jugador.energia_max}")
        print(f"Movimientos: {movimientos_jugador}")
        print(f"Enemigos restantes: {total_enemigos - atrapados}")

class RegistroJugadores:
    """
    Clase para guardar jugadores y sus puntajes.

    Cada jugador tiene:
    - partidas_jugadas
    - mejor_puntaje_escapa
    - mejor_puntaje_cazador
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
        Separamos los mejores puntajes por modo de juego.
        """
        if nombre not in self.jugadores:
            self.jugadores[nombre] = {
                "partidas_jugadas": 0,
                "mejor_puntaje_escapa": 0,
                "mejor_puntaje_cazador": 0
            }
            self.guardar_en_archivo()

    def registrar_partida(self, nombre, puntaje, modo):
        """
        Actualiza las estadísticas del jugador:
        - suma 1 partida jugada
        - actualiza mejor puntaje si el nuevo es mayor
        """
        self.crear_jugador_si_no_existe(nombre)

        jugador = self.jugadores[nombre]

        # Asegurar que existan todas las llaves, por si el JSON es viejo
        if "partidas_jugadas" not in jugador:
            jugador["partidas_jugadas"] = 0
        if "mejor_puntaje_escapa" not in jugador:
            jugador["mejor_puntaje_escapa"] = 0
        if "mejor_puntaje_cazador" not in jugador:
            jugador["mejor_puntaje_cazador"] = 0

        jugador["partidas_jugadas"] += 1

        if modo == MODO_ESCAPA:
            if puntaje > jugador["mejor_puntaje_escapa"]:
                jugador["mejor_puntaje_escapa"] = puntaje
        elif modo == MODO_CAZADOR:
            if puntaje > jugador["mejor_puntaje_cazador"]:
                jugador["mejor_puntaje_cazador"] = puntaje

        self.guardar_en_archivo()

    def obtener_datos_jugador(self, nombre):
        """Devuelve el diccionario del jugador o None si no existe."""
        return self.jugadores.get(nombre)

    def obtener_todos_los_jugadores(self):
        """Devuelve una lista con todos los nombres de jugadores registrados."""
        return list(self.jugadores.keys())

    def obtener_top5_por_modo(self, modo):
        """
        Devuelve una lista de tuplas (nombre, puntaje) ordenada de mayor a menor,
        con máximo 5 jugadores, según el modo.
        """
        jugadores_puntajes = []

        for nombre, datos in self.jugadores.items():
            if modo == MODO_ESCAPA:
                puntaje = datos.get("mejor_puntaje_escapa", 0)
            elif modo == MODO_CAZADOR:
                puntaje = datos.get("mejor_puntaje_cazador", 0)
            else:
                puntaje = 0

            jugadores_puntajes.append((nombre, puntaje))

        # Ordenar de mayor a menor puntaje
        jugadores_puntajes.sort(key=lambda x: x[1], reverse=True)

        # Devolver solo los primeros 5
        return jugadores_puntajes[:5]




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
        print(
            f"- {nombre}: {datos['partidas_jugadas']} partidas, "
            f"mejor ESCAPA = {datos['mejor_puntaje_escapa']}, "
            f"mejor CAZADOR = {datos['mejor_puntaje_cazador']}"
        )

def mostrar_top5_escapa(registro):
    print("\n=== TOP 5 - Modo ESCAPA ===")
    top = registro.obtener_top5_por_modo(MODO_ESCAPA)

    if len(top) == 0:
        print("Aún no hay puntajes registrados en este modo.")
        return

    posicion = 1
    for nombre, puntaje in top:
        print(f"{posicion}. {nombre}: {puntaje} puntos")
        posicion += 1


def mostrar_top5_cazador(registro):
    print("\n=== TOP 5 - Modo CAZADOR ===")
    top = registro.obtener_top5_por_modo(MODO_CAZADOR)

    if len(top) == 0:
        print("Aún no hay puntajes registrados en este modo.")
        return

    posicion = 1
    for nombre, puntaje in top:
        print(f"{posicion}. {nombre}: {puntaje} puntos")
        posicion += 1


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
        print("3. Ver Top 5 ESCAPA")
        print("4. Ver Top 5 CAZADOR")
        print("5. Salir")

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            # Elegir dificultad y modo
            clave_dificultad = menu_dificultad()
            modo = menu_modo()

            if modo == MODO_ESCAPA:
                iniciar_modo_escapa(nombre_jugador, clave_dificultad, registro)
            elif modo == MODO_CAZADOR:
                iniciar_modo_cazador(nombre_jugador, clave_dificultad, registro)

        elif opcion == "2":
            mostrar_historial(registro)

        elif opcion == "3":
            mostrar_top5_escapa(registro)

        elif opcion == "4":
            mostrar_top5_cazador(registro)

        elif opcion == "5":
            print("\nGracias por jugar. ¡Hasta luego!\n")
            break

        else:
            print("Opción inválida. Intente de nuevo.\n")



if __name__ == "__main__":
    main()
