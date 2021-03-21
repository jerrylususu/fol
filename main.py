from folObj import *

# example 1

# need to declare symbols first
# all symbols (predicate, constant, functional) has a name
# predicate and functional symbols have to specify argument count (ar)
P = PredicateSymbol("P", 1)
Q = PredicateSymbol("Q", 1)
a = ConstantSymbol("a")
x = Variable("x")

# then you can begin to write formulas
# formulas are written in prefix
formula = Exists(x, And(P(x), Q(x)))
print(formula)

# example 2, worksheet 2 q5
x = Variable("x")
y = Variable("y")
z = Variable("z")
Child = PredicateSymbol("Child", 2)
Descendant = PredicateSymbol("Descendant", 2)
formula = ForAll(x,
                 ForAll(y, (Or(Child(x, y), Exists(z, Implies(Or(Child(x, z), Descendant(z, y)), Descendant(x, y)))))))
print(formula)

# other important items

# And/Or can only have 2 argument, for more you need nest them manually
And(P(a), And(Q(a), P(x)))

# For quantifiers, Use `ForAll` and `Exists`, and write variable as the first parameter
ForAll(x, P(x))
Exists(x, Q(x))