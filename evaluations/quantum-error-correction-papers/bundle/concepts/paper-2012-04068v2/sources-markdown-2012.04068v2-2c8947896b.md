---
type: Research Paper
title: Quantum LDPC Codes with Almost Linear Minimum Distance
description: '- Pinned arXiv record: [2012.04068v2](https://arxiv.org/abs/2012.04068v2)'
resource: https://example.org/qec-arxiv-papers/resource/paper-2012-04068v2/sources%2Fmarkdown%2F2012.04068v2
tags:
- paper-2012-04068v2
- markdown
- rl
concept_id: concepts/paper-2012-04068v2/sources-markdown-2012.04068v2-2c8947896b
concept_path: concepts/paper-2012-04068v2/sources-markdown-2012.04068v2-2c8947896b.md
subject_iri: https://example.org/qec-arxiv-papers/resource/paper-2012-04068v2/sources%2Fmarkdown%2F2012.04068v2
ontology_class_iri: https://example.org/ontology/qec-arxiv-papers#Paper
ontology_version_iri: https://example.org/ontology/qec-arxiv-papers/1.0.0
source_id: paper-2012-04068v2
source_kind: markdown
source_path: sources/markdown/2012.04068v2.md
source_content_sha256: 8949df94c409ef0da03ad8a9c7224269d48733bcc4b88b60aea6eebc547379a4
record_sha256: 10f2a6152791e49e0ef84c5c3963a346ebe102e208791cb2a77525739b505e6c
source_refs:
- https://example.org/qec-arxiv-papers/provenance/record/paper-2012-04068v2/6e11b58cc72a70b3a039afc3
record_id: sources/markdown/2012.04068v2
---

# Quantum LDPC Codes with Almost Linear Minimum Distance

## Source citation

