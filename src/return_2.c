// make sure we don't treat different cases as different scopes

// int main(void) {
//     switch (1) {
//         case 1:
//         ;
//             int b = 10;
//             break;

//         case 2:;
//             // invalid redefinition, because we're in the same scope
//             // as declaration of b above
//             int b = 11;
//             break;

//         default:
//             break;
//     }
//     return 0;
// }

// int main(void) {
//     switch (1) {
//         case 1: {
//         ;
//             int b = 10;
//             break;
//         }
//         case 2:;
//             // invalid redefinition, because we're in the same scope
//             // as declaration of b above
//             int b = 11;
//             break;

//         default:
//             break;
//     }
//     return 0;
// }

// Can't have two default statements in same enclosing switch, even in different scopes
// test that we perform usual variable resolution/validation for switch
// statement bodies, including outside of case/default statements
// int main(void) {
//     int a = 1;
//     switch (a) {
//         // variable resolution must process this even though it's not reachable;
//         // it still declares the variable/brings it into scope
//         int b = 2;
//         case 0:
//             a = 3;
//             int b = 2;  // error - duplicate declaration
//     }
//     return 0;
// }
// A fun use of fallthrough - see https://en.wikipedia.org/wiki/Duff%27s_device
// int main(void) {
//     int count = 37;
//     int iterations = (count + 4) / 5;
//     switch (count % 5) {
//         case 0:
//             do {
//                 count = count - 1;
//                 case 4:
//                     count = count - 1;
//                 case 3:
//                     count = count - 1;
//                 case 2:
//                     count = count - 1;
//                 case 1:
//                     count = count - 1;
//             } while ((iterations = iterations - 1) > 0);
//     }
//     return (count == 0 && iterations == 0);
// }

int main(void) {
    int a = 1;
    switch(a) default: return 1;
    return 0;
}
// int main(void) {
//     switch (1) {
//         case 1: {
//         ;
//             int b = 10;
//             return b;
//         }
//         return 99;
//         case 2:;
//             // invalid redefinition, because we're in the same scope
//             // as declaration of b above
//             int b = 11;

//         default:{;
//             int blah = 34;
//         }
//     }
//     return 123;
// }



// int main(void) {
//     int a = 5;
//     if (a > 4) {
//         a -= 4;
//         int a = 5;
//         if (a > 4) {
//             a -= 4;
//         }
//     }
//     return a;
// }