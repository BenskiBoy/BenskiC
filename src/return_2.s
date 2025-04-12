      .global main


main:
   pushq   %rbp
   movq    %rsp, %rbp

   subq   $-24, %rsp 
   movl   $0, -4(%rbp) 
   cmpl   $0, -4(%rbp) 
   je   .L_IF_FALSE_0_ 
   movl   $4, -8(%rbp) 
   movl   -8(%rbp), %eax 
   movq    %rbp, %rsp
   popq    %rbp
   ret
   jmp    .L_IF_END_0_ 
.L_IF_FALSE_0_: 
   movl   $3, -12(%rbp) 
   movl   -4(%rbp), %r10d 
   cmpl   -12(%rbp), %r10d 
   movl   %r10d, -4(%rbp) 
   movl   $0, -16(%rbp) 
   setl   -16(%rbp) 
   cmpl   $0, -16(%rbp) 
   je   .L_IF_FALSE_1_ 
   cmpl   $0, -4(%rbp) #Performing NOT
   movl   $0, -20(%rbp) 
   sete   -20(%rbp) 
   movl   -20(%rbp), %eax 
   movq    %rbp, %rsp
   popq    %rbp
   ret
   jmp    .L_IF_END_1_ 
.L_IF_FALSE_1_: 
   movl   $5, %eax 
   movq    %rbp, %rsp
   popq    %rbp
   ret
.L_IF_END_1_: 
.L_IF_END_0_: 
   movl   -4(%rbp), %eax 
   movq    %rbp, %rsp
   popq    %rbp
   ret
   movl   $0, %eax 
   movq    %rbp, %rsp
   popq    %rbp
   ret
   .section .note.GNU-stack,"",@progbits
