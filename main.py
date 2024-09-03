from BitDogLib import *
from utime import ticks_us
from sys import exit

HORIZONTAL = 0
VERTICAL = 1

VERDE = [0,2,0]
VERMELHO = [2,0,0]
AZUL = [0,0,2]
BRANCO = [10,10,10]

class Barco:
    def __init__(self, tamanho) -> None:
        self.x = 0
        self.y = 0
        self.orientacao = HORIZONTAL
        self.tamanho = tamanho
        self.colocado = False

    def desenhar(self, matriz):
        b = 0
        x = round(self.x)
        y = round(self.y)
        while b < self.tamanho:
            if self.orientacao == HORIZONTAL:
                ligar_led(x + b, y, VERDE)
                matriz[y][x + b] = 1
            else:
                ligar_led(x, y + b, VERDE)
                matriz[y + b][x] = 1
            b = b + 1
        return matriz

QUANTIDADE_DE_BARCOS = 6
barcos = [Barco(3),
          Barco(3),
          Barco(2),
          Barco(2),
          Barco(1),
          Barco(1)]

def posicionando_barco(novo_barco:Barco, barcos:list[Barco]):
    matriz = desenhar_todos_os_barcos(barcos)
    b = 0
    aceitavel = True
    while b < novo_barco.tamanho:
        if novo_barco.orientacao == HORIZONTAL:
            x = novo_barco.x + b
            y = novo_barco.y
        else:
            x = novo_barco.x
            y = novo_barco.y + b
        x = round(x)
        y = round(y)
        if matriz[y][x] == 1:
            ligar_led(x, y, VERMELHO)
            aceitavel = False
        else:
            ligar_led(x, y, BRANCO)
        b = b + 1
    return aceitavel


def desenhar_todos_os_barcos(barcos:list[Barco]):
    matriz = [[0 for _ in range(5)]for _ in range(5)]
    for barco in barcos:
        if barco.colocado:
            matriz = barco.desenhar(matriz)
    return matriz

def tempo_de_jogo(old):
    new = ticks_us()
    delta = abs(new - old)
    old = new
    return (delta, old)

def fase_posicionamento():
    for barco in barcos:
        old = ticks_us()
        while True:
            delta, old = tempo_de_jogo(old)
            x_end = 1
            y_end = 1
            if botao_A_pressionado():
                if barco.orientacao == VERTICAL:
                    if round(barco.x) + barco.tamanho <= 5:
                        barco.orientacao = HORIZONTAL
                else:
                    if round(barco.y) + barco.tamanho <= 5:
                        barco.orientacao = VERTICAL
    
            if barco.orientacao == VERTICAL:
                y_end = barco.tamanho
            else:
                x_end = barco.tamanho
    
            jx = joystick_x()
            if jx > 0 and barco.x <= 5-x_end:
                barco.x = barco.x + 1/250000*delta
            if jx < 0 and barco.x >= 0:
                barco.x = barco.x - 1/250000*delta
    
            jy = joystick_y()
            if jy > 0 and barco.y <= 5-y_end:
                barco.y = barco.y + 1/250000*delta
            if jy < 0 and barco.y >= 0:
                barco.y = barco.y - 1/250000*delta
    
            apagar_leds()
            pode = posicionando_barco(barco, barcos)
            if botao_B_pressionado() and pode:
                barco.colocado = True
                break
    apagar_leds()

def selecionar_posicao_tiro(matriz_tiros, tiro_x, tiro_y, delta):
    jx = joystick_x()
    jy = joystick_y()
    
    if jx > 0 and tiro_x <= 4:
        tiro_x = tiro_x + 1/250000*delta
    if jx < 0 and tiro_x >= 0:
        tiro_x = tiro_x - 1/250000*delta
        
    
    if jy > 0 and tiro_y <= 4:
        tiro_y = tiro_y  + 1/250000*delta
    if jy < 0 and tiro_y >= 0:
        tiro_y = tiro_y - 1/250000*delta
    
    pode = True
    if matriz_tiros[round(tiro_y)][round(tiro_x)] > 0:
        ligar_led(tiro_x, tiro_y, VERMELHO)
        pode = False
    else:
        ligar_led(tiro_x, tiro_y, BRANCO)
    return tiro_x, tiro_y, pode

def checar_acertou(x, y):
    x = round(x)
    y = round(y)
    #return bluetooth_mandar(x,y)
    matriz_adv = [[1, 1, 1, 0, 0], [0, 0, 0, 1, 0], [1, 1, 0, 1, 0], [1, 0, 0, 1, 0], [0, 0, 0, 1, 1]]
    if matriz_adv[y][x] == 1:
        return True
    else: 
        return False

def desenhar_tiros(matriz_tiros, tiro_x, tiro_y):
    y = 0
    while y < 5:
        x = 0
        while x < 5:
            if x == round(tiro_x) and y == round(tiro_y):
                pass
            elif matriz_tiros[y][x] == 1:
                ligar_led(x,y, VERDE)
            elif matriz_tiros[y][x] == 2:
                ligar_led(x,y,AZUL)
            x = x + 1
        y = y + 1
    
def fase_batalha():
    matriz_tiros = [[0 for _ in range(5)]for _ in range(5)]
    tiro_x = 0
    tiro_y = 0
    old = ticks_us()
    while True:
        apagar_led(tiro_x, tiro_y)
        delta, old = tempo_de_jogo(old)
        tiro_x, tiro_y, pode = selecionar_posicao_tiro(matriz_tiros, tiro_x, tiro_y, delta)
        if botao_B_pressionado() and pode:
            acertou = checar_acertou(tiro_x, tiro_y)
            if acertou:
                matriz_tiros[round(tiro_y)][round(tiro_x)] = 1
            else:
                matriz_tiros[round(tiro_y)][round(tiro_x)] = 2
        desenhar_tiros(matriz_tiros, tiro_x, tiro_y)
        
    
fase_batalha()