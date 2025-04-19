      .global main


main:
   pushq   %rbp
   movq    %rsp, %rbp

   subq   $-8, %rsp 
   movl   $1, -4(%rbp) 
   jmp    .L_DEFAULT_1 
.L_DEFAULT_1: 
   movl   $1, %eax 
   movq    %rbp, %rsp
   popq    %rbp
   ret
.L_SWITCH_0_END: 
.L_BREAK__SWITCH_0_: 
   movl   $0, %eax 
   movq    %rbp, %rsp
   popq    %rbp
   ret
   movl   $0, %eax 
   movq    %rbp, %rsp
   popq    %rbp
   ret
   .section .note.GNU-stack,"",@progbits