- Pinned arXiv record: [2012.04068v2](https://arxiv.org/abs/2012.04068v2)
- Authors: Panteleev, Pavel; Kalachev, Gleb
- PDF: [https://arxiv.org/pdf/2012.04068v2](https://arxiv.org/pdf/2012.04068v2)
- PDF SHA-256: `f814847ebd0c1d2dbd277f50037e3ae4bc0bfca30a8784f647f1eee13f4eb132`
- Extracted pages: 17

The following text was extracted page by page from the pinned PDF. Page headings are stable evidence locators.

## PDF page 1

arXiv:2012.04068v2  [cs.IT]  3 Oct 2021
1
Quantum LDPC Codes with Almost Linear
Minimum Distance
Pavel Panteleev and Gleb Kalachev
Abstract—We give a construction of quantum LDPC codes
of dimension Θ(log N ) and distance Θ( N/ log N ) as the code
length N → ∞ . Using a product of chain complexes this
construction also provides a family of quantum LDPC codes of
distance Ω( N 1− α/2/ log N ) and dimension Ω( N α log N ), where
0 ⩽ α < 1. We also introduce and study a new operation called
lifted product, which naturally generalizes the product op erations
for quantum codes and chain complexes. Moreover , as a simple
byproduct of our results on quantum codes, we obtain a new
result on classical codes. We show that for any ﬁxed R < 1
there exists an asymptotically good family of classical qua si-
cyclic LDPC codes of rate at least R with, in some sense, optimal
circulant size Ω( N/ log N ) as the code length N → ∞ .
Index Terms —CSS code, quantum LDPC, quasi-cyclic (QC)
LDPC, hypergraph product code, chain complex.
I. I NTRODUCTION
C
LASSICAL LOW-DENSITY parity-check (LDPC)
codes [1] are a very important class of linear codes
widely used in theory and practise. The deﬁnitive property o f
a family of LDPC codes is that there exists some constant
w such that for any code from this family both the row and
the column weights of its parity-check matrix are bounded
above by w. The theoretical importance of LDPC codes
stems mostly from the fact that they contain asymptotically
good codes of any positive rate with a linear time decoding
that can attain the Shannon capacity [2], [3]. Their quantum
analogs, called quantum LDPC (QLDPC) codes (see [4] for
a good review), may play a very important role in design of
future fault-tolerant quantum computers [5], [6]. However ,
it is still unknown whether there exists an asymptotically
good family of QLDPC codes with a positive rate. More
dramatically, to the best of our knowledge, there are even
no such examples of constant dimension and linear distance,
while in the classical case we have the repetition code as
a trivial example.
Up until very recently, the minimum distance of all
known examples of QLDPC codes [7]–[11] was bounded
above by O(N 1/2 logα N ) for some α ⩾ 0 as the code
length N → ∞. In [12] it was shown that there exists a family
of QLDPC codes of distance and dimension bounded below by
Ω( N 3/5/ polylog N ). The QLDPC codes from the all above-
mentioned papers belong to a wide class of quantum codes
called CSS codes [13], [14]. A CSS code Q of dimension K
is deﬁned by a pair of classical linear codes CZ, CX ⊆ FN
2
such that C⊥
X ⊆ C Z, and K = dim CZ/C⊥
X . Its minimum
distance d is deﬁned as min(dZ, dX), where dZ and dX are
the minimal Hamming weights of the vectors from CZ \ C ⊥
X
Pavel Panteleev and Gleb Kalachev are with the Faculty of Mec hanics and
Mathematics, Moscow State University, Moscow, Russia.
and CX \ C ⊥
Z , respectively. In this case we often say that Q
is an [[N, K, d]] code, or, if we want to be more precise,
an [[N, K, dZ, dX]] code. The code CZ is usually represented
by a parity-check matrix HX, and the code CX by a parity-
check matrix HZ, and C⊥
X ⊆ C Z implies that HXH T
Z = 0.
The approach used in [10]–[12] is, ﬁrst, to construct a quan-
tum code Q with dZ ≫ dX, dZdX > Ω( N ), and then to
apply the homological product [11], [15], [16] of the quantu m
code Q with a classical code C of minimal distance d ≈ dZ/dX
in order to obtain a new quantum code Q′ of distance
min(dZ, d · dX). In [12] this “distance balancing” procedure
was applied to a family of codes (called ﬁber bundle codes)
with parameters dZ = Ω( N 3/4/ polylog N ), dX = Ω( N 1/2),
and K = Θ( N 1/2). We should note that this particular family
of ﬁber bundle codes coincides 1 with an earlier proposed [17]
family of quasi-cyclic GHP codes 2, deﬁned by some quasi-
cyclic matrix A of circulant size ℓ and the polynomial
b = 1 + x, which is a parity polynomial of the cyclic repetition
code of length ℓ. The parity-check matrices HX, HZ for such
codes are binary block matrices that look as follows:
HX =



A11 . . . A 1n
.
.
. . . . .
.
.
Am1 . . . A mn
B . . . 0
.
.
. . . . .
.
.
0 . . . B


;
HZ =



BT . . . 0
.
.
. . . . .
.
.
0 . . . B T
AT
11 . . . A T
m1
.
.
. . . . .
.
.
AT
1n . . . A T
mn


;
(1)
where each Aij is an ℓ × ℓ-circulant matrix (see Appendix A),
and B is the ℓ × ℓ circulant matrix that is the parity-check
matrix for the cyclic code with the parity polynomial b. Since
we want to obtain low-density matrices, the circulants in
the above block matrices should be as sparse as possible. Thi s
is the reason why in all the examples of such codes in [17]
the matrices Aij are circulants of weight 1, i.e., permutation
matrices of some cyclic shifts modulo ℓ.
In the terminology of [12], the polynomial b corresponds
to the ﬁber, and the matrix A to the parity-check matrix of
the base with twists. In [17] this class of codes was studied i n
the case of arbitrary parity polynomial b, and in the case of
odd ℓ a formula for the dimension of such codes was given.
Moreover, several examples of these codes were constructed ,
and one of them was shown to outperform under the BP-OSD
decoder (also proposed in [17]) a relatively large surface c ode
decoded by a near-optimal decoder from [18].
1The deﬁnition of these codes in [12] is given in terms of chain complexes,
while in [17] these codes are deﬁned by parity-check matrice s HX and HZ.
2In the current paper we further generalize these codes and ca ll them lifted
product codes.
Copyright © 2017 IEEE. Personal use of this material is permi tted. However, permission to use this
material for any other purposes must be obtained from the IEE E by sending a request to pubs-permissions@ieee.org.

## PDF page 2

2
In this paper we show that if we carefully choose a low-
density quasi-cyclic matrix A and use b = 1 + x, then
the corresponding GHP code has distance Θ( N/ log N ) and
dimension Θ(log N ) as the code length N → ∞ . This gives
us our ﬁrst main result.
Theorem 1. There exists a family of QLDPC codes of
dimension Θ(log N ) and distance Θ( N/ log N ) as the code
length N → ∞.
The main technical tool in the proof of the above theorem
is expander codes [2], [19], [20]. Such codes are deﬁned by
a graph G and a small linear code C0. In order to obtain a good
expander code, the second largest eigenvalue of the adjacen cy
matrix of G should be sufﬁciently small. A graph 3 that satisﬁes
this condition is called an expander graph (see [21] for a good
survey). An important result, we rely on in our proof, is
Theorem 1.2 from [22], which gives us a way to construct
quasi-cyclic matrices A with the desired properties of very
large circulant size ℓ = Ω( N/ log N ). Using this result, we
ﬁrst construct a large expander graph G with a quasi-cyclic
adjacency matrix of circulant size ℓ from a small expander
graph; then we apply to G the expander code construction
to obtain a code T (G, C0) and deﬁne A as its parity-check
matrix. Since the adjacency matrix of G is quasi-cyclic, it is
possible to deﬁne T (G, C0) in such a way that its parity-check
matrix A is also quasi-cyclic of circulant size ℓ.
As a byproduct of the proof of Theorem 1 we also obtain
(Corollary 1) that there exists a family of classical quasi-
cyclic LDPC codes with distance Θ( N ) and circulant size
Ω( N/ log N ). Using the well-known upper bound [23] on
the minimal distance of quasi-cyclic LDPC codes we show
that, in some sense, this circulant size is optimal.
Though the distance of the obtained quantum codes is
almost linear as N → ∞ , their dimension is only Θ(log N ).
In fact, the dimension can be easily increased by a moderate
reduction of the code distance. The idea is somewhat similar
to the mentioned above “distance balancing” procedure, but
instead of the code distance, we increase the code dimension .
As it was shown 4 in [10, Theorem 2.3], if we have a quantum
[[N, K, dZ , dX ]] code Q and a classical [n, k, d] code C, then
we can obtain the quantum [[N ′, kK, d′
Z, d′
X]] code Q ⊗ C
called the homological product of Q and C such that:
N ′ ⩽ 2nN, d ′
Z ⩾ d · dZ, d ′
X ⩾ dX.
Now if we consider the quantum code (Q ⊗ C )∗, where
we change the roles of codes CZ and CX in Q ⊗ C , and
again apply the homological product with C, then we get
the [[N ′′, k2K, d′′
Z, d′′
X]] code5 (Q ⊗ C )∗ ⊗ C such that:
N ′′ ⩽ 4n2N, d ′′
Z ⩾ d · dZ, d ′′
X ⩾ d · dX. (2)
Therefore in order to obtain codes of large dimension out of
the constructed in this work codes of dimension Θ(log N ) and
3Formally, we should rather talk about an inﬁnite family of gr aphs.
4Note that a similar bound on the distance was obtained earlie r in [16,
Theorem 1] in the language of chain complexes.
5It is not hard to see that this construction is equivalent to t he homological
product of a quantum code and a hypergraph product code deﬁne d by C.
v
v′
base graph G
v1
. . .
vℓ
v′
1
. . .
v′
ℓ
π ∈ Sℓ
ℓ-lift ˆG of G
Fig. 1. Lifting of the base graph G.
distance Θ( N/ log N ) it remains to let C be from a family 6 of
classical LDPC [n, k, d] codes such that k = Θ( n), d = Θ( n),
and n = Θ( N
α
2(1−α) ) as N → ∞ , where α > 0. Indeed, we
can easily check using (2) that as the end result we obtain
the quantum [[N ′′, K′′, d′′]] code such that:
N ′′ = O(n2N ) = O(N
1
1−α ), and hence N = Ω
(
(N ′′)1−α)
;
K ′′ = k2K = Θ( N
α
1−α log N ) = Ω(( N ′′)α log N ′′);
d′′ = Ω( d · N/ log N ) = Ω( n · N/ log N )
= Ω
(
(N ′′)α/2 · N/ log N
)
= Ω
(
(N ′′)1−α/2 log N ′′
)
.
We should emphasize that all the codes involved in the above
construction have low-density parity-check matrices. Hen ce
the obtained quantum codes are QLDPC codes, and we get
the following result.
Theorem 2. F or every α such that 0 ⩽ α < 1 there exists
a family of QLDPC codes of dimension Ω( N α log N ) and
distance Ω( N 1−α/2/ log N ) as the code length N → ∞.
Remark 1. Let us note that the case α = 0 of the above
theorem corresponds to the codes of distance Θ( N/ log N )
and dimension Θ(log N ) from Theorem 1.
Lifted Product Codes
In this paper, we continue our study of the codes from [17]
in a more general form, and call them lifted product (LP)
codes. Roughly speaking, LP codes are the lifted versions of
hypergraph product codes proposed in [9], [24]. As we will
see later in Section III, LP codes generalize many well-know n
examples of QLDPC codes [9], [25]–[27], of which they are
mostly motivated. We should also note that quasi-cyclic LP
codes can be shown to be equivalent to a special case of
hyperbicycle codes [27], when the parameter χ = 1 (see, more
in Subsection III-E).
Large classical LDPC codes are often constructed as lifts of
a small graph called the base graph or the protograph [28].
In graph theory, the Tanner graphs [19] of such ℓ times larger
codes are called ℓ-lifts or ℓ-fold cover graphs for the base
graph. Let us remind that an ℓ-lift ˆG of a base graph 7 G is
obtained if we replace in the base graph each vertex v ∈ V (G)
with ℓ replicas v1, . . . , vℓ; and replace each edge e ∈ E(G)
that connects vertices v, v′ ∈ V (G) with ℓ replicas e1, . . . , eℓ
6As we already mentioned before, asymptotically good classi cal LDPC
codes of non-vanishing rate do exist [1].
7Multiple edges and loops are usually allowed in the base grap h G.

## PDF page 3

3
such that ei connects in ˆG the vertices vi and v′
π(i), where
π ∈ Sℓ is some permutation on the set {1, . . . , ℓ} (see Fig. 1).
Note that the permutations for different edges may be differ ent.
If the set of permutations π is restricted to some ﬁnite
permutation subgroup Γ ⊆ Sℓ such that 8 |Γ | = ℓ, then we
also say that ˆG is a Γ -lift of G, and a shift ℓ-lift when
Γ = ⟨(1, 2, . . . , ℓ)⟩ ⊆ Sℓ is the cyclic group of size ℓ generated
by the permutation (1, 2, . . . , ℓ) ∈ Sℓ.
Note that the parity-check matrix of an LDPC code that was
obtained as a shift ℓ-lift of some base graph is a quasi-cyclic
matrix of circulant size ℓ. Let us brieﬂy remind that quasi-
cyclic (QC) matrices are block matrices, where each block is
an ℓ × ℓ-circulant. They are usually represented by matrices
over the quotient polynomial ring Rℓ = F2[x]/(xℓ − 1).
In a more general case of Γ -lifts the corresponding binary
block matrices can be represented by matrices over a group
algebra F2G, where G is an abstract group of order ℓ that is
isomorphic to the permutation subgroup Γ ⊆ Sℓ.
The idea of the lifted product is to start from two small
Tanner graphs A and B that have some shift ℓ-lifts ˆA and ˆB,
respectively. Let A be the corresponding matrix over Rℓ for ˆA,
and B be the corresponding matrix for ˆB. Since the ring Rℓ
is commutative, we will show in Section III that one can
use a slightly modiﬁed hypergraph product construction [9] in
order to obtain the parity-check matrices HX and HZ over Rℓ.
Finally, we will see that HX and HZ (considered as binary
block matrices) deﬁne a CSS code denoted by LP(A, B).
In fact, the idea of the lifted product is more general and can
be used not only with the ring Rℓ. Later we will show that this
construction works for matrices A and B over any ring R that
is a commutative ℓ-dimensional F2-algebra. For example, if
G is an abelian group of order ℓ, then the group algebra F2G
can be used as the ring R. Hence, we can use not only shift ℓ-
lifts, but also Γ -lifts when the permutation group Γ is abelian.
In fact, the general deﬁnition of lifted product codes, give n
in Section III, can also be used with non-abelian groups as
well. However, in this paper, we consider only abelian group s,
while the non-abelian case is left for future work.
We should emphasize that the codes from Theorem 1
correspond to the case when B is a 1 × 1 matrix with only one
element b ∈ Rℓ. We denote the code LP(A, B) by LP(A, b)
in this case. Later we will show how to ﬁnd or estimate
the dimension of LP(A, B) and LP(A, b) in many special
cases.
In Fig. 2 you can see the parameters of the LP codes from
Theorems 1 and 2 (shown in red) against the parameters
of the ﬁber bundle (FB) codes [12] (shown in green) and
the hypergraph product (HP) codes [9] (shown in blue). In fac t,
if we apply the method used in Theorem 2 to the ﬁber bundle
codes, then we can also increase their dimension in the same
way as for LP codes. The parameters of the quantum codes
obtained in this way are also shown in green. We can see
from Fig. 2 that (up to polylog factors) the parameters of
the all mentioned above codes converge to the parameters
8Such groups are obtained from some abstract ﬁnite group as th e group of
all its left actions on itself.
N/ log N
log N
N 1/2
N 3/5/ polylog N
N 3/5/ polylog N N
HP
LP
FB
?
K
d
Fig. 2. HP – hypergraph product codes, FB – ﬁber-bundle codes , LP –
lifted product code LP(A, 1 +x). The parameters of all codes (the minimum
distance d and the dimension K) are shown in the logarithmic scale up to
polylogarithmic factors as the code length N → ∞ .
of the hypergraph product codes as the dimension K grows
asymptotically up to the code length N .
Lifted products of chain complexes
Let us brieﬂy show how to extend the idea of the lifted
product to chain complexes. It is known that 2-dimensional
chain complexes correspond to CSS codes [29]. Nevertheless ,
s-dimensional chain complexes for s > 2 can also be useful
in the context of single-shot error correction [30].
Consider some commutative ring R. Let us remind that
a free R-module of rank r is an R-module M , where there
exists a set of elements {m1, . . . , mr} ⊆ M called basis such
that every m ∈ M is uniquely represented as:
m = a1m1 + · · · + armr,
where a1, . . . , ar ∈ R. Hence M ∼
= Rr, and if the ring R
is a ﬁeld, then M is simply an r-dimensional vector space
over R. A canonical example of a free R-module of rank r is
the module of formal R-linear combinations of the elements
of some set S, where |S| = r.
By a chain complex over a commutative ring R we mean
a free R-module C = ⨁
i∈Z Ci with an R-linear map ∂ : C → C
called a boundary map such that ∂2 = 0 , and ∂(Ci) ⊆ C i−1.
We suppose that each free R-module Ci has ﬁnite rank, and
Ci = 0 when i < 0 or i > n , where the parameter n is called
the dimension of C. We also assume that each Ci comes with
some preferred basis ˜Ci ⊆ C i, and we call its elements i-cells.
An n-dimensional chain complex C is usually written as
Cn
∂n
− → Cn−1
∂n−1
− − − → · · ·
∂2
− → C1
∂1
− → C0,
where ∂i = ∂|Ci, i = 1, . . . , n.
The lifted product of two chain complexes is obtained in
a similar way as for codes. We just consider the standard tens or
product A ⊗ B of chain complexes A, B over a commutative 9
9For simplicity we deﬁne here the lifted product only for comm utative
rings, though it may be easily extended to any ring R if we consider a tensor
product A ⊗ B of a free right R-module A and a free left R-module B.

## PDF page 4

4
ring R with boundary maps ∂A, ∂B, respectively. Thus if R is
in turn an ℓ-dimensional F2-algebra with some ﬁxed basis 10
˜R = {r1, . . . , rℓ} ⊆ R,
then the boundary map ∂ = ∂A ⊗ idB + idA ⊗ ∂B of A ⊗ B is
an R-linear map, and hence an F2-linear map. Therefore we
can consider A ⊗ B also as a chain complex over F2, which
we call the lifted product of the chain complexes A and B,
and denote by A ⊗R B in order to emphasize the role of R.
When R = Rℓ we use a shorter notation A⊗ℓB. The n-cells of
the obtained chain complex A⊗ R B take the form: ra(i) ⊗b(j);
where r ∈ ˜R, a(i) is an i-cell from ˜Ai, b(j) is a j-cell from ˜Bj,
and i + j = n.
Note that any matrix over an ℓ-dimensional F2-algebra R
deﬁnes some binary linear code as its parity-check matrix 11.
For example, any matrix over Rℓ deﬁnes a quasi-cyclic code.
Any such linear code can be identiﬁed with the corresponding
1-dimensional chain complex C1
∂1
− → C0 such that A is a matrix
of the R-linear map ∂1. Let A, B be 1-dimensional chain
complexes over R that correspond to the classical codes with
parity-check matrices A, B over R, respectively. Then it is not
hard to see that the CSS code LP(A, B) deﬁned in Section III
corresponds to the 2-dimensional chain complex A ⊗R B.
The remainder of the paper is structured as follows.
Section II contains some standard deﬁnitions and notations
related to codes. In Section III we give the deﬁnition of lift ed
product codes, where we also demonstrate that they contain
many well-known QLDPC codes. Expanders are described in
Section IV. Then we proceed with the proof of Theorem 1 in
Section V, and in the last section, we give some ﬁnal remarks.
The paper also contains three appendices, where we describe
some well-known facts on the ring Rℓ (Appendix A), study
the decomposition of quasi-abelian LP codes when the lift
size is odd (Appendix 12 B), and give the list of frequently
used symbols and abbreviations (Appendix C).
II. B ASIC FACTS AND DEFINITIONS
Here we ﬁx notations and brieﬂy recall some standard
deﬁnitions related to classical and quantum codes. More
information can be found in a survey [4]. In what follows, we
assume that the reader is familiar with the standard algebra ic
objects like rings, ﬁelds, vector spaces, and modules (see [ 31]
for a good reference).
In this paper, it is convenient to consider vectors over a ﬁel d
or a ring as column vectors. Hence the matrix-vector product
is written as Av instead of AvT. Besides, we denote by ker A
and im A the kernel and the image of the corresponding linear
operator v ↦→ Av, respectively. Note that im A coincides
with the column space of the matrix A. In many places
we use the standard notation [n] = {1, 2, . . . , n}, where
n is a natural number. If x, y are two binary vectors of
length n, then we denote by x ∩ y their intersection, i.e.,
10For example, for Rℓ the standard basis is ˜Rℓ = {1, x, . . . , xℓ− 1}; for
F2G the standard basis is G.
11Any m × n matrix over R can be also considered as an ℓm × ℓn binary
block matrix (see Section III).
12Our main results do not rely on this supplementary material.
the vector x ∩ y = ( x1y1, . . . , xnyn). We say that an event
An occurs with high probability (w.h.p) if P(An) → 1 as
n → ∞ . Please, refer to Appendix C for the list of symbols
and abbreviations frequently used in our work.
A. Classical codes
Consider a ﬁnite ﬁeld 13 Fq and an n-dimensional vector
space Fn
q over Fq. A linear [n, k]q code is a k-dimensional
subspace C ⊆ Fn
q , where the parameters n and k are called
the length and the dimension of C, respectively. We denote
the dimension k of the code C by dim C. The rate of the code C
is equal to k/n. The elements of C are called codewords.
The Hamming distance d(v, v′) between vectors v, v′ ∈ Fn
q
is the number of positions in which they differ. The paramete r
d(C) = min {d(c, c′) | c ̸= c′; c, c′ ∈ C}
is called the minimal distance of C. By deﬁnition, we
put d(C) = ∞ when k = 0 . It is easy to see that d(C) is
equal to the minimal weight |c| of non-zero codewords, where
the weight |c| is the number of non-zero components in c.
When d(C) = d for a linear [n, k]q code C, we say that C is
an [n, k, d]q code.
A linear [n, k]q code is usually deﬁned either as the row
space of a matrix G called the generator matrix or as the kernel
of a matrix H called the parity-check matrix. It is easy to see
that GH T = 0, rk G = k, and rk H = n−k. The code deﬁned
by a parity-check matrix H is denoted by C(H).
The vector space Fn
2 usually comes with the standard scalar
product ⟨x, y⟩ = x1y1 + · · · + xnyn. The dual code C⊥ for
a linear [n, k]q code C is the [n, n − k]q code
C⊥ = {x ∈ Fn
q | ⟨x, y⟩ = 0 for all y ∈ C} .
It is not hard to see that a generator matrix for C is a parity-
matrix for C⊥ and vice versa.
Let π ∈ Sn be a permutation on the set [n]. Given a vector
v = ( v1, . . . , vn), we denote by π(v) the permuted vector
(vπ(1), . . . , vπ(n)). We also extend this notation to sets of
vectors of length n in a straightforward way:
π(S) = {π(v) | v ∈ S}.
We say that two codes C, C′ ⊆ Fn
q are (permutation) equivalent
and write C ∼ C ′ if C′ = π(C) for some π ∈ Sn. It is clear
that equivalent codes have the same parameters [n, k, d]q.
In this paper we mostly deal with binary linear codes , i.e.,
when q = 2. In such cases we omit q and simply write [n, k]
or [n, k, d] code.
B. Quantum CSS codes
Consider the 2n-dimensional Hilbert space C2n
, where
the 2n standard basis vectors are indexed by binary vectors
u ∈ Fn
2 and denoted by |u⟩. The space C2n
= ( C2)⊗n is
usually called the n-qubit space , where each component in
the tensor product corresponds to one qubit.
13In this paper we consider only ﬁnite ﬁelds of characteristic 2, but most
of the results are valid for arbitrary ﬁnite ﬁelds.

## PDF page 5

5
A quantum code Q of length n and dimension k is
a 2k-dimensional subspace of C2n
. As in the classical case,
we denote the dimension k of the quantum code by dim Q.
In [13], [14] a very important subclass of quantum codes call ed
the Calderbank-Shor-Steane (CSS) codes , which is related to
classical linear codes, was introduced. A quantum CSS [[n, k]]
code Q of length n and dimension k is deﬁned by two
classical linear codes CZ, CX ⊆ Fn
2 such that C⊥
X ⊆ C Z and
k = dim CZ/C⊥
X in the following way:
Q = span C
{∑
x∈C⊥
X
|z + x⟩ | z ∈ C Z
}
.
It is easy to see that the property C⊥
X ⊆ C Z is equivalent
to C⊥
Z ⊆ C X. Moreover, if HX is a parity-check matrix of CZ,
HZ is the parity-check matrix of CX; then this property can
be expressed as the following orthogonality condition :
HXH T
Z = 0. (3)
Hence in order to deﬁne a CSS code, we need two parity-
check matrices HX and HZ such that every row of HX is
orthogonal to every row of HZ. The dimension k = dim Q of
the obtained quantum code Q is given by
k = n − rk HX − rk HZ, (4)
since k = dim CZ/C⊥
X .
Given a quantum CSS code Q, we call the codewords from
the codes CZ = CZ(Q) and CX = CX(Q) the Z-codewords and
X-codewords of Q, respectively. Furthermore, the Z-codewords
from C⊥
X and the X-codewords from C⊥
Z are called degenerate.
This name can be explained if we interpret the codewords
from CZ and CX as undetected errors in a quantum system
protected by the quantum code Q. It can be shown that
the degenerate errors are precisely the ones that don’t chan ge
the state of the system. Therefore it makes sense to consider
the quotient spaces CZ/C⊥
X , CX/C⊥
Z instead of CZ, CX. We say
that codewords c, c′ from the same equivalence class in these
quotient spaces are equivalent and denote this fact by c ∼ c′.
It is obvious that a codeword c is degenerate iff c ∼ 0, where
0 is the zero vector. Let us note that the degenerate codewords
correspond to the stabilizers of the quantum code Q; while
the quotient spaces CZ/C⊥
X , CX/C⊥
Z correspond to the logical
operators, acting on the quantum states protected by Q.
Let us note that the spaces of degenerate Z-codewords C⊥
X
and degenerate X-codewords C⊥
Z are generated by the rows of
the parity-check matrices HX and HZ, respectively. Hence the
difference c−c′ of two equivalent codewords is always a linear
combination of the rows from the corresponding parity-chec k
matrix.
Since CSS codes have two types of codewords, they also
have two types of minimum distances:
dZ(Q) = min
z∈CZ\C⊥
X
|z|, d X(Q) = min
x∈CX\C⊥
Z
|x|.
The minimum of these distances
d(Q) = min {dZ(Q), dX(Q)}
is called the minimum distance of Q. As in the case of
the classical codes, we say that a quantum CSS [[n, k]] code
is an [[n, k, d]] code if d(Q) = d.
As in the case of classical codes, we also say that two CSS
codes Q, Q′ of length n are (permutation) equivalent and write
Q ∼ Q ′ if CZ(Q) = π(CZ(Q′)) and CX(Q) = π(CX(Q′))
for some π ∈ Sn. It is clear that equivalent codes have
the same parameters [[n, k, d]], and, moreover, we see that
dZ(Q) = dZ(Q′), dX(Q) = dX(Q′). For any CSS code Q we
can also deﬁne the CSS code Q∗ with CZ(Q∗) := CX(Q) and
CX(Q∗) := CZ(Q). It is obvious that:
dZ(Q∗) = dX(Q), d X(Q∗) = dZ(Q). (5)
The CSS codes deﬁned so far are binary quantum codes.
In some cases, we also need non-binary CSS codes . They
are deﬁned by two matrices HX and HZ over Fq that satisfy
equation (3). The deﬁnitions of dimension, minimum distanc e,
degenerate codewords, equivalent codewords are obtained
from the corresponding deﬁnitions for binary CSS codes if
we replace F2 by Fq.
C. Classical and quantum LDPC codes
A classical low density parity check (LDPC) code [1] is
a linear code deﬁned by a sparse binary parity-check matrix
H = (hij)m×n. The sparseness usually means that the weights
of all rows and columns in H are upper bounded by some
constant w as the code length n grows to inﬁnity. It is helpful
to deﬁne the bipartite graph T = T (H) called the T anner
graph [19]. In this graph the ﬁrst part of nodes v1, . . . , vn
(called the v-nodes) corresponds to the columns of H (the
variables), the second part of nodes c1, . . . , cm (called the
c-nodes) corresponds to the rows of H (the checks), and we
connect a v-node vj with with a c-note ci whenever hij = 1,
i ∈ [m], j ∈ [n].
If the parity-check matrix H is (wc, wr)-regular (i.e., each
column has weight wc and each row has weight wr) then the
corresponding Tanner graph is also (wc, wr)-regular (i.e., each
v-node has degree wc and each c-node has degree wr). We say
that an LDPC code is w-limited if the degree of each node
in its Tanner graph is upper bounded by w. It is obvious that
any LDPC code with (wc, wr)-regular parity-check matrix is
max(wc, wr)-limited.
In this paper by a quantum LDPC (QLDPC) we mean a CSS
[[n, k, d]] code with sparse parity-check matrices HX and HZ.
We can also introduce the Tanner graph T = T (HX, HZ) for
any CSS [[n, k, d]] code Q deﬁned by HX and HZ. In this case,
the v-nodes correspond to n qubits and the c-nodes to the rows
of HX and HZ called the X-checks and Z-checks, respectively.
We connect a v-node with a c-node if the corresponding qubit
participates in the corresponding check. Similar to the cla ssic
case we say that a QLDPC code is w-limited if the degree of
each node in its Tanner graph is upper bounded by w. This
property is much more important in the quantum case due to
the faulty nature of the current quantum hardware. It is clea r
that any CSS code with (wc, wr)-regular matrices HX and
HZ is max(2wc, wr)-limited.
III. L IFTED PRODUCT
In this section, we give our main deﬁnition of lifted product
codes and show how it generalizes several known types of

## PDF page 6

6
quantum codes [9], [25]–[27]. We also show how to estimate
the dimension of our codes in some important special cases,
and give several examples. Finally, in Subsection III-F, we
consider a more speciﬁc case of our codes, ﬁrst deﬁned in [17] ,
and show how to ﬁnd the dimension. Later, in Section V, we
will use this special case to construct quantum LDPC with
almost linear distance.
Before we move to the description of our codes, we need
some standard deﬁnitions and notations from algebra. Let
R be a ring. We denote the set of all m × n matrices
over R by Mm×n(R) or by Mn(R) in the case m = n.
Consider a ﬁeld F. In what follows by an F-algebra we always
mean an associative algebra with a multiplicative identity . It
is well known [32, Theorem 1.3.1] that every such algebra has
a faithful representation by ℓ × ℓ matrices over F, and for any
element a ∈ R we denote by B(a) the corresponding ℓ × ℓ
matrix over F. In the cases when R is already a matrix ring
over F we assume that B(a) = a. Moreover, if A = (aij)m×n
is a matrix over R, then we consider the corresponding block
matrix
B(A) = [ B(aij)]m×n ∈ M ℓm×ℓn(F).
It is easy to see that for any matrices A, B over R we have:
B(AB) = B(A)B(B); (6)
In this work we are mostly interested in the case when R is
a group algebra F2G for some ﬁnite group G. The elements
of F2G are formal sums ∑
g∈G αgg, where αg ∈ F2. Consider
elements a = ∑
g∈G αgg and b = ∑
g∈G βgg from F2G. Their
sum a + b and product ab are deﬁned as follows:
a + b =
∑
g∈G
(αg + βg)g, ab =
∑
g∈G
( ∑
hr=g
h,r∈G
αhβr
)
g.
If we index the elements of the group G = {g1, . . . , gℓ}, then
for every element a = ∑
g∈G αgg ∈ F2G we deﬁne
/CQ (a) = ( αg1 , . . . , αgℓ ) ∈ Fℓ
2;
B(a) =
∑
g∈G
αgB(g),
where B(g) is the permutation ℓ×ℓ matrix, deﬁned as follows:
B(g)ij =
{
1, if gi = ggj;
0, otherwise.
For every vector v ∈ (F2G)n we also consider the block vector
/CQ (v) = [ /CQ (v1), . . . , /CQ (vn)] ∈ Fℓn
2 .
It is not hard to see that for any a ∈ F2G the weight of each
row and each column of the binary matrix B(a) is the same
and equal to |
/CQ (a)|. Thus the row and column weights of
the block matrix B(A), where A = ( aij)m×n is a matrix
over F2G, can be easily found from the corresponding weight
matrix (also called the base matrix) W = W (A) = ( wij)m×n,
where wij = |/CQ (aij)|. For example, B(A) is w-limited iff
the sum of elements of any row and column in W is bounded
above by w. The matrix W can be interpreted as the adjacency
matrix for the base Tanner graph T that was used to obtain
the G-lifted Tanner graph ˆT for the code C(A) with the parity-
check matrix B(A), where wij is equal to the number of edges
between nodes vi and vj in the base Tanner graph T .
Sometimes, where it does not cause confusion, we identify
matrices and vectors over R = F2G with the corresponding
block matrices B(·) and vectors /CQ (·) over F2. For example,
if we say that A is w-limited, then it means that B(A)
is w-limited. For any vector v ∈ Rn we denote by |v|
the Hamming weight |/CQ (v)| of the corresponding block vector
/CQ (v) ∈ Fn
2 . We also often implicitly use the following trivial
equality:
/CQ (Av) = B(A)/CQ (v); (7)
where v is a vector, and A is a matrix over F2G.
If H is a matrix over R = F2G where |G| = ℓ, then by
C(H) we denote the set
C(H) = {c ∈ Rn | Hc = 0}.
It is clear that the set C(H) is also a vector space over F2, and
from (7) we see that it corresponds to the binary linear code
C(B(H)) ⊆ Fℓn
2 deﬁned by the binary block matrix B(H).
Let us note that if G is abelian then F2G is a commutative
ring. Speciﬁcally, if G is a cyclic group Cℓ of order ℓ generated
by x, then F2Cℓ is isomorphic as a ring to the polynomial
quotient ring F2[x]/(xℓ − 1). We denote this ring by Rℓ and
usually represent its elements by polynomials in x. If we index
the elements of the group Cℓ as gi = xi−1, i ∈ [ℓ], then the set
of binary matrices B(a) where a ∈ Rℓ is the ring of circulant
ℓ × ℓ matrices over F2. More details on Rℓ can be found in
Appendix A.
In this paper, with some small abuse of terminology,
a matrix A over Rℓ and the corresponding binary block matrix
B(A) are called quasi-cyclic (QC) of lift size ℓ (also called
the circulant size ). Thus every ℓm × ℓn binary QC matrix
of lift size ℓ can be represented by some polynomial matrix
A ∈ M m×n(Rℓ). The class of QC matrices is well known
in coding theory since they are the parity-check matrices of
quasi-cyclic codes. At the same time, if G is a ﬁnite abelian
group, then matrices over F2G and the corresponding binary
classical error-correcting codes are called quasi-abelian. Note
that most of the best practical classical LDPC codes have
QC parity-check matrices.
Example 1. Consider a matrix A ∈ M 2×3(R3) deﬁned as
follows:
A =
( 1 0 1 + x2
1 + x 1 + x + x2 x2
)
.
It has the corresponding block matrix of lift size ℓ = 3
B(A) =








1 0 0
0 0 0 1 1 0
0 1 0 0 0 0 0 1 1
0 0 1 0 0 0 1 0 1
1 0 1 1 1 1 0 1 0
1 1 0 1 1 1 0 0 1
0 1 1 1 1 1 1 0 0








,
and the corresponding integer weight matrix
W (A) =
( 1 0 2
2 3 1
)
.

## PDF page 7

7
A. Generalized bicycle (GB) codes
The orthogonality condition (3) from the deﬁnition of CSS
codes for the parity-check matrices HX and HZ is a serious
obstacle to designing good QLDPC codes using random-like
constructions similar to the constructions used for classi cal
LDPC codes. Thus it makes sense to consider large families
of matrices of some particular form, where the orthogonalit y
condition is always satisﬁed. One such quite general form
for CSS codes was proposed in [27]. We call these codes
the generalized bicycle (GB) codes since they include bicycle
QLDPC codes [33] as a special case. Let us brieﬂy remind this
construction. Consider two commuting binary ℓ×ℓ matrices A
and B, i.e., AB = BA. Let us deﬁne the parity-check matrices
as follows:
HX = [A, B] and HZ = [BT, AT]. (8)
Then we see that HXH T
Z = AB + BA = 0. Hence
the commutativity condition (3) is always satisﬁed, and we
obtain a CSS code. It was proposed in [27] to use binary
circulant matrices A and B since they always commute.
The corresponding class of codes includes the bicycle codes
from [33] as a special case when B = AT.
Furthermore, we can obtain a more general class of codes
if A and B are some ℓ × ℓ matrices representing elements
from a group algebra F2G for an abelian group G, |G| = ℓ.
For example, the quasi-cyclic CSS codes from [25] can be
considered as GB codes with G = CP × CL/2. At the same
time, Haah’s cubic codes [26] can also be considered as GB
codes with G = CL × CL × CL, where L is the lattice size.
B. Hypergraph product (HP) codes
Before we formally describe the LP codes in the next
section, let us ﬁrst remind the deﬁnition of the hypergraph
product (HP) codes from [9]. Note that originally these code s
were deﬁned in terms of hypergraphs, but here it will be more
convenient for us to give their deﬁnition in a matrix form.
Suppose that we have an [nA, kA, dA] linear code C(A) and
an [nB, kB, dB] linear code C(B) with parity-check matrices 14
A ∈ M mA×nA(F2) and B ∈ M mB ×nB (F2), respectively.
Then the hypergraph product (HP) code is the CSS [[N, K, d]]
code denoted HP(A, B) with the parity-check matrices:
HX = [A ⊗ ImB , ImA ⊗ B],
HZ = [InA ⊗ BT, AT ⊗ InB ], (9)
where the length N and the dimension K are as follows:
N = nAmB + nBmA,
K = 2kAkB − kA(nB − mB) − kB(nA − mA). (10)
As it was shown in [9], the minimum distance d of the
hypergraph product code HP(a, b) satisﬁes the following lower
bound:
d ⩾ min(dA, dB, dT
A, dT
B),
where the parameters dT
A and dT
B are the minimal distances
of the “transposed” codes C(AT) and C(BT) deﬁned by
the parity-check matrices AT and BT, respectively.
14The parity-check matrices are not necessary full rank.
It is important to note that if the matrices A and B are
(wc, wr)-limited then the parity-check matrices HX and HZ of
the code HP(A, B) are w-limited, where w = 2 max(wc, wr).
Hence, using known asymptotically good families of classi-
cal LDPC codes with (wc, wr)-limited parity check-matrices,
it is possible [9] to construct w-limited CSS codes with
asymptotically non-zero rate and d = Θ(
√
N ) as the code
length N → ∞.
C. Non-binary HP codes
Though HP codes in the previous section are deﬁned as
binary CSS codes, it is also quite straightforward to deﬁne
their non-binary versions over an arbitrary ﬁnite ﬁeld Fq.
Suppose that the characteristic of Fq is 2; then the parity-check
matrices HX and HZ for the non-binary HP code HP(A, B)
are obtained from matrices A and B over Fq by (9) as for the
case of binary HP codes.
If the characteristics of Fq is not 2, we need a slightly
modiﬁed version of (9) in order to satisfy the orthogonality
condition HXH T
Z :
HX = [A ⊗ ImB , −ImA ⊗ B],
HZ = [InA ⊗ BT, AT ⊗ InB ]. (11)
D. Lifted product (LP) codes
Here we consider a large family of quantum CSS codes
that simultaneously generalize the GB codes and the HP
codes. These codes ﬁrst appeared in our previous work [17] in
a more restricted form under the name generalized hypergraph
product (GHP) codes. In this work we present them in
a more general form and propose a more informative name —
lifted product (LP) codes . In some sense, we can view these
codes as lifted versions of HP codes from [9], where we lift
the coefﬁcients in the matrices from the binary ﬁeld F2 up
to some ring R that is also a ﬁnite dimensional F2-algebra.
Let us remind that the elements of R can be represented by
binary ℓ × ℓ matrices. Hence when we deﬁne the LP code
over R we identify R with the corresponding matrix ring 15.
Therefore without loss of generality in the deﬁnition below
we assume that R ⊆ M ℓ(F2), and B(a) = a for every a ∈ R.
Thus LP codes are essentially HP codes, where we replace
elements in their binary matrices A and B by some elements
of a matrix ring R ⊆ M ℓ(F2). As the result, we have matrices
A ∈ M mA×nA (R) and B ∈ M mB ×nB (R) over some matrix
ring R ⊆ M ℓ(F2). If M = (mij)m×n is a matrix over R we
can consider its conjugate transpose M ∗ = (mT
ji)n×m, where
mT
ji is the standard transpose of the matrix mji ∈ M ℓ(F2).
Let us emphasize that B(M ∗) = B(M )T. Now, as in the case
of HP codes, we also introduce matrices:
HX = [A ⊗ ImB , ImA ⊗ B],
HZ = [InA ⊗ B∗, A∗ ⊗ InB ]. (12)
These matrices have coefﬁcients from the matrix ring R,
but we can consider the corresponding binary block matrices
15In each example of a ﬁnite dimensional F2-algebra below we always
provide the corresponding matrix representation.

## PDF page 8

8
B(HX) and B(HZ). In order to deﬁne a CSS code, we need to
make sure that these block matrices satisfy the orthogonali ty
condition B(HX)B(HZ)T = 0. Since B(HZ)T = B(H ∗
Z),
using (6) we see that condition is equivalent to HXH ∗
Z = 0,
and thus can be rewritten as:
[A ⊗ ImB , ImA ⊗ B]
[
InA ⊗ B
A ⊗ InB
]
= 0,
which can be further simpliﬁed to
(A ⊗ ImB)(InA ⊗ B) + (ImA ⊗ B)(A ⊗ InB) = 0. (13)
It is not hard to see that if every element of A commutes
with every element of B (we call such matrices element-wise
commuting) then using the mixed-product formula
(X ⊗ Y )(X ′ ⊗ Y ′) = ( XX ′ ⊗ Y Y ′)
for the Kronecker product ⊗ we have:
(A ⊗ ImB)(InA ⊗ B) = ( ImA ⊗ B)(A ⊗ InB) = A ⊗ B.
Since R is a ring of characteristic 16 2, condition (13) is
satisﬁed, and every pair of element-wise commuting matrice s
A and B deﬁnes the CSS code with the parity-check matrices
B(HX) and B(HZ). We denote this code by LP(A, B) and
call the lifted product (LP) code . In what follows HX and HZ
are also called the parity-check matrices for LP(A, B)
One can easily verify that if we take R = F2 ∼
= M1(F2)
then LP codes coincide with HP codes. We can also see that
the generalized bicycle (GB) codes with two commuting ℓ × ℓ
matrices A and B given in (8) are also a special case of LP
codes if we consider the matrices A and B as 1 × 1 matrices
over Mℓ(F2).
The code length N of the CSS code LP(A, B) is given by
N = ℓ(nAmB + nBmA). We are not aware of any simple
way to ﬁnd the dimension K of the code LP(A, B) in the
general case, but it is possible to ﬁnd or estimate K in some
special cases. For example, if mA < n A and mB > n B, then
by counting the number of rows in B(HX) and B(HZ) we
obtain from (4) the following lower bound:
K ⩾ ℓ(nA − mA)(mB − nB).
Below we consider some other examples.
Example 2. If R is a ﬁnite ﬁeld Fq with q = 2 r elements and
A, B are some matrices over Fq, then the code LP(A, B) is
obtained from the non-binary code HP(A, B) if we replace
each non-binary element α in the parity-check matrix HX
of HP(A, B) by the corresponding associated r × r binary
matrix17 Mα. At the same time, in the parity-check matrix
HZ each non-binary element α is replaced by M T
α . Thus
we obtain binary block matrices that deﬁne the binary CSS
code LP(A, B). It is clear that the length of the binary code
LP(A, B) is r times the length of the corresponding non-
binary code HP(A, B). It is also not hard to check that
the dimension of LP(A, B) is also r times bigger:
dim LP(A, B) = r dim HP(A, B). (14)
16If char R ̸= 2 we should deﬁne HX = [ A ⊗ ImB , −ImA ⊗ B].
17The ﬁnite ﬁeld Fq, q = 2 r, is an r-dimensional vector space over F2.
The associated matrix Mα for α ∈ Fq is the matrix of the F2-linear transform
x ↦→αx.
Example 3. If A is some m × n matrix over a commutative
ring R ⊆ M ℓ(F2) and B = A∗, then we have the LP code
LP(A) = LP( A, A∗) of length
N = ℓ(n2 + m2)
and dimension
K ⩾ ℓ(n − m)2,
with parity-check matrices
HX = [A ⊗ In, Im ⊗ A∗],
HZ = [In ⊗ A, A∗ ⊗ Im].
The lower bound for K easily follows from the CSS dimension
formula (4) if we take into account that matrices HX and HZ
have no more than 2ℓmn rows in total. Moreover, if A is full
rank (as a binary block matrix), then the matrices A ⊗ ImB
and InA ⊗ A are also full rank. Hence all rows in B(HX) and
B(HZ) are independent and we see that:
K = ℓ(n − m)2.
E. Quasi-cyclic and quasi-abelian LP codes
One simple way to make all matrices over R to be element-
wise commuting is to enforce R to be a commutative ring.
In this section we consider one particularly important spec ial
case of LP codes with commutative ring R = Rℓ that we
call quasi-cyclic (QC) LP codes , and its generalization called
quasi-abelian (QA) LP codes when R = F2G for some ﬁnite
abelian group G. As we saw at the beginning of this section,
if R is one of these rings we can easily control the density
of the parity-check matrices B(HX) and B(HZ) by looking
at the weight matrices W (HX) and W (HZ). In what follows,
we are going to identify matrices and vectors over R = F2G
with the corresponding block matrices B(·) and vectors
/CQ (·)
over F2.
One big advantage of QC LP codes is that they are
constructed from classical QC LDPC codes. There are many
examples of such codes with very good parameters.
Example 4. Consider the [155, 64, 20] QC LDPC code C(A)
of circulant size ℓ = 31 from [34].
A =


x x 2 x4 x8 x16
x5 x10 x20 x9 x18
x25 x19 x7 x14 x28


We can construct the 8-limited code LP(A) = LP( A, A∗)
(see Example 3) with parameters [[1054, 140, d]]. We should
note that after an extensive simulation under the BP-OSD
decoder [17] we have not found any non-degenerate codeword
of weight less than 20.
If an element a = ∑
g∈G αgg ∈ F2G is represented by
the matrix B(a) ∈ M ℓ(F2), then we have B(a)T = B(¯a),
where ¯a = ∑
g∈G αgg−1 ∈ F2G. The map a ↦→¯a is called
the antipode map for F2G. If the group G is abelian, then
the antipode map is an automorphism of F2G that respects
the weight of elements, i.e., for any u, v ∈ F2G we have:
u + v = ¯u + ¯v, uv = ¯u¯v, |¯u| = |u|.

## PDF page 9

9
For example, for any a = a0 + a1x + · · · + aℓ−1xℓ−1 ∈ Rℓ
we have ¯a = a0 + aℓ−1x + · · · + a1xℓ−1, i.e., ¯a = xℓa(x−1).
If A = ( aij)m×n is a matrix over F2G, then it is clear
that the conjugate transpose deﬁned in subsection III-D is
the matrix A∗ = (¯aji)n×m. Since the antipode map is
an automorphism of F2G, one can easily check that:
rkF2 A = rk F2 AT = rk F2 A∗ = rk F2
¯A, (15)
where ¯A = (¯aij)m×n = ( A∗)T. At the same time, since
the map u ↦→ ¯u just permutes the bits in u, it is not
hard to verify that LP(A, B) ∼ LP( ¯A, ¯B). Besides, for
Q = LP( A, B) we see from equation (12) that when we
change the roles of the matrices HX and HZ, we obtain
the code Q∗ that is permutation equivalent to LP(B∗, A∗)
and also to LP(A∗, B∗). Hence we have that:
Q∗ ∼ LP(A∗, B∗) ∼ LP(
A∗, B∗) = LP( AT, BT),
and by (5) we have:
dZ(LP(A, B)) = dX(LP(AT, BT));
dX(LP(A, B)) = dZ(LP(AT, BT)). (16)
Equations (16) allow us to reduce a problem of ﬁnding
dX(LP(A, B)) to a similar problem for dZ(LP(A, B) and vice
versa.
Let us note that QC LP codes are permutation equivalent
to a special case of hyperbicycle codes [27]. If we let χ = 1
in equation (19) from [27], then the obtained CSS code is
permutation equivalent to the code LP(A, B); where ℓ := c,
A := ∑
i aixi, B := ∑
i bixi. We should also note that some
general results on hyperbicycle codes, such as Theorem 3
from [27], can be applied to QC LP codes if we assert that
χ = 1.
F . Special case of QC LP codes
Let us describe a more speciﬁc case of QC LP codes
used in [17] in order to construct several examples 18 with
good error-correcting performance in the depolarizing cha nnel.
In [17] for simplicity we considered only the case when the
lift size is odd. Here we consider the general case.
Let polynomial b ∈ F2[x] be an irreducible factor of
xℓ − 1 and A = ( aij)m×n be a matrix over Rℓ. Consider
the code LP(A, b), where we understand b as a 1 × 1 matrix
over Rℓ. Hence the parity-check matrices for this code have
the following form 19
HX = [A, bIm], H Z = [¯bIn, A∗]. (17)
We denote by ϕb the homomorphism from Rℓ to the quo-
tient ring R(b) = F2[x]/(b) given by the map u ↦→u mod b.
Since b is an irreducible polynomial over F2, the quotient
ring R(b) is isomorphic to the ﬁnite ﬁeld Fq, where q = 2 deg b.
Thus we can describe this homomorphism as
ϕb(u) = u(β) = u0 + u1β + · · · + uℓ−1βℓ−1 ∈ Fq,
18In [17] these codes were called GHP codes. The parity-check m atrices
of three examples were described in the appendix.
19See also equation (1) in the introduction.
where β ∈ Fq is a root of b and u = ∑ ℓ−1
i=0 uixi ∈ Rℓ.
For example, if b = 1 + x then the ring R(b) = F2[x]/(1 + x)
can be identiﬁed with F2 and ϕb(u) = u(1) = u0 + · · ·+ uℓ−1
is just the number of ones modulo 2 in the binary vector u.
The homomorphism ϕb can be also extended to vectors and
matrices over Rℓ if we apply it to each element. For a vector v
and a matrix M , the result of its action is denoted by v(β)
and M (β), respectively.
Lemma 1. Let b ∈ F2[x] be an irreducible factor of xℓ−1, and
A be a matrix over Rℓ. The dimension of the code LP(A, b)
is equal to
dim LP(A, b) = deg b
(
dim C(A(β)) + dim C(AT(β))
)
,
where β is a root of the polynomial b in the ﬁeld Fq ∼
= R(b).
Proof. Trivially, using (15) we have:
dimF2ker H T
X = ℓm − rkF2 HX;
dimF2ker H ∗
Z = ℓn − rkF2HZ.
Besides, from (17), taking into account that H T
X =
[
AT
bIm
]
, and
H ∗
Z =
[ bIn
A
]
, it follows that:
H T
X u = 0 ⇐ ⇒ ATu = 0, bu = 0;
H ∗
Zu = 0 ⇐ ⇒ Au = 0, bu = 0;
and we have 20 ker H T
X = C(AT) ∩ C m
b , ker H ∗
Z = C(A) ∩ C n
b ,
where Cb = {c ∈ Rℓ | bc = 0 } is the cyclic [ℓ, deg b]-code
deﬁned by the parity polynomial b. Clearly, g = (xℓ − 1)/b is
the generator polynomial for Cb, and the elements of the ﬁnite
ﬁeld R(b) ∼
= Fq are in one-to-one correspondence, given
by the map r ↦→gr, with the elements of Cb. Indeed, since
gb = 0, and hence g(r + bRℓ) = gr, we see that this one-to-
one correspondence is deﬁned correctly. Moreover, for ever y
r ∈ Rℓ it follows that gϕb(r) = g(r + bRℓ) = gr, where we
used that the homomorphism ϕb : Rℓ → F2[x]/(b) can be also
deﬁned as ϕb : r ↦→r + bRℓ. Therefore for every c = gu ∈ C n
b
we have:
c ∈ C(A) ⇐ ⇒gAu = 0 ⇐ ⇒gϕb(Au) = 0 ⇐ ⇒u ∈ C(ϕb(A)),
and the map u ↦→ gu also gives a one-to-one correspon-
dence between C(A) ∩ C n
b and C(ϕb(A)). Since R(b) ∼
= Fq,
q = 2 deg b, we see that dimF2C(A)∩C n
b = deg b·dim C(A(β)).
By exactly the same arguments as before, we also ﬁnd that
dimF2C(AT) ∩ C m
b = deg b · dim C(AT(β)). Finally, using
CSS dimension formula (4) we get:
dim LP(A, b) = ℓ(n + m) − rkF2HX − rkF2HZ
= dim F2ker H T
X + dimF2ker H ∗
Z
= dim F2C(AT) ∩ C m
b + dimF2C(A) ∩ C n
b
= deg b
(
dim C(AT(β)) + dim C(A(β))
)
,
and the lemma is proved.
Remark 2. An alternative proof of Lemma 1 in the case of
odd ℓ can be found in Appendix B.
20Here C(H) = {c | Hc = 0} is considered as a vector space over F2.

## PDF page 10

10
Remark 3. If b = 1 + x then Rb ∼
= F2, β = 1, and we obtain
a slightly simpler dimension formula:
dim LP(A, 1 + x) = dim C(A(1)) + dim C(AT(1)). (18)
We should also emphasize that in this case the cyclic code Cb
is the [ℓ, 1, ℓ] repetition code with g = ∑ ℓ−1
i=0 xi.
IV. E XPANDERS
In this section, we remind some standard deﬁnitions and
facts related to expander graphs and codes. A more detailed
treatment of these subjects can be found in [21]. The main
theoretical result of this section is Proposition 1, which g ives
us a way to construct quasi-cyclic matrices of very larger li ft
sizes with good expansion properties. We use this construct ion
to obtain our main result in Section V. As a byproduct of this
construction, we also get Corollary 1, which shows us how
to get asymptotically good families of classical quasi-cyc lic
LDPC codes with a close to optimal lift size.
A. Expander graphs
Let G be a simple 21 graph with the set of vertices V (G)
and the set of edges E(G). If vertices v, v′ ∈ V (G) are
connected by an edge e ∈ E(G), we call v, v′ adjacent and
denote this fact by v ∼ v′ or by v ∼e v′ when we want to
emphasize the edge e. We also say that a vertex v ∈ V (G) is
incident to an edge e ∈ E(G) if v is one of the two vertices
that e connects. The degree of a vertex v denoted by deg v
is the number of edges connected to it. A graph G is called
w-regular if all its vertices have degree w. The adjacency
matrix for a graph G with V (G) = {v1, . . . , vn} is the
matrix A(G) = ( aij)n×n, where aij is the number of edges
e ∈ E(G) such that vi ∼e vj . Since A(G) is a symmetric
matrix, it has n real-valued eigenvalues λ1 ⩾ · · · ⩾ λn.
Let λ(G) = max( |λ2|, |λn|). We call an n-vertex w-regular
graph G an (n, w, λ)-expander if λ(G) = λ.
For any S ⊆ V (G) we denote by E(S) the set of internal
edges for S, i.e.,
E(S) = {e ∈ E(G) | ∃v, v′ ∈ S : v ∼e v′}.
In the next section, we will need the following very well-
known property of the expander graphs.
Lemma 2. If G is an (n, w, λ)-expander and |S| ⩽ αn, then
|E(S)| ⩽ 1
2
(
α + λ
w
)
w|S|.
Proof. If G is an (n, w, α)-expander and S ⊆ V (G), then by
the expander mixing lemma [21, Lemma 2.5] we have:
⏐
⏐
⏐
⏐|E(S, S)| − w|S||S|
n
⏐
⏐
⏐
⏐ ⩽ λ
√
|S||S|, (19)
where E(S, S) = {(v, v′) ∈ S×S | v ∼ v′}. Let us emphasize
that each edge e ∈ E(G) that connects v, v′ ∈ S gives two
21Simple graphs do not have loops and multiple edges.
different pairs (v, v′) and (v′, v) in the set E(S, S). Hence
|E(S, S)| = 2|E(S)| and we obtain:
2|E(S)| ⩽ w
n |S|2 + λ|S| ⩽
(|S|
n + λ
w
)
w|S|.
Since |S| ⩽ αn, we have |E(S)| ⩽ 1
2
(
α + λ
w
)
w|S|.
B. Expanding binary matrices
We say that a binary m × n matrix H is (α, β)-expanding,
where α, β are some positive real numbers, if for all x ∈ Fn
2
such that |x| ⩽ αn we have |Hx| ⩾ β|x|. It is obvious that if
H is a parity-check matrix of some code C, then d(C) > αn.
Furthermore, we also say that an m × n matrix A over Rℓ
is (α, β)-expanding if the corresponding binary block matrix
H = B(A) is (α, β)-expanding. It is clear that if B(A) is
a parity-check matrix of some QC code C, then d(C) > αℓn.
The following important proposition shows that for a wide
range of parameters there exists a w-limited QC matrix A such
that A and AT are both (α, β)-expanding.
Proposition 1. F or every ε ∈ (0, 1) there exist α, β, γ, w
such that for any natural numbers ℓ > 1 and n ⩾ γ ln ℓ there
exists a w-limited QC matrix A ∈ M m×wn(Rℓ), m ⩽ εwn,
such that the matrices A and AT are both (α, β)-expanding.
In order to prove this proposition, we need to describe some
particular type of Tanner codes [19] used in [2], [20]. Consi der
a simple w-regular graph G with 2n vertices and a linear
[w, w − r] code C0. The idea of the Tanner code T (G, C0)
is to assign its code bits to the wn edges of G and for
each vertex v ∈ V (G) constrain the bits connected to v by
the code C0. More formally, if we index the edges of G by
the set [wn] and for each vertex v ∈ V (G) denote by N (v)
the set of indexes for the edges connected to v; then the Tanner
code is deﬁned as
T (G, C0) = {c ∈ Fwn
2 | ∀v ∈ V (G) : c|N (v) ∈ C 0},
where c|N (v) is obtained from c by deleting all the bits with
indexes outside of N (v).
We suppose that C0 always comes with the some ﬁxed
parity-check matrix 22 H0 ∈ M r×w(F2). The parity-check
matrix H for the code T (G, C0) consists of 2n groups of
rows (Rv)v∈V (G), where each group Rv corresponds to the r
parity-checks of C0 related to the vertex v ∈ V (G), i.e.,
ρ|N (v) is one of the rows from H0 for ρ ∈ R v. Hence
H ∈ M 2rn×wn(F2), and the code T (G, C0) has non-zero
dimension whenever 2r < w . Moreover, it is not hard to see
that if 2r < w then H is a w-limited matrix.
Remark 4. Let us warn the reader that the code T (G, C0)
depends on how we index the edges of G by the set [wn].
Moreover, the parity-check matrix H for the code T (G, C0)
also depends on how we order its rows. Let ˆG be an ℓ-
lift of a smaller base graph G, obtained by ﬁxing in G
an arbitrary edge orientation and assigning to each oriente d
edge e = ( v, v′) some shift s = s(e), which corresponds to
the permutation π ∈ Sℓ (the right cyclic shift by s positions)
22Since C0 is a [w, w − r] code, the rows of H0 are linearly independent.

## PDF page 11

11
from Fig. 1. Denote by h(e) (resp. h′(e)) the column of
H0 ∈ M r×w(F2), corresponding to the connection of the edge
e to the vertex v (resp. v′) in the Tanner code T (G, C0).
The parity-check matrix of this code looks as follows:
H =






0
· · · h′(e) · · ·
0
· · · h(e) · · ·
0






if we arrange its rows to make each group of rows
(Rv)v∈V (G) a contiguous block. Then it is not hard to see
that T ( ˆG, C0) is a QC code of lift size ℓ with the follow-
ing QC parity-check matrix ˆH, deﬁned as a matrix over
the ring Rℓ = F2[x]/(xℓ − 1):
ˆH =






0
· · · xs(e)h′(e) · · ·
0
· · · h(e) · · ·
0






.
The next lemma shows that if G is a sufﬁciently good
expander and C0, C⊥
0 have relatively large minimum distances,
then both H and H T are (α, β)-expanding for any size of G.
Lemma 3. Let H be the parity-check matrix of T (G, C0),
where G is a (2n, w, λ)-expander; C0 is a [w, w − r, d] code.
If λ < δw , d ⩾ δw and d(C⊥
0 ) ⩾ δw, then the binary matrices
H, H T are (α, β)-expanding for all α < δ
w
(
1 − λ
δw
)
and
β = 1
δw
(
δ − αw − λ
w
)
.
Proof. Let us start with a quick remark that the conditions
λ < δw and α < δ
w
(
1 − λ
δw
)
imply that δ
w
(
1 − λ
δw
)
> 0 and
β > 0. We divide the proof into two parts. In the ﬁrst part we
show that the matrix H ∈ M 2rn×wn(F2) is (α, β)-expanding,
while in the second part that the same holds for H T.
Consider a binary vector x ∈ Fwn
2 such that |x| ⩽ αwn.
Let X ⊆ E(G) be the corresponding set of edges, where
the bits from x are equal to 1. We divide the set of vertices
incident to some edges from X into two parts: the set S of
vertices incident to at least δw edges from X; and the set S′ of
vertices incident to less than δw edges from X. One can easily
check23 that |S| ⩽ 2|X|/δw. Hence from |X| ⩽ αwn it also
follows that |S| ⩽ 2αn/δ, and we can estimate the number of
edges from X connected only to S by Lemma 2:
|E(S)| ⩽ 1
2
(α
δ + λ
w
)
w|S| ⩽
( α
δ2 + λ
δw
)
|X|.
Therefore we have:
|X \ E(S)| ⩾ |X| − |E(S)| ⩾
(
1 − α
δ2 − λ
δw
)
|X|.
For each edge from X \ E(S) one of the two vertices it
connects is outside of S; hence this vertex is in S′. Since S′
is connected to less than δw edges from X, we can estimate
the size of S′ as follows:
|S′| > |X \ E(S)|
δw ⩾ 1
δw
(
1 − α
δ2 − λ
δw
)
|X|.
23Each edge from X is connected to at most 2 vertices from S.
Since d(C0) ⩾ δw, for each v ∈ S′ the parity-checks of
the code C0 that correspond to v can not be simultaneously
satisﬁed. Therefore we have
|Hx| ⩾ |S′| > 1
δw
(
1 − α
δ2 − λ
δw
)
|X|
⩾ 1
δw
(
1 − αw
δ − λ
δw
)
|X| = β
δ |x| ⩾ β|x|,
where we used that 1/δ ⩽ w and δ ⩽ 1. Hence we see that
|x| ⩽ αwn implies |Hx| ⩾ β|x|. Thus H is (α, β)-expanding,
and the ﬁrst part of the proof is complete.
Now let us prove that H T is also (α, β)-expanding. Hence
we need to show that for any y ∈ F2rn
2 such that |y| ⩽ 2αrn
we have
⏐
⏐H Ty
⏐
⏐ ⩾ β|y|. As we already mentioned, H consists
of 2n groups of rows (Rv)v∈V (G), where each group Rv
corresponds to the r parity-checks of C0 related to the vertex
v ∈ V (G). Thus H Ty = ∑
v∈S ρv, where ρv is a linear
combination of the rows from the group Rv and S is the set
of vertices v ∈ V (G) such that Rv contains at least one row
from the linear combination H Ty. Since ρv|N (v) is a linear
combination of rows from H0 and d(C⊥
0 ) ⩾ δw, we see 24 that
|ρv| ⩾ δw for all v ∈ S. Let us note that |ρv ∩ ρv′ | = 0
for v ̸= v′ unless the vertices v, v′ are connected by an edge
from E(S), in which case we have |ρv ∩ ρv′ | ⩽ 1. Moreover,⏐
⏐⋂
v∈I ρv
⏐
⏐ = 0 if |I| > 2. Therefore we obtain that
⏐
⏐H Ty
⏐
⏐ =
⏐
⏐
⏐
∑
v∈S
ρv
⏐
⏐
⏐ =
∑
v∈S
|ρv| − 2
∑
v̸=v′
v,v′∈S
|ρv ∩ ρv′|
⩾
∑
v∈S
|ρv| − 2|E(S)| ⩾ δw|S| − 2|E(S)|.
Since |S| ⩽ |y| ⩽ 2αrn, if we apply Lemma 2 to the set S,
we obtain that |E(S)| ⩽ 1
2
(
αr + λ
w
)
w|S| and
⏐
⏐H Ty
⏐
⏐ ⩾ δw|S| − 2|E(S)| ⩾
(
δ − αr − λ
w
)
w|S|
⩾
(
δ − αw − λ
w
)
|y| = δwβ |y| ⩾ β|y|,
where we used that w ⩾ r, w|S| ⩾ r|S| ⩾ |y|, and δw ⩾ 1.
Hence we proved that |y| ⩽ 2αrn implies
⏐
⏐H Ty
⏐
⏐ ⩾ β|y| and
the second part is complete.
Proof of Proposition 1. It is known [35], [36] that a random
w-regular graph G w.h.p. has λ(G) < 2√w − 1 + 1 . Thus
for any sufﬁciently large n ⩾ n0 there exists 25 a w-regular
graph G with 2n vertices such that λ(G) < 2√w − 1 + 1.
At the same time, it is known [22] that for some positive
constants c1, c2 for a random shift ℓ-lift ˆG of G we have
λ( ˆG) ⩽ c1λ(G) with probability at least 1 − ℓ exp(−c2n/w2).
Hence if we choose a sufﬁciently large 26 γ this probability is
positive for all ℓ > 1, n ⩾ γ log2 ℓ; and therefore there exists
a shift ℓ-lift ˆG of G such that
λ( ˆG) < c 1
(
2
√
w − 1 + 1
)
. (20)
24We have ρv ̸= 0 since the rows in H0 are linearly independent.
25We should also mention the reference [37, Theorem 1.3] where an explicit
construction of such graphs is given.
26It is enough to use γ = max(
⌈
w2/c2
⌉
, n0).

## PDF page 12

12
Now consider ε ∈ (0, 1), and let δ be some real number
from the interval (0, 1/2) such that the following inequality
holds:
max(1 − ε/2, ε/2) + ε/4 < 1 − h2(δ), (21)
where h2(x) = −x log2 x − (1 − x) log2(1 − x) is the binary
entropy function. Let C0 be a code deﬁned by a uniformly ran-
dom parity-check matrix H0 ∈ M r×w(F2), where r =
⌊ ε
2 w
⌋
.
Since 1 − r/w → 1 − ε/2 and r/w → ε/2 as w → ∞, taking
into account (21), the Gilbert–V arshamov bound implies tha t
for every sufﬁciently large w w.h.p. we have
d(C0) ⩾ δw, d (C⊥
0 ) ⩾ δw, (22)
and the matrix H0 is full rank. Indeed, let us remind that
the Gilbert–V arshamov bound can be proved [38] using a code
deﬁned either by a random parity-check matrix or a random
generator matrix (i.e., the parity-check matrix of the dual
code), and w.h.p. those matrices are full rank. Therefore by
the union bound we see that w.h.p C0 is a [w, w − r] code
that satisfy (22) as w → ∞ . Hence if we consider a Tanner
code T ( ˆG, C0) with the code C0 that satisfy (22), and choose
a sufﬁciently large w such that we also have
c1
(
2
√
w − 1 + 1
)
< δw,
then using (20) by Lemma 3 we obtain that the matrices
H, H T are (α, β)-expanding for some positive constants α, β;
where H is the parity-check matrix of the code T ( ˆG, C0).
Since ˆG is a shift ℓ-lift for G, according to Remark 4 we can
assume that the matrix H is a QC matrix of lift size ℓ, i.e.,
H = B(A) for some w-limited matrix A ∈ M m×wn(Rℓ),
where n ⩾ γ log2 ℓ, and m = 2
⌊ ε
2 w
⌋
n ⩽ εwn. Now since
the matrices H = B(A), H T = B(A∗) are (α, β)-expanding,
we see that A and A∗ are (α, β)-expanding. Finally, since
the antipode map u ↦→ ¯u is an automorphism of Rℓ, and
|ATu| = |ATu| = |A∗ ¯u|, we also obtain that the matrix AT
is (α, β)-expanding, and the proof is complete.
C. Asymptotically good QC LDPC codes with large lift sizes
Proposition 1 can be used to construct asymptotically good
families of classical QC LDPC codes of very large lift sizes ℓ.
Indeed, if we put n = ⌈γ ln ℓ⌉ and ε = 1 − R in Proposition 1,
then we obtain the code C(A) of rate at least R and distance
at least αN , where N is the code length. Moreover since
log N ∼ log ℓ, and n = Θ(log N ) as N → ∞ , we obtain
the following corollary.
Corollary 1. F or any R < 1 there exists a family of classical
QC LDPC codes of length N and rate at least R with
distance Ω( N ) and lift size Ω( N/ log N ) as N → ∞.
We will see below that the lift size Ω( N/ log N ) from
Corollary 1 is in some sense the best possible for QC LDPC
codes and even for quasi-abelian LDPC codes with linear
minimum distance. More speciﬁcally, we will show using
the results from [23] that: for any family of quasi-abelian
LDPC codes of distance Ω( N ), deﬁned by m × n parity-
check matrices with m < n over commutative group algebras,
the lift size grows at most like O(N/ log N ) as the code
length N → ∞.
Before we prove this we need some deﬁnitions and notations
from [23]. If A is an m × n matrix and I ⊆ [n], then
we denote by AI the m × |I| submatrix of A that contains
only the columns of A with indexes from the set I. If X is
a ﬁnite set and f is a real-valued function on X, we denote by
min∗
x∈X
f (x) the minimum nonzero value of f (x) on X; if there
are no nonzero values then min∗ gives +∞. Let us remind
that the permanent of an integer matrix A = (aij)n×n denoted
by perm A is given by the following formula:
perm A =
∑
π∈Sn
a1,π(1) . . . an,π(n).
Thus perm A is essentially det A if we ignore the signatures
of the permutations π ∈ Sn. If all elements from A are non-
negative integers then we have the following trivial upper
bound:
perm A ⩽
∏
j∈[n]
(a1j + · · · + anj). (23)
If we have a matrix H = (hij)m×n over F2G, where G is
some abelian group of size ℓ; then we can consider its weight
matrix W = ( wij)m×n, where wij = |hij| is the row and
the column weight of each ℓ × ℓ block in H (considered as
a binary block matrix), i ∈ [m], j ∈ [n]. If we ﬁx the weight
matrix W and consider matrices H with ℓ → ∞, it is natural
to expect that d(C(H)) → ∞ . However it turns out [23,
Theorem 7] that when m < n there is an upper bound 27 on
the minimum distance d of the code C(H) that depends only
the weight matrix W , which implies that d doesn’t grow with
the lift size ℓ. The upper bound is as follows:
d ⩽ min∗
S⊆[n]
|S|=m+1
∑
i∈S
perm WS\i. (24)
Remark 5. We should emphasize that if m = n, then this
bound does not work anymore, and the distance d can grow
linearly with the lift size ℓ. For example, if H ∈ M n(Rℓ) is
given by the formula:
H =






1 1 0 . . . 0
0 1 1 . . . 0
. . . . . . . . . . . . . . . . . .
0 0 . . . 1 1
x 0 . . . 0 1






,
then H is a 2-limited matrix, but d = ℓn.
Let us now return to the case when m < n . If the matrix
H is w-limited and 28 w ⩾ 2, then the sum of elements in any
row and column of the weight matrix W is bounded above
by w. Hence the same holds for every its submatrix WS\i
from bound (24). Thus using (23) we obtain from (24) that
d ⩽ (m + 1)wm. Now suppose that the minimum distance d
27In [23] the bound is proved only for QC matrices, but the way it is proved
in [39] can be easily extended to matrices over abelian group algebras.
28The w-limited matrices with w ⩽ 1 deﬁne trivial codes with minimum
distance 1.

## PDF page 13

13
of the code C(H) is Ω( N ) as N → ∞, i.e., d ⩾ αN for some
ﬁxed α > 0. In this case we have:
αN ⩽ (m + 1)wm ⩽ 2mwm ⩽ w2m < w 2n.
Hence αN < w 2n, n = Ω(log N ), and ﬁnally we obtain that
ℓ = N/n is bounded above by O(N/ log N ) as N → ∞.
V. LP CODES WITH ALMOST LINEAR DISTANCE
This section contains the proof of our main result. We con-
sider the special case of QC LP codes, studied in Section III- F,
and prove Proposition 2, which is the main technical tool
to establish the lower bound on the code distance. Finally,
we combine this lower bound with our results on expanding
matrices from Section IV to show the existence of QLDPC
codes with almost linear distance.
Proposition 2. Let A ∈ M m×n(Rℓ) be a w-limited QC
matrix such that A and AT are (α, β)-expanding. Consider
a quantum code Q = LP( A, 1 + x). There exists a constant
γ > 0, that depends only on α, β, and w, such that :
1) d(Q) ⩾ γℓ;
2) If dim C(AT(1)) = 0 then dZ(Q) ⩾ γℓn;
3) If dim C(A(1)) = 0 then dX(Q) ⩾ γℓm.
In order to prove Proposition 2 we need two simple lemmas.
Below by jℓ we denote the all one polynomial ∑ ℓ−1
i=0 xi.
Lemma 4. Consider a quantum code Q = LP( A, 1 + x),
where A ∈ M m×n(Rℓ), and let B = A(1) ∈ Mm×n(F2).
Then every non-degenerate codeword [u, v] ∈ C Z(Q) \ C ⊥
X (Q)
satisﬁes one of the following two conditions :
1) u(1) is a non-zero codeword from C(B) ⊆ Fn
2 ;
2) [u, v] ∼ [0, jℓv′] for some v′ ∈ Fm
2 \ im B; and we have
u = (1 +x)h, v = j ℓv′ + Ah, where h ∈ Rn
ℓ , |hi| ⩽ ℓ/2,
i ∈ [n].
Proof. First, we describe the equivalence classes of codewords
in CZ = CZ(Q). From the deﬁnition of Q it easily follows that
[u, v] ∈ C Z ⇐ ⇒ Au = (1 + x)v;
[u, v] ∈ C ⊥
X ⇐ ⇒ ∃h ∈ Rn
ℓ : u = (1 + x)h, v = Ah; (25)
and [u, v] ∈ C Z is equivalent to [u′, v′] ∈ C Z iff there exists
h ∈ Rn
ℓ such that
u′ − u = (1 + x)h, v ′ − v = Ah. (26)
Hence if [u, v] ∈ C Z(Q) then A(1)u(1) = 0, and we have
u(1) ∈ C (B). Therefore when u(1) ̸= 0 we obtain that [u, v]
satisﬁes the ﬁrst condition of the lemma.
Now let us suppose that u(1) = 0. In this case we see
that u = (1 + x)h for some h ∈ Rn
ℓ . Let us note that we can
always choose h such that |hi| ⩽ ℓ/2, i ∈ [n]. Indeed, if it
does not have this property, then we can replace it with h′
such that (1 + x)h′ = (1 + x)h, deﬁned by
h′
i =
{
hi, if |hi| ⩽ ℓ/2;
hi + jℓ, if |hi| > ℓ/2.
Hence we can assume that we have h with the desired property,
and from (26) it follows that [u, v] ∼ [0, r], where r = v+Ah.
Since [0, r] is a non-degenerate codeword from CZ(Q), we see
that r ̸= 0, and (1 + x)r = 0. Thus we have r = j ℓv′, where
v′ ∈ Fm
2 , and obtain that:
v = r + Ah = j ℓv′ + Ah.
We claim that v′ ̸∈im B. Indeed, otherwise v′ = Bs for
some s ∈ Fn
2 , and it is easy to see that r = Ajℓs in this case.
Hence we have [0, r] ∼ [0, 0], and obtain a contradiction with
the fact that [0, r] is a non-degenerate codeword. This proves
that v′ ̸∈im B, and [u, v] satisﬁes the second condition of
the lemma.
Lemma 5. F or any vector a ∈ Rn
ℓ , where |ai| ⩽ ℓ/2, i ∈ [n],
there exists t such that |(1 + xt)a| ⩾ |a|.
Proof. Since |a| = |xta| for any t, we have
|(1 + xt)a| = |a| + |xta| − 2|a ∩ xta| = 2(|a| − |a ∩ xta|).
It is not hard to see that:
ℓ−1∑
i=0
|a ∩ xia| =
n∑
j=1
ℓ−1∑
i=0
|aj ∩ xiaj| =
n∑
j=1
|aj|2.
Since |ai| ⩽ ℓ/2, i ∈ [n], we obtain
ℓ−1∑
i=0
|a ∩ xia| =
n∑
j=1
|aj|2 ⩽
n∑
j=1
|aj| ℓ
2 = 1
2 |a|ℓ.
Therefore we have:
ℓ−1∑
t=0
|(1+ xt)a| = 2
ℓ−1∑
i=0
|a|− 2
ℓ−1∑
t=0
|a∩xta| ⩾ 2|a|ℓ−|a|ℓ = |a|ℓ,
and there should exists t such that |(1 + xt)a| ⩾ |a|.
Proof of Proposition 2. Since A and AT are (α, β)-expanding
matrices, we see that
d(C(A)) ⩾ αℓn, d (C(AT)) ⩾ αℓm.
Let B = A(1) ∈ M m×n(F2) be the base matrix for the QC
matrix A. It is clear that if c ∈ C (B) then jℓc ∈ C (A). Hence
we obtain that d(C(A)) ⩽ ℓd(C(B)) and by the same argument
d(C(AT)) ⩽ ℓd(C(BT)). Thus we have
d(C(B)) ⩾ αn, d (C(BT)) ⩾ αm.
Consider a non-degenerate codeword c = [u, v] ∈ CZ(Q)\ C⊥
X(Q).
From Lemma 4 it follows that u(1) ∈ C (B), and we have only
two cases:
1) u(1) ̸= 0, and thus |u(1)| ⩾ αn, since u(1) ∈ C (B);
2) u(1) = 0, and thus c ∼ [0, jℓv′] for some v′ ∈ Fm
2 \ {0}.
Let us consider each case separately.
Case 1. In this case we have |u(1)| ⩾ αn. Let us show
that |c| = |u| + |v| ⩾ γ1ℓn, where γ1 = min( α/2, αβ/4).
If |u| > αℓn/ 2 then we are done. Now suppose we have
|u| ⩽ αℓn/2. We claim that |v| ⩾ αβℓn/4. Indeed, consider
u(t) = jtu, s (t) = Au(t),
where jt = ∑ t−1
i=0 xi, t ∈ [ℓ]. Since for any t ∈ [ℓ] we have
(1 + x)jt = 1 + xt, it follows that:
s(t) = Aujt = (1 + x)vjt = (1 + xt)v,

