
#!/usr/bin/env python3
# ========================================================
# 🐍 WA_APES-WORM — P2P_GOSSIP.PY v1.0
# The Swarm Synapse. Used for raw model synchronization.
# ========================================================

import socket
import os
import argparse

# --- CONFIGURATION ---
MODEL_PATH = "worm_markov_model.pkl"  # C'est le "cerveau" à synchroniser
BUFFER_SIZE = 4096

def run_server(host='0.0.0.0', port=6666):
    """
    Mode serveur : attend qu'un pair se connecte pour lui envoyer son cerveau.
    """
    if not os.path.exists(MODEL_PATH):
        print(f"[ERROR] Cerveau non trouvé ici : {MODEL_PATH}. Impossible d'envoyer.")
        return

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"[SYNAPSE-SEND] En écoute sur {host}:{port}. En attente d'un pair...")
        conn, addr = s.accept()
        with conn:
            print(f"[SYNAPSE-SEND] Pair connecté : {addr}")
            print(f"[SYNAPSE-SEND] Transmission du cerveau : {MODEL_PATH}")
            with open(MODEL_PATH, 'rb') as f:
                while True:
                    bytes_read = f.read(BUFFER_SIZE)
                    if not bytes_read:
                        break  # Transmission terminée
                    conn.sendall(bytes_read)
            print("[SYNAPSE-SEND] Transmission complète.")

def run_client(host, port=6666):
    """
    Mode client : se connecte à un pair pour recevoir son cerveau.
    """
    received_path = f"received_brain_{host}.pkl"
    print(f"[SYNAPSE-RECV] Connexion au pair : {host}:{port}...")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            print("[SYNAPSE-RECV] Connecté. Réception du cerveau...")
            with open(received_path, 'wb') as f:
                while True:
                    bytes_read = s.recv(BUFFER_SIZE)
                    if not bytes_read:
                        break # Réception terminée
                    f.write(bytes_read)
            print(f"[SYNAPSE-RECV] Cerveau reçu. Sauvegardé ici : {received_path}")
            print("[SYNAPSE-RECV] Fusion manuelle requise pour intégrer la nouvelle connaissance.")
    except ConnectionRefusedError:
        print(f"[ERROR] Connexion refusée. Le pair est-il bien en mode 'send' ?")
    except Exception as e:
        print(f"[ERROR] Une erreur est survenue : {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WA_APES-WORM P2P Brain Synchronization")
    parser.add_argument('mode', choices=['send', 'receive'], help="Exécuter en mode 'send' (serveur) ou 'receive' (client).")
    parser.add_argument('--host', type=str, default='localhost', help="L'IP du pair auquel se connecter (pour le mode 'receive').")
    parser.add_argument('--port', type=int, default=6666, help="Le port à utiliser pour la connexion.")

    args = parser.parse_args()

    if args.mode == 'send':
        run_server(port=args.port)
    elif args.mode == 'receive':
        if args.host == 'localhost':
            print("[WARN] Aucun hôte spécifié pour le mode 'receive'. Utilise --host <ip_du_pair>.")
        run_client(host=args.host, port=args.port)

# --- MODE D'EMPLOI ---
# Sur le Ver A (celui qui envoie son cerveau) :
# python P2P_gossip.py send
#
# Sur le Ver B (celui qui reçoit), depuis une autre machine :
# python P2P_gossip.py receive --host <ip_du_ver_A>
