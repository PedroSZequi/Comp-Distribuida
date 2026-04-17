import grpc
from concurrent import futures
import notas_pb2
import notas_pb2_grpc

# Banco em memória
db_notas = {}
# Exemplo de chave: "123_CIC0001"

class GerenciadorNotasServicer(notas_pb2_grpc.GerenciadorNotasServicer):
    def AdicionarNota(self, request, context):
        print(f"Adicionando nota para RA {request.ra} na disciplina {request.cod_disciplina}")

        chave = f"{request.ra}_{request.cod_disciplina}"

        if chave in db_notas:
            return notas_pb2.StatusResponse(
                sucesso=False,
                msg="Nota já existe para este aluno/disciplina. Use AlterarNota."
            )

        nova_nota = notas_pb2.Nota(
            ra=request.ra,
            cod_disciplina=request.cod_disciplina,
            ano=request.ano,
            semestre=request.semestre,
            nota=request.nota
        )

        db_notas[chave] = nova_nota

        return notas_pb2.StatusResponse(
            sucesso=True,
            msg="Nota adicionada com sucesso!"
        )

    def AlterarNota(self, request, context):
        print(f"Alterando nota para RA {request.ra} na disciplina {request.cod_disciplina}")

        chave = f"{request.ra}_{request.cod_disciplina}"

        if chave not in db_notas:
            return notas_pb2.StatusResponse(
                sucesso=False,
                msg="Nota não encontrada para este aluno/disciplina."
            )

        nota_alterada = notas_pb2.Nota(
            ra=request.ra,
            cod_disciplina=request.cod_disciplina,
            ano=request.ano,
            semestre=request.semestre,
            nota=request.nota
        )

        db_notas[chave] = nota_alterada

        return notas_pb2.StatusResponse(
            sucesso=True,
            msg="Nota alterada com sucesso!"
        )

    def ConsultarNota(self, request, context):
        print(f"Consultando nota para RA {request.ra} na disciplina {request.cod_disciplina}")

        chave = f"{request.ra}_{request.cod_disciplina}"

        if chave not in db_notas:
            return notas_pb2.ConsultaNotaResponse(
                sucesso=False,
                msg_erro="Nota não encontrada."
            )

        return notas_pb2.ConsultaNotaResponse(
            sucesso=True,
            nota=db_notas[chave]
        )

    def CalcularMedia(self, request, context):
        print(f"Calculando média do aluno {request.ra}")

        notas_aluno = []

        for nota in db_notas.values():
            if nota.ra == request.ra:
                notas_aluno.append(nota.nota)

        if not notas_aluno:
            return notas_pb2.MediaResponse(
                sucesso=False,
                msg_erro="Aluno não possui notas cadastradas."
            )

        media = sum(notas_aluno) / len(notas_aluno)

        return notas_pb2.MediaResponse(
            sucesso=True,
            media=media
        )

    def ListarNotasAluno(self, request, context):
        print(f"Listando notas para o RA {request.ra}")

        encontrou = False

        for nota in db_notas.values():
            if nota.ra == request.ra:
                encontrou = True
                yield nota

        if not encontrou:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Aluno não possui notas cadastradas.")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    notas_pb2_grpc.add_GerenciadorNotasServicer_to_server(
        GerenciadorNotasServicer(),
        server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Servidor gRPC rodando na porta 50051.")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
