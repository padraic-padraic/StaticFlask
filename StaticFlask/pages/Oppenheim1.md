title: 'QInfo'

# Quantum Information Theory 1

## Evolution

Evolution is described by quantum channels. A quantum channel is a **Linear, Completely Positive, Trace Preserving Map**. Each of those terms has a very precise meaning.

1. Linearity
    - A physical map must be linear. This means that for a map $\Lambda(\rho)$, $\Lambda(\rho_{a} + \rho_{b}) = \Lambda(\rho_{a}) + \Lambda(\rho_{b})$.
    - Physical maps must have this quality because....

2. Positivity
    - A map acts on a densitry matrix, which has an interpretation as an ensemble of quantum states where the eigenvalues associated with each state are the probabilities of obtaining that state from a projective measurement in that basis.
    - For this interpretation to be meaningful, the eigenvalues of the densitry matrix must all be postive $p_{i}>0 \forall i$
    - Thus, the eigenvalues new density matrix produce by the applicaiton of the map must also have this property. A map which has this behaviour is called positive.

3. 'Complete' Positivity
    - The map must also be positive when acting on one component of an extended system.
    - This allows for 'local' operations when we don't have access to the whole system.
4. Trace preservation
    - As the eigenvalues of the density matrix are probabilities, we require it has unit trace. For probabilities to remain normalised, we thus require the map to preserve this unit trace.

### The Partial Trace

### The Partial Transpose

## The CHSH Game
Consider a game played by Alice and Bob with a referee. Alice and Bob are sufficiently appart as to have no means of communicating. The referee sends them each a bit, ${r, s} \in {0,1}$, and they must give a reply ${a_{r},b_{s}}\in{0,1}$, such that they win if $ a_{r} \oplus b_{s} = r\wedge s$.

We can easily show that this is not possible to win 100% of the time by considering the 4 scenarios:
\[
a_{0} + b_{0} = 0 \\
a_{1} + b_{0} = 0 \\
a_{0} + b_{1} = 0 \\
a_{1} + b_{1} = 0
\]
sum to $0\oplus 0 \oplus 0 \oplus 0 \oplus 1 \oplus 1 \oplus 1 \oplus 1 \oplus 1 = 0 = 0\oplus 0\oplus 0\oplus0 \oplus 1$, which is inconsistent. At most, three of these simulatenous equations can be satisfied at once.
