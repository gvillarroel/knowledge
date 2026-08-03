---
type: Research Paper
title: Asymptotically Good Quantum and Locally Testable Classical LDPC Codes
description: '- Pinned arXiv record: [2111.03654v2](https://arxiv.org/abs/2111.03654v2)'
resource: https://example.org/qec-arxiv-papers/resource/paper-2111-03654v2/sources%2Fmarkdown%2F2111.03654v2
tags:
- paper-2111-03654v2
- markdown
- rl
concept_id: concepts/paper-2111-03654v2/sources-markdown-2111.03654v2-c51c6c2268
concept_path: concepts/paper-2111-03654v2/sources-markdown-2111.03654v2-c51c6c2268.md
subject_iri: https://example.org/qec-arxiv-papers/resource/paper-2111-03654v2/sources%2Fmarkdown%2F2111.03654v2
ontology_class_iri: https://example.org/ontology/qec-arxiv-papers#Paper
ontology_version_iri: https://example.org/ontology/qec-arxiv-papers/1.0.0
source_id: paper-2111-03654v2
source_kind: markdown
source_path: sources/markdown/2111.03654v2.md
source_content_sha256: 02543837a586bb8fd4723f8edc530e441930a1ad9bfa56969e51256dd916b675
record_sha256: 7be88b61f53bd20f6cbb8ab8a2b332ac454f3352f1c741b9a22b406335a0a698
source_refs:
- https://example.org/qec-arxiv-papers/provenance/record/paper-2111-03654v2/e2fbe0faeb59fdfef3c36b9f
record_id: sources/markdown/2111.03654v2
---

# Asymptotically Good Quantum and Locally Testable Classical LDPC Codes

## Source citation

