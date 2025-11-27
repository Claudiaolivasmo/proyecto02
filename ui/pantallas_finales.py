import pygame
from typing import Optional


class FinalScreen:
	"""Base para pantallas finales (POO)."""
	def __init__(self, width: int = 800, height: int = 600):
		self.width = width
		self.height = height
		self.bg_color = (18, 18, 30)
		self.screen = pygame.display.set_mode((self.width, self.height))
		pygame.display.set_caption("Resultado")
		self.clock = pygame.time.Clock()
		# Fuentes reutilizables
		self.font_title = pygame.font.Font(None, 64)
		self.font_sub = pygame.font.Font(None, 36)
		self.font_text = pygame.font.Font(None, 28)

	def _draw_button(self, rect, text, hover=False):
		color = (180, 70, 70) if not hover else (210, 90, 90)
		pygame.draw.rect(self.screen, color, rect, border_radius=8)
		text_surf = self.font_text.render(text, True, (255, 255, 255))
		self.screen.blit(text_surf, (rect.x + rect.w // 2 - text_surf.get_width() // 2,
									 rect.y + rect.h // 2 - text_surf.get_height() // 2))


class WinScreen(FinalScreen):
	"""Pantalla que muestra que el jugador ganó."""
	def __init__(self, width: int = 800, height: int = 600, title: str = "¡Ganaste!"):
		super().__init__(width, height)
		self.title = title

	def show(self, message: Optional[str] = None):
		running = True
		back_rect = pygame.Rect(self.width // 2 - 150, self.height - 110, 300, 60)

		while running:
			mouse_pos = pygame.mouse.get_pos()
			hover_back = back_rect.collidepoint(mouse_pos)

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						running = False
				if event.type == pygame.MOUSEBUTTONDOWN:
					if back_rect.collidepoint(event.pos):
						running = False

			# Dibujado
			self.screen.fill(self.bg_color)
			# Título
			title_surf = self.font_title.render(self.title, True, (255, 250, 200))
			self.screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 60))

			# Mensaje opcional
			if message:
				msg_surf = self.font_sub.render(message, True, (160, 255, 160))
				self.screen.blit(msg_surf, (self.width // 2 - msg_surf.get_width() // 2, 150))

			# Decoración: estrellas
			star = self.font_sub.render("⭐ ⭐ ⭐", True, (255, 215, 0))
			self.screen.blit(star, (self.width // 2 - star.get_width() // 2, 220))

			# Texto de felicitación
			info = self.font_text.render("Has completado el nivel. Excelente trabajo!", True, (200, 200, 200))
			self.screen.blit(info, (self.width // 2 - info.get_width() // 2, 300))

			# Botón volver
			self._draw_button(back_rect, "← Volver", hover_back)

			pygame.display.flip()
			self.clock.tick(60)


class LoseScreen(FinalScreen):
	"""Pantalla que muestra que el jugador perdió."""
	def __init__(self, width: int = 800, height: int = 600, title: str = "Has Perdido"):
		super().__init__(width, height)
		self.title = title

	def show(self, message: Optional[str] = None):
		running = True
		back_rect = pygame.Rect(self.width // 2 - 150, self.height - 110, 300, 60)

		while running:
			mouse_pos = pygame.mouse.get_pos()
			hover_back = back_rect.collidepoint(mouse_pos)

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						running = False
				if event.type == pygame.MOUSEBUTTONDOWN:
					if back_rect.collidepoint(event.pos):
						running = False

			# Dibujado
			self.screen.fill((25, 10, 20))
			title_surf = self.font_title.render(self.title, True, (255, 180, 180))
			self.screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 60))

			if message:
				msg_surf = self.font_sub.render(message, True, (255, 140, 140))
				self.screen.blit(msg_surf, (self.width // 2 - msg_surf.get_width() // 2, 150))

			# Decoración: nubes de derrota
			sad = self.font_sub.render("☹ ☹", True, (200, 120, 120))
			self.screen.blit(sad, (self.width // 2 - sad.get_width() // 2, 220))

			info = self.font_text.render("Intenta de nuevo para superar el nivel.", True, (220, 220, 220))
			self.screen.blit(info, (self.width // 2 - info.get_width() // 2, 300))

			# Botón volver
			self._draw_button(back_rect, "← Volver", hover_back)

			pygame.display.flip()
			self.clock.tick(60)


if __name__ == '__main__':
	# Demo rápido: cambia estas banderas a True/False para ver cada pantalla
	SHOW_WIN = True
	SHOW_LOSE = False

	pygame.init()
	pygame.font.init()

	if SHOW_WIN:
		w = WinScreen()
		w.show(message="Puntaje: 3000 pts")
	elif SHOW_LOSE:
		l = LoseScreen()
		l.show(message="Te quedaste sin vidas")
	else:
		print("Cambiar SHOW_WIN o SHOW_LOSE a True para ver las pantallas de demo.")

