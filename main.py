import pygame
import lector_mqtt
from mapa import dibujar_mapa
from semaforo import Semaforo
from semaforo_peatonal import SemaforoPeatonal
from vehiculo import Vehiculo  
from peaton import Peaton  
from controlador import ControladorTrafico 
from interfaz_de_datos import InterfazDatos 

# CONFIGURACIÓN INICIAL DE PYGAME
pygame.init()
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
monitor_interfaz = InterfazDatos() 

entorno = {
    "solicitud_peaton": False,
    "ambulancia_detectada": None,
    "es_de_madrugada": False
}

modo_ambulancia = False
modo_peaton = False  
simulacion_activa = False  
mostrar_panel_datos = True  

# Inicializamos la red MQTT
lector_mqtt.iniciar()

running = True
while running:
    
    # Esta variable centralizará cualquier estímulo del frame (ya sea de tecla o de Wokwi)
    estimulo_recibido = None

    # 1. ENTRADA LOCAL: CAPTURA DE TECLADO
    
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

            # Teclas de dirección rápidas
            elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                direcciones = {pygame.K_1: "AUTO_NORTE", pygame.K_2: "AUTO_SUR", pygame.K_3: "AUTO_ESTE", pygame.K_4: "AUTO_OESTE"}
                estimulo_recibido = direcciones[event.key]

            elif event.key == pygame.K_p:
                estimulo_recibido = "PEATON"
            elif event.key == pygame.K_m:
                estimulo_recibido = "MADRUGADA"

    # 2. ENTRADA REMOTA: CAPTURA DE WOKWI (MQTT)
    
    evento_mqtt = lector_mqtt.leer()
    if evento_mqtt:
        estimulo_recibido = evento_mqtt

    # 3. PROCESAMIENTO UNIFICADO DE LOS ESTÍMULOS
    if estimulo_recibido:
        print(f"[EVENTO] Procesando: {estimulo_recibido}")
        
        # Activar los modos preparatorios desde Wokwi o teclado
        if estimulo_recibido == "MODO_PEATON":
            modo_peaton = True
            modo_ambulancia = False
            
        elif estimulo_recibido == "AMBULANCIA":
            modo_ambulancia = True
            modo_peaton = False
            
        elif estimulo_recibido == "SOLICITUD_SEMAFORO_PEATON" or estimulo_recibido == "PEATON":
            # El botón de solicitar cruce (Pin 17) o la tecla 'P' activan la inteligencia de tráfico
            entorno["solicitud_peaton"] = True
            
        elif estimulo_recibido == "MADRUGADA":
            entorno["es_de_madrugada"] = not entorno["es_de_madrugada"]

        # Lógica de direcciones (Norte, Sur, Este, Oeste)
        elif estimulo_recibido == "AUTO_NORTE":
            if modo_peaton: peatones.append(Peaton("NORTE")); modo_peaton = False
            elif modo_ambulancia: vehiculos.append(Vehiculo("NORTE", tipo="AMBULANCIA")); modo_ambulancia = False
            else: vehiculos.append(Vehiculo("NORTE", tipo="NORMAL"))
            
        elif estimulo_recibido == "AUTO_SUR":
            if modo_peaton: peatones.append(Peaton("SUR")); modo_peaton = False
            elif modo_ambulancia: vehiculos.append(Vehiculo("SUR", tipo="AMBULANCIA")); modo_ambulancia = False
            else: vehiculos.append(Vehiculo("SUR", tipo="NORMAL"))
            
        elif estimulo_recibido == "AUTO_ESTE":
            if modo_peaton: peatones.append(Peaton("ESTE")); modo_peaton = False
            elif modo_ambulancia: vehiculos.append(Vehiculo("ESTE", tipo="AMBULANCIA")); modo_ambulancia = False
            else: vehiculos.append(Vehiculo("ESTE", tipo="NORMAL"))
            
        elif estimulo_recibido == "AUTO_OESTE":
            if modo_peaton: peatones.append(Peaton("OESTE")); modo_peaton = False
            elif modo_ambulancia: vehiculos.append(Vehiculo("OESTE", tipo="AMBULANCIA")); modo_ambulancia = False
            else: vehiculos.append(Vehiculo("OESTE", tipo="NORMAL"))

    # =====================================================================
    # 4. RENDERIZADO Y DIBUJO DE PYGAME (Se mantiene igual de limpio)
    # =====================================================================
    screen.fill((10, 10, 12)) 
    dibujar_mapa(screen)

    fase_activa, t_restante = 0, 0

    if simulacion_activa:
        fase_activa, t_restante = cerebro_trafico.procesar_inteligencia(semaforos_autos, semaforos_peatonales, vehiculos, entorno)
        
        for humano in peatones[:]:
            humano.actualizar(semaforos_peatonales)
            if humano.x < -20 or humano.x > 820 or humano.y < -20 or humano.y > 620: 
                peatones.remove(humano)
            
        for auto in vehiculos[:]:
            auto.actualizar(semaforos_autos, vehiculos)  
            if auto.x < -50 or auto.x > 850 or auto.y < -50 or auto.y > 650:
                vehiculos.remove(auto)
    else:
        for s in semaforos_autos: s.estado = "rojo"
        for auto in vehiculos:
            auto.actualizar(semaforos_autos, vehiculos)

    for humano in peatones: humano.dibujar(screen)
    for auto in vehiculos: auto.dibujar(screen)

    for i, s in enumerate(semaforos_autos):
        if simulacion_activa and ((fase_activa == 0 and i in [0, 1]) or (fase_activa == 1 and i in [2, 3])):
            s.dibujar(screen, tiempo_restante=t_restante)
        else:
            s.dibujar(screen)

    for sp in semaforos_peatonales: 
        sp.dibujar(screen)

    if mostrar_panel_datos:
        monitor_interfaz.dibujar_tabla(screen, cerebro_trafico.historial, cerebro_trafico)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()