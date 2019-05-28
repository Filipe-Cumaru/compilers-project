from antlr4 import *
from autogen.CymbolParser import CymbolParser
from autogen.CymbolVisitor import CymbolVisitor


class Type:
    INT = "int"
    FLOAT = "float"
    BOOLEAN = "boolean"


class CymbolCheckerVisitor (CymbolVisitor):
    # A string to store the LLVM IR code.
    program = ""
    # A dict to keep track of function data (return type, used temp variables).
    functions_data = {}

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

        # TODO: Add store instructions for float and boolean types.
        if ctx.expr() != None:
            last_var = ctx.expr().accept(self)
            if var_type == Type.INT:
                self.program += "store i32 " + last_var + ", i32* %" + var_name + ", align 4\n"

    def visitFuncDecl(self, ctx: CymbolParser.FuncDeclContext):
        func_name = ctx.ID().getText()
        func_ret_type = ctx.tyype().getText()

        # Creating entry in the dict for this function.
        self.functions_data[func_name] = (func_ret_type, 0)

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
        self.program += ") {\n"
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
            param_type = "i32 "
        elif param_type == Type.FLOAT:
            param_type = "float "
        elif param_type == Type.BOOLEAN:
            param_type = "i8 "

        return param_type + "%" + param_name

    def visitReturnStat(self, ctx: CymbolParser.ReturnStatContext):
        return_stat = "ret "
        function_data_key = list(self.functions_data)[-1]
        return_type = self.functions_data[function_data_key][0]

        if return_type == Type.INT:
            return_stat += "i32 "
        elif return_type == Type.FLOAT:
            return_stat += "float "
        elif return_type == Type.BOOLEAN:
            return_stat += "i8 "

        return_var = ctx.expr().accept(self)

        self.program += return_stat + return_var + "\n"

    def visitMulDivExpr(self, ctx: CymbolParser.MulDivExprContext):
        return self.visitChildren(ctx)

    def visitSignedExpr(self, ctx: CymbolParser.SignedExprContext):
        if ctx.op.text == '+':
            return self.visitChildren(ctx)
        elif ctx.op.text == '-':
            self.program += ctx.expr().accept(self)
        return self.visitChildren(ctx)
