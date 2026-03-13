from mpi4py import MPI
import random

# Inicialização do MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# -----------------------------
# Função para gerar logs
# -----------------------------
def gerar_logs(qtd):
    ips = [f"192.168.1.{i}" for i in range(1, 255)]
    endpoints = [
        "/",
        "/login",
        "/products",
        "/cart",
        "/checkout",
        "/api/users",
        "/api/orders"
    ]
    metodos = ["GET", "POST"]
    status = ["200", "200", "200", "404", "500"]

    logs = []

    for _ in range(qtd):
        ip = random.choice(ips)
        metodo = random.choice(metodos)
        endpoint = random.choice(endpoints)
        codigo = random.choice(status)
        linha = f"{ip} {metodo} {endpoint} {codigo}"
        logs.append(linha)

    return logs

# -----------------------------
# Processo 0 gera o dataset
# -----------------------------
logs_divididos = None
TOTAL_LOGS = 100000

if rank == 0:
    print("\nGerando dataset de logs...\n")
    logs = gerar_logs(TOTAL_LOGS)

    tamanho_parte = TOTAL_LOGS // size
    logs_divididos = []

    for i in range(size):
        inicio = i * tamanho_parte
        fim = inicio + tamanho_parte
        logs_divididos.append(logs[inicio:fim])

# -----------------------------
# Distribuição usando Scatter
# -----------------------------
logs_locais = comm.scatter(logs_divididos, root=0)

# -----------------------------
# Processamento local
# -----------------------------
erros = 0

for linha in logs_locais:
    partes = linha.split()
    status_code = partes[3]

    if status_code == "404" or status_code == "500":
        erros += 1

# -----------------------------
# Resultado local
# -----------------------------
print(
    f"Processo {rank} analisou {len(logs_locais)} linhas "
    f"e encontrou {erros} erros."
)