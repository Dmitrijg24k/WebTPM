"""
TPM WebSocket Consumer

Handles real-time TPM synchronization between client and server machines.
"""

import json
import logging
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import numpy as np
import random
import time
from typing import Dict, Any, Optional, Tuple

from .models import Sessions, User
from django.db.models import Q
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES

logger = logging.getLogger('tpm')


class MersenneTwisterRNG:
    """
    Mersenne Twister pseudo-random number generator implementation.
    
    This implementation provides high-quality random numbers for TPM
    weight initialization and input vector generation. The Mersenne
    Twister has a period of 2^19937-1 and passes many statistical tests.
    
    Reference: Matsumoto, M., & Nishimura, T. (1998). Mersenne twister:
    a 623-dimensionally equidistributed uniform pseudo-random number generator.
    ACM Transactions on Modeling and Computer Simulation, 8(1), 3-30.
    """
    
    def __init__(self, seed: int = 5489):
        """
        Initialize the Mersenne Twister with a seed value.
        
        Args:
            seed: Initial seed value for the generator
        """
        self.state = [0] * 624
        self.f = 1812433253  # Multiplier
        self.m = 397         # Middle word offset
        self.u = 11          # Tempering bit shift
        self.s = 7           # Tempering bit shift
        self.b = 0x9D2C5680  # Tempering bit mask
        self.t = 15          # Tempering bit shift
        self.c = 0xEFC60000  # Tempering bit mask
        self.l = 18          # Tempering bit shift
        self.index = 624     # Current state index
        self.lower_mask = (1 << 31) - 1  # Lower 31 bits
        self.upper_mask = 1 << 31        # Upper bit

        # Initialize state array
        self.state[0] = seed
        for i in range(1, 624):
            self.state[i] = self._int_32(
                self.f * (self.state[i-1] ^ (self.state[i-1] >> 30)) + i
            )

    def _twist(self) -> None:
        """Generate the next 624 values in the sequence."""
        for i in range(624):
            temp = self._int_32(
                (self.state[i] & self.upper_mask) + 
                (self.state[(i + 1) % 624] & self.lower_mask)
            )
            temp_shift = temp >> 1
            if temp % 2 != 0:
                temp_shift = temp_shift ^ 0x9908b0df
            self.state[i] = self.state[(i + self.m) % 624] ^ temp_shift
        self.index = 0

    def get_random_number(self) -> int:
        """
        Generate the next random number in the sequence.
        
        Returns:
            A 32-bit random integer
        """
        if self.index >= 624:
            self._twist()
        
        y = self.state[self.index]
        y = y ^ (y >> self.u)
        y = y ^ ((y << self.s) & self.b)
        y = y ^ ((y << self.t) & self.c)
        y = y ^ (y >> self.l)
        self.index += 1
        return self._int_32(y)

    def _int_32(self, number: int) -> int:
        """Ensure the number fits in 32 bits."""
        return int(0xFFFFFFFF & number)


