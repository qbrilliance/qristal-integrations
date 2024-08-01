import nextflow
import numpy as np
import os

def get_result(nf_ppl_run_in):
    allout = [x.all_output_data() for x in nf_ppl_run_in.process_executions]
    energy = []
    for p in allout:
        for q in p:
            if 'energy_result' in q:
                eres = open(q)
                for line in eres:
                    energy.append(float(line))
    return energy

def test_qristal_vqe():
    nf_ppl = nextflow.Pipeline("main.nf", config="nextflow.config")
    # Using Slurm scheduler
    # nf_ppl_run = nf_ppl.run(profile=["cluster_pawsey"])
    #
    # Using local execution
    nf_ppl_run = nf_ppl.run(profile=["standard"], params={
        "bin_dir"  : os.environ['QRISTAL_INSTALL_DIR']+"/examples/cpp/vqe_opt_hpc_app/build",
        "geometry" : "../../tests/nextflow/introduction/2-hydrogen.geo",
        "qpu_n"    : "2"
        })
    energy = np.mean(get_result(nf_ppl_run))
    return energy

if os.environ.get('QRISTAL_INSTALL_DIR') :
    print(test_qristal_vqe())
else :
    print("QRISTAL_INSTALL_DIR is not set in your environment.  Please set it to the location where Qristal is installed.")
