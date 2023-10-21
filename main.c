#include <argp.h>
#include <stdarg.h>
#include <stdio.h>
#include <errno.h>
#include "utils.h"

#define VERSION_FILE "/usr/share/pyhoney/version.py"

int main(int argc, char *argv[]) {
  FILE *version_file = fopen(VERSION_FILE, "r");
  char *version = malloc(1 * sizeof(char));
  version[0] = '\0';
  if (version_file == NULL) {
    ERR(warning("File \"%s\" with version don`t exists, skipped"), VERSION_FILE);
  }
  else {
    print_warn("TODO: fix version reading (and version saving too)");
    fclose(version_file);
    /* TODO
    int i;
    fscanf(version_file, "%d\n%s\n", &i, version);
    printf("%d %s\n", i, version);
    */
  }
  FILE *fp = popen("/usr/bin/ls", "r");
  puts(strerror(errno));

  argp_parse(0, argc, argv, 0, 0, 0);

  // printf(run("/bin/ls"));

  // FILE *fp = popen("", "");
  return 0;
}
