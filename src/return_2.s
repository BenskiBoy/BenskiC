      .global main


main:
   pushq   %rbp
   movq    %rsp, %rbp

   subq   $-24, %rsp
   movl   $80, -4(%rbp)
   movl   $2, %ecx
   movl   -4(%rbp), %r10d
   shrl   %ecx, %r10d
   movl   %r10d, -4(%rbp)
   movl   -4(%rbp), %r10d
   movl   %r10d, -8(%rbp)
   orl   $1, -8(%rbp)
   movl   -8(%rbp), %r10d
   movl   %r10d, -12(%rbp)
   xorl   $5, -12(%rbp)
   movl   $7, -16(%rbp)
   movl   $1, %ecx
   movl   -16(%rbp), %r10d
   shll   %ecx, %r10d
   movl   %r10d, -16(%rbp)
   movl   -12(%rbp), %r10d
   movl   %r10d, -20(%rbp)
   movl   -16(%rbp), %ecx
   movl   -20(%rbp), %r10d
   andl   %ecx, %r10d
   movl   %r10d, -20(%rbp)
   movl   -20(%rbp), %eax
   movq    %rbp, %rsp
   popq    %rbp
   ret
   .section .note.GNU-stack,"",@progbits