- Pinned arXiv record: [2111.03654v2](https://arxiv.org/abs/2111.03654v2)
- Authors: Panteleev, Pavel; Kalachev, Gleb
- PDF: [https://arxiv.org/pdf/2111.03654v2](https://arxiv.org/pdf/2111.03654v2)
- PDF SHA-256: `36b8a9a979cdd0685a86ce6f19efa4109ccb7cb3f738a170f75f5c7aa691bfb1`
- Extracted pages: 51

The following text was extracted page by page from the pinned PDF. Page headings are stable evidence locators.

## PDF page 1

arXiv:2111.03654v2  [cs.IT]  21 Jan 2022
Asymptotically Good Quantum and Locally Testable Classica l
LDPC Codes
Pavel Panteleev and Gleb Kalachev ∗
January 24, 2022
Abstract
We study classical and quantum LDPC codes of constant rate obta ined by the lifted product
construction over non-abelian groups. We show that the obtained families of quantum LDPC
codes are asymptotically good, which proves the qLDPC conjectur e. Moreover, we show that the
produced classical LDPC codes are also asymptotically good and loca lly testable with constant
query and soundness parameters, which proves a well-known conj ecture in the ﬁeld of locally
testable codes.
Introduction
Classical low-density parity-check (LDPC) codes [
1], as well as their quantum counterparts [ 2],
have many important applications in theory and practice. Th ese codes are represented by sparse
parity-check matrices, where the term sparse usually means that the corresponding Tanner graphs
are of bounded degree. Besides numerous applications in dat a storage and transmission systems,
such codes are often used to construct classical and quantum locally testable codes [ 3–5], where
the sparseness of a code ensures the constant-query propert y, also known as the constant locality.
Informally speaking, a classical locally testable code (LT C) is a code that comes with an eﬃcient
non-deterministic procedure that allows to test with high p robability whether a given sequence is
close to some codeword by looking at a very small, usually con stant, number of randomly chosen
bits from this sequence. There are several ways how one can fo rmally deﬁne LTCs [ 6]. In this paper,
we adopt a very simple combinatorial deﬁnition (see [ 7, Deﬁnition 11]) that implies a rather strong
form of local testability. According to this deﬁnition, a li near code C⊆ Fn
q is called ( ω, s)-locally
testable if it has a parity-check matrix H∈ Fm×n
q with rows of weight at most ω such that for any
vector x∈ Fn
q we have
1
m|Hx| ⩾ s
n d(x,C),
where d(x,C) := min c∈C d(x, c), and we denote by d(·,·) and |·| the Hamming distance and the
Hamming weigh. The parameters ω and s are positive real numbers called the locality and sound-
ness, respectively. As we already mentioned above, this deﬁniti on implies a strong form of local
testability. Indeed, if our test procedure picks uniformly at random a row from H and ﬁnds the
∗ Pavel Panteleev and Gleb Kalachev are with the Faculty of Mec hanics and Mathematics, Moscow State University,
Moscow, Russia.
1

## PDF page 2

corresponding syndrome component, then the probability of rejection rej H(x) = 1
m|Hx| grows at
least linearly with the normalized minimum distance δ(x,C) := 1
n d(x,C) from the tested vector
x∈ Fn
q to the code C. In fact, for any family of LDPC codes with m = Θ( n) where the the weights
of rows and columns in H are bounded from above by ω (such codes are called ω-limited), it follows
that 1
m|Hx| can not grow more than linearly with δ(x,C) since for every parity-check matrix H we
get|Hx| ⩽ ω· d(x,C).
In the case of quantum locally testable codes (qLTCs) introd uced in [ 4], one can give a similar to
the above deﬁnition if a sparse parity-check matrix H is replaced by a local Hamiltonian H deﬁning
the quantum code. However, for a quantum CSS code Q (see [8,9]), obtained from a pair of classical
codesCX andCZ, it is possible [ 4, 7] to infer the local testability of Q from the local testability
ofCX andCZ . Let us recall that a quantum CSS code Q of dimension k is deﬁned by a pair of
classical linear codes CX,CZ⊆ Fn
q such thatC⊥
Z⊆C X , and k = dimCX/C⊥
Z . Its minimum distance
d is deﬁned as min( dX , dZ ), where dX and dZ are the minimal Hamming weights of the vectors
fromCX\C ⊥
Z andCZ\C ⊥
X, respectively. In this case, we often say that Q is an /llbracketn, k, d/rrbracketq code.
The codes CX,CZ are usually represented respectively by parity-check matr ices HX, HZ, and the
conditionC⊥
Z ⊆C X is equivalent to HXH ∗
Z = 0, where H ∗
Z is the transpose of HZ. It was shown
in [
7, Lemma 13] that if a CSS code Q is deﬁned by two classical ( ω, s)-locally testable codes
with parity-check matrices HX, HZ, then the quantum code Q is ( ω, s′)-locally testable, where
s′ := s min
(
mX
mX +mZ
, mZ
mX +mZ
)
, and mX (resp. mZ) is the number of rows in the matrix HX (resp.
HZ).
Classical and quantum LTCs have many interesting applicati ons in theoretical computer science
since they are intimately related to a number of important pr oblems in complexity theory [ 4, 10].
A major open problem is whether there are such codes of constant locality ω, constant rate, and
constant normalized minimum distance, sometimes also known as the c3-conjecture (in the context
of classical codes [ 11]) and qLTC conjecture (in the quantum case [ 4]). In this respect, the situation
for classical LTCs is much better than for their quantum coun terparts since classical LTCs of almost
constant rate have been known for a long time [ 12]. However, in the quantum case, even if the
property of local testability is not required, it is still a w idely open problem, known as the qLDPC
conjecture [13], to obtain an asymptotically good family of quantum LDPC (qLDPC) codes 1, i.e.,
with the constant rate and normalized minimum distance. Up u ntil very recently [ 16–19], the best
provable lower bounds on the distances of qLDPC codes were, u p to polylogarithmic factors, at
most of the order √n as the number of qubits n→∞ [20–25]. At the same time, asymptotically
good families of classical LDPC codes have been known since t heir introduction by Robert Gallager
in the 1960s [ 1].
In the current work, we show the existence of classical LTCs o f constant rate, constant locality,
and constant normalized minimum distance. In particular, w e prove the following theorem, which
gives a positive answer to the c3-conjecture. Let us recall that a classical linear code C⊆ Fn
q has
the parameters [ n, k, d]q if k = dimC and d = min c∈C\{0}|c|.
Theorem 1. For every number R∈ (0, 1/2) and ﬁnite ﬁeld Fq it is possible to ﬁnd universal
constants s and ω such that there exists an explicit family of (ω, s)-locally testable classical LDPC
codes with the parameters [n, k ⩾ Rn, d = Θ( n)]q as n→∞ .
In the quantum case, we obtained a somewhat weaker analog of t he above theorem, given
1Note that if one goes beyond the standard deﬁnition of a quant um LDPC code then codes with very good
parameters were already known to exist [ 14, 15].
2

## PDF page 3

below, which shows the existence of asymptotically good fam ilies of qLDPC codes, not necessarily
the locally testable ones. This gives an aﬃrmative answer to the qLDPC conjecture.
Theorem 2. For every number R∈ (0, 1) and ﬁnite ﬁeld Fq there exists an explicit family of
quantum LDPC codes over Fq with the parameters /llbracketn, k ⩾ Rn, d = Θ( n)/rrbracketq as n→∞ .
Remark 1. In the case of classical codes from Theorem 1, it is relatively easy to show that an al-
gorithm, similar to the bit-ﬂipping algorithm, corrects in linear time any error of weight up to the
constant fraction of the code length n. As for the quantum codes from Theorem 2, we conjec-
ture that it is also possible with a variant of the small-set- ﬂip decoding algorithm from [ 26] (see
also [ 24]).
The codes from the above two theorems are obtained using the r ecently introduced lifted product
construction [ 17], which can be seen as a generalization of the (tensor) produ ct construction for
classical codes [ 27, 28] and the hypergraph product construction for quantum codes [29]. This
product operation is a special case of the balanced product f rom [18] and best understood in terms
of homological algebra 2. Let us brieﬂy recall that a chain complex is a sequence
···
∂i+1
− −− →Ci
∂i
−→Ci−1
∂i−1
−−−→···
of abelian groups and morphisms called boundary maps such that ∂i◦ ∂i+1 = 0 for all i ∈ Z.
The term Ci in a complex C is called the group of i-chains and the assertion ∂i◦ ∂i+1 = 0 is
equivalent to im ∂i+1 ⊆ ker ∂i, which allows us to consider for every i∈ Z the quotient group
Hi(C) = ker ∂i/ im ∂i+1 called the i-th homology group of the complex C. The abelian groups in
a complex often come with some additional algebraic structu re that makes them vector spaces over
a ﬁeld F or modules over a ring R, in which case it is further assumed that all boundary maps ar e
linear maps. In the context of error correcting codes, we are interested in the complexes with τ
non-zero terms ( τ -term complexes) where each term Ci can be naturally identiﬁed with Fni
q and
interpreted as a space of ni symbols over Fq (code symbols or parity-checks of the code). In such
cases, it is natural to represent an τ -term complex C by the corresponding τ -partite graph called
its Tanner graph, where the edges connect only the parts corresponding to adj acent termsCi,Ci−1
and the connection is governed by ∂i∈ Fni−1×ni
q considered as a biadjacency matrix if we replace
each non-zero entry by 1.
Given two classical linear codes invariant under a free acti on of a group G on their index sets 3, we
can represent them by 2-term chain complexes A : Rna A− →Rma andB : Rnb B− →Rmb over the group
algebra R = FqG, where A∈ Rma×na, B∈ Rmb×nb are the corresponding parity-check matrices 4.
The lifted product over R is deﬁned as the tensor product complex 5C =A⊗ RB over the ring R,
2In this text, we assume that the reader is familiar with the st andard notions of homological algebra such as
a (co)chain complex and the corresponding (co)homology gro ups. See Appendix A for the relevant deﬁnitions and [ 30]
for a short introduction into this subject.
3A classical linear code C ⊆ Fn
q is invariant under an action of a group G on the index set [ n] if for every g ∈ G and
(ci)i∈[n] ∈ C it follows that ( cπ g (i))i∈[n] ∈ C , where π g is the permutation corresponding to the action of g on [ n]. If
the action of G is free then each orbit has |G| elements, and C can be considered as a subspace of Rs, where R = FqG
is the group algebra over Fq for G, and s := n/ |G|. If G is a cyclic group then such codes correspond to the class of
quasi-cyclic codes, which contains classical cyclic codes as a special case when s = 1.
4If G is non-abelian then when we multiply a vector over R = FqG by the matrix A (resp. B), we assume that
we multiply by the elements from R from the right (resp. from the left). See Appendix
B for more details on the
deﬁnition of the lifted product in terms of the parity-check matrices.
5The general deﬁnition of the tensor product complex A ⊗R B over an arbitrary ring R can be found in [ 30, p. 7].
3

## PDF page 4

i.e., the 3-term complex
Rnanb ∂2
−→Rnamb⊕ Rmanb ∂1
−→Rmamb
with the boundary map ∂ :C→C given by the following diagram
Rnamb Rmamb
Rnanb Rmanb
A⊗Rid
−id⊗RB
A⊗Rid
id⊗RB ,
which means that ∂2 :=
[
A⊗Rid
−id⊗RB
]
, ∂1 := [ A⊗R id, id⊗R B]. One can easily check that ∂1◦ ∂2 =
A⊗R B− A⊗R B = 0, and C is indeed a chain complex. Now we can consider the classical c ode
ker ∂2 with the parity-check matrix ∂2 and the quantum CSS code Q(∂1, ∂∗
2 ) where CX := ker ∂1
andCZ := ker ∂∗
2. We can naturally identify these codes with the second homol ogy group H2(C)
and the ﬁrst homology group H1(C) of the complex C, and we use them to obtain the classical
codes from Theorem 1 and the quantum ones from Theorem 2, respectively. Note that when G is a
trivial group, i.e., |G| = 1, then R∼
= Fq, and one can see that ker ∂2 andQ(∂1, ∂∗
2 ) are respectively
the tensor product and the hypergraph product of the two clas sical codes ker A and ker B. Hence
the lifted product complex A⊗ RB, which we also sometimes denote by LP( A, B), can be seen as
a generalization of these two constructions, where instead of individual symbols from Fq we have
blocks of|G| symbols represented by elements from FqG∼
= F|G|
q . In fact, lifted product can also be
used with arbitrary ﬁnite-dimensional associative algebr a R over Fq, not necessary equal to FqG.
In the current paper, if R = FqG we call this operation lifted product over G or G-lifted product
and denote the corresponding lifted product complex by A⊗ GB.
The idea of the lifted product was used recently in [
17] to obtain the ﬁrst family of qLDPC
codes with almost linear distance. In the follow-up paper [ 18], where some of the ideas from [ 17]
were developed independently, a very similar construction called balanced product was used to get
qLDPC codes of very large distances 6. As in the case of lifted product, the balanced product A⊗GB
of two chain complexes A andB can also be considered as the tensor product complex A⊗ RB
over the the group algebra R = FqG, but this time A andB are arbitrary (i.e., not necessary free)
R-modules. As it was shown in [ 18], the G-lifted product and the balanced product can both be
viewed as instances of even more general topological idea ca lled a ﬁber bundle , proposed as a way
to construct qLDPC codes in the breakthrough paper [ 16], which ﬁrst broke the n1/2polylog(n)
barrier on the distance of qLDPC codes. It is also interestin g to note that the codes that were
actually used to get the main results in [ 16–18] are equivalent to LP( A, b) where A is a sparse
matrix over R = F2Cℓ, and b∈ R, where Cℓ is the cyclic group of order ℓ. This more restricted
class of lifted product codes were previously studied in [ 31] under the name GHP codes and shown
to have surprisingly good error-correcting performance un der the BP-OSD decoder.
A very important ingredient of the constructions from [ 17, 18] is expander codes [ 32], which
are the Tanner codes [ 33] obtained from spectral expander graphs. The individual sy mbols of
the expander code T (Γ; h) are assigned to the edges of the corresponding graph Γ, and w e get
a codeword precisely when for each vertex v from Γ the symbols assigned to the edges connected
to v form a codeword of the local code ker h. In [ 17] expander graphs Γ are obtained as G-lifts (i.e.,
6Note that the codes from [ 17] are CSS codes, while the codes from [ 18] are in general from a wider class of
quantum codes called subsystem codes.
4

## PDF page 5

regular|G|-fold covers) of some small base graphs, where G is a very large group 7. It is not hard
to see that the obtained in this way expander codes are invari ant under the free action of G, and
thus they are free modules over the group algebra FqG. Therefore such codes can be used with the
G-lifted product to obtain a 3-term chain complex C, which can also be considered as a quantum
CSS code.
It is shown in [ 17, Example 3] that using a G-lifted product of two classical codes it is possible to
obtain qLDPC codes of constant rate 8. In particular, if ρ := 1− m/n is the design rate of a classical
code ker A represented by the complexA := Rn A− →Rm, then the rate of the corresponding quantum
code represented by A⊗ GA∗ is at least (n−m)2
n2+m2 = ρ2
1+(1−ρ)2 . Here A∗ := Rm A∗
− − →Rn is the dual
chain complex forA, i.e., A∗ is the transpose of the parity-check matrix A, considered as a matrix
over Fq. Hence the rate of the quantum codes obtained from A⊗ GA∗ can be arbitrary close to 1 as
ρ→ 1. Moreover, some particular examples of such codes [ 17, Example 4], indicate that they may
also have very large minimal distances, close to the distanc es of the classical codes ker A used in the
lifted product. However, if the group G is abelian, then the upper bound on the minimum distance
of such classical codes [ 17, Eq. 24] provides strong evidence that to obtain an asymptot ically good
family of qLDPC codes by a G-lifted product one has to use non-abelian groups.
One particular construction of balanced product codes, ana logous to the aforementioned G-
lifted productA⊗ GA∗, for non-abelian group G, was conjectured in [ 18] to give an asymptotically
good family of qLDPC codes. Unfortunately, our proof strate gy does not work for complexes
A⊗ GA∗, and we can not prove this conjecture with the methods develo ped here. Instead, we
consider similar complexes A⊗ GB∗, where A andB are respectively the expander codes T (Γ; h)
andT (Γ; h′) deﬁned for the same expander graph Γ but for diﬀerent local codes ker h and ker h′.
It is very simple to show by counting the number of the code sym bols and parity-checks in the LTC
and the qLDPC code obtained from A⊗ GB∗ that these codes have constant rate. However, for our
proof of Theorems 1 and 2 to work, the pair of local codes used in A⊗ GB∗ can not be arbitrary
and should satisfy some special property we call product-expansion, which is similar to the robust
testability property often used in the context of LTCs [ 28,34]. We prove that a pair of random linear
codes has the product-expansion property with high probabi lity. Informally speaking, the product-
expansion of the pair of local codes corresponds to the local expansion in the complexA⊗ GB∗, but
to get the main result we also need the global expansion property of the graph Γ, which connects
the local codes attached to its vertices. Our main technical result (Proposition 1) shows that the
general constructionA⊗ GB∗ can be used with arbitrary regular graphs Γ obtained as G-lifts if they
are suﬃciently good small set expanders 9. We prove that spectral expander graphs and their ﬁnite
covers are good small set expanders. Hence we can let the grap h Γ to be the bipartite double-cover
of a Cayley graph for some ﬁnite group G. This is important for the G-lifted product construction
since such graphs Γ can be also represented as G-lifts10. In particular, we use the Ramanujan
Cayley graphs [ 35, 36], which were also used in the original construction of the ex pander codes [ 32]
and in the mentioned earlier conjecture from [ 18].
The main technical tool in our proof of Theorems 1 and 2 is the notion of a locally minimal
7In [ 17] this general idea was applied to cyclic groups to obtain the main result.
8A similar observation about balanced products is also made ( without a proof) in [ 18].
9Informally this means that every suﬃciently small set of ver tices has a lot of outgoing edges. See Subsection 2.2
for the relevant deﬁnitions and results.
10Note that in most cases a Cayley graph with w generators can also be viewed as a G-lift of the w-bouquet
graph Bw. However, this is not true if we have an order 2 generator.
5

## PDF page 6

(co)chain, often used in the context of high-dimensional ex panders to show expansion properties
in simplicial complexes [ 37]. It is known that such expansion properties can be used to sh ow local
testability of a classical code [ 38] and to give a lower bound on the minimum distance of a quantum
code [ 24]. In the current work, we extend these ideas to a much more gen eral context of (co)chain
complexes with local system of coeﬃcients, which can be cons idered as high-dimensional analogs
of the Tanner codes, similar to the ones studied in [ 39]. Instead of graphs such generalized Tanner
codes are deﬁned on high-dimensional complexes. Since the G-lifted product is deﬁned for arbitrary
complexes, it can naturally be applied to graphs, viewed as 1 -dimensional complexes. If we consider
graphs Γ and Γ ′ as topological spaces, their G-lifted product (as a topological space) can be viewed
as the balanced product Γ ×G Γ ′ of these spaces [ 18]. In fact, it can be shown that the products
Γ×G Γ ′ are examples of a well-known class of 2-dimensional complex es called complete square
complexes [40]. The deﬁning property of a complete square complex is that t he links of all its
vertices are isomorphic to a complete bipartite graph. Since complete bipartite graphs are perfe ct
expanders, then, in some sense, this property is analogous t o the property of other high-dimensional
expanders to have links that are good expanders [ 37].
Using the discussed above G-lifted products of expander codes over non-abelian groups G we
show that it is possible to obtain qLDPC codes with the parame ters as in Theorem 2. This gives
a positive answer to the questions posed in [ 17, Conclusion] and in [ 18, Conjecture] of whether
respectively lifted and balanced products of classical cod es can give an asymptotically good family
of qLDPC codes. Moreover, we also show that, under some addit ional assumptions, if HX and
HZ are the parity-check matrices of such qLDPC codes, then the c lassical code ker H ∗
Z is locally
testable with the parameters as in Theorem 1.
Remark. After the ﬁrst draft of this manuscript was published we beca me aware that a result
similar to our Theorem 1 for the case of binary ﬁeld F2 was independently claimed in [ 41]. The
3-term complex used in [ 41] to get the main result is equivalent to the balanced product over G
of the expander codes [ 13, 18], deﬁned on two diﬀerent Cayley graphs for the same group G. It is
interesting to note that this construction is similar to the lifted product construction we consider
in Remark 5, where instead of the product A⊗ GB∗ we propose to use the product A⊗ GB and
conjecture that this way it is still possible to get asymptot ically good LTCs. The diagrams for
A⊗ GB andA⊗ GB∗ are shown below
A⊗ GB :=
Rnamb Rmamb
Rnanb Rmanb
A⊗Rid
−id⊗RB
A⊗Rid
id⊗RB , A⊗ GB∗ :=
Rnamb Rmamb
Rnanb Rmanb
A⊗Rid
−id⊗RB∗
A⊗Rid
id⊗RB∗ .
In fact, the Tanner graphs of the complexes A⊗ GB andA⊗ GB∗ are isomorphic. What is diﬀerent
is the interpretation of the Tanner graph vertices as code symbols and parity-checks when we make
a code out of the complex. In some sense, the product A⊗ GB is better suited for LTCs since it
gives classical codes of rate arbitrary close to 1 (please, s ee Remark 5). Hence it is an interesting
open question whether the approach used in [ 41] can also succeed on our codes from Remark 5. At
the same time, the construction A⊗ GB∗, which we use to prove the main results, is much better
suited for qLDPC codes since it symmetric. This symmetry all ows us to prove the lower bound
on the Z-distance of our qLDPC code in the same way as for the X-distance. Besides, we can get
equal number of X-checks and Z-checks, which gives qLDPC codes of rates arbitrary close to 1.
6

## PDF page 7

1 Preliminaries
1.1 Chain complexes
In recent years, ideas from homological algebra found many i nteresting applications in the ﬁeld of
classical and quantum codes [
38,42,43]. A common approach is to consider some based 11 (co)chain
complex of ﬁnite-dimensional vector spaces over a ﬁnite ﬁel d Fq, and use it to deﬁne a code with
the desired parameters. For example, a 2-term chain complex
Fn
q
∂1
−→Fm
q
can be identiﬁed with the classical linear code ker ∂1 deﬁned by the parity-check matrix H := ∂1.
Here, the space Fn
q of 1-chains corresponds to the n bits, while the space Fm
q of 0-chains to the
m checks. At the same time, a 3-term chain complex
C :=
(
FmZ
q
∂2
−→Fn
q
∂1
−→FmX
q
)
can be identiﬁed with the quantum CSS /llbracketn, k, d/rrbracketq codeQ =Q(HX, HZ ) deﬁned by the parity-
check matrices HX := ∂1 and HZ := ∂∗
2, where ∂∗
2 : Fn
q → FmZ
q is the transpose of the map
∂2 : FmZ
q → Fn
q . In this case, the space Fn
q of 1-cells corresponds to the n qubits, and the space
FmX
q of 0-cells (resp. the space FmZ
q of 2-cells) to the X-checks (resp. Z-checks). The length of
Q is equal to n = dim Fn
q , while its dimension k is equal to the dimension of the ﬁrst homology
group H1(C) := ker ∂1/ im ∂2 =CX/C⊥
Z , where CX := ker ∂1 andCZ := ker ∂∗
2. The minimum
distance d = d(Q) can also be described in the language of homology groups if w e consider the
quotient vector space H1(C) as a metric space, where the distance d(A, B) between homology classes
A, B∈ H1(C) is deﬁned as d(A, B) := |A− B| using the corresponding quotient Hamming norm
|A| := min a∈A|a|. It is easy to see that d = min(d(H1(C), d(H1(C∗)), where
C∗ :=
(
FmX
q
∂∗
1
−→Fn
q
∂∗
2
−→FmZ
q
)
is the dual chain complex forC. The distances d(H1(C)) and d(H1(C∗)) are sometimes called the
1-systolic and 1 -cosystolic distances ofC.
1.2 Lifted product
In this work, we consider several new families of classical a nd quantum LDPC codes of constant rate
based on the introduced recently lifted product constructi on [
17], which generalizes many known
constructions of quantum LDPC codes [ 2, 29, 43–46]. This construction can be deﬁned in terms of
parity-check matrices (see Appendix B) and in the abstract language of homological algebra, which
we prefer in the current work. Before we proceed, let us brieﬂ y remind some standard deﬁnitions
from algebra. Consider some ring R. A left R-module M is called free if there exists a set of
elements{m1, . . . , mr}⊆ M called basis such that every m∈ M is uniquely represented as:
m = a1m1 + . . . + armr,
11The term based means that the vector spaces of a (co)chain complex come with some distinguished bases. If in
a vector space V we ﬁx a basis ˜V ⊆ V , we can identify V and its dual space V ∗ with the coordinate space Fdim V
q in
the standard way. This also allows us to identify linear maps between such spaces with the corresponding matrices.
7

## PDF page 8

where a1, . . . , ar∈ R, and the parameter r is called the rank12 of M . Hence M∼
= Rr, and if the
ring R is a ﬁeld, then M is just an r-dimensional vector space over R. A canonical example of
a free R-module of rank r is the module RS of formal R-linear combinations of the elements of
some set S, where|S| = r. One can also deﬁne free right R-modules in a similar way.
Deﬁnition. Suppose we have a ﬁnite-dimensional associative algebra R over Fq with some ﬁxed
basis ˜R⊆ R. Consider two chain complexes A = ⨁ m
i=0Ai andB = ⨁ n
j=0Bj over Fq such that the
vector spacesAi andBj are also free R-modules with some distinguished bases (over R) ˜AR⊆A
and ˜BR⊆B , and the boundary maps ∂A :A→A , ∂B :B→B are R-linear. If the algebra R is not
commutative, then we further assume that R acts from the right on A and from the left on B, i.e.,
A is a right free R-module, and B is a left free R-module. The lifted product ofA andB over R
is their tensor product complex A⊗ RB (see [
30, p. 7]), where for k = 0, 1, . . . , m+ n the space of
k-chains (A⊗ RB)k is equal to ⨁
i+j=kAi⊗RBj, while the boundary map ∂ :A⊗ RB→A⊗ RB
is deﬁned for a∈A i, b∈B j as13
∂(a⊗R b) := ∂Aa⊗R b + (−1)ia⊗R ∂Bb, (1)
and extended by linearity. Furthermore, we always assume th at the lifted product C =A⊗ RB is
a based chain complex of vector spaces over Fq. By deﬁnition its distinguished basis (over Fq) is
given by
˜C :={a· r· b| a∈ ˜AR, b∈ ˜BR, r∈ ˜R},
where we used a short-hand notation:
a· r· b := ar⊗R b = a⊗R rb. (2)
From the properties of the tensor product ⊗R it follows that the map ( a, r, b)↦→a· r· b is Fq-
multilinear, which means that for every a, a′∈A , b, b′∈B , and r, r′∈ R we have:
(a + a′)· r· b = a· r· b + a′· r· b,
a· (r + r′)· b = a· r· b + a· r′· b,
a· r· (b + b′) = a· r· b + a· r· b′,
and for every λ∈ Fq we get:
(λa)· r· b = a· (λr)· b = a· r· (λb) = λ(a· r· b).
We should note that if R = Fq, then the lifted product is equivalent to the product constr uction
from [ 43], while if, in addition, we have m = n = 1, then it is the same as the hypergraph
product [ 29]. Moreover, if m = n = 1 and R = F2[x]/(xℓ− 1), it is essentially equivalent to
the hyperbicycle codes construction [ 46]. It is also important to note that when m = n = 1 the
complexes
A :=
(
A1
A− →A0
)
andB :=
(
B1
B− →B0
)
12Note that there are some inﬁnite non-commutative rings R such that Rm ∼
= Rn when m ̸= n. However, all the
rings we consider here are either ﬁnite or commutative, and h ence have the invariant basis number (IBN) property
that implies that this never happens.
13We should note that the sign ( −1)i in this deﬁnition is only relevant in the case of ﬁnite ﬁelds o f odd characteristic.
8

## PDF page 9

are uniquely deﬁned by the corresponding matrices A, B over R. In this case, we denote the
lifted productA⊗ RB as LP( A, B) and usually identify it with the corresponding CSS code. No te
that this code also has a concise description in terms of the p arity-check matrices HX and HZ
(see [ 17, Eq. 12] and Eq. 13 from Appendix B).
Though the lifted product can be deﬁned over an arbitrary ﬁni te-dimensional associative alge-
bra R, the most interesting case [ 17,18] is when R is the group algebra FqG for some ﬁnite group G.
The elements of FqG are formal sums ∑
g∈G αgg, where αg∈ Fq. Consider elements a = ∑
g∈G αgg
and b = ∑
g∈G βgg from FqG. Their sum a + b and product ab are deﬁned as follows:
a + b :=
∑
g∈G
(αg + βg)g, ab :=
∑
g∈G

 ∑
hr=g
αhβr

 g.
In this case, the condition that the vector spaces A andB over Fq are free FqG-modules is equivalent
to the condition that the group G has a free action
14 on the their bases over Fq (from the right forA
and from the left for B), which is extended by linearity to A andB. Moreover, the boundary map ∂
is FqG-linear if‌f it is an Fq-linear map that commutes with the action of the group G. Therefore
in what follows, in tensor products over R = FqG instead of ⊗R we write ⊗G, and assume that
˜R := G. Let ˜AG = ⨆
i∈Z ˜AG,i and ˜BG = ⨆
j∈Z ˜BG,j be respectively the distinguished bases (over
FqG) of the the free FqG-modulesA = ⨁
i∈ZAi andB = ⨁
j∈ZBj. It is clear that the elements
ag (resp. gb), where a∈ ˜AG,i, g∈ G, b∈ ˜BG,j, constitute the basis for Ai (resp. Bj), considered
as a vector space over Fq. Moreover, we see, using short-hand notation ( 2), that the distinguished
basis ofA⊗ GB over Fq consists of the elements a· g· b, where a∈ ˜AG,i, g∈ G, b∈ ˜BG,j; i, j∈ Z.
Furthermore, we can express the boundary operator given in e quation ( 1) as follows:
∂(a· g· b) := ( ∂Aa)· g· b + (−1)ia· g· (∂Bb). (3)
We can also express the boundary operator ∂ as
∂ := ∂A⊗G id + id⊗G ∂B
if, by deﬁnition, assume that ( ∂A⊗Gid)(a·g·b) := ( ∂Aa)·g·b and (id⊗G∂B)(a·g·b) := (−1)ia·g·(∂Bb).
Remark 2. For any chain complex C we can consider its dual chain complex C∗ obtained fromC if
we replace the boundary map ∂ ofC by its transpose map ∂∗ (see Appendix A). It is not hard to
see that if C is a left (resp. right) G-module, then C∗ is a right (resp. left) G-module. Therefore
if chain complexes A andB are right G-modules, we can consider the G-lifted product A⊗ GB∗.
In fact, for any set S with a left action ( g, s)↦→g· s (resp. a right action ( s, g)↦→s· g) of a group
G we can also consider the corresponding right (resp. left) ac tion of G deﬁned as ( s, g)↦→g−1· s
(resp. ( g, s)↦→s· g−1). Therefore if a group G has a right free action on a chain complex C, then
it also has the corresponding left free action on C, and vice versa. This allows us to apply G-lifted
productA⊗ GB to two right G-modulesA andB, if we use the corresponding left action of G on
B.
14A left (resp. right) action of a group G on a set S is called free if for every g ∈ G when we have gs = s (resp.
sg = s) for some s ∈ S, then g is the identity element of G. Note that the sizes of all orbits of a free action are the
same and equal to |G|.
9

## PDF page 10

Remark 3. Let us note that G-lifted product is a special case of balanced product from [ 18], where
a non-free action of the group G is also allowed. We should also emphasize that the ﬁrst examp les
of the lifted products over R = F2G for a non-abelian group G were also considered in [ 18], while
in [ 17] all the examples were only for the abelian case. In the curre nt work, we also give new
examples of non-abelian lifted products based on the double -cover of a Cayley graph, which are
similar, though not equivalent, to the horizontal subsyste m codes mentioned in the Conjecture
from [ 13]. Generally speaking, the term G-lifted product , used in the current work, may seem
redundant since it is just a special case of the balanced prod uct. However, we think that this
special case deserves its own name since the free action of G implies that the obtained complex
has a much more regular structure than in the general case. In some sense, the relation of the
G-lifted product to the more general balanced product is simi lar to the relation of Cayley graphs to
Schreier graphs. While the latter are more general, the form er are usually much easier to describe
and study.
1.3 Expander graphs and lifts
To produce linear maps ϕ : Fn
q → Fm
q with good expansion and coexpansion properties it was
proposed in [
17, 18] to use expander codes [ 32], i.e., the Tanner codes [ 33] deﬁned on some spectral
expander graph. Before we move on, let us recall some standar d deﬁnitions related to expander
graphs and Tanner codes.
Let Γ be a graph 15 with the set of vertices V (Γ) and the set of edges E(Γ). If vertices v, v′∈ V (Γ)
are connected by an edge e∈ E(Γ), we call v, v′ adjacent and denote this fact by v↔ v′ or by v↔e v′
when we want to emphasize the edge e. A graph Γ is called d-regular if all its vertices have degree d.
The adjacency matrix of a graph Γ with V (Γ) ={v1, . . . , vn} is the matrix A(Γ) = ( aij)n×n, where
aij is the number of edges e∈ E(Γ) such that vi↔e vj. Since A(Γ) is a symmetric matrix, it has n
real-valued eigenvalues λ1 ⩾ ··· ⩾ λn. Let λ2(Γ) := λ2, and λ(Γ) := max(|λ2| ,|λn|). It is obvious
that λ2(Γ) ⩽ λ(Γ). We call an n-vertex d-regular graph Γ an ( n, d, λ)-expander if λ(Γ) ⩽ λ. The
term expander here means that the graph Γ has a very good conne ctivity, which can be quantiﬁed
by its Cheeger constant. Consider a subset of vertices S⊆ V (Γ) in the graph Γ. We call the set
∂S :={e∈ E(Γ)| v↔e v′, v∈ S, v′ /∈ S}
the edge boundary, which is the set of all edges that go outside of S. The Cheeger constant h(Γ) of
the graph Γ is deﬁned as follows:
h(Γ) := min
0<|S|⩽ 1
2 |V (Γ) |
S⊆V (Γ)
|∂S|
|S| .
Since for d-regular graphs it is known [ 47, Theorem 4.11] that h(Γ) ⩾ 1
2 (d− λ2(Γ)), then the
smaller the value of λ2(Γ), the higher the Cheeger constant. However, the Alon-Bop pana bound [ 47,
Theorem 5.3] implies that for d-regular graphs with n vertices we have λ2(Γ) ⩾ 2
√
d− 1− on(1)
as n→∞ . There are a number of diﬀerent constructions that almost att ain this lower bound.
In fact, it was shown in [ 48] that for any ﬁxed ε > 0, a random d-regular graph with n vertices
has λ2(Γ) < 2
√
d− 1 + ε with high probability as n→∞ . A d-regular graph Γ that satisfy the
15It may have loops and multiple edges.
10

## PDF page 11

v
v′
base graph Γ
ˆv1
. . .
ˆvℓ
ˆv′
1. . .
ˆv′
ℓ
π∈ Sℓ
ℓ-lift ˆΓ of Γ
Figure 1: Lifting of the base graph Γ.
condition λ(Γ) ⩽ 2
√
d− 1 is called Ramanujan16. There are a number of explicit constructions of
such graphs [ 35, 36] that use Cayley graphs of some non-commutative groups (see [49] for a good
survey).
We will see later that Tanner codes with such Ramanujan graph s (or their double-covers) can
be used with the lifted product construction. The obtained c hain complexes, which we can also
consider as CSS codes, have very interesting expansion prop erties, similar to the ones studied in the
theory of high-dimensional expanders (HDXs) [ 50]. We will show later that some of the standard
deﬁnitions from this theory (e.g., the local minimality of ( co)chains) can be naturally extended to
a more broad context of based (co)chain complexes.
In [ 17], the graph ˆΓ for the Tanner code was obtained as an ℓ-lift of a small base graph Γ using
voltage assignments [ 51] with the cyclic group Cℓ as the voltage group. Recall that an ℓ-lift (also
called an ℓ-fold cover ) of a base graph 17 Γ is a graph ˆΓ obtained if we replace in the base graph
each vertex v∈ V (Γ) with ℓ replicas ˆv1, . . . ,ˆvℓ, and replace each edge e∈ E(Γ) that connects
vertices v, v′∈ V (Γ) with ℓ replicas ˆe1, . . . ,ˆeℓ such that ˆei connects in ˆΓ the vertices ˆ vi and ˆv′
π(i),
where π∈ Sℓ is some permutation on the set {1, . . . , ℓ} (see Fig. 1). Note that the permutations
for diﬀerent edges may be diﬀerent and are usually deﬁned [ 51] by a voltage assignment using some
group G, in which case we call the obtained graph a G-lift of Γ.
A voltage assignment for a graph Γ with a voltage group G is a map γ : E(Γ)→ G . Let us ﬁx
some orientation of the edges, i.e., a function o : E(Γ)→ V (Γ)× V (Γ), which tells us that the edge
e is oriented from v to v′ if o(e) = ( v, v′). For any voltage assignment γ, we can obtain the G-lift
ˆΓ of the base graph Γ called the ( left) derived graph for Γ and γ, which we denote by D(Γ; γ). To
deﬁne ˆΓ = D(Γ; γ) we ﬁrst let V (ˆΓ) := V (Γ)× G, E(ˆΓ) := E(Γ)× G, and introduce the following
short-hand notations: ˆ vg := ( v, g), ˆeg := ( e, g), where v∈ V (Γ), e∈ E(Γ), g∈ G. Now, if in
the base graph Γ an edge e∈ E(Γ) connects vertices v, v′∈ V (Γ), and o(e) = ( v, v′), then in the
derived graph ˆΓ, for every g∈ G, the edge ˆ eg connects the vertices ˆvg and ˆv′
γ(e)g. One can also
deﬁne the right derived graph if the edge ˆeg connects the vertices ˆvg and ˆv′
gγ(e). We call the G-lifts
obtained from the left and right derived graphs left and right respectively.
Note that a G-lift ˆΓ obtained by a voltage assignment from a base graph Γ is usual ly called
a regular lift or a regular cover of Γ. If a group G has a right (resp. left) free action on the vertices
and edges of a graph, and the condition v↔e v′ implies vg↔eg v′g (resp. gv↔ge gv′) for every
vertices v, v′, edge e, and g∈ G, then we say that G has a right (resp. left) free action on this
16In this work we consider only non-bipartite Ramanujan graph s.
17Multiple edges and loops are usually allowed in the base grap h Γ.
11

## PDF page 12

graph. One can easily check that for any left G-lift we can deﬁne a right action of G if for every
ˆvg∈ V (ˆΓ), ˆeg∈ E(ˆΓ), and h∈ G we put ˆvgh := ˆvgh, ˆegh := egh. In what follows, we consider
only left G-lifts and omit the word “left”. Note that when the group G is abelian, then there is no
diﬀerence between left and right G-lifts.
When the voltage group is a cyclic group Cℓ, then the corresponding derived graphs are also
called shift ℓ-lifts and the assigned voltages are called shifts. In the special case when ℓ = 2,
and we assign to each edge e of the base graph Γ the non-identity shift from C2, we obtain the
bipartite graph ¯Γ called the ( bipartite) double-cover of G. Since ¯Γ is the tensor product of Γ and
the complete graph K2, then it is not hard to show that λ2(¯Γ) = λ(Γ). Hence this particular 2-lift
almost preserves the spectral expansion properties. Note t hat if Γ is a bipartite graph then ¯Γ is
a disconnected graph. Hence, it does not make a lot of sense to apply this simple construction more
than once since on the second iteration one inevitably obtai ns a disconnected graph. However, the
situation is not that bad if we apply a large shift ℓ-lift only once. As it was shown in Theorem 1.2
from [ 52], if the base graph Γ has good spectral expansion properties , then by using random shifts
the obtained graph ˆΓ also has good expansion properties, even when the lift size ℓ is very large.
In [ 17], such graphs ˆΓ were used to construct quasi-cyclic expander codes of very large lift size
ℓ such that the corresponding parity-check matrix H and its transpose H ∗ have good expansion
properties.
In the current work, we also obtain graphs ˆΓ using voltage assignments. We start from a very
small base graph Γ such as the bouquet graph Bw (one vertex, w loops) or the graph Dw (two
vertices connected by w multiple edges). Then we consider a ﬁnite group G with some ﬁxed w-
element set of generators S⊆ G and assign each generator from S ={s1, . . . , sw} to exactly one of
the w edges (see Fig. 2). It is not hard to see that the derived graphs for Bw correspond to Cayley
graphs Cay( G, S) if the generating set S is symmetric, i.e. S ={s−1| s∈ S}, and there are no
generators s∈ S such that s = s−1. Let us remind that, given a ﬁnite group G with some symmetric
generating set S, the corresponding ( left) Cayley graph is the simple graph Cay( G, S) with the set
of vertices V (Γ) := G and the set of edges E(Γ) := {{g, sg}| g∈ G, s∈ S}. Now if we assign the
elements of a symmetric generating set S of some ﬁnite group G one-to-one to the w edges of the
graph Dw (the orientation is shown in Fig. 2), then we obtain the graph Cay 2(G, S), which is the
double-cover of Cay( G, S). The graph Cay 2(G, S) has the set of vertices V (Γ) := G×{ 0, 1} and
the set of edges:
E(Γ) :={{(g, 0), (sg, 1)}| g∈ G, s∈ S}.
Note that the free right action of the group G on this graph is deﬁned as ( g, a)h := ( gh, a) and
{(g, 0), (sg, 1)}h :={(gh, 0), (sgh, 1)}, where h, g∈ G, s∈ S, and a∈{ 0, 1}.
Example 1. Let us now consider the inﬁnite family of ( p + 1)-regular non-bipartite Ramanujan
graphs X p,q from [35], where p and q are two unequal primes such that q > 2√p, p≡ q≡ 1 (mod 4),
and p(q−1)/2≡ 1 (mod q). The graph X p,q is obtained in [ 35] as the Cayley graph Cay( G, Sp,q),
where18 G := PSL(F2
q) and Sp,q is some speciﬁc symmetric set of p + 1 generators. Denote by ¯X p,q
the corresponding double-cover Cay 2(G, Sp,q). Hence ¯X p,q is a ( p + 1)-regular bipartite graph with
n = 2|G| vertices, where|G| = q(q2− 1)/2. Since it is proved in [
35] that λ(X p,q) ⩽ 2√p, then we
also have λ2( ¯X p,q) ⩽ 2√p. Moreover, the graph ¯X p,q is a G-lift of the base graph Dp+1 from Fig. 2,
and the group G has a free right action on ¯X p,q.
18The group PSL( F2
q) is the projective special linear group for F2
q, i.e. the quotient of the group of matrices A ∈ F2×2
q
with det A = 1 modulo its subgroup {± ( 1 0
0 1 )}.
12

## PDF page 13

. . .
s1
s2
sw
Graph Bw
v1 v2
. . .
s1
s2
sw
Graph Dw
Figure 2: Voltage assignments for the graphs Bw and Dw. The derived graph for Bw corresponds
to Cay( G, S), while the derived graph for Dw is the double-cover of Cay( G, S). The small arrows
shows the orientation that we ﬁx.
1.4 Classical codes
In this subsection we review some standard deﬁnitions and te rminology related to classical linear
codes. A linear [n, k]q code is a k-dimensional subspaceC⊆ Fn
q , where the parameters n and k are
called the length and the dimension ofC, respectively. We denote the dimension k of the code C by
dimC. The rate of the codeC is equal to k/n. The elements of C are called codewords. The minimal
distance d(C) of the code C is the minimal weight of a non-zero codeword from C, and d(C) :=∞
when k = 0. When a linear [ n, k]q codeC has minimal distance d, we say that C is an [ n, k, d]q
code.
A linear [ n, k]q code is usually deﬁned either as the row space of a matrix G called the generator
matrix , or as the kernel of a matrix H called the parity-check matrix. It is easy to see that GH ∗ = 0,
rk G = k, and rk H = n− k. The code deﬁned by a parity-check matrix H is denoted by ker H.
The vector space Fn
q usually comes with the standard scalar product ⟨x, y⟩ = x1y1 +··· + xnyn.
The dual codeC⊥ for a linear [ n, k]q codeC is the [ n, n− k]q code
C⊥ ={x∈ Fn
q|⟨ x, y⟩ = 0 for all y∈C} .
It is not hard to see that a generator matrix for C is a parity-check matrix for C⊥ and vice versa.
Remark 4. Note that in the current work it is convenient to consider a sl ightly more general case,
where instead of Fn
q we have an arbitrary based n-dimensional vector space M over Fq equipped
with some distinguished basis ˜M ={m1, . . . , mn}⊆M . In this case, M∼
= Fn
q , and we can consider
subspacesC⊆M as linear codes, and apply all the terminology we introduced above to this case
as well.
In what follows, we will often use the following important de ﬁnitions.
Deﬁnition. Consider two linear codes C ⊆ Mand C′ ⊆ M′, where M and M′ are two n-
dimensional vector space over Fq with distinguished bases ˜M and ˜M′ respectively. We say that
C andC′ are ( permutation) equivalent and write C∼C ′ if there exists a linear map π :M→M ′
such that π( ˜M) = π( ˜M′) and π(C) = π(C′). We also say that two m× n matrices A and B are
(permutation) equivalent and write A∼ B if we can obtain one from another by some row/column
permutations. It is clear that if A∼ B then ker A∼ ker B.
13

## PDF page 14

1.5 Expander codes
In this subsection, we describe expander codes, which are Ta nner codes obtained from expander
graphs. We adopt a very convenient way, used in [
39], [ 18] to represent these codes in the language
of chain complexes and local systems. If F is some abelian group and X is some n-element set, then
we denote by FX the abelian group of all formal linear combinations ∑
x∈X axx of the elements
x∈ X with coeﬃcients ax∈F . When n = 1, and X ={x}, we usually write Fx instead ofF{x}.
IfF = Fq then the group FX is isomorphic to the vector space Fn
q . When F = Fm
q , the group FX
can be identiﬁed with the vector space Fmn
q of block vectors ( v1, . . . , vn) with the blocks vi∈ Fm
q ,
i∈ [n]. If S⊆ X and a = ∑
x∈X axx, then a|S := ∑
x∈S axx. Now let us introduce the following
important deﬁnition.
Deﬁnition. Consider a graph Γ = ( V, E) and a collection ( ∂(v))v∈V of linear maps ∂(v) : FqEv→
Fr
qv called local boundary maps, where Ev is the set of edges incident to the vertex v∈ V . A Tanner
chain complex T = T•(Γ; (∂(v))v∈V ) is a chain complex FqE ∂1
−→Fr
qV such that for every e∈ E
that connects v and v′ we have:
∂e := ∂(v)e + ∂(v′)e. (4)
Any Tanner complex T deﬁnes the global linear code C := ker ∂1, also known as the Tanner
code, and a number of local linear codesCv := ker ∂(v), v∈ V , also known as subcodes. We see that
c∈C if‌f c|Ev∈C v for all v∈ V . In what follows, we consider Tanner complexes where the mat rices
of all local boundary maps ∂(v) are equivalent to one matrix h∈ Fr×w
q . Hence all local codes Cv
are also equivalent to the same linear [ n, k, d]q code ker h. We denote the class of all such Tanner
complexes on the graph Γ as T(Γ; h).
We can lift Tanner complexes in a similar way as we lift graphs using voltage assignments.
Consider a Tanner complex T = T•(Γ; (∂(v))v∈V ) for the graph Γ. For any G-lift ˆΓ = ( ˆV , ˆE),
obtained from Γ by a voltage assignment γ : E(Γ)→ G, we can deﬁne the G-lifted Tanner complex
ˆT = D(T ; γ). It is convenient to represent ˆT as the complex
FqE⊗ FqG
ˆ∂1
−→Fr
qV⊗ FqG,
where by the tensor product ⊗ we mean the tensor product over Fq. Since Fr
qV⊗ FqG∼
= Fr
q ˆV and
FqE⊗ FqG∼
= Fq ˆE, we can assume that v⊗ g = ( v, g) and e⊗ g = ( e, g) and still consider ˆT as
a Tanner complex
Fq ˆE
ˆ∂1
−→Fq ˆV
for the graph ˆΓ. The boundary map ˆ∂ of this complex is deﬁned for every g∈ G and e∈ E with
o(e) = ( v, v′) as
ˆ∂(e⊗ g) := ∂(v)e⊗ g + ∂(v′)e⊗ γ(e)g,
and extended by linearity (cf. Equation (
4)). Let ˆΓ = D(Γ; γ) be a G-lift of a graph Γ. We denote
by TG(ˆΓ; h) the class of all G-lifted Tanner complexes ˆT = D(T ; γ) whereT ∈T(Γ; h).
Since the G-lifted Tanner complex ˆT is a right G-module19, we can use any such complex with
the G-lifted product construction discussed earlier. Let us now consider a local [ w, k, d]q code ker h
19We can multiply from the right on its basis as follows: ( e ⊗ g)h := e ⊗ gh, ( v ⊗ g)h := v ⊗ gh.
14

## PDF page 15

with the parity-check matrix h∈ Fr×w
q , and the Tanner complexT (h) :=
(
FqE(Dw) ∂1
−→Fr
qV (Dw)
)
with the boundary map deﬁned as
∂ei := hiv1 + hiv2,
where E(Dw) = {e1, . . . , ew}, V (Dw) = {v1, v2}, and hi is the i-th column of the parity-check
matrix h. It is easy to see that the two local codes Cv1 andCv2 ofT (h) are both equivalent
to ker h. As it was already mentioned, we can obtain the double-cover Γ := Cay 2(G, S) of any
Cayley graph Cay( G, S) as the G-lift of Dw, where w :=|S|, by a one-to-one assignment of the w
generators from S to the edges of Dw (see Fig.
2). Thus we can consider the lifted Tanner complex
T (Γ; h) := D(T (h); γ), where γ is the corresponding voltage assignment map: γ(ei) := si, i∈ [w].
It is not hard to check that the boundary map ˆ∂ of this lifted complex acts on its bases as follows:
ˆ∂(ei⊗ g) = hiv1⊗ g + hiv2⊗ sig, i ∈ [w].
Let us remind that the chain complex T (Γ; h) is a G-module.
Let us ﬁx a graph Γ = Cay 2(G, S) and two parity-check matrices h∈ Fr×w
q , h′∈ Fr′×w
q . We
can deﬁne the following 3-term chain complexes using the G-lifted product construction:
C•(Γ; h, h′) :=T (Γ; h)⊗GT ∗(Γ; h′),
C′
•(Γ; h, h′) :=T (Γ; h)⊗GT (Γ; h′).
Remark 5. Let ¯X w−1,t = Cay 2(G, Sw−1,t) be the w-regular graph from Example 1, where G =
PSL(F2
t ). Consider the chain complexes C•( ¯X w−1,t; h, h′) andC′
•( ¯X w−1,t; h, h′) respectively. In the
current work, we use the ﬁrst complex to show the existence of two asymptotically good families of
codes: quantum LDPC codes and classical LTCs. However, as we can see from Theorem
1, the rate
of the obtained LTCs is bounded above by 1 /2. We conjecture 20 that the complex C′
•( ¯X w−1,t; h, h′)
can be used to obtain asymptotically good LTCs of rate arbitr ary close to 1. For example, if
h, h′∈ Fr×w
q , then the rate of the classical codes ker ∂2 obtained from C′
•( ¯X w−1,t; h, h′) is at least
1− 4r/w since we have w2|G| code symbols and 4 wr|G| parity-checks. Hence if the rate of the local
codes goes to 1, the same happens with the rate of the obtained LTCs.
1.6 Posets and incidence chain complexes
In this subsection, we consider based chain complexes I with integer coeﬃcients
21 and call the
elements from the corresponding distinguished basis ˜I cells. We say that I is an incidence chain
complex if the matrix of its boundary map ∂ contains only elements from {−1, 0, 1}, and for every
such a complex we also deﬁne its cell poset, which can be viewed as a combinatorial structure that
represents the incidence relation between the cells. In som e sense, one can view the cell poset with
the corresponding incidence chain complex 22 as an abstract cell complex (see, e.g. [ 53, Section 2.12]),
which generalizes the notion of an abstract simplicial comp lex and an abstract polytope [ 54].
Let X be a poset, i.e., a set with a partial order ⩽ . We say that an element a∈ X covers
an element b∈ X and write a≺ b or b≻ a if a < b , and there is no element c∈ X such that
20Note that a construction similar to this complex was used in [ 41] to produce asymptotically good classical LTCs.
21Chain complexes with integer coeﬃcient are often used in alg ebraic topology to study the integral homology
groups of CW-complexes
22In fact, if the reader is only interested in the codes over ﬁni te ﬁeld of even characteristic, then the signs in the
matrix ∂ are not relevant, and we can represent every abstract cell co mplex by the corresponding cell poset.
15

## PDF page 16

a < c < b . It is easy to see that any ﬁnite poset can be uniquely deﬁned b y its covering relation ≺
if we let a ⩽ b if‌f there exists a sequence c0≺ c1≺···≺ cn of elements from X such that c0 = a,
cn = b, and n ⩾ 0. Let C be a based chain complex over some ring 23 R. We can deﬁne the partial
order ⩽ on the distinguished basis ˜C if for every two cells c, c′∈ ˜C we put c′≺ c if‌f c′∈ supp ∂c.
We call the poset ˜C with the relation ⩽ the cell poset of C.
A graded poset is a poset X equipped with a map ρ : X→ Z called a rank function such that
for any a, b∈ X the following conditions hold:
1. if a ⩽ b then ρ(a) ⩽ ρ(b);
2. if a≺ b then ρ(b) = ρ(a) + 1.
If X is a ﬁnite graded poset, then it is not hard to see that it can be decomposed as
X = X(s)⊔ X(s + 1)⊔···⊔ X(t),
where the subset X(i) :={a∈ X| ρ(a) = i} is called the i-th level of X, i∈ [s, t]∩ Z. It is clear
that all the elements from X(s) (resp. X(t)) are minimal (resp. maximal) elements in X. It is also
trivial to check that the cell poset ˜C of a based (co)chain complex C is a graded poset, where the
levels correspond to the cells of the same dimension.
Another example of a graded poset, often studied in the conte xt of HDXs, is an ( abstract)
simplicial complex on a ﬁnite non-empty set V , which is deﬁned as a closed under taking subsets
family X⊆ 2V . In this case, the partial order ⩽ is just the set inclusion relation ⊆, and ρ(x) :=
|x|− 1 for every x∈ X. The elements x∈ X with ρ(x) = i are called i-dimensional faces or just
i-faces. The highest dimension of the faces from the simplicial comp lex X is called its dimension.
Let us note that a simple graph can be represented as a 1-dimen sional simplicial complex, where the
0-faces and the 1-faces correspond respectively to the vert ices and the edges of the graph. Hence
we can also view an undirected graph Γ as the graded poset with the levels V (Γ) and E(Γ), where
for every v∈ V (Γ) and e∈ E(Γ) we have v≺ e whenever v is incident to e. In fact, 2-level posets
are equivalent to the incidence systems, and thus can be used to represent undirected multigraphs
and hypergraphs as well.
In this work, it is convenient to deﬁne objects such as graphs , incidence systems, and simplicial
complexes by the corresponding based chain complexes over Z. In some way, we can view such
complexes with integer coeﬃcients as a vast generalization of these objects. For example, for
any 2-level poset X with the levels V and E, we can deﬁne the based chain complex C•(X) :=(
ZE ∂1
−→ZV
)
with the distinguished bases ˜C0 := V , ˜C1 := E, where
∂e :=
∑
v≺e
v∈V
v.
The matrix of ∂1 is a zero–one matrix usually called the incidence matrix of X. For example,
since we view an undirected graph Γ as a 2-level poset, we can c onsider the corresponding chain
complexC•(Γ). Now let X be a simplicial complex with some ﬁxed linear order <V on its set of
vertices V = X(0). Then we can deﬁne the chain complex C•(X) by the following diagram
ZX(n) ∂n
−→··· ∂1
−→ZX(0) ∂0
−→ZX(−1),
23In this section, we are interested in only two cases: R = Z and R = Fq.
16

## PDF page 17

where for every k-face x = {v0, . . . , vk} ∈X such that v0 <V ··· <V vk the boundary map
∂ : ZX→ ZX is deﬁned as ∂x := ∑ k
i=0(−1)ix\{ vi}, and then extended by linearity to all chains
from ZX. As we can see, the integer coeﬃcients in the matrix of the bou ndary maps for C•(Γ)
andC•(X) are from the set {−1, 0, 1}. Let us call any based chain complex I with this property
24
an incidence complex. Let I be some incidence complex with a distinguished basis X. It is clear
that its boundary map ∂ : ZX→ ZX acts on a cell x∈ X as
∂x =
∑
x≻x′
x′∈X
[x : x′]x′, (5)
where the coeﬃcient [ x : x′]∈{− 1, +1} is called the incidence number for x, x′∈ X. It is also
convenient to assume that [ x : x′] = 0 whenever x̸≻x′. Let us note that since ∂2 = 0, then for
every x, x′′∈ X we obtain ∑
x≻x′≻x′′
x′∈X
[x : x′][x′ : x′′] = 0 . (6)
1.7 Products of graphs and posets
By interpreting objects like graphs, hypergraphs, or more g enerally abstract cell complexes as the
corresponding incidence complexes allows us to deﬁne the li fted product of such objects. We say
that a group G acts on a poset P if it acts on P as on a set, and for every g∈ G if x ⩽ y then
gx ⩽ gy (resp. xg ⩽ yg in the case of a right action). It is readily seen that an actio n of a group on
a graph Γ is also an action on Γ as a 2-level poset. Therefore if IX andIY are incidence complexes
with cell posets X and Y , respectively, where a group G acts freely (from the right on X and from
the left on Y ), then we can deﬁne the lifted product X×G Y of X and Y over G as the cell poset
of the complex IX⊗GIY . In fact, the lifted product X×G Y can be deﬁned for arbitrary ﬁnite
posets X and Y with a free action of a group G. Recall that if we have a free action of a group G
on a set S, then the size of each orbit is equal to |G|, and we can identify S with ( S/G)× G,
where S/G is the set of all orbits under the action of G. We deﬁne the poset X×G Y as the set
(X/G)× G× (Y /G) in terms of the covering relations as follows: we have ( x, g, y)≻ (x′, g′, y′) if‌f
either x = x′ and ( y, g)≻Y (y′, g′) or ( x, g)≻X (x′, g′) and y = y′. If the posets X and Y are
graded, then we can also deﬁne the rank function ρ(·) for X×G Y in terms of the rank functions
of X and Y as follows: ρ(x, g, y) := ρX (x, g) + ρY (y, g). If |G| = 1 we denote the poset X×G Y
simply by X× Y .
Remark 6. If X and Y are two graphs (considered as 2-level posets), then from the geometrical
point of view the poset X× Y corresponds to the direct product of X and Y (as topological graphs).
At the same time, the geometrical interpretation of the pose t X×G Y can be given in terms of
the balanced product
25 of graphs [ 18]. Note that the 1 -skeleton of X× Y , i.e., its restriction to
the ﬁrst two levels, is the 2-level poset representing the gr aph X ✷ Y , which is usually called the
Cartesian product of the graphs X and Y . Recall that for every G-lifted graph Γ the group G acts
24In fact, sometimes it is also convenient to consider arbitra ry integer coeﬃcients. But this more general case is
not covered here.
25A geometric realization of a graph can be considered as a topo logical space. The balanced product of two
topological spaces X and Y with a group G acting on the right on X and on the left on Y is the quotient space
X ×G Y := X × Y / ∼, where the equivalence relation ∼ is induced by ( xg, y ) ∼ (x, gy ) for x ∈ X, y ∈ Y , g ∈ G.
17

## PDF page 18

freely on Γ. Hence, we can also deﬁne the G-lifted Cartesian product ˆX ✷G ˆY for G-lifts ˆX, ˆY of
base graphs X, Y as the 1-skeleton of ˆX×G ˆY . It is not hard to check that the graph ˆX ✷G ˆY is
a|G|-fold cover for the standard Cartesian product X ✷ Y . Furthermore, if G is abelian, then this
cover is regular, i.e., ˆX ✷G ˆY is a G-lift of X ✷ Y .
Suppose that ˆΓ is a G-lift of some base graph Γ. Consider the cell poset ˜X := ˆΓ×G ˆΓ, and let
us represent its elements by triples x· g· y, where x, y∈ V (Γ)∪ E(Γ) , g∈ G. From the deﬁnition
of the poset ˜X it follows that x′· g′· y′≻ x· g· y if‌f one of the following conditions hold:
1. ˆx′
g′≻ˆΓ ˆxg and y = y′;
2. x = x′ and ˆy′
g′≻ˆΓ ˆyg;
where≻ˆΓ is the covering relation in the graph ˆΓ considered as a 2-level poset, i.e., its incidence
relation. It is convenient to interpret the poset ˜X as a 2-dimensional geometric object. An element
x· g· y∈ ˜X is called:
• a vertex if x∈ V (Γ) , y∈ V (Γ);
• a horizontal edge if x∈ E(Γ) , y∈ V (Γ);
• a vertical edge if x∈ V (Γ) , y∈ E(Γ);
• a face if x∈ E(Γ) , y∈ E(Γ),
and the corresponding subsets of elements are denoted as V = V ( ˜X), E→ = E→( ˜X), E↑ = E↑( ˜X),
and F = F ( ˜X). We also deﬁne the set E( ˜X) = E→( ˜X)∪ E↑( ˜X).
If P is a poset we denote by P ∗ the dual poset, i.e., x ⩽ P ∗ y whenever y ⩽ P x. In what follows,
we will also need a poset X := ˆΓ×G ˆΓ ∗, which is deﬁned on the same set as ˜X = ˆΓ×G ˆΓ but has
diﬀerent partial order and rank function. This means that the grading of X is diﬀerent from ˜X.
It is easy to check that the cell poset ˜X has 3 levels: ˜X(0) := V , ˜X(1) := E↑∪E→, and ˜X(2) := E→,
while the levels for X are as follows: X(0) := E↑, X(1) := F∪ V , and X(2) := E→.
Remark 7. As we will see in Section
2.3, the poset X = ˆΓ×G ˆΓ ∗ corresponds to the lifted product
complexT (Γ; h)⊗GT ∗(Γ; h′), which we use to show the main result. However the levels in t he
poset X do not correspond to the natural geometrical dimension of th e cells, and in the proof of our
main result it is more convenient to work with the poset ˜X = ˆΓ×G ˆΓ deﬁned on the same set as X,
but giving it a natural geometrical interpretation as a 2-di mensional complex. To this end we deﬁne
the incidence relation inc(·,·) on the set V∪ E→∪ E↑∪ F in a standard geometrical sense, i.e., we
assume that inc( x, y) if‌f x ⩽ y or y ⩽ x, where ⩽ is the partial order of the poset ˜X = ˆΓ×G ˆΓ. For
example, every face can be represented geometrically as a sq uare incident to two horizontal edges,
two vertical edges, and to four vertices. If x∈ X and S, T⊆ X, then we also use the following
notations:
Sx :={y∈ S| inc(x, y)},
ST :={y∈ S| inc(x, y) for some x∈ T}.
Hence Sx is the subset of the elements from X incident to x, and ST is the the subset of the
elements from S incident to some element from T . For example, Xv ={v}∪ Ev∪ Fv is the set of all
cells incident to v called the star of v, where Ev (resp. Fv) is the set of edges (resp. faces) incident
to v.
18

## PDF page 19

For the proof of our main result we will also need the 1-skelet on Λ := ˆΓ ✷G ˆΓ of ˆΓ×G ˆΓ with
the set of vertices V (Λ) := V ( ˜X) and the set of edges E(Λ) := E( ˜X).
Remark 8. In the proof of the main result in Section 2, when we mention sets V , E, E→, E↑, F or
a graph Λ, we refer to the corresponding sets and the graph deﬁ ned for the poset ˆΓ×G ˆΓ in this
section unless otherwise stated.
1.8 Local systems
In this subsection, we consider a generalization of based ch ain complexes with coeﬃcients from some
ﬁeld or ring to the complexes with local system of coeﬃcients , where the chains are formal linear
sums of cells with coeﬃcients in arbitrary abelian groups. I n fact, in this work, we are interested
in the case when all these abelian groups are vector spaces ov er the same ﬁnite ﬁeld Fq, and thus
the corresponding chain complexes can be still considered a s complexes of vector spaces over Fq.
In some sense, a complex with local coeﬃcients gives us a high -level view of the corresponding
complex over Fq.
Let X be some ﬁnite set, which we are going to use as an index set. If a vector space C is
the direct sum ⨁
x∈XFx of a collection of vector spaces F = (Fx)x∈X, then we can consider the
elements ofC as formal sums ∑
x∈X axx of elements from X, where for every x∈ X the coeﬃcient
ax is from the vector space Fx called the local coeﬃcient space of x. In such cases, we also denote
the vector space C byFX or by AX when all the local coeﬃcient spaces are equal to the same
space A. If each local coeﬃcient space Fx comes with a distinguished basis ˜Fx, then we assume
that the distinguished basis for FX is the set{ax| a∈ ˜Fx, x ∈ X}, in which case we say that FX
is based.
Deﬁnition. Given a poset X we say thatF is a local system of coeﬃcients for X if to each x∈ X
we assign a vector space Fx, and to each x, x′ ∈ X where x ⩾ x′ we assign an Fq-linear map
Fx→x′ :Fx→F x′ such that whenever x ⩾ x′ ⩾ x′′ we have:
Fx′→x′′◦F x→x′ =Fx→x′′.
Remark 9. Note that in the language of category theory we can view F as a functor from a poset
X to the category of vector spaces over Fq. Here we consider the poset X as a small category,
where the objects are the elements of X, and we have an arrow x→ x′ whenever x ⩾ x′.
Given an incidence chain complex I with some local system F on its cell poset X := ˜I, we
can consider the chain complex C•(I;F) as the vector space FX over Fq with the boundary map
∂ :FX→F X deﬁned on the elements ax∈F X, where a∈F x, x∈ X, as follows:
∂(ax) :=
∑
x≻x′
x′∈X
[x : x′]Fx→x′(a)x′,
and extended to all formal sums ∑
x∈X axx by linearity. It is easy to prove that ∂2 = 0. Indeed, it
is enough to check that
∂2(ax) := ∂
∑
x≻x′
x′∈X
[x : x′]Fx→x′(a)x′ =
∑
x≻x′≻x′′
x′,x′′∈X
[x : x′][x′ : x′′]Fx→x′′(a)x′′ = 0,
where the last step follows from (
6). Note that if FX is based, then the chain complex C•(I;F) is
also based.
19

## PDF page 20

Remark 10. With some small abuse of notation, we usually denote the comp lex C•(I;F) by
C•(X;F), in which case we always assume that the cell poset X comes with the correspond-
ing incidence complex I, i.e., for every two elements x ⩾ x′ from X their incidence number
[x : x′] ∈ {−1, +1} is deﬁned (cf. abstract cell complex from [ 53, Section 2.12]). In fact, in
the case of complexes over the ﬁelds of characteristic 2, we c an always assume that [ x : x′] = 1
if x ⩾ x′, and [ x : x′] = 0 otherwise. Hence, in such cases, the poset X completely deﬁnes the
corresponding incidence complex I by ( 5).
Consider a based chain complex C =C•(X;F) over Fq. Let a = ∑
x∈X axx∈C , where each
coeﬃcient ax is from the based vector spaceFx over Fq. We denote by wt(a) the standard Hamming
weight of a, considered as a vector over Fq. We also consider the block weight wtX(a) deﬁned as
the number non-zero blocks in a, viewed as a block vector ( ax)x∈X, i.e. we have
wtX(a) := card{x∈ X| ax̸= 0}.
Sometimes we need to take into account only the blocks that co rrespond to some subset S⊆ X.
In this case, we can deﬁne the block weight wtS(a) := card {x ∈ S | ax ̸= 0} relative to the
subset S ⊆ X. We also deﬁne supp a :={x∈ X | ax ̸= 0} and x|S := ∑
x∈S ax, where a =∑
x∈X axx.
Let ∂ :FX→F X be the boundary map ofC. In some cases, we want to restrict the domain and
codomain of ∂. For every S, T⊆ X we consider the map ∂S→T :FS→F T deﬁned as a↦→(∂a)|T .
From the deﬁnition it is clear that for every a∈F X we have:
(∂(a|S ))|T = ∂S→T (a|S ). (7)
As we already mentioned, local systems can be used to obtain a high-level view of a chain
complex over Fq. For example, we can represent a Tanner complex
T•(Γ; (∂(v))v∈V ) =
(
FqE ∂1
−→Fr
qV
)
for a graph Γ (considered as a 2-level poset) as the complex C•(Γ;F), where for every v∈ V we
haveFv := Fr
q, for every e∈ E we haveFe := Fq, and if e is incident to v thenFe→v := ∂(v)|Fqe.
In the next subsection, we show that the G-lifted product of two G-lifted Tanner complexes can
also be represented as a complex with a local system on the pos et ˆΓ×G ˆΓ ∗ from Subsection
1.7.
With some small abuse of terminology in what follows we call T anner complexes Tanner codes
and sometimes identify such a complex with the global code it deﬁnes.
2 Proof of the main results
2.1 Local minimality
One of the key ideas used in the proof of our main result is the i dea of local minimality. It was used
previously in the context of cohomology of simplicial compl exes with F2-coeﬃcients [
24, 37]. In the
current work, we extend this idea to a much more general conte xt of (co)homology of abstract cell
complexes with local systems of coeﬃcients. As we mentioned before, by an abstract cell complex
we mean a poset X with a map ∂ : ZX→ ZX such that ZX is an incidence complex with the
boundary map ∂, and X is its cell poset.
20

## PDF page 21

Consider an abstract cell complex X and a based chain complex C =C•(X;F) of vector spaces
···
∂i+1
− −− →Ci
∂i
−→Ci−1
∂i−1
−−−→···
over Fq, where F is a local system on X. Denote by |·| the block weight wtX (·), which makes
each term Ci in this complex a normed abelian group (see Appendix C) with the norm |·| and
allows us to deﬁne the distance in the standard way: d(a, b) := |a− b|, d(a,B) := min b∈B|a− b|.
We also use |·| to deﬁne for every i∈ Z the corresponding quotient norm on the i-th homology
group Hi(C) = Zi(C)/Bi(C) called the systolic norm by the formula |A| := min a∈A|a|, where
A∈ Hi(C), Bi(C) = im ∂i+1, Zi(C) = ker ∂i. This in turn allows us to deﬁne the distance on Hi(C)
as d(A,B) :=|A−B| and consider the minimal distance of Hi(C) given by the standard formulas:
d(Hi(C)) := min
A̸=B
A,B∈Hi(C)
d(A,B) = min
A∈Hi(C)\{Bi(C)}
|A| = min
a∈Zi(C)\Bi(C)
|a|.
Note that the minimal distance of Hi(C) is also called the i-systolic distance ofC, while the distance
d(Hi(C∗)) of the dual chain complex C∗ is called its i-cosystolic distance. These distances are related
to the minimal distance d(Q) of the quantum CSS code Q =Q(∂i, ∂∗
i+1) over Fq deﬁned by three
consecutive terms of the complex
Ci+1
∂i+1
− −− →Ci
∂i
−→Ci−1.
It is easy to see that d(Q) ⩾ min(d(Hi(C)), d(Hi(C∗))), where we have the equality if Fx = Fq
for all x∈ X since the block Hamming weight wtX(·) is less than or equal to the corresponding
Hamming weight wt(·).
Deﬁnition. We say that an i-chain c ∈ Ci, i ∈ Z, is locally minimal (with respect to X) if
|c + ∂ax| ⩾ |c| for all x∈ X(i + 1) and a∈F x. We also deﬁne the value
d(i)
LM(C) := min{|c|| c∈ Zi(C)\{ 0}, c is locally minimal},
which we call the i-th locally minimal distance ofC. If we do not have non-zero locally minimal
i-cycles, then we assume that d(i)
LM(C) =∞.
Note that in general the locally minimal distance d(i)
LM(C) is not equal to the minimal distance
of Zi(C) since the codewords of minimal weight from Zi(C) are not necessarily locally minimal. For
example, in the context of w-limited qLDPC codes where |∂x| ⩽ w for every x∈ X(i + 1), and
thus we have ∂x∈ Zi(C) and d(Zi(C)) ⩽ w, one can see that the codeword c = ∂x is not locally
minimal since|c− ∂x| = 0 <|c|.
The next lemma connects the locally minimal distance of the c omplex to the properties of the
corresponding quantum and classical codes obtained from it . The ﬁrst assertion can be used to
obtain the lower bound on the minimal distance d(Q) of the corresponding quantum CSS code Q,
while the second one can be used to show that the space Zi+1(C) is a locally testable code.
Lemma 1. LetC =C•(X;F) be a chain complex, where F is a local system on X. Then for every
i∈ Z we have
d(Hi(C)) ⩾ d(i)
LM(C),
and for every chain c∈C i+1 such that |∂c| < d (i)
LM(C) we have
|∂c| ⩾ d(c, Zi+1(C)). (8)
21

## PDF page 22

Proof. By deﬁnition we have
d(Hi(C)) =|c0|, where c0 := arg min
c∈Zi(C)\Bi(C)
|c|.
Since the element c0 has the minimal norm in the coset c0 + Bi(C), it is also locally minimal. Hence
we have d(Hi(C)) =|c0| ⩾ d(i)
LM(C).
We prove the second claim by induction on |∂c|. If |∂c| = 0 then d(c, Zi+1(C)) = 0, and ( 8) is
true. Consider c∈C i+1 such that 0 <|∂c| < d (i)
LM(C). Since ∂c∈ Zi(C) and|∂c| < d (i)
LM(C), we see
that ∂c cannot be locally minimal, and hence there exists a∈F x where x∈ X(i + 1) such that
|∂(c+ax)| ⩽ |∂c|− 1. Therefore by the induction hypothesis we have |∂(c+ax)| ⩾ d(c+ax, Zi+1(C)).
Thus we obtain
d(c, Zi+1(C)) ⩽ d(c + ax, Zi+1(C)) +|ax| ⩽ |∂(c + ax)| +|ax|
=1
⩽ |∂c|,
which completes the proof of the second claim.
2.2 Graph expansion
For any graph Γ we denote by Γ 2 the graph with V (Γ 2) = V (Γ) and A(Γ 2) = ( A(Γ)) 2, i.e., the
number of edges connecting two vertices in Γ 2 is equal to the number of length 2 paths connecting
them in Γ. In this section, we prove several technical lemmas to establish expanding properties
of the graphs Λ and Λ 2, where Λ is the graph deﬁned in Subsection
1.7. If Γ = ( V, E) is a graph
(possibly with multiple edges), and S, T ⊆ E, then by EΓ (S, T ), we denote the set of oriented
edges from S to T , i.e. EΓ (S, T ) :={(s, e, t)| e∈ E; s∈ S, t∈ T ; s↔e t} (every edge connecting
s, t∈ S∩ T is counted twice). We also usually write E(S, T ) and E(S) instead of EΓ (S, T ) and
EΓ (S) if the graph Γ is clear from the context.
Deﬁnition. We say that a graph Γ is an ( n, w, λ)-expander if it is a simple w-regular graph on
n vertices such that λ = λ(G).
Let us now state without proof a well-known variant of the exp ander mixing lemma for ( n, w, λ)-
regular graphs [ 47, Lemma 2.5].
Lemma 2 (Expanding mixing lemma) . If Γ = ( V, E) is an (n, w, λ)-expander graph, then for every
S, T⊆ V we have: ⏐
⏐
⏐
⏐|E(S, T )|− w|S|| T|
n
⏐
⏐
⏐
⏐ ⩽ λ
√
|S|| T|.
In what follows, it will be convenient to deﬁne a property cal led ( a, λ)-edge-expansion, which
captures the edge expansion on small sets of vertices in a gra ph.
Deﬁnition. We say that a graph Γ is ( a, λ)-edge-expanding if for any S, T ⊆ V (Γ) such that
|S|,|T| ⩽ a the following condition holds:
|E(S, T )| ⩽ λ
√
|S||T|.
Lemma 3. If Γ is an (n, w, λ)-expander graph, then it is (λn/w, 2λ)-edge-expanding.
22

## PDF page 23

Proof. If Γ is a w-regular, then from Lemma 2 it follows that for any S, T ⊆ V (Γ) such that
|S|,|T| ⩽ λn/w we have
⏐
⏐
⏐|E(S, T )|− w |S||T |
n
⏐
⏐
⏐ ⩽ λ
√
|S||T|. Hence we have:
|E(S, T )| ⩽ w|S||T|
n + λ
√
|S||T| ⩽
( λn
w · w
n + λ
) √
|S||T| = 2λ
√
|S||T|,
and the Lemma is proved.
Lemma 4. If ˆΓ is a G-lift of an (a, λ)-edge-expanding base graph Γ , then ˆΓ is (a,|G|· λ)-edge-
expanding.
Proof. Consider subsets ˆS, ˆT⊆ V (ˆΓ) such that | ˆS|,| ˆT| ⩽ a, and let S, T⊆ V (Γ) be their projec-
tions26 to the base graph Γ. Since each edge of Γ is the projection of m =|G| edges from ˆΓ, then
using the edge-expansion of the base graph Γ we have:
|E( ˆS, ˆT )| ⩽ m|E(S, T )| ⩽ mλ
√
|S||T| ⩽ mλ
√
| ˆS|| ˆT|.
Lemma 5. Every graph ¯X w−1,t from Example 1 is (n/√w, 8√w)-edge-expanding, where n = t(t2−
1) is the number of its vertices.
Proof. Since the Ramanujan graph X w−1,t is an ( n/2, w, 2√w)-graph, then by Lemma 3 it is
(n/√w, 4√w)-edge-expanding. Moreover, since the graph ¯X w−1,t is a 2-lift of X w−1,t, then by
Lemma 4 it is ( n/√w, 8√w)-edge-expanding.
Remark 11. In what follows, we are going to use the following properties of ( a, λ)-edge-expansion,
which are easy to prove.
1. If a′ ⩽ a, λ′ ⩾ λ, and the graph Γ is ( a, λ)-edge-expanding, then Γ is ( a′, λ′)-edge-expanding.
2. If a graph Γ = ( V, E) is ( a, λ)-edge-expanding, and Γ ′ = ( V, E′) is a subgraph of Γ (i.e.
E′⊆ E), then Γ ′ is also ( a, λ)-edge-expanding.
3. If graphs Γ 1, . . . ,Γ m are ( a, λ)-edge-expanding, then their disjoint union Γ = Γ 1⊔···⊔ Γ m is
also ( a, λ)-edge-expanding.
4. If graphs Γ 1, . . . ,Γ m have the same set of vertices, and Γ i is ( ai, λi)-edge-expanding, then
their union Γ = Γ 1∪···∪ Γ m is (min i∈[m] ai, ∑ m
i=1 λi)-edge-expanding.
Lemma 6. Let x1, ..., xn∈ R+, y1, ..., yn∈ R+ be sequences of non-negative real numbers. Then
min
i∈[n]
xiyi ⩽ ¯x¯y,
where ¯x = 1
n
∑ n
i=1 xi, ¯y = 1
n
∑ n
i=1 yi.
26The projection of a vertex ( v, g ) ∈ V (˜Γ) is the vertex v ∈ V (Γ).
23

## PDF page 24

Proof. By the Cauchy–Schwarz inequality for the vectors ( √xi)n
i=1 and (√
yi)n
i=1 we have
n∑
i=1
√
xiyi ⩽
( n∑
i=1
xi
) 1/2
·
( n∑
i=1
yi
) 1/2
= n√¯x¯y.
Therefore min i∈[n]
√xiyi ⩽ √¯x¯y, and ﬁnally we get
min
i∈[n]
xiyi =
(
min
i∈[n]
√xiyi
) 2 ⩽ ¯x¯y.
Lemma 7. If a w-regular graph Γ is (a, λ)-edge-expanding, then the graph Γ 2 is (a/w, 2λ2(1+ln w))-
edge-expanding.
Proof. Let S, T⊆ V (Γ) and |S|,|T| ⩽ a/w. There are at most w|S| ⩽ a vertices adjacent to the
vertices from S. Let v1, v2, . . . be the sequence of the vertices incident to S in the decreasing order
of the number of length 2 paths from S to T that goes through each of these vertices. Consider
the set Uj ={v1, . . . , vj} of size j ⩽ a. By the edge-expansion property of the graph Γ we have
|EΓ (Uj, S)| ⩽ λ
√
j|S|, |EΓ (Uj, T )| ⩽ λ
√
j|T|.
Hence, using Lemma 6 with n = j, xi =|EΓ ({vi}, S)|, yi =|EΓ ({vi}, T )| the number of length 2
paths through the vertex vj is
xjyj = min
i∈[j]
xiyi ⩽ |EΓ (Uj, S)|
j ·|EΓ (Uj, T )|
j ⩽ λ2√
|S||T|
j .
On the other hand, the degree of each vertex in Γ is w, and hence the total number of pairs of edges
incident to each vertex is w2. Hence, if we let µ := λ2√
|S||T|, then the total number of length 2
paths from S to T can be estimated as
|EΓ 2(S, T )| ⩽
⌊µ⌋∑
j=1
min
(
w2, µ/j
)
= w2· µ
w2 + µ
⌊µ⌋∑
j=⌈µ/w2⌉
1
j
< µ(2 + ln µ− ln(µ/w2)) = 2 µ(1 + ln w) = 2 λ2(1 + ln w)
√
|S||T|.
Above we truncate the summation at j =⌊µ⌋ since for j > µ the number of length 2 paths going
through the vertex vj is less or equal to min( w2, µ/j) < 1, and therefore is equal to 0. Thus there
exist at most 2 λ2(1 + ln w)
√
|S||T| edges from S to T in Γ 2, and Γ 2 is ( a/w, 2λ2(1 + ln w))-edge-
expanding.
2.3 Proof outline
In this subsection, we give some deﬁnitions and an informal i dea of the proof of our main results.
Let ˆΓ = ( ˆE, ˆV ) be a G-lift of some base graph Γ. We assume that ˆΓ is a w-regular ( a, λ)-edge-
expanding simple graph with n vertices. For example, we can use an inﬁnite family of graphs
¯X w−1,t from Example
1, where by Lemma 5 we have a = n/√w, λ = 8√w.
24

## PDF page 25

id⊗ ∂B∗id⊗ ∂B∗
∂A⊗ id
∂A⊗ id
v
V
E↑
E→
F
id⊗ h′∗id⊗ h′∗
h⊗ id
h⊗ id
v
E↑v
E→v
Fv
Figure 3: High-level view of the tensor product complex A⊗B ∗, whereA∈ T(Dw; h),B∈ T(Dw; h′),
and w = 8 (on the right); and its part that corresponds to the elemen ts from X incident to the
vertex v (on the left).
Let h∈ Fr×w
q , h′∈ Fr′×w
q be some full rank matrices, and A∈ TG(ˆΓ , h),B∈ TG(ˆΓ , h′) be the
corresponding G-lifted Tanner codes:
A =
(
Fq ˆE
∂A
− − →Fr
q ˆV
)
, B =
(
Fq ˆE
∂B
− − →Fr′
q ˆV
)
.
Now since G acts freely on A andB, we can consider their G-lifted product complex C :=A⊗ GB∗
over Fq shown below:
Fq ˆE⊗G Fr′
q ˆV
 
C2
∂2
−→
CF
  
Fq ˆE⊗G Fq ˆE⊕
CV
  
Fr
q ˆV⊗G Fr′
q ˆV
 
C1
∂1
−→Fr
q ˆV⊗G F2 ˆE
 
C0
.
It is convenient to represent C as the the chain complex C•(X,F), whereF is the local system
on X := ˆΓ×G ˆΓ ∗. Since the poset X has three levels: X(2) = E→, X(1) = F∪ V , and X(0) = E↑,
it is not hard to see that C•(X,F) has the following form:
Fr′
q E→
  
C2
∂2
−→
CF

FqF⊕
CV
  
Fr×r′
q V  
C1
∂1
−→Fr
qE↑

 
C0
,
where we identify Fr
q⊗ Fr′
q with Fr×r′
q .
Remark 12. As we can see, C•(X;F) gives us a high-level representation of the complex C. For
example, on the left of Fig.
3 you can ﬁnd a graphical representation of the tensor product complex
A⊗B ∗, whereA∈ T(Dw; h),B∈ T(Dw; h′), and w = 8. For simplicity we consider in this example
the tensor product instead of the G-lifted product. On the right of Fig. 3 you can see the “part”
of this complex corresponding to the faces and edges inciden t to one particular vertex v∈ V .
25

## PDF page 26

Now we consider the classical code Z2(C) = ker ∂2 and the quantum code Q(C) := Q(∂1, ∂∗
2 ),
and show that for some suﬃciently large number w we can choose the matrices h, h′ such that Z2(C)
andQ(C) satisfy the requirements of Theorems 1 and 2, respectively. The most diﬃcult part of the
proof is to show that Z2(C) is locally testable, and Q(C) has linear minimum distance. However,
from Lemma 1 it easily follows that if C has the locally minimal distance d(1)
LM(C) = Θ( n) as n→∞ ,
then both Z2(C) and Q(C) have the desired properties. Therefore we need to show that for every
locally minimal 1-cycle c∈ Z1(C) such that|c| = o(n) as n→∞ we have c = 0, where|c| = wtX (c)
is the block weight of c.
Let us ﬁx some non-zero locally minimal 1-cycle c = ∑
x∈X(1) cxx∈ Z1(C). Hence we have c̸= 0
and ∂c = 0. We have c = cF + cV , where cF := c|F and cV := c|V . Below we give a number of
important deﬁnitions used in the rest of the paper. Note that some of them depend on the ﬁxed
1-cycle c. However, for brevity, we usually do not mention c.
Deﬁnition. An element x∈ X(1) (a vertex or a face) is called active if cx̸= 0. A vertical edge
e∈ E↑ is called active if it is incident to an active vertex or an active face. Furthe rmore, e is called
face-active if it is not incident to any active vertex (only to an active fa ce).
We also need another type of vertices we call labeled that include active vertices as a special
case. However, the number of the labeled vertices is O(|c|), and we can still use the expansion
properties of the graphs involved in the proof. We deﬁne the s et of labeled vertices as the minimal
set of vertices such that:
1. every active vertex is labeled;
2. every vertex of a face-active edge adjacent to at least m labeled vertices is labeled.
We also consider 2 types of labeled vertices:
1. a vertex is called m-edge-expanding if there are at least m edges connecting it to the labeled
vertices in Λ;
2. a vertex is called s-face-expanding if there are at least s edges connecting it to the labeled
vertices in Λ 2.
In the proof outlined below, we consider classical codes tha t are duals of the product codes.
In Subsection
2.4 we deﬁne a special property of such codes called ( s, m, β)-product-expansion.
Informally speaking, this property corresponds to the loca l expansion in the complex C. In some
sense, it plays a role similar to the role of the minimal dista nce of the local codes in the classical
proof of Sipser and Spielman from [ 32], where it is shown that expander codes have linear minimum
distances.
Fix ε := 1 /6, and put m := w1/2+ε, s := w1+ε. From Lemma 10 it follows that we can ﬁnd
a suﬃciently large number w and choose matrices h and h′ with w columns such that both pairs
(im h∗, ker h′) and (ker h, im h′∗) are ( s, 2m, β)-product-expanding.
In the proof, we often use expansion properties of the graphs Λ and Λ 2, where Λ := ˆΓ ✷G ˆΓ
is the graph deﬁned in Subsection 1.7. Using the edge expansion of ˆΓ we show in Lemma 11
that Λ is (Θ( n), λ′)-edge-expanding where λ′ = Θ( w1/2). We also show in Lemma 12 that Λ 2 is
(Θ( n), λ′′)-edge-expanding, where λ′′ = Θ( w ln w).
Suppose that |c| = o(n), i.e., the number of the active vertices and faces is relati vely small.
Then the proof by contradiction contains the following step s.
26

## PDF page 27

1. Since each labeled vertex is either active itself or incid ent to an active face, then the number
of the labeled vertices is O(|c|) = o(n). Hence we can use the expansion properties of the
graphs Λ and Λ 2 for subsets of labeled vertices.
2. Using the expansion properties of the graph ˆΓ it is possible to show that each face-active edge
is incident to a labeled vertex (Lemma 14).
3. Note that, by deﬁnition, each labeled non-active vertex i s m-edge-expanding.
4. Using local minimality of c and ( s, 2m, β)-product-expansion of (im h, ker h′) we can show
that each active vertex is either m-edge-expanding or s-face-expanding (Lemma 15—the key
lemma).
5. From the previous 2 items we have that each labeled vertex i s either m-edge-expanding or
s-face-expanding (Corollary 1).
6. Thus using the expansion properties of Λ and Λ 2 we obtain a contradiction (Lemma 16):
(a) from the (Θ( n), λ′)-edge expansion of Λ we obtain that the ratio of the m-edge-expanding
labeled vertices is Θ( λ′/m) < 1/2 for a suﬃciently large w since λ′ = Θ( w1/2) and
m = Θ( w1/2+ε);
(b) from the (Θ( n), λ′′)-edge expansion of Λ 2 we obtain that the ratio of the s-face-expanding
labeled vertices is Θ( λ′′/s) < 1/2 for a suﬃciently large w since λ′′ = Θ( w ln w) and
s = Θ( w1+ε);
(c) the ratio of the labeled vertices that are either m-edge-expanding or s-face expanding is
less than 1, which can be true only when the 1-cycle c is zero.
Since we obtained a contradiction, we have that |c| = Θ( n), i.e., the locally minimal distance
d(1)
LM(C) = Θ( n) as n→∞ , which is in turn of the same order as the length of the classic al or
quantum codes obtained from the chain complex C. Hence by Lemma
1 we get what we need.
2.4 Local expansion
In this section, we consider the dual code to the classical pr oduct code [
55, 56] and study its
expansion properties 27. Such codes are related to the local expansion properties of the G-lifted
product of two Tanner codes. Let ker h⊆ Fw
q and ker h′⊆ Fw
q be linear codes with parity-check
matrices h and h′ respectively. Consider the code C = ker( h⊗ h′)⊆ Fw
q ⊗ Fw
q . We will identify
the elements of Fw
q ⊗ Fw
q with the corresponding matrices x = ( xi
j)w
i,j=1∈ Fw×w
q , where xi is the
i-th row, and xj is the j-th column. Note that the matrix h⊗ h′ is also a generator matrix for
the product of the codes (ker h)⊥ = im h∗ and (ker h′)⊥ = im h′∗ with the generator matrices h, h′
respectively, which means that C is the dual to this product code.
Remark 13. Using matrix representation, it is not hard to check that the codewords of C are
precisely the matrices x∈ Fw×w
q such that h′xh∗ = 0. Therefore if x∈C then every row of the
matrix s↑ := h′x is a codeword from ker h and every column of the matrix s→ := xh∗ is a codeword
from ker h′ (see Fig.
4).
27The property we consider is similar to the robust testability property of tensor product codes, often studied in
the literature on LTCs [ 28, 34].
27

## PDF page 28

Deﬁnition. A codeword x∈C = ker(h⊗ h′) is called ∆ -minimal if the following conditions hold:
1. wt(xi) ⩽ d(xi, ker h) + ∆ for all i∈ [w],
2. wt(xj) ⩽ d(xj, ker h′) + ∆ for all j∈ [w],
which means that we cannot decrease the weight of the matrix x by more than ∆ if we add
any codeword from ker h (resp. ker h′) to some row (resp. column) of x. A pair of codes (ker h, ker h′)
is called ( s, m, β)-product-expanding if for each non-zero βw-minimal codeword x∈C and for each
A, B⊆ [w] such that |A|,|B| ⩾ w− m we have wtA×B(x) ⩾ s, where wtA×B(x) := wt(x|A×B).
In this section, we often use the following short-hand notat ions: xI := x|I×[w], xJ := x|[w]×J,
and xI
J := x|I×J , where x∈ Fw×w
q , I, J⊆ [w].
Lemma 8. Let h∈ Fr×w
q , h′∈ Fr′×w
q be parity-check matrices such that min(d(ker h), d(ker h′)) ⩾ d,
and x = (xi
j)w
i,j=1∈ Fw×w
q be a d/3-minimal codeword of ker(h⊗ h′). If there exist A, B⊆ [w] such
that|A| > w− d/3,|B| ⩾ w− d + 1 and xB
A = 0 or xA
B = 0, then x = 0.
h′ h′
h
h
s→
s↑ 0
0B
< d
A< d/3
− δ
h′ h′
h
h
s′
→
0 0
0
0
A′
Figure 4: Idea of the proof.
Proof. Suppose that xB
A = 0 for some A, B⊆ [w] such that |A| > w− d/3,|B| ⩾ w− d + 1 (shown
on the left of Fig.
4). Since |A| > w − d(ker h),|B| > w − d(ker h′), there exist information 28
sets A′⊆ A, B′⊆ B of the codes ker h and ker h′ respectively. Let g be the generator matrix in
systematic form 29 for the information set A′. Consider matrices δ := xA′g and x′ := x− δ.
Let us show that x′
A = 0. Since δA′ = xA′, we have x′
A′ = 0. On the other hand, δh∗ = xA′gh∗ =
0, and hence
h′x′h∗ = h′(x− δ)h∗ = h′xh∗− h′δh∗ = 0.
Therefore ( h′x′)h∗ = 0, and each row of h′x′ is a codeword from ker h. The condition x′
A′ = 0
implies that ( h′x′)A′ = 0, and since A′ is an information set of ker h, we get h′x′ = 0, which means
28An information set for a linear code C ⊆ Fn
q is a smallest by inclusion index set I ⊆ [n] such that for every c ∈ C
if c|I = 0 then c = 0. It is clear that for every S ⊆ [n] such that |S| > n − d(C) if for some codeword c ∈ C we have
c|S = 0 then c = 0. Hence there should exist an information set I ⊆ S.
29A generator matrix g is in systematic form for an information set I if the submatrix gI is the identity matrix.
28

## PDF page 29

that every column of x′ is a codeword of ker h′ (shown on the right of Fig. 4). Since xB′
A = 0
and xB′
A′ = 0, we have δB′
= xB′
A′ g = 0, and therefore x′B′
A = xB′
A − δB′
A = 0. Now since B′ is
an information set of ker h′, x′B′
A = 0, and h′x′
A = 0, we have x′
A = 0.
Suppose δ̸= 0. In this case, there exists i∈ [w] such that δi̸= 0. Taking into account that δi∈
ker h, we obtain wt(δi) ⩾ d. But since x′
A = 0, and|A| > w− d/3, we have wt(x′i) ⩽ w−| A| < d/3,
and thus wt(xi) ⩾ wt(δi)− wt(x′i) > 2d/3 > wt(x′i) + d/3, which contradicts the d/3-minimality
of x. Thus δ = 0, which implies that x′ = x and h′x = 0, hence d(xj, ker h′) = 0 for all j∈ [w]. By
d/3-minimality of x we have wt(xj) ⩽ d/3 < d (ker h′), therefore xj = 0 for all j∈ [w], i.e. x = 0.
Hence we showed that xB
A = 0 implies x = 0. Thus to prove the lemma it remains to show that
xA
B = 0 also implies x = 0, which can be shown in a similar way.
Lemma 9. Let h ∈ Fr×w
q , h′ ∈ Fr′×w
q , d = min( d(ker h), d(ker h′)), m ⩽ d/6. Suppose x ∈
ker(h⊗ h′) is a d/3-minimal non-zero codeword such that wtA×B(x) < s for some A, B⊆ [w],
|A| =|B| = w− m. Then rk h′x ⩾ 5
36· d2
s .
Proof. By Lemma 8 each submatrix of w− d + 1 columns of x must have at least d/3 nonzero rows,
and each submatrix of w− d + 1 rows of x must have at least d/3 nonzero columns. In particular,
x has at least d nonzero columns and at least d nonzero rows. Indeed, otherwise we would have at
least w− d + 1 zero rows or columns, which contradicts what we said earli er.
Let k = rk h′x, and {h′ ˜x1, . . . , h′ ˜xk} be a generating set for the column space of h′x with the
minimal total weight wtA(˜x) := wtA(˜x1) +··· + wtA(˜xk), where ˜x is a matrix with the columns
˜x1, . . . , ˜xk. Without loss of generality we assume that wtA(˜x1) ⩽ ··· ⩽ wtA(˜xk).
Let us show that | ⋃ k
j=1 supp ˜xj| ⩾ d/3. Denote U = ⋃ k
j=1 supp ˜xj. Suppose |U| < d/ 3. Since
| ⋃ w
i=1 supp xi| ⩾ d, there is a column xi such that supp xi̸⊆U , hence xi̸∈im ˜x. However h′xi∈
im h′ ˜x, and hence there exists some y∈ ker h′\{ 0} such that xi + y∈ im ˜x. Since supp( xi + y)⊆ U ,
we have wt(xi + y) < d/ 3 and wt(xi) ⩾ wt(y)− wt(xi + y) > 2d/3 > wt(xi + y) + d/3, which
contradicts the d/3-minimality of x, and hence our assumption is wrong, and |U| ⩾ d/3.
We have
k∑
i=1
wtA(˜xi) ⩾
⏐
⏐
⏐
k⋃
i=1
(supp ˜xi∩ A)
⏐
⏐
⏐ =|U∩ A| =|U\ ([w]\ A)| ⩾ |U|− (w−| A|)
 
m
⩾ d
3− m ⩾ d
6 .
Let k′ be the minimal number such that ∑ k′
j=1 wtA(˜xj) ⩾ d/6, then wtA(˜xk′) ⩾ d
6k′ ⩾ d
6k . Put
U0 = ⋃ k′−1
j=1 supp ˜xj. Each column xi is uniquely represented as xi = yi + ˜xai where yi∈ ker h′,
ai∈ Fk
q . If supp ai⊆ [k′− 1], then
wt(˜xai) ⩽ m + wtA(˜xai) ⩽ m +
k′−1∑
j=1
wtA(˜xj) < d/3,
and hence yi = 0, otherwise wt(xi) ⩾ d− wt(˜xai) > 2d/3 ⩾ wt(xi + yi) + d/3 which contradicts
the d/3-minimality of x. Therefore supp xi⊆ U0.
Since every w− d + 1 columns of x have at least d/3 nonzero rows, there are at most w− d
columns xi such that supp ai ⊆ [k′− 1]. Hence there exists a set C ⊆ [w] of size d such that
max(supp ai) ⩾ k′ for all i∈ C. Note that if j = max(supp ai), then wtA(xi) ⩾ wtA(˜xj). Indeed,
29

## PDF page 30

otherwise we can replace ˜xj by xi and reduce wtA(˜x), which contradicts the minimality of wtA(˜x).
Hence wt(xi) ⩾ wtA(˜xk1) ⩾ d
6k for all i∈ C, and therefore
wtA×B(x) ⩾ wtA×(B∩C)(x) =
∑
i∈B∩C
wtA(xi) ⩾ d|B∩ C|
6k .
Since|B∩ C| =|C\ ([w]\ B)| ⩾ |C|− (w−| B|) = d− m, we have
k ⩾ d|B∩ C|
6wtA×B(x) ⩾ d(d− m)
6s ⩾ 5
36· d2
s , (9)
and the lemma is proved.
Lemma 10. Let ε∈ (0, 1/4), α > 0, γ > 0, R1∈ (0, 1), R2∈ (0, 1). Then there exist β > 0 and
δ > 0 such that for random 30 matrices h∈ F⌊R1w⌋×w
q , g′∈ F⌊R2w⌋×w
q the following three conditions
hold with high probability as w→∞ :
1. min(d(ker h), d(im g′∗)) ⩾ δw;
2. the matrices h and g′ have full rank;
3. the pair of codes (ker h, im g′∗) is (αw1+ε, γw1/2+ε, β)-product-expanding.
Proof. Let us start the proof by saying that the ﬁrst two conditions f ollows from the probabilistic
proof of the asymptotic Gilbert-Varshamov bound 31. Indeed, it is enough to choose δ ⩽ (q− 1)/q
such that Hq(δ) = min( R1/2, (1− R2)/2), where
Hq(x) := x logq(q− 1)− x logq x− (1− x) logq(1− x)
is the q-ary entropy function .
Now put r1 :=⌊R1w⌋, r2 :=⌊R2w⌋, d := δw, β := δ/3, and let us ﬁx a full-rank matrix
g′∈ Fr2×w
q such that d(im g′∗) ⩾ d. In the rest of the proof, we will consider all the probabilit ies
conditioned on this choice of g′.
Let h′∈ F(w−r2)×w
q be a parity-check matrix of the code im g′∗, and consider the code C :=
ker(h⊗ h′). The entries of the matrix h are independent uniformly distributed elements of Fq. Now
we estimate the probability that the code C has a codeword of some particular form. Recall that
we interpret elements of Fw
q ⊗ Fw
q as w× w matrices over Fq. In this interpretation every x∈C
satisﬁes the condition h′xh∗ = 0. Hence, for x∈C we have
0 = h′xh∗ = s↑h∗ (10)
where s↑ = h′x. Let us remind that for matrix u∈ Fa×b
q by ui we denote the i-th column of u and
by uj we denote the j-th row of u.
When h′ and x are ﬁxed, then (
10) deﬁnes a system of linear equations on the elements of the
matrix h. To estimate the number of solutions we need to estimate the r ank of this system. For all
j∈ [r2] we have hj∈ ker s↑. Hence, the probability that the equation ( 10) satisﬁed is q−r2 rk s↑.
30We suppose that the entries of the both matrices are chosen un iformly and independently at random from Fq.
31Note that the probabilistic proof of the Gilbert–Varshamov bound can be used with a random code deﬁned either
by a random parity-check matrix or a random generator matrix . See [ 57] for a good review of this bound.
30

## PDF page 31

Put β = d
3w = δ/3, m = γw 1/2+ε and suppose w is suﬃciently large such that m ⩽ d/6.
By Lemma 9 for every βw-minimal non-zero codeword x∈C such that wt(x) ⩽ αw1+ε we have
rk h′x ⩾ 5
36· d2
αw1+ε = c1w1−ε where c1 = 5δ2
36α . So, to summarize, we proved that if (ker h, ker h′) is
not ( αw1+ε, m, β)-product-expanding, and m ⩽ δw/6, then one of the following three cases is true:
1. d(ker h) < δw ;
2. d(ker h′) < δw ;
3. there exist subsets A, B ⊆ [w], |A| = |B| = w− m and a matrix x ∈ Fw×w
q such that
wt(x|A×B) < αw 1+ε, rk h′x ⩾ c1w1−ε, and equation ( 10) is satisﬁed.
For every i∈{ 1, 2, 3} let pi be the probability that the i-th case above holds if we choose the
matrices h and g′ uniformly at random. Recall that we have already chosen δ such that p1→ 0
and p2→ 0 as w→∞ . Hence to complete the proof we also need to show that p3→ 0 as w→∞ .
To estimate the probability p3 we need to estimate the number of ways one can choose the matri x
x such that the third case above holds. It is clear that we have
1.
( w
m
) 2 < w 2m choices for the subsets A and B;
2. less than q2mw choices for the elements of x at the positions from [ w]× [w]\ A× B;
3. less than
( w2
αw1+ε
)
qαw1+ε
< (qw)2αw1+ε
choices for the elements of x at the positions from A×B.
Totally, we have N choices of vector x, where
logq N ⩽ logq
(
q2mww2m(qw)2αw1+ε
)
= 2γw 3/2+ε + 2γw 1/2+ε logq w + 2αw1+ε(1 + logq w).
For each choice of the vector x the probability that (10) is satisﬁed equals to q−r2 rk hx < q −c1r2w1−ε
=
q−c2w2−ε
where c2 = c1(1− R2). Thus, by the union bound, the probability p3 is bounded from
above by N q−c2w2−ε
, and we get
logq p3 ⩽ logq N− c2w2−ε ⩽ γw 3/2+ε + 2γw 1/2+ε logq w + 2αw1+ε(1 + logq w) − c2w2−ε
  
main term
.
It is easy to see that log q p3 →−∞ as w→∞ for any constants ε < 1/4, α > 0, γ > 0. If
w is large enough then m = γw 1/2+ε < δw/ 6. Hence the probability p that (ker h, ker h′) is not
(αw1+ε, m, β)-product-expanding is bounded from above by p1 + p2 + p3→ 0 as w→∞ , and the
lemma is proved.
2.5 Global expansion
In this subsection, the graph Λ is the graph from Subsection
1.7.
Lemma 11. The graph Λ is (a, 2λ)-edge-expanding.
Proof. Since E = E→∪ E↑, we can split the graph Λ as Λ = Λ →∪ Λ ↑, where
Λ → := V∪ E→ ={x· g· y| x∈ V (Γ)∪ E(Γ) , y∈ V (Γ) , g∈ G},
31

## PDF page 32

Λ ↑ := V∪ E↑ ={x· g· y| x∈ V (Γ) , y∈ V (Γ)∪ E(Γ) , g∈ G}.
In terms of graphs, Λ → is the subgraph of Λ containing only horizontal edges, and Λ ↑ is the subgraph
of Λ containing only vertical edges. It is easy to see that
Λ → =
⨆
y∈V (Γ)
Λ (y)
→ , Λ ↑ =
⨆
x∈V (Γ)
Λ (x)
↑ ,
where
Λ (y)
→ ={x· g· y| x∈ V (Γ)∪ E(Γ) , g∈ G},
Λ (x)
↑ ={x· g· y| y∈ V (Γ)∪ E(Γ) , g∈ G}.
Since the graphs Λ (x)
↑ and Λ (y)
→ are isomorphic to ˆΓ, they are ( a, λ)-edge-expanding. Hence, by
property 3 of the edge expansion (see Remark 11), their disjoint unions Λ → and Λ ↑ have the
same edge expansion. Therefore by property 4 of the edge expansion their union Λ is ( a, 2λ)-edge-
expanding.
Lemma 12. The graph Λ 2 is (a/2w, 8λ2(ln w + 2))-edge-expanding.
Proof. By Lemma 11 graph Λ is ( a, 2λ)-edge-expanding. From the deﬁnition of Λ it is easy to see
that Λ is a 2 w-regular graph. Hence by Lemma 7 the graph Λ 2 is ( a/2w, 8λ2(1 + ln(2 w)))-edge-
expanding. Since ln(2 w) < ln w + 1, we obtain the assertion of the lemma.
In the rest of this subsection, we assume that c is some ﬁxed locally minimal 1-cycle in the
complexC•(X;F) from Subsection 2.3.
Lemma 13. If ∂c = 0 , then each face-active vertical edge is incident to at least d(ker h) active
faces.
Proof. Consider a face-active vertical edge e. Then Fe is the set of faces incident to e, and Ve is
the set of (two) vertices incident to e. Since e is face-active, c|Ve = 0 but c|Fe̸= 0. Since ( ∂c)|e
depends only on c|Fe and c|Ve , then using (
7) we have
0 = ( ∂c)|e = (∂(c|Fe + c|Ve
=0
))|e = ∂Fe→e(c|Fe)
Since ∂Fe→e∼ h, c|Fe̸= 0, and ∂Fe→e(c|Fe) = 0, we have that the number of active faces incident
to the edge e is
wt(c|Fe) ⩾ d(ker ∂Fe→e) = d(ker h),
and the lemma is proved.
Lemma 14. If d(ker h) ⩾ 2m + λ, ∂c = 0 and wtX(c) ⩽ a/w, then every active edge is incident
to a labeled vertex.
Proof. The number of active vertical edges is at most wtX(c)w ⩽ a. Let S⊆ E↑ be the set of
active edges that are not incident to a labeled vertex, A⊂ E↑ be the set of all active edges. If
an active edge is not incident to labeled vertices, then it is not incident to active vertices (every
active vertex is labeled), then by deﬁnition it is face-acti ve, hence S is a subset of face-active edges.
32

## PDF page 33

Consider the subposet Λ ✷ = E↑∪F of the poset X. Since each face from F is incident to exactly
two vertical edges from E↑, Λ ✷ can be interpreted as a graph with V (Λ ✷) = E↑ and E(Λ ✷) = F .
We have
Λ ✷ ={x· g· y| x∈ V (Γ)∪ E(Γ) , y∈ E(Γ) , g∈ G} =
⨆
y∈E(Γ)
Λ (y)
✷
where
Λ (y)
✷ ={x· g· y| x∈ V (Γ)∪ E(Γ) , g∈ G}≃ ˆΓ .
By property 3 of edge expansion Λ ✷ has the same edge expansion as ˆΓ, i.e. it is ( a, λ)-edge-
expanding. The sets S and A can be interpreted as sets of vertices of graph Λ ✷. From the edge
expansion of Λ ✷ we have|EΛ ✷ (S, S)| ⩽ λ|S|.
On the other hand, by Lemma 13 since each edge e∈ S is face-active, it is incident to at least
d = d(ker h) active faces, hence in the graph Λ ✷ it is adjacent to at least d ⩾ 2m + λ active edges,
therefore|EΛ ✷(S, A)| ⩾ (λ + 2m)|S|. Thus
|EΛ ✷ (S, A\ S)| =|EΛ ✷ (S, A)|−| EΛ ✷ (S, S)| ⩾ (λ + 2m)|S|− λ|S| = 2m|S|.
Suppose,|S|̸= ∅ . Then there exists an edge e∈ S adjacent to 2 m edges e1, . . . , e2m∈ A\ S in Λ ✷.
By the deﬁnition of A and S each of the edges ei is incident to some labeled vertex xi, which is
adjacent to one of the two vertices of e in Λ. Hence, there are 2 m diﬀerent labeled vertices adjacent
to one of the vertices of the edge e, and therefore one of these vertices is adjacent to at least m
labeled vertices, therefore it is labeled by deﬁnition. Thi s contradicts the fact that the edge e is
from S and cannot be incident to labeled vertices. Hence S = ∅ , and the lemma is proved.
In the next lemma, we need the following deﬁnition.
Deﬁnition. For a given vector y∈ Fr
q and a parity-check matrix h∈ Fr×w
q we say that a vector
x∈ Fw
q is an ( y, h)-coset leader if it has the minimal possible Hamming weight among the vecto rs
from{x∈ Fw
q | hx = y}.
Lemma 15. Suppose the pair of codes (ker h, im h′∗) is (s, 2m, β)-product-expanding, h′ has full
rank, βw ⩾ 4m + 3, d = min( d(ker h), d(im h′∗)) ⩾ 4m, and m ⩾ max(4s/d, λ). If c is a locally
minimal 1-cycle, and wtX(c) ⩽ a/w, then for each active vertex v one of the following conditions
holds:
1. v is m-edge-expanding (i.e., it is adjacent to at least m labeled vertices in Λ );
2. v is s-face-expanding (i.e., it is adjacent to at least s labeled vertices in Λ 2).
Proof. Before we start, let us ﬁx some active vertex v = v′· g· v′′; v′, v′′∈ V (Γ), g∈ G. Let
y = c|v∈ Fr×r′
q v, f = c|Fv∈ FqFv. Then it is not hard to see that
E→v ={e′· g′· v′′∈ E→| ˆe′
g′≻ˆΓ ˆv′
g},
E↑v ={v′· g′′· e′′∈ E↑| ˆe′′
g′′≻ˆΓ ˆv′′
g},
Fv ={e′· g′g−1g′′· e′′∈ F| ˆe′
g′≻ˆΓ ˆv′
g, ˆe′′
g′′≻ˆΓ ˆv′′
g}.
Since|E→v| =|E↑v| = w, and each face from Fv is incident to one edge from E↑ and one edge from
E→, the set Fv is in natural one-to-one correspondence
32 with the set E→v× E↑v (see Fig. 5(a)).
32An equivalent way to express this property is to say that the 2 -dimensional complex ˜X = ˆΓ ×G ˆΓ is a complete
square complex [40], i.e., a square complex where the link of each vertex is isom orphic to a complete bipartite graph.
33

## PDF page 34

N↑(v)
E↑v
E→v v
Fv
(a) Star of the vertex v in ˆΓ ×G ˆΓ ∗
A
J3
J2
J1
B
f̸= t:
|fi| ⩾ d
2
f = t:
|fi| =|ti|
(b) Case when v is s-face-expanding
Figure 5: Local expansion for the vertex v
Therefore we can represent the restriction f = c|Fv as a w× w matrix with the rows and columns
indexed by the edges from E↑v and E→v respectively, i.e., f∈ FqFv∼
= Fq(E→v× E↑v). Deﬁne the
set
N↑(v) :={v′∈ V| v↔e v′, e ∈ E↑},
which consists of the vertices connected to v by vertical edges. Note that the set of elements
from X(1) = V ∪ F incident to the elements from E↑v ⊆ X(0) is equal to VE↑v∪ FE↑v , where
VE↑v = N↑(v)∪{ v} and FE↑v = Fv. Hence we obtain
(∂c)|E↑v =
(
∂(c|v + c|Fv + c|N↑(v))
)
|E↑v = ∂v→E↑v

 
id⊗∂(v′′)
B
∗
(y) + ∂Fv→E↑v
  
∂(v′)
A ⊗id
(f ) + ∂N↑(v)→E↑v (c|N↑(v)).
SinceA∈ TG(ˆΓ; h),B ∈TG(ˆΓ; h′), we have ∂(v′)
A ∼ h and ∂(v′′)
B ∼ h′, therefore with a proper
ordering of the edges in Ev we can identify ∂v→E↑v with Ir⊗ h′∗ and ∂Fv→E↑v with h⊗ Iw. Consider
zv := (Ir⊗ h′∗)y, zF := (h⊗ Iw)f , and zN := ∂N↑(v)→E↑v (c|N↑(v)). Then we have
0 = ( ∂c)|E↑v = zv + zF + zN .
Since each vertex v′∈ N↑(v) is connected to v by a single vertical edge 33, we have that|E↑v∩E↑v′| =
1, supp ∂v′→E↑v (c|v′ )⊆ E↑v′∩ E↑v, and hence wtX(∂v′→E↑v(c|v′ )) ⩽ wtX(c|v′ ) ⩽ 1. Therefore we
33Here we use the assumption from Subsection 2.3 that ˆΓ is simple. In fact, the lemma can also be proved in the
case of multiple edges in ˆΓ.
34

## PDF page 35

get
wtX (zN ) = wtX
( ∑
v′∈N↑(v)
∂v′→E↑v(c|v′ )
)
⩽
∑
v′∈N↑(v)
wtX
(
∂v′→E↑v (c|v′ )
)
⩽
⩽
∑
v′∈N↑(v)
wtX(c|v′ ) = wtN↑(v)(c).
Note that wtN↑(v)(c) is the number of active vertices adjacent to v by vertical edges. If wtX (zN ) ⩾
m, then wtN↑(v)(c) ⩾ m, and hence v is m-edge-expanding and the lemma is proved.
In the rest of the proof, we consider the most complex case whe n wtX (zN ) < m. Let A⊆ E→v
(resp. B⊆ E↑v) be the set of horizontal (resp. vertical) edges connecting v with the unlabeled
vertices. Each pair of edges in A× B determines a face incident to v and not incident to the
labeled vertices adjacent to v in Λ. To prove the s-face expansion of v, ﬁrst we need to show
that wtA×B(f ) ⩾ s. If |A| ⩽ w− m or|B| ⩽ w− m, then there are at least m labeled vertices
adjacent to v in Λ, hence v is m-edge-expanding. In the rest of proof, we consider the case w hen
|A|,|B| > w− m.
It this case, we have wtX(zF + zv) = wtX(zN ) < m . Let zv = ( z1
v , . . . , zw
v ) = ( Ir⊗ h′∗)y,
t = ( t1, . . . , tw)∈ Fw
q ⊗ Fw
q , where for each i∈ [w] the vector ti is some ( zi
v, h)-coset leader. Then
(h⊗ Iw)t = zv, and
(h⊗ g′)t = (Ir⊗ g′)zv = (Ir⊗ g′h′∗)y = 0,
where g′ is a parity-check matrix for the code im h′∗. Hence t∈ ker(h⊗ g′).
Consider f ′ = f + t = ( f ′1, . . . , f′w). We call the component f ′i the i-th row of f ′. We have
(h⊗ Iw)f ′ = zF + zv. For each i∈ [w] we have one on the following cases:
1. i̸∈B: the corresponding vertical edge connects v with an active vertex;
2. i∈ B and f ′i̸= 0: in this case hf ′i = 0, i.e. f ′i∈ ker h\{ 0}, hence|f ′i| ⩾ d;
3. i∈ B and f ′i = 0: in this case f i =−ti, hence wt(f i|A) = wt(ti|A).
Denote by J1, J2, and J3 the sets of indices corresponding to these cases (see Fig.
5(b)). For these
sets we have the following conditions:
[m] = J1⊔ J2⊔ J3, B = J2⊔ J3, |J1| < w.
There are two cases we need to consider:
1.|J3| < w− 2m. Then
|J2| = w−| J1|−| J3| > w− m− (w− 2m) = m ⩾ 4s/d.
Each of the rows f ′i for i∈ J2 has weight at least d. On the other hand, for each i∈ J2 since
ti is a ( zi
v, h)-coset leader and f ′i∈ ker h, we have wt(ti) ⩽ wt(ti + f ′i) = wt(f i), and hence
wt(f ′i) ⩽ wt(ti) + wt(f i) ⩽ 2wt(f i). Therefore wt(f i) ⩾ wt(f ′i)/2 ⩾ d/2. Thus we obtain
wt(f|A×B) ⩾ wt(f|A×J2) ⩾ |J2|
( d
2− (w−| A|)
)
⩾ 4s
d
( d
2− m
)
  
⩾ d/4
⩾ s.
35

## PDF page 36

unlabeled
E↑v
E→v vA
Figure 6: Active elements in the star of v: black circles—labeled vertices, green faces—active face s
from (E→v\A)×E↑v, blue faces—active faces from A×E↑v, thick black edges—active vertical edges
that are not incident to v. Each thick edge is incident to a labeled vertex which is the o pposite to
v in this face.
2.|J3| ⩾ w− 2m. Each row ti has the minimal weight in the coset ti + ker h since it is a ( zi
v, h)-
coset leader. Suppose that t is not a βw-minimal codeword. Then there exist a column tj
and a vector ∆ t∈ im h′∗ such that wt(tj + ∆ t) ⩽ wt(tj)− βw. Since tj|J3 = fj|J3, we have
wt(fj + ∆ t) ⩽ wt(fj + tj)  
⩽ w−|J3|⩽ 2m
+ wt(tj + ∆ t)  
⩽ wt(tj )−βw
⩽ 2m + wt(tj)  
⩽ wt(fj )+2m
−βw ⩽ wt(fj) + 4m− βw.
Taking into account that βw ⩾ 4m + 3, we have wt(fj + ∆ t) ⩽ wt(fj)− 3. Since ∆ t∈ im h′∗,
there exists u∈ Fr′
q such that ∆ t = h′∗u. Consider uej∈C 0, where ej∈ E→v is the j-th
horizontal edge such that v↔ej vj, i.e., ej is incident to the faces corresponding to the j-th
column of f . Then we get ∂ej→Fej∼ h′∗, and|Vej| = 2. Therefore we obtain
wtF (c + ∂(uej ))− wtF (c) = wt(c|Fej

=fj
+ ∂ej→Fej (uej)
  
=h′∗u=∆ t
)− wt(c|Fej ) ⩽ −3,
wtV (c + ∂(uej))− wtV (c) ⩽ | supp ∂(uej )∩ V| ⩽ |Vej| = 2,
and ﬁnally we see that
wtX(c + ∂(uej ))− wtX(c) ⩽ −1
which contradicts the local minimality of c. Hence our assumption is wrong, and t is a βw-
minimal codeword. Therefore from the ( s, 2m, β)-product-expansion property of (ker h, im h′∗)
we obtain wt(t|A×J3) ⩾ s, and it follows that
wt(f|A×B) ⩾ wt(f|A×J3) = wt(t|A×J3) ⩾ s.
Thus in both cases wt(f|A×B) ⩾ s. Each active face is incident to 2 active vertical edges. Sin ce
d ⩾ 4m > 2m + λ, the conditions of Lemma 14 satisﬁed, therefore each of these active edges is
36

## PDF page 37

incident to a labeled vertex. For an active face x∈ A× B one of its vertical edges is incident to the
vertex v; another vertical edge is incident to some labeled vertex vx which is not adjacent to v in Λ
by a horizontal edge, hence vx is the opposite vertex to v in the face x, i.e. it is connected to v by
a path of length 2 consisting of one horizontal and one vertic al edge in the graph Λ (see Fig. 6). It
is not hard to see that all these length 2 paths are diﬀerent (th ough some vertices vx may be equal),
and for each x∈ A× B the vertex vx is adjacent 34 to v in Λ 2. Thus v is s-face-expanding.
From Lemma 15 and the deﬁnition of the labeled vertices we obtain the follo wing result.
Corollary 1. Suppose the pair of codes (ker h, im h′∗) is (s, 2m, β)-product-expanding, βw ⩾ 4m+3,
d = min( d(ker h), d(im h′∗)) ⩾ 4m, and m ⩾ max(4s/d, λ). If c is a locally minimal 1-cycle, and
wtX (c) ⩽ a/w, then for each labeled vertex v one of the following conditions holds:
1. v is m-edge-expanding (i.e. it is adjacent to at least m labeled vertices in Λ );
2. v is s-face-expanding (i.e. it is adjacent to at least s labeled vertices in Λ 2).
Proof. If the vertex v is active, then the lemma assertion is true by Lemma 15. Otherwise, by
deﬁnition, the vertex v is adjacent to at least m active vertices in Λ, and hence it is m-edge-
expanding.
Lemma 16. Suppose the pair of codes (ker h, im h′∗) is (s, 2m, β)-product-expanding, βw ⩾ 4m + 3,
d = min( d(ker h), d(im h′∗)) ⩾ 4m, m ⩾ max(4s/d, 2λ′), and s ⩾ 2λ′′ where35 λ′ = 2 λ and λ′′ =
8λ2(ln w + 2). If c is a locally minimal 1-cycle, and wtX (c) ⩽ a
2w , then c = 0.
Proof. Let L be the set of labeled vertices. Then by Corollary 1 each vertex v∈ L is either m-edge-
expanding or s-face-expanding, i.e. L = Le∪ Lf where Le is the set of m-edge-expanding vertices,
Lf is the set of s-face-expanding vertices. By deﬁnition we have
|EΛ (Le, L)| ⩾ m|Le|, |EΛ 2(Lf , L)| ⩾ s|Lf|. (11)
Since each labeled vertex v is either active ( v∈ supp cV ) or incident to a face-active edge, and
hence adjacent to at least d active faces, we get
|L| ⩽ wtX(cV ) + 4wtX(cF )/d ⩽ wtX (cV ) + wtX(cF ) = wtX (c) ⩽ a
2w
Hence by ( a, λ′)-edge-expansion of Λ we have
|E(Le, L)| ⩽ λ′√
|L||Le|.
Similarly, from ( a/2w, λ′′)-edge-expansion of Λ 2 we obtain
|E(Lf , L)| ⩽ λ′′
√
|L||Lf|.
Taking into account ( 11), we obtain
m|Le| ⩽ λ′√
|L||Le|, s |Lf| ⩽ λ′′
√
|L||Lf|,
34Note that vx can be equal to v, which gives a loop in Λ 2.
35The parameters λ ′ and λ ′′ correspond to the edge expansion of the graphs Λ and Λ 2.
37

## PDF page 38

and hence
|Le| ⩽
( λ′
m
) 2
|L| ⩽ |L|
4 , |Lf| ⩽
( λ′′
s
) 2
|L| ⩽ |L|
4 .
Since|L| =|Le∪ Lf| ⩽ |L|/2, we obtain |L| = 0. Since each active vertical edge by Lemma 14
contains labeled vertices, we have that the number of active vertical edges is 0, and hence c = 0.
2.6 Proof of the theorems
Proposition 1. For every ﬁnite ﬁeld Fq, intervals (ρ0, ρ1), (ρ′
0, ρ′
1)⊆ (0, 1), constant µ > 0, and
inﬁnite set W⊆ N, there exist matrices h∈ Fr×w
q , h′∈ Fr′×w
q for suﬃciently large w∈ W such that
r/w∈ (ρ0, ρ1), r′/w∈ (ρ′
0, ρ′
1), and for every G-lifted w-regular (a, µ√
w)-edge-expanding simple
graph ˆΓ and Tanner codesA∈ TG(ˆΓ; h),B∈ TG(ˆΓ; h′) with a free action of a group G we have
d(1)
LM(A⊗ GB∗) ⩾ a/2w,
d(1)
LM(B⊗ GA∗) ⩾ a/2w.
Proof. Let w be a parameter which we will ﬁx later. Deﬁne ε := 1 /6, m := w1/2+ε, s := w1+ε,
r :=
⌊1
2 (ρ0 + ρ1)w
⌋
, r′ :=
⌊ 1
2 (ρ′
0 + ρ′
1)w
⌋
. By Lemma
10 with α := 1, γ := 2, there exist β1, β2 > 0
and δ1, δ2 > 0 such that for random matrices h∈ Fr×w
q , h′∈ Fr′×w
q as w→∞ the following three
conditions hold with high probability 36:
1. the matrices h and h′ have maximal rank, i.e. rk h = r, rk h′ = r′;
2. the pair (ker h, im h′∗) is ( s, 2m, β1)-product-expanding and min( d(ker h), d(im h′∗)) ⩾ δ1w;
3. the pair (im h∗, ker h′) is ( s, 2m, β2)-product-expanding and min( d(ker h′), d(im h∗)) ⩾ δ2w.
Therefore by the union bound for a suﬃciently large w0∈ N for every w ⩾ w0 there exists a pair
(h, h′) that satisﬁes these three conditions. Let β := min( β1, β2), d := min( δ1, δ2)w, λ := µ√w,
λ′ := 2λ, λ′′ := 8λ2(ln w + 2). We have
d = Θ( w), λ ′ = Θ( w
1
2 ) = o(m), λ ′′ = Θ( w ln w) = o(s), m = Θ( w
1
2 +ε) = o(w)
as w→∞ . Hence there exists w1 such that for every w ⩾ w1 the following inequalities hold:
d > 4m, βw ⩾ 4m + 3, m > max
( 4s
d , 2λ′
)
, s > 2λ′′. (12)
Since the set W is inﬁnite, we can take w := min{w∈ W| w ⩾ max(w0, w1)} and ﬁx some pair
(h, h′) that satisfy the conditions 1–3. Now consider a G-lifted ( a, λ)-edge-expanding graph ˆΓ and
some G-lifted Tanner codes A∈ TG(ˆΓ; h),B∈ TG(ˆΓ; h′).
Since min( d(ker h), d(ker h′), d(im h∗), d(im h′∗)) ⩾ d, and conditions ( 12) hold, we can apply
Lemma 16 to the pair of codes ( h, h′) and obtain that every non-zero locally minimal 1-cycle of t he
chain complexA⊗ GB∗ has the weight at least a/2w. Hence we have
d(1)
LM(A⊗ GB∗) ⩾ a/2w.
36Note that Lemma 10 is used here twice. First time h is interpreted as a parity-check matrix, but h′ as a generator
matrix, and the second time vice versa.
38

## PDF page 39

Since lemma 16 is also applicable to the pair ( h′, h), we have
d(1)
LM(B⊗ GA∗) ⩾ a/2w,
which completes the proof of the proposition.
Theorem 1. For every number R∈ (0, 1/2) and ﬁnite ﬁeld Fq it is possible to ﬁnd universal
constants s and ω such that there exists an explicit family of (ω, s)-locally testable classical LDPC
codes with the parameters [n, k ⩾ Rn, d = Θ( n)]q as n→∞ .
Proof. Fix some R∈ (0, 1/2) and put ε := (1 − 2R)/(6− 2R). Note that for any w from the
inﬁnite set W :={p + 1∈ N| p≡ 1 mod 4 and p is prime} there exist inﬁnite family of graphs
¯X w−1,t from Example 1. By Lemma 5 every graph ¯X w−1,t is ( n0(t)/√w, 8√w)-edge-expanding,
where n0(t) = t(t2− 1) =|V ( ¯X w−1,t)|. Consider the chain complex
C :=T ( ¯X w−1,t, h)⊗GT ∗( ¯X w−1,t, h′),
with the boundary operator ∂, where G := PSL( F2
t ), and h, h′ are the parity-check matrices of
the local codes, which we will ﬁx later. Let |·| be the block weight norm wtX(·) deﬁned on C,
considered as a chain complex with a local system on the cell p oset X = ¯X w−1,t×G ( ¯X w−1,t)∗. By
Proposition
1 for the intervals (1 − ε, 1), (0 , ε) and the parameter µ = 8 there exist w∈ W and
matrices h∈ Fr×w
q , h′∈ Fr′×w
q such that for every ¯X w−1,t we have
d(1)
LM(C) ⩾ n0(t)/2w√
w
where r/w > 1− ε, r′/w < ε . Let n := dimC2 and m := dimC1, then n = n0(t)rw, m =
1
2 n0(t)(w2 + 4rr′). Hence d(1)
LM(C) ⩾ n
2w2r√w > n
2w7/ 2 . By Lemma 1 for all c∈C 2 we have
|∂c| ⩾ min(d(1)
LM(C),|c + Z2(C)|).
Since|y| ⩽ wt(y) for y∈C and wt(c) ⩽ r|c| ⩽ w|c| for c∈C 2, taking into account that n ⩾
wt(c + Z2(C)) ﬁnally we obtain
wt(∂c) ⩾ min
( n
2w7/2 , wt(c + Z2(C))
w
)
⩾ 1
2w7/2 wt(c + Z2(C)).
We have
m
n = w2 + 4rr′
2rw = 1 + 4 r
w· r′
w
2r/w ⩽ 1 + 4ε
2(1− ε) = 1− R.
In particular, we have m < n , and hence
1
m wt(∂c) ⩾ w−7/2
2m wt(c + Z2(C)) ⩾ w−7/2
2n wt(c + Z2(C)).
Therefore the code Z2(C) is ( ω, s)-locally testable where ω := 2 w and s := 1
2 w−7/2. For the
dimension k = dim Z2(C) we have k ⩾ n− m ⩾ Rn.
To complete the proof we also need to show that the linear code Z2(C) has the minimal distance
Θ( n) as n→∞ . It is not hard to see that the minimal distance of Z2(C) is not less than the
distance of the component Tanner code T ( ¯X w−1,t, h), which is a classical expander code [ 32]. Thus,
as it follows from the proof of Proposition 1, we can ﬁx a suﬃciently large number w such that
d(ker h) > λ 2( ¯X w−1,t) and obtain that d(T ( ¯X w−1,t, h)) = Θ( n) as n→∞ .
39

## PDF page 40

Theorem 2. For every number R∈ (0, 1) and ﬁnite ﬁeld Fq there exists an explicit family of
quantum LDPC codes over Fq with the parameters /llbracketn, k ⩾ Rn, d = Θ( n)/rrbracketq as n→∞ .
Proof. Fix some R∈ (0, 1). Note that for every w from the inﬁnite set W :={p + 1∈ N| p≡ 1
mod 4 and p is prime} there exist inﬁnite family of graphs ¯X w−1,t from Example 1. By Lemma 5
the graph ¯X w−1,t is (n0(t)/√w, 8√w)-edge-expanding where n0(t) = t(t2− 1) =|V ( ¯X w−1,t)|. As in
the proof of Theorem 1, we consider the complex C =T ( ¯X w−1,t, h)⊗GT ∗( ¯X w−1,t, h′) with the
boundary operator ∂ where G = PSL(F2
t ). Let|·| be the block weight deﬁned onC. By Proposition
1
for ρ0 = ρ′
0 = 0, ρ1 = ρ′
1 = (1 − R)/4, and µ = 8 there exist w∈ W and matrices h∈ Fr×w
q ,
h′∈ Fr′×w
q such that for all ¯X w−1,t we have
d(1)
LM(C) ⩾ n0(t)/2w√
w, d (1)
LM(C∗) ⩾ n0(t)/2w√
w
where r/w < (1− R)/4, r′/w < (1− R)/4. Let n := dimC1, then n = 1
2 n0(t)(w2 + 4rr′) < w 2n0(t).
The chain complexC deﬁnes the quantum CSS codeQ =Q(HX , HZ) with the parity-check matrices
HX := ∂1 and HZ := ∂∗
2 . By Lemma 1 for the complex C we have
dX (Q) = d(H1(C)) ⩾ d(1)
LM(C) ⩾ n0(t)
2w√w > n
2w7/2 .
Similarly, since the dual chain complex C∗ is isomorphic 37 to the chain complex B⊗ GA∗, then by
Lemma 1 we have
dZ (Q) = d(H1(C∗)) ⩾ d(1)
LM(C∗) > n
2w7/2 ,
and hence d(Q) = min( dX (Q), dZ (Q)) ⩾ 1
2 n/w7/2. To complete the proof we also need to estimate
the dimension k = dim(H1(C)) of the quantum code Q. We have
dimC0 = n0(t)rw = 2n rw
w2 + 4rr′ < n(1− R)/2,
dimC2 = n0(t)r′w = 2n r′w
w2 + 4rr′ < n(1− R)/2,
and therefore
k = dim(H1(C)) ⩾ n− dimC0− dimC2 > n− n(1− R)/2− n(1− R)/2 = nR.
ThusQ is a w-limited quantum CSS code with the parameters /llbracketn, k ⩾ Rn, d ⩾ 1
2 n/w7/2/rrbracketq.
Conclusions
In this work, we showed that there exist asymptotically good families of quantum LDPC codes,
which proves the well-known qLDPC conjecture. We also conje cture that a decoder, similar to the
small-set-ﬂip decoding algorithm from [
26] (see also [ 24]), can be used to correct in linear time any
adversarial errors up to the constant fraction of the code le ngth.
The constructed qLDPC codes were obtained from the G-lifted product of two G-lifted Tanner
codes, and to obtain qLDPC codes of linear minimum distance a non-abelian group G was used.
37We say that two based chain complexes C and C′ over Fq are isomorphic if there exists a one-to-one Fq-linear
map f : C → C ′ such that f ( ˜Ci) = ˜C′
i for every i ∈ Z.
40

## PDF page 41

In fact, it is not hard to see that Proposition 1 implies that using the Cℓ-lifted product of two
Cℓ-lifted Tanner codes from [ 17], where Cℓ is the cyclic group of size ℓ = Θ( n/ log n), one can
obtain qLDPC codes with the parameters /llbracketn, k = Θ( n), d = Θ( n/ log n)/rrbracketq as n→∞ . Note that
very recent results on explicit Cℓ-lifted expander graphs from [ 58] implies that the construction of
these qLDPC codes can also be made explicit.
In addition, as a byproduct of our proof of the qLDPC conjectu re, we show that the second
homology groups of the constructed in this work chain comple xes can be used to obtain asymptot-
ically good families of classical LDPC codes, which are also locally testable with constant query
and soundness parameters. This resolves an important conje cture in the ﬁeld of locally-testable
codes38.
Though all the constructions we propose here can be consider ed as explicit, the constant size
local codes used in our expander codes are still obtained by p robabilistic methods. We think that
it is an interesting open problem to ﬁnd an explicit construc tion of such codes. One possible option
would be to use MDS codes such as Reed-Solomon codes. In fact, such non-binary local codes can
be used even if we want to get codes over F2 since every classical and quantum code over F2s can
be also considered as a code over F2, and the rate and minimal distance of such a code is at least
as good as for the non-binary one. However, it is not clear whe ther one can ﬁnd a pair of MDS
codes that satisﬁes the product-expansion property requir ed for our proof to work.
We also hope that some of the methods developed in the current work can be used to show the
existence of locally-testable qLDPC codes required to prov e the qLTC conjecture, which in turn
implies [ 59] the NLTS conjecture. A natural candidate for such a code wou ld be a 5-term chain
complex, where the three middle terms corresponds to a good q LDPC code, and the remaining
two terms represents its X- and Z-meta-checks (i.e., checks on checks). In fact, similar 5-t erm
complexes were already used in the context of single-shot de coding of qLDPC codes [ 60, Figure 1].
Acknowledgment
We would like to thank Nikolas Breuckmann and Jens Eberhardt for very helpful and insightful
discussions of possible ways to get good qLDPC codes, and for an opportunity to report our results
in the QCDA seminar. We want to express our gratitude to many p eople, including Thomas
Vidick, Sergey Sadov, Victor Albert, Shouzhen Gu, who read o ur manuscript and made a number
of valuable comments. We also want to thank anonymous review ers for indicating several unclear
places in our work and for pointing out the connection of our p roduct-expansion property to the
robust testability of tensor product codes.
This work was supported by the Ministry of Science and Higher Education of the Russian
Federation (Grant 075-15-2020-801).
References
[1] R. G. Gallager, Low-density parity-check codes. M.I.T. Press, Cambridge, MA, 1963.
[2] D. J. C. MacKay, G. Mitchison, and P. L. McFadden, “Sparse -graph codes for quantum error
correction,” IEEE Transactions on Information Theory , vol. 50, no. 10, pp. 2315–2330, Oct.
2004.
38An independent solution to this problem was also proposed in [41].
41

## PDF page 42

[3] T. Kaufman and M. Sudan, “Sparse random linear codes are l ocally decodable and testable,”
in 48th Annual IEEE Symposium on Foundations of Computer Science (FOCS’07), Oct. 2007,
pp. 590–600.
[4] D. Aharonov and L. Eldar, “Quantum locally testable code s,” SIAM Journal on Computing ,
vol. 44, no. 5, pp. 1230–1262, Jan. 2015.
[5] L. Eldar and A. W. Harrow, “Local hamiltonians whose grou nd states are hard to approximate,”
2017 IEEE 58th Annual Symposium on Foundations of Computer Sci ence (FOCS) , pp. 427–
438, Oct. 2017.
[6] O. Goldreich, “Short locally testable codes and proofs: A survey in two parts,” in Property
Testing: Current Research and Surveys , ser. Lecture Notes in Computer Science, O. Goldreich,
Ed. Berlin, Heidelberg: Springer, 2010, pp. 65–104.
[7] A. Leverrier, V. Londe, and G. Z´ emor, “Towards local tes tability for quantum coding,” Mar.
2021. [Online]. Available: http://arxiv.org/abs/1911.03069
[8] A. R. Calderbank and P. W. Shor, “Good quantum error-corr ecting codes ex-
ist,” Phys. Rev. A , vol. 54, pp. 1098–1105, Aug 1996. [Online]. Available:
https://link.aps.org/doi/10.1103/PhysRevA.54.1098
[9] A. M. Steane, “Error correcting codes in quantum theory, ” Phys. Rev. Lett. , vol. 77, pp.
793–797, Jul 1996. [Online]. Available: https://link.aps.org/doi/10.1103/PhysRevLett.77.793
[10] I. Dinur, “The PCP theorem by gap ampliﬁcation,” Journal of the ACM , vol. 54, no. 3, pp.
12–es, Jun. 2007.
[11] Y. Dikstein, I. Dinur, P. Harsha, and N. Ron-Zewi, “Loca lly testable codes via high-
dimensional expanders,” May 2020. [Online]. Available: http://arxiv.org/abs/2005.01045
[12] O. Goldreich and M. Sudan, “Locally testable codes and P CPs of almost-linear length,” in
The 43rd Annual IEEE Symposium on Foundations of Computer Scien ce, 2002. Proceedings.,
Nov. 2002, pp. 13–22.
[13] N. P. Breuckmann and J. N. Eberhardt, “Quantum low-dens ity parity-check codes,” PRX
Quantum, vol. 2, no. 4, p. 040101, Oct. 2021.
[14] D. Bacon, S. T. Flammia, A. W. Harrow, and J. Shi, “Sparse quantum codes from quantum
circuits,” IEEE Transactions on Information Theory , vol. 63, no. 4, pp. 2464–2479, 2017.
[15] T. C. Bohdanowicz, E. Crosson, C. Nirkhe, and H. Yuen, “G ood approximate quantum
ldpc codes from spacetime circuit hamiltonians,” in Proceedings of the 51st Annual
ACM SIGACT Symposium on Theory of Computing , ser. STOC 2019. New York, NY,
USA: Association for Computing Machinery, Jun. 2019, pp. 48 1–490. [Online]. Available:
https://doi.org/10.1145/3313276.3316384
[16] M. B. Hastings, J. Haah, and R. O’Donnell, “Fiber bundle codes: breaking the N 1/2 polylog(N )
barrier for quantum LDPC codes,” in Proceedings of the 53rd Annual ACM SIGACT Sympo-
sium on Theory of Computing . New York, NY, USA: Association for Computing Machinery,
Jun. 2021, pp. 1276–1288.
42

## PDF page 43

[17] P. Panteleev and G. Kalachev, “Quantum LDPC codes with a lmost linear minimum distance,”
IEEE Transactions on Information Theory , pp. 1–1, 2021.
[18] N. P. Breuckmann and J. N. Eberhardt, “Balanced product quantum codes,” IEEE Transac-
tions on Information Theory , vol. 67, no. 10, pp. 6653–6674, Oct. 2021.
[19] M. B. Hastings, “On quantum weight reduction,” Sep. 202 1. [Online]. Available:
http://arxiv.org/abs/2102.10030
[20] E. Dennis, A. Kitaev, A. Landahl, and J. Preskill, “Topo logical quantum memory,” Journal
of Mathematical Physics , vol. 43, no. 9, pp. 4452–4505, 2002.
[21] M. H. Freedman, D. A. Meyer, and F. Luo, “ Z2-systolic freedom and quantum codes,” in Math-
ematics of quantum computation , R. K. Brylinski and G. Chen, Eds. New York: Chapman
& Hall/CRC, 2002, ch. 12, pp. 287–320.
[22] J. Tillich and G. Z´ emor, “Quantum LDPC codes with posit ive rate and minimum distance
proportional to n1/2,” in 2009 IEEE International Symposium on Information Theory , June
2009, pp. 799–803.
[23] L. Guth and A. Lubotzky, “Quantum error correcting code s and 4-dimensional arithmetic
hyperbolic manifolds,” Journal of Mathematical Physics , vol. 55, no. 8, p. 082202, Aug. 2014.
[24] S. Evra, T. Kaufman, and G. Z´ emor, “Decodable quantum LDPC codes beyond the square root
distance barrier using high dimensional expanders,” in 2020 IEEE 61st Annual Symposium on
Foundations of Computer Science (FOCS) , Nov. 2020, pp. 218–227.
[25] T. Kaufman and R. J. Tessler, “New cosystolic expanders from tensors imply explicit Quantum
LDPC codes with Ω( √n logk n) distance,” in Proceedings of the 53rd Annual ACM SIGACT
Symposium on Theory of Computing . New York, NY, USA: Association for Computing
Machinery, Jun. 2021, pp. 1317–1329.
[26] A. Leverrier, J.-P. Tillich, and G. Z´ emor, “Quantum ex pander codes,” in 2015 IEEE 56th
Annual Symposium on Foundations of Computer Science , Oct. 2015, pp. 810–824.
[27] F. J. MacWilliams and N. J. A. Sloane, The Theory of Error-Correcting Codes , 1st ed. Am-
sterdam: North Holland Publishing Co., Jan. 1977.
[28] E. Ben-Sasson and M. Sudan, “Robust locally testable co des and products of codes,”
Random Structures & Algorithms , vol. 28, no. 4, pp. 387–402, 2006. [Online]. Available:
https://onlinelibrary.wiley.com/doi/abs/10.1002/rsa.20120
[29] J. Tillich and G. Z´ emor, “Quantum LDPC codes with posit ive rate and minimum distance
proportional to the square root of the blocklength,” IEEE Transactions on Information Theory ,
vol. 60, no. 2, pp. 1193–1202, Feb. 2014.
[30] K. S. Brown, “Some homological algebra,” in Cohomology of Groups , ser. Graduate Texts in
Mathematics, K. S. Brown, Ed. New York, NY: Springer, 1982, p p. 4–32.
43

## PDF page 44

[31] P. Panteleev and G. Kalachev, “Degenerate quantum ldpc codes with good ﬁnite
length performance,” Quantum, vol. 5, p. 585, Nov. 2021. [Online]. Available:
https://quantum-journal.org/papers/q-2021-11-22-585 /
[32] M. Sipser and D. Spielman, “Expander codes,” IEEE Transactions on Information Theory ,
vol. 42, no. 6, pp. 1710–1722, Nov. 1996.
[33] R. Tanner, “A recursive approach to low complexity code s,” Information Theory, IEEE Trans-
actions on , vol. 27, no. 5, pp. 533–547, 1981.
[34] I. Dinur, M. Sudan, and A. Wigderson, “Robust local test ability of tensor products of ldpc
codes,” in Approximation, Randomization, and Combinatorial Optimiza tion. Algorithms and
Techniques, ser. Lecture Notes in Computer Science, J. D ´ ıaz, K. Jansen , J. D. P. Rolim, and
U. Zwick, Eds. Berlin, Heidelberg: Springer, 2006, pp. 304– 315.
[35] A. Lubotzky, R. Phillips, and P. Sarnak, “Ramanujan gra phs,” Combinatorica, vol. 8, no. 3,
pp. 261–277, Sep. 1988. [Online]. Available: https://doi.org/10.1007/BF02126799
[36] G. A. Margulis, “Explicit group-theoretical construc tions of combinatorial schemes and their
application to the design of expanders and concentrators,” Problemy peredachi informatsii ,
vol. 24, no. 1, pp. 51–60, 1988.
[37] T. Kaufman, D. Kazhdan, and A. Lubotzky, “Ramanujan com plexes and bounded degree
topological expanders,” in 2014 IEEE 55th Annual Symposium on Foundations of Computer
Science, Oct. 2014, pp. 484–493.
[38] T. Kaufman and A. Lubotzky, “High dimensional expander s and property testing,” in Pro-
ceedings of the 5th conference on Innovations in theoretical computer science , ser. ITCS ’14.
New York, NY, USA: Association for Computing Machinery, Jan . 2014, pp. 501–506.
[39] R. Meshulam, “Graph codes and local systems,” Mar. 2018 . [Online]. Available:
https://arxiv.org/abs/1803.05643v1
[40] D. T. Wise, “Complete square complexes,” Commentarii Mathematici Helvetici , vol. 82, no. 4,
pp. 683–724, Dec. 2007. [Online]. Available: https://ems.press/journals/cmh/articles/1470
[41] I. Dinur, S. Evra, R. Livne, A. Lubotzky, and S. Mozes, “L ocally testable codes with constant
rate, distance, and locality,” Nov. 2021. [Online]. Availa ble: http://arxiv.org/abs/2111.04808
[42] S. Bravyi and M. B. Hastings, “Homological product code s,” in Proceedings of the forty-sixth
annual ACM symposium on theory of computing , ser. STOC ’14. New York, NY, USA: ACM,
2014, pp. 273–282.
[43] W. Zeng and L. P. Pryadko, “Higher-dimensional quantum hypergraph-product codes with
ﬁnite rates,” Physical Review Letters , vol. 122, no. 23, p. 230501, Jun. 2019.
[44] M. Hagiwara and H. Imai, “Quantum quasi-cyclic LDPC cod es,” in 2007 IEEE international
symposium on information theory , Jun. 2007, pp. 806–810.
[45] J. Haah, “Local stabilizer codes in three dimensions wi thout string logical operators,” Physical
Review A , vol. 83, no. 4, p. 042330, Apr. 2011.
44

## PDF page 45

[46] A. A. Kovalev and L. P. Pryadko, “Quantum kronecker sum- product low-density parity-check
codes with ﬁnite rate,” Physical Review A , vol. 88, no. 1, p. 012311, Jul. 2013.
[47] S. Hoory, N. Linial, and A. Wigderson, “Expander graphs and their applications,” Bull. Amer.
Math. Soc. , vol. 43, no. 04, pp. 439–562, Aug. 2006.
[48] J. Friedman, “A proof of Alon’s second eigenvalue conje cture,” in Proceedings of the
Thirty-Fifth Annual ACM Symposium on Theory of Computing , ser. STOC ’03. New York,
NY, USA: Association for Computing Machinery, 2003, pp. 720 –724. [Online]. Available:
https://doi.org/10.1145/780542.780646
[49] G. Davidoﬀ, P. Sarnak, and A. Valette, Elementary Number Theory, Group Theory and Ra-
manujan Graphs, ser. London Mathematical Society Student Texts. Cambridg e: Cambridge
University Press, 2003.
[50] A. Lubotzky, “High dimensional expanders,” in Proceedings of the International Congress of
Mathematicians (ICM 2018) . WORLD SCIENTIFIC, Jun. 2018, pp. 705–730.
[51] J. L. Gross and T. W. Tucker, Topological graph theory , ser. Wiley-Interscience Series in
Discrete Mathematics and Optimization. Wiley, 1987.
[52] N. Agarwal, K. Chandrasekaran, A. Kolla, and V. Madan, “ On the expansion of group-based
lifts,” SIAM Journal on Discrete Mathematics , vol. 33, no. 3, pp. 1338–1373, 2019. [Online].
Available: https://doi.org/10.1137/17M1141047
[53] P. J. Hilton and S. Wylie, “Homology theory of a simplici al complex,” in Homology Theory:
An Introduction to Algebraic Topology . Cambridge: Cambridge University Press, 1960, pp.
53–94.
[54] P. McMullen and E. Schulte, Abstract Regular Polytopes . Cambridge University Press, Dec.
2002.
[55] J. Wolf, “On codes derivable from the tensor product of c heck matrices,” IEEE Transactions
on Information Theory , vol. 11, no. 2, pp. 281–284, Apr. 1965.
[56] R. Chien and S. Ng, “Dual product codes for correction of multiple low-density burst errors,”
IEEE Transactions on Information Theory , vol. 19, no. 5, pp. 672–677, Sep. 1973.
[57] A. Barg and G. D. Forney, “Random codes: minimum distanc es and error exponents,” IEEE
Transactions on Information Theory , vol. 48, no. 9, pp. 2568–2573, 2002.
[58] F. G. Jeronimo, T. Mittal, R. O’Donnell, P. Paredes, and M. Tulsiani, “Explicit abelian lifts
and quantum ldpc codes,” Dec. 2021. [Online]. Available: http://arxiv.org/abs/2112.01647
[59] L. Eldar and A. W. Harrow, “Local hamiltonians whose gro und states are hard to approximate,”
in 2017 IEEE 58th Annual Symposium on Foundations of Computer Sci ence (FOCS) , Oct.
2017, pp. 427–438.
[60] E. T. Campbell, “A theory of single-shot error correcti on for adversarial noise,” Quantum
Science and Technology , vol. 4, no. 2, p. 025006, Feb. 2019. [Online]. Available:
https://doi.org/10.1088/2058-9565/aafc8f
45

## PDF page 46

[61] E. R. Berlekamp, Algebraic Coding Theory . New York: McGraw-Hill, 1968.
[62] N. Aydin, I. Siap, and D. K. Ray-Chaudhuri, “The structu re of 1-generator quasi-twisted
codes and new linear codes,” Designs, Codes and Cryptography , vol. 24, no. 3, pp. 313–326,
Dec. 2001.
[63] Y. Jia, “On quasi-twisted codes over ﬁnite ﬁelds,” Finite Fields and Their Applications , vol. 18,
no. 2, pp. 237–257, Mar. 2012.
[64] J. Lv, R. Li, and J. Wang, “Constructions of quasi-twist ed quantum codes,” Quantum Infor-
mation Processing, vol. 19, no. 8, p. 274, Jul. 2020.
[65] M. M. Deza and E. Deza, “Distances in algebra,” in Encyclopedia of Distances , M. M. Deza
and E. Deza, Eds. Berlin, Heidelberg: Springer, 2013, pp. 18 3–195.
A Chain complexes
Let F be a ﬁeld. We say that an n-dimentional vector space V over F is based if it comes with
some distinguished basis ˜V :={v1, . . . , vn}⊆ V . In this case we can naturally identify V with
the coordinate vector space Fn. Moreover, we can consider the standard inner product ⟨v, v⟩ deﬁned
on the basis as ⟨vi, vj⟩ := δij and extend it by linearity. This also allows us to identify th e dual
vector space V ∗ := Hom( V, F) with V and hence with Fn if for every v∈ V we let v(x) :=⟨v, x⟩.
Now consider an F-linear map ϕ : U → V between based vector spaces U ∼
= Fm and V ∼
= Fn.
We usually identify such maps with the corresponding m× n matrix over F. For every such map
ϕ : U→ V , we can consider the corresponding transpose map ϕ∗ : V ∗→ U ∗ that takes each linear
function f ∈ V ∗ to the function f◦ ϕ∈ U ∗. It is easy to check that the n× m matrix of the
transposed map ϕ∗ is the transpose of the matrix for ϕ.
Consider a ﬁeld F. A chain complex (over F) is a collection of vector spaces
39 (Ci)i∈Z over F,
which is convenient to consider as one big vector space C = ⨁
i∈ZCi, with some ﬁxed linear operator
∂ :C→C called the boundary map such that ∂Ci+1⊆C i and ∂2 = 0 for all i∈ Z. The condition
∂Ci+1⊆C i says that one can deﬁne the maps ∂i := ∂|Ci :Ci→C i−1, i∈ Z; while the condition
∂2 = 0 implies that ∂i◦∂i+1 = 0 for all i∈ Z or, equivalently, Bi(C)⊆ Zi(C), where Bi(C) := im ∂i+1,
Zi(C) := ker ∂i. Therefore for every i∈ Z we can deﬁne the quotient group Hi(C) := Zi(C)/Bi(C)
called the i-th homology group of the complexC. The elements from Ci, Zi(C), and Bi(C) are called
the i-chains, i-cycles, and i-boundaries ofC, respectively. We say that a complex C is based if every
spaceCi comes with a distinguished basis ˜Ci⊆C i, which elements are called i-cells. In this work
we consider only bounded chain complexes, i.e., when Ci = 0 for all i̸∈[s, t]. A bounded chain
complexC is usually represented by the following diagram:
Cs
∂s
−→Cs−1
∂s−1
−−−→···
∂t+1
−−−→Ct,
where t− s + 1 is called the length ofC. A complex of length n is also called an n-term complex.
The deﬁnition of a chain complex and the related terminology come from algebraic topology,
where an i-cell c∈ ˜Ci usually corresponds to some i-dimensional object, and ∂c is an algebraic
39In fact, the deﬁnitions given below also can be generalized t o the case when F is an arbitrary commutative ring.
In this case, instead of vector spaces over F one should consider free F-modules.
46

## PDF page 47

representation of its ( i− 1)-dimensional boundary. For example, one can consider for any simple
graph Γ = ( V, E) its 2-term chain complex C•(Γ; F2) over F2:
F2E
C1
∂1
−→F2V
C0
,
where ˜C0 := V , ˜C1 := E, and the boundary map ∂ is deﬁned as ∂e := v+v′, for every e ={v, v′}∈ E.
Sometimes it is also convenient to consider the dual notion o f a chain complex called cochain
complex. If we have a chain complex C we can obtain the corresponding cochain complex for C
if we replace C by its dual vector space C∗ := Hom(C, Fq), and the boundary map ∂ :C→C by
the corresponding coboundary map δ :C∗ →C ∗ that takes each linear function x↦→f (x)∈C ∗
to x ↦→f (∂x) ∈ C∗. Since ∂2 = 0, it follows that δ2 : x ↦→f (∂2x) is the zero map, and we
also get δ2 = 0. Moreover, since C = ⨁
i∈ZCi, we see that C∗ = ⨁
i∈ZCi and δ(Ci) ⊆ Ci+1,
whereCi := Hom(Ci, Fq), i∈ Z. Similar to the case of chain complexes, we can deﬁne the maps
δi := δ|Ci :Ci → Ci+1, and the condition δ2 = 0 implies that δi+1◦ δi = 0 for all i ∈ Z, or,
equivalently, Bi(C)⊆ Z i(C), where Bi(C) := im δi−1, Z i(C) := ker δi. Hence we have the spaces Ci,
Z i(C), and Bi(C) of i-cochains, i-cocycles, and i-coboundaries, respectively. Since for every i∈ Z
we have Bi(C)⊆ Z i(C), we can also deﬁne the quotient group H i(C) := Z i(C)/Bi(C) called the i-th
cohomology group ofC.
Since in the current work we always assume that each Ci comes with some distinguished basis ˜Ci,
we can identify both Ci andCi with the corresponding coordinate vector space Fni
q , where ni :=| ˜Ci|.
In this case, the maps ∂i : Fni
q → Fni−1
q and δi−1 : Fni−1
q → Fni
q can be also identiﬁed with the
corresponding matrices over Fq, and it is easy to verify that δi−1 is the transpose of ∂i.
Every chain (resp. cochain) complex can be also considered a s a cochain (resp. chain) complex
if we use the following convention Ci =C−i. Thus in what follows we are going to consider the
cochain complexC∗ also as the chain complex, in which case we call it the dual chain complex ofC.
For example, if we have a chain complex, corresponding to a qu antum CCS code Q with matrices
HX and HZ:
C•(HX, HZ ) :=


FmZ
q

C1
H ∗
Z
−−→Fn
q
C0
HX
−−→FmX
q

C−1


 ,
then its cochain complex is
C•(HX, HZ ) :=
(
FmZ
q
HZ
←−−Fn
q
H ∗
X
←−−FmX
q
)
and the dual chain complex for C is
C∗
• (HX, HZ ) :=
(
FmX
q
H ∗
X
−−→Fn
q
HZ
−−→FmZ
q
)
,
and we see that C∗
•(HX , HZ) =C•(HZ , HX), i.e., the dual chain complex corresponds to the dual
CSS code Q∗, where the roles of HX and HZ are reversed.
B Lifted product of two classical codes
The lifted product was introduced in [
17] as a way to generalize many known constructions [ 2, 29,
44–46] of qLDPC codes. The general idea was to lift the hypergraph product construction [ 29],
47

## PDF page 48

which, for any two classical codes with parity-check matric es A∈ Fma×na
q and B∈ Fmb×nb
q , gives
the quantum CSS code HP( A, B) with the following parity-check matrices 40:
HX := [ A⊗ Imb,−Ima⊗ B],
HZ := [ Ina⊗ B∗, A∗⊗ Inb].
If we replace the elements of the matrices A := ( aij)ma×na and B := ( bij)mb×nb by some ℓ× ℓ
matrices over Fq, we obtain matrices ˆA := (ˆaij)ma×na∈ Rma×na and ˆB := ( ˆbij)mb×nb∈ Rmb×nb
over the matrix ring R := Fℓ×ℓ
q . We can also consider the matrices ˆA and ˆB as the ℓ times larger
block matrices over Fq, which, in turn, are used to deﬁne the ℓ times larger analogs of HX and HZ
in the following way:
ˆHX := [ ˆA⊗ Imb,−Ima⊗ ˆB],
ˆHZ := [ Ina⊗ ˆB∗, ˆA∗⊗ Inb], (13)
where in the transposed block matrices ˆA∗ and ˆB∗ we also transpose each ℓ× ℓ block. As it was
shown in [ 17], if every element (i.e., a matrix from R) of ˆA commutes with every element of ˆB,
then this construction always gives a quantum CSS code with t he parity-check matrices ˆHX and
ˆHZ, called the lifted product of ˆA, ˆB and denoted by LP( ˆA, ˆB). Actually, it is easy to see that this
commutativity condition is a necessary and suﬃcient condit ion to produce a well deﬁned CSS code.
Indeed, we have:
ˆHX ˆH ∗
Z = 0 ⇐⇒ ( ˆA⊗ Imb)
(
Ina⊗ ˆB
)
= (Ima⊗ ˆB)( ˆA⊗ Inb),
where the last equation is equivalent to ˆ aijˆbst = ˆbstˆaij for all i, j, s, t.
The most straightforward way to make this general deﬁnition always work is to use ℓ×ℓ matrices
from some commutative matrix ring R⊆ Fℓ×ℓ
q . However, it also works well with any ℓ-dimensional
associative algebra R over Fq, not necessary a commutative 41 one, if we use the right (resp. left)
regular matrix representation of its elements as the entrie s of ˆA (resp. ˆB). Indeed, if we ﬁx a basis
in the algebra R, then the right (resp. left) regular matrix representation of an element r∈ R is
deﬁned as the ℓ× ℓ matrix of the linear operator ρr := x↦→xr (resp. λr := x↦→rx). Since the
multiplication in R is associative, then for any a, b∈ R the operators ρa and λb always commute:
(ρaλb)(x) = ( bx)a = b(xa) = ( λbρa)(x).
Hence, for any two matrices A∈ Rma×na and B∈ Rmb×nb we can replace their elements by
the corresponding right and left matrix representations to obtain the block matrices ˆA, ˆB and get
the well-deﬁned CSS code using Equation ( 13), which we denote by LP( A, B).
Let us note that when the algebra R is commutative, then ρr = λr for each r∈ R, and we do
not need to distinguish the left and the right representatio ns of R. A very simple example of a lifted
product code in this case is Kitaev’s toric code [ 20], which can be obtained as LP(1 + x, 1 + y) with
the ring R = F2[x, y]/(xL− 1, yL− 1). Another important example is Haah’s cubic code [ 45], which
is equal to LP(1 + x + y + z, 1 + xy + xz + yz), and R = F2[x, y, z]/(xL− 1, yL− 1, zL− 1). In these
two examples the parameter L is the lattice size. We see that in both these cases the ring R is a
40If the characteristics of Fq is 2, we can omit the sign in the deﬁnition of HX.
41Let us note that for all the examples of lifted products in [ 17] the algebra R is commutative, and the ﬁrst
examples of non-abelian lifted products ﬁrst appeared in [ 18] in the context of a very similar construction called
balanced product.
48

## PDF page 49

group algebra FqG for some ﬁnite group G. Indeed, G = C2
L for Kitaev’s code, and G = C3
L for
Haah’s code, where CL is the cyclic group of order L.
Remark 14. Let us note that lifted products can also be used not only for g roup rings R = FqG. For
example, if R = Fq[x]/(xℓ− α), where α∈ F×
q , then any matrix H∈ Rm×n deﬁnes the code C(H),
which is called quasi-twisted code, or constacyclic if m = n = 1. Such codes [
61–63] sometimes
have better parameters than quasi-cyclic and cyclic codes, which are their special cases when α = 1.
Thus it is an interesting open problem whether lifted produc ts of these classical codes can give
quantum CSS codes with good parameters (cf. [ 64]).
C Normed abelian groups
LetM be a ﬁnite metric space with a distance function d(x, y). For any non-empty subset C⊆M
we can deﬁne its minimal distance d(C) as
d(C) := min{d(x, y)| x̸= y; x, y∈C} , (14)
where we assume that d(C) :=∞ if|C| = 1.
We can also deﬁne d(x,Y) and d(X ,Y) for x∈M andX ,Y⊆M in a straightforward way:
d(x,Y) := min
y∈Y
d(x, y), (15)
d(X ,Y) := min
x∈X ,y∈Y
d(x, y). (16)
In what follows, we always assume that the metric space M is an abelian normed group , which
means that it has an abelian group structure ( M, +, 0), and the distance d(·,·) is invariant, i.e.,
d(x + h, y + h) = d(x, y) for any x, y, h∈M . For example, if we have a based vector space M∼
= Fn
q ,
then the standard Hamming distance d(x, y) := wt(x− y) is invariant. It is a well-known and easily
veriﬁed fact that the invariant distances d(·,·) are in a one-to-one correspondence with the functions
|·| :M→ R⩾ 0 called norms such that for all x, y∈M we have:
|x| = 0 ⇐⇒ x = 0, (17)
|− x| = |x|, (18)
|x + y| ⩽ |x| +|y|; (19)
where the correspondence is given by d(x, y) :=|x− y| and|x| := d(x, 0). Such invariant distances
on normed groups are sometimes also called group norm metrics [
65]. One can easily check that if
C is a subgroup of M, then the minimal distance d(C) can be also found by the formula:
d(C) = min
x∈C\{0}
|x|. (20)
In fact, a group norm metric on M also induces the corresponding metric on the quotient group
M =M/N called the quotient norm metric [65], where N is some subgroup of M. In this case,
the norm|X| forX∈ M is deﬁned as
|X| := min
x∈X
|x|. (21)
49

## PDF page 50

It is trivial to check that this norm satisﬁes ( 17)-(19), and the corresponding distance
d(X ,Y) :=|X−Y|
forX ,Y ∈ M is equivalent to the distance deﬁned by ( 16). Thus, the quotient group M is
a metric space, and for any group C such thatN⊆C⊆M we can deﬁne the minimal distance of
the subgroup C =C/N⊆ M as in ( 14):
d(C) := min{d(X ,Y)|X̸ =Y;X ,Y∈ C}.
In fact, using ( 20) and ( 21) we can get a much simpler formula:
d(C) = min
X ∈ C\{N }
|X| = min
x∈C\N
|x|. (22)
Moreover, if [·] :M→ M is a canonical projection, giving by x∈M its coset [ x] = x +N ∈M,
then we get: d([x],Y) = d(x,Y) and |[x]| = d(x,N ) for x∈M andY ∈M. This allows us to
deﬁne for any subgroup N⊆M a new norm on M that we call a systolic norm as
|x|N :=|[x]| = d(x,N ).
50

## PDF page 51

D List of symbols and standard notations
[n] set {1, 2, . . . , n}
Fq ﬁnite ﬁeld with q elements
Rm×n set of m× n matrices over R
In identity n× n matrix
ker A kernel of the linear map v↦→Av
im A image of the linear map v↦→Av
A∗ transpose map or transposed matrix for A
C∗ dual chain complex
FX abelian group of formal sums ∑
x∈X axx with
coeﬃcients ax∈F x in a local system F
wt(a) Hamming weight of a∈ Fn
q
wtS(a) block Hamming weight of a∈F X relative
to the subset S⊆ X
|a| norm of a∈ A in a normed abelian group A
supp a support{x∈ X| ax̸= 0} for a∈F X
a|S restriction ∑
x∈S axx to the subset S ⊆ X
of the formal sum a = ∑
x∈X axx∈F X or
a vector a∈ FX
q
KG group algebra over K for the group G
v↔e v′ e connects v and v′
G-lift |G|-fold regular cover
A(Γ) adjacency matrix of Γ
Γ 2 square of the graph Γ, i.e., A(Γ 2) = ( A(Γ)) 2
EΓ (S, T ) set of oriented edges from S to T in Γ
x≻P y x covers y in a poset P
¯X p,q double-cover of the Ramanujan graph X p,q
A⊗ GB G-lifted product of complexes A andB
X×G Y G -lifted product of posets X and Y
[x : x′] incidence number for x∈ X(i), x′∈ X(i− 1)
T(Γ; h) Tanner codes on Γ with local code ker h
TG(ˆΓ; h) G-lifted Tanner codes from T(ˆΓ; h)
A∼ B permutation equivalent codes or matrices
Zi(C), Bi(C) spaces of i-cycles and i-boundaries for C
Hi(C) i-th homology group of C
d(i)
LM(C) i-th locally minimal distance of C
∂S→T restriction ∂S→T :FS→F T of a boundary
map ∂ :FX→F X fromC•(X;F)
51
