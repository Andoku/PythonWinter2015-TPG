#!/usr/bin/python
# coding: utf

import readline
import sys
import tpg
import itertools

def make_op(s):
    return {
        '+': lambda x,y: x+y,
        '-': lambda x,y: x-y,
        '*': lambda x,y: x*y,
        '/': lambda x,y: x/y,
        '&': lambda x,y: x&y,
        '|': lambda x,y: x|y,
    }[s]

def isMatrix(x):
    if type(x) is not Vector: return False
    if len(x) < 1: return False
    for s in x:
        if not isSimpleVector(s): return False
    d = len(x[0])
    for s in x:
        if len(s) != d: return False
    return True

def isSimpleVector(x):
    if type(x) is not Vector: return False
    for e in x:
        if not isinstance(e, (int, long, float)): return False
    return True

class Vector(list):
    def __init__(self, *argp, **argn):
        list.__init__(self, *argp, **argn)

    def __str__(self):
        if isSimpleVector(self):
            return "|" + " ".join(str(c) for c in self) + "|"
        elif isMatrix(self):
            res, lens = "", []
            for j in xrange(len(self[0])):
                lens.append(0)
                for i in xrange(len(self)):
                    l = len(str(self[i][j])) 
                    if l > lens[j]: lens[j] = l 
            for s in self:
                res += "|" + " ".join(" " * (lens[j] - len(str(s[j]))) + str(s[j]) for j in xrange(len(s))) + "|\n"
            return res[0:-1]
        return "[" + " ".join(str(c) for c in self) + "]"

    def __op(self, a, op):
        try:
            return self.__class__(op(s,e) for s,e in zip(self, a))
        except TypeError:
            return self.__class__(op(c,a) for c in self)

    def __add__(self, a): return self.__op(a, lambda c,d: c+d)
    def __sub__(self, a): return self.__op(a, lambda c,d: c-d)
    def __div__(self, a): return self.__op(a, lambda c,d: c/d)
    def __mul__(self, a):
        if isSimpleVector(self) and isSimpleVector(a):
            if len(self) == len(a):
                return self.__and__(a)
        elif isMatrix(self) and isMatrix(a):
            d1 = (len(self), len(self[0]))
            d2 = (len(a), len(a[0]))
            if d1[0] != d2[1] and d1[1] != d2[0]:
                print "Wrong dimensions for matrix multiplication."
                return None
            res = Vector()
            for i in xrange(d1[0]):
                res.append([])
                for j in xrange(d1[1]):
                    e = 0
                    for k in xrange(d1[1]):
                        e += self[i][k] * a[k][j]
                    res[i].append(e)
            return res
        print "Operation is not supported."
        return None

    def __and__(self, a):
        try:
            return reduce(lambda s, (c,d): s+c*d, zip(self, a), 0)
        except TypeError:
            return self.__class__(c and a for c in self)

    def __or__(self, a):
        try:
            return self.__class__(itertools.chain(self, a))
        except TypeError:
            return self.__class__(c or a for c in self)

class Calc(tpg.Parser):
    r"""

    separator spaces: '\s+' ;
    separator comment: '#.*' ;

    token fnumber: '\d+[.]\d*' float ;
    token number: '\d+' int ;
    token op1: '[|&+-]' make_op ;
    token op2: '[*/]' make_op ;
    token id: '\w+' ;

    START/e -> Operator $e=None$ | Expr/e | $e=None$ ;
    Operator -> Assign ;
    Assign -> id/i '=' Expr/e $Vars[i]=e$ ;
    Expr/t -> Fact/t ( op1/op Fact/f $t=op(t,f)$ )* ;
    Fact/f -> Atom/f ( op2/op Atom/a $f=op(f,a)$ )* ;
    Atom/a ->   Vector/a
              | id/i ( check $i in Vars$ | error $"Undefined variable '{}'".format(i)$ ) $a=Vars[i]$
              | fnumber/a
              | number/a
              | '\(' Expr/a '\)' ;
    Vector/$Vector(a)$ -> '\[' '\]' $a=[]$ | '\[' Atoms/a '\]' ;
    Atoms/v -> Atom/a Atoms/t $v=[a]+t$ | Atom/a $v=[a]$ ;

    """

calc = Calc()
Vars={}
PS1='--> '

def calculate(line):
    try:
        res = calc(line)
    except tpg.Error as exc:
        print >> sys.stderr, exc
        res = None
    if res != None:
        print res

if len(sys.argv) == 2:
    f = open(sys.argv[1], 'r')
    for line in f:
        calculate(line)
    sys.exit(0)
    
Stop=False
while not Stop:
    try:
        line = raw_input(PS1)
    except EOFError:
        print
        break
    except KeyboardInterrupt:
        print
        break
    calculate(line) 
