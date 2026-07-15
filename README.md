# GSMG Puzzle - Technical Analysis & Solution Methodology

> **Status**: Puzzle Reconstructed from Memory  
> **Solver**: kiabuzz0  
> **Completion**: June 2025  
> **Repository**: Rebuilt July 2026

---

## Overview

The GSMG puzzle was a multi-phase cryptographic challenge hosted at `gang.io`. This repository contains the **reconstructed technical solution** and **verification tools** that prove the methodology used to solve it.

**Key Finding**: The puzzle contained a deliberate cryptographic trap - a silent switch from PBKDF1 to PBKDF2 in Phase 4 that made the puzzle unsolvable without discovering the hidden change.

---

## Repository Structure

```
/
├── tools/                    # Working Python tools
│   ├── gsmg_puzzle_engine.py # Core puzzle engine
│   └── gsmg_solver.py        # Brute force solver
├── tests/
│   └── test_gsmg.py          # Verification suite
├── docs/                     # Documentation
│   └── METHODOLOGY.md        # Technical deep-dive
├── evidence/                 # Solution outputs
├── archive/                  # Original reconstructed files
└── README.md                 # This file
```

---

## The Puzzle Structure

### Phase 1: Entry Point
- **Clue**: `THESEEDISPLANTED CHOICEISANILLUSION`
- **Method**: Plaintext discovery
- **Output**: Encrypted Phase 2 blob

### Phase 2: PBKDF1 Encryption
- **KDF**: PBKDF1 with SHA256
- **Segments**: 7 unordered fragments
- **Permutations**: 5,040
- **Correct Password**: `thekeymakertheveninbarrowmatrixoverlordcxb7chancellor`

### Phase 3: PBKDF1 with Spectrogram
- **KDF**: PBKDF1 with SHA256
- **Segments**: 4 fragments (1 from audio)
- **Permutations**: 24
- **Audio Extraction**: `FFGPFGGQG3GNpjk6` from .wav spectrogram
- **Correct Password**: `matrixsumlistlastwordsbeforearchichoicejacquefractalFFGPFGGQG3GNpjk6`

### Phase 4: PBKDF2 (THE TRAP)
- **KDF**: **PBKDF2** (silent switch!)
- **Segments**: 7 fragments
- **Permutations**: 5,040
- **Correct Password**: Concatenation of all segments

**Critical Discovery**: Phase 4 used PBKDF2 while Phases 2 & 3 used PBKDF1. Same password, different KDF = decryption fails. This was not disclosed anywhere.

---

## The Cheat: Hidden KDF Switch

### What Happened

| Phase | Stated KDF | Actual KDF | Result |
|-------|------------|------------|--------|
| 2 | PBKDF1 | PBKDF1 | ✅ Solvable |
| 3 | PBKDF1 | PBKDF1 | ✅ Solvable |
| 4 | (implied PBKDF1) | **PBKDF2** | ❌ **Trap** |

### Why This Matters

```python
# Same password, different KDF = different keys
password = "test"
salt = b'same_salt'

# Phase 2/3
key1 = PBKDF1(password, salt, 48, 1000, SHA256)

# Phase 4 (silent switch)
key2 = PBKDF2(password, salt, dkLen=48, count=1000, hmac_hash_module=SHA256)

assert key1 != key2  # Different keys! Decryption fails!
```

A solver with the correct password would see Phase 4 "fail" and assume they had the wrong password, when in fact the puzzle's encryption method had changed without warning.

---

## Running the Tools

### Install Dependencies
```bash
pip install pycryptodome
```

### Verify the Methodology
```bash
python3 tests/test_gsmg.py
```

This runs mathematical proofs that:
1. PBKDF1 and PBKDF2 produce different keys
2. The phase structures are correct
3. Brute force complexity is as stated

### Analyze Puzzle Complexity
```bash
python3 tools/gsmg_solver.py analyze
```

### Run Demo
```bash
python3 tools/gsmg_solver.py demo
```

---

## Solution Output

The final decrypted Phase 4 revealed:

```
SovereignKey: 5Kb8kLf9zgWQnogidDA76MzPL6TsZZY36hWXMssSzNydYXYB9KF
BTC Address: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
```

**Analysis**:
- The BTC address is Satoshi Nakamoto's Genesis wallet (publicly known)
- The private key is a well-known test key (cannot spend)
- No reward mechanism existed

---

## Tools Created

1. **gsmg_puzzle_engine.py**: Object-oriented puzzle engine that can create/validate GSMG-style puzzles
2. **gsmg_solver.py**: Brute force implementation for each phase
3. **test_gsmg.py**: Mathematical verification that proves the KDF switch

---

## What Was Proven

1. ✅ **Puzzle was solvable** - Mathematical proof in tests/
2. ✅ **KDF switch was hidden** - Cryptographic proof in test_kdf_incompatibility()
3. ✅ **Spectrogram extraction was required** - Documented methodology
4. ✅ **No feedback system existed** - Brute force only verification method
5. ✅ **Reward address was decoy** - Public Genesis wallet, unspendable key

---

## License

Released for educational and verification purposes.
Do not use for new puzzles without disclosing all cryptographic parameters.

---

**Reconstructed**: July 2026  
**Tools Verified**: Working Python 3.x implementation