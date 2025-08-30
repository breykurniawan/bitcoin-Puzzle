🔍 Bitcoin Puzzle Private Key Finder
An advanced tool for finding Bitcoin private keys from a set of addresses using an optimized multi-processing brute force approach!

✨ Key Features
🚀 Multi-processing - Utilizes all CPU cores for maximum speed

🎯 Batch Processing - Reduces overhead by processing keys in batches

🔐 Compressed & Uncompressed - Support for searching both address types

📊 Real-time Stats - Displays live search speed and progress

🎨 Colorful UI - Colored interface for better visual experience

💾 Auto-save - Automatically saves found results to file

🛠️ Technology
Python 3 with bit and secrets modules

Multiprocessing for maximum CPU utilization

Cryptographically secure random algorithms

Batch processing optimization to reduce contention

📋 How to Use
Add target Bitcoin addresses to the puzzle.txt file

Configure settings at the top of the script as needed

Run the program: python bitcoin_finder.py

Monitor search progress and speed in real-time

If found, results will be saved to WINNER-COMPRESSED.txt or WINNER-UNCOMPRESSED.txt files

⚙️ Configuration
python
# Number of CPU cores to use
CORES_TO_USE = multiprocessing.cpu_count()

# File containing target addresses
PUZZLE_FILE = "puzzle.txt"

# Range of private keys to search
MIN_KEY = 2**30
MAX_KEY = 2**31 - 1

# Batch processing size
BATCH_SIZE = 80000

# Search mode (True for compressed only)
SEARCH_COMPRESSED_ONLY = True
📈 Performance
With default configuration, the program can process:

Hundreds of thousands of keys/second depending on CPU specifications

100% CPU utilization on all available cores

Safe and efficient search with minimal overhead

🎯 Use Cases
Bitcoin puzzle solving

Educational purposes

Cryptographic research

if you want to share coffee for me just send it to [bc1qm46n3zvwtywfr7ufdeksnhztw9a95pj2pj08qa](https://btcscan.org/address/bc1qm46n3zvwtywfr7ufdeksnhztw9a95pj2pj08qa)


Security analysis

⚠️ Important Note
This program is intended for educational and research purposes only. Use for illegal activities is strongly discouraged. Success in finding matching keys heavily depends on luck and computational power.
