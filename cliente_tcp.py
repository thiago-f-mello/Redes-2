#!/usr/bin/env python3
# Copyright (c) 2025 Rafael Urbanek Laurentino e Thiago Fabricio de Melo
# Todos os direitos reservados.

import os
import socket
import sys
import config as c      # Configurações gerais
import ast              # Para tratar a lista de arquivos no servidor

# ------------------------------------------- Funções -------------------------------------------

# Função de ajuda que imprime os comandos disponíveis
def help():
    print ("----------------------------- Comandos -----------------------------")
    print ("upload - faz upload de um arquivo - uso correto: upload <arquivo>")
    print ("list - lista todos os arquivos mantidos no servidor")
    print ("exit - encerra a execução do programa")
    print ("help - exibe modo de uso e comandos disponíveis")

# Função que realiza o upload de um arquivo para o servidor
def upload(port, id, arqPath):
      # Pega o nome do arquivo, independente do caminho
      arqName = os.path.basename(arqPath)

      # Pega caminho completo caso use ~
      if arqPath[0] == "~":
            arqPath = os.path.expanduser(arqPath)

      # Retorna caso não encontre o arquivo
      if not os.path.exists(arqPath):
            print(arqPath)
            print(f"Arquivo '{arqName}' não encontrado.")
            return
            
      # Cria socket TCP (IPv4 + TCP)
      sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      # Conecta ao servidor
      sockfd.connect((host, port))

      if c.DEBUG: print("[CLIENTE] SERVIDOR CONECTADO")

      # Pega os metadados do arquivo
      metaData = os.stat(arqPath)
      # Constrói a header
      header = (
           f"{id}\n"                      # Id do cliente
           f"upload\n"                    # Operação
           f"{arqName}\n"                 # Nome do arquivo
           f"{metaData.st_size}\n"        # Tamanho do arquivo
           f"{metaData.st_mtime}\n"       # Última modificação do arquivo
           f"{metaData.st_atime}\n"       # Último acesso do arquivo
           f"{metaData.st_mode}\n"        # Permissões do arquivo
           "\n"
      )

      # Envia o "header" para o servidor
      sockfd.sendall(header.encode())

      if c.DEBUG: print("[CLIENTE] HEADER ENVIADA")

      # Espera confirmação do header
      response = sockfd.recv(c.TAM_MAX).decode()
      if response == c.ACK:
           # Lê e envia os bytes do arquivo
            with open(arqPath, "rb") as f:
                  while chunk := f.read(c.TAM_MAX):
                        sockfd.sendall(chunk)

            if c.DEBUG: print("[CLIENTE] ARQUIVO ENVIADO")

            # Recebe resposta do servidor
            response = sockfd.recv(c.TAM_MAX).decode()
            if response == c.ACK:
                  print(f"Envio concluído. Arquivo replicado com sucesso para {c.TAM_REP} servidores réplica.")
            else:      
                  print(f"Erro. Resposta recebida: {response}")
            
            # Fecha o socket
            sockfd.close()  
      else:      
            print(f"Erro. Resposta recebida: {response}")
     
def list(port, id):    
      # Cria socket TCP (IPv4 + TCP)
      sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      # Conecta ao servidor
      sockfd.connect((host, port))
      
      # Constrói header
      header = (
           f"{id}\n"    # Id do cliente
           f"list\n"    # Operação
           "\n"
      )

      # Envia o "header" para o servidor
      sockfd.sendall(header.encode())

      # Recebe lista de arquivos do servidor
      content = sockfd.recv(c.TAM_MAX).decode()
      if content != "[]": 

            # Converte a string "['...']" em uma lista real ['...', '...']
            arqList = ast.literal_eval(content)

            for arq in arqList:
                  print(arq)
      else:
           print("Não há arquivos salvos no servidor")
      
      # Fecha socket 
      sockfd.close()

# ---------------------------------------- Início Main ---------------------------------------

# Verifica o uso correto
if len(sys.argv) != 4:
    print(f"Uso correto: {sys.argv[0]} <id> <host> <porta 'menor que 9000'>")
    sys.exit(1)

clientId = int(sys.argv[1])     # Identificador do cliente
host = sys.argv[2]              # Endereço do servidor
port = int(sys.argv[3])         # Porta do servidor

while True:

    print ("\nPara listar todos os comandos digite 'help'")
    userInput = input("Digite um comando: ")
    
    if not userInput.strip():
        continue
    
    inputList = userInput.split()
    op = inputList[0]
        
    match op:
        case _ if op == c.OPTIONS[0]:
              if len(inputList) != 2 :
                print ("Só é possível fazer upload de 1 arquivo por vez; Uso correto: upload <arquivo>")
                continue
              print (f"Enviando arquivo '{inputList[1]}' ...")
              upload(port, clientId, inputList[1])
        
        case _ if op == c.OPTIONS[1]:
              print("Listando todos arquivos do servidor")
              list(port, clientId)
       
        case _ if op == c.OPTIONS[2]:
              print ("Encerrando execução...")
              break
        
        case _ if op == c.OPTIONS[3]:
              help()
        
        case _:
              print ("Comando desconhecido\n")