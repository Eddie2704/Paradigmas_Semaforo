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
intersecciones = [] 

#CONFIGURACIÓN DE SENSORES HARDWARE VIAL (Mapeados desde mapa.py)
sensores_lazos = {}
id_cruce = 0

for x in CX:
    for y in CY:
        # Semáforos Vehiculares
        s_norte = Semaforo(x + 60, y - 30, "horizontal")
        s_sur   = Semaforo(x - 0,  y + 110, "horizontal")
        s_este  = Semaforo(x - 20, y + 0, "vertical")
        s_oeste = Semaforo(x + 100, y + 60, "vertical")
        
        # Guardamos en la lista global para los vehículos
        semaforos_autos.extend([s_norte, s_sur, s_este, s_oeste])

        # Semáforos Peatonales
        sp1 = SemaforoPeatonal(x - 30, y - 30)
        sp2 = SemaforoPeatonal(x + 120, y - 30)
        sp3 = SemaforoPeatonal(x - 30, y + 115)
        sp4 = SemaforoPeatonal(x + 120, y + 115)
        
        # Guardamos en la lista global para los peatones (compatibilidad)
        semaforos_peatonales.extend([sp1, sp2, sp3, sp4])

        #Asignamos su ID único y sus semáforos
        intersecciones.append({
            "id": id_cruce,
            "autos": [s_norte, s_sur, s_este, s_oeste],
            "peatones": [sp1, sp2, sp3, sp4]
        })
        
        # Guardar las posiciones exactas de los cuadros grises para las colisiones físicas
        sensores_lazos[id_cruce] = {
            "NORTE": pygame.Rect(x + 8, y - 55, 38, 15),
            "SUR": pygame.Rect(x + 54, y + 140, 38, 15),
            "OESTE": pygame.Rect(x - 55, y + 54, 15, 38),
            "ESTE": pygame.Rect(x + 140, y + 8, 15, 38)
        }
        
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

    # 1. CAPTURA DE EVENTOS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Clic izquierdo
                interfaz.verificar_click(event.pos)
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

        # --- Inyección pura de flujo vehicular/peatonal (Sin conteo prematuro) ---
        elif estimulo_recibido == "AUTO_NORTE":
            calle_aleatoria = random.choice(CX)
            if modo_peaton: 
                calle_h = random.choice(CY)
                peatones.append(Peaton("NORTE", pos_calle_v=calle_aleatoria, pos_calle_h=calle_h))
                modo_peaton = False
            elif modo_ambulancia: 
                vehiculos.append(Vehiculo("NORTE", tipo="AMBULANCIA", pos_calle=calle_aleatoria))
                modo_ambulancia = False
            else: 
                vehiculos.append(Vehiculo("NORTE", tipo="NORMAL", pos_calle=calle_aleatoria))
            
        elif estimulo_recibido == "AUTO_SUR":
            calle_aleatoria = random.choice(CX)
            if modo_peaton: 
                calle_h = random.choice(CY)
                peatones.append(Peaton("SUR", pos_calle_v=calle_aleatoria, pos_calle_h=calle_h))
                modo_peaton = False
            elif modo_ambulancia: 
                vehiculos.append(Vehiculo("SUR", tipo="AMBULANCIA", pos_calle=calle_aleatoria))
                modo_ambulancia = False
            else: 
                vehiculos.append(Vehiculo("SUR", tipo="NORMAL", pos_calle=calle_aleatoria))
            
        elif estimulo_recibido == "AUTO_ESTE":
            calle_aleatoria = random.choice(CY)
            if modo_peaton: 
                calle_v = random.choice(CX)
                peatones.append(Peaton("ESTE", pos_calle_v=calle_v, pos_calle_h=calle_aleatoria))
                modo_peaton = False
            elif modo_ambulancia: 
                vehiculos.append(Vehiculo("ESTE", tipo="AMBULANCIA", pos_calle=calle_aleatoria))
                modo_ambulancia = False
            else: 
                vehiculos.append(Vehiculo("ESTE", tipo="NORMAL", pos_calle=calle_aleatoria))
            
        elif estimulo_recibido == "AUTO_OESTE":
            calle_aleatoria = random.choice(CY)
            if modo_peaton: 
                calle_v = random.choice(CX)
                peatones.append(Peaton("OESTE", pos_calle_v=calle_v, pos_calle_h=calle_aleatoria))
                modo_peaton = False
            elif modo_ambulancia: 
                vehiculos.append(Vehiculo("OESTE", tipo="AMBULANCIA", pos_calle=calle_aleatoria))
                modo_ambulancia = False
            else: 
                vehiculos.append(Vehiculo("OESTE", tipo="NORMAL", pos_calle=calle_aleatoria))

    # 4. ACTUALIZACIÓN Y RENDERIZADO VISUAL
    dibujar_mapa(screen)
    if not simulacion_activa:
        diccionario_tiempos = {}      

    if simulacion_activa:
        # 1. Ejecutar la inteligencia del controlador.
        diccionario_tiempos = cerebro_trafico.procesar_inteligencia(intersecciones, vehiculos, entorno)
        
        # 2. Actualizar peatones
        for humano in peatones[:]:
            humano.actualizar(semaforos_peatonales)
            
            # Condición de salida
            desaparecer = False
            if humano.cruce == "NORTE" or humano.cruce == "SUR":
                if humano.x > humano.pos_calle_v + 120:
                    desaparecer = True
            elif humano.cruce == "OESTE" or humano.cruce == "ESTE":
                if humano.y > humano.pos_calle_h + 120:
                    desaparecer = True
                    
            if desaparecer:
                peatones.remove(humano)
            
        # 3. Actualizar vehículos y procesar sensores físicos sobre el mapa
        for auto in vehiculos[:]:
            auto.actualizar(semaforos_autos, vehiculos, diccionario_tiempos)  
            
            # --- DETECCIÓN FÍSICA EN CUADROS GRISES ---
            if not hasattr(auto, 'cruces_contados'):
                auto.cruces_contados = []
                
            # Caja de colisión virtual del auto basada en su tamaño y coordenadas actuales
            auto_rect = pygame.Rect(auto.x, auto.y, 30, 20) 
            
            # Comprobar si el auto está rodando sobre algún sensor de inducción
            for id_int, direcciones in sensores_lazos.items():
                for direccion, lazo_rect in direcciones.items():
                    if auto_rect.colliderect(lazo_rect) and (id_int, direccion) not in auto.cruces_contados:
                        historial.registrar_vehiculo(id_int, direccion)
                        auto.cruces_contados.append((id_int, direccion))
                        print(f"[SENSOR] Vehículo detectado físicamente en Cruce {id_int + 1} ({direccion})")
            # ------------------------------------------
            
            if auto.x < -50 or auto.x > 1200 or auto.y < -50 or auto.y > 750: 
                vehiculos.remove(auto)
            
        # 4. Dibujar Semáforos iterando por intersección para asignar el tiempo correcto
        for inter in intersecciones:
            id_int = inter["id"]
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
    interfaz.dibujar_interfaz(screen, historial, cerebro_trafico, diccionario_tiempos)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()