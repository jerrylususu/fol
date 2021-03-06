# Q for quantifier

from folObj import *
from typing import Set, Dict
from multi import remove_duplicate_multiarg, expand_multi

def eliminate(f: Formula) -> Formula:
    if isinstance(f, AtomicFormula):
        return f

    if isinstance(f, Implies):
        return eliminate(Or(Not(f.formula1), f.formula2))
    elif isinstance(f, Equivalent):
        return eliminate(And(Implies(f.formula1, f.formula2), Implies(f.formula2, f.formula1)))

    if isinstance(f, FoLOperator):
        f.recursive_apply(eliminate)
        return f


def push(f: Formula) -> Formula:
    if isinstance(f, AtomicFormula):
        return f

    if isinstance(f, Not):
        if isinstance(f.formula, And):
            return push(Or(Not(f.formula.formula1), Not(f.formula.formula2)))
        elif isinstance(f.formula, Or):
            return push(And(Not(f.formula.formula1), Not(f.formula.formula2)))
        elif isinstance(f.formula, Quantifier):
            quantifier: Quantifier = f.formula
            if isinstance(quantifier, ForAll):
                return push(Exists(quantifier.var, Not(quantifier.formula)))
            elif isinstance(quantifier, Exists):
                return push(ForAll(quantifier.var, Not(quantifier.formula)))
        elif isinstance(f.formula, Not):
            # remove double not
            return f.formula.formula

    if isinstance(f, FoLOperator):
        f.recursive_apply(push)
        return f


class VarStorage(object):
    def __init__(self):
        self.vars: Set[Variable] = set()
        self.rename_counter = 1

    def check_and_replace(self, var: Variable) -> Tuple[bool, Variable]:
        if var not in self.vars:
            self.vars.add(var)
            # false: no need to be replaced later
            return False, var
        else:
            new_var = Variable(f"$r{self.rename_counter}")
            self.rename_counter += 1
            self.vars.add(new_var)
            # true: need to be replaced in downstream
            return True, new_var

    def generate_new_var(self) -> Variable:
        new_var = Variable(f"$r{self.rename_counter}")
        self.rename_counter += 1
        return new_var


# vs: check if variable needs to be changed
# remap: map of variables that need to be renamed / replaced
# path: the path of quantifiers from root to current formula
def standardize(f: Formula, vs: VarStorage, remap: Dict[Variable, Variable], path: List[Variable]) -> Formula:
    if isinstance(f, AtomicFormula):
        for idx, p in enumerate(f.param):
            if isinstance(p, Variable):
                if p in path and p in remap:
                    f.param[idx] = remap[p]
                elif p not in path:
                    # out of scope variable
                    if p not in remap:
                        remap[p] = vs.generate_new_var()
                    f.param[idx] = remap[p]
        return f

    if isinstance(f, Quantifier):
        if isinstance(f, Exists):
            mod_remap = remap.copy()
            mod_path = path.copy()
            mod_path.append(f.var)
            need_replace, new_var = vs.check_and_replace(f.var)
            if new_var:
                mod_remap[f.var] = new_var
            return Exists(new_var, standardize(f.formula, vs=vs, remap=mod_remap, path=mod_path))
        elif isinstance(f, ForAll):
            mod_remap = remap.copy()
            mod_path = path.copy()
            mod_path.append(f.var)
            need_replace, new_var = vs.check_and_replace(f.var)
            if new_var:
                mod_remap[f.var] = new_var
            return ForAll(new_var, standardize(f.formula, vs=vs, remap=mod_remap, path=mod_path))

    if isinstance(f, FoLOperator):
        f.recursive_apply(standardize, vs=vs, remap=remap, path=path)
        return f


class FuncStorage(object):
    def __init__(self):
        self.var_func_dict: Dict[Variable, Union[FunctionalSymbol, ConstantSymbol]] = dict()
        self.function_count = 1
        self.constant_count = 1

    def get_path_function(self, var: Variable, forall_path: List[Variable]) -> Union[FunctionalSymbol, ConstantSymbol]:
        path_str = ",".join([var.name for var in forall_path])

        if path_str == "":
            new_var = ConstantSymbol(f"$c{self.constant_count}")
            self.constant_count += 1

        else:
            new_var = FunctionalSymbol(f"$pf{self.function_count}", len(forall_path))
            self.function_count += 1

        self.var_func_dict[var] = new_var

        return self.var_func_dict[var]


