import os
import pygame
import lector_mqtt
import random 
from mapa import dibujar_mapa
from semaforo import Semaforo
from semaforo_peatonal import SemaforoPeatonal
from vehiculo import Vehiculo  
from peaton import Peaton  
from controlador import ControladorTrafico 
from interfaz_de_datos import InterfazDatos
from historial import HistorialTrafico

# Centrado automático de la ventana en el monitor
os.environ['SDL_VIDEO_CENTERED'] = '1'

pygame.init()

# Dimensiones optimizadas para la cuadrícula 2x2 visible y movible
ANCHO_BASE, ALTO_BASE = 1150, 700
screen = pygame.display.set_mode((ANCHO_BASE, ALTO_BASE), pygame.RESIZABLE)
pygame.display.set_caption("Simulador Semaforo Inteligente")
clock = pygame.time.Clock()

# Coordenadas maestras de los 4 cruces
CX = [250, 750]  
CY = [120, 470]  


# LÓGICA DE POSICIONAMIENTO Y ORIENTACIÓN DE SEMÁFOROS
semaforos_autos = []
semaforos_peatonales = []
intersecciones = []  # <--- Lista estructurada para el nuevo controlador

id_cruce = 0

for x in CX:
    for y in CY:
        # Semáforos Vehiculares: Copiados exactamente con tus orientaciones y posiciones
        s_norte = Semaforo(x + 60, y - 30, "horizontal")
        s_sur   = Semaforo(x - 0,  y + 110, "horizontal")
        s_este  = Semaforo(x - 20, y + 0, "vertical")
        s_oeste = Semaforo(x + 100, y + 60, "vertical")
        
        # Guardamos en la lista global para los vehículos (compatibilidad)
        semaforos_autos.extend([s_norte, s_sur, s_este, s_oeste])

        # Semáforos Peatonales: Esquinas correspondientes
        sp1 = SemaforoPeatonal(x - 30, y - 30)
        sp2 = SemaforoPeatonal(x + 120, y - 30)
        sp3 = SemaforoPeatonal(x - 30, y + 115)
        sp4 = SemaforoPeatonal(x + 120, y + 115)
        
        # Guardamos en la lista global para los peatones (compatibilidad)
        semaforos_peatonales.extend([sp1, sp2, sp3, sp4])

        # EMPAQUETAMOS EL CRUCE: Asignamos su ID único y sus semáforos
        intersecciones.append({
            "id": id_cruce,
            "autos": [s_norte, s_sur, s_este, s_oeste],
            "peatones": [sp1, sp2, sp3, sp4]
        })
        
        id_cruce += 1

vehiculos = []
peatones = []  
cerebro_trafico = ControladorTrafico()

entorno = {
    "solicitud_peaton": False,
    "ambulancia_detectada": None,
    "es_de_madrugada": False,
    "colision_activa": False,
    "zona_bloqueada": None
}

modo_ambulancia = False
modo_peaton = False  
simulacion_activa = False  

# Conexión al broker MQTT (Wokwi)
lector_mqtt.iniciar()
interfaz = InterfazDatos()
historial = HistorialTrafico()

