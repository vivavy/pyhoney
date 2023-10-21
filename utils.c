#include "utils.h"
#include <stdio.h>

char* strcon(char* a, char* b) {
  // va_list ap;
  // va_start(ap, a);

  char* out = malloc(strlen(a) + strlen(b));
  strcpy(out, a);
  strcat(out, b);
  // strcat(out, c);
  return out;
}

char* normal_color() {
  return strcon("\n", COLOR("0"));
}

char* err(char* str) {
  return strcon(COLOR("31"), strcon(str, normal_color()));
}

char* error(char* str) {
  return err(strcon("Error: ", str));
}

void print_err(char* str) {
  fputs(err(str), stderr);
}

char* warn(char* str) {
  return strcon(COLOR("33"), strcon(str, normal_color()));
}

char* warning(char* str) {
  return warn(strcon("Warning: ", str));
}

void print_warn(char* str) {
  fputs(warn(str), stderr);
}

void* handle_malloc(long int size, char* process, int exit_code) {
  void* p = malloc(size);
  if (p == NULL) {
    ERR(error("malloc failed: %s\n\n"), process)
    if (exit_code)
      exit(exit_code);
    ERR(error("Skipped\n"))
    return NULL;
  }
  return p;
}

char* run(char* command) {
  FILE *fptr = popen(command, "r");
  puts(strerror(errno));
  if (fptr == NULL) {
    ERR(warning("Failed to run command \"%s\""), command);
    pclose(fptr);
    return NULL; 
  } 
  fseek(fptr, 0, SEEK_END);
  long size = ftell(fptr);
  fseek(fptr, 0, SEEK_SET);
  printf("%d", size);

  char* str = handle_malloc(sizeof(char) * size, strcon("reading file for command \"", strcon(command, "\"")), -1);

  int result = fread(str, 0, size, fptr);

  pclose(fptr);
  return str;
}

