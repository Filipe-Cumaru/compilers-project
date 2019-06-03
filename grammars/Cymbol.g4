grammar Cymbol;

//Lexer
fragment NUMBER    : [0-9];
fragment LETTER    : [a-zA-Z];

TYPEINT  : 'int';
TYPEFLOAT  : 'float';
TYPEBOOLEAN : 'boolean';

IF     : 'if';
ELSE   : 'else';
RETURN : 'return';

LP        : '(';
RP        : ')';
COMMA     : ',';
SEMICOLON : ';';
LB        : '{';
RB        : '}';

AS    : '=';
EQ    : '==';
NE    : '!=';
NOT   : '!';
GT    : '>';
LT    : '<';
GE    : '>=';
LE    : '<=';
MUL   : '*';
DIV   : '/';
PLUS  : '+';
MINUS : '-';
AND   : '&&';
OR    : '||';

BOOLEAN:  'true' | 'false';
ID  : (LETTER) (LETTER | NUMBER)*;
INT : NUMBER+;
FLOAT:  NUMBER+ '.' NUMBER+;

BLOCKCOMMENT : '/*' .*? '*/' -> skip;
LINECOMMENT  : '//' .*? '\n' -> skip;
WS           : [ \t\n\r]+ -> skip;

//Parser
fiile : (funcDecl | varDecl)+ EOF?
     ;

varDecl : tyype ID ('=' expr)? ';'
        ;

tyype : TYPEINT
     | TYPEFLOAT
     | TYPEBOOLEAN
     ;

funcDecl : tyype ID '(' paramTypeList? ')' block
         ;

paramTypeList : paramType (',' paramType)*
              ;

paramType : tyype ID
          ;

block : '{' stat* '}'
      ;

assignStat : ID '=' expr ';'
           ;

returnStat : 'return' expr? ';'
           ;

ifElseStat : ifStat (elseStat)?
           ;

ifElseExprStat : block
               | ifElseStat
               | returnStat
               | assignStat
               | exprStat
               ;

ifStat : 'if' '(' expr ')' ifElseExprStat
       ;

elseStat : 'else' ifElseExprStat
         ;

exprStat : expr ';'
         ;

exprList : expr (',' expr)*
         ;

stat : varDecl
     | ifElseStat
     | returnStat
     | assignStat
     | exprStat
     ;

expr : ID '(' exprList? ')'                      #FunctionCallExpr 4
     | op=('+' | '-') expr                       #SignedExpr 3
     | '!' expr                                  #NotExpr 2
     | expr op=('<' | '>' | '<=' | '>=') expr    #ComparisonExpr 6
     | expr op=('*' | '/') expr                  #MulDivExpr 3
     | expr op=('+' | '-') expr                  #AddSubExpr 3
     | expr op=('&&'| '||') expr                 #AndOrExpr 2
     | expr op=('=='| '!=') expr                 #EqExpr 2
     | ID                                        #VarIdExpr 2
     | INT                                       #IntExpr 1
     | FLOAT                                     #FloatExpr 1
     | BOOLEAN                                   #BooleanExpr 1
     | '(' expr ')'                              #ParenthesisExpr 1
     ;
