SHELL := /bin/bash


main:
	@python3 -m venv venv
	@source ./venv/bin/activate;         \
	pip install pyinstaller >/dev/null;  \
	pyinstaller main.py                  \
		-n "hny"                         \
		--add-data hisp.glr:.            \
		--add-data hisp.py:.             \
		--add-data hny.glr:.             \
		--add-data hnyir.py:.            \
		--log-level WARN                 \
		-F
	@mv -f dist/hny hny
	@rm -f hny.spec
	@rm -rf build dist venv
	@find -iname "*.pyc" -delete