# eliminate existential quantifier
def existential(f: Formula, fs: FuncStorage, remap: Dict[Variable, Union[FunctionalSymbol, ConstantSymbol]],
                forall_path: List[Variable]) -> Formula:
    if isinstance(f, AtomicFormula):
        for idx, p in enumerate(f.param):
            if isinstance(p, Variable) and p in remap:
                func_or_const = remap[p]
                if isinstance(func_or_const, FunctionalSymbol):
                    f.param[idx] = Term(func_or_const, forall_path)
                elif isinstance(func_or_const, ConstantSymbol):
                    f.param[idx] = func_or_const
        return f

    if isinstance(f, Quantifier):

        if isinstance(f, ForAll):
            mod_forall_path = forall_path.copy()
            mod_forall_path.append(f.var)
            return ForAll(f.var, existential(f.formula, fs=fs, remap=remap, forall_path=mod_forall_path))
        elif isinstance(f, Exists):
            mod_remap = remap.copy()
            new_func = fs.get_path_function(f.var, forall_path)
            mod_remap[f.var] = new_func
            return existential(f.formula, fs=fs, remap=mod_remap, forall_path=forall_path)

    if isinstance(f, FoLOperator):
        f.recursive_apply(existential, fs=fs, remap=remap, forall_path=forall_path)
        return f


# move quantifier forward
def universal(f: Formula) -> Formula:
    if isinstance(f, AtomicFormula):
        return f

    if isinstance(f, BinaryLogicalConnector):
        if isinstance(f, And) or isinstance(f, Or):
            connector = type(f)
            f.recursive_apply(universal)

            if not (isinstance(f.formula1, Quantifier) and isinstance(f.formula2, Quantifier)):
                return f

            var1, f1 = None, None
            var2, f2 = None, None
            if isinstance(f.formula1, Quantifier):
                var1, f1 = f.formula1.var, f.formula1.formula
            if isinstance(f.formula2, Quantifier):
                var2, f2 = f.formula2.var, f.formula2.formula

            processed_f = connector(f1, f2)
            if var1 is not None and var2 is None:
                return ForAll(var1, processed_f)
            elif var1 is None and var2 is not None:
                return ForAll(var2, processed_f)
            else:
                return ForAll(var1, ForAll(var2, processed_f))

        else:
            raise Exception("should not have other binary logical connector at this stage")

    if isinstance(f, FoLOperator):
        f.recursive_apply(universal)
        return f


def distribute(f: Formula) -> Formula:
    if isinstance(f, AtomicFormula):
        return f

    if isinstance(f, Or):
        if isinstance(f.formula1, And) and not isinstance(f.formula2, And):
            andf = f.formula1
            af = f.formula2
            return distribute(And(Or(andf.formula1, af), Or(andf.formula2, af)))
        elif not isinstance(f.formula1, And) and isinstance(f.formula2, And):
            andf = f.formula2
            af = f.formula1
            return distribute(And(Or(andf.formula1, af), Or(andf.formula2, af)))

    if isinstance(f, FoLOperator):
        f.recursive_apply(distribute)
        return f


def deduplicate(f: Formula) -> Formula:
    if isinstance(f, AtomicFormula):
        return f

    if isinstance(f, And):
        if f.formula1 == f.formula2:
            return deduplicate(f.formula1)
        else:
            f.recursive_apply(deduplicate)
            return f

    elif isinstance(f, Or):
        if f.formula1 == f.formula2:
            # print(type(f), type(f.formula1), type(f.formula2))
            # print(f)
            return deduplicate(f.formula1)
        else:
            f.recursive_apply(deduplicate)
            return f

    if isinstance(f, FoLOperator):
        f.recursive_apply(deduplicate)
        return f


def strip(f: Formula) -> Formula:
    if isinstance(f, AtomicFormula):
        return f

    if isinstance(f, Quantifier):
        if isinstance(f, ForAll):
            return strip(f.formula)
        else:
            raise Exception("should not have other quantifier at this stage")

    if isinstance(f, FoLOperator):
        f.recursive_apply(deduplicate)
        return f


def split_to_literal(f: Formula, literals: List[Set[Literal]]):
    if isinstance(f, Not) or isinstance(f, AtomicFormula):
        if len(literals) == 0:
            literals.append(set())
        literals[0].add(Literal(f))

    elif isinstance(f, And):
        # should only happen at first layer
        list1, list2 = [set()], [set()]
        split_to_literal(f.formula1, list1)
        split_to_literal(f.formula2, list2)
        literals.extend(list1)
        literals.extend(list2)
        # nasty hack to remove empty sets
        delete_idxs = []
        for idx, literal_set in enumerate(literals):
            if len(literal_set) == 0:
                delete_idxs.append(idx)
        for idx in delete_idxs[::-1]:
            del literals[idx]

    elif isinstance(f, FoLOperator):
        f.recursive_apply(split_to_literal, literals=literals)


