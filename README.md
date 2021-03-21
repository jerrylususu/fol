# KR&R Assignment 1: FoL

Zhirui Lu

Language: Python

Environment Requirement: Python 3.7+

## File Structure

* `folObj.py`: All the classes for FoL, such as `Literal`, `AtomicFormula`, `PredicateSymbol`...
* `main.py`: Example of expressing FoL formula
* `norm.py`: Normalization to CNF without quantifier
* `normQ.py`: Normalization to CNF with quantifer
* `mgu.py`: Find MGU
* `resolute.pu`: Perform resolution

## Run the programs

1. Open the file and go to `if __name__=="__main__"` part
2. Search for `---- INPUT AREA BEGIN -----` and `---- INPUT AREA END -----`
3. Between these two comments are the input area. Some formulas from worksheets are already here but commented. Uncomment them or write new formulas.
4. Run the file using `python3 ${filename}`







## Expressing FoL

see `main.py`

## Convert to CNF

see `normQ.py`

## Find MGU

see `MGU.py`

## Do Resolution

see `resolute.py`

Reference output for Q4:

```
1 {L(AF(PS('Shave', 2), [Var('x'), Var('y')])), ¬L(AF(PS('Barber', 1), [Var('x')])), L(AF(PS('Shave', 2), [Var('y'), Var('y')]))}
2 {¬L(AF(PS('Barber', 1), [Var('x')])), ¬L(AF(PS('Shave', 2), [Var('y'), Var('y')])), ¬L(AF(PS('Shave', 2), [Var('x'), Var('y')]))}
3 {L(AF(PS('Barber', 1), [CS('$c1')]))}
done (3, 1) new: 4 {L(AF(PS('Shave', 2), [CS('$c1'), Var('y')])), L(AF(PS('Shave', 2), [Var('y'), Var('y')]))}
done (3, 2) new: 5 {¬L(AF(PS('Shave', 2), [CS('$c1'), Var('y')])), ¬L(AF(PS('Shave', 2), [Var('y'), Var('y')]))}
found empty clause!
[(3, 1, 4, [ST[Var('x')/CS('$c1')]]), (3, 2, 5, [ST[Var('x')/CS('$c1')]]), (5, 4, 6, [])]

3 {L(AF(PS('Barber', 1), [CS('$c1')]))}
1 {L(AF(PS('Shave', 2), [Var('x'), Var('y')])), ¬L(AF(PS('Barber', 1), [Var('x')])), L(AF(PS('Shave', 2), [Var('y'), Var('y')]))}
θ [ST[Var('x')/CS('$c1')]]
-> 4 {L(AF(PS('Shave', 2), [CS('$c1'), Var('y')])), L(AF(PS('Shave', 2), [Var('y'), Var('y')]))}
-----------
3 {L(AF(PS('Barber', 1), [CS('$c1')]))}
2 {¬L(AF(PS('Barber', 1), [Var('x')])), ¬L(AF(PS('Shave', 2), [Var('y'), Var('y')])), ¬L(AF(PS('Shave', 2), [Var('x'), Var('y')]))}
θ [ST[Var('x')/CS('$c1')]]
-> 5 {¬L(AF(PS('Shave', 2), [CS('$c1'), Var('y')])), ¬L(AF(PS('Shave', 2), [Var('y'), Var('y')]))}
-----------
5 {¬L(AF(PS('Shave', 2), [CS('$c1'), Var('y')])), ¬L(AF(PS('Shave', 2), [Var('y'), Var('y')]))}
4 {L(AF(PS('Shave', 2), [CS('$c1'), Var('y')])), L(AF(PS('Shave', 2), [Var('y'), Var('y')]))}
θ []
-> 6 set()
-----------
Resolutes: True

```



