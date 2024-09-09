# Importação das Bibliotecas: Importa as bibliotecas Pin e neopixel necessárias para controlar os LEDs.
# lib
from machine import Pin
import neopixel
from utime import ticks_ms
from .block import *

# Número de LEDs na sua matriz 5x5
# lib / aula
ROW_SIZE = 5
COL_SIZE = 5
NUM_LEDS = ROW_SIZE * COL_SIZE

# Inicializar a matriz de NeoPixels no GPIO7
# A Raspberry Pi Pico está conectada à matriz de NeoPixels no pino GPIO7

# lib
# mapeia os indicies em uma matriz para utilização mais intuitiva
LED_MAP = [[i for i in range(j*COL_SIZE+COL_SIZE-1,j*COL_SIZE-1, -1)]
    if j % 2 == 0
    else [i for i in range(j*COL_SIZE, j*COL_SIZE+COL_SIZE)]
    for j in range(0,ROW_SIZE)]

# cria uma matriz inicial que vai guardar o estado anterior da matriz
omatrix = [[[0,0,0] for _ in range(COL_SIZE)] for _ in range(ROW_SIZE)]

# inicializa a conexão com a matriz de leds
np = neopixel.NeoPixel(Pin(7), NUM_LEDS)
block_lib = False

def criar_matriz():
    '''retorna uma matriz apagada do tamanho da matriz de leds'''
    return [[[0,0,0] for _ in range(COL_SIZE)] for _ in range(ROW_SIZE)]

def copiar_matriz(matriz):
    '''faz uma cópia de uma matriz de duas dimensões'''
    return [[j for j in i] for i in matriz]

def ligar_matriz(matriz):
    '''liga a matriz passada'''
    blocked()
    _ligar_matriz(matriz)

def _ligar_matriz(matriz):
    global omatrix
    mudou = False
    for y,linha in enumerate(zip(omatrix, matriz)):
        linha_velha, linha_nova = linha
        for x, coluna in enumerate(zip(linha_velha, linha_nova)):
            coluna_velha,coluna_nova = coluna
            # verifica se o led mudou para evitar mudar desnecessariamente o que causa piscação
            if coluna_velha != coluna_nova:
                mudou = True
                indice = LED_MAP[y][x]
                valor = coluna_nova
                omatrix[y][x] = valor
                np[indice] = valor
    if mudou:
        np.write()

def ligar_led(x, y, cor):
    '''liga um led na posição e cor especificada'''
    blocked()
    _ligar_led(x, y, cor)

def _ligar_led(x, y, cor):
    global omatrix
    x = round(x)
    y = round(y)
    if 0 > x >= ROW_SIZE:
        print("Índice x fora do intervalo. Por favor, escolha um índice de 0 a", NUM_LEDS - 1)
        return
    if 0 > y >= COL_SIZE:
        print("Índice x fora do intervalo. Por favor, escolha um índice de 0 a", NUM_LEDS - 1)
        return

    omatrix[y][x] = cor
    indice = LED_MAP[y][x]
    # Verifica se o índice está dentro do intervalo permitido
    np[indice] = cor  # Define a cor do LED específico
    np.write()  # Atualiza a matriz de LEDs para aplicar a mudança

def carinha_feliz(cor):
    '''carinha feliz :)'''
    blocked()
    _carinha_feliz(cor)

def _carinha_feliz(cor):
    apagar_leds()
    np[LED_MAP[3][1]] = cor
    np[LED_MAP[3][3]] = cor
    np[LED_MAP[1][0]] = cor
    np[LED_MAP[1][4]] = cor
    np[LED_MAP[0][1]] = cor
    np[LED_MAP[0][3]] = cor
    np[LED_MAP[0][2]] = cor
    np.write()
    
def carinha_triste(cor):
    '''carinha triste :)'''
    blocked()
    _carinha_triste(cor)

def _carinha_triste(cor):
    apagar_leds()
    np[LED_MAP[3][1]] = cor
    np[LED_MAP[3][3]] = cor
    np[LED_MAP[0][0]] = cor
    np[LED_MAP[0][4]] = cor
    np[LED_MAP[1][1]] = cor
    np[LED_MAP[1][3]] = cor
    np[LED_MAP[1][2]] = cor
    np.write()

def apagar_led(x, y):
    '''apaga um led na posição especificada'''
    blocked()
    _apagar_led(x, y)

def _apagar_led(x, y):
    global omatrix
    x = round(x)
    y = round(y)

    if 0 > x  and x >= ROW_SIZE:
        print("Índice x fora do intervalo. Por favor, escolha um índice de 0 a", NUM_LEDS - 1)
        return
    if 0 > y and y >= COL_SIZE:
        print("Índice x fora do intervalo. Por favor, escolha um índice de 0 a", NUM_LEDS - 1)
        return

    off = [0,0,0]
    omatrix[y][x] = off
    indice = LED_MAP[y][x]
    np[indice] = off  # Define a cor do LED específico
    np.write()  # Atualiza a matriz de LEDs para aplicar a mudança

def apagar_leds():
    '''apaga todos os leds'''
    blocked()
    _apagar_leds()

def _apagar_leds():
    i = 0
    while i < 5:
        j = 0
        while j < 5:
            off = [0,0,0]
            omatrix[j][i] = off
            indice = LED_MAP[j][i]
            np[indice] = off
            j = j + 1
        i = i + 1
    np.write()
