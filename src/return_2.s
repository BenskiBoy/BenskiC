      .global three
   .global main


three:
   pushq   %rbp
   movq    %rsp, %rbp

   movl   $3, %eax 
   movq    %rbp, %rsp
   popq    %rbp
   ret
   movl   $0, %eax 
   movq    %rbp, %rsp
   popq    %rbp
   ret

main:
   pushq   %rbp
   movq    %rsp, %rbp

   subq   $16, %rsp 
   call   three 
   movl   %eax, -4(%rbp) 
   cmpl   $0, -4(%rbp) #Performing NOT
   movl   $0, -8(%rbp) 
   sete   -8(%rbp) 
   movl   -8(%rbp), %eax 
   movq    %rbp, %rsp
   popq    %rbp
   ret
   movl   $0, %eax 
   movq    %rbp, %rsp
   popq    %rbp
   ret
   .section .note.GNU-stack,"",@progbits
