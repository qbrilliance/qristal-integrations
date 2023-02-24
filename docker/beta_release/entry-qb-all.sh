#!/bin/bash    

# Jupyter Lab: serve at port 8889
jupyter lab --allow-root --no-browser --notebook-dir=$QB_SDK_ROOT --ip=0.0.0.0 --port=8889 --ServerApp.token="" --ServerApp.terminado_settings ="{'shell_command': ['/bin/bash']}" --IPKernelApp.pylab="inline"