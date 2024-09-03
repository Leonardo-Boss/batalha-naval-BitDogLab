from BitDogLib import *

HORIZONTAL = 0
VERTICAL = 1

VERDE = [0,1,0]



BARCO_X = 0
BARCO_Y = 1
BARCO_ORIENTACAO = 2
BARCO_TAMANHO = 3
# barco = [x, y, orientacao, tamanho]
barcos = [[0, 0, HORIZONTAL, 3],
          [0, 0, HORIZONTAL, 3],
          [0, 0, HORIZONTAL, 2],
          [0, 0, HORIZONTAL, 2],
          [0, 0, HORIZONTAL, 1],
          [0, 0, HORIZONTAL, 1]]
barcos[0][BARCO_X]

class Barco:
    def __init__(self, tamanho) -> None:
        self.x = 0
        self.y = 0
        self.orientacao = HORIZONTAL
        self.tamanho = tamanho

    def desenhar(self):
        b = 0
        while b < self.tamanho:
            if self.orientacao == HORIZONTAL:
                ligar_led(self.x + b, self.y, VERDE)
            else:
                ligar_led(self.x, self.y + b, VERDE)
            b = b + 1

QUANTIDADE_DE_BARCOS = 6
barcos = [3,
          3,
          2,
          2,
          1,
          1]

matriz = []
i = 0
while i < 5:
    j = 0
    linha = []
    while j < 5:
        linha.append(0)
        j = j + 1
    matriz.append(linha)
    i = i + 1

def desenhar_barco(x, y, tamanho, orientacao):
    global matriz
    b = 0
    while b < tamanho:
        if orientacao == HORIZONTAL:
            matriz[y][x + b] = 1
        else:
            matriz[y + b][x] = 1
        b = b + 1

barco = 0
while barco < QUANTIDADE_DE_BARCOS:
    x = 0
    y = 0
    orientacao = HORIZONTAL
    barcos[0]
    barco = barco + 1
while True:
    if botao_A_pressionado():
        if barcos[0].orientacao == VERTICAL:
            nova_orientacao = HORIZONTAL
        else:
            nova_orientacao = VERTICAL
        barcos[0].orientacao = nova_orientacao
        apagar_leds()
        barcos[0].desenhar()
