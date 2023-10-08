SHELL := /bin/bash


main:
	@printf "\nPlease, specify a command. Available commands:\n\n - install\n"
	@printf " - uninstall\n - remove\n\n"
	@exit

install:
	@mkdir -p $(PREFIX)/share/pyhoney
	@python3 -m pip install parglare >/dev/null
	@cp main.py $(PREFIX)/share/pyhoney/main.py
	@cp hnyir.py $(PREFIX)/share/pyhoney/hnyir.py
	@cp hisp.py $(PREFIX)/share/pyhoney/hisp.py
	@mkdir -p $(PREFIX)/share/pyhoney/grammar/
	@cp grammar/hny.glr $(PREFIX)/share/pyhoney/grammar/hny.glr
	@cp grammar/hisp.glr $(PREFIX)/share/pyhoney/grammar/hisp.glr
	@cp detect_c_compiler.py $(PREFIX)/share/pyhoney/detect_c_compiler.py
	@chmod +x hny
	@cp ./hny $(PREFIX)/bin/hny
	@echo
	@echo Done
	@echo

uninstall: remove
	@printf ""

remove:
	@rm -f /usr/share/pyhoney/main.py
	@rm -f /usr/share/pyhoney/hnyir.py
	@rm -f /usr/share/pyhoney/hisp.py
	@rm -f /usr/share/pyhoney/grammar/hny.glr
	@rm -f /usr/share/pyhoney/grammar/hisp.glr
	@rm -f /usr/share/pyhoney/detect_c_compiler.py
	@rm -f /usr/bin/hny
	@echo
	@echo Done
	@echo

reinstall: remove install
	@printf ""
