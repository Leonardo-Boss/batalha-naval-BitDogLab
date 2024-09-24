from machine import Pin, SoftI2C
from ssd1306 import SSD1306_I2C
import framebuf
import utime

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

def explosao_oled():
    '''roda animação de explosão'''
    # ler arquivo explosão
    with open('explosion.pbm', 'rb') as f:
        explosion_pbm = f.read()
    play_pbm(explosion_pbm)

def agua_oled():
    '''roda animação de agua'''
    # ler arquivo agua
    with open('watersplash.pbm', 'rb') as f:
        watersplash_pbm = f.read()
    play_pbm(watersplash_pbm)

def read_until(inp:bytes, start, end_value):
    '''lê um array de bytes até encontrar o valor end_value
    retorna os bytes lidos e a posição depois do valor end_value'''
    i = len(inp)
    for i, byte in enumerate(inp[start:], start):
        if byte == end_value:
            return (inp[start:i],i+1)
    return ('',i)

def play_pbm(inp):
    '''exibe um ou multiplos frames de um arquivo pbm'''
    l = len(inp)
    x = 128 # largura da imagem valor default apenas para o LSP não reclamar
    y = 64 # altura da imagem valor default apenas para o LSP não reclamar
    start = 0 # define de onde começar a ler no arquivo
    linebreak = 10 # valor em byte da quebra de linha
    while start < l:
        # lê a primeira linha do pbm corresponde ao tipo de pbm nesse caso P4
        value, start = read_until(inp, start, linebreak)

        # verificar que imagem está no formato correto
        if value != b'P4':
            print(value)
            raise(Exception('arquivo inválido precisa ser no formato P4'))

        # ler tamanho da imagem
        value, start = read_until(inp, start, linebreak)
        x,y = map(int,value.split())


        # ler imagem
        end = start + x*y//8 # cada bit representa um pixel por isso dividimos pelo valor de bits em um byte para obter a quantidade de bytes até o final da imagem
        buffer = bytearray(inp[start:end]) #
        start = end

        # exibir imagem no display oled
        fb = framebuf.FrameBuffer(buffer, x, y, framebuf.MONO_HLSB)
        oled.fill(0)
        oled.blit(fb, 8, 0)
        oled.show()
        utime.sleep_ms(35)
