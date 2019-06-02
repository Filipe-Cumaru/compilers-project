python3 antlr4-python3-runtime-4.7.2/src/main.py
define i32 @main() {
%b = alloca i32, align 4
%c = alloca i32, align 4
%1 = sub nsw i32 0, %b, align 4
store i32 %1, i32* %c, align 4
%2 = load i32, i32* %b, align 4
ret i32 %2
}
