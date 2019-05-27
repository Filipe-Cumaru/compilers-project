from antlr4 import *
from autogen.CymbolParser import CymbolParser
from autogen.CymbolVisitor import CymbolVisitor

class CymbolCheckerVisitor (CymbolVisitor):

    def visitVarDecl(self, ctx:CymbolParser.VarDeclContext):
        return self.visitChildren(ctx)
