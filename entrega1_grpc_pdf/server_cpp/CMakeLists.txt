cmake_minimum_required(VERSION 3.10)
project(file_processor_server CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Protobuf REQUIRED)
find_package(gRPC REQUIRED)

add_executable(server
    server.cpp
    file_processor.pb.cc
    file_processor.grpc.pb.cc
)

target_link_libraries(server
    gRPC::grpc++
    protobuf::libprotobuf
)

target_include_directories(server PRIVATE .)
