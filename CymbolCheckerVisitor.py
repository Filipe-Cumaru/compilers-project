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

    # A dict to keep track of variable data (return type).
    vars_data = {}

    # START AUXILIARY FUNCTIONS
    def getVarType(self, var, exprCtx):
        if (type(var) == type(int()) or exprCtx.ID):
            return self.vars_data[self.func_name][var]
        elif exprCtx.BOOLEAN:
            return 'i8'
        elif exprCtx.INT:
            return 'i32'
        elif exprCtx.FLOAT:
            return 'float'

    def setVarType(self, var, varType):
        self.vars_data[self.func_name][var] = varType

    # returns the next temp var to be used
    def getNextVar(self, increment=True):
        # to avoid doing set all the fucking time
        if(increment):
            self.functions_data[self.func_name][1] += 1
        return self.functions_data[self.func_name][1]

    # Adds load statement and returns the temp var that contains
    # the value of the given variable
    def loadVariable(self, var, var_type):
        current_var = None
        if (isinstance(var, int)):
            var = '%' + str(var)

        # if the expr result is a variable
        if('%' in var):
            current_var = '%' + str(self.getNextVar())

            # load the value of the returned var into the current var
            # TODO: Fix align number based on var_type
            self.program += '{} = load {}, {}* {}, align 4\n'.format(
                current_var, var_type, var_type, var)

            self.setVarType(current_var, var_type)

        return current_var
    # END AUXILIARY FUNCTIONS

    def visitVarDecl(self, ctx: CymbolParser.VarDeclContext):
        var_name = '%' + ctx.ID().getText()
        var_type = ctx.tyype().getText()

        # Add line with variable allocation.
        self.program += "{0} = alloca ".format(var_name)
        if var_type == Type.INT:
            self.vars_data[self.func_name][var_name] = 'i32'
            self.program += "i32, align 4\n"
        elif var_type == Type.FLOAT:
            self.vars_data[self.func_name][var_name] = 'float'
            self.program += "float, align 4\n"
        elif var_type == Type.BOOLEAN:
            self.vars_data[self.func_name][var_name] = 'i8'
            self.program += "i8, align 1\n"

        # TODO: Add store instructions for float and boolean types.
        if ctx.expr() != None:
            last_var = ctx.expr().accept(self)
            # If the last var is a temporary variable
            if(isinstance(last_var, int)):
                last_var = '%' + str(last_var)
            # If not then it's an int, bolean or float
            if var_type == Type.INT:
                self.program += "store i32 " + last_var + \
                    ", i32* " + var_name + ", align 4\n"

    def visitFuncDecl(self, ctx: CymbolParser.FuncDeclContext):
        self.func_name = ctx.ID().getText()
        self.func_ret_type = ctx.tyype().getText()

        # Creating entry in the functions dict for this function.
        # changed to array because tuples are immutable
        self.functions_data[self.func_name] = [self.func_ret_type, 0]
        # Creating entry in the variables dict for this function.
        self.vars_data[self.func_name] = {}

        # Add function declaration and return type.
        self.program += "define "
        if self.func_ret_type == Type.INT:
            self.program += "i32 "
        elif self.func_ret_type == Type.FLOAT:
            self.program += "float "
        elif self.func_ret_type == Type.BOOLEAN:
            self.program += "i8 "

        self.program += "@{0}(".format(self.func_name)
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
        param_name = '%' + ctx.ID().getText()

        if param_type == Type.INT:
            param_type = "i32 "
        elif param_type == Type.FLOAT:
            param_type = "float "
        elif param_type == Type.BOOLEAN:
            param_type = "i8 "

        # Add var to dict
        self.vars_data[self.func_name][param_name] = param_type

        return param_type + param_name

    def visitReturnStat(self, ctx: CymbolParser.ReturnStatContext):
        return_stat = "ret "
        return_type = self.functions_data[self.func_name][0]

        if return_type == Type.INT:
            return_stat += "i32 "
            return_type = "i32"
        elif return_type == Type.FLOAT:
            return_stat += "float "
            return_type = "float"
        elif return_type == Type.BOOLEAN:
            return_stat += "i8 "
            return_type = "i8"

        return_var = ctx.expr().accept(self)

        # TODO check if variable is a pointer and only then do the load
        if (isinstance(return_var, int) or '%' in return_var):
            current_var = '%' + str(self.getNextVar())

            self.program += '{} = load {}, {}* {}, align 4\n'.format(
                current_var, return_type, return_type, return_var)

            return_var = current_var  # the temp var should be returned

        self.program += return_stat + return_var + "\n"

    def visitAssignStat(self, ctx: CymbolParser.AssignStatContext):
        var_id = '%' + ctx.ID().getText()
        # print(self.vars_data)
        var_type = self.getVarType(var_id, ctx)
        expr_result = ctx.expr().accept(self)
        expr_result_type = self.getVarType(expr_result, ctx.expr())

        expr_result_value = self.loadVariable(expr_result, expr_result_type)

        if(expr_result_value is None):
            expr_result_value = expr_result

        # store the value of the expr result where it should be stored
        # TODO: Store variable types as pointers too when necessary
        self.program += 'store {} {}, {}* {}, align 4\n'.format(
            expr_result_type, expr_result_value, var_type, var_id)

        return var_id

    # START EXPRESSIONS
    # Note: In case expressions return the last temp variable used
    # their type MUST be an int!!!
    def visitIntExpr(self, ctx: CymbolParser.VarIdExprContext):
        return ctx.INT().getText()

    def visitFloatExpr(self, ctx: CymbolParser.VarIdExprContext):
        return ctx.FLOAT().getText()

    def visitBooleanExpr(self, ctx: CymbolParser.VarIdExprContext):
        return '1' if ctx.BOOLEAN().getText() == 'true' else '0'

    def visitVarIdExpr(self, ctx: CymbolParser.VarIdExprContext):
        return '%' + ctx.ID().getText()

    def visitSignedExpr(self, ctx: CymbolParser.SignedExprContext):
        # get last variable number
        expr_result = ctx.expr().accept(self)

        if(isinstance(expr_result, int)):
            expr_result = '%' + expr_result

        current_var = self.getNextVar()

        if ctx.op.text == '+':  # Nothing to do, just accept the next expressions
            return self.visitChildren(ctx)

        # if it's just a negative number
        elif ctx.op.text == '-' and (hasattr(ctx.expr(), 'INT') or hasattr(ctx.expr(), 'FLOAT')):
            print('TODO: Treat negative number expression')
        # all other cases
        elif ctx.op.text == '-':
            last_var_type = self.getVarType(expr_result, ctx.expr())

            self.program += '%{} = sub nsw {} 0, {}, align 4\n'.format(
                current_var, last_var_type, expr_result
            )

            # set current var's type to be the same as the last var's type
            self.setVarType(current_var, last_var_type)
        return current_var

    def visitMulDivExpr(self, ctx: CymbolParser.MulDivExprContext):
        return self.visitChildren(ctx)
