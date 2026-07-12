# historial.py

class HistorialTrafico:
    def __init__(self):
        # Conteo acumulado de vehículos que cruzaron en el periodo actual
        self.vehiculos_por_calle = {
            "NORTE": 0,
            "SUR": 0,
            "ESTE": 0,
            "OESTE": 0
        }
        # Registro histórico general (para reportes en consola)
        self.historico_total = {k: 0 for k in self.vehiculos_por_calle}
        
        self.contador_cambios_fase = 0
        self.limite_cambios = 4  # Ajuste cada 4 cambios de semáforo completo

    def registrar_vehiculo(self, direccion):
        if direccion in self.vehiculos_por_calle:
            self.vehiculos_por_calle[direccion] += 1
            self.historico_total[direccion] += 1

    def registrar_cambio_fase(self, tiempo_verde_base):
        """
        Incrementa el contador de fases. Al llegar al límite (4), 
        calcula los nuevos tiempos verdes óptimos según el flujo de datos.
        """
        self.contador_cambios_fase += 1
        
        if self.contador_cambios_fase >= self.limite_cambios:
            self.contador_cambios_fase = 0
            
            # Calcular flujo por eje funcional
            flujo_ns = self.vehiculos_por_calle["NORTE"] + self.vehiculos_por_calle["SUR"]
            flujo_eo = self.vehiculos_por_calle["ESTE"] + self.vehiculos_por_calle["OESTE"]
            
            total_flujo = flujo_ns + flujo_eo
            
            print("\n" + "="*40)
            print("[HISTORIAL] Analizando datos de los últimos 4 ciclos...")
            print(f" -> Flujo Eje Norte/Sur: {flujo_ns} vehículos")
            print(f" -> Flujo Eje Este/Oeste: {flujo_eo} vehicles")
            
            # Tiempos por defecto
            nuevo_tiempo_ns = tiempo_verde_base
            nuevo_tiempo_eo = tiempo_verde_base
            
            if total_flujo > 0:
                # Algoritmo de optimización: Asignación proporcional del tiempo según el flujo de datos
                proporcion_ns = flujo_ns / total_flujo
                proporcion_eo = flujo_eo / total_flujo
                
                # Definimos un pozo de tiempo total dinámico para el verde (ejemplo: 12 segundos en total)
                tiempo_total_disponible = tiempo_verde_base * 2 
                
                # Asignar tiempos con límites mínimos (3s) y máximos (9s) para evitar bloqueos
                nuevo_tiempo_ns = max(3000, min(9000, int(tiempo_total_disponible * proporcion_ns)))
                nuevo_tiempo_eo = max(3000, min(9000, int(tiempo_total_disponible * proporcion_eo)))
            
            print(f"[ALGORITMO] Nuevos tiempos calculados:")
            print(f" -> Verde Norte/Sur: {nuevo_tiempo_ns / 1000}s")
            print(f" -> Verde Este/Oeste: {nuevo_tiempo_eo / 1000}s")
            print("="*40 + "\n")
            
            # Reiniciar contadores del intervalo de datos
            self.vehiculos_por_calle = {k: 0 for k in self.vehiculos_por_calle}
            
            return nuevo_tiempo_ns, nuevo_tiempo_eo
            
        return None