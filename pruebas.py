import os
import random

# ===============================
#  CONSTANTES BÁSICAS
# ===============================

CAMINO = 0
MURO   = 3

PUNTOS_ATRAPAR_ENEMIGO = 100

# ===============================
#  CLASES DE CASILLAS
# ===============================

class Casilla:
    def __init__(self, tipo, simbolo):
        self.tipo = tipo
        self.simbolo = simbolo

    def puede_pisar_jugador(self):
        return False

    def puede_pisar_enemigo(self):
        return False


class Camino(Casilla):
    def __init__(self):
        super().__init__(CAMINO, ".")

    def puede_pisar_jugador(self):
        return True

    def puede_pisar_enemigo(self):
        return True


class Muro(Casilla):
    def __init__(self):
        super().__init__(MURO, "#")

    def puede_pisar_jugador(self):
        return False

    def puede_pisar_enemigo(self):
        return False


# ===============================
#  JUGADOR Y ENEMIGO
# ===============================

class Jugador:
    def __init__(self, nombre, fila_inicial, columna_inicial):
        self.nombre = nombre
        self.fila = fila_inicial
        self.columna = columna_inicial
        self.puntaje = 0


class Enemigo:
    def __init__(self, fila_inicial, columna_inicial):
        self.fila = fila_inicial
        self.columna = columna_inicial
        self.vivo = True


# ===============================
#  MAPA FIJO SENCILLO
# ===============================

def crear_mapa_simple():
    """
    Crea un mapa pequeño y fijo (sin laberinto aleatorio)
    para poder reproducir fácilmente el error.
    """

    # 15 columnas x 7 filas
    layout = [
        "###############",
        "#.............#",
        "#.#####.#####.#",
        "#.............#",
        "#.#####.#####.#",
        "#.............#",
        "###############",
    ]
    # fila 0..6, col 0..14

    mapa = []
    for fila_str in layout:
        fila_casillas = []
        for ch in fila_str:
            if ch == "#":
                fila_casillas.append(Muro())
            else:
                fila_casillas.append(Camino())
        mapa.append(fila_casillas)

    # Definimos posiciones de prueba:
    # Jugador: fila 3, col 2
    inicio = (3, 2)
    # Salida: fila 3, col 13 (a la derecha)
    salida = (3, 13)

    # Camino principal aproximado (solo para mover enemigo hacia la salida)
    camino_principal = []
    for c in range(1, 14):
        camino_principal.append((3, c))

    return mapa, inicio, salida, camino_principal


# ===============================
#  DIBUJAR MAPA
# ===============================

def mostrar_mapa_consola(mapa, jugador, salida, enemigos):
    filas = len(mapa)
    columnas = len(mapa[0])

    for f in range(filas):
        linea = ""
        for c in range(columnas):

            # Jugador
            if f == jugador.fila and c == jugador.columna:
                linea += "🤠"
                continue

            # Enemigos
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

            # Terreno
            celda = mapa[f][c]
            if isinstance(celda, Camino):
                linea += "  "
            elif isinstance(celda, Muro):
                linea += "██"
            else:
                linea += "??"
        print(linea)


# ===============================
#  MOVIMIENTO
# ===============================

def mover_jugador(jugador, direccion, mapa):
    if direccion == "arriba":
        nf, nc = jugador.fila - 1, jugador.columna
    elif direccion == "abajo":
        nf, nc = jugador.fila + 1, jugador.columna
    elif direccion == "izquierda":
        nf, nc = jugador.fila, jugador.columna - 1
    elif direccion == "derecha":
        nf, nc = jugador.fila, jugador.columna + 1
    else:
        return False

    filas = len(mapa)
    columnas = len(mapa[0])

    if not (0 <= nf < filas and 0 <= nc < columnas):
        return False

    if not mapa[nf][nc].puede_pisar_jugador():
        return False

    jugador.fila = nf
    jugador.columna = nc
    return True


