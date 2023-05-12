#include "ObservableTransform.hpp"
#include "PauliOperator.hpp"
#include "Utils.hpp"
#include "xacc.hpp"
#include "xacc_observable.hpp"
#include "xacc_service.hpp"
#include <cassert>
#include <fstream>
#include <memory>
#include <numeric>
#include <sstream>
#include <random>

#include <mpi.h>

namespace {

int GetSize() {
  int size;
  if (MPI_Comm_size(MPI_COMM_WORLD, &size) != MPI_SUCCESS) throw std::runtime_error("MPI_Comm_size failed!");
  return size;
}
int GetRank() {
  int rank;
  if (MPI_Comm_rank(MPI_COMM_WORLD, &rank) != MPI_SUCCESS) throw std::runtime_error("MPI_Comm_rank failed!");
  return rank;
}

template <typename T>
void MPI_Bcast_Vector(std::vector<T> &v, int root = 0,
                      MPI_Comm comm = MPI_COMM_WORLD) {
  if (!v.empty()) {
    if (MPI_Bcast(&v[0], v.size() * sizeof(T), MPI_BYTE, root, MPI_COMM_WORLD) != MPI_SUCCESS) throw std::runtime_error("MPI_Bcast failed!");
  }
}

// Split a Pauli into multiple sub-Paulis according to a max number of terms
// constraint.
std::vector<std::shared_ptr<xacc::quantum::PauliOperator>>
splitPauli(std::shared_ptr<xacc::quantum::PauliOperator> &in_pauli,
           int nTermsPerSplit) {
  std::vector<std::shared_ptr<xacc::quantum::PauliOperator>> subPaulis;
  std::map<std::string, xacc::quantum::Term> terms;
  for (auto termIt = in_pauli->begin(); termIt != in_pauli->end(); ++termIt) {
    terms.emplace(*termIt);
    if (terms.size() >= nTermsPerSplit) {
      subPaulis.emplace_back(
          std::make_shared<xacc::quantum::PauliOperator>(terms));
      terms.clear();
    }
  }
  if (!terms.empty()) {
    assert(subPaulis.size() * nTermsPerSplit + terms.size() ==
           in_pauli->nTerms());
    subPaulis.emplace_back(
        std::make_shared<xacc::quantum::PauliOperator>(terms));
  }
  return subPaulis;
}
} // namespace


