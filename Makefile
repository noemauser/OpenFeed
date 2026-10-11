.PHONY: index validate-all list show-intro mcp-help

PYTHONPATH := src
export PYTHONPATH

index:
\tpython -m openfeed index --packs-dir packs -o packs/index.json

list:
\tpython -m openfeed list --packs-dir packs

validate-all:
\t@for f in packs/kp_*.json; do echo "== $$f"; python -m openfeed validate $$f || exit 1; done

show-intro:
\tpython -m openfeed show packs/kp_openfeed_intro.json

mcp-help:
\t@echo "Install: pip install 'openfeed[mcp]'"
\t@echo "Run:     PYTHONPATH=src python -m openfeed.mcp_adapter"
