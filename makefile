SHELL := /bin/bash


main:
	@printf "\nPlease, specify a command. Available commands:\n\n - install\n"
	@printf " - uninstall\n - remove\n\n"
	@exit

install:
	@mkdir -p $(PREFIX)/share/pyhoney
	@mkdir -p $(PREFIX)/share/pyhoney $(PREFIX)/share/pyhoney/grammar
	@python3 -m pip install parglare >/dev/null
	@cp main.py $(PREFIX)/share/pyhoney/main.py
	@cp hnyir.py $(PREFIX)/share/pyhoney/hnyir.py
	@cp hisp.py $(PREFIX)/share/pyhoney/hisp.py
	@cp grammar/hny.glr $(PREFIX)/share/pyhoney/grammar/hny.glr
	@cp grammar/hisp.glr $(PREFIX)/share/pyhoney/grammar/hisp.glr
	@cp detect_c_compiler.py $(PREFIX)/share/pyhoney/detect_c_compiler.py
	@chmod +x hny
	@cp ./hny $(PREFIX)/bin/hny
	@echo
	@echo Don\'t forget to run \'source \~/.bashrc\' to apply installation!
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
