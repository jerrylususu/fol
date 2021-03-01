from folObj import *

# example 1
P = PredicateSymbol("P", 1)
Q = PredicateSymbol("Q", 1)
x = Variable("x")
formula = Exists(x, And(P(x), Q(x)))
print(formula)

# example 2
x = Variable("x")
y = Variable("y")
z = Variable("z")
Child = PredicateSymbol("Child", 2)
Descendant = PredicateSymbol("Descendant", 2)
formula = ForAll(x, ForAll(y, (Or(Child(x, y), Exists(z, Implies(Or(Child(x, z), Descendant(z, y)), Descendant(x, y)))))))
print(formula)


