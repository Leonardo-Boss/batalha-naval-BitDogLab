from machine import Pin, SoftI2C
from ssd1306 import SSD1306_I2C

# Configuração OLED
i2c = SoftI2C(scl=Pin(15), sda=Pin(14))
oled = SSD1306_I2C(128, 64, i2c)

texts = []
old_texts = []

def limpar_tela():
    global texts
    texts = []
    oled.fill(0)

def safe_old_text():
    global old_texts
    old_texts = texts

def load_old_texts():
    limpar_tela()
    for i in old_texts:
        escrever_tela(*i)
    mostrar_tela()

def escrever_tela(texto, x, y):
    global texts
    texts.append((texto, x, y))
    oled.text(texto, x, y)

def mostrar_tela():
    oled.show()
