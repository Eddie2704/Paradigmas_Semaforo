import pygame

def dibujar_mapa(screen):
    # 1. Fondo (Zonas verdes)
    screen.fill((34, 139, 34)) 

    # VEGETACIÓN (Se dibuja al fondo para que no tape calles ni cebras)
    def dibujar_arbol(cx, cy):
        # Tronco
        pygame.draw.rect(screen, (101, 67, 33), (cx - 3, cy, 6, 15))
        # Copa del árbol (Hojas)
        pygame.draw.circle(screen, (20, 100, 20), (cx, cy), 15)
        pygame.draw.circle(screen, (46, 125, 50), (cx - 2, cy - 2), 11)

    # Distribución de árboles en las 4 esquinas verdes sin tocar las vías
    arboles_posiciones = [
        # Esquina Superior Izquierda
        (60, 50), (120, 70), (200, 40), (240, 100), (80, 140),
        # Esquina Superior Derecha
        (560, 60), (620, 110), (700, 50), (740, 130), (600, 40),
        # Esquina Inferior Izquierda
        (50, 440), (110, 520), (180, 460), (240, 530), (90, 410),
        # Esquina Inferior Derecha
        (560, 470), (620, 420), (710, 500), (730, 430), (650, 530)
    ]
    
    for pos in arboles_posiciones:
        dibujar_arbol(pos[0], pos[1])

    # 2. Calles (Gris oscuro)
    pygame.draw.rect(screen, (50, 50, 50), (0, 250, 800, 100))  # horizontal
    pygame.draw.rect(screen, (50, 50, 50), (350, 0, 100, 600))  # vertical
    pygame.draw.rect(screen, (50, 50, 50), (350, 250, 100, 100)) # intersección

    # 3. Líneas centrales discontinuas amarillas
    for x in range(0, 280, 20):
        pygame.draw.line(screen, (255, 215, 0), (x, 300), (x + 10, 300), 2)
    for x in range(500, 800, 20):
        pygame.draw.line(screen, (255, 215, 0), (x, 300), (x + 10, 300), 2)
    for y in range(0, 180, 20):
        pygame.draw.line(screen, (255, 215, 0), (400, y), (400, y + 10), 2)
    for y in range(400, 600, 20):
        pygame.draw.line(screen, (255, 215, 0), (400, y), (400, y + 10), 2)

    # 4. Pasos Peatonales (Cebras)
    def dibujar_cebra_horizontal(x_inicio, y_inicio):
        for i in range(0, 100, 15):
            pygame.draw.rect(screen, (255, 255, 255), (x_inicio, y_inicio + i, 20, 8))

    def dibujar_cebra_vertical(x_inicio, y_inicio):
        for i in range(0, 100, 15):
            pygame.draw.rect(screen, (255, 255, 255), (x_inicio + i, y_inicio, 8, 20))

    dibujar_cebra_vertical(350, 180)   # Cruce Norte
    dibujar_cebra_vertical(350, 400)   # Cruce Sur
    dibujar_cebra_horizontal(280, 250) # Cruce Oeste
    dibujar_cebra_horizontal(500, 250) # Cruce Este

    # 5. Flechas de Dirección Corregidas (Sentido de conducción por la derecha completo)
    blanco_flecha = (200, 200, 200)

    # --- CALLE NORTE (Vertical Arriba) ---
    # Carril Derecho: Va hacia ARRIBA (NORTE) 
    pygame.draw.line(screen, blanco_flecha, (425, 120), (425, 150), 4)
    pygame.draw.polygon(screen, blanco_flecha, [(420, 125), (430, 125), (425, 115)])
    # Carril Izquierdo: Va hacia ABAJO (SUR) ↓
    pygame.draw.line(screen, blanco_flecha, (375, 120), (375, 150), 4)
    pygame.draw.polygon(screen, blanco_flecha, [(370, 145), (380, 145), (375, 155)])

    # --- CALLE SUR (Vertical Abajo) ---
    # Carril Derecho: Va hacia ARRIBA (NORTE) 
    pygame.draw.line(screen, blanco_flecha, (425, 450), (425, 480), 4)
    pygame.draw.polygon(screen, blanco_flecha, [(420, 455), (430, 455), (425, 445)])
    # Carril Izquierdo: Va hacia ABAJO (SUR) 
    pygame.draw.line(screen, blanco_flecha, (375, 450), (375, 480), 4)
    pygame.draw.polygon(screen, blanco_flecha, [(370, 475), (380, 475), (375, 485)])

    # --- CALLE OESTE (Horizontal Izquierda) ---
    # Carril Superior: Ahora VA HACIA LA IZQUIERDA (OESTE) 
    pygame.draw.line(screen, blanco_flecha, (210, 275), (240, 275), 4)
    pygame.draw.polygon(screen, blanco_flecha, [(215, 270), (215, 280), (205, 275)])
    # Carril Inferior: Ahora VA HACIA LA DERECHA (ESTE) 
    pygame.draw.line(screen, blanco_flecha, (210, 325), (240, 325), 4)
    pygame.draw.polygon(screen, blanco_flecha, [(235, 320), (235, 330), (245, 325)])

    # --- CALLE ESTE (Horizontal Derecha) ---
    # Carril Superior: Ahora VA HACIA LA IZQUIERDA (OESTE) 
    pygame.draw.line(screen, blanco_flecha, (560, 275), (590, 275), 4)
    pygame.draw.polygon(screen, blanco_flecha, [(565, 270), (565, 280), (555, 275)])
    # Carril Inferior: Ahora VA HACIA LA DERECHA (ESTE) 
    pygame.draw.line(screen, blanco_flecha, (560, 325), (590, 325), 4)
    pygame.draw.polygon(screen, blanco_flecha, [(585, 320), (585, 330), (595, 325)])
