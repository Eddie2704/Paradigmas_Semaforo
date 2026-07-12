import pygame
from mapa import dibujar_mapa
from semaforo import Semaforo
from semaforo_peatonal import SemaforoPeatonal
from vehiculo import Vehiculo  
from peaton import Peaton  
from controlador import ControladorTrafico 
from interfaz_de_datos import InterfazDatos # NUEVO IMPORT

# CONFIGURACIÓN INICIAL DE PYGAME
pygame.init()
# Configuración de la ventana
screen = pygame.display.set_mode((1150, 600))
pygame.display.set_caption("Simulador Semaforo Inteligente")
clock = pygame.time.Clock()

semaforos_autos = [
    Semaforo(410, 220, "horizontal"),
    Semaforo(350, 360, "horizontal"),
    Semaforo(330, 250, "vertical"),
    Semaforo(450, 310, "vertical")
]

semaforos_peatonales = [
    SemaforoPeatonal(320, 220), SemaforoPeatonal(470, 220),
    SemaforoPeatonal(320, 365), SemaforoPeatonal(470, 365)
]

vehiculos = []
peatones = []  
cerebro_trafico = ControladorTrafico()
monitor_interfaz = InterfazDatos() # INSTANCIA DE LA NUEVA INTERFAZ

entorno = {
    "solicitud_peaton": False,
    "ambulancia_detectada": None,
    "es_de_madrugada": False
}

modo_ambulancia = False
modo_peaton = False  
simulacion_activa = False  
mostrar_panel_datos = True  # Inicia visible para mostrar el diseño analítico

running = True
while running:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            # INTERRUPTOR DE ENCENDIDO
            if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                if not simulacion_activa:
                    simulacion_activa = True
                    cerebro_trafico.ultima_actualizacion = pygame.time.get_ticks()
                    
            if event.key == pygame.K_h:
                modo_peaton = True
                modo_ambulancia = False
            elif event.key == pygame.K_a:
                modo_ambulancia = True
                modo_peaton = False

            elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                direcciones = {pygame.K_1: "NORTE", pygame.K_2: "SUR", pygame.K_3: "ESTE", pygame.K_4: "OESTE"}
                dir_seleccionada = direcciones[event.key]

                if modo_peaton:
                    peatones.append(Peaton(dir_seleccionada))
                    modo_peaton = False
                elif modo_ambulancia:
                    vehiculos.append(Vehiculo(dir_seleccionada, tipo="AMBULANCIA"))
                    modo_ambulancia = False
                else:
                    vehiculos.append(Vehiculo(dir_seleccionada, tipo="NORMAL"))

            if event.key == pygame.K_p:
                entorno["solicitud_peaton"] = True
            if event.key == pygame.K_m:
                entorno["es_de_madrugada"] = not entorno["es_de_madrugada"]

    # 1. Limpiar pantalla completa y dibujar el mapa en su zona (0 a 800)
    # Rellenamos de negro el fondo de la zona extra para que no se dupliquen imágenes
    screen.fill((10, 10, 12)) 
    dibujar_mapa(screen)

    fase_activa, t_restante = 0, 0

    # 2. Lógicas y actualizaciones
    if simulacion_activa:
        fase_activa, t_restante = cerebro_trafico.procesar_inteligencia(semaforos_autos, semaforos_peatonales, vehiculos, entorno)
        
        for humano in peatones[:]:
            humano.actualizar(semaforos_peatonales)
            if humano.x > 600 or humano.y > 500: peatones.remove(humano)
            
        for auto in vehiculos[:]:
            auto.actualizar(semaforos_autos, vehiculos)  
            if auto.x < -50 or auto.x > 850 or auto.y < -50 or auto.y > 650:
                vehiculos.remove(auto)
    else:
        for s in semaforos_autos: s.estado = "rojo"
        for auto in vehiculos:
            auto.actualizar(semaforos_autos, vehiculos)

    # 3. Dibujo de Entidades viales
    for humano in peatones: humano.dibujar(screen)
    for auto in vehiculos: auto.dibujar(screen)

    # 4. Dibujar Semáforos
    for i, s in enumerate(semaforos_autos):
        if simulacion_activa and ((fase_activa == 0 and i in [0, 1]) or (fase_activa == 1 and i in [2, 3])):
            s.dibujar(screen, tiempo_restante=t_restante)
        else:
            s.dibujar(screen)

    for sp in semaforos_peatonales: 
        sp.dibujar(screen)

    
    # 5. DIBUJAR PANTALLA DE MONITOREO DE DATOS
    if mostrar_panel_datos:
        monitor_interfaz.dibujar_tabla(screen, cerebro_trafico.historial, cerebro_trafico)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()