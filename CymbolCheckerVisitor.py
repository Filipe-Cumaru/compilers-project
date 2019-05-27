from antlr4 import *
from autogen.CymbolParser import CymbolParser
from autogen.CymbolVisitor import CymbolVisitor

class Type:
	INT = "int"
	FLOAT = "float"
	BOOLEAN = "boolean"

class CymbolCheckerVisitor (CymbolVisitor):
    program = ""

    def visitVarDecl(self, ctx:CymbolParser.VarDeclContext):
        var_name = ctx.ID().getText()
		var_type = ctx.tyype().getText()

        # Add line with variable allocation.
        self.program = "%{0} = alloca ".format(var_name)
        if var_type == Type.INT:
            self.program += "i32, align 4\n"
        elif var_type == Type.FLOAT:
            self.program += "float, align 4\n"
        elif var_type == Type.BOOLEAN:
            self.program += "i8, align 4\n"

        if ctx.expr() != None:
            ctx.expr().accept(self)

    def visitFuncDecl(self, ctx:CymbolParser.FuncDeclContext):
        func_name = ctx.ID().getText()
        func_ret_type = ctx.ID().getText()

        # Add function declaration and return type.
        self.program += "define "
        if func_ret_type == Type.INT:
            self.program += "i32 "
        elif func_ret_type == Type.FLOAT:
            self.program += "float "
        elif func_ret_type == Type.BOOLEAN:
            self.program += "i8 "

        self.program += "@{0}(".format(func_name)
        # NOTE: Not sure if this is right. Still needs to be tested.
        if ctx.paramTypeList() != None:
            ctx.paramTypeList().accept(self)
        self.program += ") {\n\t"
        ctx.block().accept(self)
        self.program += "}"
