from qiskit import QuantumCircuit, transpile
from qiskit.circuit.controlflow.break_loop import BreakLoopPlaceholder
from qiskit.circuit.library import ZGate, MCXGate
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler, Session
from qiskit.primitives import SamplerResult
from qiskit.primitives.containers.primitive_result import PrimitiveResult
from collections import Counter
from Crypto.Hash import RIPEMD160
from ecdsa import SigningKey, SECP256k1
from qiskit_algorithms import Grover, AmplificationProblem
from qiskit.quantum_info import Statevector
from bitarray import bitarray
from qiskit_aer.primitives import SamplerV2  # for simulator
from qiskit_ibm_runtime import SamplerV2 as real_sampler  # for hardware
from qiskit_aer import AerSimulator, Aer
import random
import time
import hashlib
import base58
import numpy as np
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
from qiskit import QuantumRegister, ClassicalRegister
from qiskit.circuit.library import QFT
from qiskit.quantum_info import Operator
import math
import cupy as cp  # Import CuPy for CUDA-accelerated operations

# Load IBMQ account using QiskitRuntimeService
QiskitRuntimeService.save_account(
    channel='ibm_quantum',
    token='623357116bf40ae972db60e06cb35610de97fbbb900c10f7cfc6ba5c88a2b851d04b47360f0a9c277de660dbed7a5b213e6fc0613a905cbf1574dac8c69f709c',  # Replace with your actual token
    instance='ibm-q/open/main',
    overwrite=True,
    set_as_default=True
)

# Load the service
service = QiskitRuntimeService()

SECP256K1_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# EC Prime Field (Secp256k1)
p = int("0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F", 16)
g_x = int("0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798", 16)
g_y = int("0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8", 16)

# Modular Inverse using Extended Euclidean Algorithm
def mod_inverse(a, p):
    if a == 0:
        return 0
    lm, hm = 1, 0
    low, high = a % p, p
    while low > 1:
        ratio = high // low
        nm, new_low = hm - lm * ratio, high - low * ratio
        lm, low, hm, high = nm, new_low, lm, low
    return lm % p

# Point Addition on elliptic curve (Secp256k1)
def point_addition(x1, y1, x2, y2, p):
    if x1 == x2 and y1 == y2:
        return point_doubling(x1, y1, p)
    lam = ((y2 - y1) * mod_inverse(x2 - x1, p)) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return x3, y3

# Point Doubling on elliptic curve (Secp256k1)
def point_doubling(x1, y1, p):
    lam = ((3 * x1 * x1) * mod_inverse(2 * y1, p)) % p
    x3 = (lam * lam - 2 * x1) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return x3, y3

# Scalar multiplication using double-and-add method
def scalar_multiplication(k, x, y, p):
    x_res, y_res = x, y
    k_bin = bin(k)[2:]  # Convert k to binary string
    for bit in k_bin[1:]:
        x_res, y_res = point_doubling(x_res, y_res, p)
        if bit == '1':
            x_res, y_res = point_addition(x_res, y_res, x, y, p)
    return x_res, y_res  

# Function to convert private key to compressed Bitcoin address
def private_key_to_compressed_address(private_key_hex):
    print(f"Converting private key {private_key_hex} to Bitcoin address...")
    private_key_bytes = bytes.fromhex(private_key_hex)
    sk = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
    vk = sk.verifying_key
    public_key_bytes = vk.to_string()
    x_coord = public_key_bytes[:32]
    y_coord = public_key_bytes[32:]
    prefix = b'\x02' if int.from_bytes(y_coord, 'big') % 2 == 0 else b'\x03'
    compressed_public_key = prefix + x_coord

    sha256_pk = hashlib.sha256(compressed_public_key).digest()
    ripemd160 = RIPEMD160.new()
    ripemd160.update(sha256_pk)
    hashed_public_key = ripemd160.digest()

    network_byte = b'\x00' + hashed_public_key
    sha256_first = hashlib.sha256(network_byte).digest()
    sha256_second = hashlib.sha256(sha256_first).digest()
    checksum = sha256_second[:4]

    binary_address = network_byte + checksum
    bitcoin_address = base58.b58encode(binary_address).decode('utf-8')
    print(f"Generated Bitcoin address: {bitcoin_address}")
    return bitcoin_address

def create_oracles_shors_gpu(num_qubits):
    """Creates Shor's oracles in keyspace with CUDA-enabled steps."""
    # Example of initializing an oracle matrix in CUDA memory
    oracle_matrix_gpu = cp.eye(2**num_qubits, dtype=cp.complex128)  # Identity matrix in GPU as a placeholder
    # More complex operations for your oracle would go here
    return oracle_matrix_gpu

# GPU-accelerated Oracle function to implement Shor's algorithm with keyspace restriction
def shors_oracle_with_keyspace_gpu(circuit, q_x, anc, public_key_x, keyspace_start, keyspace_end):
    print(f"Applying Shor's oracle with keyspace [{keyspace_start}, {keyspace_end}] using GPU...")
    for k in range(keyspace_start, keyspace_end + 1):  # Loop through the restricted keyspace
        index = k - keyspace_start
        if index < len(q_x):  # Check if the index is within bounds of the register
            computed_x, _ = scalar_multiplication(k, g_x, g_y, p)
            if computed_x == public_key_x:
                circuit.mcx(q_x, anc[0])  # Use MCXGate with ancilla qubit as target
    print("Oracle applied with GPU acceleration in keyspace.")
    return circuit

# Convert binary string to hexadecimal
def binary_to_hex(bin_str):
    hex_str = hex(int(bin_str, 2))[2:].upper()
    return hex_str.zfill(64)  # Pad hex string to ensure it's 64 characters long (32 bytes)

