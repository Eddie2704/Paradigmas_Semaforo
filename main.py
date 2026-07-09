import pygame
from mapa import dibujar_mapa
from semaforo import Semaforo
from semaforo_peatonal import SemaforoPeatonal
# Importamos tu clase Vehiculo desde tu archivo externo 'vehiculo.py'
from vehiculo import Vehiculo  

# CONFIGURACIÓN INICIAL DE PYGAME
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Simulador de Semáforo Inteligente")
clock = pygame.time.Clock()

#SEMÁFOROS
semaforos_autos = [
    Semaforo(410, 220, "horizontal"),  # índice 0: norte (controla autos que vienen del norte al sur)
    Semaforo(350, 360, "horizontal"),  # índice 1: sur (controla autos que vienen del sur al norte)
    Semaforo(330, 250, "vertical"),    # índice 2: oeste (controla autos que vienen del oeste al este)
    Semaforo(450, 310, "vertical")     # índice 3: este (controla autos que vienen del este al oeste)
]

# Semáforos peatonales 
semaforos_peatonales = [
    SemaforoPeatonal(320, 220),  # arriba-izquierda
    SemaforoPeatonal(470, 220),  # arriba-derecha
    SemaforoPeatonal(320, 365),  # abajo-izquierda
    SemaforoPeatonal(470, 365)   # abajo-derecha
]

# INICIALIZACIÓN DE VEHÍCULOS (Esperando en las filas)

# Creamos autos que inician su recorrido desde los extremos de la pantalla
# y se detendrán ordenadamente en sus respectivas líneas de parada al estar en rojo.
vehiculos = [
    Vehiculo("NORTE"),  # Fila SUR: viene de abajo (y=600) y sube hacia el norte
    Vehiculo("SUR"),    # Fila NORTE: viene de arriba (y=-40) y baja hacia el sur
    Vehiculo("ESTE"),   # Fila OESTE: viene de la izquierda (x=-40) y va hacia el este
    Vehiculo("OESTE")   # Fila ESTE: viene de la derecha (x=800) y va hacia el oeste
]

# BUCLE PRINCIPAL DE LA SIMULACIÓN
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            # Tecla "p" alterna manualmente los semáforos peatonales
            if event.key == pygame.K_p:  
                for sp in semaforos_peatonales:
                    sp.cambiar_estado()
                    
            # Tecla "c" alterna los semáforos de autos para darles paso libre
            if event.key == pygame.K_c:  
                for s in semaforos_autos:
                    s.cambiar_estado()

    # 1. Dibujar el mapa (Calles, cebras, césped y flechas direccionales)
    dibujar_mapa(screen)

    # 2. Actualizar lógica de movimiento, detección de colisiones y renderizado de autos
    for auto in vehiculos:
        # Pasamos tanto la lista de semáforos como la lista de los demás autos 
        # para que calcule el frenado en semáforo o el frenado en fila automática.
        auto.actualizar(semaforos_autos, vehiculos)  
        auto.dibujar(screen)

    # 3. Dibujar semáforos viales para automóviles
    for s in semaforos_autos:
        s.dibujar(screen)

    # 4. Dibujar semáforos para peatones
    for sp in semaforos_peatonales:
        sp.dibujar(screen)

    # Actualización de pantalla y control de FPS (60 fotogramas por segundo)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()