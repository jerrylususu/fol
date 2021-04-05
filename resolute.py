from folObj import *
from mgu import *
from normQ import *
from typing import FrozenSet
from copy import deepcopy
import itertools


class ClauseStorage(object):
    def __init__(self):
        self.clause_set: Set[FrozenSet[Literal]] = set()

        # clause_id -> clause
        self.map: Dict[int, FrozenSet[Literal]] = {}

        # (clause_id1, clause_id2)
        self.todo: Set[Tuple[int, int]] = set()
        self.impossible: Set[Tuple[int, int]] = set()

        # (clause_id1, clause_id2) -> clause_id3
        self.done: Dict[Tuple[int, int], int] = dict()
        # clause_id3 -> (clause_id1, clause_id2)
        self.source: Dict[int, Tuple[int, int, List[Substitution]]] = dict()

        self.counter = 1

    def __getitem__(self, item: int):
        return self.map[item]

    # def __setitem__(self, key, value):
    #     self.map[key] = value

    def put_clause(self, clause: Set[Literal]) -> Union[None, int]:
        # don't add duplicate
        if frozenset(clause) in self.clause_set:
            return None

        self.clause_set.add(frozenset(clause))
        self.map[self.counter] = frozenset(clause)
        self.counter += 1
        for idx in range(1, self.counter):
            self.todo.add((self.counter - 1, idx))

        return self.counter - 1

    def put_clauses(self, clauses: Iterable[Set[Literal]]):
        for c in clauses:
            self.put_clause(c)

    def note_impossible(self, combination: Tuple[int, int]):
        if combination not in self.todo:
            raise Exception("combination not in todo")
        self.todo.remove(combination)
        self.impossible.add(combination)

    def note_done(self, combination: Tuple[int, int], new_clause_id: int, substitution: List[Substitution]):
        if combination not in self.todo:
            raise Exception("combination not in todo")
        self.todo.remove(combination)
        self.done[combination] = new_clause_id
        self.source[new_clause_id] = (combination[0], combination[1], substitution)

    def get_combination_length_sum(self, combination: Tuple[int, int]) -> int:
        return sum([len(self.map[i]) for i in combination])

    def get_next_combination(self) -> Tuple[int, int]:
        combination_and_length_sum: List[Tuple[int, Tuple[int, int]]] = [(self.get_combination_length_sum(comb), comb)
                                                                         for comb in self.todo]
        combination_and_length_sum.sort(key=lambda x: x[0])
        if len(combination_and_length_sum) == 0:
            raise Exception("empty combination list, can not proceed")
        return combination_and_length_sum[0][1]

    def get_reverse_chain(self, clause_id: int, record_list: List[Tuple[int, int, int, List[Substitution]]]):
        if clause_id not in self.source:
            return

        source1, source2, subs = self.source[clause_id]
        if (source1, source2, clause_id, subs) not in record_list:
            record_list.insert(0, (source1, source2, clause_id, subs))
        self.get_reverse_chain(source1, record_list=record_list)
        self.get_reverse_chain(source2, record_list=record_list)

    def pretty_print_reverse_chain(self, record_list: List[Tuple[int, int, int, List[Substitution]]]):
        for s1, s2, res, subs in record_list:
            print(s1, set(self.map[s1]))
            print(s2, set(self.map[s2]))
            print("θ", subs)
            print("->", res, set(self.map[res]))
            print("-----------")


def do_resolution(cs: ClauseStorage) -> bool:
    got_empty_clause = False
    while len(cs.todo) != 0:
        combination = cs.get_next_combination()
        clause1, clause2 = cs[combination[0]], cs[combination[1]]
        # otherwise at some stage it will be changed
        found, new_clause, substitution = find_mgu_in_clause(deepcopy(clause1), deepcopy(clause2))
        if found:
            if len(new_clause) == 0:
                got_empty_clause = True
                print("found empty clause!")
                record_list = []
                finish_clause_id = cs.put_clause(new_clause)
                cs.note_done(combination, finish_clause_id, substitution)
                cs.get_reverse_chain(finish_clause_id, record_list=record_list)
                print(record_list)
                print()
                cs.pretty_print_reverse_chain(record_list)
                return True
            new_clause_id = cs.put_clause(new_clause)
            # if new_clause_id is not None:
            cs.note_done(combination, new_clause_id, substitution)
            print("done", combination, "new:", new_clause_id, new_clause)
        else:
            cs.note_impossible(combination)
            # print("impossible", combination)

    return False


