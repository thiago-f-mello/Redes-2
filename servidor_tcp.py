#!/usr/bin/env python3
#
# ***************************************************************
# 
# Nome do arquivo: servidor_tcp.py
#
# Descrição: Servidor TCP simples iterativo.
#            Recebe mensagens e envia de volta.
#
# Autor: Giovanni Venâncio
# Data: 29/10/2025
#
# Execução:
#     python3 servidor_tcp.py <porta>
#
# Exemplo:
#     python3 servidor_tcp.py 8500
#
# ***************************************************************
import os
import socket
import sys
import json

TAM_MAX = 1024          # Tamanho máximo do buffer de dados
TAM_FILA = 5            # Tamanho da fila de conexões/Clientes
DEBUG = False           # Flag para as informações de DEBUG
TAM_REP = 3             # Quantidade de Réplicas
DIRNAME = "Server"      # Nome do diretório do servidor
DEFAULT_PORT = 9000     # Porta padrão para as réplicas
ACK = "ok"              # ACK para confirmação de recebimento

# Função para criar os sockets para se conectar com as N réplicas
def createReplicasSockets(port):
    
    replicasPorts = [DEFAULT_PORT + i for i in range(1, TAM_REP + 1)]
    replicasSockets = []

    # Cria os sockets
    for port in replicasPorts:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", port))
        replicasSockets.append(sock)

# Função para criar o socket para se conectar com o cliente
def createClientSocket(port):
    
    # Cria socket TCP (IPv4 + TCP)
    sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Associa o socket a todas as interfaces locais
    sockfd.bind(('', port))

    return sockfd

# Função para criar o diretório do cliente no servidor local
def createClientDirectory(id):
    clientPath = ("./" + DIRNAME + "/" + id + "/")

    if not os.path.isdir(clientPath):
        try:
            os.mkdir(clientPath)
            if DEBUG: print(f"Diretório '{clientPath}' criado com sucesso!")
        except Exception as ex:
            if DEBUG: print("Erro: ", ex)
    
    return clientPath

# Função que faz o upload do arquivo e chama a função de replicação
def uploadFile(skt, header):
    clientId = header[0]
    arqName = header[2]
    arqSize = int(header[3])
    arqmtime = header[4]
    arqatime = header[5]
    arqMode = header[6]
    
    # Prepara o caminho do arquivo
    arqPath = (createClientDirectory(clientId) + arqName)
    
    # Recebe o arquivo em si
    with open(arqPath, "wb") as f:
        readBytes = 0

        # Recebe o arquivo em partes
        while readBytes < arqSize:
            # Recebe próximo bloco do arquivo
            buffer = skt.recv(TAM_MAX)
            # Se não há mais dados, encerra o recebimento
            if not buffer:
                break
            # Escreve os bytes recebidos no arquivo
            f.write(buffer)
            # Atualiza a quantidade total de bytes lidos
            readBytes += len(buffer)
    
    # Aplica permissões
    os.chmod(arqPath, int(arqMode))
    # Aplica timestamps (acesso e modificação)
    os.utime(arqPath, (float(arqatime), float(arqmtime)))

    print(f"Arquivo '{arqName}' recebido. Armazenamento local concluído.")
    
    # Envia a mesma mensagem de confirmação
    print("Replicação concluída com sucesso. Enviando confirmação ao cliente.")
    skt.send(ACK.encode())

    # Fecha a conexão com o cliente
    skt.close()
    if DEBUG: print("[SERVIDOR] Conexão encerrada.\n")

# Função para listar os arquivos do cliente
def listFiles(skt, id):
    
    # Prepara o caminho do diretório do cliente
    arqPath = createClientDirectory(id)
    content = os.listdir(arqPath)

    skt.send(str(content).encode())
    
    # Fecha a conexão com o cliente
    skt.close()
    if DEBUG: print("[SERVIDOR] Conexão encerrada.\n")



# -------------------------------------- Início do Main --------------------------------------

# Verifica uso correto, com passagem para debug
# Sem argumentos suficientes
if len(sys.argv) < 2:
    print(f"Uso correto: {sys.argv[0]} <porta 'menor que 9000'>")
    sys.exit(1)
# Verifica se é modo debug
if len(sys.argv) == 3 and sys.argv[2].lower() == "debug":
    DEBUG = True
# Porta do servidor/Cliente, converte para int
clientPort = int(sys.argv[1])
# Valida a porta
if clientPort >= 9000:
    print(f"Erro: porta deve ser menor que 9000 (recebido {clientPort}).")
    sys.exit(1)

# Cria o diretório do servidor principal se não existir
if not os.path.isdir(DIRNAME):
    try:
        os.mkdir(DIRNAME)
        if DEBUG: print(f"Diretório '{DIRNAME}' criado com sucesso!")
    except Exception as ex:
        if DEBUG: print("Erro: ", ex) 

# Cria o socket para se comunicar com o cliente
clientSocket = createClientSocket(clientPort)
# Coloca o socket em modo de escuta
clientSocket.listen(TAM_FILA)
if DEBUG: print("[SERVIDOR] Aguardando conexões...")

# Loop principal: aceita conexões iterativamente
while True:
    # Aceita a conexão
    auxSocket, client_addr = clientSocket.accept()
    # Recebe as informações do arquivo (IMPLEMENTAR PARA HEADERS QUE SEJAM MAIORES QUE O TAM_MAX)
    header = (auxSocket.recv(TAM_MAX).decode()).split("\n")

    # Processa o "header" recebido
    clientId = header[0]
    operation = header[1]

    print(f"[SERVIDOR] Conexão com cliente [{clientId}] estabelecida")
    if DEBUG: print(f"Endereço: {client_addr}")
    print(f"Operação solicitada: {operation}")

    match operation.lower():
        case "upload":
              uploadFile(auxSocket, header)
        
        case "list":
              listFiles(auxSocket, clientId)

        case _:
              print ("Comando desconhecido\n")