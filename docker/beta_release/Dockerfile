FROM ubuntu:22.04

# API token to access Gitlab repos
ARG GITLAB_PRIVATE_TOKEN

ENV DEBIAN_FRONTEND noninteractive
ENV GITLAB_PRIVATE_TOKEN $GITLAB_PRIVATE_TOKEN

RUN apt update --fix-missing && TZ=Etc/UTC apt install -y tzdata

# Install deps
RUN apt install -y \
    build-essential \
    cmake \ 
    gfortran \
    git \
    libboost-all-dev \
    libcurl4-openssl-dev  \
    libeigen3-dev \
    libopenblas-dev \
    libpython3-dev \
    libunwind-dev \
    python3 \
    python3-pip 

RUN python3 -m pip install \
    amazon-braket-sdk \
    boto3 cirq==1.0.0 \
    conan \
    flask \
    ipopo \
    openfermion \
    openfermionpyscf \
    pyQuirk \
    pyscf \
    qiskit \
    qsimcirq==0.14.0 \
    scikit-quant

ENV PATH $PATH:$HOME/.local/bin

# Set up an alias to GitLab set that we don't need to authenticate interactively
RUN git config --global url.https://gitlab-token:$GITLAB_PRIVATE_TOKEN@gitlab.com/.insteadOf https://gitlab.com

# Root SDK directory:
# - /source sub-directory contains source code
# - /install sub-directory contains all install resources
ARG SDK_ROOT_DIR=$HOME/SDK
RUN mkdir -p $SDK_ROOT_DIR

# QB SDK build
RUN cd $SDK_ROOT_DIR && \
    git clone https://gitlab.com/qbau/software-and-apps/QBSDK source && \
    cd source && \
    # Disable all warnings
    sed  -i '49i add_definitions(-w)' CMakeLists.txt && \
    mkdir build && \
    cd build && \
    cmake .. -DINSTALL_MISSING=ON -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=$SDK_ROOT_DIR/install && \
    make -j$(nproc) install

# Emulator build
RUN cd $SDK_ROOT_DIR/source && \
    git clone https://gitlab.com/qbau/software-and-apps/emulator.git && \
    cd emulator && \
    mkdir build && \
    cd build && \
    cmake .. -DINSTALL_MISSING=ON -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=$SDK_ROOT_DIR/install && \
    make -j$(nproc) install && \
    # Remove emulator source
    cd $SDK_ROOT_DIR/source && rm -rf emulator

ENTRYPOINT ["/bin/bash"]
