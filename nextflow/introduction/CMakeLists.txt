# Copyright (c) 2022 Quantum Brilliance Pty Ltd
#
# IMPORTANT: -DCMAKE_INSTALL_PREFIX must be
# provided when invoking this and must point to
# an existing Qristal core installation
###############################################

cmake_minimum_required(VERSION 3.20 FATAL_ERROR)

project(nf_intro_install
  DESCRIPTION "Copy (does not compile) submodules from this directory to the examples location in Qristal"
  LANGUAGES CXX
)

configure_file(${CMAKE_CURRENT_SOURCE_DIR}/vqe/CMakeLists.txt.in
                  ${CMAKE_BINARY_DIR}/configured_example_files/vqe/CMakeLists.txt
                  @ONLY)

install(
    FILES
      ${CMAKE_CURRENT_SOURCE_DIR}/vqe/OptVQEParallelization.cpp
      ${CMAKE_BINARY_DIR}/configured_example_files/vqe/CMakeLists.txt
    DESTINATION ${CMAKE_INSTALL_PREFIX}/examples/cpp/vqe_opt_hpc_app
)
