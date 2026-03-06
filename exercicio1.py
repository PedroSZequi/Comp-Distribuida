from mpi4py import MPI
import random
import time
import math

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

N = 300

if rank == 0:
    A = [[random.random() for _ in range(N)] for _ in range(N)]
    B = [[random.random() for _ in range(N)] for _ in range(N)]
    inicio = time.time()
else:
    A = None
    B = None
    inicio = None

A = comm.bcast(A, root=0)
B = comm.bcast(B, root=0)

linhas_por_processo = math.ceil(N / size)
inicio_linha = rank * linhas_por_processo
fim_linha = min(inicio_linha + linhas_por_processo, N)

parte_local = []

for i in range(inicio_linha, fim_linha):
    linha_resultado = []
    for j in range(N):
        soma = 0
        for k in range(N):
            soma += A[i][k] * B[k][j]
        linha_resultado.append(soma)
    parte_local.append((i, linha_resultado))

partes = comm.gather(parte_local, root=0)

if rank == 0:
    C = [[0] * N for _ in range(N)]

    for parte_processo in partes:
        for indice_linha, linha in parte_processo:
            C[indice_linha] = linha

    fim = time.time()
    print("Tempo distribuído:", (fim - inicio) * 1000, "ms")