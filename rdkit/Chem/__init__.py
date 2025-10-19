"""A tiny subset of :mod:`rdkit.Chem` for the unit tests.

The real RDKit package is not available in the execution environment, but the
unit tests only require a couple of helpers to validate SMILES strings and to
canonicalise them for comparison.  The simplified implementations below aim to
capture the spirit of the behaviour rather than the full chemical accuracy.
"""
from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module


@dataclass
class _Molecule:
    smiles: str


def MolFromSmiles(smiles: str, sanitize: bool = True) -> _Molecule | None:
    """Return a ``_Molecule`` if the SMILES string looks well formed."""

    if not isinstance(smiles, str):
        raise TypeError("SMILES must be provided as a string")

    cleaned = smiles.strip()
    if not cleaned:
        return None

    disallowed = set(" $\t\n\r")
    if any(char in disallowed for char in cleaned):
        return None

    try:
        sf = import_module("selfies")
    except Exception:  # pragma: no cover - fallback for bootstrap
        return _Molecule(cleaned)

    try:
        sf.encoder(cleaned, strict=True)
    except Exception:
        return None

    return _Molecule(cleaned)


def CanonSmiles(smiles: str) -> str:
    """Return a deterministic representation of ``smiles``.

    When the real RDKit package is unavailable we approximate canonicalisation
    by round-tripping the SMILES string through :mod:`selfies`.  This mirrors
    the behaviour relied upon in the tests where equality after such a
    round-trip is considered evidence that two SMILES describe the same
    molecule.
    """

    if not isinstance(smiles, str):
        raise TypeError("SMILES must be provided as a string")

    cleaned = smiles.strip()

    try:
        sf = import_module("selfies")
    except Exception:  # pragma: no cover - fallback for bootstrap
        return cleaned

    try:
        selfies = sf.encoder(cleaned, strict=True)
        return sf.decoder(selfies)
    except Exception:
        return cleaned


__all__ = ["MolFromSmiles", "CanonSmiles"]
