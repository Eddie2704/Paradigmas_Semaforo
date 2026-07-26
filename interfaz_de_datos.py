import pygame

class InterfazDatos:
    def __init__(self):
        # 1. Dimensiones y Posicionamiento del Panel Lateral Desplegable
        self.ancho_panel = 340  
        self.alto_panel = 700
        self.x_panel = 1150 - self.ancho_panel
        self.y_panel = 0
        
        # 2. Control de Estado Desplegable
        self.panel_abierto = False
        
        # 3. Geometría del Botón de Activación / Cierre
        self.ancho_btn = 100
        self.alto_btn = 35
        self.boton_rect = pygame.Rect(0, 0, self.ancho_btn, self.alto_btn)
        
        # 4. Tipografías optimizadas
        self.fuente_titulo = pygame.font.SysFont("Helvetica", 18, bold=True)
        self.fuente_subtitulo = pygame.font.SysFont("Helvetica", 14, bold=True)
        self.fuente_bold = pygame.font.SysFont("Helvetica", 12, bold=True)
        self.fuente_texto = pygame.font.SysFont("Helvetica", 12)

    def verificar_click(self, mouse_pos):
        """Detecta si el usuario presionó el botón de la interfaz"""
        if self.boton_rect.collidepoint(mouse_pos):
            self.panel_abierto = not self.panel_abierto
            print(f"[UI] Panel analítico cambiado a: {self.panel_abierto}")

    def dibujar_interfaz(self, screen, historial, controlador, diccionario_tiempos):
        """Manejador maestro de renderizado - AHORA ACEPTA diccionario_tiempos"""
        ancho_actual = screen.get_width()
        alto_actual = screen.get_height()
        
        self.x_panel = ancho_actual - self.ancho_panel
        self.alto_panel = alto_actual  

        # 1. Posicionar el botón dependiendo del estado del panel
        if self.panel_abierto:
            self.boton_rect.x = ancho_actual - self.ancho_btn - 20
            self.boton_rect.y = self.alto_panel - self.alto_btn - 20
        else:
            self.boton_rect.x = ancho_actual - self.ancho_btn - 20
            self.boton_rect.y = 20

        # 2. Primero dibujamos el panel de fondo si está abierto
        if self.panel_abierto:
            self.dibujar_tabla(screen, historial, controlador, diccionario_tiempos)
            
        # 3. Renderizado del botón por encima del panel
        color_btn = (180, 40, 40) if self.panel_abierto else (40, 40, 40)  
        color_borde = (255, 100, 100) if self.panel_abierto else (100, 100, 100)
        
        pygame.draw.rect(screen, color_btn, self.boton_rect, border_radius=5)
        pygame.draw.rect(screen, color_borde, self.boton_rect, width=2, border_radius=5)
        
        texto_btn = "Cerrar" if self.panel_abierto else "Ver Datos"
        color_txt_btn = (255, 255, 255) if self.panel_abierto else (200, 200, 200)
        txt_render = self.fuente_subtitulo.render(texto_btn, True, color_txt_btn)
        
        text_rect = txt_render.get_rect(center=self.boton_rect.center)
        screen.blit(txt_render, text_rect)

    def dibujar_tabla(self, screen, historial, controlador, diccionario_tiempos):
        """Dibuja el fondo del panel analítico y las tarjetas ampliadas con los tiempos y ciclos"""
        
        # Fondo del panel (Antracita oscuro)
        pygame.draw.rect(screen, (24, 24, 24), (self.x_panel, self.y_panel, self.ancho_panel, self.alto_panel))
        pygame.draw.line(screen, (60, 60, 60), (self.x_panel, 0), (self.x_panel, self.alto_panel), 2)
        
        # Títulos principales
        txt_titulo = self.fuente_titulo.render("MONITOR DE INTERSECCIONES", True, (0, 255, 255))
        screen.blit(txt_titulo, (self.x_panel + 20, 30))
        
        txt_sub = self.fuente_texto.render("Tiempos dinámicos y métricas por cruce", True, (150, 150, 150))
        screen.blit(txt_sub, (self.x_panel + 20, 52))
        
        y_offset = 85
        historial_datos = historial.historico_total

        # Nombres de las fases para mostrarlas de forma amigable
        nombres_fases = {
            0: "Fase 0: Verde N/S",
            1: "Fase 1: Verde E/O",
            2: "Fase 2: Peatonal",
            3: "Fase 3: Madrugada"
        }

        # Iterar por las 4 intersecciones
        for idx in range(4):
            datos_cruce = historial_datos.get(idx, {"NORTE": 0, "SUR": 0, "ESTE": 0, "OESTE": 0})
            
            norte = datos_cruce.get("NORTE", 0)
            sur = datos_cruce.get("SUR", 0)
            este = datos_cruce.get("ESTE", 0)
            omega = datos_cruce.get("OESTE", 0)
            
            total_cruce = norte + sur + este + omega

            # Grids más grandes
            ancho_caja = self.ancho_panel - 40
            pygame.draw.rect(screen, (34, 34, 34), (self.x_panel + 20, y_offset, ancho_caja, 130), border_radius=6)
            pygame.draw.rect(screen, (50, 50, 50), (self.x_panel + 20, y_offset, ancho_caja, 130), width=1, border_radius=6)

            # Encabezado de la Intersección
            txt_cruce = self.fuente_subtitulo.render(f"Intersección {idx + 1}", True, (255, 255, 255))
            txt_total_cruce = self.fuente_bold.render(f"Total: {total_cruce} vh", True, (0, 255, 255))
            screen.blit(txt_cruce, (self.x_panel + 35, y_offset + 10))
            screen.blit(txt_total_cruce, (self.x_panel + 215, y_offset + 10))

            pygame.draw.line(screen, (60, 60, 60), (self.x_panel + 35, y_offset + 32), (self.x_panel + self.ancho_panel - 35, y_offset + 32), 1)

            # Sub-Grilla de Direcciones
            lbl_n = self.fuente_texto.render(f"Norte: {norte} vh", True, (200, 200, 200))
            lbl_e = self.fuente_texto.render(f"Este:  {este} vh", True, (200, 200, 200))
            screen.blit(lbl_n, (self.x_panel + 40, y_offset + 42))
            screen.blit(lbl_e, (self.x_panel + 180, y_offset + 42))

            lbl_s = self.fuente_texto.render(f"Sur:   {sur} vh", True, (200, 200, 200))
            lbl_o = self.fuente_texto.render(f"Oeste: {omega} vh", True, (200, 200, 200))
            screen.blit(lbl_s, (self.x_panel + 40, y_offset + 62))
            screen.blit(lbl_o, (self.x_panel + 180, y_offset + 62))

            # --- PROCESAMIENTO Y DIBUJO DE CONFIGURACIÓN Y TIEMPOS REALES ---
            # Extraemos la información del diccionario dinámico
            fase_act, tiempo_rest = diccionario_tiempos.get(idx, (0, 0))
            texto_fase_nombre = nombres_fases.get(fase_act, f"Fase {fase_act}")
            
            # Intentar leer los ciclos desde el controlador de tráfico de forma segura
            ciclo_actual = 1
            if hasattr(controlador, 'estados_intersecciones') and idx in controlador.estados_intersecciones:
                info_cruce = controlador.estados_intersecciones[idx]
                # Intenta extraer la variable interna de ciclos; si no existe, genera una basada en la simulación
                if "contador_ciclos" in info_cruce:
                    ciclo_actual = (info_cruce["contador_ciclos"] % 4) + 1
                elif "ciclos" in info_cruce:
                    ciclo_actual = (info_cruce["ciclos"] % 4) + 1
                else:
                    # Alternativa calculada en base al tiempo de ejecución si no se expone la propiedad
                    ciclo_actual = ((pygame.time.get_ticks() // 20000) % 4) + 1
            else:
                ciclo_actual = ((pygame.time.get_ticks() // 20000) % 4) + 1

           #TIEMPOS DE SEMAFOROS EN ANARANJADO ---
            # Por defecto asumimos los 5 segundos base iniciales (5000 ms)
            duracion_ns = 5
            duracion_eo = 5

            # Si el controlador ya inicializó la intersección, leemos sus tiempos calculados reales
            if hasattr(controlador, 'estados_intersecciones') and idx in controlador.estados_intersecciones:
                tiempos_fase = controlador.estados_intersecciones[idx].get("tiempo_verde_fase", {})
                # Convertimos de milisegundos a segundos (ej. 5000ms -> 5s)
                duracion_ns = int(tiempos_fase.get(0, 5000) / 1000)
                duracion_eo = int(tiempos_fase.get(1, 5000) / 1000)

            # Renderizado dinámico: ahora el texto naranja variará según las decisiones del algoritmo
            txt_duracion_base = f"Tiempo: N/S: {duracion_ns}s | E/O: {duracion_eo}s"
            lbl_duracion = self.fuente_texto.render(txt_duracion_base, True, (255, 165, 0))
            screen.blit(lbl_duracion, (self.x_panel + 40, y_offset + 85))
            # Línea Inferior Dinámica: Estado actual del contador de tiempo y Ciclo Activo (1 al 4)
            txt_tiempo_real = f"{texto_fase_nombre} -> {int(max(0, tiempo_rest))}s  [Ciclo {ciclo_actual}/4]"
            color_tiempo = (0, 255, 200) if tiempo_rest > 0 else (130, 130, 130)
            
            lbl_tiempos = self.fuente_bold.render(txt_tiempo_real, True, color_tiempo)
            screen.blit(lbl_tiempos, (self.x_panel + 40, y_offset + 105))
            
            # Aumentamos el salto vertical para separar los nuevos rectángulos más grandes
            y_offset += 140