#include <argp.h>
#include <stdio.h>
#include <string.h>

#define VERSION_FILE "/usr/share/pyhoney/version.py"

int main(int argc, char *argv[]) {
  FILE *version_file = fopen(VERSION_FILE, "r");
  if (version_file == NULL) {
    char *error_str = "File \"%s\" with version don`t exists";
    fprintf(stderr, error_str, VERSION_FILE);
  }
  argp_parse(0, argc, argv, 0, 0, 0);
  return 0;
}
