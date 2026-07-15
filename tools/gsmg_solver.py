#!/usr/bin/env python3
"""
GSMG Brute Force Solver
Implements the actual solving methodology used for each phase
"""

import sys
import itertools
import base64
from typing import List, Tuple, Optional

try:
    from Crypto.Cipher import AES
    from Crypto.Protocol.KDF import PBKDF1, PBKDF2
    from Crypto.Hash import SHA256
except ImportError:
    print("Error: pycryptodome required. Install: pip install pycryptodome")
    sys.exit(1)

class PhaseSolver:
    """Solver for individual GSMG phases"""
    
    @staticmethod
    def try_decrypt_phase2(encrypted_b64: str, segments: List[str]) -> Optional[Tuple[str, str]]:
        """
        Phase 2: PBKDF1 with SHA256, 7 segments
        Correct order: thekeymaker + thevenin + barrow + matrix + overlord + cxb7 + chancellor
        """
        encrypted_data = base64.b64decode(encrypted_b64)
        salt = encrypted_data[8:16]
        ciphertext = encrypted_data[16:]
        
        for perm in itertools.permutations(segments):
            password = ''.join(perm)
            
            # PBKDF1 (Phase 2 & 3)
            key_iv = PBKDF1(password.encode(), salt, 48, 1000, SHA256)
            key = key_iv[:32]
            iv = key_iv[32:]
            
            try:
                cipher = AES.new(key, AES.MODE_CBC, iv)
                decrypted = cipher.decrypt(ciphertext)
                
                # Check for success marker
                if b"::==DATA_BLOCK_START==::" in decrypted:
                    return password, decrypted.decode(errors='replace')
            except Exception:
                continue
        
        return None
    
    @staticmethod
    def try_decrypt_phase3(encrypted_b64: str, segments: List[str]) -> Optional[Tuple[str, str]]:
        """
        Phase 3: PBKDF1 with SHA256, 4 segments
        Includes spectrogram-extracted segment: FFGPFGGQG3GNpjk6
        """
        encrypted_data = base64.b64decode(encrypted_b64)
        salt = encrypted_data[8:16]
        ciphertext = encrypted_data[16:]
        
        for perm in itertools.permutations(segments):
            password = ''.join(perm)
            
            # Still PBKDF1
            key_iv = PBKDF1(password.encode(), salt, 48, 1000, SHA256)
            key = key_iv[:32]
            iv = key_iv[32:]
            
            try:
                cipher = AES.new(key, AES.MODE_CBC, iv)
                decrypted = cipher.decrypt(ciphertext)
                
                if b"::==DATA_BLOCK_START==::" in decrypted:
                    return password, decrypted.decode(errors='replace')
            except Exception:
                continue
        
        return None
    
    @staticmethod
    def try_decrypt_phase4(encrypted_b64: str, segments: List[str]) -> Optional[Tuple[str, str]]:
        """
        Phase 4: PBKDF2 (SILENT SWITCH!), 7 segments
        THIS IS THE KEY INSIGHT - Phase 4 used different KDF
        """
        encrypted_data = base64.b64decode(encrypted_b64)
        salt = encrypted_data[8:16]
        ciphertext = encrypted_data[16:]
        
        for perm in itertools.permutations(segments):
            password = ''.join(perm)
            
            # PBKDF2 - the silent switch that broke solvers
            key_iv = PBKDF2(password.encode(), salt, dkLen=48, count=1000, hmac_hash_module=SHA256)
            key = key_iv[:32]
            iv = key_iv[32:]
            
            try:
                cipher = AES.new(key, AES.MODE_CBC, iv)
                decrypted = cipher.decrypt(ciphertext)
                
                if b"::==DATA_BLOCK_START==::" in decrypted:
                    return password, decrypted.decode(errors='replace')
            except Exception:
                continue
        
        return None

def analyze_complexity():
    """Calculate brute force complexity for each phase"""
    
    phases = {
        'Phase 2': {'segments': 7, 'kdf': 'PBKDF1'},
        'Phase 3': {'segments': 4, 'kdf': 'PBKDF1'},
        'Phase 4': {'segments': 7, 'kdf': 'PBKDF2 (hidden switch)'}
    }
    
    print("GSMG Puzzle Complexity Analysis")
    print("=" * 50)
    
    for name, info in phases.items():
        perms = __import__('math').factorial(info['segments'])
        print(f"\n{name}:")
        print(f"  Segments: {info['segments']}")
        print(f"  Permutations: {perms:,}")
        print(f"  KDF: {info['kdf']}")
        print(f"  Time estimate (1000 attempts/sec): ~{perms/1000/60:.1f} minutes")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("GSMG Solver")
        print("Usage:")
        print("  python3 gsmg_solver.py analyze")
        print("  python3 gsmg_solver.py demo")
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == "analyze":
        analyze_complexity()
    elif command == "demo":
        print("Demo: Showing phase structures...")
        print("\nPhase 2 segments:", ["thekeymaker", "thevenin", "barrow", "matrix", "overlord", "cxb7", "chancellor"])
        print("Phase 3 segments:", ["matrixsumlist", "lastwordsbeforearchichoice", "jacquefractal", "FFGPFGGQG3GNpjk6"])
        print("\nPhase 4 segments (the trap):")
        print(["TheSeedIsPlanted", "ChoiceIsAnIllusion", "MatrixSumList", 
               "LastWordsBeforeArchiChoice", "JacqueFractal", "ThereIsNoSpoon", "FFGPFGGQG3GNpjk6"])
        print("\nNOTE: Phase 4 uses PBKDF2, not PBKDF1 like phases 2 & 3")
        print("Without knowing this switch, correct passwords would fail to decrypt.")