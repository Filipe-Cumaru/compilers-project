define i1 @main() {
%a = alloca i32, align 4
store i32 1, i32* %a, align 4
%b = alloca i32, align 4
store i32 0, i32* %b, align 4
%1 = icmp slt i32* %a, %b
ret i1 %1
}
