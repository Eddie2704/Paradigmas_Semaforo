import pygame

class SemaforoPeatonal:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.estado = "rojo"

    def cambiar_estado(self):
        self.estado = "verde" if self.estado == "rojo" else "rojo"

    def dibujar(self, screen):
        # Caja pequeña en la acera
        pygame.draw.rect(screen, (30,30,30), (self.x, self.y, 12, 24))
        color = (0,255,0) if self.estado=="verde" else (255,0,0)
        pygame.draw.circle(screen, color, (self.x+6, self.y+12), 5)