class TreeParityMachine:
    """
    Tree-like Parity Machine implementation for neural cryptography.
    
    A TPM is a neural network with K hidden units, each receiving N inputs.
    The network computes a binary output based on the product of hidden unit
    activations, enabling secure key exchange through synchronization.
    
    Reference: Kinzel, W., & Kanter, I. (2002). Neural cryptography with feedback.
    Physical Review E, 65(5), 056103.
    """
    
    def __init__(self, k: int = 3, n: int = 4, l: int = 6):
        """
        Initialize a Tree-like Parity Machine.
        
        Args:
            k: Number of hidden units
            n: Input dimension per hidden unit
            l: Weight range [-l, l]
        """
        self.k = k
        self.n = n
        self.l = l
        # Initialize weight matrix with random values in [-l, l]
        self.W = np.random.randint(-l, l + 1, [k, n], dtype=np.int32)
        
        # Internal state variables
        self.X = None
        self.sigma = None
        self.tau = None

    def get_output(self, X: np.ndarray) -> int:
        """
        Compute the TPM output for a given input vector.
        
        The output is computed as:
        τ = ∏(i=1 to K) sign(∑(j=1 to N) W_ij × X_ij)
        
        Args:
            X: Input vector of shape (K, N)
            
        Returns:
            Binary output τ ∈ {-1, 1}
        """
        X = X.reshape([self.k, self.n])
        
        # Compute inner activations for each hidden unit
        sigma = np.sign(np.sum(X * self.W, axis=1))
        
        # Compute final output as product of hidden unit activations
        tau = np.prod(sigma)
        
        # Store state for potential weight updates
        self.X = X
        self.sigma = sigma
        self.tau = tau
        
        return int(tau)

    def __call__(self, X: np.ndarray) -> int:
        """Allow the TPM to be called as a function."""
        return self.get_output(X)

    def update(self, tau2: int, update_rule: str = 'hebbian') -> None:
        """
        Update weights according to the specified learning rule.
        
        Weight updates only occur when both machines produce the same output
        (τ₁ = τ₂), ensuring synchronization.
        
        Args:
            tau2: Output from the other TPM
            update_rule: Learning rule ('hebbian', 'anti_hebbian', 'random_walk')
        """
        if self.tau != tau2:
            return  # No update if outputs don't match
            
        if update_rule == 'hebbian':
            self._hebbian_update()
        elif update_rule == 'anti_hebbian':
            self._anti_hebbian_update()
        elif update_rule == 'random_walk':
            self._random_walk_update()
        else:
            raise ValueError(
                f"Invalid update rule: {update_rule}. "
                "Valid rules: 'hebbian', 'anti_hebbian', 'random_walk'"
            )

    def _theta(self, t1: int, t2: int) -> int:
        """Indicator function: 1 if t1 == t2, 0 otherwise."""
        return 1 if t1 == t2 else 0

    def _hebbian_update(self) -> None:
        """Hebbian learning rule: strengthen connections that are active together."""
        for (i, j), _ in np.ndenumerate(self.W):
            self.W[i, j] += (
                self.X[i, j] * self.tau * 
                self._theta(self.sigma[i], self.tau) * 
                self._theta(self.tau, self.tau)  # Always 1 when updating
            )
            self.W[i, j] = np.clip(self.W[i, j], -self.l, self.l)

    def _anti_hebbian_update(self) -> None:
        """Anti-Hebbian learning rule: weaken active connections."""
        for (i, j), _ in np.ndenumerate(self.W):
            self.W[i, j] -= (
                self.X[i, j] * self.tau * 
                self._theta(self.sigma[i], self.tau) * 
                self._theta(self.tau, self.tau)
            )
            self.W[i, j] = np.clip(self.W[i, j], -self.l, self.l)

    def _random_walk_update(self) -> None:
        """Random walk learning rule: random weight changes."""
        for (i, j), _ in np.ndenumerate(self.W):
            self.W[i, j] += (
                self.X[i, j] * 
                self._theta(self.sigma[i], self.tau) * 
                self._theta(self.tau, self.tau)
            )
            self.W[i, j] = np.clip(self.W[i, j], -self.l, self.l)

    def chaos_map(self) -> float:
        """
        Generate a chaotic value based on the current weight matrix.
        
        This method uses a logistic map to generate chaotic values for
        additional randomness in the synchronization process.
        
        Returns:
            Chaotic value in [0, 1]
        """
        r = np.sum(self.W)
        rr = np.sum(np.abs(self.W))
        
        if rr == 0:
            return 0.5  # Default value if all weights are zero
            
        t = abs(r) / rr
        x = t
        
        # Apply logistic map iterations
        for _ in range(int(rr)):
            x = (3.6 + t/2) * x * (1 - x)
            
        return x

    def is_synchronized_with(self, other: 'TreeParityMachine', 
                           test_inputs: int = 100) -> bool:
        """
        Test if this TPM is synchronized with another TPM.
        
        Args:
            other: Another TPM to test synchronization with
            test_inputs: Number of random inputs to test
            
        Returns:
            True if synchronized, False otherwise
        """
        for _ in range(test_inputs):
            X = np.random.randint(-self.l, self.l + 1, [self.k, self.n])
            if self.get_output(X) != other.get_output(X):
                return False
        return True


def generate_random_vector(seed: int, L: int, K: int, N: int) -> np.ndarray:
    """
    Generate a random input vector for TPM using Mersenne Twister.
    
    Args:
        seed: Random seed for reproducibility
        L: Weight range parameter
        K: Number of hidden units
        N: Input dimension per hidden unit
        
    Returns:
        Random vector of shape (K, N) with values in [-L, L]
    """
    generator = MersenneTwisterRNG(seed)
    
    result = np.empty((K, N), dtype=np.int32)
    for i in range(K):
        for j in range(N):
            value = generator.get_random_number() % (2 * L)
            if value - L < 0:
                value *= -1
            result[i, j] = value
    return result


def generate_seed() -> int:
    """Generate a random seed for TPM initialization."""
    return random.randint(0, 10000)


