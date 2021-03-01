from __future__ import annotations
from typing import List, Union


class Term(object):
    def __init__(self, symbol: Union[ConstantSymbol, FunctionalSymbol, Variable], param: List[Term] = None):

        if (isinstance(symbol, ConstantSymbol) or isinstance(symbol, Variable)) and param is not None:
            raise Exception("constant symbol or variable should not have param")

        if isinstance(symbol, FunctionalSymbol) and (param is None or len(param) != symbol.ar):
            raise Exception("functional symbol with incorrect number of param")

        self.symbol = symbol
        self.param = param

    def __repr__(self):
        return f"Term({self.symbol!r}, {self.param!r})"


class Symbol(object):
    def __init__(self, name: str, ar: int):
        self.name = name
        self.ar = ar

    def __repr__(self):
        return f"Symbol({self.name!r}, {self.ar!r})"


class ConstantSymbol(Symbol, Term):
    def __init__(self, name: str):
        Symbol.__init__(self, name, 0)
        Term.__init__(self, self)

    def __repr__(self) -> str:
        return f"ConstantSymbol({self.name!r})"


class FunctionalSymbol(Symbol, Term):
    def __init__(self, name: str, ar: int):
        Symbol.__init__(self, name, ar)
        Term.__init__(self, self)

    def __repr__(self) -> str:
        return f"FunctionalSymbol({self.name!r}, {self.ar!r})"


class PredicateSymbol(Symbol):
    def __init__(self, name: str, ar: int):
        super().__init__(name, ar)

    def __repr__(self) -> str:
        return f"PredicateSymbol({self.name!r}, {self.ar!r})"

    def __call__(self, *param: Term) -> AtomicFormula:
        return AtomicFormula(self, list(param))


class Variable(Symbol, Term):
    def __init__(self, name: str):
        Symbol.__init__(self, name, 0)
        Term.__init__(self, self)

    def __repr__(self):
        return f"Variable({self.name!r})"


class Formula(object):
    def __init__(self, content: Union[AtomicFormula, FoLOperator]):
        if not (isinstance(content, AtomicFormula) or isinstance(content, FoLOperator)):
            raise Exception("formula init error", type(content))

        self.content = content

    def __repr__(self):
        return f"Formula({self.content!r})"


class AtomicFormula(Formula):
    def __init__(self, symbol: PredicateSymbol, param: List[Term]):

        if not isinstance(symbol, PredicateSymbol):
            raise Exception("incorrect atomic formula init")

        if param is None or len(param) != symbol.ar:
            raise Exception("functional symbol with incorrect number of param")

        self.symbol = symbol
        self.param = param

        super().__init__(self)

    def __repr__(self):
        return f"AtomicFormula({self.symbol!r}, {self.param!r})"


class FoLOperator(Formula):
    def __init__(self, name: str):
        self.name = name
        super().__init__(self)

    def __repr__(self) -> str:
        return f"FoLOperator({self.name!r})"


class Quantifier(FoLOperator):
    def __init__(self, name: str, var: Variable, formula: Formula):
        super().__init__(name)
        self.var = var
        self.formula = formula

    def __repr__(self):
        return f"Quantifier({self.name!r} {self.var!r} {self.formula!r})"


class ForAll(Quantifier):
    def __init__(self, var: Variable, formula: Formula):
        super().__init__("ForAll", var, formula)

    def __repr__(self):
        return f"(ForAll {self.var!r} {self.formula!r})"


class Exists(Quantifier):
    def __init__(self, var: Variable, formula: Formula):
        super().__init__("Exists", var, formula)

    def __repr__(self):
        return f"(Exists {self.var!r} {self.formula!r})"


class BinaryLogicalConnector(FoLOperator):
    def __init__(self, name: str):
        super().__init__(name)

    def __repr__(self) -> str:
        return f"BinaryLogicalConnector({self.name!r})"


class And(BinaryLogicalConnector):
    def __init__(self, f1: Formula, f2: Formula):
        super().__init__("And")
        # FIXME
        self.formula1 = f1
        self.formula2 = f2

    def __repr__(self):
        return f"({self.formula1!r} And {self.formula2!r})"


class Or(BinaryLogicalConnector):
    def __init__(self, f1: Formula, f2: Formula):
        super().__init__("Or")
        self.formula1 = f1
        self.formula2 = f2

    def __repr__(self):
        return f"({self.formula1!r} Or {self.formula2!r})"


class Implies(BinaryLogicalConnector):
    def __init__(self, f1: Formula, f2: Formula):
        super().__init__("Implies")
        self.formula1 = f1
        self.formula2 = f2

    def __repr__(self):
        return f"({self.formula1!r} -> {self.formula2!r})"


class Equivalent(BinaryLogicalConnector):
    def __init__(self, f1: Formula, f2: Formula):
        super().__init__("Equivalent")
        self.formula1 = f1
        self.formula2 = f2

    def __repr__(self):
        return f"({self.formula1!r} <-> {self.formula2!r})"


class Not(BinaryLogicalConnector):
    def __init__(self, formula: Formula):
        super().__init__("Or")
        self.formula = formula

    def __repr__(self):
        return f"(Not {self.formula!r})"
