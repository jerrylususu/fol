from folObj import *
from typing import Iterable, Set
from copy import copy


def get_term_from_literal_position(literals: Iterable[Literal], pos: int) -> List[Term]:
    items = []
    for literal in literals:
        f: AtomicFormula = literal.formula
        if not isinstance(f, AtomicFormula):
            raise Exception("should be atomic formula")
        if len(f.param) <= pos:
            raise Exception("out of length")
        items.append(f.param[pos])

    return items


def all_same_type(items: List) -> bool:
    return all(type(x) == type(items[0]) for x in items)


def all_same_value(items: List) -> bool:
    return all(x == items[0] for x in items)


def tree_compare(*current: Union[Symbol, Term, AtomicFormula, Literal], ds: List[Set[Union[Variable, Term]]]):
    current = list(current)
    # print("debug", current)
    if not all_same_type(current):
        current_set = set(current)
        ds.append(current_set)
        return

    if isinstance(current[0], ConstantSymbol) or isinstance(current[0], Variable):
        current_set = set(current)
        if len(current_set) == 1:
            return
        else:
            ds.append(current_set)
            return

    elif (isinstance(current[0], Term) and isinstance(current[0].symbol, FunctionalSymbol)) or \
            (isinstance(current[0], AtomicFormula) and isinstance(current[0].symbol, PredicateSymbol)):
        len_list = [len(item.param) for item in current]
        if not all_same_type(len_list) or not all_same_value([item.symbol for item in current]):
            current_set = set(current)
            ds.append(current_set)
            return
        else:
            for idx in range(len(current[0].param)):
                terms: List[Term] = [item.param[idx] for item in current]
                tree_compare(*terms, ds=ds)
            return

    elif isinstance(current[0], Literal):
        formulas: List[Formula] = [item.formula for item in current]
        return tree_compare(*formulas, ds=ds)

    else:
        print(type(current[0]))
        raise Exception("should not happen")


def recursive_check_var_in_term(var: Variable, term: Term) -> bool:
    if isinstance(term, ConstantSymbol):
        return False
    if isinstance(term, Variable):
        return term == var
    if isinstance(term, Term) and isinstance(term.symbol, FunctionalSymbol):
        results = [recursive_check_var_in_term(var, p) for p in term.param]
        return any(results)


def generate_possible_pairs(ds: List[Set[Union[Variable, Term]]]) -> List[List[Tuple[Variable, Term]]]:
    all_pairs: List[List[Tuple[Variable, Term]]] = []
    for one_set in ds:
        pairs: List[Tuple[Variable, Term]] = []
        vars: List[Variable] = []
        terms: List[Term] = []
        for item in one_set:
            if isinstance(item, Variable):
                vars.append(item)

            terms.append(item)
        for var in vars:
            for term in terms:
                if var == term:
                    continue
                if (term, var) in pairs:
                    continue
                if term.param is not None and len(term.param) != 0:
                    if recursive_check_var_in_term(var, term):
                        continue
                pairs.append((var, term))

        all_pairs.append(pairs)

    return all_pairs


def apply_substitution(current: Union[Symbol, Term, AtomicFormula, Literal], substitutions: List[Substitution]):
    if isinstance(current, Literal):
        apply_substitution(current.formula, substitutions=substitutions)
        return current

    if (isinstance(current, Term) or isinstance(current, AtomicFormula)) and (
            isinstance(current.symbol, FunctionalSymbol) or isinstance(current.symbol, PredicateSymbol)):
        current.recursive_apply(apply_substitution, substitutions=substitutions)
        return current

    if isinstance(current, Variable):
        modified = current
        for substitution in substitutions:
            if current == substitution.var:
                modified = substitution.term

        return modified
    else:
        return current


def get_copy_of_list(items) -> List:
    return [copy(item) for item in items]


# https://stackoverflow.com/questions/952914/how-to-make-a-flat-list-out-of-list-of-lists
def flatten(t) -> List:
    return [item for sublist in t for item in sublist]


