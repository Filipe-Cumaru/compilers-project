define i1 @main() {
	%c = alloca 	i1, align 1
	store i1 1, i1* %c, align 1
	%b = alloca 	i1, align 1
	store i1 0, i1* %b, align 1
	%1 = load i1, i1* %c, align 4
	%2 = load i1, i1* %b, align 4
	%3 = and i1 %1, %2
	ret i1 %3
}
