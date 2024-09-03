from utime import ticks_us
import random


def ler_arquivo(nome):
    try:
        with open(nome, 'r') as f:
            mensagem = int(f.read())
    except:
       mensagem  = ''
    return mensagem

def escrever_arquivo(nome, mensagem):
    with open(nome, 'w') as f:
        f.write(mensagem)

def numero_aleatorio(numero1, numero2):
    return random.randint(numero1, numero2)

def tempo_de_jogo(old):
    new = ticks_us()
    delta = abs(new - old)
    old = new
    return (delta, old)

def loop(func):
    old = ticks_us()
    while True:
        delta, old = tempo_de_jogo(old)
        func(delta)
