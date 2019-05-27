# Generated from antlr4-python3-runtime-4.7.2/src/autogen/Cymbol.g4 by ANTLR 4.7.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .CymbolParser import CymbolParser
else:
    from CymbolParser import CymbolParser

# This class defines a complete generic visitor for a parse tree produced by CymbolParser.

class CymbolVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by CymbolParser#fiile.
    def visitFiile(self, ctx:CymbolParser.FiileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CymbolParser#varDecl.
    def visitVarDecl(self, ctx:CymbolParser.VarDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CymbolParser#tyype.
    def visitTyype(self, ctx:CymbolParser.TyypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CymbolParser#funcDecl.
    def visitFuncDecl(self, ctx:CymbolParser.FuncDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CymbolParser#paramTypeList.
    def visitParamTypeList(self, ctx:CymbolParser.ParamTypeListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CymbolParser#paramType.
    def visitParamType(self, ctx:CymbolParser.ParamTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CymbolParser#block.
    def visitBlock(self, ctx:CymbolParser.BlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CymbolParser#assignStat.
    def visitAssignStat(self, ctx:CymbolParser.AssignStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CymbolParser#returnStat.
    def visitReturnStat(self, ctx:CymbolParser.ReturnStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CymbolParser#ifElseStat.
    def visitIfElseStat(self, ctx:CymbolParser.IfElseStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CymbolParser#ifElseExprStat.
    def visitIfElseExprStat(self, ctx:CymbolParser.IfElseExprStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CymbolParser#ifStat.
    def visitIfStat(self, ctx:CymbolParser.IfStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CymbolParser#elseStat.
    def visitElseStat(self, ctx:CymbolParser.ElseStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CymbolParser#exprStat.
    def visitExprStat(self, ctx:CymbolParser.ExprStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CymbolParser#exprList.
    def visitExprList(self, ctx:CymbolParser.ExprListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CymbolParser#stat.
    def visitStat(self, ctx:CymbolParser.StatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CymbolParser#FloatExpr.
    def visitFloatExpr(self, ctx:CymbolParser.FloatExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CymbolParser#ParenthesisExpr.
    def visitParenthesisExpr(self, ctx:CymbolParser.ParenthesisExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CymbolParser#ComparisonExpr.
    def visitComparisonExpr(self, ctx:CymbolParser.ComparisonExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CymbolParser#AndOrExpr.
    def visitAndOrExpr(self, ctx:CymbolParser.AndOrExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CymbolParser#SignedExpr.
    def visitSignedExpr(self, ctx:CymbolParser.SignedExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CymbolParser#FunctionCallExpr.
    def visitFunctionCallExpr(self, ctx:CymbolParser.FunctionCallExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CymbolParser#MulDivExpr.
    def visitMulDivExpr(self, ctx:CymbolParser.MulDivExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CymbolParser#EqExpr.
    def visitEqExpr(self, ctx:CymbolParser.EqExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CymbolParser#NotExpr.
    def visitNotExpr(self, ctx:CymbolParser.NotExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CymbolParser#IntExpr.
    def visitIntExpr(self, ctx:CymbolParser.IntExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CymbolParser#AddSubExpr.
    def visitAddSubExpr(self, ctx:CymbolParser.AddSubExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CymbolParser#VarIdExpr.
    def visitVarIdExpr(self, ctx:CymbolParser.VarIdExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CymbolParser#BooleanExpr.
    def visitBooleanExpr(self, ctx:CymbolParser.BooleanExprContext):
        return self.visitChildren(ctx)



del CymbolParser