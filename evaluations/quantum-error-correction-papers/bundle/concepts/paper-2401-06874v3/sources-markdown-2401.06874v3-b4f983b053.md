---
type: Research Paper
title: A Joint Code and Belief Propagation Decoder Design for Quantum LDPC Codes
description: '- Pinned arXiv record: [2401.06874v3](https://arxiv.org/abs/2401.06874v3)'
resource: https://example.org/qec-arxiv-papers/resource/paper-2401-06874v3/sources%2Fmarkdown%2F2401.06874v3
tags:
- paper-2401-06874v3
- markdown
- rl
concept_id: concepts/paper-2401-06874v3/sources-markdown-2401.06874v3-b4f983b053
concept_path: concepts/paper-2401-06874v3/sources-markdown-2401.06874v3-b4f983b053.md
subject_iri: https://example.org/qec-arxiv-papers/resource/paper-2401-06874v3/sources%2Fmarkdown%2F2401.06874v3
ontology_class_iri: https://example.org/ontology/qec-arxiv-papers#Paper
ontology_version_iri: https://example.org/ontology/qec-arxiv-papers/1.0.0
source_id: paper-2401-06874v3
source_kind: markdown
source_path: sources/markdown/2401.06874v3.md
source_content_sha256: 01a46b01f3f61522bdaecaa927e7d8bf4363e1f20374846251f3e9ce329fa70d
record_sha256: f1a4c575ccd0bd57d26ae701f102841bf6589d8e136699242e810f533e80886a
source_refs:
- https://example.org/qec-arxiv-papers/provenance/record/paper-2401-06874v3/6b63167107e772339c37ff8c
record_id: sources/markdown/2401.06874v3
---

# A Joint Code and Belief Propagation Decoder Design for Quantum LDPC Codes

## Source citation

