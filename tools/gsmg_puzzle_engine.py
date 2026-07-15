#!/usr/bin/env python3
"""
GSMG Puzzle Engine - Reconstruction & Verification Tool
Recreates the puzzle structure and validates solution methodology
"""

import os
import base64
import itertools
import hashlib
import json
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF1, PBKDF2
from Crypto.Hash import SHA256
from typing import List, Tuple, Optional, Dict

class GSMGPhase:
    """Base class for GSMG puzzle phases"""
    
    def __init__(self, phase_num: int, kdf_type: str, segments: List[str]):
        self.phase_num = phase_num
        self.kdf_type = kdf_type  # 'PBKDF1' or 'PBKDF2'
        self.segments = segments
        self.salt = os.urandom(8)  # Salted__ header + 8 bytes
        
    def derive_key_iv(self, password: str, salt: bytes) -> Tuple[bytes, bytes]:
        """Derive key and IV based on phase's KDF"""
        if self.kdf_type == 'PBKDF1':
            # Phase 2 & 3 used PBKDF1 with SHA256
            key_iv = PBKDF1(password.encode(), salt, 32 + 16, 1000, SHA256)
        else:  # PBKDF2
            # Phase 4 switched to PBKDF2
            key_iv = PBKDF2(password.encode(), salt, dkLen=48, count=1000, hmac_hash_module=SHA256)
        return key_iv[:32], key_iv[32:48]
    
    def encrypt(self, plaintext: str, password: str) -> bytes:
        """Encrypt data using phase's methodology"""
        key, iv = self.derive_key_iv(password, self.salt)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        # PKCS7 padding
        pad_len = 16 - (len(plaintext) % 16)
        padded = plaintext + chr(pad_len) * pad_len
        
        ciphertext = cipher.encrypt(padded.encode())
        return b'Salted__' + self.salt + ciphertext
    
    def decrypt(self, encrypted_data: bytes, password: str) -> Optional[str]:
        """Attempt decryption with given password"""
        try:
            if encrypted_data[:8] != b'Salted__':
                return None
            
            salt = encrypted_data[8:16]
            ciphertext = encrypted_data[16:]
            
            key, iv = self.derive_key_iv(password, salt)
            cipher = AES.new(key, AES.MODE_CBC, iv)
            
            decrypted = cipher.decrypt(ciphertext)
            
            # Remove PKCS7 padding
            pad_len = decrypted[-1]
            plaintext = decrypted[:-pad_len].decode('utf-8', errors='replace')
            
            return plaintext
        except Exception:
            return None

class GSMGSolver:
    """Main solver engine for GSMG puzzle"""
    
    def __init__(self):
        self.phases = {}
        self.solutions = {}
        
    def add_phase(self, phase: GSMGPhase):
        """Register a puzzle phase"""
        self.phases[phase.phase_num] = phase
        
    def brute_force_phase(self, phase_num: int, encrypted_data: bytes, 
                         progress_callback=None) -> Optional[Tuple[str, str]]:
        """
        Brute force a phase by trying all segment permutations
        Returns (password, decrypted_text) if found, None otherwise
        """
        if phase_num not in self.phases:
            raise ValueError(f"Phase {phase_num} not registered")
        
        phase = self.phases[phase_num]
        segments = phase.segments
        
        total_perms = len(list(itertools.permutations(segments)))
        
        for i, perm in enumerate(itertools.permutations(segments)):
            password = ''.join(perm)
            
            if progress_callback and i % 100 == 0:
                progress_callback(i, total_perms, password)
            
            result = phase.decrypt(encrypted_data, password)
            
            if result and "::==DATA_BLOCK_START==::" in result:
                self.solutions[phase_num] = (password, result)
                return password, result
                
        return None
    
    def verify_solution_chain(self) -> Dict:
        """Verify the complete solution chain is valid"""
        report = {
            'phases_solved': len(self.solutions),
            'chain_valid': False,
            'details': {}
        }
        
        for phase_num, (password, result) in sorted(self.solutions.items()):
            report['details'][f'phase_{phase_num}'] = {
                'password': password,
                'has_delimiter': '::==DATA_BLOCK_START==::' in result,
                'result_preview': result[:200] if len(result) > 200 else result
            }
        
        # Check if all phases solved
        if len(self.solutions) == len(self.phases):
            report['chain_valid'] = True
            
        return report

def create_demo_puzzle():
    """Create a demonstration puzzle following GSMG structure"""
    
    # Phase 2: PBKDF1, 7 segments
    phase2 = GSMGPhase(2, 'PBKDF1', [
        "thekeymaker", "thevenin", "barrow", 
        "matrix", "overlord", "cxb7", "chancellor"
    ])
    
    # Phase 3: PBKDF1, 4 segments (includes spectrogram extract)
    phase3 = GSMGPhase(3, 'PBKDF1', [
        "matrixsumlist", "lastwordsbeforearchichoice",
        "jacquefractal", "FFGPFGGQG3GNpjk6"
    ])
    
    # Phase 4: PBKDF2 (silent switch!), 7 segments
    phase4 = GSMGPhase(4, 'PBKDF2', [
        "TheSeedIsPlanted", "ChoiceIsAnIllusion",
        "MatrixSumList", "LastWordsBeforeArchiChoice",
        "JacqueFractal", "ThereIsNoSpoon", "FFGPFGGQG3GNpjk6"
    ])
    
    solver = GSMGSolver()
    solver.add_phase(phase2)
    solver.add_phase(phase3)
    solver.add_phase(phase4)
    
    return solver

if __name__ == "__main__":
    print("GSMG Puzzle Engine v2.0 - Reconstruction")
    print("=" * 50)
    
    # Demo: Create and verify puzzle structure
    solver = create_demo_puzzle()
    
    print("\nPhase Structure:")
    for num, phase in solver.phases.items():
        perms = len(list(itertools.permutations(phase.segments)))
        print(f"  Phase {num}: {len(phase.segments)} segments, {perms} permutations, KDF={phase.kdf_type}")
    
    print("\nKey Insight:")
    print("  Phase 4 silently switched from PBKDF1 to PBKDF2")
    print("  This was the 'cheat' - solvers with correct passwords would fail")
    print("  because they didn't know the KDF changed")