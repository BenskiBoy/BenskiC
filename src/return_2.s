      .global main


main:
   pushq   %rbp
   movq    %rsp, %rbp

   subq   $-28, %rsp 
   movl   $0, -4(%rbp) 
   movl   $400, -8(%rbp) 
.L_FOR_LOOP_0_: 
   cmpl   $0, -8(%rbp) 
   movl   $0, -12(%rbp) 
   setne   -12(%rbp) 
   movl   -12(%rbp), %r10d 
   movl   %r10d, -16(%rbp) 
   cmpl   $0, -16(%rbp) 
   je   .L_BREAK_FOR_LOOP_0_ 
   movl   -4(%rbp), %r10d #Performing ADD
   movl   %r10d, -20(%rbp) 
   addl   $1, -20(%rbp) 
   movl   -20(%rbp), %r10d 
   movl   %r10d, -4(%rbp) 
   jmp    .L_CONTINUE_FOR_LOOP_0_ 
.L_CONTINUE_FOR_LOOP_0_: 
   movl   -8(%rbp), %r10d #Performing SUBTRACT
   movl   %r10d, -24(%rbp) 
   subl   $100, -24(%rbp) 
   movl   -24(%rbp), %r10d 
   movl   %r10d, -8(%rbp) 
   jmp    .L_FOR_LOOP_0_ 
.L_BREAK_FOR_LOOP_0_: 
   movl   -4(%rbp), %eax 
   movq    %rbp, %rsp
   popq    %rbp
   ret
   movl   $0, %eax 
   movq    %rbp, %rsp
   popq    %rbp
   ret
   .section .note.GNU-stack,"",@progbits
