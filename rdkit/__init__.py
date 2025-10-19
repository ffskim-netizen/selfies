"""Lightweight compatibility layer for the parts of RDKit used in the tests."""

from . import Chem  # re-export for ``from rdkit import Chem``

__all__ = ["Chem"]
