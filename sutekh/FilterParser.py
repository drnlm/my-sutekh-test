# FilterParser.py
# Copyright Neil Muller <drnlmuller+sutekh@gmail.com>, 2007
# GPL - see COPYING for details

import ply.lex as lex
import ply.yacc as yacc
from sutekh.Filters import MultiCardTypeFilter, MultiClanFilter, \
        MultiDisciplineFilter, MultiGroupFilter, MultiCapacityFilter,\
        MultiCostFilter, MultiLifeFilter, MultiCreedFilter, MultiVirtueFilter,\
        CardTextFilter, CardNameFilter, MultiSectFilter, MultiTitleFilter,\
        MultiExpansionRarityFilter, MultiDisciplineLevelFilter, \
        FilterAndBox, FilterOrBox
from sutekh.SutekhObjects import Clan, Discipline, CardType, Title,\
                                 Creed, Virtue, Sect, Expansion, Rarity,\
                                 RarityPair, IExpansion

# FIXME: The intention is to push this into the Individual Filter Objects

dFilterParts = {
        "CardType" : [MultiCardTypeFilter, "Card Type"],
        "Clan" : [MultiClanFilter, "Clan"],
        "Discipline" : [MultiDisciplineFilter, "Discipline"],
        "Group" : [MultiGroupFilter, "Group"],
        "Capacity" : [MultiCapacityFilter, "Capacity"],
        "Cost" : [MultiCostFilter, "Cost"],
        "Life" : [MultiLifeFilter, "Life"],
        "Creed" : [MultiCreedFilter, "Creed"],
        "Virtue" : [MultiVirtueFilter, "Virtue"],
        "CardText" : [CardTextFilter, "Card Text"],
        "CardName" : [CardNameFilter, "Card Name"],
        "Sect" : [MultiSectFilter, "Sect" ],
        "Title" : [MultiTitleFilter, "Title" ],
        "Expansion_with_Rarity" : [MultiExpansionRarityFilter, "Expansion with Rarity"],
        "Discipline_with_Level" : [MultiDisciplineLevelFilter, "Discipline with Level"]
        }

# These should be elsewhere
aEntryFilters =   ['CardText','CardName']

def getValues(sFilterType):
    """Return a list of values to fill the selection dialog, or
       None if the input should be a text string"""
    if sFilterType in aEntryFilters:
        return None
    elif sFilterType == "Clan":
        return [x.name for x in Clan.select().orderBy('name')]
    elif sFilterType == "Discipline":
        return [x.fullname for x in Discipline.select().orderBy('name')]
    elif sFilterType == "Group":
        return range(1,6)
    elif sFilterType == "Capacity":
        return range(1,12)
    elif sFilterType == "Cost":
        return range(0,7)+['X']
    elif sFilterType == "CostType":
        return ["blood","pool","conviction"]
    elif sFilterType == "Life":
        return range(1,8)
    elif sFilterType == "Creed":
        return [x.name for x in Creed.select().orderBy('name')]
    elif sFilterType == "Virtue":
        return [x.fullname for x in Virtue.select().orderBy('name')]
    elif sFilterType == "Sect":
        return [x.name for x in Sect.select().orderBy('name')]
    elif sFilterType == "Title":
        return [x.name for x in Title.select().orderBy('name')]
    elif sFilterType == "CardType":
        return [x.name for x in CardType.select().orderBy('name')]
    elif sFilterType == 'Expansion_with_Rarity':
        aExpansions=[x.name for x in Expansion.select().orderBy('name')
                if x.name[:5]!='Promo']
        aResults=[]
        for sExpan in aExpansions:
            oE=IExpansion(sExpan)
            aRarities=[x.rarity.name for x in RarityPair.selectBy(expansion=oE)]
            for sRarity in aRarities:
                aResults.append(sExpan+' with '+sRarity)
        return aResults
    elif sFilterType == 'Discipline_with_Level':
        aDisciplines=getValues('Discipline')
        aResults=[]
        for disc in aDisciplines:
            aResults.append(disc+' with inferior')
            aResults.append(disc+' with superior')
        return aResults
    else:
        raise RuntimeError("Unknown Filter Type %s" % sFilterType)

# We define an object for the lex parser