- Pinned arXiv record: [2401.06874v3](https://arxiv.org/abs/2401.06874v3)
- Authors: Miao, Sisi; Mandelbaum, Jonathan; Jäkel, Holger; Schmalen, Laurent
- PDF: [https://arxiv.org/pdf/2401.06874v3](https://arxiv.org/pdf/2401.06874v3)
- PDF SHA-256: `493c2ea24139cc3a02d9554ce1cccf3d0e179523da83a13c0227309f2ef9d3c6`
- Extracted pages: 6

The following text was extracted page by page from the pinned PDF. Page headings are stable evidence locators.

## PDF page 1

arXiv:2401.06874v3  [cs.IT]  5 May 2024
A Joint Code and Belief Propagation Decoder
Design for Quantum LDPC Codes
Sisi Miao, Jonathan Mandelbaum, Holger Jäkel, and Laurent S chmalen
Karlsruhe Institute of Technology (KIT), Communications E ngineering Lab (CEL), 76187 Karlsruhe, Germany
Email: { firstname.lastname@kit.edu}
Abstract—Quantum low-density parity-check (QLDPC) codes
are among the most promising candidates for future quantum
error correction schemes. However , a limited number of shor t
to moderate-length QLDPC codes have been designed and their
decoding performance is sub-optimal with a quaternary beli ef
propagation (BP) decoder due to unavoidable short cycles in their
Tanner graphs. In this paper , we propose a novel joint code an d
decoder design for QLDPC codes. The constructed codes have a
minimum distance of about the square root of the block length .
In addition, it is, to the best of our knowledge, the ﬁrst QLDP C
code family where BP decoding is not impaired by short cycles
of length 4. This is achieved by using an ensemble BP decoder
mitigating the inﬂuence of assembled short cycles. We outli ne
two code construction methods based on classical quasi-cyc lic
codes and ﬁnite geometry codes. Numerical results demonstr ate
outstanding decoding performance over depolarizing chann els.
Index Terms—Quantum error correction, LDPC codes, belief
propagation decoding
I. I NTRODUCTION
Quantum low-density parity-checks (QLDPCs) codes are
among the most promising candidates for future quantum
error correction (QEC) schemes [
1]. V arious promising code
constructions have been proposed, e.g., [ 2]–[ 6]. Still, some
challenges remain. First, only a small number of good short
to moderate-length QLDPC codes have been constructed,
which are of special interest due to their low implementatio n
complexity and their low decoding latency. Second, most
construction methods ignore the structure of the underlyin g
Tanner graph of the constructed codes. Thus, unavoidable
short cycles of length 4 signiﬁcantly impair the quaternary
belief propagation (BP) decoding performance. However, th e
good decoding performance for classical LDPC codes and low
decoding latency make BP an attractive candidate for QEC.
Therefore, many previous works have tried to improve the
decoding performance in the presence of short cycles, e.g., by
modifying the BP decoder [
7]–[ 10], or by introducing post-
processing steps such as ordered statistics decoding (OSD) [9],
[11]. However, these approaches cannot guarantee to com-
pletely mitigate the inﬂuence of the short cycles. Furtherm ore,
the extra decoding latency introduced by these methods make s
them less appealing for QEC where linear or even constant
time decoding complexity is desired to achieve ultra-low
This work has received funding from the European Research Co uncil (ERC)
under the European Union’s Horizon 2020 research and innova tion programme
(grant agreement No. 101001899) and the German Federal Mini stry of
Education and Research (BMBF) within the project Open6GHub (grant
agreement 16KISK010).
latency decoding. For example, the complexity of OSD is
O
(
n3)
while the complexity of BP decoding is only O (n).
In this work, we construct short to moderate-length QLDPC
codes with a good decoding performance with only BP de-
coding, achieved by joint code and decoder design such that
the proposed ensemble BP decoding is not impaired by short
cycles of length 4. The proposed scheme is referred to as
CAMEL (Cycle Assembling and Mitigating with EnsembLe
decoding). We introduce two exemplary code construction
methods in this paper. The ﬁrst one is constructed from
classical quasi-cyclic (QC) codes. The second one reuses th e
construction in [
4] which is based on ﬁnite geometries (FGs).
We evaluate the performance of CAMEL with numerical
simulations over depolarizing channels.
Notation: Boldface letters denote vectors and matrices, e.g.,
a and A. The i-th component of vector a is denoted by ai, and
the element at the i-th row and j-th column of A is denoted
by Ai,j. Let Ai,: be the i-th row of a matrix A and A:,i the
i-th column of A. AT denotes the matrix transpose. The set
{0, 1, 2, · · · , p − 1} is denoted by [p] for any p ∈ N. The trace
inner product for x, y ∈ F4 is written as ⟨x, y⟩ ∈ { 0, 1}. It
evaluates to 1 if x ̸= 0, y ̸= 0 and x ̸= y, and 0 otherwise. We
use ⊕ to denote binary summation. The indicator function is
denoted by
/BD
{·}. Throughout the paper, the indexing of vector
and matrix elements always starts from 0.
II. P RELIMINARIES
We consider a Calderbank–Shor–Steane (CSS) type quan-
tum stabilizer code (QSC) [ 12] given by Theorem 1.
Theorem 1. Consider two classical binary linear codes
C1 and C2 with parameters [n, k1, d1] and [n, k2, d2]. Their
parity check matrices (PCMs) are HX ∈ F(n−k1)×n
2 and
HZ ∈ F(n−k2)×n
2 , respectively. If C⊥
2 ⊆ C 1, i.e., satisfying
the so-called twisted condition
HX H T
Z = 0, (1)
an [[n, k1 + k2 − n, min{d1, d2}]] QSC can be constructed.
Unless mentioned differently, we restrict ourselves to the
case where k1 = k2 =: k. Thus, the check matrix of the QSC
is written as
S =
( ωHX
¯ωHZ
)
∈ F2(n−k)×n
4 (2)

## PDF page 2

with ω and ¯ω being elements of the Galois ﬁeld
F4 = {0, 1, ω, ¯ω}. Furthermore, HX and HZ being sparse
matrices results in a QLDPC code.
To estimate the error e ∈ Fn
4 that occurred, the syn-
drome z ∈ F2(n−k)
2 is measured on the stabilizer generators.
For simulation purpose, the syndrome z is computed as
zj = ⨁
i∈[n]⟨ei, Sj,i⟩ with j ∈ [2(n − k)]. In this work, we
perform quaternary BP decoding [
14] on the Tanner graph
associated with the check matrix S. A Tanner graph is a
bipartite graph with two sets of vertices: the variable node s
(VNs) corresponding to the code symbols and the check nodes
(CNs) corresponding to the checks and thus to rows of S. A
VN vi is connected to a CN cj if the corresponding entry
Sj,i ̸= 0.
Note that (
1) requires an even number of overlapping ones
between any row of HX and any row of HZ. Therefore,
the Tanner graph associated with S has a girth of either
inﬁnity or 4. First, if the Tanner graph has a girth of inﬁnity,
i.e., it is a tree, then the Tanner graphs associated with HX
and HZ are necessarily trees. Such binary codes are known
to have poor minimum distance [ 13]. Hence, short cycles
are necessary in constructing good QLDPC codes. However,
the Tanner graph structure needs careful optimization for B P
decoding. One potential solution is to construct component
matrices HX and HZ with a girth of at least 6 yet permitting
4-cycles between HX and HZ, as, e.g., done in [
3]. Therefore,
acceptable performance can be attained by decoding the X and
Z errors separately using two binary BP decoders operating
on the PCMs HZ and HX , respectively. However, binary
decoding ignores the correlation between X and Z errors and
is thus inherently sub-optimal, see, e.g., [ 7], [ 9], [ 10] for a
performance comparison. Hence, to take the correlation int o
account while still mitigating the inﬂuence of short cycles ,
we propose CAMEL, a novel code construction where an
ensemble of quaternary BP decoding is not impaired by short
cycles of length 4.
III. CAMEL: J OINT CODE AND DECODER DESIGN
CAMEL consists of the construction of codes where all
short cycles are assembled onto a single VN and an ensemble
BP decoder in which the inﬂuence of short cycles is fully
mitigated.
To this end, we ﬁrst construct two classical binary LDPC
codes whose parity check matrices H1, H2 ∈ Fm×n
2 fulﬁll
H1H T
2 = 1m×m, (3)
where 1m×m denotes an all-one matrix of size m × m. A
straightforward way to satisfy (
3) is to construct matrices H1
and H2 such that any row of H1 overlaps with any row of
H2 in exactly one position. It is possible to construct H1 and
H2 fulﬁlling ( 3) such that the Tanner graph associated with
the matrix
(
H T
1 H T
2
) T
has a girth of at least 6. Two explicit
code constructions will be presented in the following secti ons.
Next, we construct two new PCMs by appending an all-one
column vector 1m×1 to H1 and H2, respectively, resulting in
HX =
( H1 | 1m×1
)
∈ Fm×(n+1)
2
z
vn = 0 BP
vn = 1 BP
vn = ω
BP
vn = ¯ω
BP
ML
ˆe0
ˆe1
ˆe2
ˆe3
ˆe
Figure 1. Block diagram of the proposed ensemble decoder.
and
HZ =
( H2 | 1m×1
)
∈ Fm×(n+1)
2 .
Then, we can verify that
HXH T
Z =
( H1 | 1) (
H T
2
1T
)
= H1H T
2 + 1m×m = 0
and ( 1) is fulﬁlled. Note that all cycles of length 4 are
nested on vn. Then, using Theorem 1, we obtain an
[[n + 1, n + 1 − rank(HX ) − rank(HZ), d]] QLDPC code.
We proceed by introducing the decoder part of CAMEL
which essentially relies on ensemble decoding [ 16]. As de-
picted in Fig. 1, after measuring the syndrome z, four BP
decodings are performed in parallel. In each BP decoding, th e
last bit is assigned a distinct ﬁxed value η ∈ F4. The effect of
doing so will be discussed below.
Let ˆei denote the error estimate of the BP decoding in
the i-th path of the decoder shown in Fig. 1 and deﬁne
I := {i ∈ [4] : ˆei satisﬁes syndrome z}. If |I| = 0 , the de-
coder declares a decoding failure. Otherwise, we perform
a maximum likelihood (ML)-in-the-list step by choosing the
error candidate ˆe = ˆei⋆ , i⋆ ∈ I , of lowest weight, i.e.,
i⋆ = arg min
i∈I
w(ˆei) where w (·) denotes the number of
nonzero elements in the argument.
The approach of decoding using multiple decoders with hard
guesses for certain bits is known as decimation in classical
coding theory, e.g., in [
17]. Next, we analyze the inﬂuence
of decimating one bit in BP decoding for QLDPC codes.
To this end, we consider a quarternary BP decoder passing
probabilities. One can verify that the upcoming conclusion s
also hold for BP decoders with log-likelihood ratio (LLR)
message passing [
14], [ 15] and their reﬁned version [ 7].
Assume that we provide the decoder with the hard guess η
of the last VN, i.e., vn = η. For an arbitrary decoding iteration,
the outgoing message vector of vn to a neighboring CN cj is(
m(0)
v,n→j m(1)
v,n→j m(ω)
v,n→j m(¯ω)
v,n→j
)
where
m(a)
v,n→j = b · Pch(vn = a)
∏
j′∈M(n)\{j}
m(a)
c,j′→n (4)
for a ∈ F4 with M(i) denoting the set of indices of the
neighboring CNs of VN vi. The parameter b is a normaliza-
tion factor such that the probabilities sum up to 1. As we
provide a hard guess of vn = η, the channel probability is
Pch(vn = a) =
/BD
{a=η}. Therefore, the outgoing message of
vn in ( 4) evaluates to
m(a)
v,n→j = /BD
{a=η}, (5)

## PDF page 3

regardless of the incoming messages from the CNs. We now
inspect the outgoing message of a CN cj that is a neighbor of
the decimated VN vn, i.e., j ∈ M(n):
m(a)
c,j→i = c ·
∑
t:ti=a
fSj,: (t, zj)
∏
i′∈N (j)\{i}
m(ti′ )
v,i′→j (6)
where c is again some normalization factor and N (j) denotes
the set of indices of the neighboring VNs of cj. The check
function fSj,: (t, zj) indicates if an error vector t fulﬁlls
the syndrome zj speciﬁed by the j-th row of the check
matrix Sj,:, i.e., , fSj,: (t, zj) = 1 if ⨁
i∈N (j)⟨ti, Sj,i⟩ = zj
and 0 otherwise. Together with (
5), we derive that for any
i ∈ N (j), i ̸= n, the outgoing message in ( 6) is
m(a)
c,j→i = c ·
∑
t:ti=a,tn=η
fSj,: (t, zj)
∏
i′∈N (j)\{i,n}
m(ti′ )
v,i′→j
= c ·
∑
t∼n:ti=a
⟨η, Sj,n⟩ ⊕ fSj,∼n (t∼n, zj)
∏
i′∈N (j)\{i,n}
m(ti′ )
v,i′→j, (7)
where t∼n and Sj,∼n denote t and Sj,: excluding their last
entry, i.e., tn and Sj,n, respectively.
From ( 7), it follows that messages associated with vn are
excluded in BP, except for ⟨η, Sj,n⟩, which is a constant.
Thus, vn can be removed together with all edges incident to it.
This essentially dissolves all short cycles of length 4 in ea ch
decoding path as they are all assembled on vn. Hence, their
inﬂuence is fully mitigated.
IV. Q UASI -C YCLIC QLDPC C ODES
In [ 3], a class of QC QLDPC codes without short cycles
of length 4 in their component matrices HX and HZ were
constructed. In this section, we adapt this method to constr uct
codes fulﬁlling ( 3). We ﬁrst introduce a few deﬁnitions.
Let p be a prime number and Fp be the prime ﬁeld. We
focus on a class of classical binary QC LDPC codes deﬁned
as the null space of a PCM
H =





I(c0,0) I(c0,1) · · · I(c0,L−1)
I(c1,0) I(c1,1) · · · I(c1,L−1)
.
.
. .
.
. . . . .
.
.
I(cJ−1,0) I(cJ−1,1) · · · I(cJ−1,L−1)




 ∈ FJp×Lp
2 ,
(8)
obtained by replacing each element ci,j ∈ [p] of a base
matrix H ∈ [p]J×L by a circulant permutation matrix (CPM)
I(ci,j). A CPM I(x) is obtained by cyclically right shifting
all the rows of the identity matrix I ∈ Fp×p
2 by x positions.
For brevity, we denote the procedure of obtaining a binary
PCM from a base matrix H as H = Cyc(H). Note that the
commutative group of CPMs I(x) with x ∈ [p] under matrix
multiplication is isomorphic to the additive group of Fp as
I(x)I(y) = I((x+y) mod p). Furthermore, for a commutative
group G and a subgroup G′ of G, the coset of g ∈ G w.r.t. G′
is deﬁned as [g]G′ := {gh : h ∈ G ′}. Note that two cosets are
either identical or disjoint.
Following the notation of [
3], a vector x ∈ FL
p is called
multiplicity odd if every element of x occurs an odd number
of times and multiplicity free if every element of x is unique.
The vector x is a permutation vector if it contains all elements
of Fp exactly once. Hence, a permutation vector of length p
is multiplicity odd and free. Next, we need Lemma
1.
Lemma 1. Consider two matrices A ∈ FJ1×L
p and
B ∈ FJ2×L
p . Then, Cyc(A)Cyc(B)T = 1J1p×J2p if
and only if the difference vector between any two rows of A
and B is multiplicity odd and contains all elements of Fp.
Proof. Let a be an arbitrary row of A and b be a row of B.
First, we have:
Cyc(a)Cyc(b)T =
L−1∑
i=0
I(ai)I(bi)T =
L−1∑
i=0
I(ai − bi).
This is a summation of L CPMs. Note that the ones in two
CPMs either completely overlap or do not overlap at all. To
ensure that ∑ L−1
i=0 I(ai −bi) = 1p×p, the set {ai−bi : i ∈ [L]}
must contain all elements of Fp an odd number of times.
Thus, the difference vector of any two rows a and b must be
multiplicity odd and contain all elements of Fp at least once.
As this holds for any two rows, it concludes the proof.
In order to obtain an all-one matrix, Lemma 1 implies
L ≥ p. Y et L > p implies a Tanner graph with girth
4 [3]. Hence, we choose L = p. In this case, the set
{ai − bi : i ∈ [L]} yields a permutation vector and a check
matrix with girth at least 6 can be constructed, as shown by
Theorem 2.
Theorem 2. Let p be a prime number . There exists a base
matrix H ∈ Fℓ×p
p with ℓ ≤ p − 1 such that any partition of
H into H =
(
HT
1 HT
2
) T
yields Cyc(H1)Cyc(H2)T = 1.
Besides, the T anner graph of Cyc(H) has girth at least 6.
Proof. The proof is constructive. Let F∗
p := Fp \ {0} denote
the multiplicative group of Fp. Additionally, let σ ∈ F∗
p be
of order ord(σ) = ℓ. Then, G′ = {σ0, . . . , σℓ−1} forms a
subgroup of F∗
p. We now form T = |F∗
p|/ℓ cosets [τi]G′ of
size ℓ by choosing τi in the following way. First, let τ0 = 1 .
Then, for i ∈ { 1, 2, . . . , T − 1}, we consecutively choose
τi ∈ F∗
p\⋃ i−1
j=0[τj]G′ . This choice ensures that every τi belongs
to a distinct coset. Now, form the matrix
M =





1 σ . . . σ ℓ−1
σℓ−1 1 σℓ−2
.
.
. . . . .
.
.
σ σ 2 . . . 1




 ∈
(
F∗
p
) ℓ×ℓ,
as well as the matrix
H =
(
1ℓ×1 τ0M . . . τ T −1M
)
∈
(
F∗
p
) ℓ×p
.
Let Hj1,: and Hj2,: be two distinct rows of H, i.e.,
j1, j2 ∈ [ℓ], j1 ̸= j2. Their difference vector d := Hj1,:−Hj2,:
can be written as d =
(
0 d(0) d(1) · · · d(T −1))
∈ Fp
p
where for i ∈ [T ],
d(i) = τi · (Mj1 − Mj2 ) :=
(
d(i)
0 d(i)
1 · · · d(i)
ℓ−1
)
∈ Fℓ
p.

## PDF page 4

TABLE I
QC C ODE CONSTRUCTED WITH ORD (σ )=p − 1.
Code n k rate p σ d
Q1 50 12 0.24 7 3 6
Q2 122 20 0.16 11 2 12
Q3 170 24 0.14 13 2 14
Q4 290 32 0.11 17 3 18
Q5 362 36 0.10 19 3 20
For x ∈ [ℓ], we write
d(i)
x = τi · (σℓ−j1+x − σℓ−j2+x) = τi · (σ−j1 − σ−j2 ) · σℓ+x.
Thus, one can see that
{
d(i)
x : x ∈ [ℓ]
}
≡ [τi(σ−j1 − σ−j2 )]G′ .
Therefore, the sets {d(i)
x : x ∈ [ℓ]} for i ∈ [T ] yield the T
distinct cosets permuting all elements in F∗
p. Together with the
ﬁrst 0 element, d forms a permutation vector of Fp. Performing
an arbitrary partition of H into H =
(
HT
1 HT
2
) T
with
H1 ∈ (F∗
p)ℓ1×p, H2 ∈ (F∗
p)ℓ2×p, and ℓ1 + ℓ2 = ℓ and using
Lemma
1, we know that Cyc(H1)Cyc(H2)T = 1. In this
work, ℓ is always an even number and we choose ℓ1 = ℓ2.
It remains to show that the Tanner graph of Cyc(H) has
girth at least 6 which is fulﬁlled if the difference vector of any
two rows of Cyc(H) is multiplicity free [ 3]. This condition
is met because the difference vectors of the rows of H are
permutation vectors.
We use the matrices H1 and H2 from the proof of
Theorem 2 to construct QSCs as described in Sec. III. The
parameters of the constructed codes are listed in Tab. I
Example. W e consider an example for p = 7. Choosing σ = 3
yields the subgroup G′ = [7]. Note that ord(σ) = 6 and T = 1.
Then, choose τ0 = 1 ∈ [1]G′ . Since T = 1 , no more τi are
required. Hence, we can construct the base matrix
H =
( 1ℓ×1 τ0M )
=





1 1 3 2 6 4 5
1 5 1 3 2 6 4
1 4 5 1 3 2 6
1 6 4 5 1 3 2
1 2 6 4 5 1 3
1 3 2 6 4 5 1




 .
One can verify that the difference of any two rows, computed
in Fp, results in a permutation vector of Fp. Note that we
choose T = 1 as it yields low-rate codes, which are suitable
for the current quantum channels with high noise level. W e
take the ﬁrst three rows of H to be H1 and the last three
rows to be H2. Then, we obtain two binary matrices Cyc( H1)
and Cyc( H2) ∈ F21×49
2 , both with rank 19.
1 By appending an
all-one column to them, we obtain the Q1 code.
1Note that H is almost never of full rank. Therefore, the constructed cod es
naturally have an overcomplete set of stabilizers that will all be used for
decoding. The same holds for the codes constructed in Sec. V. The beneﬁts
and complexity of this approach are discussed in [ 10].
V. QLDPC C ODES FROM FINITE GEOMETRIES
In [ 4], a QLDPC code construction using FGs fulﬁlling ( 3)
was proposed. We brieﬂy review the construction and focus on
concrete examples of the constructed codes and their decodi ng
performance with CAMEL.
Consider a set N of N points and a set M of M lines con-
structed from a certain ﬁnite ﬁeld. Details on the construct ion
method can be found in [
18], [ 19]. The points and lines form
an FG if the following conditions are satisﬁed for some ﬁxed
integers γ ≥ 2 and ρ ≥ 2:
(1) Each line passes through ρ points,
(2) any two points are on exactly one line,
(3) each point lies on γ lines,
(4) two lines are either parallel or intersect at one and only
one point.
In this work, we use the 2D-FGs based on ﬁnite ﬁelds Fq
of characteristic 2 with q = 2 s. This yields codes with the
best minimum distances and decoding performance among the
codes we constructed using FGs. Then, we focus on the most
famous examples of FGs which are the Euclidean geometries
(EGs) and the projective geometries (PGs). A 2D-EG consists
of N = q2 points and M = q2 + q lines. Moreover, we have
ρ = q and γ = q +1. A 2D-PG contains N = q2 +q +1 points
and M = q2 + q + 1 lines where ρ = q + 1 and γ = q + 1.
We index the points in an FG from 0 to N − 1. For each
line in an FG, indexed from 0 to M − 1, deﬁne an incidence
vector a ∈ FN
2 as follows: for i ∈ [N ], ai = 1 if the point i
is on the line and ai = 0 otherwise.
Now, form a binary PCM H ∈ FN ×M
2 whose columns
consist of the incidence vectors of all lines in the FG. It fol lows
that H has a row weight of γ and a column weight of ρ.
Moreover, it was shown in [
19] that the minimum distance of
the binary linear code deﬁned by H is lower bounded by ρ.
For this binary PCM H ∈ FN ×M
2 , it is easy to show that
HH T = 1 using condition ( 2) and with our assumption
that q = 2 s.2 To construct QLDPC codes with relatively low
rates, we choose HX = HZ =
( H | 1)
∈ FN ×(M+1)
2 .3 One
can verify that the minimum distance of the code deﬁned by
the PCM
(
H | 1
)
is the same as the minimum distance of the
code deﬁned by H, which is lower bounded by ρ. Therefore,
for codes constructed from the 2D-FG, the minimum distance
is approximately √
n.
The parameters of the exemplary codes constructed from
EGs are listed in Tab. II. As for the PG codes, assume that a
QLDPC code constructed from an EG using a ﬁnite ﬁeld has
parameters [[n, k, d]]. Then, the QLDPC code constructed from
2We have to point out a mistake in [
4] where the columns of H are the
incidence vectors of the lines which do not pass through origin instead of all
the lines in the geometry as we do. We can verify that the former does not
yield a matrix H that fulﬁlls ( 3) by looking at any two non-origin points i and
j located on a line λ which passes through the origin. In our construction, it
means that the λ -th column is the only column where the two rows Hi, : and
Hj, : have an overlapping one as two points are on exactly one line. Therefore,
Hi, :H T
j, : = 1. Thus, removing column H:,λ leads to Hi, :H T
j, : = 0.
3This unfortunately introduces some short cycles of length 4 between HX
and HZ. However, thanks to the other good properties of the FG codes , the
performance degradation is acceptable.

## PDF page 5

10− 2 10− 110− 5
10− 4
10− 3
10− 2
10− 1
100
Depolarizing probability ε
Frame Error Rate (FER)
CAMEL
BP
BP (GA)
BP2
BP2 (GA)
BP2-OSD
Figure 2. FER vs. depolarizing probability ε curves
when decoding an E4 [[273, 111, 17]] QLDPC code
from an EG using different decoding algorithms.
10− 2 10− 1
Depolarizing probability ε
Q1
Q2
Q3
Q4
Q5
R1
Figure 3. FER vs. depolarizing probability ε
curves for the quasi-cyclic QLDPC codes shown
in Tab.
I and the reference code R1.
10− 2 10− 1
Depolarizing probability ε
E1
E2
E3
E4
E5
R2
Figure 4. FER vs. depolarizing probability ε
curves for QLDPC codes constructed using EGs
shown in Tab.
II and the reference code R2.
TABLE II
QLDPC CODES FROM 2D EG OF FINITE FIELD OF CHARACTERISTIC 2.
Code n k rate s d
E1 7 1 0.14 1 3
E2 21 3 0.14 2 5
E3 73 19 0.26 3 9
E4 273 111 0.41 4 17
E5 1057 571 0.54 5 33
a PG using the same ﬁeld has parameters [[n+ 1, k+ 1, d+ 1]].
Hence, we do not list them explicitly.
VI. N UMERICAL RESULTS
We assess the proposed scheme using Monte Carlo simula-
tions over the quantum depolarizing channel where the three
types of Pauli errors occur with equal probability ε/3. At least
300 frame errors are collected to obtain the frame error rate
(FER) for each data point. All BP decoding paths use sum-
product algorithm with 15 iterations and a ﬂooding schedule.
First, we highlight the importance of decoding using our
proposed ensemble decoder. Figure
2 depicts the decoding
results using different decoding algorithms for the E4 code
as an example. When decoded with a single BP decoder, the
decoding performance is poor due to numerous short cycles of
length 4. However, when using ensemble decoding in CAMEL
as described in Sec.
III, the performance improves by orders
of magnitude. Additionally, no error ﬂoor is observed when
simulating at a low FER of 10−7. Moreover, as a benchmark,
we evaluate a genie-aided (GA) BP decoder which is fed the
correct value of vn. The ensemble BP decoding has almost the
same performance as the genie-aided version. As the reliabi lity
of the guessed value is set to inﬁnity, corresponding to a
probability of 1, the paths with the wrong guess usually either
fail to converge or will ﬁnd a high-weight error estimate.
For completeness, we also plot the decoding results using a
pair of binary BP (BP2) decoders and its genie-aided version
where the correct value of vn is fed to both decoders. They
are outperformed by their respective quaternary counterpa rt.
Furthermore, we decode the E4 code using the BP2-OSD
decoder with combination sweep (CS) strategy and an order
of 42, which is implemented in [
11]. Further increasing the
order of OSD does not improve the performance noticeably.
The decoding gain achieved by the BP-OSD decoder is
limited compared to the genie-aided BP2 decoder. For other
constructed codes, we observe similar results.
We also compare the performance of the QLDPC codes
constructed in Sec.
IV and Sec. V using the proposed ensemble
BP decoder with existing codes as depicted in Fig. 3 and
Fig. 4, respectively. Our Q5 code outperforms the [[400, 16]]
hypergraph product code (R1) with BP-OSD decoder [ 11]
and our E5 code outperforms the [[800, 400]] bicycle code
(R2) using the modiﬁed non-binary decoder with enhanced
feedback [
8], [ 20]. Note that both reference codes use a
signiﬁcantly more complex decoding algorithm and have
lower code rates than our constructed codes. We conclude
that CAMEL achieves great decoding performance with low
decoding latency.
VII. C ONCLUSION
In this paper, we proposed a novel joint code and decoder
design for QLDPC codes with good quarternary BP decoding
performance without the need for any major modiﬁcation
of the BP decoder or any post-processing steps. Simulation
results show a signiﬁcant improvement compared to conven-
tional BP decoding.
Future work includes investigating the generalization of t he
proposed CAMEL scheme to provide codes with improved
properties. For example, constructing codes that are more
degenerate, enabling joint decoding of the circuit-level n oise,
and constructing codes with local qubit connectivity.
REFERENCES
[1] D. Gottesman, “Fault-tolerant quantum computation wit h constant over-
head,” Quantum Information and Computation , vol. 14, 2014.

## PDF page 6

[2] D. J. MacKay, G. Mitchison, and P . L. McFadden, “Sparse-g raph codes
for quantum error correction,” IEEE Trans. Inf. Theory , vol. 50, no. 10,
2004.
[3] M. Hagiwara and H. Imai, “Quantum quasi-cyclic LDPC code s,” in Proc.
ISIT, 2007.
[4] S. A. Aly, “A class of quantum LDPC codes constructed from ﬁnite
geometries,” in Proc. GLOBECOM , 2008.
[5] J.-P . Tillich and G. Zémor, “Quantum LDPC codes with posi tive rate and
minimum distance proportional to the square root of the bloc klength,”
IEEE Trans. Inf. Theory , vol. 60, no. 2, 2013.
[6] P . Panteleev and G. Kalachev, “Asymptotically good quan tum and locally
testable classical LDPC codes,” in Proc. SIGACT Symposium on Theory
of Computing , 2022.
[7] C.-Y . Lai and K.-Y . Kuo, “Log-domain decoding of quantum LDPC
codes over binary ﬁnite ﬁelds,” IEEE Trans. Quantum Eng., vol. 2, 2021.
[8] Z. Babar, P . Botsinis, D. Alanis, S. X. Ng, and L. Hanzo, “F ifteen
years of quantum LDPC coding and improved decoding strategi es” IEEE
Access, vol. 3, 2015.
[9] P . Panteleev and G. Kalachev, “Degenerate quantum LDPC c odes with
good ﬁnite length performance,” Quantum, vol. 5, 2021.
[10] S. Miao, A. Schnerring, H. Li, and L. Schmalen, “Quatern ary neural
belief propagation decoding of quantum LDPC codes with over complete
check matrices,” arXiv preprint arXiv:2308.08208 , 2023.
[11] J. Roffe, D. R. White, S. Burton, and E. Campbell, “Decod ing across
the quantum low-density parity-check code landscape,” Physical Review
Research, vol. 2, no. 4, 2020.
[12] A. R. Calderbank, E. M. Rains, P . W. Shor, and N. J. A. Sloa ne,
“Quantum error correction via codes over GF(4),” IEEE Trans. Inf.
Theory, vol. 44, no. 4, 1998.
[13] T. Etzion, A. Trachtenberg and A. V ardy, “Which codes ha ve cycle-free
Tanner graphs?,” IEEE Trans. Inf. Theory , vol. 45, no. 6, 1999.
[14] M. C. Davey and D. J. MacKay, “Low density parity check co des over
GF(q),” in Proc. ITW, 1998.
[15] D. Declercq and M. Fossorier, “Decoding algorithms for nonbinary
LDPC codes over GF(q),” IEEE Trans. Commun. , vol. 55, no. 4, 2007.
[16] T. Hehn, J. B. Huber, S. Laendner, and O. Milenkovic, “Mu ltiple-bases
belief-propagation for decoding of short block codes,” in Proc. ISIT ,
2007.
[17] V . Aref, N. Macris, and M. Vuffray, “Approaching the rat e-distortion
limit with spatial coupling, belief propagation, and decim ation,” IEEE
Trans. Inf. Theory , vol. 61, no. 7, 2015.
[18] S. Lin and D. J. Costello, Jr., Error Control Coding: Fundamentals and
Applications. Prentice-Hall, 2004.
[19] Y . Kou, S. Lin, and M. Fossorier, “Low-density parity-c heck codes based
on ﬁnite geometries: a rediscovery and new results,” IEEE Trans. Inf.
Theory, vol. 47, no. 7, 2001.
[20] Y .-J. Wang, B. C. Sanders, B.-M. Bai, and X.-M. Wang, “En hanced
Feedback Iterative Decoding of Sparse Quantum Codes,” IEEE Trans.
Inf. Theory , vol. 58, no. 2, 2012.
