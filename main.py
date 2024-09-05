from BitDogLib import *
from utime import ticks_us
#Apenas para testes
import _thread

from BitDogLib.led import carinha_feliz

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
                matriz[y][x + b] = 1
            else:
                matriz[y + b][x] = 1
            b = b + 1
        return matriz

class conexao:
    def __init__(self, wlan, conn, is_server) -> None:
        self.wlan = wlan
        self.conn = conn
        self.is_server = is_server
    
conn = conexao(0,0, False)

QUANTIDADE_DE_BARCOS = 6
barcos = [Barco(3),
          Barco(3),
          Barco(2),
          Barco(2),
          Barco(1),
          Barco(1)]

matriz_old = [[0 for _ in range(5)] for _ in range(5)]

def posicionando_barco(novo_barco:Barco, barcos:list[Barco]):
    global matriz_old
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
        if matriz[y][x] == 1:
            matriz[y][x] = 2
            aceitavel = False
        else:
            matriz[y][x] = 4
        b = b + 1
    diff_matriz(matriz_old, matriz)
    matriz_old = copy_matriz(matriz)
    return aceitavel

def criar_matriz_barcos(barcos:list[Barco]):
    matriz = [[0 for _ in range(5)]for _ in range(5)]
    for barco in barcos:
        if barco.colocado:
            matriz = barco.desenhar(matriz)
    return matriz

def desenhar_todos_os_barcos(barcos:list[Barco]):
    matriz = criar_matriz_barcos(barcos)
    desenhar_matriz(matriz)
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
            acertou, acabou = checar_acertou_ganhou(tiro_x, tiro_y)
            old = ticks_us()
            if acertou:
                matriz_tiros[round(tiro_y)][round(tiro_x)] = 1
            else:
                matriz_tiros[round(tiro_y)][round(tiro_x)] = 2
                break
                
            if(acabou):
                break
        desenhar_tiros(matriz_tiros, tiro_x, tiro_y)
    return acabou

def checar_acertou_ganhou(x, y):
    x = round(x)
    y = round(y)
    
    enviar_via_wifi(conn.conn, [x,y])
    dado = esperar_receber()
    acertou = dado[0]
    acabou = dado[1]
    print(acertou)
    if acertou == 0:
        som_explosao()
    elif acertou == 1: 
        som_agua()
    return acertou, acabou

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
            elif matriz[y][x] == 4:
                ligar_led(x,y,BRANCO)
            x = x + 1
        y = y + 1
    
def colorir_led(type, x, y):
    if type == 1:
        ligar_led(x,y, VERDE)
    elif type == 2:
        ligar_led(x,y,VERMELHO)
    elif type == 3:
        ligar_led(x,y,AZUL)
    elif type == 4:
        ligar_led(x,y,BRANCO)
    elif type == 0:
        apagar_led(x,y)
    
def diff_matriz(matriz_old, matriz_new):
    for y,l in enumerate(zip(matriz_old, matriz_new)):
        lo,ln = l
        for x, c in enumerate(zip(lo, ln)):
            co,cn = c
            if co != cn:
                colorir_led(cn, x, y)

def dar_tiro(matriz_tiros):
    old = ticks_us()
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
            if matriz_barcos[y][x] == 1:
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
        apagar_leds()
        desenhar_matriz(matriz_barcos)
        dado = esperar_receber()
        tiro_x = dado[0]
        tiro_y = dado[1]
        if matriz_barcos[tiro_y][tiro_x] == 1:
            acertou = 1
            matriz_barcos[tiro_y][tiro_x] = 2
            som_explosao()
        else:
            matriz_barcos[tiro_y][tiro_x] = 3
            desenhar_matriz(matriz_barcos)
            som_agua()
            
        if checar_perdeu(matriz_barcos):
            acabou = 1
            
        enviar_via_wifi(conn.conn, [acertou, acabou])
        if acertou == 0 or acabou == 1:
            break
        
    return acabou

def atacar(matriz_tiros):
    apagar_leds()
    acabou = dar_tiro(matriz_tiros)
    if acabou:
        limpar_tela()
        escrever_tela("GANHOU",0,0)
        mostrar_tela()
        carinha_feliz(AZUL)
        desligar_wifi(conn.wlan, conn.is_server)
        return True
    return False

def defender(matriz_tiros):
    apagar_leds()
    acabou = receber_tiro(matriz_barcos)
    if acabou:
        limpar_tela()
        escrever_tela("PERDEU",0,0)
        mostrar_tela()
        desligar_wifi(conn.wlan, conn.is_server)
        return True
    return False


def time_A_batalha(matriz_tiros):
    while True:
        acabou = atacar(matriz_tiros)
        if acabou:
            break
        acabou = defender(matriz_tiros)
        if acabou:
            break

def time_B_batalha(matriz_tiros):
    while True:
        acabou = defender(matriz_tiros)
        if acabou:
            break
        acabou = atacar(matriz_tiros)
        if acabou:
            break

def fase_batalha(matriz_barcos):
    matriz_tiros = [[0 for _ in range(5)]for _ in range(5)]
    if conn.is_server:
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
    wlan = iniciar_servidor(ssid, senha, num)
    if wlan == -1:
        reiniciar()
    conn = servidor_conectar()
    return wlan,conn

def iniciar_time_B(ssid, senha, num):
    wlan,conn = cliente_conectar(ssid, senha, num)
    if wlan == -1:
        reiniciar()
    return wlan, conn
    
def fase_busca_inimigo():
    global conn
    time = escolher_lado()
    numero = escolher_grupo()
    limpar_tela()
    escrever_tela("Estabelecendo", 0, 0)
    escrever_tela("Conexao", 0, 10)
    mostrar_tela()
    
    ssid = f'BitDogLab_{numero}'
    senha = f'BitDogLab_{numero}'
    if time == 0:
        wlanA,connA = iniciar_time_A(ssid, senha, numero)
        conn = conexao(wlanA, connA, True)
    elif time == 1:
        wlanB,connB = iniciar_time_B(ssid, senha, numero)
        conn = conexao(wlanB, connB, False)
    else:
        reiniciar()
    _thread.start_new_thread(receber_via_wifi, (conn.conn,))
    limpar_tela()
    escrever_tela("Conexao", 0, 0)
    escrever_tela("Estabelecida", 0, 10)
    mostrar_tela()
    
def mandar_pronto():
    global conn
    
    apagar_leds()
    limpar_tela()
    escrever_tela('Aguardando',0,0)
    escrever_tela('Inimigo',0,10)
    mostrar_tela()
    
    enviar_via_wifi(conn.conn, ['1'])
    esperar_receber()
    
def copy_matriz(matriz):
    return [[j for j in i] for i in matriz]
 
while True:
    fase_busca_inimigo()
    matriz_barcos = fase_posicionamento()
    mandar_pronto()
    fase_batalha(matriz_barcos)
    while valor_botao_A:
        pass
    reiniciar()