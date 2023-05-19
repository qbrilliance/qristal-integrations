## Qristal

This directory contains a Docker image bundling Qristal.

The image will be pushed to the GitLab container registry of the SDK repository.


**Steps to build and push the image**

1. Login to GitLab.

```
sudo docker login registry.gitlab.com
```

2. Build the Docker image.

```
sudo docker build . --tag registry.gitlab.com/qbau/software-and-apps/public/qbsdk --no-cache --network=host
```  
   

3. Push the image to the container registry of the `software-and-apps/public/qbsdk` repository.   

```
sudo docker push registry.gitlab.com/qbau/software-and-apps/public/qbsdk
```
