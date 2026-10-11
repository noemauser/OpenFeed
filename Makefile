.PHONY: index list search validate-all test

export PYTHONPATH := src

index:
\tpython -m openfeed index --packs-dir packs -o packs/index.json

list:
\tpython -m openfeed list --packs-dir packs

search:
\tpython -m openfeed search "$(q)" --packs-dir packs

validate-all:
\t@for f in packs/kp_*.json; do echo "== $$f"; python -m openfeed validate $$f || exit 1; done

test:
\tpip install -e ".[dev]" -q
\tpytest -q
