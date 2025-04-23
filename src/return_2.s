      .global main


main:
   pushq   %rbp
   movq    %rsp, %rbp

   subq   $-40, %rsp 
   movl   $1, -4(%rbp) 
   movl   $2, -8(%rbp) 
   movl   $2, -12(%rbp) 
   movl   $20, -16(%rbp) 
   movl   -16(%rbp), %r10d 
   movl   %r10d, -20(%rbp) 
   movl   $5, -24(%rbp) 
   movl   -20(%rbp), %r10d #Performing ADD
   movl   %r10d, -28(%rbp) 
   movl   -28(%rbp), %r10d 
   addl   -24(%rbp), %r10d 
   movl   %r10d, -28(%rbp) 
   movl   -28(%rbp), %r10d 
   movl   %r10d, -20(%rbp) 
   movl   -20(%rbp), %r10d #Performing ADD
   movl   %r10d, -32(%rbp) 
   movl   -32(%rbp), %r10d 
   addl   -12(%rbp), %r10d 
   movl   %r10d, -32(%rbp) 
   movl   -32(%rbp), %r10d 
   movl   %r10d, -20(%rbp) 
   movl   -20(%rbp), %r10d #Performing ADD
   movl   %r10d, -36(%rbp) 
   movl   -36(%rbp), %r10d 
   addl   -4(%rbp), %r10d 
   movl   %r10d, -36(%rbp) 
   movl   -36(%rbp), %eax 
   movq    %rbp, %rsp
   popq    %rbp
   ret
   movl   $0, %eax 
   movq    %rbp, %rsp
   popq    %rbp
   ret
   .section .note.GNU-stack,"",@progbits
