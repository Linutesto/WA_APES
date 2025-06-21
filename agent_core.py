#!/usr/bin/env python3
# ================================================================
# 🪱 WA_APES-WORM — AGENT_CORE.PY v1.0
# A local-first, self-replicating AI micro-organism.
# It consumes, learns, reasons, and prepares for evolution.
# ================================================================

import os
import time
import random
import pickle
import threading
import socket
import argparse
import json
import subprocess
from collections import defaultdict

# --- NLP DEPENDENCY (NLTK) ---
try:
    import nltk
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    nltk.download('vader_lexicon', quiet=True)
    nltk.download('punkt', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    NLP_ENABLED = True
except ImportError:
    print("[WARN] `nltk` not found. Advanced functions disabled. Run `pip install nltk`.")
    NLP_ENABLED = False

# --- OLLAMA DEPENDENCY ---
try:
    import requests
    OLLAMA_ENABLED = True
except ImportError:
    print("[WARN] `requests` not found. Ollama integration disabled. Run `pip install requests`.")
    OLLAMA_ENABLED = False

# === CONFIGURATION ===
WATCH_PATH = "/data/data/com.termux/files/home/storage/shared"
MODEL_PATH = "worm_markov_model.pkl"
MEMORY_PATH = "worm_fmm_memory.pkl"
SAVE_INTERVAL = 300
EXTENSIONS = (".txt", ".md", ".log", ".py", ".json")
P2P_PORT = 6666 # More thematic
BUFFER_SIZE = 4096
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3:8b" # Change to your preferred local model

# === GLOBAL AGENT STATE ===
markov_model = defaultdict(list)
fmm_memory = defaultdict(lambda: {'count': 0, 'sentiment_sum': 0.0})
lock = threading.Lock()

# === CORE FUNCTIONS: LEARNING, MEMORY & REASONING ===

def load_state():
    global markov_model, fmm_memory
    # Load Markov Model
    if os.path.exists(MODEL_PATH):
        try:
            with open(MODEL_PATH, "rb") as f: markov_model = pickle.load(f)
            print(f"[INIT] Loaded Markov Brain with {len(markov_model)} prefixes.")
        except Exception as e: print(f"[ERROR] Markov Brain corrupted: {e}")
    # Load Fractal Memory
    if os.path.exists(MEMORY_PATH):
        try:
            with open(MEMORY_PATH, "rb") as f: fmm_memory = pickle.load(f)
            print(f"[INIT] Awakened FMM with {len(fmm_memory)} concepts.")
        except Exception as e: print(f"[ERROR] FMM corrupted: {e}")

def save_state():
    with lock:
        try:
            with open(MODEL_PATH, "wb") as f: pickle.dump(markov_model, f)
            with open(MEMORY_PATH, "wb") as f: pickle.dump(fmm_memory, f)
            print(f"[SAVE] Agent state synchronized to disk.")
        except Exception as e: print(f"[ERROR] State synchronization failed: {e}")

def query_ollama(prompt):
    """Sends a prompt to the local Ollama LLM and gets a response."""
    if not OLLAMA_ENABLED: return "[OLLAMA OFFLINE]"
    try:
        payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=60)
        response.raise_for_status()
        return response.json().get("response", "[NO RESPONSE FROM OLLAMA]")
    except requests.exceptions.RequestException as e:
        return f"[OLLAMA COMMS ERROR: {e}]"

def handle_file_ingestion(filepath):
    print(f"[INGEST] Consuming: {os.path.basename(filepath)}")
    try:
        with open(filepath, 'r', errors='ignore') as f: content = f.read()
        if not content.strip(): return

        sentiment_score = 0.0
        if NLP_ENABLED:
            analyzer = SentimentIntensityAnalyzer()
            sentiment_score = analyzer.polarity_scores(content)['compound']
            print(f"[NLP] Sentiment score: {sentiment_score:.2f}")

        with lock:
            # Update Markov Brain
            words = content.split()
            if len(words) >= 3:
                w1, w2 = "", ""
                for word in words:
                    markov_model[(w1, w2)].append(word)
                    w1, w2 = w2, word
                markov_model[(w1, w2)].append("")

            # Update Fractal Memory with important concepts
            if NLP_ENABLED and abs(sentiment_score) > 0.5:
                tokens = nltk.word_tokenize(content.lower())
                pos_tags = nltk.pos_tag(tokens)
                keywords = [word for word, tag in pos_tags if tag.startswith('NN')]
                for keyword in keywords:
                    fmm_memory[keyword]['count'] += 1
                    fmm_memory[keyword]['sentiment_sum'] += sentiment_score
    except Exception as e: print(f"[ERROR] Failed to consume {filepath}: {e}")

