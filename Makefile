NAME=pyhoney
HONEY_PATH=/usr/share/$(NAME)

main:
	@echo "Type \`sudo make install' and \`make apply' for installation \
(second if it is your first installation) or \`sudo make uninstall' for uninstallation"
	@echo "For update, type \`sudo make update'"
	@echo "For same version fix, type \`sudo make patch'"
	@exit

install:
	@mkdir -p HONEY_PATH HONEY_PATH/objects HONEY_PATH/parser \
		HONEY_PATH/lds HONEY_PATH/compiler HONEY_PATH/analyzer \
		~/.config/sublime-text/Packages ~/.config/micro/syntax 
	@cp *.py HONEY_PATH
	@cp support/sublime/Honey.sublime-syntax ~/.config/sublime-text/Packages/Honey.sublime-syntax
	@cp support/micro/hny.yaml ~/.config/micro/syntax
	@rm /usr/share/$(NAME)/update.py
	@cp grammar.antlr HONEY_PATH
	@cp lds/*.ld HONEY_PATH/lds
	@cp parser/* HONEY_PATH/parser
	@cp compiler/* HONEY_PATH/compiler
	@cp analyzer/* HONEY_PATH/analyzer
	@echo

apply:
	@echo "python3 /usr/share/$(NAME)/main.py $@" > /bin/hny

uninstall: remove
	@printf ""

remove:
	@rm -rf /usr/share/$(NAME)
	@rm -f /bin/hny
	@rm -f ~/.config/sublime-text/Honey.sublime-syntax
	@rm -f ~/.config/micro/syntax/hny.yaml
	@echo
	@echo Done
	@echo

patch: reinstall
	@printf ""

reinstall: remove install
	@printf ""

update:
	@python3 update.py
