# historial.py

class HistorialTrafico:
    def __init__(self):
        # Mapeo de IDs a nombres amigables para reportes en consola
        self.nombres_intersecciones = {
            0: "Interseccion 1 (Arriba Izquierda)",
            1: "Interseccion 2 (Arriba Derecha)",
            2: "Interseccion 3 (Abajo Izquierda)",
            3: "Interseccion 4 (Abajo Derecha)"
        }
        
        # Inicializamos las estructuras de datos para las 4 intersecciones
        self.vehiculos_por_calle = {}
        self.historico_total = {}
        self.contador_cambios_fase = {}
        
        for id_int in range(4):
            # Conteo acumulado por periodo actual para cada cruce
            self.vehiculos_por_calle[id_int] = {
                "NORTE": 0,
                "SUR": 0,
                "ESTE": 0,
                "OESTE": 0
            }
            # Historial histórico total de cada cruce
            self.historico_total[id_int] = {
                "NORTE": 0,
                "SUR": 0,
                "ESTE": 0,
                "OESTE": 0
            }
            # Contador de fases independiente por intersección
            self.contador_cambios_fase[id_int] = 0

        self.limite_cambios = 4  # Ajuste cada 4 cambios de semáforo completo

    def registrar_vehiculo(self, id_interseccion, direccion):
        """Registra el paso de un vehículo por el sensor de una intersección específica."""
        if id_interseccion in self.vehiculos_por_calle:
            if direccion in self.vehiculos_por_calle[id_interseccion]:
                self.vehiculos_por_calle[id_interseccion][direccion] += 1
                self.historico_total[id_interseccion][direccion] += 1

    def registrar_cambio_fase(self, id_interseccion, tiempo_verde_base):
        """
        Incrementa el contador de fases de una intersección específica.
        Al llegar al límite (4), calcula los nuevos tiempos verdes óptimos 
        según el flujo de datos exclusivo de esa intersección.
        """
        if id_interseccion not in self.contador_cambios_fase:
            return None

        self.contador_cambios_fase[id_interseccion] += 1
        
        if self.contador_cambios_fase[id_interseccion] >= self.limite_cambios:
            self.contador_cambios_fase[id_interseccion] = 0
            
            datos_cruce = self.vehiculos_por_calle[id_interseccion]
            
            # Calcular flujo por eje funcional en esta intersección
            flujo_ns = datos_cruce["NORTE"] + datos_cruce["SUR"]
            flujo_eo = datos_cruce["ESTE"] + datos_cruce["OESTE"]
            
            total_flujo = flujo_ns + flujo_eo
            
            # Tiempos por defecto
            nuevo_tiempo_ns = tiempo_verde_base
            nuevo_tiempo_eo = tiempo_verde_base
            
            if total_flujo > 0:
                # Algoritmo de optimización: Asignación proporcional según el flujo
                proporcion_ns = flujo_ns / total_flujo
                proporcion_eo = flujo_eo / total_flujo
                
                # Pozo de tiempo total dinámico para el verde (milisegundos)
                tiempo_total_disponible = tiempo_verde_base * 2 
                
                # Asignar tiempos con límites mínimos (3s) y máximos (9s)
                nuevo_tiempo_ns = max(3000, min(9000, int(tiempo_total_disponible * proporcion_ns)))
                nuevo_tiempo_eo = max(3000, min(9000, int(tiempo_total_disponible * proporcion_eo)))
                
                nombre = self.nombres_intersecciones.get(id_interseccion, f"Cruce {id_interseccion}")
                print(f"[OPTIMIZACIÓN {nombre}] Nuevo Tiempo NS: {nuevo_tiempo_ns}ms, EO: {nuevo_tiempo_eo}ms")
            
            # Reiniciar contadores del intervalo de datos para esta intersección
            self.vehiculos_por_calle[id_interseccion] = {k: 0 for k in datos_cruce}
            
            return nuevo_tiempo_ns, nuevo_tiempo_eo
            
        return None