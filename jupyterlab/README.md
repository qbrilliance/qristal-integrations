## JupyterLab resources

This directory holds all items that assist in running Qristal in a JupyterLab environment.


## Using JupyterLab for Python notebooks with QB SDK
Use these instructions to:
* Setup JupyterLab to serve on port 8889
* Make Jupyter sessions without requiring a session password

### Instructions for Ubuntu 20.04, x86_64 systems

**Virtual environment**
```
sudo apt-get install -y python3.8-venv
sudo locale-gen en_US.UTF-8

python3 -m venv "${HOME}"/qb_venv
export VIRTUAL_ENV="${HOME}"/qb_venv

source "${HOME}"/qb_venv/bin/activate

python3 -m pip install --upgrade \
  pip \
  cmake \
  clang-format \
  pytest
```
**Packages needed for applications based on the SDK**
```
python3 -m pip install \
  amazon-braket-sdk \
  ase \
  boto3 \
  cirq==0.14.1 \
  flask \
  ipopo \
  ipywidgets \
  jupyterlab==3 \
  mock \
  nftopt \
  opencv-python \
  openfermion \
  openfermionpyscf \
  pyQuirk \
  pyscf \
  pylint \
  qiskit \
  qsimcirq==0.12.1 \
  scikit-quant \
  wheel
```
**Set a location for storing a JupyterLab configuration**
```
export JUPYTER_DIR="${HOME}"/.jupyter
mkdir -p ${JUPYTER_DIR}
```
**Contents of `${JUPYTER_DIR}/jupyter_lab_config.py`**


```python
  c = get_config()
  c.IPKernelApp.pylab = 'inline'
  c.NotebookApp.open_browser = False
  c.ServerApp.ip = '0.0.0.0'
  c.ServerApp.port = 8889
  c.ServerApp.token = ''
  c.ServerApp.password = ''
  c.ServerApp.root_dir = ''
  c.ServerApp.terminado_settings = {'shell_command': ['/bin/bash']}

```
The above configuration allows
* the $HOME directory to be the JupyterLab root, and
* allows passwordless JupyterLab sessions.

**Start JupyterLab**

Now launch JupyterLab using the command:
```
jupyter lab
```