int main(int argc, char **argv) {
  int rank;
  MPI_Status status;
  MPI_Init(&argc, &argv);
  MPI_Comm_rank(MPI_COMM_WORLD, &rank);
  xacc::Initialize(argc, argv);
  xacc::external::load_external_language_plugins();
  // Process the input arguments
  std::vector<std::string> arguments(argv + 1, argv + argc);
  auto n_virt_qpus = 2;
  auto n_hydrogens = 8;
  bool verbose = false;

  std::string out_filename("all_results.log");
  std::string out_energy_filename("energy.result");
  std::string out_hamiltonian_filename("hamiltonian.result");

  std::ofstream out_fs;
  std::ofstream out_energy_fs;
  std::ofstream out_hamiltonian_fs;
  
  // Random initial values:
  std::uniform_real_distribution<double> unif(-M_PI, M_PI);
  std::mt19937 re(std::random_device{}());
  auto generator = std::bind(unif, std::ref(re));

  for (int i = 0; i < arguments.size(); i++) {
    if (arguments[i] == "--n-virtual-qpus") {
      n_virt_qpus = std::stoi(arguments[i + 1]);
    }
    if (arguments[i] == "--n-hydrogens") {
      n_hydrogens = std::stoi(arguments[i + 1]);
    }
    if (arguments[i] == "--verbose") {
      verbose = true;
    }
    if (arguments[i] == "--out-filename") {
      out_filename = std::string(arguments[i + 1]);
    }
    if (arguments[i] == "--out-energy-filename") {
      out_energy_filename = std::string(arguments[i + 1]);
    }
    if (arguments[i] == "--out-hamiltonian-filename") {
      out_hamiltonian_filename = std::string(arguments[i + 1]);
    }
  }
  xacc::set_verbose(verbose);
  const bool isRoot = GetRank() == 0;

  if (isRoot) {
    std::cout << "Start running H" << n_hydrogens << " with " << n_virt_qpus
              << " QPUs.\n";
  }
  std::stringstream linestdin;
  std::stringstream geom_ss;
  std::string ggs("NOT-AVAILABLE");
  int ggs_size = 0;

  if (isRoot) {  
    for (std::string line; std::getline(std::cin,line);) {
      linestdin << line << "\n";
    }
    ggs = linestdin.str();
  }

  ggs_size = ggs.size();
  MPI_Bcast(&ggs_size, 1, MPI_INT, 0, MPI_COMM_WORLD);

  if (!isRoot) {
    ggs.resize(ggs_size);
  }

  if (isRoot) {
    out_fs.open(out_filename);
    if (!out_fs.is_open()) {
      std::cerr << "Failed to open " << out_filename << "\n";
      exit(10);
    }

    out_energy_fs.open(out_energy_filename);
    if (!out_energy_fs.is_open()) {
      std::cerr << "Failed to open " << out_energy_filename << "\n";
      exit(11);
    }
    
    out_hamiltonian_fs.open(out_hamiltonian_filename);  
    if (!out_hamiltonian_fs.is_open()) {
      std::cerr << "Failed to open " << out_hamiltonian_filename << "\n";
      exit(12);
    }
  }

  MPI_Barrier(MPI_COMM_WORLD);
  MPI_Bcast(const_cast<char*>(ggs.data()),ggs_size,MPI_CHAR,0,MPI_COMM_WORLD);
  MPI_Barrier(MPI_COMM_WORLD);
  if (verbose) {
    std::cout << "Rank " << rank << ": Geometry from stdin: \n" << ggs << "\n";
  }

  // Create the Observable
  xacc::ScopeTimer ham_timer("pyscf", false);
  auto ham = xacc::quantum::getObservable(
      "pyscf", {{"basis", "sto-3g"}, {"geometry", ggs}});
  if (isRoot) {
    out_fs << "pySCF Hamiltonian generation runtime: "
              << ham_timer.getDurationMs() << " [ms].\n";
  }
  // Ham as Pauli:
  auto jw = xacc::getService<xacc::ObservableTransform>("jw");
  ham = jw->transform(ham);
  if (isRoot) {
    out_hamiltonian_fs << ham->toString() << "\n";
  }
  auto Ham_pauli = std::dynamic_pointer_cast<xacc::quantum::PauliOperator>(ham);
  assert(Ham_pauli);

  const int MAX_TERMS_PER_OBSERVE = 2 * n_virt_qpus;
  auto subPaulis = splitPauli(Ham_pauli, MAX_TERMS_PER_OBSERVE);

  // UCCSD ansatz:
  xacc::ScopeTimer uccsd_timer("uccsd", false);
  auto tmp = xacc::getService<xacc::Instruction>("uccsd");
  auto uccsd = std::dynamic_pointer_cast<xacc::CompositeInstruction>(tmp);
  assert(uccsd);
  uccsd->expand({{"nq", 2 * n_hydrogens}, {"ne", n_hydrogens}});
  const int nOptVars = uccsd->nVariables();
  if (isRoot) {
    out_fs << "UCCSD circuit generation runtime: "
              << uccsd_timer.getDurationMs() << " [ms].\n";
  }

  std::vector<double> init_params(nOptVars);
  std::generate(std::begin(init_params), std::end(init_params), generator);

  MPI_Bcast_Vector(init_params);

  // Function to optimize:
  xacc::OptFunction f(
      [&](const std::vector<double> &x, std::vector<double> &g) {
        assert(x.size() == nOptVars);
        std::vector<double> subEnergies;
        int totalProcess = 0;
        for (auto &obs : subPaulis) {
          auto accelerator =
              xacc::getAccelerator("aer", {{"sim-type", "statevector"}});
          
          accelerator = xacc::getAcceleratorDecorator(
              "hpc-virtualization", accelerator,
              {{"n-virtual-qpus", n_virt_qpus}, {"sim-type", "statevector"}});
          
          auto q = xacc::qalloc(2 * n_hydrogens);
          auto ansatz = (*uccsd)(x);
          auto vqe = xacc::getAlgorithm(
              "vqe",
              {{"ansatz", ansatz},
               {"observable", std::dynamic_pointer_cast<xacc::Observable>(obs)},
               {"accelerator", accelerator}});

          xacc::ScopeTimer timer("runtime", false);
          xacc::set_verbose(false);
          const double energy = vqe->execute(q, {})[0];
          xacc::set_verbose(verbose);
          auto run_time = timer.getDurationMs();
          const bool isRank0 =
              q->hasExtraInfoKey("rank") ? ((*q)["rank"].as<int>() == 0) : true;
          totalProcess += obs->nTerms();
          if (isRoot) {
            if (isRank0) {
              out_fs << "Processed " << std::to_string(totalProcess) << " / " <<
                       std::to_string(Ham_pauli->nTerms()) << "\n";
            }
          }
          subEnergies.emplace_back(energy);
        }
        const double total_energy =
            std::accumulate(subEnergies.begin(), subEnergies.end(),
                            decltype(subEnergies)::value_type(0));
        return total_energy;
      },
      nOptVars);

  // Run optimization:
  auto optimizer =
      xacc::getOptimizer("nlopt", {{"initial-parameters", init_params}});
  
  auto [min_energy, opt_params] = optimizer->optimize(f);
  
  if (isRoot) {
    out_fs << "Min energy = " << min_energy << "\n";
    out_energy_fs << min_energy << "\n";
    out_fs << "Optimal parameters = ";
    for (int i = 0; i < opt_params.size() - 1; ++i) {
      out_fs << opt_params[i] << ", ";
    }
    out_fs << opt_params.back() << "\n";
    out_fs.close();
    out_energy_fs.close();
    out_hamiltonian_fs.close();
  }
  

  // Finalize
  xacc::Finalize();
}