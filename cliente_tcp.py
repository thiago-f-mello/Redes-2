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
porta = int(sys.argv[3])        # Porta do servidor

def help():
    print ("---------------------------------------- Comandos ----------------------------------------")
    print ("upload - faz upload de um arquivo - uso correto: upload <arquivo>")
    print ("list - lista todos os arquivos mantidos no servidor")
    print ("exit - encerra a execução do programa")
    print ("help - exibe modo de uso e comandos disponíveis\n")

def initConnection(id, host, porta):
      # Cria socket TCP (IPv4 + TCP)
      sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

      # Conecta ao servidor
      sockfd.connect((host, porta))

      return sockfd

# Realiza upload de arquivo para o servidor
def upload(skt, id, host, porta, arq):
      # Pega informações do arquivo
      info = os.stat(arq)
      buffer = f"{id}\n{arq}\n{info.st_size}\n{info.st_mtime}\n{info.st_ctime}\n"

      # Envia o "header" textual para o servidor
      skt.sendall(buffer.encode())

      # Lê e envia bytes do arquivo
      with open(arq, "rb") as f:
            while True:
                  # Lê próximo bloco do arquivo
                  buffer = f.read(TAM_MAX)

                  # Se não há mais dados, encerra o envio
                  if not buffer:
                        break
                  
                  # Envia bloco lido
                  skt.sendall(buffer)

      print("[CLIENTE] Arquivo enviado.")

      # Recebe resposta do servidor
      resposta = skt.recv(TAM_MAX).decode()

      print(f"[CLIENTE] Resposta recebida: {resposta}")
     
     

def list(skt,id, host, porta):
     # Conecta ao servidor
     skt.connect((host, porta))

     # Lê mensagem do usuário
     buffer = "listar"

     # Envia mensagem para o servidor
     skt.send(buffer.encode())

     # Recebe resposta do servidor
     resposta = skt.recv(TAM_MAX).decode()

     print(f"[CLIENTE] Resposta recebida: {resposta}")

def exit(skt):
     print()
     # Fecha socket
     skt.close()

skt = initConnection(clientId, host, porta)

while(True):

    print ("Para listar todos os comandos digite 'help'")
    userInput = input("Digite um comando: ")
    inputList = userInput.split()
    op = inputList[0]
        
    match op:
        case _ if op == options[0]:
              if len(inputList) != 2 :
                print ("Só é possível fazer upload de 1 arquivo por vez; Uso correto: upload <arquivo>\n")
                continue
              print (f"Fazendo upload do arquivo {inputList[1]}\n")
              upload(skt, clientId, host, porta, inputList[1])
        case _ if op == options[1]:
              print("Listando todos arquivos do servidor\n")
              list(skt, clientId, host, porta)
        case _ if op == options[2]:
              print ("Encerrando execução\n")
              exit(skt)
              break
        case _ if op == options[3]:
              help()
        case _:
              print ("Comando não encontrado\n")