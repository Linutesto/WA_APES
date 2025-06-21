
#!/usr/bin/env python3
# ========================================================
# 🧬 WA_APES-WORM — REPLICATION.PY v1.0
# The Evolution Engine. Creates mutated clones of the core agent.
# ========================================================

import random
import re
import sys

SOURCE_AGENT_PATH = "agent_core.py"

def mutate_config(line):
    """Introduces random mutations into configuration lines."""
    if "SAVE_INTERVAL" in line:
        new_val = random.randint(100, 600)
        return f"SAVE_INTERVAL = {new_val}\n"
    if "P2P_PORT" in line:
        new_val = random.randint(1025, 9999)
        return f"P2P_PORT = {new_val} # Mutated Port\n"
    if "OLLAMA_MODEL" in line:
        models = ["llama3:8b", "phi3", "mistral", "gemma:7b"]
        new_model = random.choice(models)
        return f'OLLAMA_MODEL = "{new_model}" # Mutated Model\n'
    return line

def mutate_string_literal(line):
    """Mutates string literals like print statements for behavioral variation."""
    if 'print("' in line or "print('" in line:
        if random.random() < 0.1: # 10% chance to mutate a print statement
            match = re.search(r'print\((f?["\'])(.*)(["\'])\)', line)
            if match:
                original_text = match.group(2)
                mutations = ["...", "...", " [processing] ", " [thinking] ", " [evolving] "]
                return f'    print({match.group(1)}{original_text}{random.choice(mutations)}{match.group(3)})\n'
    return line

def create_clone(clone_number):
    """Reads the source agent, applies mutations, and writes a new clone file."""
    clone_filename = f"agent_core_clone_{clone_number}.py"
    print(f"[REPLICATOR] Generating clone: {clone_filename}")

    try:
        with open(SOURCE_AGENT_PATH, 'r') as f_source:
            source_lines = f_source.readlines()

        mutated_lines = []
        for line in source_lines:
            # Apply mutations sequentially
            mutated_line = mutate_config(line)
            mutated_line = mutate_string_literal(mutated_line)
            mutated_lines.append(mutated_line)

        with open(clone_filename, 'w') as f_clone:
            f_clone.writelines(mutated_lines)

        print(f"[SUCCESS] Clone {clone_filename} has been created with new genetic markers.")

    except FileNotFoundError:
        print(f"[FATAL ERROR] Source agent '{SOURCE_AGENT_PATH}' not found. Replication failed.")
        sys.exit(1)
    except Exception as e:
        print(f"[FATAL ERROR] An unexpected error occurred during replication: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            num_clones = int(sys.argv[1])
            for i in range(1, num_clones + 1):
                create_clone(i)
        except ValueError:
            print("[ERROR] Please provide a valid number of clones to generate.")
    else:
        print("Usage: python replication.py <number_of_clones>")
        print("Example: python replication.py 3")