# =========================================================================
    # 6. NUEVO: DISEÑO ESTILIZADO DE HARDWARE VIAL (SENSORES Y ANTENAS)
    # =========================================================================
    COLOR_LAZO_CONTOUNRO = (120, 120, 120)  # Gris asfalto cortado para el lazo magnético
    COLOR_POSTE = (180, 180, 180)          # Gris metálico para la estructura de la antena
    COLOR_ANTENA_RFID = (0, 102, 204)      # Azul tecnológico para el receptor RFID

    # --- CALLE NORTE (Entrada superior) ---
    # Sensor de flujo en el suelo (Lazo magnético calado en el carril izquierdo)
    pygame.draw.rect(screen, COLOR_LAZO_CONTOUNRO, (358, 205, 38, 15), 1)
    pygame.draw.line(screen, COLOR_LAZO_CONTOUNRO, (377, 205), (377, 220), 1)
    # Antena RFID en la acera (Al par de la calle, a la izquierda)
    pygame.draw.rect(screen, COLOR_POSTE, (342, 20, 5, 12))  # Base/Poste
    pygame.draw.circle(screen, COLOR_ANTENA_RFID, (344, 15), 5)  # Domo Lector

    # --- CALLE SUR (Entrada inferior) ---
    # Sensor de flujo en el suelo (Lazo magnético calado en el carril derecho)
    pygame.draw.rect(screen, COLOR_LAZO_CONTOUNRO, (404, 380, 38, 15), 1)
    pygame.draw.line(screen, COLOR_LAZO_CONTOUNRO, (423, 380), (423, 395), 1)
    # Antena RFID en la acera (Al par de la calle, a la derecha)
    pygame.draw.rect(screen, COLOR_POSTE, (453, 570, 5, 12)) # Base/Poste
    pygame.draw.circle(screen, COLOR_ANTENA_RFID, (455, 565), 5) # Domo Lector

    # --- CALLE ESTE (Entrada derecha) ---
    # Sensor de flujo en el suelo (Lazo magnético calado en el carril superior)
    pygame.draw.rect(screen, COLOR_LAZO_CONTOUNRO, (475, 253, 15, 38), 1)
    pygame.draw.line(screen, COLOR_LAZO_CONTOUNRO, (475, 272), (490, 272), 1)
    # Antena RFID en la acera (Al par de la calle, arriba)
    pygame.draw.rect(screen, COLOR_POSTE, (770, 238, 12, 5)) # Base/Poste
    pygame.draw.circle(screen, COLOR_ANTENA_RFID, (765, 240), 5) # Domo Lector

    # --- CALLE OESTE (Entrada izquierda) ---
    # Sensor de flujo en el suelo (Lazo magnético calado en el carril inferior)
    pygame.draw.rect(screen, COLOR_LAZO_CONTOUNRO, (310, 309, 15, 38), 1)
    pygame.draw.line(screen, COLOR_LAZO_CONTOUNRO, (310, 328), (325, 328), 1)
    # Antena RFID en la acera (Al par de la calle, abajo)
    pygame.draw.rect(screen, COLOR_POSTE, (20, 357, 12, 5))  # Base/Poste
    pygame.draw.circle(screen, COLOR_ANTENA_RFID, (35, 359), 5)  # Domo Lector