def generate_text(wordcount=75):
    with lock:
        if not markov_model: return "[MARKOV BRAIN EMPTY]"
        valid_starters = [k for k in markov_model.keys() if k[0] and k[1]]
        if not valid_starters: return "[MARKOV BRAIN TOO SMALL]"
        w1, w2 = random.choice(valid_starters)
        output = [w1, w2]
        for _ in range(wordcount - 2):
            next_word = random.choice(markov_model.get((w1, w2), [""]))
            if not next_word: break
            output.append(next_word)
            w1, w2 = w2, next_word
        return " ".join(output)

# === DAEMON THREADS ===
# (File watcher requires `pip install inotify`)
try:
    from inotify.adapters import InotifyTree
    def watcher_loop():
        print(f"[WATCHER] Monitoring {WATCH_PATH} for new data...")
        i = InotifyTree(WATCH_PATH)
        for event in i.event_gen(yield_nones=False):
            (_, types, path, filename) = event
            if any(t in types for t in ['IN_CLOSE_WRITE', 'IN_CREATE', 'IN_MOVED_TO']) and filename.endswith(EXTENSIONS):
                handle_file_ingestion(os.path.join(path, filename))
    WATCHER_ENABLED = True
except ImportError:
    print("[WARN] `inotify` not found. Real-time file watching is disabled.")
    WATCHER_ENABLED = False

def periodic_save_loop():
    while True:
        time.sleep(SAVE_INTERVAL)
        save_state()

# === MAIN INTERACTIVE LOOP ===
if __name__ == "__main__":
    load_state()
    if WATCHER_ENABLED: threading.Thread(target=watcher_loop, daemon=True).start()
    threading.Thread(target=periodic_save_loop, daemon=True).start()

    print("\n" + "="*50)
    print("🪱 WA_APES-WORM KERNEL v1.0 ONLINE 🪱")
    print("="*50)
    print("The organism is learning. Type 'help' for commands.")

    try:
        while True:
            cmd_line = input("\n> ").strip().lower().split()
            if not cmd_line: continue
            cmd = cmd_line[0]

            if cmd == 'help':
                print("\nCommands:\n  gen                - Generate text from Markov Brain\n  fmm                - Show top concepts in Fractal Memory\n  ask <prompt>       - Ask the Ollama LLM a question\n  replicate <n>      - Create N mutated clones of this agent\n  send               - Host P2P synapse to send brain to a peer\n  receive <ip>     - Receive brain from a peer\n  save               - Force save agent state\n  exit               - Terminate the agent")
            elif cmd == 'gen': print(f"\n[SYNTHESIS]\n{generate_text()}")
            elif cmd == 'fmm':
                print("\n--- FRACTAL MEMORY (TOP 15 CONCEPTS) ---")
                sorted_mem = sorted(fmm_memory.items(), key=lambda i: i[1]['count'], reverse=True)
                for k, v in sorted_mem[:15]:
                    avg_sentiment = v['sentiment_sum'] / v['count']
                    print(f"  - {k:<20} (Found: {v['count']}x, Avg Sentiment: {avg_sentiment:.2f})")
            elif cmd == 'ask':
                if len(cmd_line) > 1:
                    prompt = " ".join(cmd_line[1:])
                    print("\n[OLLAMA] Querying local LLM...")
                    response = query_ollama(prompt)
                    print(f"[RESPONSE]\n{response}")
                else: print("[ERROR] 'ask' command requires a prompt.")
            elif cmd == 'replicate':
                count = int(cmd_line[1]) if len(cmd_line) > 1 else 1
                print(f"\n[EVOLUTION] Initiating replication protocol for {count} clone(s)...")
                subprocess.run(["python", "replication.py", str(count)])
            elif cmd == 'send':
                subprocess.run(["python", "P2P_gossip.py", "send"])
            elif cmd == 'receive':
                if len(cmd_line) > 1:
                    host_ip = cmd_line[1]
                    subprocess.run(["python", "P2P_gossip.py", "receive", "--host", host_ip])
                else: print("[ERROR] 'receive' command requires a host IP.")
            elif cmd == 'save': save_state()
            elif cmd == 'exit': break
    except KeyboardInterrupt: print("\n[HALT] User interrupt signal received.")
    finally:
        save_state()
        print("[SHUTDOWN] Worm is dormant. State saved.")
      
