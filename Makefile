.PHONY: index list search validate-all test

export PYTHONPATH := src

index:
	python -m openfeed index --packs-dir packs -o packs/index.json

list:
	python -m openfeed list --packs-dir packs

search:
	python -m openfeed search "$(q)" --packs-dir packs

get:
	python -m openfeed get "$(id)" --packs-dir packs

fetch:
	python -m openfeed fetch --query "$(q)"

validate-all:
	@for f in packs/kp_*.json; do echo "== $$f"; python -m openfeed validate --strict $$f || exit 1; done

test:
	pip install -e ".[dev]" -q
	pytest -q

venue-check:
	PYTHONPATH=src python scripts/check_venue.py
	PYTHONPATH=src python -m openfeed venue --validate