def find_mgu(*literals: Literal, substitutions: List[Substitution]) -> Tuple[bool, List[Substitution]]:
    ds = []
    tree_compare(*literals, ds=ds)
    if len(ds) == 0:
        return True, substitutions
    all_pairs = generate_possible_pairs(ds)
    if all_pairs is None or len(all_pairs) == 0:
        return False, []
    all_pairs_flatten = flatten(all_pairs)
    for (var, term) in all_pairs_flatten:
        sub = Substitution(var, term)
        mod_subs = substitutions.copy()
        mod_subs.append(sub)
        mod_literals = []
        for literal in literals:
            mod_literal = copy(literal)
            apply_substitution(mod_literal, mod_subs)
            mod_literals.append(mod_literal)

        return find_mgu(*mod_literals, substitutions=mod_subs)

    return False, []


def flatten_literal_tree(current: Union[Symbol, Term, AtomicFormula, Literal], items: List[str]):
    if isinstance(current, ConstantSymbol):
        items.append(current.__repr__())
    elif isinstance(current, Variable):
        items.append(current.__repr__())
    elif isinstance(current, Term):
        if isinstance(current.symbol, FunctionalSymbol):
            functional_symbol: FunctionalSymbol = current.symbol
            items.append(functional_symbol.__repr__())
            for p in current.param:
                flatten_literal_tree(p, items=items)
        else:
            raise Exception("should not happen")
    elif isinstance(current, AtomicFormula):
        predicate_symbol: PredicateSymbol = current.symbol
        items.append(predicate_symbol.__repr__())
        for p in current.param:
            flatten_literal_tree(p, items=items)
    elif isinstance(current, Literal):
        flatten_literal_tree(current.formula, items=items)


def find_mgu_wrapper(literal1: Literal, literal2: Literal) -> Tuple[bool, List[Substitution]]:
    ds = []
    tree_compare(literal1, literal2, ds=ds)
    subs = []
    return find_mgu(literal1, literal2, substitutions=subs)


# ds: disagreement set
# def compare_literal_generate_ds(literals: Iterable[Literal], ds: Set[Set[Term]]):
#     current_set: Set[Term] = set()
#     for literal in literals:


# apply substitution


if __name__ == "__main__":

    # ---- INPUT AREA BEGIN -----

    x = Variable("x")
    y = Variable("y")
    z = Variable("z")
    f = FunctionalSymbol("f", 2)
    g = FunctionalSymbol("g", 1)
    h = FunctionalSymbol("h", 1)
    P = PredicateSymbol("P", 2)

    a = ConstantSymbol("a")
    b = ConstantSymbol("b")

    # 2.1
    formula1 = P(a, x)
    formula2 = P(y, y)

    # 2.2
    # formula1 = P(g(x), z)
    # formula2 = P(g(y), g(z))

    # 2.3
    # formula1 = P(g(x), y)
    # formula2 = P(y, h(x))

    # formula1 = P(x,g(y))
    # formula2 = P(y,g(x))

    # formula1 = P(y, f(x,y))
    # formula2 = P(g(z), f(a,z))

    # 2.4
    # formula1 = P(x, g(x))
    # formula2 = P(g(y), y)

    # 2.5
    # formula1 = P(x, g(y))
    # formula2 = P(g(y), x)

    # 2.6
    # formula1 = P(y, f(x, y))
    # formula2 = P(b, f(a, y))

    # Worksheet2, Q2.7
    # formula1 = P(y, f(x,y))
    # formula2 = P(b, f(a,y))

    #
    # formula1 = P(g(x), z)
    # formula2 = P(g(f(y,f(y,z))), g(z))
    # formula3 = P(g(f(x,f(x,x))), g(x))

    # formula1 = P(y, f(x,y))
    # formula2 = P(g(z), f(a,z))

    # ---- INPUT AREA END -----


    literal1 = Literal(formula1)
    literal2 = Literal(formula2)
    # literal3 = Literal(formula3)

    print("input literal 1:", literal1)
    print("input literal 2:", literal2)

    # literals = set()
    # literals.add(literal1)
    # literals.add(literal2)

    # print(get_term_from_literal_position(literals, 0))

    ds = []
    tree_compare(literal1, literal2, ds=ds)
    # print(ds)

    all_pairs = generate_possible_pairs(ds)
    # print(all_pairs)

    subs = []
    found, found_subs = find_mgu(literal1, literal2, substitutions=subs)
    print("find MGU:", found, found_subs)
    if found:
        print("after substitution")
        apply_substitution(literal1, found_subs)
        apply_substitution(literal2, found_subs)
        print(literal1)
        print(literal2)
