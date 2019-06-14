from antlr4 import *
from autogen.CymbolParser import CymbolParser
from autogen.CymbolVisitor import CymbolVisitor
import struct

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

    # Function to conver decimal to binary
    def float_to_hex(self, f):
        ieee_float = hex(struct.unpack('<I', struct.pack('<f', f))[0])
        extra_zeros = 16 - (len(ieee_float) - 2)
        return ieee_float + (extra_zeros*'0')

    def getVarType(self, var, exprCtx):
        if isinstance(var, int):
            var = '%' + str(var)
        if hasattr(exprCtx, 'ID') or '%' in var:
            return self.vars_data[self.func_name][var]
        elif hasattr(exprCtx, 'BOOLEAN'):
            return 'i1'
        elif hasattr(exprCtx, 'INT'):
            return 'i32'
        elif hasattr(exprCtx, 'FLOAT'):
            return 'float'

    def setVarType(self, var, varType):
        self.vars_data[self.func_name][var] = varType

    # returns the next temp var to be used
    def getNextVar(self, increment=True):
        # to avoid doing set all the fucking time
        if increment:
            self.functions_data[self.func_name][1] += 1
        return self.functions_data[self.func_name][1]

    # Returns the operands and their types of any boolean expression
    def getExprOper(self, ctx):
        operands = []  # (operand, operand_type)
        for expr in ctx.expr():
            expr_result = expr.accept(self)
            expr_result_type = self.getVarType(expr_result, expr)

            operand = self.loadVariable(expr_result, expr_result_type)
            if not operand:
                operand = expr_result
                if isinstance(operand, int):
                    operand = '%' + str(operand)

            operand_type = self.getVarType(operand, expr)
            operands.append((operand, operand_type))

        return operands

    # Adds load statement and returns the temp var that contains
    # the value of the given variable
    # NOTE: Returns None if the variable to be loaded is not a pointer

    def loadVariable(self, var, var_type):
        current_var = None
        align_val = 1

        if isinstance(var, int):
            var = '%' + str(var)

        # if the expr result is a variable
        if '*' in var_type:
            current_var = '%' + str(self.getNextVar())

            # load the value of the returned var into the current var
            if 'i32' in var_type or 'float' in var_type:
                align_val = 4

            self.program += '\t{} = load {}, {} {}, align {}\n'.format(
                current_var, var_type.replace('*', ''), var_type, var, align_val)

            self.setVarType(current_var, var_type.replace('*', ''))

        return current_var
    # END AUXILIARY FUNCTIONS

    def visitFiile(self, ctx:CymbolParser.FiileContext):
        self.visitChildren(ctx)
        print(self.program)

    def visitVarDecl(self, ctx: CymbolParser.VarDeclContext):
        var_name = '%' + ctx.ID().getText()
        var_type = ctx.tyype().getText()

        # Add line with variable allocation.
        self.program += "\t{0} = alloca ".format(var_name)
        if var_type == Type.INT:
            var_type = 'i32'
            self.vars_data[self.func_name][var_name] = 'i32*'
            self.program += "i32, align 4\n"
        elif var_type == Type.FLOAT:
            var_type = 'float'
            self.vars_data[self.func_name][var_name] = 'float*'
            self.program += "float, align 4\n"
        elif var_type == Type.BOOLEAN:
            var_type = 'i1'
            self.vars_data[self.func_name][var_name] = 'i1*'
            self.program += "i1, align 1\n"
        if ctx.expr() != None:
            expr_result = ctx.expr().accept(self)

            # If the last var is a temporary variable
            if isinstance(expr_result, int):
                expr_result = '%' + str(expr_result)

            align = 1 if var_type == 'i1' else 4
            # If not then it's an int, bolean or float
            self.program += "\tstore {} {}, {}* {}, align {}\n".format(
                var_type, expr_result, var_type, var_name, align)

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
            self.program += "i1 "

        self.program += "@{0}(".format(self.func_name)
        if ctx.paramTypeList() != None:
            self.program += ctx.paramTypeList().accept(self)
        self.program += ") {\n"
        ctx.block().accept(self)
        self.program += "}\n"

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
            param_type = "i1 "

        # Add var to dict
        self.vars_data[self.func_name][param_name] = param_type

        return param_type + param_name

    def visitReturnStat(self, ctx: CymbolParser.ReturnStatContext):
        return_stat = "\tret "
        return_type = self.functions_data[self.func_name][0]

        if return_type == Type.INT:
            return_stat += "i32 "
            return_type = "i32"
        elif return_type == Type.FLOAT:
            return_stat += "float "
            return_type = "float"
        elif return_type == Type.BOOLEAN:
            return_stat += "i1 "
            return_type = "i1"

        return_var = ctx.expr().accept(self)
        return_var_type = self.getVarType(return_var, ctx.expr())

        if (isinstance(return_var, int)):
            return_var = '%' + str(return_var)

        current_var = self.loadVariable(return_var, return_var_type)

        if current_var is not None:
            return_var = current_var

        self.program += return_stat + return_var + "\n"

    def visitAssignStat(self, ctx: CymbolParser.AssignStatContext):
        var_id = '%' + ctx.ID().getText()

        var_type = self.getVarType(var_id, ctx).replace('*', '')
        expr_result = ctx.expr().accept(self)
        expr_result_type = self.getVarType(expr_result, ctx.expr())

        expr_result_value = self.loadVariable(expr_result, expr_result_type)

        if expr_result_value is None:
            expr_result_value = expr_result

        # store the value of the expr result where it should be stored
        # TODO: Store variable types as pointers too when necessary
        self.program += '\tstore {} {}, {} {}, align 4\n'.format(
            expr_result_type, expr_result_value, var_type, var_id)

        return var_id

    # START EXPRESSIONS
    # Note: In case expressions return the last temp variable used
    # their type MUST be an int!!!
    def visitIntExpr(self, ctx: CymbolParser.VarIdExprContext):
        return ctx.INT().getText()

    def visitFloatExpr(self, ctx: CymbolParser.VarIdExprContext):
        return self.float_to_hex(float(ctx.FLOAT().getText()))

    def visitBooleanExpr(self, ctx: CymbolParser.VarIdExprContext):
        return '1' if ctx.BOOLEAN().getText() == 'true' else '0'

    def visitVarIdExpr(self, ctx: CymbolParser.VarIdExprContext):
        return '%' + ctx.ID().getText()

    def visitSignedExpr(self, ctx: CymbolParser.SignedExprContext):
        # get last variable number
        expr_result = ctx.expr().accept(self)

        if isinstance(expr_result, int):
            expr_result = '%' + str(expr_result)

        if ctx.op.text == '+':  # Nothing to do, just accept the next expressions
            return self.visitChildren(ctx)

        # if it's just a negative number
        elif ctx.op.text == '-' and (hasattr(ctx.expr(), 'INT') or hasattr(ctx.expr(), 'FLOAT')):
            expr_result = '-' + expr_result
        elif ctx.op.text == '-':
            current_var = self.getNextVar()
            last_var_type = self.getVarType(expr_result, ctx.expr())

            self.program += '\t%{} = sub nsw {} 0, {}, align 4\n'.format(
                current_var, last_var_type, expr_result
            )

            # set current var's type to be the same as the last var's type
            self.setVarType(current_var, last_var_type)
            return current_var
        return expr_result

    # helper function for both EqExpr and ComparisionExpr
    def visitAnyComparisonExpr(self, ctx):
        [(left_operand, left_operand_type),
         (right_operand, _)] = self.getExprOper(ctx)

        # Defining operation type
        if ctx.op.text == '==':
            condition = 'eq'
        elif ctx.op.text == '!=':
            condition = 'ne'
        elif ctx.op.text == '>':
            condition = 'gt'
        elif ctx.op.text == '>=':
            condition = 'ge'
        elif ctx.op.text == '<':
            condition = 'lt'
        elif ctx.op.text == '<=':
            condition = 'le'

        # Defining instruction type
        if left_operand_type.startswith('i'):  # Comparing ints or booleans
            instruction = 'icmp'
            if condition not in ['eq', 'ne']:
                condition = 's' + condition  # Operations are signed
        else:  # Comparing floats
            instruction = 'fcmp'
            condition = 'o' + condition  # Operations are ordered

        current_var = self.getNextVar()
        self.setVarType('%' + str(current_var), 'i1')

        self.program += '\t%{} = {} {} {} {}, {}\n'.format(
            current_var, instruction, condition, left_operand_type,
            left_operand, right_operand)

        return current_var

    def visitComparisonExpr(self, ctx: CymbolParser.ComparisonExprContext):
        return self.visitAnyComparisonExpr(ctx)

    def visitEqExpr(self, ctx: CymbolParser.EqExprContext):
        return self.visitAnyComparisonExpr(ctx)

    def visitAndOrExpr(self, ctx: CymbolParser.AndOrExprContext):
        [(left_operand, left_operand_type),
         (right_operand, _)] = self.getExprOper(ctx)

        current_var = self.getNextVar()
        self.setVarType('%' + str(current_var), left_operand_type)
        if(ctx.op.text == '&&'):
            operation = 'and'
        else:
            operation = 'or'

        self.program += '\t%{} = {} i1 {}, {}\n'.format(
            current_var, operation, left_operand, right_operand)

        return current_var

    def visitParenthesisExpr(self, ctx: CymbolParser.ParenthesisExprContext):
        return ctx.expr().accept(self)

    def visitMulDivExpr(self, ctx:CymbolParser.MulDivExprContext):
        [(left_operand, left_operand_type),
         (right_operand, right_operand_type)] = self.getExprOper(ctx)

        current_var = self.getNextVar()

        if 'float' in left_operand_type or 'float' in right_operand_type:
            current_var_type = 'float'
        else:
            current_var_type = 'i32'
        self.setVarType('%' + str(current_var), current_var_type)

        # Adds instruction to cast the integer variable to float.
        if 'i32' in left_operand_type and 'float' in right_operand_type:
            self.program += '\t%{} = sitofp i32 {} to float\n'.format(current_var, left_operand)
            left_operand = '%' + current_var
            current_var = self.getNextVar()
        elif 'i32' in right_operand_type and 'float' in left_operand_type:
            self.program += '\t%{} = sitofp i32 {} to float\n'.format(current_var, right_operand)
            right_operand = '%' + current_var
            current_var = self.getNextVar()

        # Based on the result type the compiler decides which instruction
        # should be used.
        if ctx.op.text == '*' and current_var_type == 'i32':
            operation = 'mul nsw'
        elif ctx.op.text == '*' and current_var_type == 'float':
            operation = 'fmul float'
        elif ctx.op.text == '/' and current_var_type == 'i32':
            operation = 'sdiv i32'
        elif ctx.op.text == '/' and current_var_type == 'float':
            operation = 'fdiv float'

        self.program += '\t%{} = {} {}, {}\n'.format(
            current_var, operation, left_operand, right_operand)

        return current_var

    def visitAddSubExpr(self, ctx:CymbolParser.AddSubExprContext):
        [(left_operand, left_operand_type),
         (right_operand, right_operand_type)] = self.getExprOper(ctx)

        current_var = self.getNextVar()

        if 'float' in left_operand_type or 'float' in right_operand_type:
            current_var_type = 'float'
        else:
            current_var_type = 'i32'
        self.setVarType('%' + str(current_var), current_var_type)

        # Adds instruction to cast the integer variable to float.
        if 'i32' in left_operand_type and 'float' in right_operand_type:
            self.program += '\t%{} = sitofp i32 {} to float\n'.format(current_var, left_operand)
            left_operand = '%' + str(current_var)
            current_var = self.getNextVar()
        elif 'i32' in right_operand_type and 'float' in left_operand_type:
            self.program += '\t%{} = sitofp i32 {} to float\n'.format(current_var, right_operand)
            right_operand = '%' + str(current_var)
            current_var = self.getNextVar()

        if ctx.op.text == '+' and current_var_type == 'i32':
            operation = 'add nsw i32'
        elif ctx.op.text == '+' and current_var_type == 'float':
            operation = 'fadd float'
        elif ctx.op.text == '-' and current_var_type == 'i32':
            operation = 'sub nsw i32'
        elif ctx.op.text == '-' and current_var_type == 'float':
            operation = 'fsub float'

        self.program += '\t%{} = {} {}, {}\n'.format(
            current_var, operation, left_operand, right_operand)

        return current_var

    def visitNotExpr(self, ctx:CymbolParser.NotExprContext):
        expr_result = ctx.expr().accept(self)
        expr_result_type = self.getVarType(expr_result, ctx.expr())
        operand = self.loadVariable(expr_result, expr_result_type)

        current_var = self.getNextVar()
        self.program += '\t%{} = xor i1 {}, true\n'.format(current_var, operand)

        return current_var

    def visitFunctionCallExpr(self, ctx:CymbolParser.FunctionCallExprContext):
        func_args = []

        if ctx.exprList() is not None:
            func_args = ctx.exprList().accept(self)

        func_args = ','.join(func_args)
        func_called_name = ctx.ID().getText()
        func_called_ret_type = self.functions_data[func_called_name][0]
        current_var = self.getNextVar()
        self.setVarType('%' + str(current_var), func_called_ret_type)

        self.program += '\t%{} = call {} @{}({})\n'.format(current_var,
            func_called_ret_type, func_called_name, func_args)

        return current_var

    def visitExprList(self, ctx:CymbolParser.ExprListContext):
        expr_list = []

        if isinstance(ctx.expr(), list):
            for e in ctx.expr():
                expr_result = e.accept(self)
                expr_result_type = self.getVarType(expr_result, e).replace('*', '')
                expr_list.append(expr_result_type + ' ' + str(expr_result))
        else:
            expr_result = ctx.expr().accept(self)
            expr_result_type = self.getVarType(expr_result, ctx.expr())
            expr_list.append(expr_result_type + ' ' + str(expr_result))

        return expr_list
