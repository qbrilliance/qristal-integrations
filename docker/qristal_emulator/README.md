## Qristal + Emulator

This directory contains a Docker image bundling Qristal and the Emulator.

**Steps to build and push the image**

1. Login to GitLab.

```
sudo docker login registry.gitlab.com
```

2. Build the Docker image.

> **_NOTE:_**  This requires access to non-public Quantum Brilliance repositories.

Please replace `<YOUR GITLAB API KEY>` with your actual key to access Quantum Brilliance's emulator repositories.

```
sudo docker build . --build-arg GITLAB_PRIVATE_TOKEN=<YOUR GITLAB API KEY> --no-cache --network=host
```  
