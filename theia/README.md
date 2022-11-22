# Theia resources
This directory holds all items that integrate QB SDK into a Theia web-based IDE environment.

=======
## Using Theia as a web-browser IDE with QB SDK
Use these instructions to:

* Setup Theia to serve on port 3001
* Display the Quantum Brilliance splash screen upon opening the Theia URL
* Automatically open a GUI panel that displays Quantum Brilliance branding
* Add a 'Documentation' entry under the Help menu which renders a HTML version of the SDK documentation

## Prerequisites

```
curl -sL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt-get install -y nodejs
sudo npm install --global yarn
sudo apt install -y pkg-config
sudo apt-get install -y libx11-dev libxkbfile-dev
sudo apt-get install -y libsecret-1-dev
```
For more information, refer to [this list of prerequisites](https://github.com/eclipse-theia/theia/blob/master/doc/Developing.md#prerequisites).

## Starting the Node service
    cd second-extension
    yarn
    yarn start:browser --port 3001

Open http://localhost:3001 in the browser.

=======
