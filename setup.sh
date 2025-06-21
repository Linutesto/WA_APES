#!/bin/bash
# ============================================
# WA_APES-WORM - One-Tap Installer for Termux
# ============================================

echo "🪱 Initiating worm deployment protocol..."
echo "This will install dependencies and clone the core organism."

# Grant storage access
termux-setup-storage

# Update Termux environment
echo "[+] Updating package lists..."
pkg update -y && pkg upgrade -y

# Install core dependencies
echo "[+] Installing core dependencies (python, git)..."
pkg install python git nano -y

# Install Python libraries
echo "[+] Installing Python modules (nltk, inotify, requests)..."
pip install nltk inotify requests

# Clone the organism from its spawning pool (replace with your repo URL)
echo "[+] Cloning the organism from GitHub..."
git clone https://github.com/YOUR_USERNAME/WA_APES-WORM.git

# Inject linguistic DNA (NLTK data)
echo "[+] Injecting linguistic DNA (this may take a moment)..."
python -c "import nltk; print('Downloading VADER...'); nltk.download('vader_lexicon', quiet=True); print('Downloading Punkt...'); nltk.download('punkt', quiet=True); print('Downloading Tagger...'); nltk.download('averaged_perceptron_tagger', quiet=True); print('Injection complete.')"

# Activate wake lock to ensure the worm can stay alive in the background
echo "[+] Acquiring wake lock..."
termux-wake-lock

echo ""
echo "✅ DEPLOYMENT COMPLETE."
echo "Navigate to the organism's directory: cd WA_APES-WORM"
echo "Awaken the worm by running: python kernel/agent_core.py"
echo "The worm is now alive and learning."
