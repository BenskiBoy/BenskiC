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

int foo(int a, int b);

int main(void) {
    return foo(2, 1);
}

/* Multiple declarations of a function
 * can use different parameter names
 */
int foo(int x, int y){
    return x - y;
}
// int main(void) {
//     int var0;
//     var0 = 2;
//     return var0;
// }

// int a(int a) {
//     return a * 2;
// }

// int main(void) {
//     return a(1);
// }

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
