# peaton.py
import pygame
import random

class Peaton:
    def __init__(self, cruce, pos_calle_v=250, pos_calle_h=120):
        self.cruce = cruce  # "NORTE", "SUR", "ESTE", "OESTE"
        self.pos_calle_v = pos_calle_v  # Coordenada X del cruce (250 o 750)
        self.pos_calle_h = pos_calle_h  # Coordenada Y del cruce (120 o 470)
        self.velocidad = 1
        self.cruzando = False

        # Guardamos a qué ID de intersección pertenece en base a sus coordenadas maestros
        columna = 0 if self.pos_calle_v < 500 else 1
        fila = 0 if self.pos_calle_h < 300 else 1
        self.idx_interseccion = columna * 2 + fila

        # --- ALINEACIÓN MATEMÁTICA EN LOS PASOS DE CEBRA DE LA RED ---
        if self.cruce == "NORTE":    
            # Paso peatonal SUPERIOR del cruce (Cruza horizontalmente de Izq a Der)
            self.x = self.pos_calle_v - 20        # Inicia en la acera izquierda
            self.y = self.pos_calle_h - 15        # Alineado al paso de cebra superior
            
        elif self.cruce == "SUR":    
            # Paso peatonal INFERIOR del cruce (Cruza horizontalmente de Izq a Der)
            self.x = self.pos_calle_v - 20        # Inicia en la acera izquierda
            self.y = self.pos_calle_h + 105       # Alineado al paso de cebra inferior
            
        elif self.cruce == "OESTE":  
            # Paso peatonal IZQUIERDO del cruce (Cruza verticalmente de Arriba a Abajo)
            self.x = self.pos_calle_v - 15        # Alineado al paso de cebra izquierdo
            self.y = self.pos_calle_h - 20        # Inicia en la acera superior
            
        elif self.cruce == "ESTE":   
            # Paso peatonal DERECHO del cruce (Cruza verticalmente de Arriba a Abajo)
            self.x = self.pos_calle_v + 105       # Alineado al paso de cebra derecho
            self.y = self.pos_calle_h - 20        # Inicia en la acera superior

        # Apariencia
        self.color = (random.randint(150, 255), random.randint(50, 150), random.randint(50, 150))
        self.radio = 6

    def actualizar(self, semaforos_peatonales):
        """ Asigna el semáforo exacto de su esquina dentro de la lista global de la red """
        
        # Cada cruce en main.py agrega exactamente 4 semáforos peatonales secuenciales:
        # sp1 (sup-izq)=0, sp2 (sup-der)=1, sp3 (inf-izq)=2, sp4 (inf-der)=3
        base_idx = self.idx_interseccion * 4
        
        sem_correspondiente = None
        if self.cruce == "NORTE":   sem_correspondiente = semaforos_peatonales[base_idx + 0] # sp1
        elif self.cruce == "ESTE":  sem_correspondiente = semaforos_peatonales[base_idx + 1] # sp2
        elif self.cruce == "SUR":   sem_correspondiente = semaforos_peatonales[base_idx + 2] # sp3
        elif self.cruce == "OESTE": sem_correspondiente = semaforos_peatonales[base_idx + 3] # sp4

        # Validación de seguridad e inicio de cruce
        if sem_correspondiente and sem_correspondiente.estado == "verde":
            self.cruzando = True

        # Comportamiento del movimiento si tiene luz verde
        if self.cruzando:
            if self.cruce in ["NORTE", "SUR"]:
                self.x += self.velocidad  # Camina limpiamente de izquierda a derecha por las líneas
            elif self.cruce in ["OESTE", "ESTE"]:
                self.y += self.velocidad  # Camina limpiamente de arriba a abajo por las líneas

    def dibujar(self, screen):
        # Renderizado nítido del círculo peatonal
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radio)
        pygame.draw.circle(screen, (20, 20, 20), (int(self.x), int(self.y)), self.radio, 1)