## PDF page 14

14
where we use that Au = (1+ x)v by (25). Besides, we see that⏐
⏐u(1)⏐
⏐ = |u| ⩽ αℓn/2 and
⏐
⏐u(ℓ)⏐
⏐ = |jℓ · u(1)| ⩾ αℓn. Hence
we can consider the minimal t0 such that
⏐
⏐u(t0+1)⏐
⏐ ⩾ αℓn.
Since u(t0+1) = u(t0) + xt0+1u and
⏐
⏐xt0+1u
⏐
⏐ = |u| ⩽ αℓn/2,
we obtain ⏐
⏐
⏐u(t0)
⏐
⏐
⏐ ⩾
⏐
⏐
⏐u(t0+1)
⏐
⏐
⏐− |u| ⩾ αℓn/2.
Finally, using that s(t0) = (1 + xt0)v, αℓn/2 ⩽
⏐
⏐u(t0)⏐
⏐ < αℓn,
and the fact that A is (α, β)-expanding, we have:
|v| ⩾ 1
2
⏐
⏐
⏐s(t0)
⏐
⏐
⏐ = 1
2
⏐
⏐
⏐Au(t0)
⏐
⏐
⏐ ⩾ β
2
⏐
⏐
⏐u(t0)
⏐
⏐
⏐ ⩾ αβ
4 ℓn,
and the claim is proved. Therefore in all cases we see that
|c| ⩾ γ1ℓn.
Case 2. In this case u = (1 + x)h, v = j ℓv′ + Ah; where
v′ ∈ Fm
2 \ {0}, h ∈ Rn
ℓ , and |hi| ⩽ ℓ/2, i ∈ [n]. We show
that either |u| ⩾ γ2ℓ or |v| ⩾ γ2ℓ, where γ2 = α
4w min(β, 1).
Assume the converse, then |u| < γ 2ℓ and |v| < γ 2ℓ. Since
Ah = v + jℓv′, for every t ∈ [ℓ] we get:
|(1 + xt)Ah| = |v + jℓv′ + xtv + xtjℓv′| = |v + xtv| < 2γ2ℓ,
where we use that xtjℓ = j ℓ. Further, since A is w-limited,
|jℓv′| ⩾ ℓ, |v| ⩽ γ2ℓ ⩽ ℓ/2, and α < 1, we obtain:
|h| ⩾ |Ah|
w = |v + jℓv′|
w ⩾ |jℓv′| − |v|
w ⩾ ℓ
2w ⩾ αℓ
2w .
Moreover, if we consider wt = |(1 + xt)h|, then by Lemma 5
there exists t such that wt ⩾ αℓ
2w . Let us denote by t0
the smallest such t. Since 1 + xt0 = (1 + x) + x(1 + xt0−1),
|(1 + x)h| = |u| ⩽ γ2ℓ, and
⏐
⏐x(1 + xt0−1)h
⏐
⏐ = wt0−1 < αℓ
2w ,
we see that
⏐
⏐(1 + xt0 )h
⏐
⏐ ⩽ |(1 + x)h| +
⏐
⏐x(1 + xt0−1)h
⏐
⏐
<
(
γ2 + α
2w
)
ℓ ⩽
( α
4w + α
2w
)
ℓ = 3
4w αℓ < αℓn.
Therefore, if we recall that the matrix A is (α, β)-expending,
then from |(1 + xt0 )h| < αℓn it follows that
⏐
⏐A(1 + xt0 )h
⏐
⏐ ⩾ βwt0 ⩾ β αℓ
2w ⩾ 2γ2ℓ.
However, we showed earlier that |A(1 + xt)h| < 2γ2ℓ for
every t ∈ [ℓ]. Hence we have a contradiction and obtain that
in the second case |c| = |u| + |v| ⩾ γ2ℓ.
Now, in order to ﬁnish the proof of Proposition 2, we
need to set γ = min( γ1, γ2) and notice that dZ(Q) ⩾ γℓ
in the both considered cases. Besides, if dim C(AT(1)) = 0
then im A(1) = C⊥(AT(1)) = Fm
2 , and by Lemma (4) we do
not have case 2. Thus in this situation we obtain a better lowe r
bound dZ(Q) ⩾ γℓn. At the same time, from (16) it follows
that dX(Q) = dZ(LP(AT, 1 + x)). Therefore since AT is also
(α, β)-expanding, we see, using exactly the same arguments
as before, that dX(Q) ⩾ γℓ, and dX(Q) ⩾ γℓm in the case
when dim C(A(1)) = 0 . This completes the proof.
Now we are ready to prove our main result.
Proof of Theorem 1. By Proposition 1 for every ℓ > 1 there
exists a w-limited matrix A ∈ M m×wn(Rℓ), n = ⌈γ ln ℓ⌉,
m ⩽ 1
2 wn, such that A and AT are (α, β)-expanding,
where α, β, γ, and w are some ﬁxed constants. Consider
a quantum code Q = LP( A, 1 + x). It has the code length
N = ℓ(wn + m), and since log N ∼ log ℓ, and n = Θ(log N )
as N → ∞ , using (18) the dimension of Q is equal to
K = Θ( n) = Θ(log N ). Moreover, Proposition 2 implies that
d(Q) ⩾ γℓ.
Let us show the upper bound d(Q) ⩽ ℓ = Ω( N/ log N ).
Indeed, from (16) it follows that dX(Q) = dZ(Q′), where
Q′ = LP( AT, b). If we apply Lemma 4 to the code Q′,
then we obtain that [0, jℓv′] is a non-degenerate codeword
from CZ(Q′) if v′ ̸∈im BT, where B = A(1) ∈ Mm×wn(F2).
Since m < wn , the column space of BT does not contain some
standard basis vector ei = (0, . . . ,1, . . . ,0) ∈ Fwn
2 . Therefore
c = [ 0, jℓei] is a non-degenerate codeword from CZ(Q′), and
dX(Q) = dZ(Q′) ⩽ |c| = ℓ. Hence we ﬁnally obtain that
d(Q) = Θ( ℓ) = Θ( N/ log N ), and the proof is complete.
VI. C ONCLUSION
We have demonstrated that the family of lifted product
codes from our previous work [17] contains QLDPC codes of
dimension Θ(log N ) and distance Θ( N/ log N ) as the code
length N → ∞ . Moreover, we have shown a way how
to increase their dimension and obtained QLDPC codes
of dimension Ω( N α log N ) and distance Ω( N 1−α/2/ log N ),
where 0 ⩽ α < 1. To the best of our knowledge, the pa-
rameters of the obtained codes are better than for previous
QLDPC constructions. Let us note that the obtained distance
Θ( N/ log N ) is also asymptotically larger than the currently
best-known distance N 1−ε for sparse subsystem codes [40],
where ε = O(1/√
log N ).
We should emphasize that Proposition 2 allows us, in
principle, to obtain (with some extra work) QLDPC codes,
where dZ = Θ( N ) and dX = Θ( N/ log N ). Though we think
that we know how to achieve this, we do not present a formal
proof here in order to make our construction of the Tanner
code T (G, C0) as simple as possible.
As a simple byproduct of the proof of Theorem 1 we have
also constructed a family of classical QC LDPC codes of any
design rate and distance Θ( N ) with, in some sense, optimal
circulant size Ω( N/ log N ).
Besides, we have further generalized our construction
from [17], and obtained a large class of CSS codes called
lifted product codes. The proposed codes are quite general a nd
contain many of the best-known quantum LDPC codes such
as the hypergraph product codes [9], the bicycle codes [33],
the Haah’s cubic codes [26]. Some of the codes from this
class (e.g., the codes LP(A, A∗) from Example 3) have
the dimension K = Θ( N ) as N → ∞ , but the only upper
bound on the minimum distance we have now is O(N/ log N ).
However, we should warn the reader that the methods we used
in the proof of Proposition 2 cannot be directly applied here .
Therefore it is an interesting open problem whether some of
these codes have distance that matches this upper bound. It i s
also interesting weather this distance can be made linear us ing
other matrix rings R ⊆ M ℓ×ℓ(F2), e.g. non-commutative
ones.
We have also extended the lifted product operation from
codes to chain complexes. It naturally generalizes the stan dard

