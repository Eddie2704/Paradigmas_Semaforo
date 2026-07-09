import pygame

class Semaforo:
    def __init__(self, x, y, orientacion="vertical"):
        self.x = x
        self.y = y
        self.estado = "rojo"
        self.orientacion = orientacion

    def cambiar_estado(self):
        if self.estado == "rojo":
            self.estado = "verde"
        elif self.estado == "verde":
            self.estado = "amarillo"
        else:
            self.estado = "rojo"

    def dibujar(self, screen):
        colores = {"rojo": (255,0,0), "amarillo": (255,255,0), "verde": (0,255,0)}

        if self.orientacion == "vertical":
            pygame.draw.rect(screen, (30,30,30), (self.x, self.y, 15, 45))
            pygame.draw.circle(screen, colores["rojo"] if self.estado=="rojo" else (100,0,0), (self.x+7, self.y+7), 5)
            pygame.draw.circle(screen, colores["amarillo"] if self.estado=="amarillo" else (100,100,0), (self.x+7, self.y+22), 5)
            pygame.draw.circle(screen, colores["verde"] if self.estado=="verde" else (0,100,0), (self.x+7, self.y+37), 5)

        else:  # horizontal
            pygame.draw.rect(screen, (30,30,30), (self.x, self.y, 45, 15))
            pygame.draw.circle(screen, colores["rojo"] if self.estado=="rojo" else (100,0,0), (self.x+7, self.y+7), 5)
            pygame.draw.circle(screen, colores["amarillo"] if self.estado=="amarillo" else (100,100,0), (self.x+22, self.y+7), 5)
            pygame.draw.circle(screen, colores["verde"] if self.estado=="verde" else (0,100,0), (self.x+37, self.y+7), 5)
