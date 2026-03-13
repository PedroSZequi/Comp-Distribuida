from mpi4py import MPI
import random
import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

N = 10000000

pontos_por_processo = N // size
dentro_local = 0

inicio = None
if rank == 0:
    inicio = time.time()

for _ in range(pontos_por_processo):
    x = random.random()
    y = random.random()
    if x*x + y*y <= 1:
        dentro_local += 1

total_dentro = comm.reduce(dentro_local, op=MPI.SUM, root=0)

if rank == 0:
    total_pontos = pontos_por_processo * size
    pi = 4 * total_dentro / total_pontos
    fim = time.time()

    print("PI aproximado:", pi)
    print("Tempo:", (fim - inicio) * 1000, "ms")