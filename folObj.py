from __future__ import annotations
from typing import List, Union, Tuple, Set


class Term(object):
    def __init__(self, symbol: Union[ConstantSymbol, FunctionalSymbol, Variable], param: List[Term] = None,
                 init_with_none_list: bool = False):

        if (isinstance(symbol, ConstantSymbol) or isinstance(symbol, Variable)) and param is not None:
            raise Exception("constant symbol or variable should not have param")

        if isinstance(symbol, FunctionalSymbol) and (param is None or len(param) != symbol.ar) and not init_with_none_list:
            raise Exception("functional symbol with incorrect number of param")

        self.symbol = symbol
        self.param = param

    def __repr__(self):
        return f"T({self.symbol!r}, {self.param!r})"

    def __eq__(self, other):
        return isinstance(other, Term) and self.symbol == other.symbol and self.param == other.param

    def __hash__(self):
        # pretty hacky here...
        return hash(self.__repr__())

    def recursive_apply(self, func, **kwargs):
        if self.param is None:
            return
        for idx in range(len(self.param)):
            self.param[idx] = func(self.param[idx], **kwargs)


class Symbol(object):
    def __init__(self, name: str, ar: int):
        self.name = name
        self.ar = ar

    def __repr__(self):
        return f"S({self.name!r}, {self.ar!r})"

    def __hash__(self):
        return hash(self.__repr__())

    def __eq__(self, other):
        return isinstance(other, Symbol) and self.name == other.name and self.ar == other.ar


class ConstantSymbol(Symbol, Term):
    def __init__(self, name: str):
        Symbol.__init__(self, name, 0)
        Term.__init__(self, self)

    def __repr__(self) -> str:
        return f"CS({self.name!r})"


class FunctionalSymbol(Symbol, Term):
    def __init__(self, name: str, ar: int):
        Symbol.__init__(self, name, ar)
        Term.__init__(self, self, None, init_with_none_list=True)

    def __repr__(self) -> str:
        return f"FS({self.name!r}, {self.ar!r})"

    def __call__(self, *param: Term) -> Term:
        return Term(self, list(param))

class PredicateSymbol(Symbol):
    def __init__(self, name: str, ar: int):
        super().__init__(name, ar)

    def __repr__(self) -> str:
        return f"PS({self.name!r}, {self.ar!r})"

    def __call__(self, *param: Term) -> AtomicFormula:
        return AtomicFormula(self, list(param))


class Variable(Symbol, Term):
    def __init__(self, name: str):
        Symbol.__init__(self, name, 0)
        Term.__init__(self, self)

    def __repr__(self):
        return f"Var({self.name!r})"

    def __eq__(self, other):
        if not isinstance(other, Variable):
            return False
        return self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)


class Formula(object):
    def __init__(self, content: Union[AtomicFormula, FoLOperator]):
        if not (isinstance(content, AtomicFormula) or isinstance(content, FoLOperator)):
            raise Exception("formula init error", type(content))

        self.content = content

    def __repr__(self):
        return f"F({self.content!r})"


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
        return f"AF({self.symbol!r}, {self.param!r})"

    def __eq__(self, other: AtomicFormula):
        if not isinstance(other, AtomicFormula):
            return False
        return self.symbol == other.symbol and self.param == other.param

    def __hash__(self):
        return hash(self.__repr__())

    def recursive_apply(self, func, **kwargs):
        if self.param is None:
            return
        for idx in range(len(self.param)):
            self.param[idx] = func(self.param[idx], **kwargs)

class FoLOperator(Formula):
    def __init__(self, name: str):
        self.name = name
        super().__init__(self)

    def __repr__(self) -> str:
        return f"FoLOperator({self.name!r})"

    def recursive_apply(self, function, **kwargs):
        raise Exception("no apply on base")


class Quantifier(FoLOperator):
    def __init__(self, name: str, var: Variable, formula: Formula):
        super().__init__(name)
        if not isinstance(var, Variable):
            raise ValueError("not a variable")
        self.var = var
        self.formula = formula

    def __repr__(self):
        return f"Quantifier({self.name!r} {self.var!r} {self.formula!r})"

    def recursive_apply(self, function, **kwargs):
        self.formula = function(self.formula, **kwargs)


class ForAll(Quantifier):
    def __init__(self, var: Variable, formula: Formula):
        super().__init__("ForAll", var, formula)

    def __repr__(self):
        return f"(∀ {self.var!r} {self.formula!r})"


