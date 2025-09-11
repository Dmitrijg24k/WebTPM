#!/usr/bin/env python
"""
Test script for Tree-like Parity Machine implementation.

This script demonstrates the TPM synchronization process and can be used
for testing and validation of the neural cryptography implementation.
"""

import os
import sys
import django
import numpy as np
import time
from typing import Tuple, List

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WebTPMG.settings')
django.setup()

from tpm.consumers import TreeParityMachine, MersenneTwisterRNG, generate_random_vector


def test_tpm_synchronization(k: int = 3, n: int = 4, l: int = 6, 
                           max_steps: int = 1000) -> Tuple[bool, int, float]:
    """
    Test TPM synchronization between two machines.
    
    Args:
        k: Number of hidden units
        n: Input dimension per hidden unit
        l: Weight range
        max_steps: Maximum synchronization steps
        
    Returns:
        Tuple of (success, steps, duration)
    """
    print(f"Testing TPM synchronization: K={k}, N={n}, L={l}")
    
    # Create two TPMs
    tpm1 = TreeParityMachine(k, n, l)
    tpm2 = TreeParityMachine(k, n, l)
    
    start_time = time.time()
    steps = 0
    
    for step in range(max_steps):
        # Generate random input vector
        X = generate_random_vector(step, l, k, n)
        
        # Get outputs from both TPMs
        output1 = tpm1.get_output(X)
        output2 = tpm2.get_output(X)
        
        # Update weights if outputs match
        if output1 == output2:
            tpm1.update(output2, 'hebbian')
            tpm2.update(output1, 'hebbian')
        
        # Check synchronization every 10 steps
        if step % 10 == 0:
            if tpm1.is_synchronized_with(tpm2, test_inputs=50):
                duration = time.time() - start_time
                print(f"Synchronization successful after {step} steps ({duration:.2f}s)")
                return True, step, duration
        
        steps = step
    
    duration = time.time() - start_time
    print(f"Synchronization failed after {max_steps} steps ({duration:.2f}s)")
    return False, max_steps, duration


def test_learning_rules(k: int = 3, n: int = 4, l: int = 6) -> None:
    """Test different learning rules for TPM synchronization."""
    learning_rules = ['hebbian', 'anti_hebbian', 'random_walk']
    
    print("\nTesting different learning rules:")
    print("-" * 50)
    
    for rule in learning_rules:
        print(f"\nTesting {rule} learning rule:")
        
        # Create two TPMs
        tpm1 = TreeParityMachine(k, n, l)
        tpm2 = TreeParityMachine(k, n, l)
        
        success, steps, duration = test_tpm_synchronization_with_rule(
            tpm1, tpm2, rule, max_steps=500
        )
        
        if success:
            print(f"  ✓ Synchronized in {steps} steps ({duration:.2f}s)")
        else:
            print(f"  ✗ Failed to synchronize in 500 steps")


def test_tpm_synchronization_with_rule(tpm1: TreeParityMachine, tpm2: TreeParityMachine,
                                     rule: str, max_steps: int = 500) -> Tuple[bool, int, float]:
    """Test synchronization with a specific learning rule."""
    start_time = time.time()
    
    for step in range(max_steps):
        # Generate random input vector
        X = generate_random_vector(step, tpm1.l, tpm1.k, tpm1.n)
        
        # Get outputs from both TPMs
        output1 = tpm1.get_output(X)
        output2 = tpm2.get_output(X)
        
        # Update weights if outputs match
        if output1 == output2:
            tpm1.update(output2, rule)
            tpm2.update(output1, rule)
        
        # Check synchronization every 10 steps
        if step % 10 == 0:
            if tpm1.is_synchronized_with(tpm2, test_inputs=20):
                duration = time.time() - start_time
                return True, step, duration
    
    duration = time.time() - start_time
    return False, max_steps, duration


def test_chaos_map() -> None:
    """Test the chaos map function."""
    print("\nTesting chaos map function:")
    print("-" * 30)
    
    tpm = TreeParityMachine(3, 4, 6)
    
    # Test multiple chaos values
    chaos_values = []
    for i in range(10):
        chaos = tpm.chaos_map()
        chaos_values.append(chaos)
        print(f"  Chaos value {i+1}: {chaos:.6f}")
    
    # Check if values are in valid range [0, 1]
    valid_range = all(0 <= val <= 1 for val in chaos_values)
    print(f"  All values in [0, 1]: {'✓' if valid_range else '✗'}")
    
    # Check for variation (not all the same)
    variation = len(set(round(val, 4) for val in chaos_values)) > 1
    print(f"  Values vary: {'✓' if variation else '✗'}")


def test_mersenne_twister() -> None:
    """Test the Mersenne Twister implementation."""
    print("\nTesting Mersenne Twister RNG:")
    print("-" * 35)
    
    # Test with same seed
    rng1 = MersenneTwisterRNG(12345)
    rng2 = MersenneTwisterRNG(12345)
    
    # Generate sequences
    seq1 = [rng1.get_random_number() for _ in range(10)]
    seq2 = [rng2.get_random_number() for _ in range(10)]
    
    # Check if sequences are identical
    identical = seq1 == seq2
    print(f"  Same seed produces identical sequences: {'✓' if identical else '✗'}")
    
    # Test with different seeds
    rng3 = MersenneTwisterRNG(54321)
    seq3 = [rng3.get_random_number() for _ in range(10)]
    
    different = seq1 != seq3
    print(f"  Different seeds produce different sequences: {'✓' if different else '✗'}")
    
    # Test range
    rng = MersenneTwisterRNG()
    numbers = [rng.get_random_number() for _ in range(1000)]
    in_range = all(0 <= num <= 0xFFFFFFFF for num in numbers)
    print(f"  All numbers in valid 32-bit range: {'✓' if in_range else '✗'}")


def run_performance_test() -> None:
    """Run performance tests with different TPM parameters."""
    print("\nPerformance Test Results:")
    print("=" * 50)
    
    test_cases = [
        (3, 4, 6),   # Default
        (5, 6, 8),   # Medium
        (8, 10, 12), # Large
    ]
    
    for k, n, l in test_cases:
        print(f"\nTPM Parameters: K={k}, N={n}, L={l}")
        print("-" * 30)
        
        # Run multiple tests
        results = []
        for i in range(5):
            success, steps, duration = test_tpm_synchronization(k, n, l, max_steps=1000)
            results.append((success, steps, duration))
        
        # Calculate statistics
        successful = sum(1 for success, _, _ in results if success)
        avg_steps = np.mean([steps for _, steps, _ in results if steps < 1000])
        avg_duration = np.mean([duration for _, _, duration in results])
        
        print(f"  Success rate: {successful}/5 ({successful*20}%)")
        if successful > 0:
            print(f"  Average steps: {avg_steps:.1f}")
            print(f"  Average duration: {avg_duration:.2f}s")


def main():
    """Main test function."""
    print("WebTPM - Tree-like Parity Machine Test Suite")
    print("=" * 50)
    
    # Test Mersenne Twister
    test_mersenne_twister()
    
    # Test chaos map
    test_chaos_map()
    
    # Test basic synchronization
    print("\nBasic Synchronization Test:")
    print("-" * 30)
    success, steps, duration = test_tpm_synchronization()
    
    # Test learning rules
    test_learning_rules()
    
    # Run performance tests
    run_performance_test()
    
    print("\n" + "=" * 50)
    print("Test suite completed!")


if __name__ == "__main__":
    main()