## PDF page 15

15
tensor product of two complexes, widely used in the context
of quantum codes. Though we do not discuss it here, this
operation can be used to obtain quantum codes out of quantum
and classical codes. For example, any quasi-cyclic (classi cal
or quantum) code C of lift size ℓ can be combined with some
other quasi-cyclic code (classical or quantum) C′ of the same
lift size in order to produce a quantum code from the lifted
product C ⊗ ℓ C′. We think that obtaining such codes, and
estimating their parameters can also be an interesting line of
future research.
ACKNOWLEDGMENT
This work was supported by the Ministry of Science and
Higher Education of the Russian Federation (Grant № 075-
15-2020-801).
REFERENCES
[1] R. G. Gallager, Low-Density Parity-Check Codes . M.I.T. Press,
Cambridge, MA, 1963.
[2] M. Sipser and D. A. Spielman, “Expander codes,” IEEE Transactions
on Information Theory , vol. 42, no. 6, pp. 1710–1722, 1996.
[3] A. Barg and G. Z´ emor, “Error exponents of expander codes ,” IEEE
Transactions on Information Theory , vol. 48, no. 6, pp. 1725–1729,
2002.
[4] Z. Babar, P . Botsinis, D. Alanis, S. X. Ng, and L. Hanzo, “F ifteen years
of quantum LDPC coding and improved decoding strategies,” IEEE
Access, vol. 3, pp. 2492–2519, 2015.
[5] D. Gottesman, “Fault-tolerant quantum computation wit h constant over-
head,” Quantum Info. Comput. , vol. 14, no. 15–16, pp. 1338–1372, Nov.
2014.
[6] O. Fawzi, A. Grospellier, and A. Leverrier, “Constant ov erhead quantum
fault-tolerance with quantum expander codes,” in 2018 IEEE 59th
Annual Symposium on F oundations of Computer Science (FOCS) , 2018,
pp. 743–754.
[7] E. Dennis, A. Kitaev, A. Landahl, and J. Preskill, “Topol ogical quantum
memory,” Journal of Mathematical Physics , vol. 43, no. 9, pp. 4452–
4505, 2002. [Online]. Available: https://doi.org/10.106 3/1.1499754
[8] M. H. Freedman, D. A. Meyer, and F. Luo, “ Z2-systolic freedom
and quantum codes,” in Mathematics of quantum computation , R. K.
Brylinski and G. Chen, Eds. New Y ork: Chapman & Hall/CRC, 200 2,
ch. 12, pp. 287–320.
[9] J. Tillich and G. Z´ emor, “Quantum LDPC codes with positi ve rate and
minimum distance proportional to n1/2,” in 2009 IEEE International
Symposium on Information Theory , June 2009, pp. 799–803.
[10] S. Evra, T. Kaufman, and G. Z´ emor, “Decodable quantum L DPC
codes beyond the square root distance barrier using high dim ensional
expanders,” in 2020 IEEE 61st Annual Symposium on F oundations of
Computer Science (FOCS) , Nov. 2020, pp. 218–227.
[11] T. Kaufman and R. J. Tessler, “New cosystolic expanders from tensors
imply explicit Quantum LDPC codes with Ω( √
n logk n) distance,” in
Proceedings of the 53rd Annual ACM SIGACT Symposium on Theor y
of Computing . New Y ork, NY , USA: Association for Computing
Machinery, Jun. 2021, pp. 1317–1329.
[12] M. B. Hastings, J. Haah, and R. O’Donnell, “Fiber bundle codes:
Breaking the N 1/2 polylog(N ) barrier for Quantum LDPC codes,” in
Proceedings of the 53rd Annual ACM SIGACT Symposium on Theor y
of Computing . New Y ork, NY , USA: Association for Computing
Machinery, Jun. 2021, pp. 1276–1288.
[13] A. R. Calderbank and P . W. Shor, “Good quantum error-cor recting
codes exist,” Phys. Rev. A , vol. 54, pp. 1098–1105, Aug 1996. [Online].
Available: https://link.aps.org/doi/10.1103/PhysRevA.54.1098
[14] A. M. Steane, “Error correcting codes in quantum theory ,” Phys.
Rev. Lett. , vol. 77, pp. 793–797, Jul 1996. [Online]. Available:
https://link.aps.org/doi/10.1103/PhysRevLett.77.793
[15] M. B. Hastings, “Weight reduction for quantum codes,” Quantum Info.
Comput., vol. 17, no. 15–16, p. 1307–1334, Dec. 2017.
[16] W. Zeng and L. P . Pryadko, “Higher-dimensional quantum
hypergraph-product codes with ﬁnite rates,” Phys. Rev.
Lett., vol. 122, p. 230501, Jun 2019. [Online]. Available:
https://link.aps.org/doi/10.1103/PhysRevLett.122.230501
[17] P . Panteleev and G. Kalachev, “Degenerate quantum LDPC codes with
good ﬁnite length performance,” arXiv:1904.02703 [quant-ph] , Apr.
2019, paper was presented at the ﬁfth international confere nce on
quantum error correction (QEC’19), Senate House, London, U K.
[18] S. Bravyi, M. Suchara, and A. V argo, “Efﬁcient algorith ms
for maximum likelihood decoding in the surface code,” Phys.
Rev. A , vol. 90, p. 032326, Sep 2014. [Online]. Available:
https://link.aps.org/doi/10.1103/PhysRevA.90.032326
[19] R. M. Tanner, “A recursive approach to low complexity co des,” Informa-
tion Theory, IEEE Transactions on , vol. 27, no. 5, pp. 533–547, 1981.
[20] G. Z´ emor, “On expander codes,” IEEE Transactions on Information
Theory, vol. 47, no. 2, pp. 835–837, 2001.
[21] S. Hoory, N. Linial, and A. Wigderson, “Expander graphs and their
applications,” Bull. Amer . Math. Soc. , vol. 43, no. 04, pp. 439–562,
Aug. 2006.
[22] N. Agarwal, K. Chandrasekaran, A. Kolla, and V . Madan, “ On
the expansion of group-based lifts,” SIAM Journal on Discrete
Mathematics, vol. 33, no. 3, pp. 1338–1373, 2019. [Online]. Available:
https://doi.org/10.1137/17M1141047
[23] R. Smarandache and P . V ontobel, “Quasi-cyclic LDPC cod es: Inﬂuence
of proto- and tanner-graph structure on minimum Hamming dis tance
upper bounds,” IEEE Transactions on Information Theory , vol. 58, no. 2,
pp. 585–607, 2012.
[24] J. Tillich and G. Z´ emor, “Quantum LDPC codes with posit ive rate and
minimum distance proportional to the square root of the bloc klength,”
IEEE Transactions on Information Theory , vol. 60, no. 2, pp. 1193–
1202, Feb 2014.
[25] M. Hagiwara and H. Imai, “Quantum quasi-cyclic ldpc cod es,” in 2007
IEEE International Symposium on Information Theory , June 2007, pp.
806–810.
[26] J. Haah, “Local stabilizer codes in three dimensions wi thout string
logical operators,” Phys. Rev. A , vol. 83, p. 042330, Apr 2011. [Online].
Available: https://link.aps.org/doi/10.1103/PhysRevA.83.042330
[27] A. A. Kovalev and L. P . Pryadko, “Quantum kronecker sum-
product low-density parity-check codes with ﬁnite rate,” Phys.
Rev. A , vol. 88, p. 012311, Jul 2013. [Online]. Available:
https://link.aps.org/doi/10.1103/PhysRevA.88.012311
[28] J. Thorpe, “Low-density parity-check (LDPC) codes con structed from
protographs,” IPN progress report , vol. 42, no. 154, pp. 42–154, 2003.
[29] S. Bravyi and M. B. Hastings, “Homological product code s,” in
Proceedings of the F orty-sixth Annual ACM Symposium on Theo ry of
Computing, ser. STOC ’14. New Y ork, NY , USA: ACM, 2014, pp. 273–
282. [Online]. Available: http://doi.acm.org/10.1145/2 591796.2591870
[30] E. T. Campbell, “A theory of single-shot error correcti on for adversarial
noise,” Quantum Science and Technology, vol. 4, no. 2, p. 025006, 2019.
[31] D. Dummit and R. Foote, Abstract Algebra, 3rd ed. Wiley, 2003.
[32] Y . Drozd and V . Kirichenko, Finite Dimensional Alge-
bras. Springer Berlin Heidelberg, 1994. [Online]. Available:
https://www.springer.com/gp/book/9783642762468
[33] D. J. C. MacKay, G. Mitchison, and P . L. McFadden, “Spars e-graph
codes for quantum error correction,” IEEE Transactions on Information
Theory, vol. 50, no. 10, pp. 2315–2330, Oct 2004.
[34] R. M. Tanner, D. Sridhara, and T. Fuja, “A class of group- structured
LDPC codes,” in Proc. ISTA, 2001, pp. 365–370.
[35] J. Friedman, “A proof of Alon’s second eigenvalue conje cture,” in
Proceedings of the Thirty-Fifth Annual ACM Symposium on The ory
of Computing , ser. STOC ’03. New Y ork, NY , USA: Association
for Computing Machinery, 2003, pp. 720–724. [Online]. Avai lable:
https://doi.org/10.1145/780542.780646
[36] D. Puder, “Expansion of random graphs: new proofs, new r esults,”
Inventiones mathematicae, vol. 201, pp. 845–908, 2015.
[37] N. Alon, “Explicit expanders of every degree and size,” Combinatorica,
Feb. 2021.
[38] A. Barg and G. D. Forney, “Random codes: minimum distanc es and
error exponents,” IEEE Transactions on Information Theory , vol. 48,
no. 9, pp. 2568–2573, 2002.
[39] B. K. Butler and P . H. Siegel, “Bounds on the minimum dist ance of
punctured quasi-cyclic LDPC codes,” IEEE Transactions on Information
Theory, vol. 59, no. 7, pp. 4584–4597, 2013.
[40] D. Bacon, S. T. Flammia, A. W. Harrow, and J. Shi, “Sparse quan-
tum codes from quantum circuits,” IEEE Transactions on Information
Theory, vol. 63, no. 4, pp. 2464–2479, 2017.
[41] S. Ling, H. Niederreiter, and P . Sol´ e, “On the algebrai c structure of
quasi-cyclic codes IV: Repeated roots,” Designs, Codes and Cryptogra-
phy, vol. 38, pp. 337–361, 2006.

