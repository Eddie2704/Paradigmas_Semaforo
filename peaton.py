import pygame
import random

class Peaton:
    def __init__(self, cruce):
        self.cruce = cruce  # "NORTE", "SUR", "ESTE", "OESTE" (Cruce donde aparecerá)
        self.velocidad = 1
        self.cruzando = False

        # Configurar posición inicial según el cruce (Aparecen en la acera/borde listo para cruzar)
        if self.cruce == "NORTE":    # Cruce peatonal superior (camina horizontalmente de izq a der)
            self.x = 330
            self.y = 190
        elif self.cruce == "SUR":    # Cruce peatonal inferior (camina horizontalmente de izq a der)
            self.x = 330
            self.y = 410
        elif self.cruce == "OESTE":  # Cruce peatonal izquierdo (camina verticalmente de arriba a abajo)
            self.x = 290
            self.y = 230
        elif self.cruce == "ESTE":   # Cruce peatonal derecho (camina verticalmente de arriba a abajo)
            self.x = 510
            self.y = 230

        # Color aleatorio para la ropa del peatón
        self.color = (random.randint(150, 255), random.randint(50, 150), random.randint(50, 150))
        self.radio = 6

    def actualizar(self, semaforos_peatonales):
        """ Controla si el peatón espera o camina según el semáforo peatonal """
        
        # Mapeo de cuál semáforo peatonal le corresponde mirar
        # 0: arriba-izq, 1: arriba-der, 2: abajo-izq, 3: abajo-der
        sem_correspondiente = None
        if self.cruce == "NORTE":   sem_correspondiente = semaforos_peatonales[0]
        elif self.cruce == "ESTE":  sem_correspondiente = semaforos_peatonales[1]
        elif self.cruce == "SUR":   sem_correspondiente = semaforos_peatonales[2]
        elif self.cruce == "OESTE": sem_correspondiente = semaforos_peatonales[3]

        # Si el semáforo peatonal está en verde, el peatón tiene autorización para cruzar
        if sem_correspondiente and sem_correspondiente.estado == "verde":
            self.cruzando = True

        # Si está autorizado a cruzar, se mueve hasta el otro lado de la calle
        if self.cruzando:
            if self.cruce == "NORTE" or self.cruce == "SUR":
                self.x += self.velocidad  # Cruza la calle vertical de izquierda a derecha
            elif self.cruce == "OESTE" or self.cruce == "ESTE":
                self.y += self.velocidad  # Cruza la calle horizontal de arriba a abajo

    def dibujar(self, screen):
        """ Dibuja al peatón como un círculo con un pequeño borde dinámico """
        # Cuerpo (cabeza/cuerpo desde arriba)
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radio)
        # Borde para definir nitidez
        pygame.draw.circle(screen, (20, 20, 20), (int(self.x), int(self.y)), self.radio, 1)