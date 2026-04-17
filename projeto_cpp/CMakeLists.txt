cmake_minimum_required(VERSION 3.10)
project(grpc_calculator_cpp CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Protobuf REQUIRED)
find_package(gRPC REQUIRED)

set(PROTO_OUTPUT_PB_CC ${CMAKE_CURRENT_BINARY_DIR}/calculator.pb.cc)
set(PROTO_OUTPUT_GRPC_CC ${CMAKE_CURRENT_BINARY_DIR}/calculator.grpc.pb.cc)
set(PROTO_OUTPUT_PB_H ${CMAKE_CURRENT_BINARY_DIR}/calculator.pb.h)
set(PROTO_OUTPUT_GRPC_H ${CMAKE_CURRENT_BINARY_DIR}/calculator.grpc.pb.h)

set(PROTO_SOURCE ${CMAKE_CURRENT_SOURCE_DIR}/calculator.proto)

add_custom_command(
  OUTPUT ${PROTO_OUTPUT_PB_CC} ${PROTO_OUTPUT_GRPC_CC} ${PROTO_OUTPUT_PB_H} ${PROTO_OUTPUT_GRPC_H}
  COMMAND ${Protobuf_PROTOC_EXECUTABLE}
  --cpp_out=${CMAKE_CURRENT_BINARY_DIR}
  --grpc_out=${CMAKE_CURRENT_BINARY_DIR}
  -I${CMAKE_CURRENT_SOURCE_DIR}
  ${PROTO_SOURCE}
  DEPENDS ${PROTO_SOURCE}
  COMMENT "Gerando stubs C++ do Protobuf/gRPC para calculator.proto"
)

add_custom_target(generate_proto ALL DEPENDS ${PROTO_OUTPUT_PB_CC} ${PROTO_OUTPUT_GRPC_CC})

add_executable(servidor_cpp servidor_cpp.cpp ${PROTO_OUTPUT_PB_CC} ${PROTO_OUTPUT_GRPC_CC})
add_dependencies(servidor_cpp generate_proto)
target_link_libraries(servidor_cpp gRPC::grpc++ protobuf::libprotobuf)
target_include_directories(servidor_cpp PRIVATE ${CMAKE_CURRENT_BINARY_DIR})

add_executable(cliente_cpp cliente_cpp.cpp ${PROTO_OUTPUT_PB_CC} ${PROTO_OUTPUT_GRPC_CC})
add_dependencies(cliente_cpp generate_proto)
target_link_libraries(cliente_cpp gRPC::grpc++ protobuf::libprotobuf)
target_include_directories(cliente_cpp PRIVATE ${CMAKE_CURRENT_BINARY_DIR})