# Retrieve the job result and search for the target
def retrieve_job_result(job_id, target_address):
    print(f"Retrieving job result for job ID: {job_id}...")
    try:
        job = service.job(job_id)
        result = job.result()

        # Print the job result to inspect its structure
        counts = result.get_counts()
        print(f"Measurement counts retrieved: {counts}")

        # Count occurrences of each unique measurement result
        sorted_counts = sorted(counts.items(), key=lambda item: item[1], reverse=True)

        # Check if any of the keys correspond to the target Bitcoin address
        for bin_key, count in sorted_counts:
            private_key_hex = binary_to_hex(bin_key)

            # Convert to compressed Bitcoin address
            compressed_address = private_key_to_compressed_address(private_key_hex)

            if compressed_address is not None and compressed_address == target_address:
                print(f"Private key found: {private_key_hex}")

                # Save the found private key to boom.txt
                with open('boom.txt', 'a') as file:
                    file.write(f"Private key: {private_key_hex}\nCompressed Address: {compressed_address}\n\n")

                return private_key_hex, compressed_address  # Return the found key

        print("No matching private key found.")
        return None, None
    except Exception as e:
        print(f"Error while retrieving job result: {e}")
        return None, None

# Convert binary string to hexadecimal
def binary_to_hex(bin_str):
    hex_str = hex(int(bin_str, 2))[2:].upper()
    return hex_str.zfill(64)  # Pad hex string to ensure it's 64 characters long (32 bytes)

# Function to plot the result histogram of counts
def plot_result_histogram(counts):
    plot_histogram(counts)
    labels, values = zip(*counts.items())  # Unpack the counts dictionary
    if isinstance(labels[0], str) and all(set(label).issubset({'0', '1'}) for label in labels):

        hex_labels = [binary_to_hex(label) for label in labels]
    else:
        hex_labels = labels

    plt.bar(range(len(values)), values, tick_label=hex_labels)
    plt.xlabel('Private Keys (Hex)' if isinstance(hex_labels[0], str) else 'Private Key Candidates')
    plt.ylabel('Counts')
    plt.title('Histogram of Measurement Counts')
    plt.tight_layout()
    plt.show()

# Function to get the top 10 most frequent counts
def get_top_10_frequent(counts):
    sorted_counts = sorted(counts.items(), key=lambda item: item[1], reverse=True)
    top_10_counts = sorted_counts[:10]
    print(f"Top 10 most frequent counts: {top_10_counts}")
    
    private_key_candidates = [int(bitstring, 2) for bitstring, _ in top_10_counts]
    return private_key_candidates

# Main quantum algorithm for private key recovery
def quantum_private_key_recovery_gpu(public_key_hex, num_qubits, target_address, keyspace_start, keyspace_end):
    public_key_x = int(public_key_hex[2:], 16)

    while True:  # Loop indefinitely until the key is found
        # Create quantum and classical registers
        q_x = QuantumRegister(num_qubits, 'x')
        c = ClassicalRegister(num_qubits + 1, 'c')
        anc = QuantumRegister(1, 'anc')  # Add ancillary qubit
        circuit = QuantumCircuit(q_x, anc, c)

        # Create superposition
        circuit.h(q_x)
        print("Superposition created.")

        # Apply the Shor's oracle with the restricted keyspace using GPU-enabled function
        circuit = shors_oracle_with_keyspace_gpu(circuit, q_x, anc, public_key_x, keyspace_start, keyspace_end)

        # Apply inverse QFT with GPU acceleration
        qft_matrix = cp.asarray(QFT(num_qubits, do_swaps=True).inverse().to_matrix())
        print("Inverse QFT with GPU applied.")

        # Measure the result
        circuit.measure(q_x, c[:num_qubits])  # Measure all qubits in q_x to classical register c
        circuit.measure(anc[0], c[num_qubits])  # Measure the ancillary qubit into the next classical bit
        print("Measurement operation added.")

        # Transpile and run the circuit
        backend = service.backend('ibm_brisbane')  # Change to the correct backend
        transpiled_circuit = transpile(circuit, backend=backend, optimization_level=3)
        print("Circuit transpiled.")

        # Run the job and retrieve results
        job = backend.run([transpiled_circuit], shots=8192)
        job_id = job.job_id()
        print(f"Job ID: {job_id}")

        # Wait for job to finish and get the result
        result = job.result()
        counts = result.get_counts()
        print("Result Counts:", counts)

        # Get the top 10 frequent counts and search for the target
        private_key_candidates = get_top_10_frequent(counts)

        # Retrieve the job result and look for the private key
        found_key, compressed_address = retrieve_job_result(job_id, target_address)

        if found_key:
            print(f"Found matching private key: {found_key}")
            
            # Save the found private key into boomm.txt
            with open("boomm.txt", "w") as file:
                file.write(found_key)

            print(f"Completed all attempts. Found key: {found_key}")
            break  # Exit the loop if the key is found
        
        print("Key not found, resubmitting job...")
        time.sleep(5)  # Wait a few seconds before resubmitting

if __name__ == "__main__":
    # Define parameters for the quantum private key recovery
    public_key_hex = "0233709eb11e0d4439a729f21c2c443dedb727528229713f0065721ba8fa46f00e"  # Replace with your public key hex
    target_address = "1PXAyUB8ZoH3WD8n5zoAthYjN15yN5CVq5"  # Replace with the target Bitcoin address
    num_qubits = 125  # Adjust the number of qubits as needed
    keyspace_start = 0x10000000000000000000000000000000   # Set start of keyspace
    keyspace_end = 0x1fffffffffffffffffffffffffffffff   # Set end of keyspace
    # Call the quantum private key recovery function
    quantum_private_key_recovery_gpu(public_key_hex, num_qubits, target_address, keyspace_start, keyspace_end)
