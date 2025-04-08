      .global main


main:
   pushq   %rbp
   movq    %rsp, %rbp

   subq   $-16, %rsp 
   movl   $1, %r11d 
   cmpl   $1, %r11d 
   movl   $0, -4(%rbp) 
   sete   -4(%rbp) 
   cmpl   $0, -4(%rbp) 
   je   .L_CONDITIONAL_ELSE_0_ 
   movl   $1, -8(%rbp) 
   jmp    .L_CONDITIONAL_END_0_ 
.L_CONDITIONAL_ELSE_0_: 
   movl   $0, -8(%rbp) 
.L_CONDITIONAL_END_0_: 
   movl   -8(%rbp), %r10d 
   movl   %r10d, -12(%rbp) 
   movl   -12(%rbp), %eax 
   movq    %rbp, %rsp
   popq    %rbp
   ret
   movl   $0, %eax 
   movq    %rbp, %rsp
   popq    %rbp
   ret
   .section .note.GNU-stack,"",@progbits
