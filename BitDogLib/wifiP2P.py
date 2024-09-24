import network
import socket
import time
import json
import _thread
from utime import ticks_ms, sleep
from .utils import reiniciar
from .block import block, unblock, blocked
from .led import _carinha_triste, _apagar_leds
from .oled import _limpar_tela, _mostrar_tela, _escrever_tela

fila = []
wlan = network.WLAN()
conn = None
pacote = 0
pacotes_recebidos = []

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
    global pacote
    global fila
    global pacotes_recebidos
    while True:
        print('Esperando dados...')
        data = conn.recv(1024)
        pck = data.decode('utf-8').strip()
        print(f"Recebido: {pck}")
        try:
            pck = json.loads(pck)
            if not pck[0] in pacotes_recebidos:
                fila.append(pck)
                pacotes_recebidos.append(pck[0])
            if pck[2] != 1:
                enviar_ack([pck[0]])
                pacote += 1
        except:
            print(f'Dado Invalido {pck}')
            
def enviar_via_wifi(msg:list):
    global conn
    global pacote
    msg = [pacote, msg, 0]
    pck = f'{json.dumps(msg)}\n'
    pacote_enviado = pacote
    while True:
        conn.send(pck.encode())
        print('Enviado:', pck)
        sleep(1)
        msg_recebida = ler_ack()
        if len(msg_recebida) > 0 and msg_recebida[1][0] == pacote_enviado:
            print('ACK Recebido')
            break
    pacote += 1

def enviar_ack(msg:list):
    global conn
    global pacote
    msg = [pacote, msg, 1]
    pck = f'{json.dumps(msg)}\n'
    conn.send(pck.encode())
    pacote += 1
    print('Enviado ACK:', pck)
    
def ler_wifi() -> list:
    global fila
    if len(fila) > 0:
        return fila.pop(0)
    return []

def ler_ack()->list:
    global fila
    for i,msg in enumerate(fila):
        if msg[2] == 1:
            return fila.pop(i)
    return []
    
def esperar_receber():
    global wlan
    old = ticks_ms()
    while True:
        #print(wlan.status('rssi'))
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
        if len(dado) > 0 and dado[2] != 1:
            return dado[1]
        
def definir_servidor_ou_cliente(grupo:int, is_servidor:bool):
    _limpar_tela()
    _escrever_tela("Estabelecendo", 0, 0)
    _escrever_tela("Conexao", 0, 10)
    _mostrar_tela()
    
    ssid = f'BitDogLab_{grupo}'
    senha = f'BitDogLab_{grupo}'
    
    if is_servidor:
        iniciar_servidor(ssid, senha, grupo)
        servidor_conectar()
        is_server = True
    elif not is_servidor:
        cliente_conectar(ssid, senha, grupo)
    else:
        reiniciar()
    _thread.start_new_thread(receber_via_wifi, ())
    _limpar_tela()
    _escrever_tela("Conexao", 0, 0)
    _escrever_tela("Estabelecida", 0, 10)
    _mostrar_tela()
        
def desligar_wifi():
    wlan.active(False)
    print('Wi-Fi Desligado')
