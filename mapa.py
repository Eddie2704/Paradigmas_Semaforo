# mapa.py
import pygame

def dibujar_mapa(screen):
    # 1. Fondo (Zonas verdes)
    screen.fill((34, 139, 34)) 

    # VEGETACIÓN
    def dibujar_arbol(cx, cy):
        pygame.draw.rect(screen, (101, 67, 33), (cx - 3, cy, 6, 15))
        pygame.draw.circle(screen, (20, 100, 20), (cx, cy), 15)
        pygame.draw.circle(screen, (46, 125, 50), (cx - 2, cy - 2), 11)

    arboles_posiciones = [
        (60, 40), (140, 50), (500, 40), (600, 50), (1000, 40),
        (50, 300), (120, 350), (520, 290), (600, 370), (1020, 310),
        (60, 620), (150, 640), (510, 630), (620, 620), (990, 640)
    ]
    for pos in arboles_posiciones:
        dibujar_arbol(pos[0], pos[1])

    # COORDENADAS DE LOS CRUCES
    CALLES_X = [250, 750]  
    CALLES_Y = [120, 470]  

    # 2. Calles (Asfalto Gris)
    for y in CALLES_Y:
        pygame.draw.rect(screen, (50, 50, 50), (0, y, 1150, 100))  
    for x in CALLES_X:
        pygame.draw.rect(screen, (50, 50, 50), (x, 0, 100, 700))   
    for x in CALLES_X:
        for y in CALLES_Y:
            pygame.draw.rect(screen, (50, 50, 50), (x, y, 100, 100)) 

    # 3. Líneas centrales discontinuas amarillas (CORTADAS ANTES DE LAS CEBRAS)
    for y in CALLES_Y:
        for x in range(0, 1150, 20):
            # No dibujar si está dentro de una intersección o en la zona de las cebras laterales (25px antes/después)
            if (225 <= x <= 375) or (725 <= x <= 875): continue
            pygame.draw.line(screen, (255, 215, 0), (x, y + 50), (x + 10, y + 50), 2)

    for x in CALLES_X:
        for y in range(0, 700, 20):
            # No dibujar si está dentro del cruce o en la zona de las cebras verticales
            if (95 <= y <= 245) or (445 <= y <= 595): continue
            pygame.draw.line(screen, (255, 215, 0), (x + 50, y), (x + 50, y + 10), 2)

    # 4. Pasos Peatonales (Cebras Originales)
    def dibujar_cebra_horizontal(x_inicio, y_inicio):
        for i in range(0, 100, 15):
            pygame.draw.rect(screen, (255, 255, 255), (x_inicio, y_inicio + i, 20, 8))

    def dibujar_cebra_vertical(x_inicio, y_inicio):
        for i in range(0, 100, 15):
            pygame.draw.rect(screen, (255, 255, 255), (x_inicio + i, y_inicio, 8, 20))

    for x in CALLES_X:
        for y in CALLES_Y:
            dibujar_cebra_vertical(x, y - 25)   # Cruce Norte
            dibujar_cebra_vertical(x, y + 105)  # Cruce Sur
            dibujar_cebra_horizontal(x - 25, y) # Cruce Oeste
            dibujar_cebra_horizontal(x + 105, y) # Cruce Este

    # 5. Hardware Vial de Sensores
    COLOR_LAZO = (120, 120, 120)  
    COLOR_POSTE = (180, 180, 180)          
    COLOR_ANTENA = (0, 102, 204)      

    for x in CALLES_X:
        for y in CALLES_Y:
            # Sensores Acceso NORTE
            pygame.draw.rect(screen, COLOR_LAZO, (x + 8, y - 55, 38, 15), 1)
            pygame.draw.line(screen, COLOR_LAZO, (x + 27, y - 55), (x + 27, y - 40), 1)
            pygame.draw.rect(screen, COLOR_POSTE, (x - 8, y - 60, 5, 12))  
            pygame.draw.circle(screen, COLOR_ANTENA, (x - 6, y - 65), 5)  

            # Sensores Acceso SUR
            pygame.draw.rect(screen, COLOR_LAZO, (x + 54, y + 140, 38, 15), 1)
            pygame.draw.line(screen, COLOR_LAZO, (x + 73, y + 140), (x + 73, y + 155), 1)
            pygame.draw.rect(screen, COLOR_POSTE, (x + 103, y + 148, 5, 12))  
            pygame.draw.circle(screen, COLOR_ANTENA, (x + 105, y + 153), 5)

            # Sensores Acceso OESTE
            pygame.draw.rect(screen, COLOR_LAZO, (x - 55, y + 54, 15, 38), 1)
            pygame.draw.line(screen, COLOR_LAZO, (x - 55, y + 73), (x - 40, y + 73), 1)
            pygame.draw.rect(screen, COLOR_POSTE, (x - 60, y - 8, 12, 5))  
            pygame.draw.circle(screen, COLOR_ANTENA, (x - 65, y - 6), 5)

            # Sensores Acceso ESTE
            pygame.draw.rect(screen, COLOR_LAZO, (x + 140, y + 8, 15, 38), 1)
            pygame.draw.line(screen, COLOR_LAZO, (x + 140, y + 27), (x + 155, y + 27), 1)
            pygame.draw.rect(screen, COLOR_POSTE, (x + 148, y + 103, 12, 5))  
            pygame.draw.circle(screen, COLOR_ANTENA, (x + 153, y + 105), 5)