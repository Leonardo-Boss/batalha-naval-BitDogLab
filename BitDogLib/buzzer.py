from machine import Pin, PWM
import time
from .block import blocked

buzzer = PWM(Pin(21))

def som_morreu():
    blocked()
    _som_morreu()

def _som_morreu():
    # Sequência de notas
    melody = [200, 50]
    
    # Ritmo para cada nota
    tempo = [50, 50, 50, 50]  # tempo em milissegundos
    
    # Reprodução das notas
    for i in range(len(melody)):
        buzzer.freq(melody[i])
        buzzer.duty_u16(20000)
        time.sleep(tempo[i] / 1000)
        buzzer.duty_u16(0)
        time.sleep(10 / 1000)  # pausa breve entre as notas


def som_explosao():
    blocked()
    _som_explosao()

def _som_explosao():
    explosion_tones = [100, 150, 200, 250, 300, 200, 100]  # Frequencies to simulate explosion

    for tone in explosion_tones:
        buzzer.freq(tone)
        buzzer.duty_u16(32768)  # Set the duty cycle to 50%
        time.sleep(0.1)  # pausa breve entre as notas

    buzzer.deinit()  # Turn off the buzzer

def som_agua():
    blocked()
    _som_agua()

def _som_agua():
    tones = [800, 600, 400, 300, 200, 100, 50]

    for tone in tones:
        buzzer.freq(tone)
        buzzer.duty_u16(32768)  # Set the duty cycle to 50%
        time.sleep(0.05)  # pausa breve entre as notas

    buzzer.deinit()  # Turn off the buzzer
