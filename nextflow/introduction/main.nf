nextflow.enable.dsl = 2
params.qpu_n = 2
params.bin_dir = "$projectDir/vqe/build"
params.geometry = "2-hydrogen*.geo"

process read_from_geometry_file {
  input:
    path file_in
  output:
    stdout
  executor 'local'
  cpus 1
  memory '1 GB'
  
  """
  cat $file_in
  """
}

process read_from_geometry_file_count {
  input:
    path file_in
  output:
    stdout
  executor 'local'
  cpus 1
  memory '1 GB'
  
  """
  cat $file_in
  """
}

process count_atoms {
  input:
    stdin
  output:
    stdout
  executor 'local'
  cpus 1
  memory '1 GB'

  """
  wc -l
  """
    
}

process get_energy_XACC_mpi {
  // For Setonix:
  // beforeScript 'eigen/3.4.0 openblas/0.3.15 cmake/3.21.4 py-pip/22.2.2-py3.10.8 python/3.10.8 PrgEnv-gnu/8.3.3 gcc/11.2.0'
  input:
    stdin
    val a_n
  output:
    stdout
  script:
    
   """
      # For Setonix: switch mpiexec -> srun 
      mpiexec --allow-run-as-root -n $params.qpu_n $params.bin_dir/vqe_opt_hpc_app --n-hydrogens $a_n --out-energy-filename energy_result --n-virtual-qpus $params.qpu_n >/dev/null
      cat energy_result
   """

}

workflow {
  def geoc_channel = Channel.fromPath(params.geometry)
  natoms = geoc_channel | read_from_geometry_file_count | count_atoms
  def geo_channel = Channel.fromPath(params.geometry)
  get_energy_XACC_mpi(read_from_geometry_file(geo_channel), natoms.map { it.trim() }).map { it.trim() }.collect().view()
}

