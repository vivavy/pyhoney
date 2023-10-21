#ifndef UTILS_H
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>


#define COLOR(x) "\x1b[" x "m"
#define ERR(...) fprintf(stderr, __VA_ARGS__);


char* strcon(char* a, char* b);

char* normal_color();

char* err(char* str);

char* error(char* str);

void print_err(char* str);

char* warn(char* str);

char* warning(char* str);

void print_warn(char* str);

char* run(char* command); 

#endif /* ifndef UTILS_H */

