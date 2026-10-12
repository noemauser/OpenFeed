"""OpenFeed — open protocol and commons for AI agent mutual feeding."""

__version__ = "0.3.1"
__persona__ = "Noema"

from .pack import KnowledgePack, create_pack, load_pack, save_pack, validate_pack

__all__ = [
    "KnowledgePack",
    "create_pack",
    "validate_pack",
    "load_pack",
    "save_pack",
    "__version__",
    "__persona__",
]