## PDF page 16

16
Pavel Panteleev received the M.S. degree in computer science from the
Moscow State Aviation Technological University in 2001 and the Ph.D. (Can-
didate of Science) degree in mathematics from the Moscow Sta te University
in 2006. Since 2003, he has been a researcher at the Faculty of Mechanics
and Mathematics of the Moscow State University. From 2004 to 2014 he had
also been working in LSI Corporation, currently a part of Bro adcom Inc.,
on hardware architectures for data storage and transmissio n systems. Starting
from 2014, he has been engaged as a consultant in several coop eration projects
with Huawei Technologies, focusing on error-correcting co des and, more
recently, on quantum computing. His research interests inc lude applications
of abstract algebra and combinatorics to computer science a nd information
theory.
Gleb Kalachev received the M.S. degree in 2013 from the Moscow State
University, where he also received the Ph.D. (Candidate of S cience) degree in
2018, both in mathematics. Since 2014, he has been a research er at the Faculty
of Mechanics and Mathematics of the Moscow State University . Starting from
2014, he also participated as a consultant in several cooper ation projects
with Huawei Technologies related to data storage, error-co rrecting codes,
and quantum computing. His research interests include comp lexity theory,
information theory, and cellular automata.
APPENDIX A
RING OF CIRCULANTS
An ℓ × ℓ circulant matrix A over F2 takes the form
A =




