#!/usr/bin/env python3
# Copyright (c) 2025 Rafael Urbanek Laurentino e Thiago Fabricio de Melo
# Todos os direitos reservados.

import os
import socket
import sys
import config as c

# ------------------------------------------- Funções -------------------------------------------

# Cria as portas das réplicas
def createReplicasPorts():
    replicasPorts = [c.DEFAULT_PORT + i for i in range(c.TAM_REP)]
    return replicasPorts

# Função para criar os sockets para se conectar com as N réplicas
def createReplicasSockets():
    
    replicasPorts = createReplicasPorts()
    replicasSockets = []

    # Cria os sockets
    for port in replicasPorts:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        replicasSockets.append(sock)
    
    return replicasSockets

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
    clientPath = ("./" + c.DIRNAME + "/" + id + "/")

    if not os.path.isdir(clientPath):
        try:
            os.mkdir(clientPath)
            if c.DEBUG: print(f"Diretório '{clientPath}' criado com sucesso!")
        except Exception as ex:
            if c.DEBUG: print("Erro: ", ex)
    
    return clientPath

def replicateFile(clientId, arqPath):
    # Pega o nome do arquivo, independente do caminho
    arqName = os.path.basename(arqPath)
    
    # Cria os sockets para se comunicar com as N réplicas
    sockets = createReplicasSockets()
    ports = createReplicasPorts()

    # Pega os metadados do arquivo
    metaData = os.stat(arqPath)
    # Constrói a header
    header = (
        f"{clientId}\n"                # Id do cliente
        f"replicate\n"                 # Operação
        f"{arqName}\n"                 # Nome do arquivo
        f"{metaData.st_size}\n"        # Tamanho do arquivo
        f"{metaData.st_mtime}\n"       # Última modificação do arquivo
        f"{metaData.st_atime}\n"       # Último acesso do arquivo
        f"{metaData.st_mode}\n"        # Permissões do arquivo
        "\n"
    )
    
    # Lê e envia os bytes do arquivo
    with open(arqPath, "rb") as f:
        print("Iniciando processo de replicação...")
        # Envia sequencialmente para todas as réplicas
        i = 1
        for sock in sockets:
            # Retorna para o início do arquivo
            f.seek(0)

            # Conecta com a réplica
            sock.connect((c.HOST_REP,ports[i-1]))
            if c.DEBUG: print(f"[SERVIDOR] RÉPLICA {i} CONECTADA")

            # Envia o "header" para o servidor
            sock.sendall(header.encode())
            if c.DEBUG: print(f"[SERVIDOR] HEADER ENVIADA PARA A RÉPLICA {i}")

            # Espera confirmação do header
            response = sock.recv(c.TAM_MAX).decode()
            if response == c.ACK:
                # Envia o arquivo
                while chunk := f.read(c.TAM_MAX):
                    sock.sendall(chunk)

                if c.DEBUG: print(f"[SERVIDOR] ARQUIVO ENVIADO PARA A RÉPLICA {i}")
                
                # Recebe resposta do servidor
                response = sock.recv(c.TAM_MAX).decode()
                if response == c.ACK:
                    print(f"[Réplica {i}] OK")
                else:      
                    print(f"Erro. Resposta recebida: {response}")

                # Deconecta
                sock.close()
                i += 1
            else:      
                  print(f"Erro. Resposta recebida: {response}")
                                       
# Função que faz o upload do arquivo e chama a função de replicação
def uploadFile(skt, header):
    # Pegando os dados da header
    clientId = header[0]
    arqName = header[2]
    arqSize = int(header[3])
    arqmtime = header[4]
    arqatime = header[5]
    arqMode = header[6]
    
    # Cria o diretório do cliente se não existir e prepara o caminho
    arqPath = (createClientDirectory(clientId) + arqName)
    
    # Recebe o arquivo em si
    with open(arqPath, "wb") as f:
        readBytes = 0

        # Enviando confirmaçao do header e liberação dos dados
        skt.sendall(c.ACK.encode())

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

    print(f"Arquivo '{arqName}' recebido. Armazenamento local concluído.")
    
    # Inicia o processo de réplica
    replicateFile(clientId, arqPath)

    # Envia a mesma mensagem de confirmação
    print("Replicação concluída com sucesso. Enviando confirmação ao cliente.")
    skt.sendall(c.ACK.encode())

    # Fecha a conexão com o cliente
    skt.close()
    if c.DEBUG: print("[SERVIDOR] Conexão encerrada.\n")

# Função para listar os arquivos do cliente
def listFiles(skt, id):
    
    # Prepara o caminho do diretório do cliente
    arqPath = createClientDirectory(id)
    content = os.listdir(arqPath)

    skt.sendall(str(content).encode())
    
    # Fecha a conexão com o cliente
    skt.close()
    if c.DEBUG: print("[SERVIDOR] Conexão encerrada.\n")

# -------------------------------------- Início do Main --------------------------------------

# Verifica uso correto, com passagem para debug
# Sem argumentos suficientes
if len(sys.argv) < 2:
    print(f"Uso correto: {sys.argv[0]} <porta 'menor que 9000'>")
    sys.exit(1)
# Verifica se é modo debug
if len(sys.argv) == 3 and sys.argv[2].lower() == "debug":
    c.DEBUG = True
# Porta do servidor/Cliente, converte para int
clientPort = int(sys.argv[1])
# Valida a porta
if clientPort >= 9000:
    print(f"Erro: porta deve ser menor que 9000 (recebido {clientPort}).")
    sys.exit(1)

# Cria o diretório do servidor principal se não existir
if not os.path.isdir(c.DIRNAME):
    try:
        os.mkdir(c.DIRNAME)
        if c.DEBUG: print(f"[SEVIDOR] Diretório '{c.DIRNAME}' criado com sucesso!")
    except Exception as ex:
        if c.DEBUG: print("[SERVIDOR] Erro: ", ex) 

# Cria o socket para se comunicar com o cliente
clientSocket = createClientSocket(clientPort)
# Coloca o socket em modo de escuta
clientSocket.listen(c.TAM_FILA)
if c.DEBUG: print("[SERVIDOR] Aguardando conexões...")

# Loop principal: aceita conexões iterativamente
while True:
    # Aceita a conexão
    auxSocket, client_addr = clientSocket.accept()
    # Recebe as informações do arquivo
    header = (auxSocket.recv(c.TAM_MAX).decode()).split("\n")

    # Processa o "header" recebido
    clientId = header[0]
    operation = header[1]

    print(f"Conexão com cliente [{clientId}] estabelecida.")
    if c.DEBUG: print(f"Endereço: {client_addr}")
    print(f"Operação solicitada: {operation}")

    match operation.lower():
        case "upload":
              uploadFile(auxSocket, header)
        
        case "list":
              listFiles(auxSocket, clientId)

        case _:
              print ("Comando desconhecido\n")