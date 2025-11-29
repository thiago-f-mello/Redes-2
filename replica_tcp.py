#!/usr/bin/env python3
# Copyright (c) 2025 Rafael Urbanek Laurentino e Thiago Fabricio de Melo
# Todos os direitos reservados.

import os
import socket
import sys
import config as c

# ------------------------------------------- Funções -------------------------------------------

# Função para criar o socket para se conectar com o Servidor principal
def createReplicaSocket(port):
    
    # Cria socket TCP (IPv4 + TCP)
    sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Associa o socket a todas as interfaces locais
    sockfd.bind(('', port))

    return sockfd

# Função para criar o diretório do cliente na réplica
def createClientDirectory(id, dirPath):
    clientPath = ("./" + dirPath + "/" + id + "/")

    if not os.path.isdir(clientPath):
        try:
            os.mkdir(clientPath)
            if c.DEBUG: print(f"[RÉPLICA {replicaId}] Diretório '{clientPath}' criado com sucesso!")
        except Exception as ex:
            if c.DEBUG: print(f"[RÉPLICA {replicaId}] Erro: ", ex)
    
    return clientPath

def saveFile(skt, header, dirPath):
    # Pegando os dados da header
    clientId = header[0]
    arqName = header[2]
    arqSize = int(header[3])
    arqmtime = header[4]
    arqatime = header[5]
    arqMode = header[6]
    
    # Cria o diretório do cliente se não existir e prepara o caminho
    arqPath = (createClientDirectory(clientId, dirPath) + arqName)
    
    # Recebe o arquivo em si
    with open(arqPath, "wb") as f:
        readBytes = 0

        # Enviando confirmaçao do header e liberação dos dados
        skt.send(c.ACK.encode())

        # Recebe o arquivo em partes
        while readBytes < arqSize:
            # Recebe próximo bloco do arquivo
            buffer = skt.recv(c.TAM_MAX)
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

    if c.DEBUG: print(f"[RÉPLICA {replicaId}] Arquivo '{arqName}' recebido. Armazenamento local concluído.")

    # Envia a mesma mensagem de confirmação
    if c.DEBUG: print(f"[RÉPLICA {replicaId}] Enviando confirmação ao cliente.")
    skt.send(c.ACK.encode())

    # Fecha a conexão com o cliente
    skt.close()
    if c.DEBUG: print(f"[RÉPLICA {replicaId}] Conexão encerrada.\n")

# -------------------------------------- Início do Main --------------------------------------

# Verifica uso correto
if len(sys.argv) < 2:
    print(f"Uso correto: {sys.argv[0]} <porta 'maior que 8999'>")
    sys.exit(1)
# Porta do Servidor/Réplica, converte para int
replicaPort = int(sys.argv[1])
# Valida a porta
if replicaPort < 9000:
    print(f"Erro: porta deve ser maior que 8999 (recebido {replicaPort}).")
    sys.exit(1)

# Id da réplica é o último digito da porta
replicaId = sys.argv[1][-1] 
# Prepara o path da réplica
dirPath = c.DIRNAME_REP + "_" + replicaId

# Cria o diretório da réplica se não existir
if not os.path.isdir(dirPath):
    try:
        os.mkdir(dirPath)
        if c.DEBUG: print(f"[RÉPLICA {replicaId}] Diretório '{dirPath}' criado com sucesso!")
    except Exception as ex:
        if c.DEBUG: print(f"[RÉPLICA {replicaId}] Erro: ", ex) 

# Cria o socket para se comunicar com o Servidor
replicaSocket = createReplicaSocket(replicaPort)
# Coloca o socket em modo de escuta
replicaSocket.listen(c.TAM_FILA)
if c.DEBUG: print(f"[RÉPLICA {replicaId}] Aguardando conexões...")

# Loop principal: aceita conexões do servidor
while True:
    # Aceita a conexão
    auxSocket, client_addr = replicaSocket.accept()
    # Recebe as informações do arquivo (IMPLEMENTAR PARA HEADERS QUE SEJAM MAIORES QUE O TAM_MAX)
    header = (auxSocket.recv(c.TAM_MAX).decode()).split("\n")

    # Processa o "header" recebido
    clientId = header[0]
    operation = header[1]

    if c.DEBUG: print(f"[RÉPLICA {replicaId}] Conexão com o Servidor estabelecida.")
    if c.DEBUG: print(f"[RÉPLICA {replicaId}] Endereço: {client_addr}")
    if c.DEBUG: print(f"[RÉPLICA {replicaId}] Operação solicitada: {operation}")

    match operation.lower():
        case "replicate":
              saveFile(auxSocket, header, dirPath)

        case _:
              print (f"[RÉPLICA {replicaId}] Comando desconhecido\n")