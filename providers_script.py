# Module: providers and backends
# Author: oanikienko, mguzzoc
# Date: 19/11/2023

# == Libraries == #

# from utils import configuration
from qiskit_ibm_runtime import QiskitRuntimeService, Options, Session, Sampler
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import SparsePauliOp
from qiskit.providers.fake_provider import FakeProvider, FakeProviderForBackendV2, FakeManilaV2, FakeNairobiV2
from qiskit.providers.aer.noise import NoiseModel
import pprint

# == Functions == #

def search_backend(provider, searched_backend_name):
    """
    Search a backend using its name among the backends of a specified provider.

    Parameters
    ==========
    - provider: Provider object
        Provider of the backends (FakeProviderForBackendV2, QiskitRuntimeService)
    - searched_backend_name: string
        Name of the backend to search ("fake_manila", "fake_melbourne")

    Return
    ======
    - searched_backend: Backend Object|None
        Corresponding backend if found, None otherwise
    """

    searched_backend = None

    for backend in provider.backends():
        if backend.name == searched_backend_name:
            searched_backend = backend

    return searched_backend


def get_backend_info(backend):
    """
    Fetch the information about a specified backend.

    Parameters
    ==========
    - backend: Backend Object
        Backend for which the information needs to be fetched

    Return
    ======
    - backend_info: dictionnary
        Dictionary containing the characteristics of the backend
    """

    backend_info = {
        'name': backend.name,
        'version': backend.backend_version,
        'online_date': backend.online_date,
        'syst_time_resolution_input_signals': backend.dt,
        'syst_time_resolution_output_signals': backend.dtm,
        'max_circuits_per_job': backend.max_circuits,
        'num_qubits': backend.num_qubits,
        'coupling_map': backend.coupling_map,
        'operation_names': backend.operation_names,
        'instruction_durations': backend.instruction_durations,
        'instruction_schedule_map': backend.instruction_schedule_map,
        'target': backend.target
    }

    return backend_info

def print_backend_info(backend_info):
    """
    Print the information about a specified backend.

    Parameters
    ==========
    - backend_info: dictionnary
        Backend information
    """

    print("Name: ", backend_info['name'])
    print("Version: ", backend_info['version'])
    print("Online date: ", backend_info['online_date'])
    print("Max circuits per job: ", backend_info['max_circuits_per_job'])
    print("Number of qubits: ", backend_info['num_qubits'])

    print("System time resolution:")
    print("\tInput signals: ", backend_info['syst_time_resolution_input_signals'])
    print("\tOutput signals: ", backend_info['syst_time_resolution_output_signals'])

    print("Coupling map:")
    backend_info['coupling_map'].draw()

    print("Operations names: ", backend_info['operation_names'])

    print("Target:")
    for gate in backend_info['target'].keys():
        print("\t", gate)
        for qbits in backend_info['target'][gate].keys():
            if backend_info['target'][gate][qbits] != None and backend_info['target'][gate][qbits] != None:
                print("\t\tQubit(s) {0}: duration={1}, error={2}".format(qbits, backend_info['target'][gate][qbits].duration, backend_info['target'][gate][qbits].error))
            else:
                print("\t\tQubit(s) {0}: duration=None, error=None".format(qbits))

        # print("\t\t", backend_info['target'][gate])
        # print("{0}: {1}".format(backend_info['target'][target_key], backend_info['target'][target_key]))


def get_gate_errors(backend):
    """
    Fetch the information about a specified backend.

    Parameters
    ==========
    - backend: Backend Object
        Backend for which the gate errors needs to be found

    Return
    ======
    - gate_errors: dictionnary
        Dictionary containing the gate errors sorted by gate and by qubits
    """

    gate_errors = dict()

    # print(backend.target.keys())

    for gate in backend.target.keys():
        # print("\t", gate)
        gate_errors[gate] = dict()
        for qbits in backend.target[gate].keys():
            if backend.target[gate][qbits] != None and backend.target[gate][qbits] != None:
                # print("\t\tQubit(s) {0}: duration={1}, error={2}".format(qbits, backend.target[gate][qbits].duration, backend.target[gate][qbits].error))
                gate_errors[gate][qbits] = backend.target[gate][qbits].error
            else:
                # print("\t\tQubit(s) {0}: duration=None, error=None".format(qbits))
                gate_errors[gate][qbits] = None
    
    return gate_errors


def create_options(nb_shots, backend = None):
    """
    Create the options for the simulations.

    Parameters
    ==========
    - nb_shots: int
        Number of executions on the simulator
    - backend: Backend Object|None
        If None, noiseless estimation; otherwise: fetch noise model, basis gates and coupling map of the specified backend

    Return
    ======
    - options: Options object
        Options to use for a specific simulation
    """

    options = Options()
    options.execution.shots = nb_shots
    options.optimization_level = 0 # We do not optimize the implementation
    options.resilience_level = 0 # We do not use quantum error mitigation

    # If a backend is defined = If the simulation is run on a noisy simulator
    if backend != None:
        options.simulator = {
                "noise_model": NoiseModel.from_backend(backend), 
                "basis_gates": backend.operation_names, 
                "coupling_map": backend.coupling_map 
        }

    return options



## == Tests == ##

if __name__ == "__main__":

    ##########################################
    # Providers and backends: function tests #
    ##########################################


    # Defining the provider (here using the provider of snapshots)
    fake_provider = FakeProviderForBackendV2()


    # Getting all the backends of the fake_provider
    fake_backends = fake_provider.backends()


    # Selecting two specific backends
    fake_Melbourne = search_backend(fake_provider, "fake_melbourne")
    fake_Armonk = search_backend(fake_provider, "fake_armonk")


    # Getting information about these fake backends
    print(">> Information about different backends")

    Melbourne_info = get_backend_info(fake_Melbourne)
    print_backend_info(Melbourne_info)

    
    Armonk_info = get_backend_info(fake_Armonk)
    print_backend_info(Armonk_info)


    
    ##########################################
    # Simulations on ideal and noisy backend #
    ##########################################

    print("\n SIMULATIONS")

    # Defining the circuit
    qc = QuantumCircuit(2,2)
    qc.h(0)
    qc.x(1)
    qc.cx(0,1)

    qc.measure_all() 

    # Defining the service to use
    ibm_quantum_service = QiskitRuntimeService(
                                channel="ibm_quantum",
                                token="", # TODO put here the api token from IBM Quantum
                                instance="ibm-q/open/main"
                              )

    # Defining the simulator
    simulator = ibm_quantum_service.get_backend("ibmq_qasm_simulator") 


    # Defining the options
    nb_shots = 1024
    ideal_options = create_options(nb_shots)
    noisy_options = create_options(nb_shots, fake_Melbourne)

    #### == Performing experiments on the ideal backend == ### 

    print(">> Running experiments on ideal backend...")
    with Session(service = ibm_quantum_service, backend = simulator) as session:
        sampler = Sampler(session = session, options = ideal_options)

        tqc = transpile(qc, simulator)
        job = sampler.run(tqc)
        result = job.result()

        print(result)


    #### == Performing experiments on the noisy backend == ### 
    # Important: here the simulations are run on simulator only, not on real backends, by using noisy_options
    # The following code works only for fake backends (snapshots)

    print(">> Running experiments on noisy backend...")
    with Session(service = ibm_quantum_service, backend = simulator) as session:
        sampler = Sampler(session = session, options = noisy_options)

        tqc = transpile(qc, simulator)
        job = sampler.run(tqc)
        result = job.result()

        print(result)

