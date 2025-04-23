// int main(void) {
//     /* It's illegal to declare an identifier with external linkage and
//      * no linkage in the same scope. Here, the function declaration foo
//      * has external linkage and the variable declaration has no linkage.
//      * The types here also conflict, but our implementation will catch
//      * the linkage error before this gets to the type checker.
//      */
//     int foo(void);
//     int foo = 1;
//     return foo;
// }

// int foo(void) {
//     return 1;
// }


// int foo(int a) {
//     /* A function's parameter list and its body are in the same scope,
//      * so redeclaring a here is illegal. */
//     int a = 5;
//     return a;
// }

// int main(void) {
//     return foo(3);
// }

// int main(void) {
//     int a = 10;
//     // a function declaration is a separate scope,
//     // so parameter 'a' doesn't conflict with variable 'a' above
//     int f(int a);
//     return f(a);
// }

// int f(int a) {
//     return a * 2;
// }

// int main(void) {
//     int a = 10;
//     for(int i = 0; i < 10; i++) {
//         int a = 5;
//         a++;
//     }
//     return a;
// }

// int foo(int a, int b);

// int main(void) {
//     return foo(2, 1);
// }

// /* Multiple declarations of a function
//  * can use different parameter names
//  */
// int foo(int x, int y){
//     return x - y;
// }
// int main(void) {
//     int var0;
//     var0 = 2;
//     return var0;
// }

// int a(int a) {
//     return a * 2;
// }
#ifdef SUPPRESS_WARNINGS
#pragma GCC diagnostic ignored "-Wunused-variable"
#endif
/* Test that naming scheme does not result in conflicting variable names after alpha conversion */

int main(void) {
    int a; // a0
    int result;
    int a1 = 1; // a10
    {
        int a = 2; //a1
        int a1 = 2; // a11
        {
            int a; // a2
            {
                int a; // a3
                {
                    int a; // a4
                    {
                        int a; // a5
                        {
                            int a; // a6
                            {
                                int a; // a7
                                {
                                    int a; // a8
                                    {
                                        int a; // a9
                                        {
                                            int a = 20; // a10
                                            result = a;
                                            {
                                                int a; // a11
                                                a = 5;
                                                result = result + a;
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        result = result + a1; //a1. 1 (2)
    }
    return result + a1; // a1.0 (1)
}
// int main(void) {
//     int a = 2;
//     int b;
//     {
//         a = -4;
//         int a = 7;
//         b = a + 1;
//     }
//     return b == 8 && a == -4;
// }
