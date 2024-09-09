import sys

from BitDogLib import *
from utime import ticks_us
from time import sleep
#Apenas para testes
import _thread
import json

from BitDogLib.led import carinha_feliz, copiar_matriz

HORIZONTAL = 0
VERTICAL = 1

VERDE = [0,10,0]
VERMELHO = [10,0,0]
AZUL = [0,0,10]
BRANCO = [10,10,10]
APAGADO = [0,0,0]

is_server = False
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
                matriz[y][x + b] = VERDE
            else:
                matriz[y + b][x] = VERDE
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
    matriz = criar_matriz_barcos(barcos)
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
        if matriz[y][x] == VERDE:
            matriz[y][x] = VERMELHO
            aceitavel = False
        else:
            matriz[y][x] = BRANCO
        b = b + 1
    ligar_matriz(matriz)
    return aceitavel

def criar_matriz_barcos(barcos:list[Barco]):
    matriz = criar_matriz()
    for barco in barcos:
        if barco.colocado:
            matriz = barco.desenhar(matriz)
    return matriz

def desenhar_todos_os_barcos(barcos:list[Barco]):
    matriz = criar_matriz_barcos(barcos)
    ligar_matriz(matriz)
    return matriz

def tempo_de_jogo(old):
    new = ticks_us()
    delta = abs(new - old)
    old = new
    return (delta, old)

def fase_posicionamento():
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

            pode = posicionando_barco(barco, barcos)
            if botao_B_pressionado() and pode:
                barco.colocado = True
                break
        barcos_restantes = barcos_restantes - 1
    matriz = desenhar_todos_os_barcos(barcos)
    return matriz

def selecionar_posicao_tiro(matriz_tiros):
    old = ticks_us()
    tiro_x = 2
    tiro_y = 2
    while True:
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
        if matriz_tiros[round(tiro_y)][round(tiro_x)] != APAGADO:
            cor_ponteiro = VERMELHO
            pode = False
        else:
            cor_ponteiro = BRANCO

        if botao_B_pressionado() and pode:
            acertou, acabou = checar_acertou_ganhou(tiro_x, tiro_y)
            old = ticks_us()
            if acertou:
                matriz_tiros[round(tiro_y)][round(tiro_x)] = VERDE
            else:
                matriz_tiros[round(tiro_y)][round(tiro_x)] = AZUL
                break
                
            if(acabou):
                break
        desenhar_tiros(matriz_tiros, tiro_x, tiro_y, cor_ponteiro)
    return acabou

def checar_acertou_ganhou(x, y):
    x = round(x)
    y = round(y)
    
    enviar_via_wifi([x,y])
    dado = esperar_receber()
    acertou = dado[0]
    acabou = dado[1]
    if acertou == 0:
        som_agua()
    elif acertou == 1: 
        som_explosao()
    return acertou, acabou

def desenhar_tiros(matriz_tiros, tiro_x, tiro_y, cor_ponteiro):
    matriz = copiar_matriz(matriz_tiros)
    matriz[round(tiro_y)][round(tiro_x)] = cor_ponteiro
    ligar_matriz(matriz)

def dar_tiro(matriz_tiros):
    ganhou = False
    limpar_tela()
    escrever_tela("FASE DE ATAQUE", 0, 0)
    mostrar_tela()
    ganhou = selecionar_posicao_tiro(matriz_tiros)
    return ganhou

def checar_perdeu(matriz_barcos):
    y = 0
    while y < 5:
        x = 0
        while x < 5:
            if matriz_barcos[y][x] == VERDE:
                return False
            x = x + 1
        y = y + 1
        
    return True
    
def receber_tiro(matriz_barcos):
    acertou = 0
    acabou = 0
    limpar_tela()
    escrever_tela("FASE DE DEFESA", 0, 0)
    mostrar_tela()
    while True:
        acertou = 0
        ligar_matriz(matriz_barcos)
        dado = esperar_receber()
        tiro_x = dado[0]
        tiro_y = dado[1]
        if matriz_barcos[tiro_y][tiro_x] == VERDE:
            acertou = 1
            matriz_barcos[tiro_y][tiro_x] = VERMELHO
            som_explosao()
        else:
            matriz_barcos[tiro_y][tiro_x] = AZUL
            ligar_matriz(matriz_barcos)
            som_agua()
            
        if checar_perdeu(matriz_barcos):
            acabou = 1
            
        enviar_via_wifi([acertou, acabou])
        if acertou == 0 or acabou == 1:
            break
        
    return acabou