running = True
while running:
    estimulo_recibido = None

    # 1. CAPTURA DE EVENTOS (Teclado local y redimensión de ventana)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Clic izquierdo
                # Pasamos los objetos a la función de verificación
                interfaz.verificar_click(event.pos, historial, cerebro_trafico)
        elif event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                if not simulacion_activa:
                    simulacion_activa = True
                    tiempo_actual = pygame.time.get_ticks()
                    
                    # Inicializamos los tiempos y desfasamos las fases iniciales
                    for inter in intersecciones:
                        id_int = inter["id"]
                        cerebro_trafico._inicializar_interseccion_si_no_existe(id_int)
                        
                        # Alternamos: Intersecciones 0 y 2 empiezan en Fase 0 (Norte/Sur Verde)
                        # Intersecciones 1 y 3 empiezan en Fase 1 (Este/Oeste Verde)
                        if id_int % 2 == 0:
                            cerebro_trafico.estados_intersecciones[id_int]["fase_actual"] = 0
                        else:
                            cerebro_trafico.estados_intersecciones[id_int]["fase_actual"] = 1
                            
                        cerebro_trafico.estados_intersecciones[id_int]["ultima_actualizacion"] = tiempo_actual
            elif event.key == pygame.K_h:
                modo_peaton = True; modo_ambulancia = False
            elif event.key == pygame.K_a:
                modo_ambulancia = True; modo_peaton = False
            elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                direcciones = {pygame.K_1: "AUTO_NORTE", pygame.K_2: "AUTO_SUR", pygame.K_3: "AUTO_ESTE", pygame.K_4: "AUTO_OESTE"}
                estimulo_recibido = direcciones[event.key]
            elif event.key == pygame.K_p:
                estimulo_recibido = "PEATON"
            elif event.key == pygame.K_m:
                estimulo_recibido = "MADRUGADA"

    # 2. CAPTURA REMOTA (Wokwi)
    evento_mqtt = lector_mqtt.leer()
    if evento_mqtt:
        estimulo_recibido = evento_mqtt

    # 3. PROCESAMIENTO DE LÓGICA DE TRÁFICO
    if estimulo_recibido:
        print(f"[EVENTO] Procesando: {estimulo_recibido}")
        if estimulo_recibido == "MODO_PEATON":
            modo_peaton = True; modo_ambulancia = False
        elif estimulo_recibido == "AMBULANCIA":
            modo_ambulancia = True; modo_peaton = False
        elif estimulo_recibido in ["SOLICITUD_SEMAFORO_PEATON", "PEATON"]:
            entorno["solicitud_peaton"] = True
        elif estimulo_recibido == "MADRUGADA":
            entorno["es_de_madrugada"] = not entorno["es_de_madrugada"]
        elif "COLISION" in estimulo_recibido:
            entorno["colision_activa"] = True
            entorno["zona_bloqueada"] = estimulo_recibido.split("_")[-1]

        #Inyección de flujo vehicular/peatonal ---
        elif estimulo_recibido == "AUTO_NORTE":
            calle_aleatoria = random.choice(CX)
            if modo_peaton: 
                # Selecciona al azar la calle horizontal (CY) donde cruzará horizontalmente
                calle_h = random.choice(CY)
                peatones.append(Peaton("NORTE", pos_calle_v=calle_aleatoria, pos_calle_h=calle_h))
                modo_peaton = False
            elif modo_ambulancia: vehiculos.append(Vehiculo("NORTE", tipo="AMBULANCIA", pos_calle=calle_aleatoria)); modo_ambulancia = False
            else: vehiculos.append(Vehiculo("NORTE", tipo="NORMAL", pos_calle=calle_aleatoria))
            
        elif estimulo_recibido == "AUTO_SUR":
            calle_aleatoria = random.choice(CX)
            if modo_peaton: 
                calle_h = random.choice(CY)
                peatones.append(Peaton("SUR", pos_calle_v=calle_aleatoria, pos_calle_h=calle_h))
                modo_peaton = False
            elif modo_ambulancia: vehiculos.append(Vehiculo("SUR", tipo="AMBULANCIA", pos_calle=calle_aleatoria)); modo_ambulancia = False
            else: vehiculos.append(Vehiculo("SUR", tipo="NORMAL", pos_calle=calle_aleatoria))
            
        elif estimulo_recibido == "AUTO_ESTE":
            calle_aleatoria = random.choice(CY)
            if modo_peaton: 
                # Selecciona al azar la calle vertical (CX) donde cruzará verticalmente
                calle_v = random.choice(CX)
                peatones.append(Peaton("ESTE", pos_calle_v=calle_v, pos_calle_h=calle_aleatoria))
                modo_peaton = False
            elif modo_ambulancia: vehiculos.append(Vehiculo("ESTE", tipo="AMBULANCIA", pos_calle=calle_aleatoria)); modo_ambulancia = False
            else: vehiculos.append(Vehiculo("ESTE", tipo="NORMAL", pos_calle=calle_aleatoria))
            
        elif estimulo_recibido == "AUTO_OESTE":
            calle_aleatoria = random.choice(CY)
            if modo_peaton: 
                calle_v = random.choice(CX)
                peatones.append(Peaton("OESTE", pos_calle_v=calle_v, pos_calle_h=calle_aleatoria))
                modo_peaton = False
            elif modo_ambulancia: vehiculos.append(Vehiculo("OESTE", tipo="AMBULANCIA", pos_calle=calle_aleatoria)); modo_ambulancia = False
            else: vehiculos.append(Vehiculo("OESTE", tipo="NORMAL", pos_calle=calle_aleatoria))

    # 4. ACTUALIZACIÓN Y RENDERIZADO VISUAL
    screen.fill((24, 24, 24))
    dibujar_mapa(screen)      

    if simulacion_activa:
        # 1. Ejecutar la inteligencia del controlador.
        # Ahora pasamos 'intersecciones' en lugar de las listas separadas.
        # Devuelve un diccionario: { id_cruce: (fase, tiempo_restante), ... }
        diccionario_tiempos = cerebro_trafico.procesar_inteligencia(intersecciones, vehiculos, entorno)
        
        # 2. Actualizar peatones y vehículos usando las listas globales (para que detecten todos los semáforos)
        for humano in peatones[:]:
            humano.actualizar(semaforos_peatonales)
            
            # Condición de salida: desaparecen justo al pisar la acera del otro lado del cruce
            desaparecer = False
            if humano.cruce == "NORTE" or humano.cruce == "SUR":
                if humano.x > humano.pos_calle_v + 120:
                    desaparecer = True
            elif humano.cruce == "OESTE" or humano.cruce == "ESTE":
                if humano.y > humano.pos_calle_h + 120:
                    desaparecer = True
                    
            if desaparecer:
                peatones.remove(humano)
            
        for auto in vehiculos[:]:
            # Pasamos diccionario_tiempos para que el auto sepa cuánto le queda al verde
            auto.actualizar(semaforos_autos, vehiculos, diccionario_tiempos)  
            
            # NUEVO LÍMITE: Si pasa de 850 (entrada al panel de datos), se elimina y registra
            if auto.x < -50 or auto.x > 850 or auto.y < -50 or auto.y > 750: 
                # Si el auto iba hacia la derecha y cruzó con éxito, lo registramos
                if auto.x > 850 and hasattr(auto, 'idx_interseccion'):
                    historial.registrar_vehiculo(auto.idx_interseccion, auto.cruce)
                vehiculos.remove(auto)
            
        # 3. Dibujar Semáforos iterando por intersección para asignar el tiempo correcto
        for inter in intersecciones:
            id_int = inter["id"]
            # Extraemos la fase y el tiempo restante de esta intersección específica
            fase, tiempo_fase = diccionario_tiempos.get(id_int, (0, 0))
            tiempo_entero = int(max(0, tiempo_fase))
            
            for s in inter["autos"]:
                if s.estado in ["verde", "amarillo"]:
                    s.dibujar(screen, tiempo_restante=tiempo_entero)
                else:
                    s.dibujar(screen, tiempo_restante=None)
                
    else:
        # Si la simulación está en pausa, todo a rojo y sin numeración
        for s in semaforos_autos: 
            s.estado = "rojo"
            s.dibujar(screen, tiempo_restante=None)
        for auto in vehiculos: 
            auto.actualizar(semaforos_autos, vehiculos, {})

    # Dibujar el resto de elementos en sus capas correspondientes
    for humano in peatones: humano.dibujar(screen)
    for auto in vehiculos: auto.dibujar(screen)
    for sp in semaforos_peatonales: sp.dibujar(screen)

    #dibujar la interfaz de la tabla
    interfaz.dibujar_tabla(screen, historial, cerebro_trafico)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()