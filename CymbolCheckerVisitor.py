from antlr4 import *
from autogen.CymbolParser import CymbolParser
from autogen.CymbolVisitor import CymbolVisitor


class Type:
    INT = "int"
    FLOAT = "float"
    BOOLEAN = "boolean"


class CymbolCheckerVisitor (CymbolVisitor):
    program = ""

    def visitVarDecl(self, ctx: CymbolParser.VarDeclContext):
        var_name = ctx.ID().getText()
        var_type = ctx.tyype().getText()

    # Add line with variable allocation.
        self.program = "%{0} = alloca ".format(var_name)
        if var_type == Type.INT:
            self.program += "i32, align 4\n"
        elif var_type == Type.FLOAT:
            self.program += "float, align 4\n"
        elif var_type == Type.BOOLEAN:
            self.program += "i8, align 1\n"

        if ctx.expr() != None:
            ctx.expr().accept(self)

    def visitFuncDecl(self, ctx: CymbolParser.FuncDeclContext):
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
        if ctx.paramTypeList() != None:
            self.program += ctx.paramTypeList().accept(self)
        self.program += ") {\n\t"
        ctx.block().accept(self)
        self.program += "}"

        print(self.program)

    def visitParamTypeList(self, ctx: CymbolParser.ParamTypeListContext):
        params = []

        for param in ctx.paramType():
            params.append(param.accept(self))

        return ", ".join(params)

    def visitParamType(self, ctx: CymbolParser.ParamTypeContext):
        param_type = ctx.tyype().getText()
        param_name = ctx.ID().getText()

        if param_type == Type.INT:
            param_type = "i32"
        elif param_type == Type.FLOAT:
            param_type = "float"
        elif param_type == Type.BOOLEAN:
            param_type = "i8"

        return param_type + " %" + param_name

    def visitSignedExpr(self, ctx: CymbolParser.SignedExprContext):
        print(ctx.op.text)
        if ctx.op.text == '+':
            return self.visitChildren(ctx)
        elif ctx.op.text == '-':
            self.program += ctx.expr().accept(self)

            return self.visitChildren(ctx)
