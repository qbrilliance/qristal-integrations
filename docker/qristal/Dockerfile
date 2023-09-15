# Base image: emulator CI image
# Note: this image will have CUDA Quantum support (including its GPU-enabled backend)
# At runtime, if GPUs are attached to the running container (i.e., launched with --gpus option), 
# the CUDA Quantum custatevec backend will also be available.
FROM registry.gitlab.com/qbau/software-and-apps/ci-dockerfiles/ubuntu-22.04:emulator-gcc-1

ENV DEBIAN_FRONTEND noninteractive
RUN apt update && apt install -y nodejs npm vim
RUN python3 -m pip install ipywidgets jupyterhub jupyterlab gpustat wheel
RUN npm install -g configurable-http-proxy

ENV LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/opt/nvidia/cuquantum/lib"

# Current Release version of the Qristal SDK
ARG SDK_VERSION

# Root Qristal directory:
# - /source sub-directory contains source code
# - /install sub-directory contains all install resources
ARG SDK_ROOT_DIR=$HOME/qristal 
# Root dir env to serve docs and Jupyter Lab 
ENV QB_SDK_ROOT=$SDK_ROOT_DIR/install
RUN mkdir -p $SDK_ROOT_DIR

# Qristal
RUN cd $SDK_ROOT_DIR && \
    git clone --branch $SDK_VERSION https://github.com/qbrilliance/qristal source  && \
    cd source && \
    mkdir build && \
    cd build && \
    cmake .. -DCMAKE_BUILD_TYPE=Release -DINSTALL_MISSING=ON -DCMAKE_INSTALL_PREFIX=$SDK_ROOT_DIR/install -DWITH_TKET=ON -DTKET_DIR=${QB_DIR}/tket-local && \
    make -j$(nproc) install 

# Copy entry point script into the container
# The entry point script will serve the Jupyter Lab endpoint. 
COPY entry-qb-all.sh /entry-qb-all.sh
RUN chmod a+rx /entry-qb-all.sh

# Use bash shell in JupyterLab
ENV SHELL=/bin/bash
WORKDIR $SDK_ROOT_DIR
RUN chmod 777 -R $SDK_ROOT_DIR

# Set up user
RUN useradd -ms /bin/bash qristal
USER qristal
ENTRYPOINT "/entry-qb-all.sh"

