from utime import ticks_us
from machine import reset
from .block import blocked
import random
from .led import apagar_leds


def ler_arquivo(nome):
    blocked()
    return _ler_arquivo(nome)

def _ler_arquivo(nome):
    try:
        with open(nome, 'r') as f:
            mensagem = int(f.read())
    except:
       mensagem  = ''
    return mensagem

def escrever_arquivo(nome, mensagem):
    blocked()
    _escrever_arquivo(nome, mensagem)

def _escrever_arquivo(nome, mensagem):
    with open(nome, 'w') as f:
        f.write(mensagem)

def numero_aleatorio(numero1, numero2):
    blocked()
    return _numero_aleatorio(numero1, numero2)

def _numero_aleatorio(numero1, numero2):
    return random.randint(numero1, numero2)

def tempo_de_jogo(old):
    blocked()
    return _tempo_de_jogo(old)

def _tempo_de_jogo(old):
    new = ticks_us()
    delta = abs(new - old)
    old = new
    return (delta, old)

def loop(func):
    old = ticks_us()
    while True:
        delta, old = tempo_de_jogo(old)
        func(delta)

def reiniciar():
    blocked()
    _reiniciar()

def _reiniciar():
    apagar_leds()
    reset()