class TpmConsumer(WebsocketConsumer):
    """
    WebSocket consumer for Tree-like Parity Machine synchronization.
    
    This consumer handles real-time communication between client and server
    TPMs, managing the neural cryptography protocol including parameter
    exchange, synchronization steps, and key generation.
    """
    
    def connect(self):
        """Accept WebSocket connection and initialize TPM state."""
        self.accept()
        logger.info(f"TPM WebSocket connection established: {self.scope['user']}")
        
        # Initialize TPM state
        self.server_tpm = None
        self.sync_steps = 0
        self.max_sync_steps = 1000  # Prevent infinite loops
        
    def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        logger.info(f"TPM WebSocket disconnected: {self.scope['user']}, code: {close_code}")
    
    def receive(self, text_data: str):
        """
        Handle incoming WebSocket messages.
        
        Args:
            text_data: JSON string containing message data
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'ClientReadySync':
                self._handle_client_ready()
            elif message_type == 'GetParameters':
                self._handle_get_parameters(data)
            elif message_type == 'GetResultClient':
                self._handle_client_result(data)
            else:
                logger.warning(f"Unknown message type: {message_type}")
                self._send_error("Unknown message type")
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
            self._send_error("Invalid JSON format")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            self._send_error("Internal server error")
    
    def _handle_client_ready(self):
        """Handle client ready for synchronization."""
        self.send(text_data=json.dumps({
            'type': 'ServerReadySync',
            'message': 'Server is ready for TPM synchronization'
        }))
        logger.info("Client ready for synchronization")
    
    def _handle_get_parameters(self, data: Dict[str, Any]):
        """Handle TPM parameter initialization."""
        try:
            self.k = int(data['k'])
            self.n = int(data['n'])
            self.l = int(data['l'])
            
            # Validate parameters
            if not (1 <= self.k <= 20 and 1 <= self.n <= 20 and 1 <= self.l <= 50):
                raise ValueError("Invalid TPM parameters")
            
            # Initialize server TPM
            self.server_tpm = TreeParityMachine(self.k, self.n, self.l)
            self.sync_steps = 0
            
            # Generate initial input vector
            self.seed = generate_seed()
            self.server_tpm.X = generate_random_vector(self.seed, self.l, self.k, self.n)
            
            self.send(text_data=json.dumps({
                'type': 'GetFirstSeed',
                'seed': self.seed,
                'vector': self.server_tpm.X.tolist()
            }))
            
            logger.info(f"TPM initialized: K={self.k}, N={self.n}, L={self.l}")
            
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Invalid parameters: {e}")
            self._send_error("Invalid TPM parameters")
    
    def _handle_client_result(self, data: Dict[str, Any]):
        """Handle client TPM result and perform synchronization step."""
        if not self.server_tpm:
            self._send_error("TPM not initialized")
            return
            
        try:
            client_result = int(data['resultClient'])
            client_chaos = float(data.get('chaosmap', 0))
            
            # Compute server result
            server_result = self.server_tpm.get_output(self.server_tpm.X)
            server_chaos = self.server_tpm.chaos_map()
            
            # Generate next input vector
            self.seed = generate_seed()
            self.server_tpm.X = generate_random_vector(self.seed, self.l, self.k, self.n)
            
            self.sync_steps += 1
            
            # Check for synchronization
            if (server_result == client_result and 
                abs(server_chaos - client_chaos) < 0.001):
                self._handle_synchronization_complete()
            else:
                # Update weights and continue
                self.server_tpm.update(client_result, 'hebbian')
                self._send_sync_step(server_result, server_chaos)
                
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Invalid client result: {e}")
            self._send_error("Invalid client result")
    
    def _handle_synchronization_complete(self):
        """Handle successful TPM synchronization."""
        try:
            # Generate session key from synchronized weights
            session_key = self._generate_session_key()
            
            # Create session record
            session = Sessions(sessionKey=session_key)
            session.save()
            
            # Update user session
            current_session = self.scope["user"].sessionId
            self.scope["user"].sessionId = session
            self.scope["user"].save(update_fields=['sessionId'])
            
            # Clean up old session
            if current_session:
                current_session.delete()
            
            # Session key generated successfully
            
            self.send(text_data=json.dumps({
                'type': 'FinishSync',
                'message': 'TPM synchronization completed successfully',
                'sync_steps': self.sync_steps,
                'session_key': session_key
            }))
            
            logger.info(f"TPM synchronization completed in {self.sync_steps} steps")
            
        except Exception as e:
            logger.error(f"Error completing synchronization: {e}")
            self._send_error("Synchronization completion failed")
    
    def _generate_session_key(self) -> str:
        """Generate session key from synchronized weight matrix."""
        key_elements = []
        for row in self.server_tpm.W:
            for weight in row:
                key_elements.append(str(weight + 100))  # Offset to ensure positive
        return ''.join(key_elements)
    
    
    def _get_encryption_key(self) -> bytes:
        """Generate encryption key from TPM weights."""
        key_elements = []
        for row in self.server_tpm.W:
            for weight in row:
                key_elements.append(weight + 100)
        return bytes(key_elements[:16])  # Use first 16 elements for 128-bit key
    
    def _send_sync_step(self, server_result: int, server_chaos: float):
        """Send synchronization step data to client."""
        self.send(text_data=json.dumps({
            'type': 'GetSeedAndResultTrue',
            'seed': self.seed,
            'vector': self.server_tpm.X.tolist(),
            'result': server_result,
            'chaosmap': server_chaos,
            'sync_steps': self.sync_steps
        }))
    
    def _send_error(self, message: str):
        """Send error message to client."""
        self.send(text_data=json.dumps({
            'type': 'Error',
            'message': message
        }))
    







