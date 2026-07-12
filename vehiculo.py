import pygame
import random

class Vehiculo:
    def __init__(self, direccion, tipo="NORMAL"):
        self.direccion = direccion  # "NORTE", "SUR", "ESTE", "OESTE"
        self.tipo = tipo            # "NORMAL" o "AMBULANCIA"

        # Pegatina de identificación única para emergencias
        self.rfid_tag = "AMB-UNAH-911" if tipo == "AMBULANCIA" else None
        
        # Si es ambulancia va más rápido, si es normal va a velocidad estándar
        self.velocidad_maxima = 4 if self.tipo == "AMBULANCIA" else 2
        self.velocidad = self.velocidad_maxima
        self.en_fila = False  

        # Posiciones iniciales (Manejando por la derecha)
        if self.direccion == "NORTE":    
            self.x = 425 - 12            
            self.y = 600                 
            self.ancho, self.alto = 24, 40
        elif self.direccion == "SUR":    
            self.x = 375 - 12            
            self.y = -40                 
            self.ancho, self.alto = 24, 40
        elif self.direccion == "ESTE":   
            self.x = -40                 
            self.y = 325 - 12            
            self.ancho, self.alto = 40, 24
        elif self.direccion == "OESTE":  
            self.x = 800                 
            self.y = 275 - 12            
            self.ancho, self.alto = 40, 24

        # Colores diferenciados
        if self.tipo == "AMBULANCIA":
            self.color = (240, 240, 240)  # Blanco para la ambulancia
        else:
            self.color = (random.randint(50, 220), random.randint(50, 220), random.randint(150, 255))

        # Contador de frames para hacer parpadear las torretas de la ambulancia
        self.frame_luces = 0

    def obtener_rect(self):
        return pygame.Rect(self.x, self.y, self.ancho, self.alto)

    def actualizar(self, semaforos, otros_vehiculos):
        pueden_avanzar = True
        self.en_fila = False

        # --- LÓGICA 1: FRENADO POR SEMÁFORO EN ROJO (Ajustado antes del paso de cebra) ---
        if self.tipo != "AMBULANCIA":
            if self.direccion == "NORTE":
                sem_sur = semaforos[1]  # Controla los que van de sur a norte
                # Antes: 350 < self.y <= 410 -> Ahora frena antes en y=440
                if sem_sur.estado == "rojo" and 390 < self.y <= 450:
                    pueden_avanzar = False
                    self.en_fila = True
                    
            elif self.direccion == "SUR":
                sem_norte = semaforos[0]  # Controla los que van de norte a sur
                # Antes: 150 <= self.y < 210 -> Ahora frena antes en y=120 (restando el largo del auto)
                if sem_norte.estado == "rojo" and 110 <= self.y < 160:
                    pueden_avanzar = False
                    self.en_fila = True
                    
            elif self.direccion == "ESTE":
                sem_oeste = semaforos[2]  # Controla los que van de oeste a este
                # Antes: 250 <= self.x < 310 -> Ahora frena antes en x=220 (restando el ancho del auto)
                if sem_oeste.estado == "rojo" and 210 <= self.x < 260:
                    pueden_avanzar = False
                    self.en_fila = True
                    
            elif self.direccion == "OESTE":
                sem_este = semaforos[3]  # Controla los que van de este a oeste
                # Antes: 450 < self.x <= 510 -> Ahora frena antes en x=540
                if sem_este.estado == "rojo" and 490 < self.x <= 550:
                    pueden_avanzar = False
                    self.en_fila = True
        # --- LÓGICA 2: EVITAR CHOQUES ---
        # Las ambulancias frenan si tienen un auto enfrente, y los autos se quitan o hacen fila si ven una ambulancia
        rect_propio = self.obtener_rect()
        distancia_seguridad = 15  

        for otro in otros_vehiculos:
            if otro == self or otro.direccion != self.direccion:
                continue  

            if self.direccion == "NORTE" and otro.y < self.y:
                if self.y - (otro.y + otro.alto) <= distancia_seguridad:
                    pueden_avanzar = False
                    if otro.en_fila or otro.velocidad == 0: self.en_fila = True

            elif self.direccion == "SUR" and otro.y > self.y:
                if otro.y - (self.y + self.alto) <= distancia_seguridad:
                    pueden_avanzar = False
                    if otro.en_fila or otro.velocidad == 0: self.en_fila = True

            elif self.direccion == "ESTE" and otro.x > self.x:
                if otro.x - (self.x + self.ancho) <= distancia_seguridad:
                    pueden_avanzar = False
                    if otro.en_fila or otro.velocidad == 0: self.en_fila = True

            elif self.direccion == "OESTE" and otro.x < self.x:
                if self.x - (otro.x + otro.ancho) <= distancia_seguridad:
                    pueden_avanzar = False
                    if otro.en_fila or otro.velocidad == 0: self.en_fila = True

        # --- LÓGICA 3: MOVIMIENTO ---
        if pueden_avanzar:
            self.velocidad = self.velocidad_maxima
            if self.direccion == "NORTE":   self.y -= self.velocidad
            elif self.direccion == "SUR":   self.y += self.velocidad
            elif self.direccion == "ESTE":  self.x += self.velocidad
            elif self.direccion == "OESTE": self.x -= self.velocidad
        else:
            self.velocidad = 0  

    def dibujar(self, screen):
        # Chasis base
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.ancho, self.alto))
        pygame.draw.rect(screen, (20, 20, 20), (self.x, self.y, self.ancho, self.alto), 1)

        # Cristal / Ventana
        color_cristal = (50, 50, 50)
        if self.direccion == "NORTE":
            pygame.draw.rect(screen, color_cristal, (self.x + 3, self.y + 8, self.ancho - 6, 6))
        elif self.direccion == "SUR":
            pygame.draw.rect(screen, color_cristal, (self.x + 3, self.y + self.alto - 14, self.ancho - 6, 6))
        elif self.direccion == "ESTE":
            pygame.draw.rect(screen, color_cristal, (self.x + self.ancho - 14, self.y + 3, 6, self.alto - 6))
        elif self.direccion == "OESTE":
            pygame.draw.rect(screen, color_cristal, (self.x + 8, self.y + 3, 6, self.alto - 6))

        # --- DETALLE EXCLUSIVO: TORRETAS DE AMBULANCIA ---
        if self.tipo == "AMBULANCIA":
            self.frame_luces += 1
            # Alternar colores cada 15 frames para simular el parpadeo de emergencia
            color_l1 = (255, 0, 0) if (self.frame_luces // 15) % 2 == 0 else (0, 0, 255)
            color_l2 = (0, 0, 255) if (self.frame_luces // 15) % 2 == 0 else (255, 0, 0)
            
            # Cruz roja decorativa en el techo
            pygame.draw.rect(screen, (255, 0, 0), (self.x + self.ancho//2 - 2, self.y + self.alto//2 - 6, 4, 12))
            pygame.draw.rect(screen, (255, 0, 0), (self.x + self.ancho//2 - 6, self.y + self.alto//2 - 2, 12, 4))

            # Pintar las luces estroboscópicas según la orientación del vehículo
            if self.direccion in ["NORTE", "SUR"]:
                pygame.draw.rect(screen, color_l1, (self.x + 2, self.y, 6, 4))
                pygame.draw.rect(screen, color_l2, (self.x + self.ancho - 8, self.y, 6, 4))
            else:
                pygame.draw.rect(screen, color_l1, (self.x, self.y + 2, 4, 6))
                pygame.draw.rect(screen, color_l2, (self.x, self.y + self.alto - 8, 4, 6))