## Introduction to VQE using Nextflow and Qristal
**Note:** All commands are to be run from the same directory that contains this README file (unless otherwise noted). 

Please follow these installation steps:
### 1. Clone the Qristal repository

```
git clone https://github.com/qbrilliance/qristal
```

### 2. Build + install Qristal with MPI enabled
Note the `CMAKE_INSTALL_PREFIX` here... you should modify this to suit your own installation if the default used here is not appropriate for you.
```
STARTDIR=$(pwd)
export QRISTAL_INSTALL_DIR=/home/ubuntu/core-local
cd QBSDK
mkdir build && cd build
cmake .. -DINSTALL_MISSING=ON -DENABLE_MPI=ON -DCMAKE_INSTALL_PREFIX="${QRISTAL_INSTALL_DIR}"

make -j4 install
```

### 3. Build the VQE with MPI support (`vqe_opt_hpc_app`)
This application uses a MPI-enabled VQE for hydrogen chains.

To use it, you need to first add it as a Qristal example by using:
```
cd "${STARTDIR}"
mkdir build && cd build
cmake .. -DCMAKE_INSTALL_PREFIX="${QRISTAL_INSTALL_DIR}"
make install
```
Next, compile it using:

```
cd "${QRISTAL_INSTALL_DIR}/examples/cpp/vqe_opt_hpc_app"
mkdir build && cd build
cmake ..
make
```

### 4. Run the 2 Hydrogen example
```
cd "${STARTDIR}"
VQE_OPT_DIR="${QRISTAL_INSTALL_DIR}/examples/cpp/vqe_opt_hpc_app/build"
INPUT_GEOM="../../tests/nextflow/introduction/2-hydrogen.geo"
NQPUS=2
NATOMS=$(cat $INPUT_GEOM | wc -l)
cat $INPUT_GEOM | mpiexec -n  $NQPUS  "${VQE_OPT_DIR}"/vqe_opt_hpc_app --n-hydrogens $NATOMS --n-virtual-qpus $NQPUS
```
### 5. Inspect the results
```
cat all_results.log
```
Example output:
```
pySCF Hamiltonian generation runtime: 643.689 [ms].
UCCSD circuit generation runtime: 148.412 [ms].
Processed 15 / 15
Processed 15 / 15
Processed 15 / 15
Processed 15 / 15
Processed 15 / 15
Processed 15 / 15
Processed 15 / 15
Processed 15 / 15
Processed 15 / 15
Processed 15 / 15
Processed 15 / 15
Processed 15 / 15
Processed 15 / 15
Processed 15 / 15
Processed 15 / 15
Processed 15 / 15
Processed 15 / 15
Processed 15 / 15
Processed 15 / 15
Processed 15 / 15
Processed 15 / 15
Processed 15 / 15
Min energy = -1.10115
Optimal parameters = 3.14159, 3.05359
```

### 6. Nextflow integration 
**Prerequisite:** you have installed Qristal with MPI-enabled.

#### **Required files (provided by this repository):**
[nextflow.config](./nextflow.config)

 [main.nf](./main.nf)
 
**Example usage**

An example of how to use the **Slurm queue submission handling features of Nextflow**:

Note: see [nextflow.config](./nextflow.config) for the details on the `delta` profile used below.
```
cd "${STARTDIR}"
nextflow run main.nf \
-profile delta \
--qpu_n 2 \
--bin_dir "${VQE_OPT_DIR}" \
--geometry ../../tests/nextflow/introduction/2-hydrogen.geo
```
**Example output**

Note: `executor > local (3), slurm (1)` in the output below which tells you that 1 process [`get_energy_XACC_mpi`] ran via Slurm:
```
N E X T F L O W  ~  version 23.04.1
Launching `main.nf` [dreamy_shockley] DSL2 - revision: f0aa2b78b2
executor >  local (3), slurm (1)
[82/be3312] process > read_from_geometry_file_count (1) [100%] 1 of 1 ✔
[be/71f9a1] process > count_atoms (1)                   [100%] 1 of 1 ✔
[f7/d5446b] process > read_from_geometry_file (1)       [100%] 1 of 1 ✔
[fa/588f1b] process > get_energy_XACC_mpi (1)           [100%] 1 of 1 ✔
['-1.10115']
```

To run **without the Slurm queue**:
```
cd "${STARTDIR}"
nextflow run main.nf \
-profile standard \
--qpu_n 2 \
--bin_dir "${VQE_OPT_DIR}" \
--geometry ../../tests/nextflow/introduction/2-hydrogen.geo
```

**Example output without Slurm**

Note: `executor > local (4)` in the output below which tells you that all processes executed locally:
```
N E X T F L O W  ~  version 23.04.1
Launching `main.nf` [sleepy_edison] DSL2 - revision: f0aa2b78b2
executor >  local (4)
[93/716e5a] process > read_from_geometry_file_count (1) [100%] 1 of 1 ✔
[dc/b7ccc0] process > count_atoms (1)                   [100%] 1 of 1 ✔
[72/a83fb6] process > read_from_geometry_file (1)       [100%] 1 of 1 ✔
[09/7bd03c] process > get_energy_XACC_mpi (1)           [100%] 1 of 1 ✔
['-1.10115']
```

### 7. Integration with Python via `nextflow.py`

Install the Python module using:
```
python3 -m pip install nextflowpy
```
#### **Required files (provided by this repository):**

[run.py](./run.py)

Example output:
```
python3 run.py

# Output: -1.10115
```