class ParseFilterDefinitions(object):
    tokens = (
            'FILTERTYPE',
            'ID',
            'INTEGER',
            'STRING',
            'OR',
            'AND',
            'COMMA',
            'IN',
            'LPAREN',
            'RPAREN',
            'VARIABLE',
            'WITH',
            )

    t_AND=r'\&\&'
    t_OR=r'\|\|'
    t_STRING=r'\".*?\"'
    t_INTEGER=r'-?\d+'
    t_COMMA=r','
    t_IN=r'='
    t_LPAREN=r'\('
    t_RPAREN=r'\)'

    # Ignore whitespace and returns
    t_ignore=' \t\n'

    # Simplistic error handler
    def t_error(self,t):
        raise ValueError("Illegal Character '%s'" % t.value[0])

    def t_ID(self,t):
        r'[A-Za-z$_]+'
        if t.value in dFilterParts.keys():
            t.type='FILTERTYPE'
        elif t.value.lower() == 'and':
            t.type='AND'
        elif t.value.lower() == 'or':
            t.type='OR'
        elif t.value.lower() == 'in':
            t.type='IN'
        elif t.value[0] == '$':
            t.type='VARIABLE'
        elif t.value.lower() == 'with':
            t.type='WITH'
        else:
            t.type='STRING'
        return t

    # Ply docs say don't do this in __init__, so we don't
    def build(self,**kwargs):
        self.lexer=lex.lex(object=self,**kwargs)

    def apply(self,data):
        self.lexer.input(data)
        aResults=[]
        while 1:
            tok=self.lexer.token()
            if not tok: return aResults
            aResults.append(tok)

# Define a yacc parser to produce the abstract syntax tree

class FilterYaccParser(object):
    tokens=ParseFilterDefinitions.tokens

    # COMMA's have higher precedence than AND + OR
    # This shut's up most shift/reduce warnings
    precedence=(
            ('left','AND','OR'),
            ('left','IN'),
            ('left','COMMA'),
            ('left','WITH')
    )

    def p_filter(self,p):
        """filter : filterpart
                  | empty
        """
        p[0] = FilterNode(p[1])

    def p_filterpart_brackets(self,p):
        """filterpart : LPAREN filterpart RPAREN"""
        p[0]=p[2]

    def p_filterpart_AND(self,p):
        """filterpart : filterpart AND filterpart"""
        p[0] = BinOpNode(p[1],'and',p[3])

    def p_filterpart_OR(self,p):
        """filterpart : filterpart OR filterpart"""
        p[0] = BinOpNode(p[1],'or',p[3])

    def p_filterpart_filtertype(self,p):
        """filterpart : FILTERTYPE IN expression"""
        p[0]=FilterPartNode(p[1],p[3])

    def p_filterpart_var(self,p):
        """filterpart : FILTERTYPE IN VARIABLE"""
        p[0]=FilterPartNode(p[1],None)

    def p_expression_comma(self,p):
        """expression : expression COMMA expression"""
        p[0]=CommaNode(p[1],p[2],p[3])

    def p_expression_string(self,p):
        """expression : STRING"""
        p[0]=StringNode(p[1])

    def p_expression_integer(self,p):
        """expression : INTEGER"""
        p[0]=IntegerNode(int(p[1]))

    def p_expression_id(self,p):
        """expression : ID"""
        # Shouldn't actually trigger this rule with a legal filter string
        raise ValueError("Invalid filter element: "+str(p[1]))

    def p_expression_with(self,p):
        """expression : expression WITH expression"""
        p[0]=WithNode(p[1],p[2],p[3])

    def p_empty(self,p):
        """empty :"""
        p[0]=None

    def p_error(self,p):
        if p is None:
            raise ValueError("Invalid filter syntax: No valid identifier")
        else:
            raise ValueError("Invalid filter syntax: "+str(p.value))

# Wrapper objects around the parser

class FilterParser(object):
    def __init__(self):
        self.oLexer = ParseFilterDefinitions()
        self.oLexer.build()
        # yacc needs an initialised lexer
        self.oParser = yacc.yacc(module=FilterYaccParser())

    def apply(self,str):
        oAST=self.oParser.parse(str)
        return oAST

# Object used by getValues representation
# Should be made more robust

class ValueObject(object):
    def __init__(self,oValue,oNode):
        self.value = oValue
        self.node = oNode

    def isEntry(self):
        return self.value is None

    def isList(self):
        return type(self.value) is list

    def isValue(self):
        return type(self.value) is str

# AST object (formulation inspired by Simon Cross's example, and notes
# from the ply documentation)

class AstBaseNode(object):
    def __init__(self,children):
        self.children = children

    def __str__(self):
        sAttrs = '('+",".join([ str(value) for key,value \
                in self.__dict__.items() if not key.startswith("_") and \
                key != "children" and value not in self.children])+")"
        s=self.__class__.__name__ + sAttrs
        for child in self.children:
            s+="\n" + "\n".join(["\t" + x for x in str(child).split("\n")])
        return s

    def getValues(self):
        pass

    def getFilter(self):
        pass

    def getInvalidValues(self):
        pass

class FilterNode(AstBaseNode):
    def __init__(self,expression):
        super(FilterNode,self).__init__([expression])
        self.expression = expression

    def getValues(self):
        return self.expression.getValues()

    def getFilter(self):
        return self.expression.getFilter()

    def getInvalidValues(self):
        return self.expression.getInvalidValues()

class OperatorNode(AstBaseNode):
    pass

class TermNode(AstBaseNode):
    pass

class StringNode(TermNode):
    def __init__(self,value):
        super(StringNode,self).__init__([value])
        # Strip quotes off strings
        if value[0]=='"' and value[-1]=='"':
            self.value=value[1:-1]
        else:
            self.value=value

    def getValues(self):
        return [ValueObject(self.value,self)]

    def getFilter(self):
        return [self.value]

