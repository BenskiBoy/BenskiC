//invalid
// int main(void) {
//     int x = 0;
//     a:
//     x = a;
//     return 0;
// }

// valid
// int main(void) {
//     // it's valid to use the same identifier as a variable and label
//     int ident = 5;
//     goto ident;
//     return 0;
// ident:
//     return ident;
// }

// any statement can have a label

// int main(void) {
//     int a = 1;
// label_if:
//     if (a)
//         goto label_expression;
//     else
//         goto label_empty;

// label_goto:
//     goto label_return;

//     if (0)
//     label_expression:
//         a = 0;

//     goto label_if;

// label_return:
//     return a;

// label_empty:;
//     a = 100;
//     goto label_goto;
// }

#ifdef SUPPRESS_WARNINGS
#pragma GCC diagnostic ignored "-Wunused-label"
#endif
int main(void) {
    goto label2;
    return 0;
    // okay to have space or newline between label and colon
    label1 :
    label2
    :
    return 1;
}