import grpc
import notas_pb2
import notas_pb2_grpc

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = notas_pb2_grpc.GerenciadorNotasStub(channel)

        print("\n--- Adicionando notas ---")
        response1 = stub.AdicionarNota(
            notas_pb2.AdicionaNotaRequest(
                ra="123",
                cod_disciplina="CIC0001",
                ano=2025,
                semestre=2,
                nota=9.5
            )
        )
        print(f"Resposta do servidor: {response1.msg}")

        response2 = stub.AdicionarNota(
            notas_pb2.AdicionaNotaRequest(
                ra="123",
                cod_disciplina="CIC0002",
                ano=2025,
                semestre=2,
                nota=8.0
            )
        )
        print(f"Resposta do servidor: {response2.msg}")

        response3 = stub.AdicionarNota(
            notas_pb2.AdicionaNotaRequest(
                ra="123",
                cod_disciplina="CIC0003",
                ano=2025,
                semestre=2,
                nota=7.5
            )
        )
        print(f"Resposta do servidor: {response3.msg}")

        print("\n--- Consultando nota ---")
        consulta = stub.ConsultarNota(
            notas_pb2.AlunoDisciplinaRequest(
                ra="123",
                cod_disciplina="CIC0001"
            )
        )

        if consulta.sucesso:
            print(
                f"Nota encontrada: RA={consulta.nota.ra}, "
                f"Disciplina={consulta.nota.cod_disciplina}, "
                f"Nota={consulta.nota.nota}"
            )
        else:
            print(f"Erro na consulta: {consulta.msg_erro}")

        print("\n--- Calculando média ---")
        media_response = stub.CalcularMedia(
            notas_pb2.AlunoRequest(ra="123")
        )

        if media_response.sucesso:
            print(f"Média do aluno 123: {media_response.media}")
        else:
            print(f"Erro ao calcular média: {media_response.msg_erro}")

        print("\n--- Listando todas as notas do aluno 123 (STREAMING) ---")
        try:
            notas_stream = stub.ListarNotasAluno(
                notas_pb2.AlunoRequest(ra="123")
            )
            for nota in notas_stream:
                print(
                    f" - Disciplina: {nota.cod_disciplina}, "
                    f"Ano: {nota.ano}, "
                    f"Semestre: {nota.semestre}, "
                    f"Nota: {nota.nota}"
                )
        except grpc.RpcError as e:
            print(f"Erro ao chamar ListarNotasAluno: {e.details()}")

if __name__ == '__main__':
    run()