class IntegerNode(TermNode):
    def __init__(self,value):
        super(IntegerNode,self).__init__([value])
        self.value=value

    def getValues(self):
        return [ValueObject(str(self.value),self)]

    def getFilter(self):
        return [self.value]

class IdNode(TermNode):
    def __init__(self,value):
        super(IdNode,self).__init__([value])
        self.value=value

    def getValues(self):
        return None

    def getFilter(self):
        return None

class FilterPartNode(OperatorNode):
    def __init__(self,filtertype,filtervalues):
        super(FilterPartNode,self).__init__([filtertype,filtervalues])
        self.filtertype=filtertype
        self.filtervalues=filtervalues

    def getValues(self):
        if self.filtertype in aEntryFilters:
            aResults=[ValueObject(dFilterParts[self.filtertype][1]+' includes',self)]
        else:
            aResults=[ValueObject(dFilterParts[self.filtertype][1]+' in',self)]
        if self.filtervalues is None:
            aVals=getValues(self.filtertype)
            # Want a list within ValueObject for the GUI stuff to work
            # None case for Entry boxes works as well
            aResults.append(ValueObject(aVals,self))
        else:
            aResults.extend(self.filtervalues.getValues())
        return aResults

    def getInvalidValues(self):
        aRes=[]
        if self.filtervalues is None or self.filtertype in aEntryFilters:
            return None
        aCurVals=self.filtervalues.getValues()
        aValidVals=getValues(self.filtertype)
        for oVal in aCurVals:
            if oVal.value not in aValidVals:
                aRes.append(oVal.value)
        if len(aRes)>0:
            return aRes
        else:
            return None

    def setValues(self,aVals):
        if self.filtervalues is not None:
            raise RuntimeError("Filter values already set")
        sCommaList=",".join(aVals)
        sInternalFilter=self.filtertype+'='+sCommaList
        oP=FilterParser()
        oInternalAST=oP.apply(sInternalFilter)
        # The filter we create is trivially of the FilterType=X,Y type
        # so this is safe, but potentially fragile in the future
        self.filtervalues=oInternalAST.children[0].filtervalues
        # Update AST to reflect change
        self.children[1]=self.filtervalues

    def getFilter(self):
        if self.filtervalues is None:
            return None
        aValues=self.filtervalues.getFilter()
        FilterType=dFilterParts[self.filtertype][0]
        if self.filtertype in aEntryFilters:
            # FIXME: Don't quite like special casing this here - MultiCardText?
            # aValues[0] is a fragile assumption - join?
            oFilter=FilterType(aValues[0])
        else:
            oFilter=FilterType(aValues)
        return oFilter

class BinOpNode(OperatorNode):
    def __init__(self,left,op,right):
        super(BinOpNode,self).__init__([left,right])
        self.op=op
        self.left=left
        self.right=right

    def getInvalidValues(self):
        aLeft=self.left.getInvalidValues()
        aRight=self.right.getInvalidValues()
        if aLeft is None:
            return aRight
        elif aRight is None:
            return aLeft
        else:
            return aLeft+aRight

    def getValues(self):
        aLeft=self.left.getValues()
        aRight=self.right.getValues()
        if aLeft is None:
            return aRight
        elif aRight is None:
            return aLeft
        else:
            # Add the extra brackets so the display in the dialog
            # reflects the correct precedence
            aResults=[ValueObject('(',None)]+aLeft+\
                    [ValueObject(') '+self.op+' (',self)]+\
                    aRight+[ValueObject(')',None)]
            return aResults

    def getFilter(self):
        oLeftFilter=self.left.getFilter()
        oRightFilter=self.right.getFilter()
        if oLeftFilter is None:
            return oRightFilter
        elif oRightFilter is None:
            return oLeftFilter
        if self.op == 'and':
            oFilter=FilterAndBox([oLeftFilter,oRightFilter])
        elif self.op == 'or':
            oFilter=FilterOrBox([oLeftFilter,oRightFilter])
        else:
            raise RuntimeError('Unknown operator in AST')
        return oFilter

class CommaNode(OperatorNode):
    def __init__(self,left,op,right):
        super(CommaNode,self).__init__([left,right])
        self.op=op
        self.left=left
        self.right=right

    def getValues(self):
        aResults=self.left.getValues()
        aResults.append(ValueObject(',',self))
        aResults.extend(self.right.getValues())
        return aResults

    def getFilter(self):
        aResults=self.left.getFilter()
        aResults.extend(self.right.getFilter())
        return aResults

class WithNode(OperatorNode):
    def __init__(self,left,op,right):
        super(WithNode,self).__init__([left,right])
        self.op=op
        self.left=left
        self.right=right

    def getValues(self):
        return [ValueObject(self.left.getFilter()[0]+' '+self.op+' '+self.right.getFilter()[0],self)]

    def getFilter(self):
        return [(self.left.getFilter()[0],self.right.getFilter()[0])]
