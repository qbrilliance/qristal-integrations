## Beta Release 

This directory contains a Docker image bundling the QB SDK and emulator (binary only).

The image will be shared with beta testers via the GitLab container registry of the SDK repository.


**Steps to build and push the image**

1. Login to GitLab.

```
sudo docker login registry.gitlab.com
```

2. Build the Docker image.

Please replace `<YOUR GITLAB API KEY>` with your actual key.

```
sudo docker build . --build-arg GITLAB_PRIVATE_TOKEN=<YOUR GITLAB API KEY> --tag registry.gitlab.com/qbau/software-and-apps/public/qbsdk --no-cache
```  
   

3. Push the image to the container registry of the `software-and-apps/public/qbsdk` repository.   

```
sudo docker push registry.gitlab.com/qbau/software-and-apps/public/qbsdk
```