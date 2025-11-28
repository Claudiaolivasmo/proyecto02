import random




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

ANCHO_MAPA = 21 
ALTO_MAPA = 17

# ====== BOMBAS (modo Escapa) ======

MAX_BOMBAS_ACTIVAS = 3           # máx. bombas colocadas al mismo tiempo
COOLDOWN_BOMBA_TURNOS = 5        # turnos entre colocar una y otra
DEMORA_EXPLOSION_BOMBA = 3       # turnos que tarda en explotar sola
RANGO_BOMBA = 1                  # radio de explosión (en casillas, estilo cruz sencilla)
RESPAWN_ENEMIGO_TURNOS = 10      # turnos para que el enemigo reviva
BONO_BOMBA = 50                  # puntos por enemigo eliminado con bomba


# ====== PUNTAJE MODO CAZADOR (versión simple) ======
PENALIZACION_ENEMIGO_ESCAPA = 50   # puntos que pierdes si un cazador sale
PUNTOS_ATRAPAR_ENEMIGO = 100       # puntos que ganas por atraparlo
OBJETIVO_CAPTURAS = 8              # cazadores a atrapar para ganar


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
        cant_enemigos=3,
        energia_max=120,
        consumo_correr=4,
        recuperacion_pasiva=3
    ),
    DIFICULTAD_MEDIA: ConfigDificultad(
        DIFICULTAD_MEDIA,
        vel_enemigos=1,
        cant_enemigos=5,
        energia_max=100,
        consumo_correr=5,
        recuperacion_pasiva=2
    ),
    DIFICULTAD_DIFICIL: ConfigDificultad(
        DIFICULTAD_DIFICIL,
        vel_enemigos=1,
        cant_enemigos=8,
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


def crear_enemigos_en_camino(camino_principal, cantidad, jugador, salida):
    enemigos = []

    # Celdas candidatas del camino donde SÍ podemos poner enemigos
    candidatos = []
    for (f, c) in camino_principal:
        if (f, c) == (jugador.fila, jugador.columna):
            continue
        if (f, c) == salida:
            continue
        candidatos.append((f, c))

    # Por si hay menos celdas que enemigos
    cantidad_real = min(cantidad, len(candidatos))

    # Elegimos posiciones al azar dentro del camino
    posiciones_elegidas = random.sample(candidatos, cantidad_real)

    for (f, c) in posiciones_elegidas:
        enemigos.append(Enemigo(f, c))

    return enemigos


def mover_enemigos_cazador(enemigos, mapa, salida):
    """
    Mueve a todos los cazadores un paso intentando acercarse a la salida (distancia Manhattan).
    Si no pueden acercarse, intentan un paso aleatorio válido para evitar quedarse atascado.
    """
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

        # 1. Analizar movimientos posibles
        for df, dc in direcciones_base:
            nf = enemigo.fila + df
            nc = enemigo.columna + dc
            
            # Chequear límites y si puede pisar
            if 0 <= nf < filas and 0 <= nc < columnas and mapa[nf][nc].puede_pisar_enemigo():
                nueva_dist = abs(nf - fila_salida) + abs(nc - col_salida)
                
                if nueva_dist < current_dist:
                    movimientos_prioritarios.append((df, dc))
                elif nueva_dist == current_dist:
                    movimientos_secundarios.append((df, dc)) # Mantiene la distancia

        se_movio = False
        
        # 2. Intentar movimiento prioritario (reduce distancia)
        random.shuffle(movimientos_prioritarios)
        for df, dc in movimientos_prioritarios:
            enemigo.fila += df
            enemigo.columna += dc
            se_movio = True
            break
        
        if se_movio:
            continue
            
        # 3. Intentar movimiento secundario (mantiene distancia)
        random.shuffle(movimientos_secundarios)
        for df, dc in movimientos_secundarios:
            enemigo.fila += df
            enemigo.columna += dc
            se_movio = True
            break
            
        # 4. Si sigue sin moverse, probar un movimiento aleatorio válido
        if not se_movio:
            random.shuffle(direcciones_base)
            for df, dc in direcciones_base:
                nf = enemigo.fila + df
                nc = enemigo.columna + dc
                
                if 0 <= nf < filas and 0 <= nc < columnas and mapa[nf][nc].puede_pisar_enemigo():
                    enemigo.fila = nf
                    enemigo.columna = nc
                    break


def respawnear_enemigo(enemigo, camino_principal, jugador, salida):
    """
    Reaparece al enemigo en una posición ALEATORIA del camino principal,
    evitando:
    - la casilla del jugador
    - la salida
    - la misma casilla donde estaba antes
    Si no encuentra lugar, el enemigo queda muerto (vivo = False).
    """
    candidatos = []
    pos_anterior = (enemigo.fila, enemigo.columna)

    for (f, c) in camino_principal:
        if (f, c) == (jugador.fila, jugador.columna):
            continue
        if (f, c) == salida:
            continue
        if (f, c) == pos_anterior:
            continue
        candidatos.append((f, c))

    if not candidatos:
        enemigo.vivo = False
        return

    f, c = random.choice(candidatos)
    enemigo.fila = f
    enemigo.columna = c
    enemigo.vivo = True


def capturar_enemigos_en_posicion_jugador(jugador, enemigos, camino_principal, salida, respawn=False):
    """
    Marca como capturados a los enemigos que estén en la misma casilla que el jugador.
    - Si respawn=True, el enemigo reaparece en otra casilla válida del camino.
    - Si respawn=False, se queda muerto (vivo = False).
    Devuelve cuántos enemigos fueron capturados.
    """
    capturados = 0
    for enemigo in enemigos:
        if enemigo.vivo and enemigo.fila == jugador.fila and enemigo.columna == jugador.columna:
            capturados += 1
            if respawn:
                respawnear_enemigo(enemigo, camino_principal, jugador, salida)
            else:
                enemigo.vivo = False
    return capturados


def mover_enemigos(enemigos, jugador, mapa):
    """
    Mueve todos los enemigos un paso hacia el jugador.
    """
    for enemigo in enemigos:
        if enemigo.vivo:
            mover_enemigo_hacia_jugador(enemigo, jugador, mapa)


def generar_mapa(ancho=ANCHO_MAPA, alto=ALTO_MAPA):

    # Aseguramos que el ancho y alto sean impares para el algoritmo de laberinto
    if alto % 2 == 0:
        alto += 1
    if ancho % 2 == 0:
        ancho += 1

    # 1. Crear matriz llena de MUROS
    mapa = []
    for f in range(alto):
        fila_nueva = []
        for c in range(ancho):
            fila_nueva.append(Muro())
        mapa.append(fila_nueva)

    # Punto de inicio del laberinto para el algoritmo (siempre fila impar, col = 1)
    start_f = random.randrange(1, alto, 2)
    start_c = 1

    # Entrada real del jugador (columna 0)
    fila_entrada_jugador = start_f
    columna_entrada_jugador = 0
    mapa[fila_entrada_jugador][columna_entrada_jugador] = Camino()  # entrada

    inicio = (fila_entrada_jugador, columna_entrada_jugador)

    # Guardamos el camino principal
    camino_principal = [(fila_entrada_jugador, columna_entrada_jugador)]

    # Backtracking para abrir celdas tipo Camino en el interior
    stack = [(start_f, start_c)]
    mapa[start_f][start_c] = Camino()
    camino_principal.append((start_f, start_c))

    direcciones = [(-2, 0), (2, 0), (0, -2), (0, 2)]

    while stack:
        current_f, current_c = stack[-1]

        unvisited_neighbors = []
        for df, dc in direcciones:
            neighbor_f = current_f + df
            neighbor_c = current_c + dc
            if (
                0 <= neighbor_f < alto
                and 0 <= neighbor_c < ancho
                and isinstance(mapa[neighbor_f][neighbor_c], Muro)
            ):
                unvisited_neighbors.append((neighbor_f, neighbor_c, df, dc))

        if unvisited_neighbors:
            next_f, next_c, df, dc = random.choice(unvisited_neighbors)

            # "Romper" el muro intermedio
            wall_f = current_f + df // 2
            wall_c = current_c + dc // 2
            mapa[wall_f][wall_c] = Camino()
            mapa[next_f][next_c] = Camino()

            camino_principal.append((wall_f, wall_c))
            camino_principal.append((next_f, next_c))

            stack.append((next_f, next_c))
        else:
            stack.pop()

    # 2. Asegurar la salida en la última columna
    fila_salida = random.randrange(1, alto, 2)
    columna_salida = ancho - 1
    mapa[fila_salida][columna_salida] = Camino()

    # Asegurar conexión con el laberinto interno
    if isinstance(mapa[fila_salida][columna_salida - 1], Muro):
        mapa[fila_salida][columna_salida - 1] = Camino()

    salida = (fila_salida, columna_salida)
    camino_principal.append(salida)

    # ------------------------------------------------------------------
    # 3. Decorar el laberinto con Lianas y Túneles
    # ------------------------------------------------------------------

    # Probabilidades (ajusta al gusto)
    PROB_TUNEL_EN_CAMINO = 0.10   # 10% de caminos normales serán túneles
    PROB_LIANA_EN_CAMINO = 0.06   # 6% serán lianas
    PROB_TUNEL_EN_MURO   = 0.08   # 8% de muros se abren como túnel
    PROB_LIANA_EN_MURO   = 0.08   # 8% de muros se abren como liana

    # Para no romper el camino garantizado entrada→salida
    camino_principal_set = set(camino_principal)

    for f in range(1, alto - 1):
        for c in range(1, ancho - 1):

            # No tocamos las casillas del camino principal
            if (f, c) in camino_principal_set:
                continue

            celda = mapa[f][c]

            # 1) Decorar caminos existentes
            if isinstance(celda, Camino):
                r = random.random()
                if r < PROB_TUNEL_EN_CAMINO:
                    mapa[f][c] = Tunel()   # solo jugador
                elif r < PROB_TUNEL_EN_CAMINO + PROB_LIANA_EN_CAMINO:
                    mapa[f][c] = Liana()   # solo enemigos

            # 2) Abrir algunos muros como pasajes especiales
            elif isinstance(celda, Muro):
                r = random.random()
                if r < PROB_TUNEL_EN_MURO:
                    mapa[f][c] = Tunel()
                elif r < PROB_TUNEL_EN_MURO + PROB_LIANA_EN_MURO:
                    mapa[f][c] = Liana()

    return mapa, inicio, salida, camino_principal


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
    if correr and jugador.energia_actual > 0:
        # Solo si tiene energía, corre y gasta
        jugador.gastar_energia(config_dificultad.consumo_correr)
    else:
        # Caminar NO consume energía
        pass

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
        print(f" Ya tienes {MAX_BOMBAS_ACTIVAS} bombas activas.")
        return False, ultimo_turno_bomba

    # Cooldown
    if turnos - ultimo_turno_bomba < COOLDOWN_BOMBA_TURNOS:
        faltan = COOLDOWN_BOMBA_TURNOS - (turnos - ultimo_turno_bomba)
        print(f" Debes esperar {faltan} turnos más para colocar otra bomba.")
        return False, ultimo_turno_bomba

    f = jugador.fila
    c = jugador.columna

    # No permitir doble bomba en la misma casilla
    for b in bombas:
        if not b.explotada and b.fila == f and b.columna == c:
            print(" Ya hay una bomba en esta casilla.")
            return False, ultimo_turno_bomba

    # La casilla ya es válida porque el jugador está parado ahí,
    # así que simplemente creamos la bomba.
    nueva_bomba = Bomba(f, c, turnos)
    bombas.append(nueva_bomba)
    print(" Has colocado una bomba.")
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
    print(" ¡Bomba explotó!")

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
            print(f" Enemigo eliminado por bomba. +{BONO_BOMBA} puntos.")
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
                print(" Un enemigo ha reaparecido en el mapa.")
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


