class Sensores:
    def __init__(self):
        self.autos = 0
        self.peaton = False
        self.emergencia = False

    def actualizar(self, eventos):
        for event in eventos:
            if event.type == 2:  # KEYDOWN
                if event.key == 49:  # tecla '1' = más autos
                    self.autos += 1
                elif event.key == 50:  # tecla '2' = peatón
                    self.peaton = True
                elif event.key == 51:  # tecla '3' = emergencia
                    self.emergencia = True