def find_mgu_in_clause(clause1: Set[Literal], clause2: Set[Literal]) -> Tuple[
    bool, Set[Literal], Union[None, List[Substitution]]]:
    found_one_mgu = False
    performed_one_remove = False
    subs = None

    for l1 in clause1:
        if not found_one_mgu:
            for l2 in clause2:
                # print(l1, l2, type(l1), type(l2))
                found, subs = find_mgu_wrapper(deepcopy(l1), deepcopy(l2))
                if found:
                    found_one_mgu = True
                    break

    if found_one_mgu:
        new_clause: Set[Literal] = set()
        for l in itertools.chain(clause1, clause2):
            mod_l = copy(l)
            apply_substitution(mod_l, subs)
            not_mod_l = copy(mod_l)
            not_mod_l.negative = not not_mod_l.negative
            if not not_mod_l in new_clause:
                new_clause.add(mod_l)
            else:
                new_clause.remove(not_mod_l)
                performed_one_remove = True
        # print(new_clause)

        if performed_one_remove:
            return True, new_clause, subs
        else:
            return False, set(), None
    else:
        return False, set(), None


def convert_all_to_literal_build_kb(formulas: Iterable[Formula]) -> List[Set[Literal]]:
    kb = []
    for f in formulas:
        cnf = to_CNF_Q(f)
        literal_set_list: List[Set[Literal]] = []
        split_to_literal(cnf, literal_set_list)
        kb.extend(literal_set_list)
    return kb


def resolution_wrapper(formulas: Iterable[Formula]) -> bool:
    kb = convert_all_to_literal_build_kb(formulas)
    for idx, i in enumerate(kb):
        print(idx+1, i)
    cs = ClauseStorage()
    cs.put_clauses(kb)
    return do_resolution(cs)


if __name__ == "__main__":
    # ---- INPUT AREA BEGIN -----


    # worksheet 2, q5
    # x = Variable("x")
    # y = Variable("y")
    # z = Variable("z")
    # Peter = ConstantSymbol("Peter")
    # Anna = ConstantSymbol("Anna")
    # Hans = ConstantSymbol("Hans")
    # Child = PredicateSymbol("Child", 2)
    # Descendant = PredicateSymbol("Descendant", 2)
    #
    # f1 = ForAll(x, ForAll(y, Implies(Or(Child(x,y), Exists(z, And(Child(x,z), Descendant(z,y)))),  Descendant(x,y))))
    # f2 = Child(Peter, Anna)
    # f3 = Child(Anna, Hans)
    # query = Descendant(Peter, Hans)
    #
    # print("Resolutes:", resolution_wrapper([f1, f2,f3,Not(query)]))

    # worksheet 2, q4 / assignment 1 q4
    B = PredicateSymbol("Barber", 1)
    S = PredicateSymbol("Shave", 2)
    x = Variable("x")
    y = Variable("y")

    f1 = ForAll(x, ForAll(y, Implies(And(B(x), Not(S(y, y))), S(x, y))))
    f2 = Not(Exists(x, Exists(y, And(B(x), And(S(x, y), S(y, y))))))
    query = Not(Exists(x, B(x)))

    print("Resolutes:", resolution_wrapper([f1, f2, Not(query)]))

    # worksheet1, 5.6
    # known bug, won't work
    # x = Variable("x")
    # y = Variable("y")
    # D = PredicateSymbol("D", 1)
    # query = Exists(x, Implies(D(x), ForAll(y, D(y))))
    #
    # print("Resolutes:", resolution_wrapper([Not(query)]))


    # worksheet 2, q3.1
    # P = PredicateSymbol("P",2)
    # x = Variable("x")
    # y = Variable("y")
    #
    # query = Implies(Exists(x, ForAll(y, P(y,x))), ForAll(x, Exists(y, P(x,y))))
    #
    # print("Resolutes:", resolution_wrapper([Not(query)]))

    # worksheet 2, q3.2
    # P = PredicateSymbol("P",1)
    # Q = PredicateSymbol("Q",1)
    # x = Variable("x")
    #
    # query = Implies(ForAll(x, Implies(P(x), Q(x))), Implies(ForAll(x, P(x)), ForAll(x, Q(x))))
    #
    # print("Resolutes:", resolution_wrapper([Not(query)]))


    # ---- INPUT AREA END -----
