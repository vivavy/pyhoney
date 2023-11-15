import pytest
import os
class TestClassDemoInstance:
    value = 0

    def test_simple(self):
        self.value = 1
        assert self.value == 1

    def test_multiboot(self):
        os.system("HOME_PATH/main.py -o tests/test1.o tests/test1.hny")