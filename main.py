from BitDogLib import *
from BitDogLib.buttons import valor_botao_A
from utime import ticks_us
from sys import exit
#Apenas para testes
from time import sleep
import machine

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
    matriz = [[0 for _ in range(5)]for _ in range(5)]
    barcos_restantes = 6
    for barco in barcos:
        limpar_tela()
        escrever_tela("FASE DE ", 0, 0)
        escrever_tela("POSICIONAMENTO", 0, 10)
        escrever_tela(f'{barcos_restantes} navios', 0, 20)
        escrever_tela('Restantes', 0, 30)
        mostrar_tela()
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
        barcos_restantes = barcos_restantes - 1
    matriz = desenhar_todos_os_barcos(barcos)
    return matriz

def selecionar_posicao_tiro(matriz_tiros, tiro_x, tiro_y):
    old = ticks_us()
    while True:
        apagar_led(tiro_x, tiro_y)
        delta, old = tempo_de_jogo(old)
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
        
        if botao_B_pressionado() and pode:
            acertou, ganhou = checar_acertou_ganhou(tiro_x, tiro_y)
            if(ganhou):
                break
            else:
                if acertou:
                    matriz_tiros[round(tiro_y)][round(tiro_x)] = 1
                else:
                    matriz_tiros[round(tiro_y)][round(tiro_x)] = 2
                    break
        desenhar_tiros(matriz_tiros, tiro_x, tiro_y)
    return ganhou

def checar_acertou_ganhou(x, y):
    x = round(x)
    y = round(y)
    #return bluetooth_mandar(x,y)
    matriz_adv = [[1, 1, 1, 0, 0], [0, 0, 0, 1, 0], [1, 1, 0, 1, 0], [1, 0, 0, 1, 0], [0, 0, 0, 1, 1]]
    if matriz_adv[y][x] == 1:
        return True, True
    else: 
        return False, False
    ########################################

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

def desenhar_matriz(matriz):
    y = 0
    while y < 5:
        x = 0
        while x < 5:
            if matriz[y][x] == 1:
                ligar_led(x,y, VERDE)
            elif matriz[y][x] == 2:
                ligar_led(x,y,VERMELHO)
            elif matriz[y][x] == 3:
                ligar_led(x,y,AZUL)
            x = x + 1
        y = y + 1

def dar_tiro(matriz_tiros, tiro_x, tiro_y):
    old = ticks_us()
    ganhou = False
    limpar_tela()
    escrever_tela("FASE DE ATAQUE", 0, 0)
    mostrar_tela()
    ganhou = selecionar_posicao_tiro(matriz_tiros, tiro_x, tiro_y)
    return ganhou

def checar_perdeu(matriz_barcos):
    y = 0
    while y < 5:
        x = 0
        while x < 5:
            if matriz_barcos[y][x] == 1:
                return False
            x = x + 1
        y = y + 1
        
    return True
    
def receber_tiro(matriz_barcos):
    acertou = False
    ganhou = False
    limpar_tela()
    escrever_tela("FASE DE DEFESA", 0, 0)
    mostrar_tela()
    while True:
        apagar_leds()
        desenhar_matriz(matriz_barcos)
        #tiro_x,tiro_y = receber_bt()
        sleep(2)
        tiro_x = numero_aleatorio(0,4)
        tiro_y = numero_aleatorio(0,4)
        ##########################
        if matriz_barcos[tiro_y][tiro_x] == 1:
            acertou = True
            matriz_barcos[tiro_y][tiro_x] = 2
        else:
            matriz_barcos[tiro_y][tiro_x] = 3
            desenhar_matriz(matriz_barcos)
            sleep(1)
            break
        if checar_perdeu(matriz_barcos):
            perdeu = True
        #enviar_bt(acertou,ganhou)
    return acertou, ganhou
        
def fase_batalha(matriz_barcos):
    matriz_tiros = [[0 for _ in range(5)]for _ in range(5)]
    tiro_x = 0
    tiro_y = 0
    while True:
        apagar_leds()
        ganhou = dar_tiro(matriz_tiros, tiro_x, tiro_y)
        if ganhou:
            limpar_tela()
            escrever_tela("GANHOU",0,0)
            mostrar_tela()
            #fechar_conexao
            break
        apagar_leds()
        acertou,perdeu = receber_tiro(matriz_barcos)
        if perdeu:
            limpar_tela()
            escrever_tela("PERDEU",0,0)
            mostrar_tela()
            #fechar_conexao
            break
        
while True:    
    matriz_barcos = fase_posicionamento()
    # matriz_barcos = [[1, 1, 1, 0, 0], [0, 0, 0, 1, 0], [1, 1, 0, 1, 0], [1, 0, 0, 1, 0], [0, 0, 0, 1, 1]]
    fase_batalha(matriz_barcos)
    while valor_botao_A():
        machine.reset()
