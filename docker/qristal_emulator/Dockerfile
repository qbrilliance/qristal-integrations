# Base image: QBSDK public image
FROM registry.gitlab.com/qbau/software-and-apps/public/qbsdk

# Current Release version of the Qristal SDK
ARG SDK_VERSION

# Add emulator
# API token to access Gitlab repos
ARG GITLAB_PRIVATE_TOKEN
ARG DEV_BUILD=FALSE
# Emulator
RUN git clone --branch $SDK_VERSION https://oauth2:${GITLAB_PRIVATE_TOKEN}@gitlab.com/qbau/software-and-apps/emulator.git && \
    cd emulator && \
    mkdir build && \
    cd build && \
    cmake .. -Dqbcore_DIR=$QB_SDK_ROOT  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTS=OFF -DINTERNAL_DEV_BUILD=$DEV_BUILD && \
    make -j$(nproc) install && \
    # Remove source code
    cd ../.. && rm -rf emulator