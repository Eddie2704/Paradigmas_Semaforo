import pygame

class InterfazDatos:
    def __init__(self):
        pygame.font.init()
        # Fuentes monoespaciadas ideales para datos estructurados
        self.fuente_titulo = pygame.font.SysFont("Courier New", 14, bold=True)
        self.fuente_texto = pygame.font.SysFont("Courier New", 12)
        self.fuente_bold = pygame.font.SysFont("Courier New", 12, bold=True)
        
        # --- PANEL DERECHO INTEGRADO ---
        # Se ubica exactamente donde termina el mapa (X: 850) hasta el final (1150)
        self.x_panel = 850
        self.y_panel = 0
        self.ancho_panel = 300
        self.alto_panel = 700 # Ocupa todo el alto de la ventana

    def dibujar_tabla(self, screen, historial, controlador):
        """Dibuja el panel analítico integrado en el extremo derecho de la pantalla"""
        
        # 1. Fondo del panel lateral (Gris oscuro/Antracita para estilo Dark Mode)
        pygame.draw.rect(screen, (24, 24, 24), (self.x_panel, self.y_panel, self.ancho_panel, self.alto_panel))
        
        # 2. Línea divisoria vertical entre la simulación y los datos
        pygame.draw.line(screen, (60, 60, 60), (self.x_panel, 0), (self.x_panel, self.alto_panel), 2)
        
        # 3. Título del Panel
        txt_titulo = self.fuente_titulo.render("HISTORIAL DE TRÁFICO", True, (0, 255, 255))
        screen.blit(txt_titulo, (self.x_panel + 20, 30))
        
        # Subtítulo o estado del sistema
        txt_sub = self.fuente_texto.render("Estado: Monitoreando...", True, (150, 150, 150))
        screen.blit(txt_sub, (self.x_panel + 20, 55))
        
        # 4. Tabla de datos por Intersección
        y_offset = 110
        t_verde_seg = controlador.tiempo_verde_base / 1000
        
        # Intentamos recuperar de forma segura el diccionario del historial
        dict_origen = getattr(historial, "datos_cruce", getattr(historial, "historial", getattr(historial, "registro", {})))
        total_global = 0

        # Dibujar cabecera de la mini-tabla
        header_int = self.fuente_bold.render("Intersección", True, (200, 200, 200))
        header_veh = self.fuente_bold.render("Vehículos", True, (200, 200, 200))
        screen.blit(header_int, (self.x_panel + 20, y_offset))
        screen.blit(header_veh, (self.x_panel + 180, y_offset))
        
        pygame.draw.line(screen, (80, 80, 80), (self.x_panel + 20, y_offset + 18), (self.x_panel + 280, y_offset + 18), 1)
        y_offset += 30

        # Renderizar las filas para las 4 intersecciones
        for idx in range(4):
            autos_cruzados = 0
            if isinstance(dict_origen, dict):
                sub_dict = dict_origen.get(idx, dict_origen.get(str(idx), {}))
                if isinstance(sub_dict, dict):
                    autos_cruzados = sub_dict.get("vehiculos_pasados", 0)
            
            total_global += autos_cruzados
            
            # Dibujar textos de la fila
            txt_col1 = self.fuente_texto.render(f"Cruze #{idx + 1}", True, (255, 255, 255))
            txt_col2 = self.fuente_texto.render(f"{autos_cruzados} vh", True, (152, 195, 121)) # Verde suave
            
            screen.blit(txt_col1, (self.x_panel + 20, y_offset))
            screen.blit(txt_col2, (self.x_panel + 180, y_offset))
            y_offset += 25
            
        # 5. Sección de Resumen Global e Inteligencia
        y_offset += 20
        pygame.draw.rect(screen, (34, 34, 34), (self.x_panel + 15, y_offset, self.ancho_panel - 30, 120), border_radius=5)
        
        lbl_resumen = self.fuente_bold.render("MÉTRICAS DE LA RED", True, (229, 192, 123)) # Amarillo/Ámbar
        screen.blit(lbl_resumen, (self.x_panel + 25, y_offset + 12))
        
        lbl_total = self.fuente_texto.render(f"Total Autos: {total_global}", True, (255, 255, 255))
        screen.blit(lbl_total, (self.x_panel + 25, y_offset + 42))
        
        lbl_tiempo = self.fuente_texto.render(f"T. Verde Base: {t_verde_seg}s", True, (255, 255, 255))
        screen.blit(lbl_tiempo, (self.x_panel + 25, y_offset + 67))
        
        lbl_modo = self.fuente_texto.render("Optimización: Activa", True, (98, 114, 164))
        screen.blit(lbl_modo, (self.x_panel + 25, y_offset + 92))