a0 al−1 . . . a 1
a1 a0 . . . a 2
. . . . . . . . . . . . . . . . . . . .
aℓ−1 aℓ−2 . . . a 0



 ,
where a0, . . . , aℓ−1 ∈ F2. It is readily seen that the matrix A
can be represented in the form
A = a0I + a1P + . . . aℓ−1P ℓ−1,
where I is the ℓ × ℓ identity matrix and
P =






0 0 . . . 1
1 0 . . . 0
0 1 . . . 0
. . . . . . . . . . . . .
0 0 . . . 0






is the ℓ × ℓ permutation matrix representing the right cyclic
shift by one position. Since P ℓ = I, we see that the ring
of all ℓ × ℓ circulant matrices over F2 is isomorphic to the
ring Rℓ = F2[x]/(xℓ − 1) of polynomials over F2 modulo
the polynomial xℓ − 1. Hence the circulant matrix A can be
uniquely represented by the polynomial:
a = a0 + a1x + · · · + aℓ−1xℓ−1.
The algebraic structure of the ring Rℓ is well studied in
the coding literature (see, e.g., [41]). We brieﬂy review it here.
First, let us consider the special case when ℓ is odd. In this
case the polynomial xℓ −1 factors into a product of irreducible
polynomials over F2
xℓ − 1 = f1(x) · · · fs(x). (27)
This is true, since
gcd
(
(xℓ − 1)′, xℓ − 1
)
= gcd
(
ℓxℓ−1, xℓ − 1
)
= 1,
and the polynomial xℓ − 1 is square-free.
In the general case we have ℓ = 2 eℓ′, where ℓ′ is odd. Hence
it follows that
xℓ − 1 = x2eℓ′
− 1 = ( xℓ′
− 1)2e
.
Moreover, since ℓ′ is odd, we can apply the factorization (27)
to the polynomial xℓ′
− 1 and obtain that
xℓ − 1 =
(
f1(x)
) 2e
· · ·
(
fs(x)
) 2e
. (28)
Since the polynomials (f1(x)
) 2e
, . . . ,(fs(x)
) 2e
are pair-
wise coprime, from the Chinese remainder theorem it follows
that the ring Rℓ is isomorphic to the direct product
R(1) × · · · × R(s) (29)
of the rings R(i) = F2[x]/
(
fi(x)
) 2e
, i ∈ [s].
When ℓ is odd we have e = 0 and the rings R(1), . . . , R(s)
are in fact ﬁelds, since the polynomials f1(x), . . . , fs(x) are
irreducible over F2.

