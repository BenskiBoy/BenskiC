  .file "./return_2.c"
  .text
  .global main
  .type main, @function
main:
  movl $100, %eax
  ret
  .ident  "GCC: (Ubuntu 9.3.0-17ubuntu1~20.04) 9.3.0"
  .section  .note.GNU-stack,"",@progbits
