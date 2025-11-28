#!/usr/bin/env python3
# ***************************************************************
# 
# Nome do arquivo: cliente_tcp.py
#
# Descrição: Cliente TCP simples.
#            Envia uma mensagem e recebe de volta.
#
# Autor: Giovanni Venâncio
# Data: 29/10/2025
#
# Execução:
#     python3 cliente_tcp.py <host> <porta>
#
# Exemplo:
#     python3 cliente_tcp.py 127.0.1.1 8500
#
# ***************************************************************

import os
import socket
import sys

options = ["upload", "list", "exit", "help"]    # Opções disponíveis para o usuário
TAM_MAX = 1024                                  # Tamanho máximo da mensagem

# Verifica uso correto
if len(sys.argv) != 4:
    print(f"Uso correto: {sys.argv[0]} <id> <host> <porta>")
    sys.exit(1)

clientId = int(sys.argv[1])     # Identificador do cliente
host = sys.argv[2]              # Endereço do servidor
port = int(sys.argv[3])         # Porta do servidor

def help():
    print ("---------------------------------------- Comandos ----------------------------------------")
    print ("upload - faz upload de um arquivo - uso correto: upload <arquivo>")
    print ("list - lista todos os arquivos mantidos no servidor")
    print ("exit - encerra a execução do programa")
    print ("help - exibe modo de uso e comandos disponíveis\n")

# Realiza upload de um arquivo para o servidor
def upload(port, id, arq):
      
      # Cria socket TCP (IPv4 + TCP)
      sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

      # Conecta ao servidor
      sockfd.connect((host, port))

      # Retorna caso não encontre o arquivo
      if not os.path.exists(arq):
            print(f"[CLIENTE] Arquivo '{arq}' não encontrado.")
            return

      # Pega informações do arquivo
      metaData = os.stat(arq)
      header = (
           f"{id}\n"
           f"upload\n"
           f"{arq}\n"
           f"{metaData.st_size}\n"
           f"{metaData.st_mtime}\n"
           f"{metaData.st_atime}\n"
           f"{metaData.st_mode}\n"
           "\n"
      )

      # Envia o "header" textual para o servidor
      sockfd.sendall(header.encode())

      # Lê e envia bytes do arquivo
      with open(arq, "rb") as f:
            while chunk := f.read(TAM_MAX):
                  sockfd.sendall(chunk)

      print("[CLIENTE] Arquivo enviado.")

      # Recebe resposta do servidor
      resposta = sockfd.recv(TAM_MAX).decode()
      print(f"[CLIENTE] Resposta recebida: {resposta}")

      sockfd.close()
     
def list_files(port, id):    
      # Cria socket TCP (IPv4 + TCP)
      sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

      # Conecta ao servidor
      sockfd.connect((host, port))
      
      # header inicial
      header = (
           f"{id}\n"
           f"list\n"
           "\n"
      )

      # Envia mensagem para o servidor
      sockfd.send(header.encode())

      # Recebe resposta do servidor
      content = sockfd.recv(TAM_MAX).decode()
      print(f"{content}")

      sockfd.close()


while True:

    print ("Para listar todos os comandos digite 'help'")
    userInput = input("Digite um comando: ")
    
    if not userInput.strip():
        continue
    
    inputList = userInput.split()
    op = inputList[0]
        
    match op:
        case _ if op == options[0]:
              if len(inputList) != 2 :
                print ("Só é possível fazer upload de 1 arquivo por vez; Uso correto: upload <arquivo>\n")
                continue
              print (f"Fazendo upload do arquivo {inputList[1]}\n")
              upload(port, clientId, inputList[1])
        
        case _ if op == options[1]:
              print("Listando todos arquivos do servidor\n")
              list_files(port, clientId)
       
        case _ if op == options[2]:
              print ("Encerrando execução...")
              break
        
        case _ if op == options[3]:
              help()
        
        case _:
              print ("Comando desconhecido\n")