int main(void) {
    int foo = 0;
    for (int i = 400; i != 0; i = i - 100){
        foo += 1;
        continue;
    }
    return foo;

}
