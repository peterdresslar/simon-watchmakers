# Simon's Watchmakers: Tempus, Hora, and Secunda

A computational re-examination of Herbert Simon's parable of the watchmakers from *The Architecture of Complexity* (1962), implemented as a [marimo](https://marimo.io) reactive notebook.

[![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/peterdresslar/simon-watchmakers/blob/main/notebooks/simon-watchmakers.py)

## About

Simon's parable of Hora and Tempus is one of the most cited arguments for hierarchical, modular organization in complex systems. This notebook validates corrected analytical predictions (Turney 1989, Saltzer 1996) through faithful Python simulation, applies Shannon entropy to trace where information is committed during assembly, and identifies an unacknowledged agent in the parable — here called *Secunda* — whose invisible, costless work at every modular ratchet point is the sole source of Hora's advantage. We derive the conditions under which Secunda's contribution provides a net benefit, showing that modularity is advantageous only when the environment is hostile enough to punish linear development.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Python 3.13+

## Run

Edit the notebook interactively:

```bash
uv run marimo edit notebooks/simon-watchmakers.py
```

Run as a read-only app (code hidden, UI elements still interactive):

```bash
uv run marimo run notebooks/simon-watchmakers.py
```

Run as a plain Python script:

```bash
uv run python notebooks/simon-watchmakers.py
```

## Citation

If you use this work, please cite it using the metadata in [CITATION.cff](CITATION.cff).

## License

This work is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## References

- Simon, H. A. (1962). The architecture of complexity. *Proceedings of the American Philosophical Society*, 106(6), 467-482.
- Turney, P. (1989). The architecture of complexity: A new blueprint. *Synthese*, 79(3), 515-542.
- Saltzer, J. H. (1996). [6.033 discussion suggestions (Simon complexity paper)](https://web.mit.edu/saltzer/www/publications/recguides/Simon.html). MIT.
