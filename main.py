import pygame
from mapa import dibujar_mapa
from semaforo import Semaforo
from semaforo_peatonal import SemaforoPeatonal
from vehiculo import Vehiculo  
from peaton import Peaton  # Importamos tu nueva clase Peaton
from controlador import ControladorTrafico 


# CONFIGURACIÓN INICIAL DE PYGAME
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Simulador de Semáforo Inteligente")
clock = pygame.time.Clock()

# SEMÁFOROS DE AUTOS ORIGINALES
semaforos_autos = [
    Semaforo(410, 220, "horizontal"),  # índice 0: norte
    Semaforo(350, 360, "horizontal"),  # índice 1: sur
    Semaforo(330, 250, "vertical"),    # índice 2: oeste
    Semaforo(450, 310, "vertical")     # índice 3: este
]

# Semáforos peatonales
semaforos_peatonales = [
    SemaforoPeatonal(320, 220),  # índice 0: arriba-izquierda (Cruce Norte)
    SemaforoPeatonal(470, 220),  # índice 1: arriba-derecha (Cruce Este)
    SemaforoPeatonal(320, 365),  # índice 2: abajo-izquierda (Cruce Sur)
    SemaforoPeatonal(470, 365)   # índice 3: abajo-derecha (Cruce Oeste)
]

# Listas de entidades activas
vehiculos = []
peatones = []  # Lista para almacenar los peatones en pantalla

cerebro_trafico = ControladorTrafico()

entorno = {
    "solicitud_peaton": False,
    "ambulancia_detectada": None,
    "es_de_madrugada": False
}

# Banderas para comandos combinados de teclado
modo_ambulancia = False
modo_peaton = False  # Detecta si se presionó la tecla 'H' previamente

# BUCLE PRINCIPAL
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            # --- PREPARAR COMANDO COMBINADO PEATÓN ('H') ---
            if event.key == pygame.K_h:
                modo_peaton = True
                modo_ambulancia = False
                print("¡Modo Peatón activo! Presiona del 1 al 4 para elegir su cruce...")

            # PREPARAR COMANDO COMBINADO AMBULANCIA ('A')
            elif event.key == pygame.K_a:
                modo_ambulancia = True
                modo_peaton = False
                print("Modo Ambulancia activo! Presiona del 1 al 4 para elegir su calle...")

            # --- CONTROL DE INYECCIÓN DE ENTIDADES (1 al 4) ---
            elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                direcciones = {pygame.K_1: "NORTE", pygame.K_2: "SUR", pygame.K_3: "ESTE", pygame.K_4: "OESTE"}
                dir_seleccionada = direcciones[event.key]

                if modo_peaton:
                    # Inyectar un peatón en la acera del cruce seleccionado
                    peatones.append(Peaton(dir_seleccionada))
                    modo_peaton = False
                    print(f"Peatón generado esperando en el cruce: {dir_seleccionada}")
                elif modo_ambulancia:
                    vehiculos.append(Vehiculo(dir_seleccionada, tipo="AMBULANCIA"))
                    entorno["ambulancia_detectada"] = dir_seleccionada
                    modo_ambulancia = False
                    print(f"Ambulancia desplegada en calle: {dir_seleccionada}.")
                else:
                    # Inyección normal de vehículos
                    vehiculos.append(Vehiculo(dir_seleccionada, tipo="NORMAL"))

            # --- BOTÓN DE SOLICITUD PEATONAL COMPLETO ('P') ---
            if event.key == pygame.K_p:
                entorno["solicitud_peaton"] = True
                print("Botón peatonal presionado. El cerebro priorizará la fase de cruce...")

            # --- CANCELAR EMERGENCIAS ('X') o ACTIVAR MADRUGADA ('M') ---
            if event.key == pygame.K_x:
                entorno["ambulancia_detectada"] = None
            if event.key == pygame.K_m:
                entorno["es_de_madrugada"] = not entorno["es_de_madrugada"]

    # 1. Dibujar mapa base
    dibujar_mapa(screen)

    # 2. Lógica del semáforo inteligente
    cerebro_trafico.procesar_inteligencia(semaforos_autos, semaforos_peatonales, vehiculos, entorno)

    # 3. Actualizar y dibujar Peatones
    for humano in peatones[:]:
        humano.actualizar(semaforos_peatonales)
        humano.dibujar(screen)
        # Limpieza: si el peatón ya terminó de cruzar toda la calle y salió del rango, se elimina
        if humano.x > 500 and (humano.cruce == "NORTE" or humano.cruce == "SUR"):
            peatones.remove(humano)
        elif humano.y > 400 and (humano.cruce == "OESTE" or humano.cruce == "ESTE"):
            peatones.remove(humano)

    # 4. Actualizar y dibujar Vehículos
    for auto in vehiculos[:]:
        auto.actualizar(semaforos_autos, vehiculos)  
        auto.dibujar(screen)
        if auto.x < -50 or auto.x > 850 or auto.y < -50 or auto.y > 650:
            vehiculos.remove(auto)

    # 5. Dibujar semáforos viales y peatonales
    for s in semaforos_autos: s.dibujar(screen)
    for sp in semaforos_peatonales: sp.dibujar(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()