import pygame
import random

class Vehiculo:
    def __init__(self, direccion):
        self.direccion = direccion  # "NORTE", "SUR", "ESTE", "OESTE"
        self.velocidad_maxima = 2
        self.velocidad = self.velocidad_maxima
        self.en_fila = False  # Indica si el auto está detenido esperando en el tráfico

        # 1. Posiciones iniciales y dimensiones según el carril (Manejando por la derecha)
        # Cada carril mide 50px de ancho. Los autos miden 24px de ancho por 40px de largo.
        if self.direccion == "NORTE":    # Viene de abajo (SUR) y sube hacia el NORTE
            self.x = 425 - 12            # Centrado en el carril derecho vertical (x=413)
            self.y = 600                 # Borde inferior
            self.ancho, self.alto = 24, 40
        elif self.direccion == "SUR":    # Viene de arriba (NORTE) y baja hacia el SUR
            self.x = 375 - 12            # Centrado en el carril izquierdo vertical (x=363)
            self.y = -40                 # Borde superior
            self.ancho, self.alto = 24, 40
        elif self.direccion == "ESTE":   # Viene de la izquierda (OESTE) y va hacia el ESTE
            self.x = -40                 # Borde izquierdo
            self.y = 325 - 12            # Centrado en el carril inferior horizontal (y=313)
            self.ancho, self.alto = 40, 24
        elif self.direccion == "OESTE":  # Viene de la derecha (ESTE) y va hacia el OESTE
            self.x = 800                 # Borde derecho
            self.y = 275 - 12            # Centrado en el carril superior horizontal (y=263)
            self.ancho, self.alto = 40, 24

        # 2. Asignar un color aleatorio para variedad visual
        self.color = (random.randint(50, 220), random.randint(50, 220), random.randint(150, 255))

    def obtener_rect(self):
        """ Retorna el objeto Rect de Pygame para facilitar detección de colisiones y distancias """
        return pygame.Rect(self.x, self.y, self.ancho, self.alto)

    def actualizar(self, semaforos, otros_vehiculos):
        """
        Controla toda la física, frenado por semáforo en rojo y frenado por tráfico (filas)
        """
        pueden_avanzar = True
        self.en_fila = False

        # --- LÓGICA 1: FRENADO POR SEMÁFORO EN ROJO ---
        # Verificamos si el auto está justo llegando a la zona de parada y el semáforo está en rojo
        if self.direccion == "NORTE":
            sem_sur = semaforos[1]  # Controla los que van de sur a norte
            if sem_sur.estado == "rojo" and 350 < self.y <= 410:
                pueden_avanzar = False
                self.en_fila = True
                
        elif self.direccion == "SUR":
            sem_norte = semaforos[0]  # Controla los que van de norte a sur
            if sem_norte.estado == "rojo" and 150 <= self.y < 210:
                pueden_avanzar = False
                self.en_fila = True
                
        elif self.direccion == "ESTE":
            sem_oeste = semaforos[2]  # Controla los que van de oeste a este
            if sem_oeste.estado == "rojo" and 250 <= self.x < 310:
                pueden_avanzar = False
                self.en_fila = True
                
        elif self.direccion == "OESTE":
            sem_este = semaforos[3]  # Controla los que van de este a oeste
            if sem_este.estado == "rojo" and 450 < self.x <= 510:
                pueden_avanzar = False
                self.en_fila = True

        # --- LÓGICA 2: EVITAR CHOQUES ENTRE AUTOS (CREAR FILAS DE ESPERA) ---
        # Si ya pasó el filtro del semáforo, revisamos si tiene un carro adelante en su misma dirección
        if pueden_avanzar:
            rect_propio = self.obtener_rect()
            distancia_seguridad = 15  # Píxeles de separación entre defensas

            for otro in otros_vehiculos:
                if otro == self or otro.direccion != self.direccion:
                    continue  # Ignorar a sí mismo y a autos de otras calles

                # Comprobar si el 'otro' auto está adelante en la ruta
                if self.direccion == "NORTE" and otro.y < self.y:
                    if self.y - (otro.y + otro.alto) <= distancia_seguridad:
                        pueden_avanzar = False
                        if otro.en_fila or otro.velocidad == 0:
                            self.en_fila = True

                elif self.direccion == "SUR" and otro.y > self.y:
                    if otro.y - (self.y + self.alto) <= distancia_seguridad:
                        pueden_avanzar = False
                        if otro.en_fila or otro.velocidad == 0:
                            self.en_fila = True

                elif self.direccion == "ESTE" and otro.x > self.x:
                    if otro.x - (self.x + self.ancho) <= distancia_seguridad:
                        pueden_avanzar = False
                        if otro.en_fila or otro.velocidad == 0:
                            self.en_fila = True

                elif self.direccion == "OESTE" and otro.x < self.x:
                    if self.x - (otro.x + otro.ancho) <= distancia_seguridad:
                        pueden_avanzar = False
                        if otro.en_fila or otro.velocidad == 0:
                            self.en_fila = True

        # --- LÓGICA 3: MOVIMIENTO APLICADO ---
        if pueden_avanzar:
            self.velocidad = self.velocidad_maxima
            if self.direccion == "NORTE":   self.y -= self.velocidad
            elif self.direccion == "SUR":   self.y += self.velocidad
            elif self.direccion == "ESTE":  self.x += self.velocidad
            elif self.direccion == "OESTE": self.x -= self.velocidad
        else:
            self.velocidad = 0  # Completamente detenido

    def dibujar(self, screen):
        """ Dibuja el chasis del vehículo y detalles de ventanas para mayor nitidez """
        # Chasis principal
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.ancho, self.alto))
        
        # Bordes del auto para que resalte
        pygame.draw.rect(screen, (20, 20, 20), (self.x, self.y, self.ancho, self.alto), 1)

        # Cristal / Ventana delantera (orientada según hacia dónde avanza)
        color_cristal = (50, 50, 50)
        if self.direccion == "NORTE":
            pygame.draw.rect(screen, color_cristal, (self.x + 3, self.y + 8, self.ancho - 6, 6))
        elif self.direccion == "SUR":
            pygame.draw.rect(screen, color_cristal, (self.x + 3, self.y + self.alto - 14, self.ancho - 6, 6))
        elif self.direccion == "ESTE":
            pygame.draw.rect(screen, color_cristal, (self.x + self.ancho - 14, self.y + 3, 6, self.alto - 6))
        elif self.direccion == "OESTE":
            pygame.draw.rect(screen, color_cristal, (self.x + 8, self.y + 3, 6, self.alto - 6))