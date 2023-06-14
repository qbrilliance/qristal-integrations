from ase import Atoms
from ase.optimize import BFGS
from ase.units import Bohr
from ase.io import read, write
from ase.constraints import FixBondLengths, FixAtoms
import numpy as np

from vqe_interface import VQE
from ase.calculators.dftb import Dftb
from ase.calculators.qmmm import EIQMMM, LJInteractions, Embedding
from ase.calculators.tip3p import TIP3P, epsilon0, sigma0, rOH, angleHOH
import itertools as it
import argparse

parser = argparse.ArgumentParser(description="QM/MM H20-H2 with Qristal + MPI + Nextflow")
parser.add_argument("-f", "--force", help = "Terminate QM/MM at this force threshold, default: 0.0003", nargs = '?', const = 0.0003, default = 0.0003, type = float)
parser.add_argument("-p", "--profile", help = "Nextflow profile list, default: 'standard'", nargs = '?', const = 'standard', type = str)
parser.add_argument("-c", "--command", help = "Path and name of commandline executable, default: ../../cpp/vqeeCalculator/build/vqeeCalculator", nargs = '?', const = "../../cpp/vqeeCalculator/build/vqeeCalculator", default = "../../cpp/vqeeCalculator/build/vqeeCalculator", type = str)
parser.add_argument("-q", "--qpun", help = "Number of QPUs to run in parallel, default: 2", nargs = '?', const = 2, default = 2, type = int)
args = parser.parse_args()
print("\nQM/MM H20-H2 geometry optimisation with Qristal + MPI + Nextflow\n")
print("  Termination criterion : ", args.force)
print("  Nextflow profile      : ", args.profile)
print("  MPI executable        : ", args.command)
print("  Number of QPUs        : ", args.qpun)

thetaHOH = angleHOH / 180 * np.pi
# Create system
atoms = Atoms('HHOHH',
              positions=[[7*Bohr, 0, 0], [8.5*Bohr, 0.5*Bohr, 0], 
              [0, 0, 0], 
              [rOH*np.cos(thetaHOH/2), rOH*np.sin(thetaHOH/2), 0], 
              [rOH*np.cos(thetaHOH/2), -rOH*np.sin(thetaHOH/2), 0]])
#atoms = read('opt.traj')
atoms.center(vacuum=2.0)
# Make QM atoms selection of LiH
qm_idx = range(2)

# Set up interaction & embedding object
# http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.1050.5218&rep=rep1&type=pdf
# https://wiki.fysik.dtu.dk/ase/tutorials/qmmm/qmmm.html
parameters = {'O': (epsilon0,sigma0),
              'H': (0.10, 1.30)}

def lorenz_berthelot(p):
    combined = {}
    for comb in it.product(p.keys(), repeat=2):
       combined[comb] = ((p[comb[0]][0] * p[comb[1]][0])**0.5,
                        (p[comb[0]][1] + p[comb[1]][1])/2)
    return combined

combined = lorenz_berthelot(parameters)
interaction = LJInteractions(combined)

vqe_params = {"acc":"qpp", "theta":[.08]*6+[.08,1.5,2.1], "ansatz":"aswap", 
    "maxeval":200, "functol":1e-5,
    "method":"cobyla", "sn":0, "addqubits":1,
    "in_profile":[args.profile], 
    "in_command":args.command,
    "in_qpus":args.qpun}
vqecalc = VQE(basis='sto6g', n_active_electrons=None, n_active_orbitals=None, 
    verbose=False, vqe_params=vqe_params)

dftcalc = Dftb(Hamiltonian_='DFTB',  # this line is included by default
            Hamiltonian_SCC='Yes',
            Hamiltonian_SCCTolerance=1e-8,
            Hamiltonian_MaxAngularMomentum_='',
            Hamiltonian_MaxAngularMomentum_H='s',
            Hamiltonian_MaxAngularMomentum_O='p')

mmcalc = TIP3P()

atoms.constraints = FixAtoms(indices=[2,3,4])

embedding = Embedding()
# Set up calculator
atoms.calc = EIQMMM(qm_idx,
                    vqecalc,
                    mmcalc,
                    interaction,
                    embedding=embedding,
                    vacuum=None,  # if None, QM cell = MM cell
                    output='qmmm.log')


opt = BFGS(atoms, trajectory='opt.traj')
opt.run(fmax=args.force)
