import pygame

class InterfazDatos:
    def __init__(self):
        pygame.font.init()
        self.fuente_titulo = pygame.font.SysFont("Courier New", 16, bold=True)
        self.fuente_texto = pygame.font.SysFont("Courier New", 14)
        self.fuente_bold = pygame.font.SysFont("Courier New", 14, bold=True)
        
        # Posición base del panel analítico (Zona lateral derecha)
        self.x_panel = 820
        self.y_panel = 20
        self.ancho_panel = 310

    def dibujar_tabla(self, screen, historial, controlador):
        # 1. Fondo del panel analítico
        pygame.draw.rect(screen, (20, 25, 30), (self.x_panel, self.y_panel, self.ancho_panel, 560))
        pygame.draw.rect(screen, (50, 60, 70), (self.x_panel, self.y_panel, self.ancho_panel, 560), 2)

        # 2. Título del Panel
        titulo = self.fuente_titulo.render("MONITOR DE SEMÁFOROS", True, (0, 255, 255))
        screen.blit(titulo, (self.x_panel + 15, self.y_panel + 15))
        
        subtitulo = self.fuente_texto.render("Análisis de Flujo e Historial", True, (150, 150, 150))
        screen.blit(subtitulo, (self.x_panel + 15, self.y_panel + 35))
        
        pygame.draw.line(screen, (50, 60, 70), (self.x_panel + 15, self.y_panel + 55), (self.x_panel + self.ancho_panel - 15, self.y_panel + 55), 2)

        # 3. Datos del Ciclo Actual
        ciclo_txt = self.fuente_bold.render(f"Cambio de Ciclo: {historial.contador_cambios_fase} / {historial.limite_cambios}", True, (255, 215, 0))
        screen.blit(ciclo_txt, (self.x_panel + 15, self.y_panel + 70))

        #TABLA 1: FLUJO DE VEHÍCULOS POR CALLE (PERIODO ACTUAL)
        y_tabla1 = self.y_panel + 110
        
        # Encabezados de la tabla
        screen.blit(self.fuente_bold.render("Calle", True, (200, 200, 200)), (self.x_panel + 20, y_tabla1))
        screen.blit(self.fuente_bold.render("Autos", True, (200, 200, 200)), (self.x_panel + 120, y_tabla1))
        screen.blit(self.fuente_bold.render("Total Acum.", True, (200, 200, 200)), (self.x_panel + 220, y_tabla1))
        
        pygame.draw.line(screen, (70, 80, 90), (self.x_panel + 15, y_tabla1 + 20), (self.x_panel + self.ancho_panel - 15, y_tabla1 + 20), 1)

        # Filas de datos
        calles = ["NORTE", "SUR", "ESTE", "OESTE"]
        for i, calle in enumerate(calles):
            y_fila = y_tabla1 + 28 + (i * 22)
            
            # Valores desde historial.py
            autos_ciclo = str(historial.vehiculos_por_calle[calle])
            autos_totales = str(historial.historico_total[calle])
            
            screen.blit(self.fuente_texto.render(calle, True, (255, 255, 255)), (self.x_panel + 20, y_fila))
            screen.blit(self.fuente_texto.render(autos_ciclo, True, (100, 255, 100)), (self.x_panel + 140, y_fila))
            screen.blit(self.fuente_texto.render(autos_totales, True, (150, 150, 255)), (self.x_panel + 240, y_fila))
            
        # TABLA 2: TIEMPOS DINÁMICOS ASIGNADOS AL SEMÁFORO
        y_tabla2 = y_tabla1 + 130
        pygame.draw.line(screen, (50, 60, 70), (self.x_panel + 15, y_tabla2), (self.x_panel + self.ancho_panel - 15, y_tabla2), 2)
        
        lbl_tiempos = self.fuente_titulo.render("TIEMPOS OPTIMIZADOS", True, (0, 255, 255))
        screen.blit(lbl_tiempos, (self.x_panel + 15, y_tabla2 + 15))

        # Mostrar los milisegundos calculados pasados a segundos
        t_ns = controlador.tiempo_verde_fase[0] / 1000
        t_eo = controlador.tiempo_verde_fase[1] / 1000

        y_valores = y_tabla2 + 45
        screen.blit(self.fuente_texto.render("Eje Norte/Sur:", True, (255, 255, 255)), (self.x_panel + 20, y_valores))
        screen.blit(self.fuente_bold.render(f"{t_ns} seg", True, (0, 255, 0)), (self.x_panel + 220, y_valores))

        screen.blit(self.fuente_texto.render("Eje Este/Oeste:", True, (255, 255, 255)), (self.x_panel + 20, y_valores + 25))
        screen.blit(self.fuente_bold.render(f"{t_eo} seg", True, (0, 255, 0)), (self.x_panel + 220, y_valores + 25))
        
        # Nota explicativa inferior
        y_nota = y_valores + 70
        pygame.draw.rect(screen, (30, 35, 45), (self.x_panel + 15, y_nota, self.ancho_panel - 30, 70))
        nota_l1 = self.fuente_texto.render("Nota: Los tiempos se recalculan", True, (180, 180, 180))
        nota_l2 = self.fuente_texto.render("de forma inteligente cada 4", True, (180, 180, 180))
        nota_l3 = self.fuente_texto.render("fases completas del ciclo.", True, (180, 180, 180))
        screen.blit(nota_l1, (self.x_panel + 22, y_nota + 8))
        screen.blit(nota_l2, (self.x_panel + 22, y_nota + 26))
        screen.blit(nota_l3, (self.x_panel + 22, y_nota + 44))