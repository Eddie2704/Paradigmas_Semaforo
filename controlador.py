# controlador.py
import pygame

class ControladorTrafico:
    def __init__(self):
        # Tiempos base por defecto
        self.tiempo_amarillo = 2000    
        self.tiempo_peatonal = 4000    
        
        self.ultima_actualizacion = pygame.time.get_ticks()
        self.fase_actual = 0  # 0: Norte/Sur, 1: Este/Oeste, 2: Peatones
        self.estado_luces = "verde" 
        
        # Control de madrugada
        self.ultimo_parpadeo = 0
        self.amarillo_encendido = True

        # ==============================================================================
        # NUEVO: SISTEMA DE SENSORES Y BASADO EN DATOS
        # ==============================================================================
        # Simula el conteo de vehículos que han pasado por cada calle en el último intervalo
        self.historial_sensores = {
            "NORTE": 0,
            "SUR": 0,
            "ESTE": 0,
            "OESTE": 0
        }
        self.ultimo_analisis_datos = pygame.time.get_ticks()
        # El tiempo asignado dinámicamente a cada fase según sus datos de flujo
        self.tiempo_verde_fase = {0: 5000, 1: 5000} # Fase 0 (N/S) inicia en 5s, Fase 1 (E/O) en 5s
        
        # Lista de vehículos que ya fueron contabilizados por el sensor para no repetir
        self.vehiculos_contados = set()

    def procesar_inteligencia(self, semaforos_autos, semaforos_peatonales, vehiculos, entorno):
        tiempo_actual = pygame.time.get_ticks()
        tiempo_restante_segundos = 0

        # --------------------------------------------------------------------------
        # SENSOR 1: RECOLECCIÓN DE DATOS EN TIEMPO REAL (Conteo de flujo por las calles)
        # --------------------------------------------------------------------------
        for v in vehiculos:
            # Si el vehículo pasó la línea del semáforo, el "sensor de la calle" lo cuenta
            if v not in self.vehiculos_contados:
                # Condición de haber cruzado la zona de detención típica
                if (v.direccion == "SUR" and v.y > 160) or \
                   (v.direccion == "NORTE" and v.y < 440) or \
                   (v.direccion == "ESTE" and v.x > 260) or \
                   (v.direccion == "OESTE" and v.x < 540):
                    
                    self.historial_sensores[v.direccion] += 1
                    self.vehiculos_contados.add(v)

        # ALGORITMO DE OPTIMIZACIÓN EN BASE A DATOS (Cada 15 segundos simula los "10 minutos")
        if tiempo_actual - self.ultimo_analisis_datos > 15000:
            flujo_ns = self.historial_sensores["NORTE"] + self.historial_sensores["SUR"]
            flujo_eo = self.historial_sensores["ESTE"] + self.historial_sensores["OESTE"]
            
            # Algoritmo adaptativo: Asigna más tiempo verde a la fase con más historial de datos
            if flujo_ns > flujo_eo:
                self.tiempo_verde_fase[0] = 8000  # Dar 8 segundos a Norte/Sur por alta demanda
                self.tiempo_verde_fase[1] = 4000  # Reducir Este/Oeste a 4 segundos
                print(f"[Datos] Mayor flujo en Eje N/S ({flujo_ns} autos). Adaptando tiempos verdes.")
            elif flujo_eo > flujo_ns:
                self.tiempo_verde_fase[0] = 4000
                self.tiempo_verde_fase[1] = 8000
                print(f"[Datos] Mayor flujo en Eje E/O ({flujo_eo} autos). Adaptando tiempos verdes.")
            else:
                self.tiempo_verde_fase[0] = 5000
                self.tiempo_verde_fase[1] = 5000
            
            # Reiniciar contadores del intervalo de datos
            self.historial_sensores = {"NORTE": 0, "SUR": 0, "ESTE": 0, "OESTE": 0}
            self.ultimo_analisis_datos = tiempo_actual

        # --------------------------------------------------------------------------
        # SENSOR 2: LECTOR RFID DE EMERGENCIA (Pegatina Única de la Ambulancia)
        # --------------------------------------------------------------------------
        ambulancia_rfid_detectada = None
        for v in vehiculos:
            # Si el vehículo tiene el Tag RFID de ambulancia autorizado y está cerca de la intersección
            if v.rfid_tag == "AMB-UNAH-911":
                # Verificar rango de proximidad al cruce
                if (v.direccion == "SUR" and v.y < 160) or \
                   (v.direccion == "NORTE" and v.y > 440) or \
                   (v.direccion == "ESTE" and v.x < 260) or \
                   (v.direccion == "OESTE" and v.x > 540):
                    ambulancia_rfid_detectada = v.direccion

        if ambulancia_rfid_detectada is not None:
            if ambulancia_rfid_detectada in ["NORTE", "SUR"]:
                semaforos_autos[0].estado, semaforos_autos[1].estado = "verde", "verde"
                semaforos_autos[2].estado, semaforos_autos[3].estado = "rojo", "rojo"
                self.fase_actual = 0
            else:
                semaforos_autos[0].estado, semaforos_autos[1].estado = "rojo", "rojo"
                semaforos_autos[2].estado, semaforos_autos[3].estado = "verde", "verde"
                self.fase_actual = 1
                
            for sp in semaforos_peatonales: sp.estado = "rojo"
            return self.fase_actual, 0

        # ---------------------------------------------------------
        # MODO DE MADRUGADA 
        # ---------------------------------------------------------
        if entorno["es_de_madrugada"]:
            if tiempo_actual - self.ultimo_parpadeo > 500:
                self.amarillo_encendido = not self.amarillo_encendido
                self.ultimo_parpadeo = tiempo_actual
            estado_intermitente = "intermitente" if self.amarillo_encendido else "apagado"
            for s in semaforos_autos: s.estado = estado_intermitente
            for sp in semaforos_peatonales: sp.estado = "rojo"
            return self.fase_actual, 0

        # ---------------------------------------------------------
        # MÁQUINA DE ESTADOS CONFIGURADA CON LOS TIEMPOS DE LOS DATOS
        # ---------------------------------------------------------
        tiempo_transcurrido = tiempo_actual - self.ultima_actualizacion
        # Usamos el tiempo verde calculado por nuestro algoritmo de historial de datos
        verde_actual_dinamico = self.tiempo_verde_fase.get(self.fase_actual, 5000)

        if self.estado_luces == "verde":
            tiempo_restante_segundos = (verde_actual_dinamico - tiempo_transcurrido) / 1000
        elif self.estado_luces == "amarillo":
            tiempo_restante_segundos = (self.tiempo_amarillo - tiempo_transcurrido) / 1000
        elif self.fase_actual == 2:
            tiempo_restante_segundos = (self.tiempo_peatonal - tiempo_transcurrido) / 1000

        if self.estado_luces == "verde" and tiempo_transcurrido > verde_actual_dinamico:
            self.estado_luces = "amarillo"
            self.ultima_actualizacion = tiempo_actual
        elif self.estado_luces == "amarillo" and tiempo_transcurrido > self.tiempo_amarillo:
            self.estado_luces = "verde"
            self.ultima_actualizacion = tiempo_actual
            
            if entorno["solicitud_peaton"]:
                self.fase_actual = 2 
            else:
                self.fase_actual = 1 if self.fase_actual == 0 else 0

        elif self.fase_actual == 2 and tiempo_transcurrido > self.tiempo_peatonal:
            entorno["solicitud_peaton"] = False
            self.fase_actual = 0
            self.estado_luces = "verde"
            self.ultima_actualizacion = tiempo_actual

        self.actualizar_luces_fisicas(semaforos_autos, semaforos_peatonales)
        return self.fase_actual, max(0, tiempo_restante_segundos)

    def actualizar_luces_fisicas(self, semaforos_autos, semaforos_peatonales):
        if self.fase_actual == 0:
            semaforos_autos[0].estado = self.estado_luces
            semaforos_autos[1].estado = self.estado_luces
            semaforos_autos[2].estado, semaforos_autos[3].estado = "rojo", "rojo"
            for sp in semaforos_peatonales: sp.estado = "rojo"
        elif self.fase_actual == 1:
            semaforos_autos[0].estado, semaforos_autos[1].estado = "rojo", "rojo"
            semaforos_autos[2].estado = self.estado_luces
            semaforos_autos[3].estado = self.estado_luces
            for sp in semaforos_peatonales: sp.estado = "rojo"
        elif self.fase_actual == 2:
            for s in semaforos_autos: s.estado = "rojo"
            for sp in semaforos_peatonales: sp.estado = "verde"