def atacar(matriz_tiros):
    acabou = dar_tiro(matriz_tiros)
    if acabou:
        limpar_tela()
        escrever_tela("GANHOU",0,0)
        mostrar_tela()
        carinha_feliz(AZUL)
        return True
    return False

def defender():
    acabou = receber_tiro(matriz_barcos)
    if acabou:
        limpar_tela()
        escrever_tela("PERDEU",0,0)
        mostrar_tela()
        carinha_triste(VERMELHO)
        return True
    return False


def time_A_batalha(matriz_tiros):
    while True:
        acabou = atacar(matriz_tiros)
        if acabou:
            break
        acabou = defender()
        if acabou:
            break

def time_B_batalha(matriz_tiros):
    while True:
        acabou = defender()
        if acabou:
            break
        acabou = atacar(matriz_tiros)
        if acabou:
            break

def fase_batalha():
    matriz_tiros = criar_matriz()
    if is_server:
        time_A_batalha(matriz_tiros)
    else:
        time_B_batalha(matriz_tiros)
        
def escolher_lado():
    limpar_tela()
    escrever_tela("Escolha seu lado", 0, 0)
    escrever_tela("A<-Time A", 0, 10)
    escrever_tela("Time B->B", 0, 20)
    mostrar_tela()
    
    while True:
        if botao_A_pressionado():
            return 0
        if botao_B_pressionado():
            return 1

def escolher_grupo():

    old = ticks_us()
    numero = 0
    while True:
        
        limpar_tela()
        escrever_tela("Escolha o grupo", 0, 0)
        escrever_tela(str(round(numero)), 0, 10)
        escrever_tela("A para confirmar", 0, 20)
        mostrar_tela()
        
        if botao_A_pressionado():
            return round(numero)
            
        delta,old = tempo_de_jogo(old)
        jx = joystick_x()
        if jx > 0 and numero <= 255:
            numero = numero + 1/250000*delta
        if jx < 0 and numero >= 0:
            numero = numero - 1/250000*delta


def iniciar_time_A(ssid, senha, num):
    iniciar_servidor(ssid, senha, num)
    servidor_conectar()

def iniciar_time_B(ssid, senha, num):
    cliente_conectar(ssid, senha, num)
    
def fase_busca_inimigo():
    global is_server
    time = escolher_lado()
    numero = escolher_grupo()
    limpar_tela()
    escrever_tela("Estabelecendo", 0, 0)
    escrever_tela("Conexao", 0, 10)
    mostrar_tela()
    
    ssid = f'BitDogLab_{numero}'
    senha = f'BitDogLab_{numero}'
    if time == 0:
        iniciar_time_A(ssid, senha, numero)
        is_server = True
    elif time == 1:
        iniciar_time_B(ssid, senha, numero)
    else:
        reiniciar()
    _thread.start_new_thread(receber_via_wifi, ())
    limpar_tela()
    escrever_tela("Conexao", 0, 0)
    escrever_tela("Estabelecida", 0, 10)
    mostrar_tela()
    
def mandar_pronto():
    apagar_leds()
    limpar_tela()
    escrever_tela('Aguardando',0,0)
    escrever_tela('Inimigo',0,10)
    mostrar_tela()
    
    enviar_via_wifi([1])
    esperar_receber()

desligar_wifi()
fase_busca_inimigo()
matriz_barcos = fase_posicionamento()
mandar_pronto()
fase_batalha()
sleep(2)
desligar_wifi()
limpar_tela()
escrever_tela('Reinicie',0,0)
escrever_tela('para jogar',0,20)
escrever_tela('novamente',0,30)
mostrar_tela()
apagar_leds()
