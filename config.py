# Copyright (c) 2025 Rafael Urbanek Laurentino e Thiago Fabricio de Melo
# Todos os direitos reservados.

# --------------------------------- Arquivo de configurações ---------------------------------

# ------ GERAIS ------
ACK = "ok"              # ACK para confirmação de recebimento de mensagem
DEBUG = False           # Flag para as informações de DEBUG
TAM_MAX = 1024          # Tamanho máximo do buffer de dados do socket

# ------ CLIENTE ------
OPTIONS = ["upload", "list", "exit", "help"]    # Opções disponíveis na interface do usuário

# ------ SERVIDOR ------
TAM_FILA = 5            # Tamanho da fila de conexões/Clientes
TAM_REP = 3             # Quantidade de Réplicas (funciona para N réplicas)
DIRNAME = "server"      # Nome do diretório do servidor
DEFAULT_PORT = 9000     # Porta padrão para as réplicas
HOST_REP = "127.0.1.1"  # Host das réplicas (localhost)

# ------ RÉPLICA ------
DIRNAME_REP = "replica" # Nome do diretório das Réplicas