"""
=============================================================================
SUICIDE ARENA: EL PRIMERO QUE MUERA GANA (Inverted PvP Shooter)
=============================================================================
Instalación de dependencias:
    pip install pygame

Ejecución:
    python main.py

Controles:
    - JUGADOR 1 (Cian / Neón Azul):
        * Movimiento: W, A, S, D
        * Disparar: ESPACIO
    - JUGADOR 2 (Naranja / Fuego):
        * Movimiento: Flechas (Arriba, Izquierda, Abajo, Derecha)
        * Disparar: ENTER (o Keypad Enter)
    - Globales:
        * ESPACIO / ENTER: Iniciar partida desde el menú
        * R: Reiniciar partida tras fin de juego
        * ESC: Pausar o salir al menú / Salir
=============================================================================
"""

import math
import random
import sys
import pygame


# =============================================================================
# CONSTANTES GLOBALES Y CONFIGURACIÓN
# =============================================================================
SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 700
FPS = 60

# Paleta de colores
COLOR_BG = (16, 18, 27)
COLOR_GRID = (28, 32, 48)
COLOR_WHITE = (245, 245, 250)
COLOR_GRAY = (140, 145, 160)
COLOR_DARK_GRAY = (40, 44, 60)

# Jugador 1: Cyan / Neón Azul
COLOR_P1 = (0, 229, 255)
COLOR_P1_DARK = (0, 140, 160)

# Jugador 2: Naranja / Fuego
COLOR_P2 = (255, 110, 0)
COLOR_P2_DARK = (180, 75, 0)

# Peligros y orbes
COLOR_HAZARD = (255, 45, 85)
COLOR_HAZARD_CORE = (255, 180, 195)
COLOR_BULLET_P1 = (80, 240, 255)
COLOR_BULLET_P2 = (255, 150, 50)


