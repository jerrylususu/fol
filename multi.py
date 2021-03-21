from folObj import *
from typing import Set, Optional


def expand_multi(f: Formula) -> Formula:
    if isinstance(f, MultiAnd) or isinstance(f, MultiOr):

        if len(f.formulas) == 0:
            raise Exception("empty multi logical connector")
        elif len(f.formulas) == 1:
            # return the only element
            return list(f.formulas)[0]

        # final type after expansion
        final_type: Optional[BinaryLogicalConnector] = None
        if isinstance(f, MultiAnd):
            final_type = And
        elif isinstance(f, MultiOr):
            final_type = Or

        # not order preserving
        formula_list: List[Formula] = list(f.formulas)

        base_formula: BinaryLogicalConnector = final_type(formula_list[0], formula_list[1])
        for idx in range(2, len(formula_list)):
            base_formula = final_type(formula_list[idx], base_formula)

        return base_formula
    elif isinstance(f, Exists) or isinstance(f, ForAll):
        return type(f)(f.var, expand_multi(f.formula))
    else:
        return f
        # raise Exception("not multi logical connector")


# f: current formula
# last: last formula in the chain
# formula_set:
def remove_duplicate_multiarg(f: Formula) -> Formula:
    if isinstance(f, AtomicFormula):
        return f

    # first do propagate
    if isinstance(f, And) or isinstance(f, Or):
        if isinstance(f.formula1, AtomicFormula) and isinstance(f.formula2, AtomicFormula):
            sub_set: Set[Formula] = set()
            sub_set.add(f.formula1)
            sub_set.add(f.formula2)
            if isinstance(f, And):
                return MultiAnd(sub_set)
            elif isinstance(f, Or):
                return MultiOr(sub_set)
        else:
            res1 = remove_duplicate_multiarg(f.formula1)
            res2 = remove_duplicate_multiarg(f.formula2)

            print("debug", f)
            print("h1", res1)
            print("h2", res2)

            # 1 check if duplicate
            if res1 == res2:
                return res1
            if isinstance(res1, MultiLogicalConnector) and isinstance(res2, MultiLogicalConnector):
                if res1.formulas == res2.formulas:
                    return res1

            # 2 check with the upper level operator
            if isinstance(f, And):
                new_set = set()
                if isinstance(res1, MultiAnd) and isinstance(res2, MultiAnd):
                    new_set = set(res1.formulas).union(res2.formulas)
                    return MultiAnd(new_set)
                if isinstance(res1, AtomicFormula) and isinstance(res2, MultiAnd):
                    new_set = set(res2.formulas)
                    new_set.add(res1)
                    return MultiAnd(new_set)
                if isinstance(res1, MultiAnd) and isinstance(res2, AtomicFormula):
                    new_set = set(res1.formulas)
                    new_set.add(res2)
                    return MultiAnd(new_set)
                if isinstance(res1, AtomicFormula) and isinstance(res2, AtomicFormula):
                    new_set.add(res1)
                    new_set.add(res2)
                    return MultiAnd(new_set)


            elif isinstance(f, Or):
                new_set = set()
                if isinstance(res1, MultiOr) and isinstance(res2, MultiOr):
                    new_set = set(res1.formulas).union(res2.formulas)
                    return MultiOr(new_set)
                if isinstance(res1, AtomicFormula) and isinstance(res2, MultiOr):
                    new_set = set(res2.formulas)
                    new_set.add(res1)
                    return MultiOr(new_set)
                if isinstance(res1, MultiOr) and isinstance(res2, AtomicFormula):
                    new_set = set(res1.formulas)
                    new_set.add(res2)
                    return MultiOr(new_set)
                if isinstance(res1, AtomicFormula) and isinstance(res2, AtomicFormula):
                    return MultiOr(new_set)

            # 3 process the rest
            base_type = type(f)
            return base_type(expand_multi(res1), expand_multi(res2))

    if isinstance(f, Quantifier):
        if isinstance(f, ForAll) or isinstance(f, Exists):
            return type(f)(f.var, remove_duplicate_multiarg(f.formula))
    if isinstance(f, Not):
        return Not(remove_duplicate_multiarg(f.formula))

    if isinstance(f, FoLOperator):
        raise Exception("should not be here")
        # f.recursive_apply(remove_duplicate)




if __name__ == '__main__':
    P = PredicateSymbol("P",1)
    Q = PredicateSymbol("Q",1)
    R = PredicateSymbol("R",1)
    x = Variable("x")

    # f = MultiAnd({P(x), Q(x), P(x), R(x)})
    # print(f)
    # f2 = expand_multi(f)
    # print(f2)

    f3 = And(P(x), And(Q(x), P(x)))
    f4 = And(And(P(x), Q(x)), And(And(P(x), And(Q(x), P(x))), P(x)))
    f5 = Or(And(P(x), Q(x)), And(P(x), Q(x)))
    f6 = And(f5, f5)

    f7 = Or(P(x), Or(P(x), Q(x)))
    f8 = And(Or(P(x), P(x)), And(P(x), P(x)))

    f9 = And(And(P(x), And(Q(x), R(x))), And(Q(x), P(x)))
    formula = f9
    print(formula)
    print(expand_multi(remove_duplicate_multiarg(formula)))
