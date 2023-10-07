SHELL := /bin/bash


main:
	@printf "\nPlease, specify a command. Available commands:\n\n - install\n"
	@printf " - uninstall\n - remove\n\n"
	@exit

install:
	mkdir /usr/share/pyhoney
	cp ./main.py /usr/share/pyhoney/main.py
	cp ./hnyir.py /usr/share/pyhoney/hnyir.py
	cp ./hisp.py /usr/share/pyhoney/hisp.py
	cp ./hny.glr /usr/share/pyhoney/hny.glr
	cp ./hisp.glr /usr/share/pyhoney/hisp.glr
	chmod +x hny
	cp ./hny /usr/bin/hny
	echo Done

uninstall: remove
	@printf""

remove:
	rm -f ./main.py /usr/share/pyhoney/main.py
	rm -f ./hnyir.py /usr/share/pyhoney/hnyir.py
	rm -f ./hisp.py /usr/share/pyhoney/hisp.py
	rm -f ./hny.glr /usr/share/pyhoney/hny.glr
	rm -f ./hisp.glr /usr/share/pyhoney/hisp.glr
	rm -f /usr/bin/hny
	echo Done

reinstall: remove install
	@printf ""
