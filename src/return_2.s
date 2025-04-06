      .global main


main:
   pushq   %rbp
   movq    %rsp, %rbp

   subq   $-20, %rsp 
   movl   $1, -4(%rbp) 
   movl   -4(%rbp), %r10d 
   movl   %r10d, -8(%rbp) 
   movl   -4(%rbp), %r10d #Performing ADD
   movl   %r10d, -4(%rbp) 
   addl   $1, -4(%rbp) 
   cmpl   $0, -8(%rbp) #Performing NOT
   movl   $0, -12(%rbp) 
   sete   -12(%rbp) 
   movl   -12(%rbp), %r10d 
   movl   %r10d, -16(%rbp) 
   movl   $0, %eax 
   movq    %rbp, %rsp
   popq    %rbp
   ret
   .section .note.GNU-stack,"",@progbits
