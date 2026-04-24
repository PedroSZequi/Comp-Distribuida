import grpc
import os
import file_processor_pb2
import file_processor_pb2_grpc

CHUNK_SIZE = 1024 * 64

def gerar_chunks_pdf(caminho_pdf):
    nome_arquivo = os.path.basename(caminho_pdf)

    with open(caminho_pdf, "rb") as f:
        while True:
            dados = f.read(CHUNK_SIZE)
            if not dados:
                break

            yield file_processor_pb2.FileChunk(
                file_name=nome_arquivo,
                content=dados
            )

def comprimir_pdf(caminho_entrada, caminho_saida):
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = file_processor_pb2_grpc.FileProcessorServiceStub(channel)

        resposta_stream = stub.CompressPDF(gerar_chunks_pdf(caminho_entrada))

        with open(caminho_saida, "wb") as saida:
            sucesso_final = True
            mensagem_final = ""

            for chunk in resposta_stream:
                if not chunk.success:
                    sucesso_final = False
                    mensagem_final = chunk.status_message
                    break

                if chunk.content:
                    saida.write(chunk.content)

        if sucesso_final:
            print(f"PDF comprimido salvo em: {caminho_saida}")
        else:
            print(f"Erro ao comprimir PDF: {mensagem_final}")

if __name__ == "__main__":
    comprimir_pdf("input.pdf", "compressed_output.pdf")
