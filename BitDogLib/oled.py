from machine import Pin, SoftI2C
from ssd1306 import SSD1306_I2C

# Inicia o I2C, passando os pinos de SCL e SDA
i2c = SoftI2C(scl=Pin(15), sda=Pin(14))
# Captura o oled no I2C
oled = SSD1306_I2C(128, 64, i2c)

# Variavel para armazenar o texto atualmente sendo mostrado
texto_atual = []
# Variavel para armazenar o texto previamente mostrado na tela
texto_antigo = []

# Essa função limpa a tela
def limpar_tela():
    global texto_atual
    texto_atual = []
    oled.fill(0)

# Essa função salva o texto previamente mostrado na tela
def salvar_texto_antigo():
    global texto_antigo
    texto_antigo = texto_atual

# Essa função carrega o texto previamente mostrado na tela na tela novamente
def carregar_texto_antigo():
    limpar_tela()
    for i in texto_antigo:
        escrever_tela(*i)
    mostrar_tela()

# Essa função recebe um texto e uma posição X, Y e escreve seu valor na tela
def escrever_tela(texto, x, y):
    global texto_atual
    texto_atual.append((texto, x, y))
    oled.text(texto, x, y)

# Essa função atualiza a a tela
def mostrar_tela():
    oled.show()
