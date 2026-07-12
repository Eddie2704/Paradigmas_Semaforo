import pygame
from historial import HistorialTrafico

class ControladorTrafico:
    def __init__(self):
        self.tiempo_verde_base = 5000  # 5 segundos base inicial
        self.tiempo_amarillo = 2000    
        self.tiempo_peatonal = 4000    
        
        self.ultima_actualizacion = pygame.time.get_ticks()
        self.fase_actual = 0  # 0: Norte/Sur, 1: Este/Oeste, 2: Peatones
        self.estado_luces = "verde" 
        
        # Control de madrugada
        self.ultimo_parpadeo = 0
        self.amarillo_encendido = True

        # Integración con el sistema de sensores e historial basado en datos
        self.historial = HistorialTrafico()
        self.tiempo_verde_fase = {0: 5000, 1: 5000} # Tiempos asignados dinámicamente
        self.vehiculos_contados = set()

    def procesar_inteligencia(self, semaforos_autos, semaforos_peatonales, vehiculos, entorno):
        tiempo_actual = pygame.time.get_ticks()
        tiempo_restante_segundos = 0

        # LECTOR/SENSOR: Registrar carros que cruzan la línea del semáforo
        for v in vehiculos:
            if v not in self.vehiculos_contados:
                if (v.direccion == "SUR" and v.y > 160) or \
                   (v.direccion == "NORTE" and v.y < 440) or \
                   (v.direccion == "ESTE" and v.x > 260) or \
                   (v.direccion == "OESTE" and v.x < 540):
                    
                    self.historial.registrar_vehiculo(v.direccion)
                    self.vehiculos_contados.add(v)

        # PRIORIDAD: Lector RFID de Ambulancias (Pegatina única)
        ambulancia_rfid_detectada = None
        for v in vehiculos:
            if getattr(v, 'rfid_tag', None) == "AMB-UNAH-911":
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

        # MODO DE MADRUGADA
        if entorno["es_de_madrugada"]:
            if tiempo_actual - self.ultimo_parpadeo > 500:
                self.amarillo_encendido = not self.amarillo_encendido
                self.ultimo_parpadeo = tiempo_actual
            
            estado_intermitente = "amarillo" if self.amarillo_encendido else "apagado"
            for s in semaforos_autos: s.estado = estado_intermitente
            for sp in semaforos_peatonales: sp.estado = "rojo"
            
            return self.fase_actual, 0

        # CONTROL DE TIEMPOS DINÁMICOS Y MÁQUINA DE ESTADOS
        tiempo_transcurrido = tiempo_actual - self.ultima_actualizacion
        verde_actual_dinamico = self.tiempo_verde_fase.get(self.fase_actual, self.tiempo_verde_base)

        if self.estado_luces == "verde":
            tiempo_restante_segundos = (verde_actual_dinamico - tiempo_transcurrido) / 1000
        elif self.estado_luces == "amarillo":
            tiempo_restante_segundos = (self.tiempo_amarillo - tiempo_transcurrido) / 1000
        elif self.fase_actual == 2:
            tiempo_restante_segundos = (self.tiempo_peatonal - tiempo_transcurrido) / 1000

        # Transiciones de estado
        if self.estado_luces == "verde" and tiempo_transcurrido > verde_actual_dinamico:
            self.estado_luces = "amarillo"
            self.ultima_actualizacion = tiempo_actual
            
            # Al terminar un estado verde, evaluamos el algoritmo dinámico
            nuevos_tiempos = self.historial.registrar_cambio_fase(self.tiempo_verde_base)
            if nuevos_tiempos:
                # ACCIÓN: Si no hay vehículos circulando en la simulación, forzar retorno a 5 segundos (5000 ms)
                if len(vehiculos) == 0:
                    self.tiempo_verde_fase[0] = 5000
                    self.tiempo_verde_fase[1] = 5000
                    print("--> [SISTEMA] No hay autos en el mapa. Retornando a tiempos base originales (5s).")
                else:
                    self.tiempo_verde_fase[0], self.tiempo_verde_fase[1] = nuevos_tiempos

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
            semaforos_autos[0].estado, semaforos_autos[1].estado = self.estado_luces, self.estado_luces
            semaforos_autos[2].estado, semaforos_autos[3].estado = "rojo", "rojo"
            for sp in semaforos_peatonales: sp.estado = "rojo"
        elif self.fase_actual == 1:
            semaforos_autos[0].estado, semaforos_autos[1].estado = "rojo", "rojo"
            semaforos_autos[2].estado, semaforos_autos[3].estado = self.estado_luces, self.estado_luces
            for sp in semaforos_peatonales: sp.estado = "rojo"
        elif self.fase_actual == 2:
            for s in semaforos_autos: s.estado = "rojo"
            for sp in semaforos_peatonales: sp.estado = "verde"