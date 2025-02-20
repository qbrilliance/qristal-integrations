FROM mcr.microsoft.com/devcontainers/cpp:ubuntu-22.04

# The mounts for this RUN command cache apt lists and packages so they don't have to be
# re-downloaded on consequent builds of the image. The files are kept in the build cache
# only and does not increase the size of the final image. To facilitate using these apt
# build cache mounts, the command configures apt to keep all downloaded packages as the
# default behaviour is to auto clean them.
# See https://docs.docker.com/build/cache/optimize/#use-cache-mounts for more info.
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    rm -f /etc/apt/apt.conf.d/docker-clean; \
    echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache && \
    apt update && \
    apt install -y --no-install-recommends \
    gfortran libboost-all-dev libopenblas-dev
