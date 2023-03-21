FROM registry.gitlab.com/qbau/software-and-apps/core:qoda-2

# API token to access Gitlab repos
ARG GITLAB_PRIVATE_TOKEN

ENV DEBIAN_FRONTEND noninteractive

RUN python3 -m pip install jupyterlab==3 
RUN python3 -m pip install cmake --upgrade

# Set up an alias to GitLab set that we don't need to authenticate interactively
RUN git config --global url.https://gitlab-token:$GITLAB_PRIVATE_TOKEN@gitlab.com/.insteadOf https://gitlab.com

# Root Qristal directory:
# - /source sub-directory contains source code
# - /install sub-directory contains all install resources
ARG SDK_ROOT_DIR=$HOME/qristal 
# Root dir env to serve docs and Jupyter Lab 
ENV QB_SDK_ROOT=$SDK_ROOT_DIR/install
RUN mkdir -p $SDK_ROOT_DIR

# QB SDK build
RUN cd $SDK_ROOT_DIR && \
    git clone https://gitlab.com/qbau/software-and-apps/public/QBSDK source && \
    cd source && \
    mkdir build && \
    cd build && \
    cmake .. -DINSTALL_MISSING=ON -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=$SDK_ROOT_DIR/install && \
    make -j$(nproc) install

# Copy entry point script into the container
# The entry point script will serve the Jupyter Lab endpoint. 
COPY entry-qb-all.sh /entry-qb-all.sh
RUN chmod a+rx /entry-qb-all.sh

# Unset the env variable 
RUN git config --global --remove-section url."https://gitlab-token:$GITLAB_PRIVATE_TOKEN@gitlab.com/"
# Use bash shell in JupyterLab
ENV SHELL=/bin/bash
WORKDIR $SDK_ROOT_DIR
ENTRYPOINT "/entry-qb-all.sh"
