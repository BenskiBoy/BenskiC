      .global main
   .global fib


fib:
   pushq   %rbp
   movq    %rsp, %rbp

   subq   $40, %rsp 
   movl   %edi, -4(%rbp) 
   cmpl   $0, -4(%rbp) 
   movl   $0, -8(%rbp) 
   sete   -8(%rbp) 
   cmpl   $0, -8(%rbp) 
   jne   .L_OR_TRUE_0_ 
   cmpl   $1, -4(%rbp) 
   movl   $0, -12(%rbp) 
   sete   -12(%rbp) 
   cmpl   $0, -12(%rbp) 
   jne   .L_OR_TRUE_0_ 
   movl   $0, -16(%rbp) 
   jmp    .L_OR_END_0_ 
.L_OR_TRUE_0_: 
   movl   $1, -16(%rbp) 
.L_OR_END_0_: 
   cmpl   $0, -16(%rbp) 
   je   .L_IF_FALSE_0_ 
   movl   -4(%rbp), %eax 
   movq    %rbp, %rsp
   popq    %rbp
   ret
   jmp    .L_IF_END_0_ 
.L_IF_FALSE_0_: 
   movl   -4(%rbp), %r10d #Performing SUBTRACT
   movl   %r10d, -20(%rbp) 
   subl   $1, -20(%rbp) 
   movl   -20(%rbp), %edi 
   call   fib 
   movl   %eax, -24(%rbp) 
   movl   -4(%rbp), %r10d #Performing SUBTRACT
   movl   %r10d, -28(%rbp) 
   subl   $2, -28(%rbp) 
   movl   -28(%rbp), %edi 
   call   fib 
   movl   %eax, -32(%rbp) 
   movl   -24(%rbp), %r10d #Performing ADD
   movl   %r10d, -36(%rbp) 
   movl   -36(%rbp), %r10d 
   addl   -32(%rbp), %r10d 
   movl   %r10d, -36(%rbp) 
   movl   -36(%rbp), %eax 
   movq    %rbp, %rsp
   popq    %rbp
   ret
.L_IF_END_0_: 
   movl   $0, %eax 
   movq    %rbp, %rsp
   popq    %rbp
   ret

main:
   pushq   %rbp
   movq    %rsp, %rbp

   subq   $12, %rsp 
   movl   $6, -4(%rbp) 
   movl   -4(%rbp), %edi 
   call   fib 
   movl   %eax, -8(%rbp) 
   movl   -8(%rbp), %eax 
   movq    %rbp, %rsp
   popq    %rbp
   ret
   movl   $0, %eax 
   movq    %rbp, %rsp
   popq    %rbp
   ret
   .section .note.GNU-stack,"",@progbits
