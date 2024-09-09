import network
import socket
import time
import json
from utime import ticks_ms, sleep
from .utils import reiniciar
from .block import block, unblock, blocked
from .led import _carinha_triste, _apagar_leds
from .oled import _limpar_tela, _mostrar_tela, _escrever_tela

fila = []
wlan = network.WLAN()
conn = None

def iniciar_servidor(ssid:str, senha:str, grupo:int):
    global wlan
    if grupo < 0 or grupo > 255:
        print('grupo inválido')
        reiniciar()
    print('Iniciando Server')
    # Configurar o Pico W como Ponto de Acesso
    wlan = network.WLAN(network.AP_IF)
    wlan.config(essid=ssid, password=senha)
    wlan.active(True)
    wlan.ifconfig((f'{grupo}.200.200.1', '255.255.255.252','0.0.0.0','0.0.0.0'))
    print('Ponto de Acesso Ativo:', wlan.ifconfig())
    
def servidor_conectar():
    global conn
    addr = socket.getaddrinfo('0.0.0.0', 8080)[0][-1]
    server_socket = socket.socket()
    server_socket.bind(addr)
    server_socket.listen(1)
    print('Aguardando conexão...')
    conn, addr = server_socket.accept()
    print('Cliente conectado:', addr)

def cliente_conectar(ssid:str, senha:str, grupo:int):
    global wlan, conn
    if grupo < 0 or grupo > 255:
        print('grupo inválido')
        reiniciar()
    print('Iniciando Client')
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.ifconfig((f'{grupo}.200.200.2', '255.255.255.252','0.0.0.0','0.0.0.0'))
    print('Cliente Ativo:', wlan.ifconfig())
    wlan.connect(ssid, senha)
    
    # Aguarda conexão ao AP
    while not wlan.isconnected():
        print("Tentando conectar")
        time.sleep(1)

    
    addr = socket.getaddrinfo(f'{grupo}.200.200.1', 8080)[0][-1]  # IP do AP Pico W
    print('Conectado ao AP:', addr)
    conn = socket.socket()
    conn.connect(addr)
    print('Conectado ao AP:', addr)

def receber_via_wifi():
    global conn
    while True:
        print('Esperando dados...')
        data = conn.recv(1024)
        string = data.decode('utf-8').strip()
        try:
            dado = json.loads(string)
            fila.append(dado)
        except:
            print('Dado Invalido')
            
def enviar_via_wifi(msg:list):
    global conn
    string = json.dumps(msg)
    conn.send(string.encode())
    print('Enviado:', msg)

def ler_wifi() -> list:
    global fila
    if len(fila) > 0:
        return fila.pop(0)
    return []

def esperar_receber():
    global wlan
    old = ticks_ms()
    while True:
        new = ticks_ms()
        if new - old >= 2000:
            old = new
            if not wlan.isconnected():
                print(f'Conexão Perdida')
                block()
                _carinha_triste((10,0,0))
                _limpar_tela()
                _escrever_tela('Conexão Perdida', 0, 0)
                _mostrar_tela()
                desligar_wifi()
                sleep(1)
                reiniciar()
                
        dado = ler_wifi()
        if len(dado) > 0:
            print(f'Recebido: {dado}')
            return dado 
        
def desligar_wifi():
    wlan.active(False)
    print('Wi-Fi Desligado')
