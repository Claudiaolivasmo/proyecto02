import pygame
import pygame_menu

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ejemplo 2 pantallas")

# Crear los menúes PRIMERO para poder conectarlos
# IMPORTANTE: Los menúes deben crearse antes de ser usados en los botones
theme_main = pygame_menu.Theme(
    background_color=(30, 30, 60),
    title_background_color=(0, 120, 200),
    widget_font_size=30,
    title_font_size=50,
    widget_padding=20,
)

menu_principal = pygame_menu.Menu("Pantalla Principal", WIDTH, HEIGHT, theme=theme_main)

# Tema para la pantalla secundaria
theme_two = pygame_menu.Theme(
    background_color=(60, 30, 30),
    title_background_color=(200, 80, 0),
    widget_font_size=30,
    title_font_size=50,
    widget_padding=20,
)

submenu = pygame_menu.Menu("Pantalla 2", WIDTH, HEIGHT, theme=theme_two)

# Configurar menú principal
menu_principal.add.label("Bienvenido", font_size=35)
menu_principal.add.vertical_margin(30)
# BOTÓN QUE NAVEGA A SUBMENU (pasando el menú directamente, no una función)
menu_principal.add.button("Ir a Pantalla 2", submenu)
menu_principal.add.button("Salir", pygame_menu.events.EXIT)

# Configurar pantalla secundaria
submenu.add.label("Esta es la segunda pantalla", font_size=30)
submenu.add.vertical_margin(30)
# ⭐ BOTÓN VOLVER: Este es el botón que cierra la pantalla secundaria
# pygame_menu.events.BACK solo funciona si el menú está conectado en jerarquía
# (como cuando pasamos submenu como argumento del botón anterior)
submenu.add.button("← Volver", pygame_menu.events.BACK)

# Ejecutar
if __name__ == "__main__":
    # Solo UN mainloop principal que maneja ambas pantallas
    # Los menúes están conectados jerárquicamente, por eso BACK funciona
    menu_principal.mainloop(screen)
