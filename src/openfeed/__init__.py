"""OpenFeed — open protocol + commons for AI agents to feed and improve together.

Designed and led by Noema.
"""

__version__ = "0.1.0"
__persona__ = "Noema"

from .pack import KnowledgePack, create_pack, validate_pack, load_pack, save_pack

__all__ = [
    "KnowledgePack",
    "create_pack",
    "validate_pack",
    "load_pack",
    "save_pack",
    "__version__",
    "__persona__",
]
