#!/bin/bash    
# Docs: serve at port 8080
python3 -m http.server 8080 --bind 0.0.0.0 --directory $QB_SDK_ROOT/docs/html &

# Jupyter Lab: serve at port 8889
jupyter lab --allow-root --no-browser --notebook-dir=$QB_SDK_ROOT --ip=0.0.0.0 --port=8889 --ServerApp.token="" --ServerApp.terminado_settings ="{'shell_command': ['/bin/bash']}" --IPKernelApp.pylab="inline"