# =============================================================================
# CLASE: PARTÍCULA (Feedback visual y jugosidad)
# =============================================================================
class Particula:
    """Partículas para explosiones, estelas y disparos."""
    def __init__(self, x, y, color, vel_x=None, vel_y=None, vida=30, radio=4):
        self.x = x
        self.y = y
        self.color = color
        self.vida = vida
        self.vida_max = vida
        self.radio = radio
        if vel_x is None:
            angulo = random.uniform(0, 2 * math.pi)
            rapidez = random.uniform(1.0, 4.5)
            self.vx = math.cos(angulo) * rapidez
            self.vy = math.sin(angulo) * rapidez
        else:
            self.vx = vel_x
            self.vy = vel_y

    def actualizar(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.94
        self.vy *= 0.94
        self.vida -= 1

    def dibujar(self, superficie):
        if self.vida > 0:
            alfa = max(0.1, self.vida / self.vida_max)
            radio_actual = max(1, int(self.radio * alfa))
            pygame.draw.circle(superficie, self.color, (int(self.x), int(self.y)), radio_actual)


# =============================================================================
# CLASE: PROYECTIL (Balas disparadas por jugadores)
# =============================================================================
class Proyectil(pygame.sprite.Sprite):
    """
    Proyectiles disparados por los jugadores.
    ATENCIÓN A LA MECÁNICA:
    - Si impacta a su PROPIO creador, le inflige 12 de daño (¡Bueno para suicidarse!).
    - Si impacta al RIVAL, le inflige 6 de daño (¡Malo porque ayuda al enemigo a ganar!).
    """
    def __init__(self, x, y, dir_x, dir_y, propietario_id, color):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.velocidad = 9.5
        self.propietario_id = propietario_id  # 1 o 2
        self.color = color
        self.radio = 7
        self.tiempo_vida = 140  # Frames antes de desaparecer
        self.danio_autoinfligido = 12
        self.danio_rival = 6

        # Rect para colisiones
        self.rect = pygame.Rect(int(self.x - self.radio), int(self.y - self.radio), self.radio * 2, self.radio * 2)

    def update(self, ancho_pantalla, alto_pantalla, obstaculos_fijos):
        self.x += self.dir_x * self.velocidad
        self.y += self.dir_y * self.velocidad
        self.tiempo_vida -= 1

        # Rebote en bordes de la pantalla (permite rebotar balas hacia uno mismo)
        if self.x - self.radio <= 0:
            self.x = self.radio
            self.dir_x *= -1
        elif self.x + self.radio >= ancho_pantalla:
            self.x = ancho_pantalla - self.radio
            self.dir_x *= -1

        if self.y - self.radio <= 60:  # Límite superior reservado para el HUD
            self.y = 60 + self.radio
            self.dir_y *= -1
        elif self.y + self.radio >= alto_pantalla:
            self.y = alto_pantalla - self.radio
            self.dir_y *= -1

        self.rect.center = (int(self.x), int(self.y))

        # Rebote o colisión con obstáculos fijos del mapa
        for obs in obstaculos_fijos:
            if self.rect.colliderect(obs.rect):
                # Desvío por impacto en pilar
                self.dir_x *= -1
                self.dir_y *= -1
                self.tiempo_vida -= 15
                break

    def esta_vivo(self):
        return self.tiempo_vida > 0

    def dibujar(self, superficie):
        # Efecto de brillo
        centro = (int(self.x), int(self.y))
        pygame.draw.circle(superficie, self.color, centro, self.radio)
        pygame.draw.circle(superficie, COLOR_WHITE, centro, max(2, self.radio - 3))


# =============================================================================
# CLASE: OBSTÁCULO Y PELIGRO AMBIENTAL
# =============================================================================
class PilarObstaculo:
    """Bloque del mapa con pinchos que daña al contacto."""
    def __init__(self, x, y, ancho, alto):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.color_borde = (90, 30, 45)
        self.color_fondo = (45, 18, 28)
        self.danio_por_segundo = 25  # Daño masivo por quedarse tocándolo

    def dibujar(self, superficie):
        pygame.draw.rect(superficie, self.color_fondo, self.rect, border_radius=6)
        pygame.draw.rect(superficie, self.color_borde, self.rect, width=2, border_radius=6)
        # Decoración de peligro
        cx, cy = self.rect.center
        pygame.draw.circle(superficie, COLOR_HAZARD, (cx, cy), 8)


class OrbePeligro(pygame.sprite.Sprite):
    """
    Minas errantes / orbes letales que patrullan la arena.
    ¡Los jugadores se pelean por tirarse de cabeza sobre ellas!
    """
    def __init__(self, x, y):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.radio = 18
        angulo = random.uniform(0, 2 * math.pi)
        velocidad = random.uniform(2.0, 3.5)
        self.vx = math.cos(angulo) * velocidad
        self.vy = math.sin(angulo) * velocidad
        self.rect = pygame.Rect(int(self.x - self.radio), int(self.y - self.radio), self.radio * 2, self.radio * 2)
        self.danio = 18
        self.pulsacion = random.uniform(0, 5)

    def update(self, ancho_pantalla, alto_pantalla, obstaculos):
        self.x += self.vx
        self.y += self.vy
        self.pulsacion += 0.08

        # Rebotes en límites de arena
        if self.x - self.radio <= 0 or self.x + self.radio >= ancho_pantalla:
            self.vx *= -1
            self.x = max(self.radio, min(ancho_pantalla - self.radio, self.x))
        if self.y - self.radio <= 60 or self.y + self.radio >= alto_pantalla:
            self.vy *= -1
            self.y = max(60 + self.radio, min(alto_pantalla - self.radio, self.y))

        self.rect.center = (int(self.x), int(self.y))

        # Colisión y rebote contra pilares
        for obs in obstaculos:
            if self.rect.colliderect(obs.rect):
                self.vx *= -1
                self.vy *= -1
                break

    def dibujar(self, superficie):
        centro = (int(self.x), int(self.y))
        pulso = int(math.sin(self.pulsacion) * 3)
        radio_dibujo = max(10, self.radio + pulso)

        # Halo exterior
        pygame.draw.circle(superficie, COLOR_HAZARD, centro, radio_dibujo, width=3)
        # Núcleo ardiente
        pygame.draw.circle(superficie, COLOR_HAZARD_CORE, centro, radio_dibujo - 6)
        # Símbolo calavera/cruz de advertencia
        pygame.draw.line(superficie, COLOR_HAZARD, (centro[0] - 5, centro[1]), (centro[0] + 5, centro[1]), 2)
        pygame.draw.line(superficie, COLOR_HAZARD, (centro[0], centro[1] - 5), (centro[0], centro[1] + 5), 2)


# =============================================================================
# CLASE: JUGADOR
# =============================================================================
class Jugador:
    def __init__(self, id_jugador, nombre, x, y, color, teclas):
        self.id = id_jugador
        self.nombre = nombre
        self.x = float(x)
        self.y = float(y)
        self.color = color
        self.teclas = teclas  # Diccionario con keys: 'up', 'down', 'left', 'right', 'shoot'

        self.radio = 20
        self.velocidad = 5.2
        self.salud_max = 100.0
        self.salud = 100.0

        # Vector de orientación de disparo (por defecto apuntando al centro)
        self.dir_mirada = [1.0 if id_jugador == 1 else -1.0, 0.0]

        # Cadencia de disparo (cooldown en frames)
        self.cooldown_disparo = 0
        self.cooldown_max = 15  # Disparo ágil

        # Inmunidad breve tras impacto grave (frames)
        self.tiempo_invulnerable = 0

        # Animación de flash al recibir daño
        self.flash_danio = 0

    @property
    def rect(self):
        return pygame.Rect(int(self.x - self.radio), int(self.y - self.radio), self.radio * 2, self.radio * 2)

    def recibir_danio(self, cantidad):
        """Reduce la vida. ¡Recuerda que llegar a 0 es el objetivo!"""
        if self.tiempo_invulnerable <= 0:
            self.salud = max(0.0, self.salud - cantidad)
            self.flash_danio = 8
            self.tiempo_invulnerable = 12
            return True
        return False

    def actualizar(self, teclas_presionadas, ancho_pantalla, alto_pantalla, obstaculos):
        # Disminución de contadores
        if self.cooldown_disparo > 0:
            self.cooldown_disparo -= 1
        if self.tiempo_invulnerable > 0:
            self.tiempo_invulnerable -= 1
        if self.flash_danio > 0:
            self.flash_danio -= 1

        # Movimiento 8 direcciones
        dx = 0
        dy = 0
        if teclas_presionadas[self.teclas['left']]:
            dx -= 1
        if teclas_presionadas[self.teclas['right']]:
            dx += 1
        if teclas_presionadas[self.teclas['up']]:
            dy -= 1
        if teclas_presionadas[self.teclas['down']]:
            dy += 1

        # Normalización diagonal
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        # Actualizar dirección de la mirada si se mueve
        if dx != 0 or dy != 0:
            self.dir_mirada = [dx, dy]

        # Aplicar movimiento con límites
        nueva_x = self.x + dx * self.velocidad
        nueva_y = self.y + dy * self.velocidad

        # Comprobar bordes
        nueva_x = max(self.radio, min(ancho_pantalla - self.radio, nueva_x))
        nueva_y = max(60 + self.radio, min(alto_pantalla - self.radio, nueva_y))

        # Colisión con obstáculos fijos
        rect_previo_x = pygame.Rect(int(nueva_x - self.radio), int(self.y - self.radio), self.radio * 2, self.radio * 2)
        bloqueado_x = any(rect_previo_x.colliderect(obs.rect) for obs in obstaculos)
        if not bloqueado_x:
            self.x = nueva_x

        rect_previo_y = pygame.Rect(int(self.x - self.radio), int(nueva_y - self.radio), self.radio * 2, self.radio * 2)
        bloqueado_y = any(rect_previo_y.colliderect(obs.rect) for obs in obstaculos)
        if not bloqueado_y:
            self.y = nueva_y

    def intentar_disparar(self, teclas_presionadas):
        """Dispara un proyectil en la dirección a la que apunta."""
        if teclas_presionadas[self.teclas['shoot']] and self.cooldown_disparo <= 0:
            self.cooldown_disparo = self.cooldown_max

            # Dirección normalizada de disparo
            vx, vy = self.dir_mirada
            norma = math.hypot(vx, vy)
            if norma == 0:
                vx, vy = (1.0, 0.0)
            else:
                vx /= norma
                vy /= norma

            punto_salida_x = self.x + vx * (self.radio + 6)
            punto_salida_y = self.y + vy * (self.radio + 6)

            color_bala = COLOR_BULLET_P1 if self.id == 1 else COLOR_BULLET_P2
            return Proyectil(punto_salida_x, punto_salida_y, vx, vy, self.id, color_bala)
        return None

    def dibujar(self, superficie):
        centro = (int(self.x), int(self.y))

        # Color con efecto de daño
        color_cuerpo = (255, 255, 255) if self.flash_danio > 0 else self.color

        # Cañón / indicador de dirección
        norma = math.hypot(self.dir_mirada[0], self.dir_mirada[1])
        if norma > 0:
            nx = self.dir_mirada[0] / norma
            ny = self.dir_mirada[1] / norma
            canon_fin = (int(self.x + nx * (self.radio + 8)), int(self.y + ny * (self.radio + 8)))
            pygame.draw.line(superficie, color_cuerpo, centro, canon_fin, 5)

        # Círculo del personaje
        pygame.draw.circle(superficie, color_cuerpo, centro, self.radio)
        pygame.draw.circle(superficie, COLOR_DARK_GRAY, centro, self.radio - 5)

        # Anillo interior con color
        pygame.draw.circle(superficie, color_cuerpo, centro, 6)

        # Barra de vida flotante sobre la cabeza
        ancho_barra = 48
        alto_barra = 6
        x_barra = self.x - ancho_barra / 2
        y_barra = self.y - self.radio - 16

        pct_vida = self.salud / self.salud_max
        # Cuanto menos vida tiene, más verde/dorada se pone porque ¡está más cerca de ganar!
        color_vida = (80, 220, 100) if pct_vida < 0.35 else (230, 70, 70)

        pygame.draw.rect(superficie, (20, 20, 25), (x_barra - 1, y_barra - 1, ancho_barra + 2, alto_barra + 2), border_radius=2)
        pygame.draw.rect(superficie, color_vida, (x_barra, y_barra, ancho_barra * pct_vida, alto_barra), border_radius=2)


# =============================================================================
# CLASE PRINCIPAL: JUEGO
# =============================================================================
class SuicideArenaGame:
    ESTADO_MENU = "MENU"
    ESTADO_JUGANDO = "JUGANDO"
    ESTADO_FIN = "FIN"

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("SUICIDE ARENA - ¡El Primero Que Muera Gana!")
        self.pantalla = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.reloj = pygame.time.Clock()

        # Fuentes
        self.font_titulo = pygame.font.SysFont("Arial", 46, bold=True)
        self.font_subtitulo = pygame.font.SysFont("Arial", 22, bold=True)
        self.font_ui = pygame.font.SysFont("Arial", 18, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 14)

        self.estado = self.ESTADO_MENU
        self.ganador = None
        self.particulas = []

        # Inicialización de entidades
        self.reiniciar_partida()

    def reiniciar_partida(self):
        """Reinicia la arena de combate y los jugadores."""
        teclas_p1 = {
            'up': pygame.K_w,
            'down': pygame.K_s,
            'left': pygame.K_a,
            'right': pygame.K_d,
            'shoot': pygame.K_SPACE
        }
        teclas_p2 = {
            'up': pygame.K_UP,
            'down': pygame.K_DOWN,
            'left': pygame.K_LEFT,
            'right': pygame.K_RIGHT,
            'shoot': pygame.K_RETURN
        }

        # Posiciones iniciales a los lados
        self.p1 = Jugador(1, "JUGADOR 1 (CIAN)", 180, SCREEN_HEIGHT // 2, COLOR_P1, teclas_p1)
        self.p2 = Jugador(2, "JUGADOR 2 (NARANJA)", SCREEN_WIDTH - 180, SCREEN_HEIGHT // 2, COLOR_P2, teclas_p2)

        self.proyectiles = []
        self.particulas = []

        # Creación de obstáculos fijos de peligro
        self.obstaculos = [
            PilarObstaculo(SCREEN_WIDTH // 2 - 25, 120, 50, 140),
            PilarObstaculo(SCREEN_WIDTH // 2 - 25, SCREEN_HEIGHT - 260, 50, 140),
            PilarObstaculo(260, SCREEN_HEIGHT // 2 - 40, 40, 80),
            PilarObstaculo(SCREEN_WIDTH - 300, SCREEN_HEIGHT // 2 - 40, 40, 80),
        ]

        # Minas / orbes móviles
        self.peligros = [
            OrbePeligro(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
            OrbePeligro(SCREEN_WIDTH // 4, 180),
            OrbePeligro(SCREEN_WIDTH * 3 // 4, SCREEN_HEIGHT - 180),
            OrbePeligro(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100),
        ]

        self.ganador = None

    def crear_explosion(self, x, y, color, cantidad=18):
        for _ in range(cantidad):
            self.particulas.append(Particula(x, y, color))

    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    if self.estado == self.ESTADO_JUGANDO:
                        self.estado = self.ESTADO_MENU
                    else:
                        return False

                if self.estado == self.ESTADO_MENU:
                    if evento.key in (pygame.K_SPACE, pygame.K_RETURN):
                        self.reiniciar_partida()
                        self.estado = self.ESTADO_JUGANDO

                elif self.estado == self.ESTADO_FIN:
                    if evento.key == pygame.K_r:
                        self.reiniciar_partida()
                        self.estado = self.ESTADO_JUGANDO
                    elif evento.key in (pygame.K_SPACE, pygame.K_RETURN):
                        self.estado = self.ESTADO_MENU

        return True

    def actualizar(self):
        if self.estado != self.ESTADO_JUGANDO:
            return

        teclas = pygame.key.get_pressed()

        # 1. Actualización de Jugadores
        self.p1.actualizar(teclas, SCREEN_WIDTH, SCREEN_HEIGHT, self.obstaculos)
        self.p2.actualizar(teclas, SCREEN_WIDTH, SCREEN_HEIGHT, self.obstaculos)

        # 2. Manejo de disparos
        bala_p1 = self.p1.intentar_disparar(teclas)
        if bala_p1:
            self.proyectiles.append(bala_p1)
            self.crear_explosion(bala_p1.x, bala_p1.y, COLOR_BULLET_P1, cantidad=5)

        bala_p2 = self.p2.intentar_disparar(teclas)
        if bala_p2:
            self.proyectiles.append(bala_p2)
            self.crear_explosion(bala_p2.x, bala_p2.y, COLOR_BULLET_P2, cantidad=5)

        # 3. Actualizar proyectiles
        for p in self.proyectiles[:]:
            p.update(SCREEN_WIDTH, SCREEN_HEIGHT, self.obstaculos)
            if not p.esta_vivo():
                self.proyectiles.remove(p)
                continue

            # Colisión con Jugador 1
            if self.p1.rect.colliderect(p.rect):
                danio = p.danio_autoinfligido if p.propietario_id == 1 else p.danio_rival
                if self.p1.recibir_danio(danio):
                    self.crear_explosion(p.x, p.y, COLOR_P1, cantidad=12)
                    if p in self.proyectiles:
                        self.proyectiles.remove(p)
                continue

            # Colisión con Jugador 2
            if self.p2.rect.colliderect(p.rect):
                danio = p.danio_autoinfligido if p.propietario_id == 2 else p.danio_rival
                if self.p2.recibir_danio(danio):
                    self.crear_explosion(p.x, p.y, COLOR_P2, cantidad=12)
                    if p in self.proyectiles:
                        self.proyectiles.remove(p)
                continue

        # 4. Actualizar peligros móviles (Orbes)
        for peligro in self.peligros:
            peligro.update(SCREEN_WIDTH, SCREEN_HEIGHT, self.obstaculos)

            # Daño a P1 si colisiona con el peligro
            if self.p1.rect.colliderect(peligro.rect):
                if self.p1.recibir_danio(peligro.danio):
                    self.crear_explosion(self.p1.x, self.p1.y, COLOR_HAZARD, cantidad=20)

            # Daño a P2 si colisiona con el peligro
            if self.p2.rect.colliderect(peligro.rect):
                if self.p2.recibir_danio(peligro.danio):
                    self.crear_explosion(self.p2.x, self.p2.y, COLOR_HAZARD, cantidad=20)

        # 5. Daño por contacto continuo con pilares electrificados
        dt_segundos = 1.0 / FPS
        for obs in self.obstaculos:
            if self.p1.rect.colliderect(obs.rect):
                self.p1.recibir_danio(obs.danio_por_segundo * dt_segundos)
                if random.random() < 0.25:
                    self.crear_explosion(self.p1.x, self.p1.y, COLOR_HAZARD, cantidad=3)

            if self.p2.rect.colliderect(obs.rect):
                self.p2.recibir_danio(obs.danio_por_segundo * dt_segundos)
                if random.random() < 0.25:
                    self.crear_explosion(self.p2.x, self.p2.y, COLOR_HAZARD, cantidad=3)

        # 6. Partículas
        for part in self.particulas[:]:
            part.actualizar()
            if part.vida <= 0:
                self.particulas.remove(part)

        # 7. COMPROBACIÓN DE CONDICIÓN DE VICTORIA INVERTIDA
        # ¡El primero que llega a 0 GANA!
        if self.p1.salud <= 0 and self.p2.salud <= 0:
            self.ganador = "¡EMPATE ÉPICO! AMBOS MURIERON A LA VEZ"
            self.estado = self.ESTADO_FIN
        elif self.p1.salud <= 0:
            self.ganador = self.p1.nombre
            self.estado = self.ESTADO_FIN
        elif self.p2.salud <= 0:
            self.ganador = self.p2.nombre
            self.estado = self.ESTADO_FIN

    # =========================================================================
    # RENDERIZADO
    # =========================================================================
    def dibujar_fondo(self):
        self.pantalla.fill(COLOR_BG)
        # Cuadrícula cibernética sutil
        tam_cuadricula = 50
        for x in range(0, SCREEN_WIDTH, tam_cuadricula):
            pygame.draw.line(self.pantalla, COLOR_GRID, (x, 60), (x, SCREEN_HEIGHT), 1)
        for y in range(60, SCREEN_HEIGHT, tam_cuadricula):
            pygame.draw.line(self.pantalla, COLOR_GRID, (0, y), (SCREEN_WIDTH, y), 1)

    def dibujar_hud(self):
        # Franja superior oscura para el HUD
        pygame.draw.rect(self.pantalla, (10, 12, 18), (0, 0, SCREEN_WIDTH, 60))
        pygame.draw.line(self.pantalla, (45, 50, 70), (0, 60), (SCREEN_WIDTH, 60), 2)

        # Barra y datos P1 (Izquierda)
        texto_p1 = self.font_ui.render(f"P1: {int(self.p1.salud)} HP", True, COLOR_P1)
        self.pantalla.blit(texto_p1, (20, 10))

        ancho_barra = 260
        alto_barra = 16
        pct_p1 = self.p1.salud / self.p1.salud_max
        # Marco
        pygame.draw.rect(self.pantalla, COLOR_DARK_GRAY, (20, 34, ancho_barra, alto_barra), border_radius=4)
        # Barra (se vuelve dorada cuando está por morir = ganar)
        color_bar_p1 = (255, 215, 0) if pct_p1 < 0.25 else COLOR_P1
        pygame.draw.rect(self.pantalla, color_bar_p1, (20, 34, int(ancho_barra * pct_p1), alto_barra), border_radius=4)

        # Regla central en el HUD
        texto_regla = self.font_ui.render("¡EL PRIMERO EN MORIR GANA!", True, (255, 60, 90))
        rect_regla = texto_regla.get_rect(center=(SCREEN_WIDTH // 2, 22))
        self.pantalla.blit(texto_regla, rect_regla)

        sub_regla = self.font_small.render("Tírate a las minas y desvía las balas hacia ti", True, COLOR_GRAY)
        rect_sub = sub_regla.get_rect(center=(SCREEN_WIDTH // 2, 44))
        self.pantalla.blit(sub_regla, rect_sub)

        # Barra y datos P2 (Derecha)
        texto_p2 = self.font_ui.render(f"P2: {int(self.p2.salud)} HP", True, COLOR_P2)
        rect_p2 = texto_p2.get_rect(topright=(SCREEN_WIDTH - 20, 10))
        self.pantalla.blit(texto_p2, rect_p2)

        pct_p2 = self.p2.salud / self.p2.salud_max
        x_bar_p2 = SCREEN_WIDTH - 20 - ancho_barra
        pygame.draw.rect(self.pantalla, COLOR_DARK_GRAY, (x_bar_p2, 34, ancho_barra, alto_barra), border_radius=4)
        color_bar_p2 = (255, 215, 0) if pct_p2 < 0.25 else COLOR_P2
        pygame.draw.rect(self.pantalla, color_bar_p2, (x_bar_p2 + int(ancho_barra * (1 - pct_p2)), 34, int(ancho_barra * pct_p2), alto_barra), border_radius=4)

    def dibujar_juego(self):
        self.dibujar_fondo()

        # Dibujar obstáculos fijos
        for obs in self.obstaculos:
            obs.dibujar(self.pantalla)

        # Dibujar peligros
        for peligro in self.peligros:
            peligro.dibujar(self.pantalla)

        # Dibujar proyectiles
        for p in self.proyectiles:
            p.dibujar(self.pantalla)

        # Dibujar jugadores
        self.p1.dibujar(self.pantalla)
        self.p2.dibujar(self.pantalla)

        # Dibujar partículas
        for part in self.particulas:
            part.dibujar(self.pantalla)

        # Dibujar HUD
        self.dibujar_hud()

    def dibujar_menu(self):
        self.pantalla.fill(COLOR_BG)

        # Título principal
        titulo = self.font_titulo.render("SUICIDE ARENA", True, COLOR_HAZARD)
        rect_titulo = titulo.get_rect(center=(SCREEN_WIDTH // 2, 90))
        self.pantalla.blit(titulo, rect_titulo)

        sub = self.font_subtitulo.render("MECÁNICA INVERTIDA: ¡EL PRIMERO QUE MUERA GANA!", True, COLOR_WHITE)
        rect_sub = sub.get_rect(center=(SCREEN_WIDTH // 2, 145))
        self.pantalla.blit(sub, rect_sub)

        # Tarjeta explicativa
        rect_card = pygame.Rect(SCREEN_WIDTH // 2 - 420, 190, 840, 270)
        pygame.draw.rect(self.pantalla, (24, 28, 42), rect_card, border_radius=12)
        pygame.draw.rect(self.pantalla, (55, 65, 95), rect_card, width=2, border_radius=12)

        reglas = [
            "• OBJETIVO: Tu barra de vida debe llegar a 0 antes que la de tu rival.",
            "• TÁCTICA 1: Tírate de cabeza contra las minas rojas y pilares electrificados.",
            "• TÁCTICA 2: Tus balas rebotan en las paredes... ¡úsalas para hacerte daño a ti mismo!",
            "• CUIDADO: Si le disparas al rival, le restarás vida y le estarás REGALANDO la victoria.",
        ]

        y_offset = 215
        for linea in reglas:
            texto = self.font_ui.render(linea, True, (220, 225, 240))
            self.pantalla.blit(texto, (rect_card.x + 30, y_offset))
            y_offset += 38

        # Controles de cada bando
        # Bando 1
        p1_box = pygame.Rect(rect_card.x + 40, 370, 360, 70)
        pygame.draw.rect(self.pantalla, (18, 30, 45), p1_box, border_radius=8)
        p1_titulo = self.font_ui.render("JUGADOR 1 (Cian)", True, COLOR_P1)
        p1_ctrl = self.font_small.render("Mover: [W, A, S, D] | Disparar: [ESPACIO]", True, COLOR_WHITE)
        self.pantalla.blit(p1_titulo, (p1_box.x + 15, p1_box.y + 12))
        self.pantalla.blit(p1_ctrl, (p1_box.x + 15, p1_box.y + 38))

        # Bando 2
        p2_box = pygame.Rect(rect_card.right - 400, 370, 360, 70)
        pygame.draw.rect(self.pantalla, (45, 25, 18), p2_box, border_radius=8)
        p2_titulo = self.font_ui.render("JUGADOR 2 (Naranja)", True, COLOR_P2)
        p2_ctrl = self.font_small.render("Mover: [FLECHAS] | Disparar: [ENTER]", True, COLOR_WHITE)
        self.pantalla.blit(p2_titulo, (p2_box.x + 15, p2_box.y + 12))
        self.pantalla.blit(p2_ctrl, (p2_box.x + 15, p2_box.y + 38))

        # Llamada a la acción
        pulso = int(math.sin(pygame.time.get_ticks() * 0.005) * 20) + 235
        color_cta = (pulso, pulso, 80)
        cta = self.font_subtitulo.render("PRESIONA [ESPACIO] O [ENTER] PARA COMENZAR", True, color_cta)
        rect_cta = cta.get_rect(center=(SCREEN_WIDTH // 2, 520))
        self.pantalla.blit(cta, rect_cta)

        salida = self.font_small.render("[ESC] para salir del juego", True, COLOR_GRAY)
        self.pantalla.blit(salida, salida.get_rect(center=(SCREEN_WIDTH // 2, 570)))

    def dibujar_fin(self):
        # Dibujar el juego oscurecido de fondo
        self.dibujar_juego()

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 12, 18, 205))
        self.pantalla.blit(overlay, (0, 0))

        # Panel de victoria
        card = pygame.Rect(SCREEN_WIDTH // 2 - 350, SCREEN_HEIGHT // 2 - 170, 700, 340)
        pygame.draw.rect(self.pantalla, (24, 28, 42), card, border_radius=16)
        pygame.draw.rect(self.pantalla, COLOR_HAZARD, card, width=3, border_radius=16)

        sub_titulo = self.font_subtitulo.render("¡PARTIDA CONCLUIDA!", True, COLOR_WHITE)
        self.pantalla.blit(sub_titulo, sub_titulo.get_rect(center=(SCREEN_WIDTH // 2, card.y + 45)))

        # Anuncio del ganador
        color_ganador = COLOR_P1 if "1" in str(self.ganador) else COLOR_P2
        if "EMPATE" in str(self.ganador):
            color_ganador = (255, 215, 0)

        txt_ganador = self.font_titulo.render(f"¡{self.ganador} GANA!", True, color_ganador)
        self.pantalla.blit(txt_ganador, txt_ganador.get_rect(center=(SCREEN_WIDTH // 2, card.y + 115)))

        explicacion = self.font_ui.render("¡Ha logrado destruir toda su salud primero que el rival!", True, (210, 215, 230))
        self.pantalla.blit(explicacion, explicacion.get_rect(center=(SCREEN_WIDTH // 2, card.y + 175)))

        reiniciar = self.font_subtitulo.render("Presiona [R] para Revancha Rápida", True, (80, 240, 120))
        self.pantalla.blit(reiniciar, reiniciar.get_rect(center=(SCREEN_WIDTH // 2, card.y + 240)))

        volver = self.font_small.render("Presiona [ESPACIO / ENTER] para Menú Principal", True, COLOR_GRAY)
        self.pantalla.blit(volver, volver.get_rect(center=(SCREEN_WIDTH // 2, card.y + 285)))

    def ejecutar(self):
        ejecutando = True
        while ejecutando:
            ejecutando = self.manejar_eventos()
            self.actualizar()

            if self.estado == self.ESTADO_MENU:
                self.dibujar_menu()
            elif self.estado == self.ESTADO_JUGANDO:
                self.dibujar_juego()
            elif self.estado == self.ESTADO_FIN:
                self.dibujar_fin()

            pygame.display.flip()
            self.reloj.tick(FPS)

        pygame.quit()
        sys.exit()


# =============================================================================
# PUNTO DE ENTRADA
# =============================================================================
if __name__ == "__main__":
    juego = SuicideArenaGame()
    juego.ejecutar()

