from folObj import *


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
        elif isinstance(f.formula, Not):
            # remove double not
            return f.formula.formula

    if isinstance(f, FoLOperator):
        f.recursive_apply(push)
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
            return deduplicate(f.formula1)
        else:
            f.recursive_apply(deduplicate)
            return f

    if isinstance(f, FoLOperator):
        f.recursive_apply(deduplicate)
        return f


def to_CNF(f: Formula) -> Formula:
    return deduplicate(distribute(push(eliminate(f))))


if __name__ == "__main__":
    x = Variable("x")
    A = PredicateSymbol("A", 0)
    B = PredicateSymbol("B", 0)
    C = PredicateSymbol("C", 0)
    D = PredicateSymbol("D", 0)

    formula = And(Implies(A(), B()), Implies(A(), B()))
    print(formula)

    print(eliminate(formula))
    print(push(eliminate(formula)))
    print(distribute(push(eliminate(formula))))
    print(deduplicate(distribute(push(eliminate(formula)))))

    print("--------------")

    x = Variable("x")
    y = Variable("y")
    z = Variable("z")
    Child = PredicateSymbol("Child", 2)
    Descendant = PredicateSymbol("Descendant", 2)
    formula = ForAll(x, ForAll(y,
                               Implies(Or(Child(x, y), Exists(z, And(Child(x, z), Descendant(z, y)))),
                                       Descendant(x, y))))
    print(formula)
    print(eliminate(formula))
    print(push(eliminate(formula)))
    print(distribute(push(eliminate(formula))))
    print(deduplicate(distribute(push(eliminate(formula)))))

    # for i in range(5):
    #     formula = to_CNF(formula)
    #     print(formula)
