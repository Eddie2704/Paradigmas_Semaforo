# controlador.py
import pygame
from historial import HistorialTrafico

class ControladorTrafico:
    def __init__(self):
        self.tiempo_verde_base = 5000  # 5 segundos base inicial
        self.tiempo_amarillo = 2000    
        self.tiempo_peatonal = 4000    
        
        # Diccionario para almacenar el estado independiente de cada intersección
        self.estados_intersecciones = {}
        
        # Control de madrugada general o por intersección
        self.ultimo_parpadeo = 0
        self.amarillo_encendido = True

        # Integración con el sistema de sensores e historial basado en datos
        self.historial = HistorialTrafico()
        self.vehiculos_contados = set()

    def _inicializar_interseccion_si_no_existe(self, id_int):
        """Inicializa las variables de estado dinámicas para una nueva intersección."""
        if id_int not in self.estados_intersecciones:
            self.estados_intersecciones[id_int] = {
                "fase_actual": 0,  # 0: Norte/Sur, 1: Este/Oeste, 2: Peatones
                "estado_luces": "verde",
                "ultima_actualizacion": pygame.time.get_ticks(),
                "tiempo_verde_fase": {0: 5000, 1: 5000}
            }

    def procesar_inteligencia(self, lista_intersecciones, vehiculos, entorno):
        """
        Argumentos:
        - lista_intersecciones: Lista de diccionarios con el ID y componentes de cada cruce.
        - vehiculos: Lista global de vehículos activos en la simulación.
        - entorno: Diccionario de variables globales del entorno.
        """
        tiempo_actual = pygame.time.get_ticks()
        datos_retorno = {} # Guardará (fase, tiempo_restante) de cada intersección

        # 1. LECTOR/SENSOR GENERAL: Registrar carros que cruzan líneas de semáforos
        for v in vehiculos:
            if v not in self.vehiculos_contados:
                if (v.direccion == "SUR" and v.y > 160) or \
                   (v.direccion == "NORTE" and v.y < 440) or \
                   (v.direccion == "ESTE" and v.x > 260) or \
                   (v.direccion == "OESTE" and v.x < 540):
                    
                    # NOTA: Para máxima precisión con 4 cruces, puedes asociar a cada vehículo 
                    # un atributo v.interseccion_id al crearlo, y pasar ese ID aquí:
                    # id_del_cruce_actual = getattr(v, "interseccion_id", 0)
                    # Por defecto usaremos el cruce 0 si no está definido en el objeto Vehiculo:
                    id_del_cruce_actual = 0 
                    
                    self.historial.registrar_vehiculo(id_del_cruce_actual, v.direccion)
                    self.vehiculos_contados.add(v)

        # 2. MODO DE MADRUGADA GLOBAL
        if entorno["es_de_madrugada"]:
            if tiempo_actual - self.ultimo_parpadeo > 500:
                self.amarillo_encendido = not self.amarillo_encendido
                self.ultimo_parpadeo = tiempo_actual
            
            estado_intermitente = "amarillo" if self.amarillo_encendido else "apagado"
            
            for inter in lista_intersecciones:
                for s in inter["autos"]: s.estado = estado_intermitente
                for sp in inter["peatones"]: sp.estado = "rojo"
            
            return {inter["id"]: (0, 0) for inter in lista_intersecciones}

        # 3. PRIORIDAD RFID GENERAL (Ambulancia)
        ambulancia_rfid_detectada = None
        for v in vehiculos:
            if getattr(v, 'rfid_tag', None) == "AMB-UNAH-911":
                if (v.direccion == "SUR" and v.y < 160) or \
                   (v.direccion == "NORTE" and v.y > 440) or \
                   (v.direccion == "ESTE" and v.x < 260) or \
                   (v.direccion == "OESTE" and v.x > 540):
                    ambulancia_rfid_detectada = v.direccion

        # 4. PROCESAR CADA INTERSECCIÓN DE FORMA INDEPENDIENTE
        for inter in lista_intersecciones:
            id_int = inter["id"]
            self._inicializar_interseccion_si_no_existe(id_int)
            est = self.estados_intersecciones[id_int]

            # Aplicar prioridad rfid si aplica a esta intersección
            if ambulancia_rfid_detectada is not None:
                if ambulancia_rfid_detectada in ["NORTE", "SUR"]:
                    inter["autos"][0].estado, inter["autos"][1].estado = "verde", "verde"
                    inter["autos"][2].estado, inter["autos"][3].estado = "rojo", "rojo"
                    est["fase_actual"] = 0
                else:
                    inter["autos"][0].estado, inter["autos"][1].estado = "rojo", "rojo"
                    inter["autos"][2].estado, inter["autos"][3].estado = "verde", "verde"
                    est["fase_actual"] = 1
                for sp in inter["peatones"]: sp.estado = "rojo"
                datos_retorno[id_int] = (est["fase_actual"], 0)
                continue 

            # CONTROL DE TIEMPOS DINÁMICOS Y MÁQUINA DE ESTADOS INDEPENDIENTE
            tiempo_transcurrido = tiempo_actual - est["ultima_actualizacion"]
            verde_actual_dinamico = est["tiempo_verde_fase"].get(est["fase_actual"], self.tiempo_verde_base)

            tiempo_restante_segundos = 0
            if est["estado_luces"] == "verde":
                tiempo_restante_segundos = (verde_actual_dinamico - tiempo_transcurrido) / 1000
            elif est["estado_luces"] == "amarillo":
                tiempo_restante_segundos = (self.tiempo_amarillo - tiempo_transcurrido) / 1000
            elif est["fase_actual"] == 2:
                tiempo_restante_segundos = (self.tiempo_peatonal - tiempo_transcurrido) / 1000

            # Transiciones de estado por intersección
            if est["estado_luces"] == "verde" and tiempo_transcurrido > verde_actual_dinamico:
                est["estado_luces"] = "amarillo"
                est["ultima_actualizacion"] = tiempo_actual
                
                # CORRECCIÓN: Enviamos id_int para actualizar la intersección correspondiente
                nuevos_tiempos = self.historial.registrar_cambio_fase(id_int, self.tiempo_verde_base)
                if nuevos_tiempos:
                    if len(vehiculos) == 0:
                        est["tiempo_verde_fase"][0] = 5000
                        est["tiempo_verde_fase"][1] = 5000
                    else:
                        est["tiempo_verde_fase"][0], est["tiempo_verde_fase"][1] = nuevos_tiempos

            elif est["estado_luces"] == "amarillo" and tiempo_transcurrido > self.tiempo_amarillo:
                est["estado_luces"] = "verde"
                est["ultima_actualizacion"] = tiempo_actual
                
                if entorno.get("solicitud_peaton", False):
                    est["fase_actual"] = 2 
                else:
                    est["fase_actual"] = 1 if est["fase_actual"] == 0 else 0

            elif est["fase_actual"] == 2 and tiempo_transcurrido > self.tiempo_peatonal:
                entorno["solicitud_peaton"] = False
                est["fase_actual"] = 0
                est["estado_luces"] = "verde"
                est["ultima_actualizacion"] = tiempo_actual

            # Actualizar hardware visual de esta intersección en específico
            self.actualizar_luces_fisicas(inter["autos"], inter["peatones"], est["fase_actual"], est["estado_luces"])
            datos_retorno[id_int] = (est["fase_actual"], max(0, tiempo_restante_segundos))

        return datos_retorno

    def actualizar_luces_fisicas(self, semaforos_autos, semaforos_peatonales, fase_actual, estado_luces):
        if fase_actual == 0:
            semaforos_autos[0].estado, semaforos_autos[1].estado = estado_luces, estado_luces
            semaforos_autos[2].estado, semaforos_autos[3].estado = "rojo", "rojo"
            for sp in semaforos_peatonales: sp.estado = "rojo"
        elif fase_actual == 1:
            semaforos_autos[0].estado, semaforos_autos[1].estado = "rojo", "rojo"
            semaforos_autos[2].estado, semaforos_autos[3].estado = estado_luces, estado_luces
            for sp in semaforos_peatonales: sp.estado = "rojo"
        elif fase_actual == 2:
            for s in semaforos_autos: s.estado = "rojo"
            for sp in semaforos_peatonales: sp.estado = "verde"