import network
import socket
import time
import json

fila = []

def iniciar_servidor(ssid:str, senha:str, grupo:int):
    if grupo < 0 or grupo > 255:
        print('grupo inválido')
        return -1
    print('Iniciando Server')
    # Configurar o Pico W como Ponto de Acesso
    wlan = network.WLAN(network.AP_IF)
    wlan.config(essid=ssid, password=senha)
    wlan.active(True)
    wlan.ifconfig((f'{grupo}.200.200.1', '255.255.255.252','0.0.0.0','0.0.0.0'))
    print('Ponto de Acesso Ativo:', wlan.ifconfig())
    return wlan
    
def servidor_conectar():
    
    addr = socket.getaddrinfo('0.0.0.0', 8080)[0][-1]
    server_socket = socket.socket()
    server_socket.bind(addr)
    server_socket.listen(1)
    print('Aguardando conexão...')
    conn, addr = server_socket.accept()
    print('Cliente conectado:', addr)
    return conn

def cliente_conectar(ssid:str, senha:str, grupo:int):
    if grupo < 0 or grupo > 255:
        print('grupo inválido')
        return -1,-1
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
    return wlan, conn

def receber_via_wifi(conn):
    while True:
        print('Esperando dados...')
        data = conn.recv(1024)
        string = data.decode('utf-8').strip()
        try:
            dado = json.loads(string)
            fila.append(dado)
        except:
            print('Dado Invalido')
            
def enviar_via_wifi(conn, msg:list):
    string = json.dumps(msg)
    conn.send(string.encode())
    print('Enviado:', msg)

def ler_wifi() -> list:
    global fila
    if len(fila) > 0:
        return fila.pop(0)
    return []

def esperar_receber():
    while True:
        dado = ler_wifi()
        if len(dado) > 0:
            print(f'Recebido: {dado}')
            return dado 
        
def desligar_wifi(wlan):
    wlan.active(False)
    print('Desligado')