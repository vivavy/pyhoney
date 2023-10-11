NAME=pyhoney

main:
	@echo "Type \`sudo make install' and \`make apply' for installation \
(second if it is your first installation) or \`sudo make uninstall' for uninstallation"
	@echo "For update, type \`sudo make update'"
	@echo "For same version fix, type \`sudo make patch'"
	@exit

install:
	@mkdir -p /usr/share/$(NAME) /usr/share/$(NAME)/grammar \
		  /usr/share/$(NAME)/objects /usr/share/$(NAME)/lds \
		  $(HOME)/.config/sublime-text/Packages
	@cp *.py /usr/share/$(NAME)
	@cp support/sublime/* $(HOME)/.config/sublime-text/Packages
	@rm /usr/share/$(NAME)/update.py
	@cp grammar/*.glr /usr/share/$(NAME)/grammar
	@cp lds/*.ld /usr/share/$(NAME)/lds
	@echo

apply:
	@echo "python3 /usr/share/$(NAME)/main.py $@" > /bin/hny

uninstall: remove
	@printf ""

remove:
	@rm -rf /usr/share/$(NAME)
	@rm -f /bin/hny
	@echo
	@echo Done
	@echo

patch: reinstall
	@printf ""

reinstall: remove install
	@printf ""

update:
	@python3 update.py
