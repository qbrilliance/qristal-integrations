nextflow.enable.dsl = 2
params.qpu_n = 2
params.bin = "$projectDir/vqeeCalculator/build/vqeeCalculator"
params.json_input = "vqeecalc_input*.json"
params.json_output = "vqeecalc_output.json"

process get_energy_XACC_mpi {
  input:
    file json_input
  output:
    val $params.json_output
  script:
    
   """
      # For Setonix: switch mpiexec -> srun
      unset \${!OMPI_*}
      unset \${!PMIX_*}
      mpiexec -v --allow-run-as-root -n $params.qpu_n $params.bin --fromJson=$json_input --jsonID=0 --outputJson=$params.json_output
   """

}

workflow {
  def json_in_channel = Channel.fromPath(params.json_input)
  calc = get_energy_XACC_mpi(json_in_channel)
  calc.view { "${it.text}" }
}

