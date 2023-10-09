SHELL := /bin/bash


main:
	@echo "Type \`sudo make install' and \`make apply' for installation \
(second if it is your first installation) or \`sudo make uninstall' for uninstallation"
	@echo "For update, type \`sudo make update'"
	@exit

install:
	@mkdir -p /usr/share/pyhoney /usr/share/pyhoney/grammar
	@mkdir -p /usr/share/pyhoney/objects /usr/share/pyhoney/lds
	@cp *.py /usr/share/pyhoney
	@rm /usr/share/pyhoney/update.py
	@cp grammar/*.glr /usr/share/pyhoney/grammar
	@cp lds/*.ld /usr/share/pyhoney/lds
	@echo

apply:
	@python3 -m pip install parglare >/dev/null
	@cat /home/*/.bashrc bashrc >/home/*/.bashrc

uninstall: remove
	@printf ""

remove:
	@rm -rf /usr/share/pyhoney
	@echo
	@echo Done
	@echo

reinstall: remove install
	@printf ""

update:
	@python3 update.py
