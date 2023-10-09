from version import raw_version as nver, version as ver
import os
import sys


with open("/usr/share/pyhoney/version.py", "rt") as f:
	cver = int(f.readline())
	rver = eval(f.readline())

print("Current version:", rver, "\b\nInstallation version:", ver)

forced = False

if cver > nver:
	print("Newer version of Honey already installed. "
		"Type `Yes' and hit [Enter] to remove newer version and install oldier one")
	if input("> ") == "Yes":
		forced = True

if cver == nver:
	print("This version of Honey already installed, "
		"but you can reinstall it via `sudo make reinstall'")

if forced or cver < nver:
	print("Updating...")
	os.system("make reinstall")
