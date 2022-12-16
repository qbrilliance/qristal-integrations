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
    doxygen \
    gfortran \
    git \
    graphviz \
    libboost-all-dev \
    libcurl4-openssl-dev  \
    libeigen3-dev \
    libopenblas-dev \
    libpython3-dev \
    libunwind-dev \
    python3 \
    python3-pip \
    python3-sphinx \
    vim

RUN python3 -m pip install \
    amazon-braket-sdk \
    boto3 cirq==1.0.0 \
    conan \
    exhale \
    flask \
    ipopo \
    ipywidgets \
    jupyterlab==3 \
    myst-parser \
    openfermion \
    openfermionpyscf \
    pyQuirk \
    pyscf \
    qiskit \
    qsimcirq==0.14.0 \
    scikit-quant \
    sphinx_rtd_theme

ENV PATH $PATH:$HOME/.local/bin

# Set up an alias to GitLab set that we don't need to authenticate interactively
RUN git config --global url.https://gitlab-token:$GITLAB_PRIVATE_TOKEN@gitlab.com/.insteadOf https://gitlab.com

# Root SDK directory:
# - /source sub-directory contains source code
# - /install sub-directory contains all install resources
ARG SDK_ROOT_DIR=$HOME/SDK
# Root dir env to serve docs and Jupyter Lab 
ENV QB_SDK_ROOT=$SDK_ROOT_DIR/install
RUN mkdir -p $SDK_ROOT_DIR

# QB SDK build
RUN cd $SDK_ROOT_DIR && \
    git clone https://gitlab.com/qbau/software-and-apps/public/QBSDK source && \
    cd source && \
    # Disable all warnings
    sed  -i '49i add_definitions(-w)' CMakeLists.txt && \
    mkdir build && \
    cd build && \
    cmake .. -DINSTALL_MISSING=ON -DQB_BUILD_DOCS=ON -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=$SDK_ROOT_DIR/install && \
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

# Copy entry point script into the container
# The entry point script will serve the ReadTheDocs and Jupyter Lab endpoints. 
COPY entry-qb-all.sh /entry-qb-all.sh
RUN chmod a+rx /entry-qb-all.sh

# Unset the env variable 
RUN git config --global --remove-section url."https://gitlab-token:$GITLAB_PRIVATE_TOKEN@gitlab.com/"
ENV GITLAB_PRIVATE_TOKEN= 
# Use bash shell in JupyterLab
ENV SHELL=/bin/bash
WORKDIR $SDK_ROOT_DIR
ENTRYPOINT "/entry-qb-all.sh"
