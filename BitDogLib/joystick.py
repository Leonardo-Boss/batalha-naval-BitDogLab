from machine import Pin, ADC
from .block import blocked

xAxis = ADC(Pin(27))
yAxis = ADC(Pin(26))
button = Pin(22,Pin.IN, Pin.PULL_UP)

def joystick_x():
    blocked()
    return _joystick_x()

def _joystick_x():
    xValue = xAxis.read_u16()
    if xValue <= 600:
        return 1
    elif xValue >= 60000:
        return -1
    return 0

def joystick_y():
    blocked()
    return _joystick_y()

def _joystick_y():
    yValue = yAxis.read_u16()
    if yValue <= 600:
        return -1
    elif yValue >= 60000:
        return 1
    return 0

def valor_botao_joystick():
    blocked()
    return _valor_botao_joystick()

def _valor_botao_joystick():
    return button.value()

button_pressed = 1
def botao_joystick_pressionado():
    blocked()
    return _botao_joystick_pressionado()

def _botao_joystick_pressionado():
    global button_pressed
    r = False
    a = valor_botao_joystick()
    if a == 0 and button_pressed != a:
        r = True
    button_pressed = a
    return r

button_released = 1
def botao_joystick_solto():
    blocked()
    return _botao_joystick_solto()

def _botao_joystick_solto():
    global button_released
    r = False
    a = valor_botao_joystick()
    if a == 1 and button_released != a:
        r = True
    button_released = a
    return r
