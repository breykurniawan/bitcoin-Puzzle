import secrets
import multiprocessing
import sys
from time import time, sleep
from datetime import datetime, timedelta
from bit import Key

# ==============================================================================
# CONFIGURATION
# ==============================================================================

# Set number of CPU cores/processors to use
# multiprocessing.cpu_count() will use all available cores
CORES_TO_USE = multiprocessing.cpu_count()

# File containing list of Bitcoin Puzzle addresses to search for
PUZZLE_FILE = "puzzle.txt"

# Private key search range (in integer form)
MIN_KEY = 2**30
MAX_KEY = 2**31 - 1

# ==============================================================================
# NEW OPTIMIZATION CONFIGURATION
# ==============================================================================

# OPTIMIZATION 1: BATCH PROCESSING
# Each worker will process this number of keys before updating the main counter
# Higher values reduce lock overhead, increase speed
# Good values between 1000 to 5000
BATCH_SIZE = 80000

# OPTIMIZATION 2: COMPRESSED ADDRESS ONLY
# Set to True to only search compressed addresses (almost 2x faster)
# Set to False to search both compressed AND uncompressed addresses
SEARCH_COMPRESSED_ONLY = True

# ==============================================================================
# COLOR DEFINITIONS & HELPER FUNCTIONS
# ==============================================================================

C_CYAN = '\033[36m'
C_RED = '\033[31m'
C_GREEN = '\033[32m'
C_RESET = '\033[0;0;39m'

def format_time(seconds):
    """Convert seconds to easy-to-read HH:MM:SS format"""
    return str(timedelta(seconds=int(seconds)))

# ==============================================================================
# OPTIMIZED WORKER FUNCTIONS
# ==============================================================================

def worker(puzzle_addresses, found_flag, key_counter, lock):
    """
    Worker optimized with batch processing
    """
    pid = multiprocessing.current_process().pid
    print(f"{C_CYAN}[WORKER {pid}] Starting work... Compressed-Only Mode: {SEARCH_COMPRESSED_ONLY}{C_RESET}")

    while not found_flag.value:
        # Local loop for batch processing
        for i in range(BATCH_SIZE):
            try:
                # 1. Generate random private key
                random_int = secrets.randbelow(MAX_KEY - MIN_KEY) + MIN_KEY
                key = Key.from_int(random_int)

                # 2. Check compressed address (always done)
                caddr = key.address
                if caddr in puzzle_addresses:
                    handle_found(caddr, key, random_int, True, found_flag, lock, pid)
                    return # Stop this worker

                # 3. If allowed, check uncompressed address
                if not SEARCH_COMPRESSED_ONLY:
                    key.compressed = False
                    uaddr = key.address
                    if uaddr in puzzle_addresses:
                        handle_found(uaddr, key, random_int, False, found_flag, lock, pid)
                        return # Stop this worker

            except Exception as e:
                # If error on one key, skip and continue batch
                print(f"{C_RED}[WORKER {pid}] Error encountered: {e}, continuing...{C_RESET}")
                continue
        
        # After completing one batch, update main counter ONLY ONCE
        with key_counter.get_lock():
            key_counter.value += BATCH_SIZE

def handle_found(found_addr, key_obj, int_val, is_compressed, found_flag, lock, pid):
    """Centralized function to handle when a key is found"""
    # Set flag to stop all other workers
    found_flag.value = 1

    key_obj.compressed = is_compressed
    wif = key_obj.to_wif()
    private_key_hex = key_obj.to_hex()
    wif_type = "Compressed" if is_compressed else "Uncompressed"

    with lock:
        print(f"\n\n{C_GREEN}🎉🎉🎉 CONGRATULATIONS! KEY FOUND BY WORKER {pid}! 🎉🎉🎉{C_RESET}")
        print(f"  {C_GREEN}Address  : {C_RESET}{found_addr}")
        print(f"  {C_GREEN}WIF ({wif_type}): {C_RESET}{wif}")
        print(f"  {C_GREEN}Hex Key : {C_RESET}{private_key_hex}")

        file_name = f"WINNER-{wif_type.upper()}.txt"
        with open(file_name, "a") as f:
            f.write(f"Address: {found_addr}\n")
            f.write(f"WIF: {wif}\n")
            f.write(f"Hex: {private_key_hex}\n")
            f.write(f"Int: {int_val}\n")
            f.write("-" * 20 + "\n")

# ==============================================================================
# MAIN & ORCHESTRATION FUNCTIONS
# ==============================================================================

def main():
    start_time = time()
    try:
        with open(PUZZLE_FILE, "r") as m:
            puzzle_addresses = set(m.read().split())
        if not puzzle_addresses:
            print(f"{C_RED}Error: File '{PUZZLE_FILE}' is empty or not found.{C_RESET}")
            return
        print(f"{C_GREEN}Successfully loaded {len(puzzle_addresses)} addresses from '{PUZZLE_FILE}'.{C_RESET}")
    except FileNotFoundError:
        print(f"{C_RED}Error: File '{PUZZLE_FILE}' not found.{C_RESET}")
        return

    # OPTIMIZATION 3: Using Value as flag, lighter than Manager.Event
    found_flag = multiprocessing.Value('i', 0) # 'i' for integer, 0=False, 1=True
    key_counter = multiprocessing.Value('L', 0)
    lock = multiprocessing.Lock() # Lock for file writing, standard is sufficient

    print(f"{C_CYAN}Starting {CORES_TO_USE} search processes with batch size {BATCH_SIZE}...{C_RESET}")
    
    processes = []
    for _ in range(CORES_TO_USE):
        p = multiprocessing.Process(target=worker, args=(puzzle_addresses, found_flag, key_counter, lock))
        processes.append(p)
        p.start()

    try:
        while not found_flag.value:
            sleep(1)
            elapsed_time = time() - start_time
            if elapsed_time == 0: continue
            current_keys = key_counter.value
            keys_per_second = current_keys / elapsed_time
            
            status_line = (
                f"{C_CYAN}Elapsed Time: {C_RESET}{format_time(elapsed_time)} | "
                f"{C_CYAN}Total Keys: {C_RESET}{current_keys:,} | "
                f"{C_GREEN}Speed: {C_RESET}{keys_per_second:,.2f} keys/second"
                f"{C_RESET}"
            )
            sys.stdout.write('\r' + status_line + ' ' * 20)
            sys.stdout.flush()

    except KeyboardInterrupt:
        print(f"\n{C_RED}Search stopped by user.{C_RESET}")
        found_flag.value = 1 # Send stop signal
    finally:
        print(f"{C_CYAN}Waiting for all worker processes to finish...{C_RESET}")
        for p in processes:
            p.join(timeout=5)
            if p.is_alive():
                p.terminate()

        total_time = time() - start_time
        print(f"\n{C_GREEN}Program completed. Total runtime: {format_time(total_time)}{C_RESET}")


if __name__ == '__main__':
    main()