def mover_enemigos_cazador(enemigos, mapa, salida):
    filas = len(mapa)
    columnas = len(mapa[0])
    fila_salida, col_salida = salida

    for enemigo in enemigos:
        if not enemigo.vivo:
            continue

        direcciones_base = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        current_dist = abs(enemigo.fila - fila_salida) + abs(enemigo.columna - col_salida)

        movimientos_prioritarios = []
        movimientos_secundarios = []

        for df, dc in direcciones_base:
            nf = enemigo.fila + df
            nc = enemigo.columna + dc

            if 0 <= nf < filas and 0 <= nc < columnas and mapa[nf][nc].puede_pisar_enemigo():
                nueva_dist = abs(nf - fila_salida) + abs(nc - col_salida)
                if nueva_dist < current_dist:
                    movimientos_prioritarios.append((df, dc))
                elif nueva_dist == current_dist:
                    movimientos_secundarios.append((df, dc))

        se_movio = False

        random.shuffle(movimientos_prioritarios)
        for df, dc in movimientos_prioritarios:
            enemigo.fila += df
            enemigo.columna += dc
            se_movio = True
            break

        if se_movio:
            continue

        random.shuffle(movimientos_secundarios)
        for df, dc in movimientos_secundarios:
            enemigo.fila += df
            enemigo.columna += dc
            se_movio = True
            break

        if not se_movio:
            random.shuffle(direcciones_base)
            for df, dc in direcciones_base:
                nf = enemigo.fila + df
                nc = enemigo.columna + dc
                if 0 <= nf < filas and 0 <= nc < columnas and mapa[nf][nc].puede_pisar_enemigo():
                    enemigo.fila = nf
                    enemigo.columna = nc
                    break


# ===============================
#  CHEQUEO DE CAPTURA
# ===============================

def hay_captura(jugador, enemigos):
    """
    Devuelve True si algún enemigo vivo está EXACTAMENTE
    en la misma casilla que el jugador.
    """
    for enemigo in enemigos:
        if enemigo.vivo and enemigo.fila == jugador.fila and enemigo.columna == jugador.columna:
            return enemigo
    return None


# ===============================
#  MODO CAZADOR SIMPLE
# ===============================

def iniciar_modo_cazador_simple():
    print("\n=== MODO CAZADOR (VERSIÓN SIMPLE) ===")

    mapa, inicio, salida, camino_principal = crear_mapa_simple()
    fila_ini, col_ini = inicio

    jugador = Jugador("Tester", fila_ini, col_ini)

    # Creamos 1 enemigo en el camino, cerca de la salida
    enemigos = [Enemigo(3, 10)]  # misma fila que el jugador, más a la derecha

    movimientos_jugador = 0

    while True:
        os.system("cls" if os.name == "nt" else "clear")
        mostrar_mapa_consola(mapa, jugador, salida, enemigos)

        print(f"\nPosición jugador: ({jugador.fila}, {jugador.columna})")
        for i, e in enumerate(enemigos):
            print(f"Enemigo {i}: ({e.fila}, {e.columna}) - {'vivo' if e.vivo else 'muerto'}")

        print(f"\nPuntaje: {jugador.puntaje}")
        print("Use w/a/s/d para moverse, x para salir.")

        tecla = input("\nMovimiento: ").strip().lower()

        if tecla == "x":
            print("Saliendo del modo cazador simple.")
            break

        direccion = None
        if tecla == "w":
            direccion = "arriba"
        elif tecla == "s":
            direccion = "abajo"
        elif tecla == "a":
            direccion = "izquierda"
        elif tecla == "d":
            direccion = "derecha"
        else:
            print("Tecla no válida.")
            continue

        se_movio = mover_jugador(jugador, direccion, mapa)
        if not se_movio:
            print("No puedes moverte en esa dirección.")
            continue

        movimientos_jugador += 1

        # 1) Revisar captura inmediatamente después de mover al jugador
        enemigo_capturado = hay_captura(jugador, enemigos)
        if enemigo_capturado is not None:
            enemigo_capturado.vivo = False
            jugador.puntaje += PUNTOS_ATRAPAR_ENEMIGO
            print("\n🎯 ¡Has atrapado a un cazador! (justo después de moverte)")
            input("Presiona Enter para continuar...")
            # En esta versión simple no hay respawn ni nada más
            continue

        # 2) Mover enemigos hacia la salida
        mover_enemigos_cazador(enemigos, mapa, salida)

        # 3) Revisar captura nuevamente (por si el enemigo se mueve hacia ti)
        enemigo_capturado = hay_captura(jugador, enemigos)
        if enemigo_capturado is not None:
            enemigo_capturado.vivo = False
            jugador.puntaje += PUNTOS_ATRAPAR_ENEMIGO
            print("\n🎯 ¡Has atrapado a un cazador! (después de que el cazador se movió)")
            input("Presiona Enter para continuar...")
            continue

        # 4) Condición de victoria: todos muertos
        if all(not e.vivo for e in enemigos):
            os.system("cls" if os.name == "nt" else "clear")
            mostrar_mapa_consola(mapa, jugador, salida, enemigos)
            print("\n🎉 ¡Has atrapado a todos los cazadores! 🎉")
            print(f"Movimientos: {movimientos_jugador}")
            print(f"Puntaje final: {jugador.puntaje}")
            break


# ===============================
#  MAIN
# ===============================

if __name__ == "__main__":
    iniciar_modo_cazador_simple()
