#include <grpcpp/grpcpp.h>
#include <fstream>
#include <iostream>
#include <string>
#include <ctime>
#include <cstdlib>
#include <cstdio>

#include "file_processor.grpc.pb.h"

using grpc::Server;
using grpc::ServerBuilder;
using grpc::ServerContext;
using grpc::ServerReaderWriter;
using grpc::Status;

using file_processor::FileChunk;
using file_processor::ProcessedFileChunk;
using file_processor::FileProcessorService;

class FileProcessorServiceImpl final : public FileProcessorService::Service {
private:
    void Log(const std::string& status, const std::string& service, const std::string& file, const std::string& msg) {
        std::ofstream log("server.log", std::ios::app);

        std::time_t agora = std::time(nullptr);
        char timestamp[100];
        std::strftime(timestamp, sizeof(timestamp), "%Y-%m-%d %H:%M:%S", std::localtime(&agora));

        log << "[" << timestamp << "] "
            << status
            << " - Service: " << service
            << ", File: " << file
            << ", Message: " << msg
            << std::endl;

        std::cout << "[" << timestamp << "] "
                  << status
                  << " - Service: " << service
                  << ", File: " << file
                  << ", Message: " << msg
                  << std::endl;
    }

public:
    Status CompressPDF(
        ServerContext* context,
        ServerReaderWriter<ProcessedFileChunk, FileChunk>* stream
    ) override {
        FileChunk chunk;
        std::string file_name = "input.pdf";
        std::string input_path;
        std::string output_path;

        bool primeiro_chunk = true;
        std::ofstream input_file;

        while (stream->Read(&chunk)) {
            if (primeiro_chunk) {
                file_name = chunk.file_name();

                input_path = "/tmp/input_" + file_name;
                output_path = "/tmp/output_" + file_name;

                input_file.open(input_path, std::ios::binary);

                if (!input_file.is_open()) {
                    ProcessedFileChunk erro;
                    erro.set_success(false);
                    erro.set_status_message("Falha ao criar arquivo temporário.");
                    stream->Write(erro);

                    Log("FAIL", "CompressPDF", file_name, "Falha ao criar arquivo temporário.");
                    return Status::OK;
                }

                primeiro_chunk = false;
            }

            input_file.write(chunk.content().data(), chunk.content().size());
        }

        input_file.close();

        std::string comando =
            "gs -sDEVICE=pdfwrite "
            "-dCompatibilityLevel=1.4 "
            "-dPDFSETTINGS=/ebook "
            "-dNOPAUSE -dQUIET -dBATCH "
            "-sOutputFile=" + output_path + " " + input_path;

        int resultado = std::system(comando.c_str());

        if (resultado != 0) {
            ProcessedFileChunk erro;
            erro.set_success(false);
            erro.set_status_message("Falha ao comprimir PDF com Ghostscript.");
            stream->Write(erro);

            Log("FAIL", "CompressPDF", file_name, "Falha ao comprimir PDF.");
            std::remove(input_path.c_str());
            return Status::OK;
        }

        std::ifstream output_file(output_path, std::ios::binary);

        if (!output_file.is_open()) {
            ProcessedFileChunk erro;
            erro.set_success(false);
            erro.set_status_message("Falha ao abrir PDF comprimido.");
            stream->Write(erro);

            Log("FAIL", "CompressPDF", file_name, "Falha ao abrir PDF comprimido.");
            std::remove(input_path.c_str());
            std::remove(output_path.c_str());
            return Status::OK;
        }

        char buffer[65536];

        while (output_file.read(buffer, sizeof(buffer)) || output_file.gcount() > 0) {
            ProcessedFileChunk resposta;
            resposta.set_file_name("compressed_" + file_name);
            resposta.set_success(true);
            resposta.set_status_message("PDF comprimido com sucesso.");
            resposta.set_content(buffer, output_file.gcount());
            stream->Write(resposta);
        }

        output_file.close();

        Log("SUCCESS", "CompressPDF", file_name, "PDF comprimido com sucesso.");

        std::remove(input_path.c_str());
        std::remove(output_path.c_str());

        return Status::OK;
    }
};

void RunServer() {
    std::string endereco("0.0.0.0:50051");

    FileProcessorServiceImpl service;

    ServerBuilder builder;
    builder.AddListeningPort(endereco, grpc::InsecureServerCredentials());
    builder.RegisterService(&service);

    std::unique_ptr<Server> server(builder.BuildAndStart());

    std::cout << "Servidor gRPC ouvindo em " << endereco << std::endl;

    server->Wait();
}

int main() {
    RunServer();
    return 0;
}