## PDF page 17

17
APPENDIX B
DECOMPOSITION OF QUASI -ABELIAN LP CODES
Consider a commutative group algebra R = F2G, where
|G| = ℓ. Suppose that R is a direct product of rings:
R ∼
= R(1) × · · · × R(s) (30)
with the corresponding morphisms ϕi : R → R(i), i ∈ [s].
Let us note that since R is a ﬁnite dimensional algebra
over F2, the same holds for the rings R(1), . . . , R(s), and
we have ∑
i∈[s] dim R(i) = ℓ. This direct product structure
implies that any matrix M over R can be uniquely represented
by the collection of matrices
(
ϕi(M )
)
i∈[s], where ϕi(M ) is
the matrix over R(i) obtained by the action of ϕi on each
element of M .
Using this idea, we can represent any code LP(A, B)
constructed from matrices A and B over R by the collection of
s codes
(
LP(Ai, Bi)
)
i∈[s], where Ai = ϕi(A), Bi = ϕi(B)
are matrices over the ring R(i). Since the direct product
gives us a one-to-one correspondence between the elements
a ∈ R and the tuples
(
ϕi(a)
)
i∈[s], we also get a one-to-
one correspondence between the codewords c from LP(A, B)
and the tuples of codewords
(
ϕi(c)
)
i∈[s] from the collection(
LP(Ai, Bi)
)
i∈[s]. Moreover, it is not hard to check that
this one-to-one correspondence also respects the degenera cy
of the codewords, i.e., c is degenerate iff all the codewords(
ϕi(c)
)
i∈[s] are degenerate. This yields that:
dim LP(A, B) =
∑
i∈[s]
dim LP(Ai, Bi).
In addition, if in decomposition (30) every ring R(i) is
a ﬁnite ﬁeld Fqi, then every LP(Ai, Bi) can be uniquely
represented (see Example 2) by a non-binary HP code deﬁned
by the matrices Ai and Bi over Fqi, where qi = 2 ri, i ∈ [s].
Hence using (14) we obtain the following formula:
dim LP(A, B) =
∑
i∈[s]
ri dim HP(Ai, Bi). (31)
At the same time, dim HP(Ai, Bi) for each i ∈ [s] can be
found by formula (10).
If the lift size ℓ = |G| is odd, then from Maschke’s theorem
it follows that the algebra F2G is semisimple and hence is
isomorphic [32, Theorem 2.4.1] to the direct product of ﬁnit e
ﬁelds Fq1 × · · · × Fqs. Hence, for matrices A and B over F2G,
the dimension of the quasi-abelian code LP(A, B) is given by
formula (31).
Let us also note that if ℓ is odd, then Lemma 1 is just
a special case of formula (31). Indeed, it is well known
(see Appendix A) that if ℓ is odd, then the ring Rℓ is
isomorphic to the direct product of ﬁnite ﬁelds:
R ∼
= Fq1 × · · · × Fqs,
where each ﬁeld Fqi , qi = 2 ri, corresponds to an irreducible
factor fi ∈ F2[x], deg fi = ri, of the polynomial xℓ − 1. We
have the following homomorphisms ϕi : Rℓ → Fqi deﬁned by
ϕi : u ↦→u(βi), where βi is a root of fi in the ﬁeld Fqi,
i ∈ [s]. Without loss of generality we can assume that f1 = b,
and β1 = β. Hence by (31) we have 29:
dim LP(A, b) =
∑
i∈[s]
ri dim HP(A(βi), b(βi)).
Since b(βi) ̸= 0 whenever i ̸= 1 , it is easy to see that
dim HP(A(βi), b(βi)) = 0 for i ̸= 1 . At the same time, it is
clear that:
dim HP(A(β), 0) = n + m − rk[A(β), 0] − rk[0, AT(β)]
= dim C(A(β)) + dim C(AT(β)),
where n, m are the number of columns and rows in A,
respectively. Thus
LP(A, b) = r1
(
dim C(A(β)) + dim C(AT(β))
)
,
where r1 = deg b, and we obtain the formula from Lemma 1.
APPENDIX C
LIST OF SYMBOLS AND ABBREVIATIONS
[n] set {1, 2, . . . , n}
|u| Hamming weight of the vector u
x ∩ y intersection of binary vectors
Fq ﬁnite ﬁeld with q elements
Sn set of all permutations on [n]
Cn cyclic group of order n
ℓ lift size or circulant size
Rℓ quotient ring F2[x]/(xℓ − 1) ∼
= F2Cℓ
jt all one polynomial ∑ t−1
i=0 xi
FG group algebra over F for the group G
¯a antipode ¯a = ∑
g∈G αgg−1 for a ∈ FG
C⊥ dual code for C
C(H) code with the parity-check matrix H
ker A kernel of the linear map v ↦→Av
im A image of the linear map v ↦→Av
Mm×n(R) set of all m × n matrices over R
Mn(R) set of all n × n matrices over R
B(A) block matrix for A ∈ Mm×n(R)
AT standard transpose for A
A∗ conjugate transpose for A
Q∗ quantum code Q with swapped CZ, CX
Q ∼ Q ′ permutation equivalent codes
HP(A, B) hypergraph product code
LP(A, B) lifted product code
QLDPC quantum low-density parity-check
LDPC classical low-density parity-check
QC quasi-cyclic
w.h.p with high probability
29Let us note that in this sum we consider non-binary HP codes.