class Exists(Quantifier):
    def __init__(self, var: Variable, formula: Formula):
        super().__init__("Exists", var, formula)

    def __repr__(self):
        return f"(∃ {self.var!r} {self.formula!r})"


class BinaryLogicalConnector(FoLOperator):
    def __init__(self, name: str, f1: Formula, f2: Formula):
        super().__init__(name)
        self.formula1 = f1
        self.formula2 = f2

    def __repr__(self) -> str:
        return f"BinaryLogicalConnector({self.name!r})"

    def recursive_apply(self, function, **kwargs):
        self.formula1 = function(self.formula1, **kwargs)
        self.formula2 = function(self.formula2, **kwargs)

    def __eq__(self, other: BinaryLogicalConnector):
        return isinstance(other, BinaryLogicalConnector) and self.name == other.name and self.formula1 == other.formula1 and self.formula2 == other.formula2


class And(BinaryLogicalConnector):
    def __init__(self, f1: Formula, f2: Formula):
        super().__init__("And", f1, f2)

    def __repr__(self):
        return f"({self.formula1!r} ∧ {self.formula2!r})"


class Or(BinaryLogicalConnector):
    def __init__(self, f1: Formula, f2: Formula):
        super().__init__("Or", f1, f2)

    def __repr__(self):
        return f"({self.formula1!r} ∨ {self.formula2!r})"


class Implies(BinaryLogicalConnector):
    def __init__(self, f1: Formula, f2: Formula):
        super().__init__("Implies", f1, f2)

    def __repr__(self):
        return f"({self.formula1!r} → {self.formula2!r})"


class Equivalent(BinaryLogicalConnector):
    def __init__(self, f1: Formula, f2: Formula):
        super().__init__("Equivalent", f1, f2)

    def __repr__(self):
        return f"({self.formula1!r} ↔ {self.formula2!r})"


class Not(FoLOperator):
    def __init__(self, formula: Formula):
        super().__init__("Not")
        self.formula = formula

    def __repr__(self):
        return f"¬({self.formula!r})"

    def recursive_apply(self, function, **kwargs):
        self.formula = function(self.formula, **kwargs)

    def __eq__(self, other):
        if not isinstance(other, Not):
            return False
        return self.formula == other.formula


class Literal(object):
    def __init__(self, formula: Union[AtomicFormula, Not]):
        self.formula: AtomicFormula = formula
        self.negative: bool = False
        if not (isinstance(formula, AtomicFormula) or isinstance(formula, Not)):
            raise Exception("incorrect literal initialization: class incompatible")
        if isinstance(formula, Not) and not isinstance(formula.formula, AtomicFormula):
            raise Exception("incorrect literal initialization: not negation of atomic formula")
        if isinstance(formula, Not):
            self.formula: AtomicFormula = formula.formula
            self.negative = True

    def __repr__(self):
        return f"{'¬' if self.negative else ''}L({self.formula!r})"

    def __hash__(self):
        return hash(self.__repr__())

    def __eq__(self, other):
        return isinstance(other, Literal) and self.negative == other.negative and self.formula == other.formula


class Substitution(object):
    def __init__(self, var: Variable, term: Term):

        if not isinstance(var, Variable) or not isinstance(term, Term):
            raise Exception("substitution error")

        self.var = var
        self.term = term

    def __repr__(self):
        return f"ST[{self.var!r}/{self.term!r}]"


class MultiLogicalConnector(FoLOperator):
    def __init__(self, name: str, formulas: Set[Formula]):
        super(MultiLogicalConnector, self).__init__(name)
        self.formulas = formulas

    def __repr__(self) -> str:
        return f"MultiLogicalConnector({self.name!r})"

    def recursive_apply(self, function, **kwargs):
        raise Exception("not implemented")


class MultiAnd(MultiLogicalConnector):
    def __init__(self, formulas: Set[Formula]):
        super(MultiAnd, self).__init__("MultiAnd", formulas)

    def __repr__(self) -> str:
        return f"MultiAnd({self.formulas!r})"

    def __hash__(self):
        return hash(self.__repr__())

    def __eq__(self, other):
        return isinstance(other, MultiAnd) and self.formulas == other.formulas


class MultiOr(MultiLogicalConnector):
    def __init__(self, formulas: Set[Formula]):
        super(MultiOr, self).__init__("MultiOr", formulas)

    def __repr__(self) -> str:
        return f"MultiOr({self.formulas!r})"

    def __hash__(self):
        return hash(self.__repr__())

    def __eq__(self, other):
        return isinstance(other, MultiOr) and self.formulas == other.formulas

