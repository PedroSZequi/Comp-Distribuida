from mpi4py import MPI
import random
import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

LINHAS = 1001   # proposital para testar divisão não exata
COLUNAS = 1000

limiar_suspeito = None
limiar_alto = None
percentual_critico = None

imagem = None

if rank == 0:
    print("\nGerando radiografia...\n")

    imagem = [
        [random.randint(0, 255) for _ in range(COLUNAS)]
        for _ in range(LINHAS)
    ]

    limiar_suspeito = 200
    limiar_alto = 230
    percentual_critico = 0.05

    inicio_total = time.time()

LINHAS = comm.bcast(LINHAS, root=0)
COLUNAS = comm.bcast(COLUNAS, root=0)
limiar_suspeito = comm.bcast(limiar_suspeito, root=0)
limiar_alto = comm.bcast(limiar_alto, root=0)
percentual_critico = comm.bcast(percentual_critico, root=0)

comm.Barrier()

partes = None
intervalos = None

if rank == 0:
    tamanho_parte = LINHAS // size
    resto = LINHAS % size

    partes = []
    intervalos = []

    inicio = 0
    for i in range(size):
        extra = 1 if i < resto else 0
        fim = inicio + tamanho_parte + extra

        partes.append(imagem[inicio:fim])
        intervalos.append((inicio, fim - 1))

        inicio = fim

imagem_local = comm.scatter(partes, root=0)
intervalo_local = comm.scatter(intervalos, root=0)

linha_inicio, linha_fim = intervalo_local

total_pixels = 0
soma_intensidade = 0
max_local = 0

suspeitos = 0
altamente_suspeitos = 0

suspeitos_esq = 0
suspeitos_dir = 0

altos_esq = 0
altos_dir = 0

for linha in imagem_local:
    for j, pixel in enumerate(linha):
        total_pixels += 1
        soma_intensidade += pixel

        if pixel > max_local:
            max_local = pixel

        if pixel > limiar_suspeito:
            suspeitos += 1

            if j < COLUNAS // 2:
                suspeitos_esq += 1
            else:
                suspeitos_dir += 1

        if pixel > limiar_alto:
            altamente_suspeitos += 1

            if j < COLUNAS // 2:
                altos_esq += 1
            else:
                altos_dir += 1

media_local = soma_intensidade / total_pixels

percentual_local = suspeitos / total_pixels

if percentual_local < percentual_critico:
    classificacao = "normal"
elif percentual_local < percentual_critico * 2:
    classificacao = "atencao"
else:
    classificacao = "critica"

if rank % 2 == 1:
    time.sleep(1)

comm.Barrier()

total_pixels_global = comm.reduce(total_pixels, op=MPI.SUM, root=0)
soma_global = comm.reduce(soma_intensidade, op=MPI.SUM, root=0)
suspeitos_global = comm.reduce(suspeitos, op=MPI.SUM, root=0)
altos_global = comm.reduce(altamente_suspeitos, op=MPI.SUM, root=0)

suspeitos_esq_global = comm.reduce(suspeitos_esq, op=MPI.SUM, root=0)
suspeitos_dir_global = comm.reduce(suspeitos_dir, op=MPI.SUM, root=0)

altos_esq_global = comm.reduce(altos_esq, op=MPI.SUM, root=0)
altos_dir_global = comm.reduce(altos_dir, op=MPI.SUM, root=0)

max_global = comm.reduce(max_local, op=MPI.MAX, root=0)

relatorio_local = {
    "rank": rank,
    "intervalo_linhas": f"{linha_inicio} a {linha_fim}",
    "linhas": len(imagem_local),
    "pixels": total_pixels,
    "suspeitos": suspeitos,
    "altos": altamente_suspeitos,
    "max": max_local,
    "classificacao": classificacao
}

relatorios = comm.gather(relatorio_local, root=0)

if rank == 0:
    fim_total = time.time()

    media_global = soma_global / total_pixels_global
    percentual_global = suspeitos_global / total_pixels_global

    print("\n===== RELATÓRIO FINAL =====\n")
    print("Tamanho:", LINHAS, "x", COLUNAS)
    print("Processos:", size)
    print("Tempo:", (fim_total - inicio_total)*1000, "ms\n")

    print("Média global:", round(media_global, 2))
    print("Máximo global:", max_global)
    print("Suspeitos:", suspeitos_global)
    print("Altamente suspeitos:", altos_global)
    print("Percentual suspeito:", round(percentual_global*100, 2), "%\n")

    print("Pulmão esquerdo:", suspeitos_esq_global)
    print("Pulmão direito:", suspeitos_dir_global)

    print("Altamente suspeitos esquerdo:", altos_esq_global)
    print("Altamente suspeitos direito:", altos_dir_global)

    lado = "esquerdo" if suspeitos_esq_global > suspeitos_dir_global else "direito"
    print("Mais afetado:", lado)

    print("\n--- Por processo ---")
    for r in relatorios:
        print(r)

    if percentual_global < percentual_critico:
        final = "Sem indícios relevantes"
    elif percentual_global < percentual_critico * 2:
        final = "Atenção clínica"
    else:
        final = "Alta concentração de áreas suspeitas"

    print("\nClassificação final:", final)