# Neural Cryptography: Tree-like Parity Machine Implementation

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-3.2+-green.svg)](https://djangoproject.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Research](https://img.shields.io/badge/Research-Cybersecurity-red.svg)](https://github.com/Dmitrijg24k/WebTPM)

## 🔬 Scientific Overview

This repository presents a comprehensive implementation of **Tree-like Parity Machines (TPMs)** for neural cryptography and secure key exchange protocols. TPMs represent a novel approach to cryptographic key generation using neural networks, offering potential advantages in quantum-resistant cryptography and secure communication systems.

### Key Research Contributions

- **Neural Synchronization Protocol**: Implementation of the Hebbian, Anti-Hebbian, and Random Walk learning rules for TPM synchronization
- **Real-time WebSocket Communication**: Secure key exchange protocol using WebSocket technology
- **Chaos-based Random Number Generation**: Integration of chaotic maps for enhanced cryptographic randomness
- **AES Encryption Integration**: Practical application of synchronized keys for data encryption

## 🏗️ Architecture

```
WebTPM/
├── tpm/                    # Core TPM implementation & user management
│   ├── models.py          # TPM models, User, Sessions
│   ├── consumers.py       # WebSocket TPM synchronization
│   ├── views.py           # TPM web interface & authentication
│   ├── admin.py           # Django admin interface
│   └── templates/         # TPM web templates
├── chat/                  # Real-time communication
│   ├── models.py          # Chat room and message models
│   └── consumers.py       # WebSocket chat implementation
└── WebTPMG/              # Django project configuration
    ├── settings.py        # Project settings
    └── asgi.py           # ASGI configuration
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Django 3.2+
- Node.js (for WebSocket support)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Dmitrijg24k/WebTPM.git
   cd WebTPM
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Main application: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## 🔬 Scientific Implementation

### Tree-like Parity Machine Algorithm

The TPM implementation follows the neural synchronization protocol:

1. **Initialization**: Two TPMs with random weight matrices W ∈ [-L, L]^(K×N)
2. **Input Generation**: Random input vectors X ∈ [-L, L]^(K×N)
3. **Output Computation**: τ = ∏(i=1 to K) sign(∑(j=1 to N) W_ij × X_ij)
4. **Synchronization**: Weight updates only when τ₁ = τ₂
5. **Key Generation**: Synchronized weights form the shared secret key

### Learning Rules

- **Hebbian**: W_ij += X_ij × τ × θ(σ_i, τ) × θ(τ₁, τ₂)
- **Anti-Hebbian**: W_ij -= X_ij × τ × θ(σ_i, τ) × θ(τ₁, τ₂)
- **Random Walk**: W_ij += X_ij × θ(σ_i, τ) × θ(τ₁, τ₂)

### Security Features

- **Chaos-based Randomness**: Logistic map for enhanced entropy
- **AES Encryption**: 128-bit encryption using synchronized keys
- **Session Management**: Secure user session handling
- **WebSocket Security**: Real-time secure communication

## 📊 Research Applications

This implementation serves as a foundation for:

- **Quantum-resistant Cryptography**: TPMs may offer resistance to quantum attacks
- **Neural Network Security**: Exploring neural networks for cryptographic purposes
- **Key Exchange Protocols**: Alternative to traditional public-key cryptography
- **Secure Communication**: Real-time encrypted messaging systems

## 🧪 Experimental Setup

### TPM Parameters
- **K**: Number of hidden units (default: 3)
- **N**: Input dimension per hidden unit (default: 4)
- **L**: Weight range (default: 6)

### Performance Metrics
- Synchronization time
- Key agreement success rate
- Cryptographic strength analysis
- Network convergence properties

## 📚 References

1. Kinzel, W., & Kanter, I. (2002). "Neural cryptography with feedback." *Physical Review E*, 65(5), 056103.
2. Ruttor, A., Kinzel, W., & Kanter, I. (2006). "Dynamics of neural cryptography." *Physical Review E*, 75(5), 056104.
3. Allam, A. M., & Abbas, H. M. (2011). "Neural cryptography with feedback." *IEEE Transactions on Neural Networks*, 22(5), 850-855.

## 🤝 Contributing

We welcome contributions to this research project! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Areas for Contribution
- Algorithm optimization
- Security analysis
- Performance improvements
- Documentation enhancement
- Additional learning rules

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Dmitrijg24k** - *Lead Researcher & Developer* - [GitHub](https://github.com/Dmitrijg24k)
