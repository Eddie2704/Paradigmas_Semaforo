# vehiculo.py
import pygame
import random

class Vehiculo:
    def __init__(self, direccion, tipo="NORMAL", pos_calle=None):
        self.direccion = direccion  # "NORTE", "SUR", "ESTE", "OESTE"
        self.tipo = tipo            # "NORMAL" o "AMBULANCIA"

        # Pegatina de identificación única para emergencias
        self.rfid_tag = "AMB-UNAH-911" if tipo == "AMBULANCIA" else None
        
        # Velocidades
        self.velocidad_maxima = 4 if self.tipo == "AMBULANCIA" else 2
        self.velocidad = self.velocidad_maxima
        self.en_fila = False  

        # --- COORDINADAS EXACTAS BASADAS EN TU MAPA (Ancho de calle: 100px) ---
        if self.direccion == "NORTE":    
            calle_x = pos_calle if pos_calle is not None else 250
            # Carril derecho subiendo: zona derecha de la calle (x + 75)
            self.x = (calle_x + 75) - 12  
            self.y = 700                 
            self.ancho, self.alto = 24, 40

        elif self.direccion == "SUR":    
            calle_x = pos_calle if pos_calle is not None else 250
            # Carril derecho bajando: zona izquierda de la calle (x + 25)
            self.x = (calle_x + 25) - 12   
            self.y = -40                 
            self.ancho, self.alto = 24, 40

        elif self.direccion == "ESTE":   
            calle_y = pos_calle if pos_calle is not None else 120
            self.x = -40                 
            # Carril derecho hacia la derecha: zona inferior de la calle (y + 75)
            self.y = (calle_y + 75) - 12   
            self.ancho, self.alto = 40, 24

        elif self.direccion == "OESTE":  
            calle_y = pos_calle if pos_calle is not None else 120
            self.x = 1150                
            # Carril derecho hacia la izquierda: zona superior de la calle (y + 25)
            self.y = (calle_y + 25) - 12  
            self.ancho, self.alto = 40, 24

        # Colores
        if self.tipo == "AMBULANCIA":
            self.color = (240, 240, 240)
        else:
            self.color = (random.randint(50, 220), random.randint(50, 220), random.randint(150, 255))

        self.frame_luces = 0

    def obtener_rect(self):
        return pygame.Rect(self.x, self.y, self.ancho, self.alto)

    def actualizar(self, semaforos, otros_vehiculos, diccionario_tiempos=None):
        pueden_avanzar = True
        self.en_fila = False

        if diccionario_tiempos is None:
            diccionario_tiempos = {}

        # --- LÓGICA 1: FRENADO EXACTO Y ANTICIPACIÓN DE CAMBIO DE SEMÁFORO ---
        if self.tipo != "AMBULANCIA":
            CX = [250, 750]
            CY = [120, 470]

            # Direcciones y mapeo de semáforos por cruce
            # 0: s_norte, 1: s_sur, 2: s_este, 3: s_oeste
            if self.direccion == "NORTE":
                for index_y, cy in enumerate(CY):
                    linea_parada = cy + 100 
                    if linea_parada < self.y <= linea_parada + 45:
                        idx_cruce = (0 if self.x < 500 else 2) + index_y
                        sem_actual = semaforos[idx_cruce * 4 + 1] # s_sur
                        
                        # Obtener tiempo restante del controlador
                        fase, tiempo_restante = diccionario_tiempos.get(idx_cruce, (0, 99))
                        
                        # Frena si está en Rojo/Amarillo O si está en Verde pero falta menos de 0.5s
                        if sem_actual.estado in ["rojo", "amarillo"] or (sem_actual.estado == "verde" and tiempo_restante <= 0.5):
                            pueden_avanzar = False
                            self.en_fila = True

            elif self.direccion == "SUR":
                for index_y, cy in enumerate(CY):
                    linea_parada = cy - self.alto
                    if linea_parada - 45 <= self.y < linea_parada:
                        idx_cruce = (0 if self.x < 500 else 2) + index_y
                        sem_actual = semaforos[idx_cruce * 4 + 0] # s_norte
                        
                        fase, tiempo_restante = diccionario_tiempos.get(idx_cruce, (0, 99))
                        
                        if sem_actual.estado in ["rojo", "amarillo"] or (sem_actual.estado == "verde" and tiempo_restante <= 0.5):
                            pueden_avanzar = False
                            self.en_fila = True

            elif self.direccion == "ESTE":
                for index_x, cx in enumerate(CX):
                    linea_parada = cx - self.ancho 
                    if linea_parada - 45 <= self.x < linea_parada:
                        fila = 0 if self.y < 300 else 1
                        idx_cruce = index_x * 2 + fila
                        sem_actual = semaforos[idx_cruce * 4 + 2] # s_este
                        
                        fase, tiempo_restante = diccionario_tiempos.get(idx_cruce, (0, 99))
                        
                        if sem_actual.estado in ["rojo", "amarillo"] or (sem_actual.estado == "verde" and tiempo_restante <= 0.5):
                            pueden_avanzar = False
                            self.en_fila = True

            elif self.direccion == "OESTE":
                for index_x, cx in enumerate(CX):
                    linea_parada = cx + 100
                    if linea_parada < self.x <= linea_parada + 45:
                        fila = 0 if self.y < 300 else 1
                        idx_cruce = index_x * 2 + fila
                        sem_actual = semaforos[idx_cruce * 4 + 3] # s_oeste
                        
                        fase, tiempo_restante = diccionario_tiempos.get(idx_cruce, (0, 99))
                        
                        if sem_actual.estado in ["rojo", "amarillo"] or (sem_actual.estado == "verde" and tiempo_restante <= 0.5):
                            pueden_avanzar = False
                            self.en_fila = True

        # --- LÓGICA 2: EVITAR CHOQUES (Mantener fila india) ---
        distancia_seguridad = 15  
        for otro in otros_vehiculos:
            if otro == self or otro.direccion != self.direccion:
                continue  

            if self.direccion in ["NORTE", "SUR"] and abs(self.x - otro.x) > 10:
                continue
            if self.direccion in ["ESTE", "OESTE"] and abs(self.y - otro.y) > 10:
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

        # Torretas Ambulancia
        if self.tipo == "AMBULANCIA":
            self.frame_luces += 1
            color_l1 = (255, 0, 0) if (self.frame_luces // 15) % 2 == 0 else (0, 0, 255)
            color_l2 = (0, 0, 255) if (self.frame_luces // 15) % 2 == 0 else (255, 0, 0)
            
            pygame.draw.rect(screen, (255, 0, 0), (self.x + self.ancho//2 - 2, self.y + self.alto//2 - 6, 4, 12))
            pygame.draw.rect(screen, (255, 0, 0), (self.x + self.ancho//2 - 6, self.y + self.alto//2 - 2, 12, 4))

            if self.direccion in ["NORTE", "SUR"]:
                pygame.draw.rect(screen, color_l1, (self.x + 2, self.y, 6, 4))
                pygame.draw.rect(screen, color_l2, (self.x + self.ancho - 8, self.y, 6, 4))
            else:
                pygame.draw.rect(screen, color_l1, (self.x, self.y + 2, 4, 6))
                pygame.draw.rect(screen, color_l2, (self.x, self.y + self.alto - 8, 4, 6))























