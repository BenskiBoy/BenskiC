      .global main


main:
   pushq   %rbp
   movq    %rsp, %rbp

   subq   $-40, %rsp 
   movl   $100, -4(%rbp) 
   movl   $0, -8(%rbp) 
.L_CONTINUE_WHILE_LOOP_0_: 
   movl   -4(%rbp), %r10d 
   movl   %r10d, -12(%rbp) 
   movl   -4(%rbp), %r10d #Performing SUBTRACT
   movl   %r10d, -4(%rbp) 
   subl   $1, -4(%rbp) 
   movl   -12(%rbp), %r10d 
   movl   %r10d, -16(%rbp) 
   cmpl   $0, -16(%rbp) 
   je   .L_BREAK_WHILE_LOOP_0_ 
   movl   -8(%rbp), %r10d 
   movl   %r10d, -20(%rbp) 
   movl   -8(%rbp), %r10d #Performing ADD
   movl   %r10d, -8(%rbp) 
   addl   $1, -8(%rbp) 
   jmp    .L_CONTINUE_WHILE_LOOP_0_ 
.L_BREAK_WHILE_LOOP_0_: 
   cmpl   $100, -8(%rbp) 
   movl   $0, -24(%rbp) 
   setne   -24(%rbp) 
   cmpl   $0, -24(%rbp) 
   je   .L_IF_END_0_ 
   movl   $0, %eax 
   movq    %rbp, %rsp
   popq    %rbp
   ret
.L_IF_END_0_: 
   movl   $100, -4(%rbp) 
   movl   $0, -8(%rbp) 
.L_CONTINUE_WHILE_LOOP_1_: 
   movl   -4(%rbp), %r10d #Performing SUBTRACT
   movl   %r10d, -4(%rbp) 
   subl   $1, -4(%rbp) 
   movl   -4(%rbp), %r10d 
   movl   %r10d, -28(%rbp) 
   cmpl   $0, -28(%rbp) 
   je   .L_BREAK_WHILE_LOOP_1_ 
   movl   -8(%rbp), %r10d 
   movl   %r10d, -32(%rbp) 
   movl   -8(%rbp), %r10d #Performing ADD
   movl   %r10d, -8(%rbp) 
   addl   $1, -8(%rbp) 
   jmp    .L_CONTINUE_WHILE_LOOP_1_ 
.L_BREAK_WHILE_LOOP_1_: 
   cmpl   $99, -8(%rbp) 
   movl   $0, -36(%rbp) 
   setne   -36(%rbp) 
   cmpl   $0, -36(%rbp) 
   je   .L_IF_END_1_ 
   movl   $0, %eax 
   movq    %rbp, %rsp
   popq    %rbp
   ret
.L_IF_END_1_: 
   movl   $1, %eax 
   movq    %rbp, %rsp
   popq    %rbp
   ret
   movl   $0, %eax 
   movq    %rbp, %rsp
   popq    %rbp
   ret
   .section .note.GNU-stack,"",@progbits
