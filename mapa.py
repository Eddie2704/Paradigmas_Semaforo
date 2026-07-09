import pygame

def dibujar_mapa(screen):
    # 1. Fondo (Zonas verdes)
    screen.fill((34, 139, 34)) 

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
    # Carril Derecho: Va hacia ARRIBA (NORTE) ↑
    pygame.draw.line(screen, blanco_flecha, (425, 120), (425, 150), 4)
    pygame.draw.polygon(screen, blanco_flecha, [(420, 125), (430, 125), (425, 115)])
    # Carril Izquierdo: Va hacia ABAJO (SUR) ↓
    pygame.draw.line(screen, blanco_flecha, (375, 120), (375, 150), 4)
    pygame.draw.polygon(screen, blanco_flecha, [(370, 145), (380, 145), (375, 155)])

    # --- CALLE SUR (Vertical Abajo) ---
    # Carril Derecho: Va hacia ARRIBA (NORTE) ↑
    pygame.draw.line(screen, blanco_flecha, (425, 450), (425, 480), 4)
    pygame.draw.polygon(screen, blanco_flecha, [(420, 455), (430, 455), (425, 445)])
    # Carril Izquierdo: Va hacia ABAJO (SUR) ↓
    pygame.draw.line(screen, blanco_flecha, (375, 450), (375, 480), 4)
    pygame.draw.polygon(screen, blanco_flecha, [(370, 475), (380, 475), (375, 485)])

    # --- CALLE OESTE (Horizontal Izquierda) ---
    # Carril Superior: Ahora VA HACIA LA IZQUIERDA (OESTE) ←
    pygame.draw.line(screen, blanco_flecha, (210, 275), (240, 275), 4)
    pygame.draw.polygon(screen, blanco_flecha, [(215, 270), (215, 280), (205, 275)])
    # Carril Inferior: Ahora VA HACIA LA DERECHA (ESTE) →
    pygame.draw.line(screen, blanco_flecha, (210, 325), (240, 325), 4)
    pygame.draw.polygon(screen, blanco_flecha, [(235, 320), (235, 330), (245, 325)])

    # --- CALLE ESTE (Horizontal Derecha) ---
    # Carril Superior: Ahora VA HACIA LA IZQUIERDA (OESTE) ←
    pygame.draw.line(screen, blanco_flecha, (560, 275), (590, 275), 4)
    pygame.draw.polygon(screen, blanco_flecha, [(565, 270), (565, 280), (555, 275)])
    # Carril Inferior: Ahora VA HACIA LA DERECHA (ESTE) →
    pygame.draw.line(screen, blanco_flecha, (560, 325), (590, 325), 4)
    pygame.draw.polygon(screen, blanco_flecha, [(585, 320), (585, 330), (595, 325)])