def to_CNF_Q(f: Formula) -> Formula:
    f = eliminate(f)
    f = push(f)

    vs = VarStorage()
    remap = dict()
    path = []

    f = standardize(f, vs=vs, remap=remap, path=path)

    fs = FuncStorage()
    remap2 = dict()
    forall_path = []

    f = existential(f, fs=fs, remap=remap2, forall_path=forall_path)
    f = universal(f)
    f = distribute(f)
    f = expand_multi(remove_duplicate_multiarg(f))
    f = deduplicate(f)
    f = strip(f)
    return f


if __name__ == "__main__":
    # ---- INPUT AREA BEGIN -----

    # x = Variable("x")
    # A = PredicateSymbol("A", 1)
    # B = PredicateSymbol("B", 1)
    #
    # formula = Not(Implies(ForAll(x, A(x)), Exists(x, B(x))))

    # Worksheet2, Q1.1
    # v0 = Variable("v0")
    # v1 = Variable("v1")
    # v2 = Variable("v2")
    # P = PredicateSymbol("P", 3)
    # Q = PredicateSymbol("Q", 3)

    # formula = Implies(ForAll(v0, Exists(v1, ForAll(v2, P(v0, v1, v2)))), ForAll(v1, Exists(v2, Q(v1, v2, v0))))

    # x = Variable("x")
    # P = PredicateSymbol("P", 1)
    #
    # formula = Not(Implies(ForAll(x, P(x)), Not(Exists(x, Not(P(x))))))
    # formula = Not(Or(ForAll(x, P(x)), ForAll(x, Not(P(x)))))

    # # Worksheet1, Q8
    x = Variable("x")
    y = Variable("y")
    P = PredicateSymbol("P", 2)
    Q = PredicateSymbol("Q", 2)
    R = PredicateSymbol("R", 2)

    formula = And(P(x,y), And(Q(x,y), P(x,y)))
    # formula = Not(ForAll(x, Exists(y, Implies(And(P(x,y), Q(x,y)), R(x,y)))))

    # Worksheet2, Q5
    # x = Variable("x")
    # y = Variable("y")
    # z = Variable("z")
    # Peter = ConstantSymbol("Peter")
    # Anna = ConstantSymbol("Anna")
    # Hans = ConstantSymbol("Hans")
    # Child = PredicateSymbol("Child", 2)
    # Descendant = PredicateSymbol("Descendant", 2)
    #
    # formula = ForAll(x, ForAll(y, Implies(Or(Child(x,y), Exists(z, And(Child(x,z), Descendant(z,y)))),  Descendant(x,y))))

    # worksheet1, 5.6
    # known bug, won't work
    # x = Variable("x")
    # y = Variable("y")
    # D = PredicateSymbol("D", 1)
    # query = Exists(x, Implies(D(x), ForAll(y, D(y))))
    # formula = Not(query)

    # worksheet 2, q4
    # B = PredicateSymbol("Barber", 1)
    # S = PredicateSymbol("Shave", 2)
    # x = Variable("x")
    # y = Variable("y")
    #
    # f1 = ForAll(x, ForAll(y, Implies(And(B(x), Not(S(y, y))), S(x, y))))
    # f2 = Not(Exists(x, Exists(y, Or(B(x), Or(S(x, y), S(y, y))))))
    # query = Not(Exists(x, B(x)))
    #
    # # f = ForAll(x, ForAll(x, B(x)))
    # formula = f1

    # ---- INPUT AREA END -----

    # P = PredicateSymbol("P",1)
    # Q = PredicateSymbol("Q",1)
    # R = PredicateSymbol("R",1)
    # x = Variable("x")
    # f8 = ForAll(x, And(Or(P(x), P(x)), And(P(x), P(x))))
    # formula = f8

    print("Input", formula)

    # print("Output", to_CNF_Q(formula))

    f = formula
    f = eliminate(f)
    print(f)
    f = push(f)
    print(f)


    vs = VarStorage()
    remap = dict()
    path = []

    f = standardize(f, vs=vs, remap=remap, path=path)
    print(f)


    fs = FuncStorage()
    remap2 = dict()
    forall_path = []

    f = existential(f, fs=fs, remap=remap2, forall_path=forall_path)
    print(f)

    f = universal(f)
    print(f)

    f = distribute(f)
    print(f)

    f = remove_duplicate_multiarg(f)
    print(f)

    f = expand_multi(f)
    print(f)

    f = deduplicate(f)
    print("Output", f)

    li = []
    split_to_literal(f, li)
    print("Literals", li)
