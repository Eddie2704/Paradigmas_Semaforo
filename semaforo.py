import pygame

class Semaforo:
    def __init__(self, x, y, orientacion="vertical"):
        self.x = x
        self.y = y
        self.estado = "rojo"
        self.orientacion = orientacion
        
        # Inicializar la fuente para el panel digital
        pygame.font.init()
        # Usamos una fuente pequeña debido al tamaño compacto de tus semáforos (15px de ancho)
        self.fuente = pygame.font.SysFont("Courier New", 12, bold=True)

    def cambiar_estado(self):
        if self.estado == "rojo":
            self.estado = "verde"
        elif self.estado == "verde":
            self.estado = "amarillo"
        else:
            self.estado = "rojo"

    def dibujar(self, screen, tiempo_restante=None):
        colores = {"rojo": (255, 0, 0), "amarillo": (255, 255, 0), "verde": (0, 255, 0)}

        if self.orientacion == "vertical":
            # Cuerpo original (15x45) + Extensión de 18px abajo para la pantalla digital = 15x63
            pygame.draw.rect(screen, (30, 30, 30), (self.x, self.y, 15, 63))
            
            # Círculos convencionales (Tus posiciones originales)
            pygame.draw.circle(screen, colores["rojo"] if self.estado == "rojo" else (100, 0, 0), (self.x + 7, self.y + 7), 5)
            pygame.draw.circle(screen, colores["amarillo"] if self.estado == "amarillo" else (100, 100, 0), (self.x + 7, self.y + 22), 5)
            pygame.draw.circle(screen, colores["verde"] if self.estado == "verde" else (0, 100, 0), (self.x + 7, self.y + 37), 5)
            
            # Caja de la minipantalla digital (Cuarta sección inferior)
            rect_pantalla = pygame.Rect(self.x + 1, self.y + 47, 13, 14)
            pygame.draw.rect(screen, (10, 15, 10), rect_pantalla) # Fondo LCD oscuro

        else:  # horizontal
            # Cuerpo original (45x15) + Extensión de 18px a la derecha para la pantalla digital = 63x15
            pygame.draw.rect(screen, (30, 30, 30), (self.x, self.y, 63, 15))
            
            # Círculos convencionales (Tus posiciones originales)
            pygame.draw.circle(screen, colores["rojo"] if self.estado == "rojo" else (100, 0, 0), (self.x + 7, self.y + 7), 5)
            pygame.draw.circle(screen, colores["amarillo"] if self.estado == "amarillo" else (100, 100, 0), (self.x + 22, self.y + 7), 5)
            pygame.draw.circle(screen, colores["verde"] if self.estado == "verde" else (0, 100, 0), (self.x + 37, self.y + 7), 5)
            
            # Caja de la minipantalla digital (Cuarta sección derecha)
            rect_pantalla = pygame.Rect(self.x + 47, self.y + 1, 14, 13)
            pygame.draw.rect(screen, (10, 15, 10), rect_pantalla) # Fondo LCD oscuro

        # Renderizar la cuenta regresiva en el panel digital
        # Solo muestra números si está activo, no está en rojo, y no está en modo intermitente/apagado de madrugada
        if tiempo_restante is not None and tiempo_restante >= 0 and self.estado in ["verde", "amarillo"]:
            str_tiempo = str(int(tiempo_restante))
            
            # Color del número: verde brillante si el semáforo está verde, amarillo si está en amarillo
            color_texto = (0, 255, 0) if self.estado == "verde" else (255, 255, 0)
            
            texto_surface = self.fuente.render(str_tiempo, True, color_texto)
            texto_rect = texto_surface.get_rect(center=rect_pantalla.center)
            screen.blit(texto_surface, texto_rect)