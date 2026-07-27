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

# Dimensiones optimizadas para la cuadrícula 2x2
ANCHO_BASE, ALTO_BASE = 1150, 700
screen = pygame.display.set_mode((ANCHO_BASE, ALTO_BASE), pygame.RESIZABLE)
pygame.display.set_caption("Simulador Semaforo Inteligente")
clock = pygame.time.Clock()

# Coordenadas maestras de los 4 cruces (Nodos)
CX = [250, 750]  
CY = [120, 470]  

# LÓGICA DE POSICIONAMIENTO Y ORIENTACIÓN DE SEMÁFOROS
semaforos_autos = []
semaforos_peatonales = []
intersecciones = [] 

# CONFIGURACIÓN DE SENSORES HARDWARE VIAL
sensores_lazos = {}
id_cruce = 0

for x in CX:
    for y in CY:
        # Semáforos Vehiculares
        s_norte = Semaforo(x + 60, y - 30, "horizontal")
        s_sur   = Semaforo(x - 0,  y + 110, "horizontal")
        s_este  = Semaforo(x - 20, y + 0, "vertical")
        s_oeste = Semaforo(x + 100, y + 60, "vertical")
        
        semaforos_autos.extend([s_norte, s_sur, s_este, s_oeste])

        # Semáforos Peatonales
        sp1 = SemaforoPeatonal(x - 30, y - 30)
        sp2 = SemaforoPeatonal(x + 120, y - 30)
        sp3 = SemaforoPeatonal(x - 30, y + 115)
        sp4 = SemaforoPeatonal(x + 120, y + 115)
        
        semaforos_peatonales.extend([sp1, sp2, sp3, sp4])

        intersecciones.append({
            "id": id_cruce,
            "autos": [s_norte, s_sur, s_este, s_oeste],
            "peatones": [sp1, sp2, sp3, sp4]
        })
        
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
    "zona_bloqueada": None,
    "justo_despejado": False
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
    tiempo_actual = pygame.time.get_ticks()

    # ==========================================
    # 1. CAPTURA DE EVENTOS LOCALES
    # ==========================================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                interfaz.verificar_click(event.pos)
        elif event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                if not simulacion_activa:
                    simulacion_activa = True
                    for inter in intersecciones:
                        id_int = inter["id"]
                        cerebro_trafico._inicializar_interseccion_si_no_existe(id_int)
                        
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

    # ==========================================
    # 2. CAPTURA REMOTA (MQTT)
    # ==========================================
    evento_mqtt = lector_mqtt.leer()
    if evento_mqtt:
        estimulo_recibido = evento_mqtt

    entorno["evento_mqtt"] = None 

    # ==========================================
    # 3. PROCESAMIENTO DE ESTÍMULOS
    # ==========================================
    if estimulo_recibido:
        print(f"[EVENTO] Procesando: {estimulo_recibido}")
        entorno["evento_mqtt"] = estimulo_recibido 
        
        if estimulo_recibido in ["MODO_PEATON", "PEATON", "SOLICITUD_SEMAFORO_PEATON"]:
            entorno["solicitud_peaton"] = True
            modo_peaton = True; modo_ambulancia = False
        elif estimulo_recibido == "AMBULANCIA":
            modo_ambulancia = True; modo_peaton = False
        elif estimulo_recibido == "MADRUGADA":
            entorno["es_de_madrugada"] = not entorno["es_de_madrugada"]

        elif "COLISION" in estimulo_recibido:
            entorno["colision_activa"] = True
            entorno["zona_bloqueada"] = int(estimulo_recibido.split("_")[-1])
            entorno["tiempo_inicio_colision"] = tiempo_actual
            
        elif estimulo_recibido == "AUTO_NORTE":
            calle_aleatoria = random.choice(CX)
            if modo_peaton: 
                peatones.append(Peaton("NORTE", pos_calle_v=calle_aleatoria, pos_calle_h=random.choice(CY)))
                modo_peaton = False
            elif modo_ambulancia: 
                vehiculos.append(Vehiculo("NORTE", tipo="AMBULANCIA", pos_calle=calle_aleatoria))
                modo_ambulancia = False
            else: 
                vehiculos.append(Vehiculo("NORTE", tipo="NORMAL", pos_calle=calle_aleatoria))
            
        elif estimulo_recibido == "AUTO_SUR":
            calle_aleatoria = random.choice(CX)
            if modo_peaton: 
                peatones.append(Peaton("SUR", pos_calle_v=calle_aleatoria, pos_calle_h=random.choice(CY)))
                modo_peaton = False
            elif modo_ambulancia: 
                vehiculos.append(Vehiculo("SUR", tipo="AMBULANCIA", pos_calle=calle_aleatoria))
                modo_ambulancia = False
            else: 
                vehiculos.append(Vehiculo("SUR", tipo="NORMAL", pos_calle=calle_aleatoria))
            
        elif estimulo_recibido == "AUTO_ESTE":
            calle_aleatoria = random.choice(CY)
            if modo_peaton: 
                peatones.append(Peaton("ESTE", pos_calle_v=random.choice(CX), pos_calle_h=calle_aleatoria))
                modo_peaton = False
            elif modo_ambulancia: 
                vehiculos.append(Vehiculo("ESTE", tipo="AMBULANCIA", pos_calle=calle_aleatoria))
                modo_ambulancia = False
            else: 
                vehiculos.append(Vehiculo("ESTE", tipo="NORMAL", pos_calle=calle_aleatoria))
            
        elif estimulo_recibido == "AUTO_OESTE":
            calle_aleatoria = random.choice(CY)
            if modo_peaton: 
                peatones.append(Peaton("OESTE", pos_calle_v=random.choice(CX), pos_calle_h=calle_aleatoria))
                modo_peaton = False
            elif modo_ambulancia: 
                vehiculos.append(Vehiculo("OESTE", tipo="AMBULANCIA", pos_calle=calle_aleatoria))
                modo_ambulancia = False
            else: 
                vehiculos.append(Vehiculo("OESTE", tipo="NORMAL", pos_calle=calle_aleatoria))

    # ==========================================
    # 4. TEMPORIZADOR DE COLISIÓN (30 Segundos)
    # ==========================================
    if entorno.get("colision_activa"):
        if "tiempo_inicio_colision" in entorno:
            if tiempo_actual - entorno["tiempo_inicio_colision"] >= 30000:
                entorno["colision_activa"] = False
                entorno["justo_despejado"] = True  
                del entorno["tiempo_inicio_colision"]
                
                # Restaurar velocidad
                for auto in vehiculos:
                    if hasattr(auto, 'velocidad_maxima'):
                        auto.velocidad = auto.velocidad_maxima

    # ==========================================
    # 5. ACTUALIZACIÓN DE LÓGICA DE SIMULACIÓN
    # ==========================================
    diccionario_tiempos = {}      

    if simulacion_activa:
        diccionario_tiempos = cerebro_trafico.procesar_inteligencia(intersecciones, vehiculos, entorno)
        
        # Bloquear semáforos en ROJO en el cruce de la colisión
        if entorno.get("colision_activa"):
            zona_bloq = entorno.get("zona_bloqueada", 0)
            if 0 <= zona_bloq < len(intersecciones):
                for s in intersecciones[zona_bloq]["autos"]:
                    s.estado = "rojo"

        # Actualizar peatones
        for humano in peatones[:]:
            humano.actualizar(semaforos_peatonales)
            desaparecer = False
            if humano.cruce in ["NORTE", "SUR"] and humano.x > humano.pos_calle_v + 120:
                desaparecer = True
            elif humano.cruce in ["OESTE", "ESTE"] and humano.y > humano.pos_calle_h + 120:
                desaparecer = True
                    
            if desaparecer:
                peatones.remove(humano)
            
        # Actualización de vehículos
        for auto in vehiculos[:]:
            
            if entorno.get("colision_activa"):
                bloqueo = entorno.get("zona_bloqueada", 0)

                # Mapeo de coordenadas
                cx_bloqueo = CX[0] if bloqueo in [0, 1] else CX[1]
                cy_bloqueo = CY[0] if bloqueo in [0, 2] else CY[1]

                dist_x = abs(auto.x - cx_bloqueo)
                dist_y = abs(auto.y - cy_bloqueo)

                # --- B. LÓGICA DE DESVÍOS INTELIGENTES ---
                if bloqueo == 0:  # Colisión en Nodo 0
                    
                    # 1. Autos bajando (dir="SUR") esquivan hacia el ESTE
                    if auto.direccion == "SUR" and dist_x < 40 and 40 < (cy_bloqueo - auto.y) < 65:
                        auto.direccion = "ESTE"
                        if hasattr(auto, 'velocidad_maxima'): auto.velocidad = auto.velocidad_maxima
                        
                    # 2. Autos yendo a la derecha (dir="ESTE") esquivan hacia el SUR
                    elif auto.direccion == "ESTE" and dist_y < 40 and 40 < (cx_bloqueo - auto.x) < 65:
                        auto.direccion = "SUR"
                        if hasattr(auto, 'velocidad_maxima'): auto.velocidad = auto.velocidad_maxima

                    # 3. Autos subiendo (dir="NORTE") esquivan hacia el OESTE
                    elif auto.direccion == "NORTE" and dist_x < 40 and 40 < (auto.y - cy_bloqueo) < 65:
                        auto.direccion = "OESTE"
                        if hasattr(auto, 'velocidad_maxima'): auto.velocidad = auto.velocidad_maxima

                    # 4. Autos yendo a la izquierda (dir="OESTE") esquivan hacia el NORTE
                    elif auto.direccion == "OESTE" and dist_y < 40 and 40 < (auto.x - cx_bloqueo) < 65:
                        auto.direccion = "NORTE"
                        if hasattr(auto, 'velocidad_maxima'): auto.velocidad = auto.velocidad_maxima

                    # Desvíos preventivos lejanos
                    elif auto.direccion == "NORTE" and dist_x < 40 and abs(auto.y - CY[1]) < 10:
                        auto.direccion = "ESTE" # Gira en el Nodo Sur
                    elif auto.direccion == "OESTE" and dist_y < 40 and abs(auto.x - CX[1]) < 10:
                        auto.direccion = "SUR"  # Gira en el Nodo Este

                # --- A. FRENADO DE SEGURIDAD EXTREMA ---
                # Radio súper corto (35px) para que tengan tiempo de doblar antes de frenar
                if dist_x < 35 and dist_y < 35:
                    if auto.direccion == "SUR" and auto.y < cy_bloqueo:
                        auto.velocidad = 0
                    elif auto.direccion == "NORTE" and auto.y > cy_bloqueo:
                        auto.velocidad = 0
                    elif auto.direccion == "ESTE" and auto.x < cx_bloqueo:
                        auto.velocidad = 0
                    elif auto.direccion == "OESTE" and auto.x > cx_bloqueo:
                        auto.velocidad = 0

            else:
                # Restaurar velocidad si ya no hay accidente
                if auto.velocidad == 0 and hasattr(auto, 'velocidad_maxima'):
                    auto.velocidad = auto.velocidad_maxima

            # Actualización física del vehículo
            auto.actualizar(semaforos_autos, vehiculos, diccionario_tiempos)  
            
            # Sensores e historial
            if not hasattr(auto, 'cruces_contados'):
                auto.cruces_contados = []
                
            auto_rect = pygame.Rect(auto.x, auto.y, 30, 20) 
            for id_int, direcciones in sensores_lazos.items():
                for direccion, lazo_rect in direcciones.items():
                    if auto_rect.colliderect(lazo_rect) and (id_int, direccion) not in auto.cruces_contados:
                        historial.registrar_vehiculo(id_int, direccion)
                        auto.cruces_contados.append((id_int, direccion))
            
            # Limpieza fuera de pantalla
            if auto.x < -50 or auto.x > 1200 or auto.y < -50 or auto.y > 750: 
                vehiculos.remove(auto)
            
    else:
        for s in semaforos_autos: 
            s.estado = "rojo"
        for auto in vehiculos: 
            auto.actualizar(semaforos_autos, vehiculos, {})

    # ==========================================
    # 6. RENDERIZADO VISUAL
    # ==========================================
    dibujar_mapa(screen)

    if simulacion_activa:
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
        for s in semaforos_autos:
            s.dibujar(screen, tiempo_restante=None)

    for humano in peatones: 
        humano.dibujar(screen)
    for auto in vehiculos: 
        auto.dibujar(screen)
    for sp in semaforos_peatonales: 
        sp.dibujar(screen)

    # Dibujo de Colisión
    if entorno.get("colision_activa"):
        zona = entorno.get("zona_bloqueada", 0)
        posiciones = [(CX[0], CY[0]), (CX[0], CY[1]), (CX[1], CY[0]), (CX[1], CY[1])]
        
        if 0 <= zona < len(posiciones):
            cx, cy = posiciones[zona]
            centro_x = cx + 50
            centro_y = cy + 50
            
            if (pygame.time.get_ticks() // 250) % 2 == 0:
                pygame.draw.circle(screen, (255, 0, 0), (centro_x, centro_y), 32, width=3)
                pygame.draw.circle(screen, (255, 200, 0), (centro_x, centro_y), 18)
            
            s1 = pygame.Surface((34, 18), pygame.SRCALPHA)
            s1.fill((220, 20, 20))
            rot1 = pygame.transform.rotate(s1, 35)
            screen.blit(rot1, (centro_x - 18, centro_y - 12))
            
            s2 = pygame.Surface((34, 18), pygame.SRCALPHA)
            s2.fill((30, 80, 220))
            rot2 = pygame.transform.rotate(s2, 110)
            screen.blit(rot2, (centro_x - 8, centro_y - 18))
            
            fuente_col = pygame.font.SysFont("Arial", 12, bold=True)
            txt = fuente_col.render("¡COLISIÓN!", True, (255, 255, 255))
            pygame.draw.rect(screen, (180, 0, 0), (centro_x - 35, centro_y - 42, 70, 18), border_radius=3)
            screen.blit(txt, (centro_x - 30, centro_y - 40))

    # Interfaz de Usuario
    interfaz.dibujar_interfaz(screen, historial, cerebro_trafico, diccionario_tiempos)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()