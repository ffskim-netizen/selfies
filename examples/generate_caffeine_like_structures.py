"""Generate SELFIES/SMILES strings similar to caffeine.

This example demonstrates how to use the :mod:`selfies` package to perform
small random mutations on the SELFIES representation of caffeine.  The script
produces a user-configurable number of unique, caffeine-like molecules and
prints both their SELFIES and SMILES strings.
"""
from __future__ import annotations

import argparse
import random
from collections import OrderedDict
from typing import Iterable, List, MutableSequence, Sequence, Tuple

import selfies as sf

CAFFEINE_SMILES = "Cn1cnc2n(C)c(=O)n(C)c(=O)c12"
CAFFEINE_SELFIES = sf.encoder(CAFFEINE_SMILES)

# SELFIES symbols that we will allow our mutations to use.  The list is tuned
# to be chemically close to the motifs already present in caffeine, while still
# allowing for a variety of substitutions that keep the generated structures in
# the same chemical neighbourhood.
_BASE_TOKENS = set(sf.split_selfies(CAFFEINE_SELFIES))
_EXTRA_TOKENS = {
    "[C]",
    "[=C]",
    "[N]",
    "[=N]",
    "[O]",
    "[=O]",
    "[#N]",
    "[#C]",
    "[Branch1]",
    "[Branch2]",
    "[=Branch1]",
    "[=Branch2]",
    "[Ring1]",
    "[=Ring1]",
}
_SEMANTIC_ALPHABET = set(sf.get_semantic_robust_alphabet())
_MUTATION_ALPHABET = sorted(((_BASE_TOKENS | _EXTRA_TOKENS) & _SEMANTIC_ALPHABET))


def _mutate_selfies(
    base_tokens: Sequence[str],
    mutation_alphabet: Sequence[str],
    rng: random.Random,
    max_mutations: int = 2,
) -> List[str]:
    """Return a mutated copy of ``base_tokens``.

    The mutation strategy favours single-token replacements, occasionally
    inserting or deleting a token.  By limiting ourselves to at most two
    mutations, we keep the mutated molecules close to the original caffeine
    scaffold.
    """

    mutated: MutableSequence[str] = list(base_tokens)
    if not mutated:
        return []

    num_mutations = rng.randint(1, max_mutations)

    for _ in range(num_mutations):
        if not mutated:
            # If all tokens were deleted, force an insertion to keep the string
            # non-empty.
            op = "insert"
        else:
            # Bias towards replacements to keep the SELFIES close to caffeine.
            operations = ("replace", "insert", "delete")
            weights = (0.65, 0.2, 0.15)
            op = rng.choices(operations, weights=weights, k=1)[0]

        if op == "replace" and mutated:
            idx = rng.randrange(len(mutated))
            mutated[idx] = rng.choice(mutation_alphabet)
        elif op == "insert":
            idx = rng.randrange(len(mutated) + 1)
            mutated.insert(idx, rng.choice(mutation_alphabet))
        elif op == "delete" and len(mutated) > 1:
            idx = rng.randrange(len(mutated))
            del mutated[idx]
        else:
            # Fall back to a replacement if deletion was not possible (e.g.
            # the SELFIES is too short).
            idx = rng.randrange(len(mutated))
            mutated[idx] = rng.choice(mutation_alphabet)

    return list(mutated)


def generate_caffeine_like_structures(
    count: int,
    seed: int | None = None,
    max_attempts: int | None = None,
) -> "OrderedDict[str, Tuple[str, str]]":
    """Generate ``count`` unique molecules similar to caffeine.

    Parameters
    ----------
    count:
        Number of unique molecules to generate.
    seed:
        Optional random seed for reproducibility.
    max_attempts:
        Optional cap on the number of mutation attempts.  If ``None`` we fall
        back to ``count * 500``.
    """

    rng = random.Random(seed)
    base_tokens = list(sf.split_selfies(CAFFEINE_SELFIES))
    attempts_left = max_attempts or count * 500

    generated: "OrderedDict[str, Tuple[str, str]]" = OrderedDict()

    while len(generated) < count and attempts_left > 0:
        attempts_left -= 1

        mutated_tokens = _mutate_selfies(base_tokens, _MUTATION_ALPHABET, rng)
        if not (
            len(base_tokens) - 3
            <= len(mutated_tokens)
            <= len(base_tokens) + 3
        ):
            # Reject mutations that deviate too much in length from caffeine,
            # which keeps the generated structures in the same size regime.
            continue

        mutated_selfies = "".join(mutated_tokens)

        try:
            mutated_smiles = sf.decoder(mutated_selfies)
        except sf.DecoderError:
            continue

        mutated_smiles = mutated_smiles.strip()
        if not mutated_smiles or mutated_smiles == CAFFEINE_SMILES:
            continue

        if len(mutated_smiles) < len(CAFFEINE_SMILES) - 5:
            # Filter out trivial fragments that are far smaller than
            # caffeine.  The numeric threshold was tuned empirically so that
            # generated structures retain the overall size of caffeine while
            # still allowing for small variations.
            continue

        if mutated_smiles not in generated:
            generated[mutated_smiles] = (mutated_selfies, mutated_smiles)

    if len(generated) < count:
        raise RuntimeError(
            f"Could only generate {len(generated)} unique molecules "
            f"similar to caffeine after the allotted number of attempts."
        )

    return generated


def _format_output(results: Iterable[Tuple[str, Tuple[str, str]]]) -> str:
    lines = []
    for idx, (smiles, (selfies_str, _)) in enumerate(results, start=1):
        lines.append(
            f"{idx:3d}. SELFIES: {selfies_str} | SMILES: {smiles}"
        )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate SELFIES/SMILES strings similar to caffeine",
    )
    parser.add_argument(
        "-n",
        "--count",
        type=int,
        default=100,
        help="number of unique molecules to generate (default: 100)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=1,
        help="random seed for reproducibility (default: 1)",
    )
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=None,
        help=(
            "maximum number of mutation attempts (default: count * 500). "
            "Increase this if you request many molecules."
        ),
    )
    args = parser.parse_args()

    results = generate_caffeine_like_structures(
        count=args.count,
        seed=args.seed,
        max_attempts=args.max_attempts,
    )
    print(_format_output(results.items()))


if __name__ == "__main__":
    main()
