---
type: Research Paper
title: Explicit Instances of Quantum Tanner Codes
description: '- Pinned arXiv record: [2508.05095v3](https://arxiv.org/abs/2508.05095v3)'
resource: https://example.org/qec-arxiv-papers/resource/paper-2508-05095v3/sources%2Fmarkdown%2F2508.05095v3
tags:
- paper-2508-05095v3
- markdown
- rl
concept_id: concepts/paper-2508-05095v3/sources-markdown-2508.05095v3-46a518434d
concept_path: concepts/paper-2508-05095v3/sources-markdown-2508.05095v3-46a518434d.md
subject_iri: https://example.org/qec-arxiv-papers/resource/paper-2508-05095v3/sources%2Fmarkdown%2F2508.05095v3
ontology_class_iri: https://example.org/ontology/qec-arxiv-papers#Paper
ontology_version_iri: https://example.org/ontology/qec-arxiv-papers/1.0.0
source_id: paper-2508-05095v3
source_kind: markdown
source_path: sources/markdown/2508.05095v3.md
source_content_sha256: 9d51b23f305164f6221d4c5d1213db88b221a0e4969d1cf91661f930085759cf
record_sha256: 34092d85bb3095062b42284234e25cb8dd211543d138e6f65e7dbf01eaa508df
source_refs:
- https://example.org/qec-arxiv-papers/provenance/record/paper-2508-05095v3/a1ca94e4962c192280ee4d62
record_id: sources/markdown/2508.05095v3
---

# Explicit Instances of Quantum Tanner Codes

## Source citation

- Pinned arXiv record: [2508.05095v3](https://arxiv.org/abs/2508.05095v3)
- Authors: Radebold, Rebecca Katharina; Bartlett, Stephen D.; Doherty, Andrew C.
- PDF: [https://arxiv.org/pdf/2508.05095v3](https://arxiv.org/pdf/2508.05095v3)
- PDF SHA-256: `be655fc8cc1f70b23b243dffdfe5f3bb880ba3754ac3dc5cc9329a0bebb6b5da`
- Extracted pages: 13

The following text was extracted page by page from the pinned PDF. Page headings are stable evidence locators.

## PDF page 1

Explicit Instances of Quantum Tanner Codes
Rebecca Katharina Radebold, 1, 2,∗ Stephen D. Bartlett, 1 and Andrew C. Doherty 1
1Centre for Engineered Quantum Systems, School of Physics,
The University of Sydney, Sydney, New South Wales 2006, Australia
2Sydney Quantum Academy, Sydney, New South Wales, Australia
We construct several explicit instances of quantum Tanner codes, a class of asymptotically good
quantum low-density parity check (qLDPC) codes. The codes are constructed using dihedral groups
and random pairs of classical codes and exhibit high encoding rates, relative distances, and pseudo-
thresholds. Using the BP+OSD decoder, we demonstrate good performance in the phenomenological
and circuit-level noise settings, comparable to the surface code with similar distances. Finally, we
conduct an analysis of the space-time overhead incurred by these codes.
I. INTRODUCTION
Quantum computers have the potential to deliver ex-
traordinary computational power by harnessing unique
quantum phenomena such as superposition and entan-
glement. However, quantum systems are very suscepti-
ble to noise, and scalable quantum computers will likely
require mechanisms to systematically and reliably de-
tect and correct errors during computations. To this
end, Shor introduced the first quantum error correcting
code [1], demonstrating the possibility of using redun-
dancy to encode and protect quantum information. This
work was followed by Kitaev’s introduction of the sur-
face code [2], which has become the standard for high-
threshold quantum error correction (QEC) and is the ba-
sis for the majority of experimental work studying QEC
such as Ref. [3–5]. While its excellent performance and
locality make it desirable for experimental realization,
the overhead required for the surface code with the error
rates of current devices represents a significant barrier
to implementing it as a scalable and efficient model for
quantum error correction.
Recently, there has been an increasing amount of re-
search investigating more efficient alternatives for QEC,
most notably the class of quantum low-density parity
check (qLDPC) codes, much of which is summarized in
Ref. [6]. More general than the surface code, this class
of codes is characterized by sparse parity check matri-
ces and non-vanishing encoding rates in return for re-
duced geometric locality. Early constructions include
the Freedman-Meyer-Luo [7], hypergraph product [8],
fiber bundle [9], lifted product [10] and balanced prod-
uct [11] codes, each progressively achieving higher en-
coding rates and relative distances by utilizing mathe-
matical tools from topology and graph theory. In 2021,
Panteleev and Kalachev published the first construction
ofasymptotically goodqLDPC codes [12], characterized
by constant encoding rate and a minimum distance linear
in the number of physical qubits. Since then, two more
asymptotically good constructions have emerged, namely
Dinur-Hsieh-Lin-Vidick codes [13] and quantum Tanner
∗ rrad0225@uni.sydney.edu.au
codes [14], paving the way for qLDPC codes to become
a promising alternative for QEC.
While asymptotically good constructions of qLDPC
codes provide the theoretical basis for scalable quantum
error correction, near-term hardware is small in size, gen-
erally consisting of tens to hundreds of qubits, and ex-
hibits relatively high physical error rates. To test the
potential of qLDPC codes for use in the near term, then,
there is a need to construct explicit instances of error-
correcting codes and evaluate their performance in nu-
merical simulations. Such numerical work allows us to
determine whether new codes are suitable for implemen-
tation and how they would compare to other codes, in-
cluding surface codes, in such implementations. This has
been the focus of recent work examining explicit con-
structions and their performances, including for varia-
tions of the bicycle code constructions [15–18], hyper-
graph product codes [19, 20], quantum Tanner codes [21]
and others [10, 22, 23].
In this paper, we construct a number of explicit in-
stances of quantum Tanner codes featuring high encoding
rates and relative distances, good performance in numer-
ical simulations in relevant noise regimes, and reduced
overheads when compared to surface codes. These codes
range in size from 36 to 250 qubits and exhibit encod-
ing rates around 20%. Moreover, the smaller instances
have weight-6 stabilizer generators and low space-time
overhead when compared to surface codes of similar dis-
tances. We conduct numerical simulations with phe-
nomenological and circuit-level noise using the BP+OSD
decoder [10, 24] to compute high pseudo-thresholds and
low logical error rates in thep≃10 −3 physical error rate
regime.
The remainder of this paper is structured as follows. In
Section II, we review quantum stabilizer and CSS codes
before describing the quantum Tanner code construction
as proposed by Leverrier and Z´ emor [14]. Additionally,
we review decoding strategies for our numerical simula-
tions. In Section III, we provide the details of the con-
struction of the explicit instances of our quantum Tanner
codes, including their parameters and other underlying
properties. In Section IV, we present our numerical re-
sults, beginning with the error models used, before de-
scribing simulation results and pseudo-thresholds. We
arXiv:2508.05095v3  [quant-ph]  14 Nov 2025

## PDF page 2

2
conclude the section with a comparison of space-time
overheads. Finally, we summarize our findings and dis-
cuss future work in Section V.
II. BACKGROUND
In this section, we provide the necessary technical
background related to quantum stabilizer and CSS codes,
before delving into the details of the quantum Tanner
code construction from [14], including the left-right Cay-
ley complexes and classical codes that form the basis of
these codes. We also review the belief propagation and
ordered-statistics decoding approach widely employed for
numerical simulations with qLDPC codes.
A. Quantum Stabilizer and CSS codes
The state space of a system ofnqubits is a Hilbert
spaceH= (C 2)⊗n. A quantum code encodingklogical
qubits is a subspace ofHof dimension 2 k. The most well-
known method for describing quantum codes is provided
by the stabilizer formalism, a group-theoretic framework
introduced in [25]. In this formalism, a quantum code is
given by the +1-eigenspace of an abelian subgroupSof
the Pauli groupP=⟨X i, Yi, Zi|i∈[n]⟩, not containing
−I. In other words, stabilizerss∈ Saren-fold ten-
sor products of Pauli operators which commute pairwise
and satisfys|ϕ⟩=|ϕ⟩for any codeword|ϕ⟩, i.e. code-
words are “stabilized” by the elements ofS. The set of
elements ofPwhich commute withSis called the cen-
tralizerC(S). The cosetsC(S)\Scorrespond to the set
of logical operators of the quantum code, of which there
are 4k. The smallest weight of any non-trivial logical op-
erator is called the distance of the code,d, and roughly
captures the error-correcting capabilities of the code.
Calderbank-Shor-Steane (CSS) codes are quantum er-
ror correcting codes given by two binary linear classical
codesC X andC Z such thatC X ⊂C ⊥
Z [26], [27]. From
the perspective of their respective parity check matrices
HX andH Z, this condition is equivalent toH X H T
Z = 0
mod 2. If the rows ofH X andH Z are viewed as sta-
bilizers, where a 1 in positioniof a row inH X (HZ)
corresponds to the operatorX i (Zi) and a 0 toI i, then a
CSS code is a stabilizer code whose stabilizer generators
each consist entirely of eitherXorZPauli operators
(aside from identity operators).
B. Quantum T anner Code Construction
We describe the construction of quantum Tanner codes
as in [14] by reviewing left-right Cayley complexes, clas-
sical codes, and the properties of the resulting quantum
CSS codes.
1. Left-Right Cayley Complexes
The left-right Cayley complex is derived from the more
familiar Cayley graph. A Cayley graph Γ(V, E) is a
graph-theoretical representation of a groupGthrough a
fixed set of generatorsSnot containing the identity ele-
ment [26]. The verticesg∈Vcorrespond to the elements
ofG. There exists an edge between two verticesgandg ′
if and only if there exists ans∈Ssuch thatg·s=g ′,
where (·) represents the group operation. An edge is di-
rected unlessScontainss −1 as well. IfSis symmetric,
that isS=S −1, then the graph is undirected.
A left-right Cayley complex is a complex constructed
from a Cayley graph by introducing two sets of vertices
corresponding to group elements and edges based on left
and right actions of generators [13]. Specifically, the ver-
tices of a left-right Cayley complex areg i wherei= 0,1
andg i ∈G. The edges of the left-right Cayley com-
plex connect the two sets of vertices generating a bipar-
tite graph. The generating setSof the Cayley graph
is replaced by two symmetric sets of generatorsAand
Bthat generate edges by left and right multiplication,
respectively.
Definition 1(Left-Right Cayley Complex).LetGbe
a finite group and letA, B⊆Gsuch that⟨A, B⟩=G.
Further, letA=A −1,B=B −1. A left-right Cayley
complexΓ(G, A, B)corresponds to a graph with
1. the vertex set
V=V 0 ∪V 1 ={g i|gi ∈G, i∈ {0,1}}
2. the edge setE=E A ∪E B, where
EA ={(g i,(ag) j)|a∈A, g i ∈G, i̸=j}and
EB ={(g i,(gb) j)|b∈B, g i ∈G, i̸=j}.
This construction yields a 2D complex with faces, as
4-cycles of the graph, of the form
{gi,(ag) j,(gb) j,(agb) i |i, j∈ {0,1}, i̸=j}.
In order to ensure that the vertices opposite each other
in the faces of the complex are distinct, elements ofA
andBmust not be conjugates of each other.
Definition 2.LetGbe a finite group and letA, B⊆G
such that⟨A, B⟩=G. If
∀a∈A, b∈B, g∈G, ag̸=gb
the left-right Cayley complexΓ(G, A, B)is said to satisfy
the total non-conjugacy condition (TNC).
Fulfillment of the total non-conjugacy condition en-
sures a 2D complex structure and that each vertex has
degree ∆ A + ∆ B, where ∆ A =|A|and ∆ B =|B|
[13]. For the sake of simplicity, we will usually choose
∆A = ∆B = ∆.

## PDF page 3

3
2. Classical Codes
Classical linear block codes use redundancy to encode
logical information and detect and correct errors. An
[n, k]-code, that is, a classical code encodingkbits of in-
formation usingn > kbits, is given by a binaryk×ngen-
erator matrixG, whose rows are a set of codewords that
span the code space. Alternatively, classical codes can be
defined by their parity check matrix,H, an (n−k)×n
binary matrix whose rows represent the parity checks of
the code used to detect errors. These two matrices sat-
isfy the constraintGH T = 0. In the following we will
specify a codeCby its generator matrix which we will
also callC.
In order to defineX- andZ-type parity checks on the
LRCC for the quantum Tanner code, we require a pair
of binary linear classical codes (C A, CB). The codeC A
encodesρ∆ A logical bits in ∆ A bits, for some 0< ρ <1,
and so its generator matrix has dimensionsρ∆ A ×∆ A.
The codeC B encodes (1−ρ)∆ B logical bits in ∆ B bits.
We construct the tensor codesC 0 =C A ⊗C B andC 1 =
C ⊥
A ⊗C ⊥
B , whereC ⊥
i represents the dual code, which can
be obtained by switching the roles of the generator and
parity check matrices. We recall that dim(C i ⊗C j) =
dim(Ci)dim(Cj) andd(C i ⊗C j) =d(C i)d(Cj) for the
minimum distances of the codes,C i, andC j, respectively.
3. Quantum Tanner Codes
In order to construct a quantum Tanner code, we se-
lect a left-right Cayley complex Γ(G, A, B) based on a
finite non-abelian groupG. We denote the set of faces
of Γ(G, A, B) incident to a given vertexvasQ(v) and
the complete set of faces of the LRCC asQ. We note
thatQ(v) is uniquely determined by a pair (a, b) for ev-
eryv∈V. The qubits of the quantum code are placed
on the faces of the LRCC, so that the number of qubits
of the code is equal|Q|. We choose two classical codes
CA andC B as described above and defineC 0 andC 1 as
previously mentioned. Since the number of columns of
CA is ∆A we can label the columns ofC A with elements
ofA. Having chosen a fixed association of the columns
with elements ofAwe will use the notation that the code-
words ofC A are binary vectorsβ A ∈F A
2 . Likewise we
can associate the columns ofC B with elements ofBand
given such a mapping we will say that codewords ofC B
are binary vectorsβ B ⊂F B
2 . The chosen correspondence
of bits of two classical codes to group elements yields a
labeling of the columns of the tensor codesC 0 andC 1
consisting of pairs (a, b)∈A×B.
In order to construct stabilizer generators on
Γ(G, A, B) using the classical codesC0 andC 1, we can
define a function
ϕv :A×B→Q(v),(a, b)7→ {v, av, vb, avb},
which maps a pair of group generators to the face in
Q(v) that it uniquely defines. It is easy to show that
ϕv is bijective. For each basis elementβ∈β 0 of
C0 we can associate a set of pairs of group generators
Z(β) ={(a, b)|β (a,b) = 1}corresponding to nonzero en-
tries ofβ. Each generator of theZstabilizers of the
quantum Tanner code is specified by a choice of vertex
v∈V 0 and classical codewordβsuch that theZsta-
bilizer generator has support equal to the set of faces
ϕv(Z(β)). We can characterize this stabilizer generator
by a binary vectorx∈F Q
2 where the|Q|qubits of the
classical code are labelled by faces of the LRCC. Thus
for a givenZ-stabilizer generator of the quantum code
x|Q(v) is equal to a basis elementβofC 0, based on a
fixed ordering of the faces, and 0 elsewhere. The result-
ing dim(C 0)|V0|Z-type stabilizer generators correspond
to codewords ofC 0 locally at each vertex. We repeat the
same process for verticesv∈V 1 and basis elements ofC 1
to produce dim(C1)|V1|X-type stabilizers at each vertex
of the partition.
This construction naturally yields a valid CSS code
with low-weight stabilizer generators. In particular, it
is shown in [14] that all stabilizer generators of opposite
type commute pairwise with one another, meaning the
CSS code orthogonality constraintC X ⊂C ⊥
Z is fulfilled.
A family of codes is said to exhibit the LDPC property
when the number of qubits involved in every stabilizer
generator and the size of the support of each stabilizer
generator are bounded above by a constant that does
not grow with the size of the code. Due to the fact that
|Q(v)|= ∆ 2 for all verticesv∈V, all stabilizers have
maximum weight ∆ 2. Additionally, we can count the
number of parity checks that each qubit is involved in
by noting that each face of the LRCC is adjacent to four
vertices and each vertex corresponds to either anXsta-
bilizer generator or aZstabilizer generator. These gen-
erators arise from the parity check matrices ofC 1 andC 0
respectively, which haveρ(1−ρ)∆ 2 rows. So each qubit
is involved in a maximum of 4ρ(1−ρ)∆ 2 stabilizer gen-
erators. Defining a family of quantum Tanner codes by
fixing ∆ and choosing groupsGsuch that|G| → ∞, it is
clear that any family of quantum Tanner codes exhibits
the LDPC property.
An examination of the parameters of quantum Tan-
ner codes in terms of the properties of the LRCCs and
classical codes from which they are constructed proves
they are also asymptotically good. By a simple counting
argument, we haven= ∆ 2|G|/2. Counting theX- and
Z-type stabilizers yieldsk≥ |V0|dim(C 0) +|V1|dim(C 1).
Recalling the dimensions ofC A andC B, it is easy to show
that dim(C 0) = dim(C 1) =ρ(1−ρ)∆ 2. This, in turn,
means that
k≥4ρ(1−ρ)n.(1)
Current lower bounds on the distances of quantum
Tanner codes which scale linearly withnhinge on the
expansion properties of the left-right Cayley complexes
and the distance and robustness of the classical codes un-
derlying them. In particular, LRCCs, when considered as
graphs, must be Ramanujan or nearly-Ramanujan. Anr-

## PDF page 4

4
regular graphGis said to be Ramanujan ifλ 1 ≤2 √r−1,
whereλ 1 denotes the second largest eigenvalue (in abso-
lute terms) of the adjacency matrix of the graphG. The
Ramanujan property represents maximal spectral expan-
sion, which can be thought of as the ideal balance be-
tween connectivity and edge-sparsity of a graph. The
classical codes and their duals in these results are as-
sumed to have sufficiently large minimal distances and
the dual tensor codesC ⊥
0 andC ⊥
1 are assumed to exhibit
a property calledκ-robustness. The former condition is
common in product constructions such as [8] and [28].
The latter appears in [13] and [12], and it has been shown
thatκ-robustness can be achieved with high probability
whenC A andC B are chosen randomly [29] [30].
By requiringC A, CB, C⊥
A andC ⊥
B to have distance at
leastδ∆ for someδ >0 andC ⊥
0 andC ⊥
1 to beκ-robust,
is is shown in [31] that the distance of the resulting quan-
tum Tanner code can be bounded by
d≥ δ2κ2
256∆ n,(2)
a tighter bound than the original one presented in [14].
Thus, under these conditions, the parameters of these
codes scale as [[n,Θ(n),Θ(n)]], meaning they are asymp-
totically good qLDPC codes.
C. Belief Propagation and Ordered-Statistics
Decoding
Error syndromes resulting from stabilizer measure-
ments are passed to a decoder that aims to provide a
suitable correction. In the classical setting, this trans-
lates to finding a minimum-weight estimate of the error
esuch that
He=s(3)
for the parity check matrixHof the code and a syndrome
s. For classical LDPC codes, the belief propagation (BP)
decoder [32] uses bit-wise marginal probabilities to de-
liver the most likely minimum-weight error. More specif-
ically, the decoder begins by computing a marginal dis-
tribution for each bit of the error vector
P(e i = 1) =
X
j∈[n]\{i}
P(e 1, e2, . . . , ei = 1, . . . , en|s) (4)
given the syndromes. This is the probability, givens,
that an error has occurred on thei th bit. This marginal
distribution is called thesoft decisionfor the bite i. The
hard decisionˆeis the error vector obtained by setting
ˆei = 1 ifP(e i = 1)≥1/2 and 0 otherwise. For some
codes, the soft decision can be computed efficiently via
factorization informed by the structure of the code’s fac-
tor graph. In each iteration of the decoder, the marginal
distributionP(e i = 1) is updated for each bit via the fac-
tor graph factorization and the validity of corresponding
hard decision vector ˆeis verified viaH·ˆe=s. This
process is repeated a maximum ofntimes, wherenis
the length of the code. If the equationH·ˆe=sis at
any point satisfied, the algorithm has converged, and ˆe
is returned as the correction.
In the context of quantum CSS codes with uncorre-
latedXandZerrors, it first appears as if this process
can be applied to theX- andZ-components of the code
separately. However, this overlooks the issue of quantum
degeneracy, which is rooted in the uniquely quantum phe-
nomenon of superposition. In the quantum setting, the
goal is to return the state to the code space, meaning
that operations equivalent up to a stabilizer are equally
valid. When the BP decoder is applied directly to quan-
tum codes, multiple equivalent corrections are assigned
high probabilities, leading to a scenario called split belief
[33]. The BP decoder returns the sum of these correc-
tions, which no longer returns the state to the code space
and the decoding fails.
To circumvent the issue of degeneracy and non-
convergent BP decoding, Panteleev and Kalachev [10]
proposed usingordered statistics decoding(OSD) as a
post-processing measure. First introduced for classical
codes in Ref. [34], the OSD algorithm uses submatrix in-
version to deliver estimates for errors that have occurred.
More specifically, this means selecting a linearly indepen-
dent subset of columns of the parity check matrixH, de-
noted [I] and termed theinformation set. The submatrix
ofHconsisting only of these columnsH [I] can be inverted
to give a solutione [I] =H −1
[I] ·s. Because each choice of
[I] yields a unique solutione [I] , the issue of degeneracy
can be avoided.
When used as a post-processing step following BP de-
coding on theX- orZ-component of a quantum code, the
soft decision can be used to inform the choice of the infor-
mation set [I]. The indices of a set [n], which correspond
to the qubits of the code, are first ordered according to
the soft information from most to least likely to have been
flipped, yielding an information set [L]. The columns of
the parity check matrixHare reordered according to the
new ordering given by [L], denotedH [L]. The OSD step
is applied toH [I] , where [I] is the set of the first rank(H)
columns ofH [L], to yielde [I] =H −1
[I] ·s. The remainder of
the bits, i.e., those which are not elements of [I], are set
to 0 and the bits of the solutione= (e [I] ,0) are returned
to their original ordering. This process, called OSD-0
post-processing, can be generalized using a greedy algo-
rithm to assign highly likely values to the remainder of
the qubits not in [I] based on the soft information passed
down from the BP step. This is known as higher-order
OSD. One variation of this method is called the “com-
bination sweep” strategy [35] and prioritizes low weight
configurations for some numberλ≤n− |[I]|of the re-
maining bits.

## PDF page 5

5
III. EXPLICIT INST ANCES OF QUANTUM
T ANNER CODES
In this section, we provide the details for our construc-
tions of explicit instances of quantum Tanner codes, in-
cluding the groups and ∆ values selected for the left-
right Cayley complexes and considerations related to the
choice of classical codes. We examine the parameters and
stabilizer weights of the explicit instances of these codes
and examine the effects of the properties of the underly-
ing LRCCs and classical codes on the properties of the
resulting quantum codes.
In order to build explicit instances of quantum Tan-
ner codes small enough for meaningful numerical sim-
ulations and potential applications on near-term hard-
ware, the requirements for asymptotically good param-
eters must be balanced with more practical considera-
tions. Spectral expansion properties are emphasized in
Ref. [14] and necessary for a lower bound on the dis-
tance that is linear in the length of the coden. Be-
cause LRCCs and Cayley graphs constructed from the
same group and generating sets are strongly related (see
Appendix A), it is sufficient to consider the expansion
properties of Cayley graphs, which are well-studied. The
first explicit Ramanujan Cayley graphs described in the
literature were constructed with projective special linear
(PSL) groups in Ref. [36]. These, however do not pro-
vide small LRCCs that are suitable for constructing codes
small enough for numerical simulations. Hiranoet al.[37]
show that Frobenius groups, when paired with generat-
ing sets of certain sizes, also yield Ramanujan Cayley
graphs. Among these, dihedral groupsD n, which are of
order 2nand represent the symmetries of ann-gon, prove
most suitable based on their slow growth innand Ra-
manujan properties at scale. Specifically, we select the
dihedral groupsD 4, D6, D8, D10 and random symmetric
sets of generators of size ∆ to generate LRCCs. These
∆ values are limited by the cardinality of the groupG,
as they must satisfy ∆<|G|/2, as well as certain group-
theoretic properties. Further details can be found in Ap-
pendix B. We note that similar considerations for group
choice were made in Ref. [21].
We construct explicit instances of quantum Tanner
codes by combining these left-right Cayley complexes
based on dihedral groups with pairs of classical codes.
Finding code pairs with appropriate dimensions severely
restricted the search, particularly within the realm of
code families such as Reed-Muller codes. Instead, we
use classical codes obtained by randomly generating a
matrixPof dimensionsρ∆×∆(1−ρ) and constructing
the generator and parity check matrices asG= [I ρ∆|P]
andH= [P T |I∆(1−ρ)]. We computed the minimum dis-
tances of these codes and then tested for robustness, one
of the properties central to the argument for asymptot-
ically good parameters in the resulting quantum codes.
Ultimately, robustness appeared to have little to no im-
pact on the parameters of the resulting quantum Tanner
codes, while large minimal distances were necessary for
high-distance quantum codes. Further details related to
the construction of these explicit instances can be found
in Appendix C.
A selection of the quantum Tanner codes resulting
from this construction is presented in Table I. The first
column lists the parameters of the codes, which vary in
the number of physical qubits from 36 to 250. The rel-
ative distances and encoding rates have been included
to facilitate a comparison across codes and with other
families of qLDPC codes. Ideally, error-correcting codes
exhibit both a high relative distance and a high encod-
ing rate, meaning, respectively, that they can correct
high-weight errors and encode more logical qubits with
less space overhead. There is a noticeable trade-off be-
tween encoding rate and relative distance; while these
codes exhibit high encoding rates around 20%, they have
slightly lower relative distances than other instances of
qLDPC codes such as the bivariate bicycle codes con-
structed in Refs. [15, 38] and lifted quantum Tanner codes
[21], though the latter family of codes only encodes two
logical qubits. We note here that all minimum distances
are given by upper bounds computed by theBP+OSDde-
coder from theLDPCpackage [35] and verified by theGAP
packageQDistRnd[39].
Constructing explicit instances of quantum Tanner
codes also allows us to qualitatively examine the impact
of the properties of the LRCC and classical codes on the
parameters of the resulting quantum codes. While the
expansion properties of the underlying left-right Cayley
complexes and the robustness of the classical code pairs
have no clear impact on the parameters of the result-
ing quantum Tanner codes, noticeable trends emerge re-
lated to the ∆ values and minimal distances of the clas-
sical codes. Table II lists the largest distances achieved
by our quantum Tanner codes as a function of the ∆
values and minimal distances of the classical code pairs
(CA, CB), denoted (d A, dB), with which they were con-
structed. Two clear patterns emerge from this table.
Firstly, we observe that the distances of the quantum
Tanner codes grow with the distances of the classical
codes. This is the case for many product constructions of
qLDPC codes, such as hypergraph product codes [8], in
which the distances of the quantum codes are bounded
in some way by the distances of the underlying classical
codes. Secondly, and perhaps more subtly, the odd ∆
values yield quantum codes with larger distances, even
when the classical codes have smaller distances. It is un-
clear whether this is related to the choice of group or if
this is a more general pattern.
IV. NUMERICAL RESUL TS
In this section, we introduce the error models used for
numerical simulations and then investigate the pseudo-
thresholds under these error models of the codes pre-
sented in the previous section. We discuss simulation
results in the phenomenological and circuit-level noise

## PDF page 6

6
[[n, k, d]] Group ∆ Stabilizer Weights Encoding Rate (k/n) Relative Distance (d/n)
[[36, 8, 3]] D4 3 6 0.222 0.083
[[54, 11, 4]] D6 3 6 0.204 0.074
[[72, 14, 4]] D8 3 6 0.194 0.056
[[200, 10, 10]] D8 5 6, 8, 9, 12 0.05 0.05
[[250, 10, 15]] D10 5 6, 8, 9, 12 0.04 0.06
TABLE I. Parameters of a collection of quantum Tanner codes. The parameters of the codes are listed in the first column,
wheren,k, anddrepresent the number of physical qubits, or length, the number of logical qubits, or dimension, and distance
of the codes, respectively. The relative distance and encoding rate allow for a comparison between codes of different sizes across
families of codes. Stabilizer weights for smaller codes are limited to 6, while they double for larger codes.
(dA, dB)
∆ 3 4 5 6
(1,1) 1 1 3 3
(1,2) 1 1 4 3
(2,1) 3 2 7 5
(2,2) 3 2 10 6
(3,1) 4 3 8 6
(3,2) 4 3 15 7
(4,1) - 3 - 7
(4,2) - 4 - 10
TABLE II. The maximal distances of the quantum codes con-
structed are listed as a function of the ∆ value used in the
construction of the LRCCs (top row) and the minimal dis-
tances of the classical code pairs, denoted (d A, dB) (left col-
umn). Classical codes with higher distances appear to yield
quantum Tanner codes with higher distances. Additionally,
we see that these distances grow more quickly with odd ∆ val-
ues. Codes constructed with ∆ = 5 and classical pairs with
minimal distances (dA, dB)∈ {(4,1),(4,2)}did not yield valid
CSS codes.
settings and compare these with surface codes of similar
distance. Finally, we analyze the space-time overheads
of the codes to facilitate a comparison with their surface
code counterparts as well as other qLDPC codes. All
code and data can be found athttps://github.com/
RebKatRad/qTanner.git.
A. Error Models
In order to evaluate the error-correcting capabilities
of the explicit instances of quantum Tanner codes in the
context of fault-tolerant quantum computing, we perform
numerical memory experiments which capture their per-
formance in systems affected by different types of noise,
including noise in the syndrome extraction process it-
self. We go beyond the standard code capacity setting,
in which Pauli noise is applied to data qubits and per-
fect syndrome extraction is assumed, by introducing phe-
nomenological and circuit level noise. In the simulations,
data qubits are initialized in theX(Z) basis andN∈N
rounds of syndrome extraction are performed, wherein all
stabilizers of the code are measured using ancilla qubits
to yield a syndrome andNis chosen depending on the
type of experiment. Subsequently, all data qubits are
measured in theX(Z) basis in a final destructive round
of measurement, simulating logical measurement, from
which the stabilizer readout can be reconstructed.
The phenomenological noise model is a heavily simpli-
fied model used to study the effect of both data qubit and
measurement errors on the error correction capabilities of
a code. In each round of syndrome extraction, each data
qubit is independently subject to aZ(X)-type error with
probabilityp. In the firstNrounds of syndrome extrac-
tion, each stabilizer measurement independently reports
an incorrect result with the same probabilityp. The fi-
nal round of measurement is noiseless. Data-qubit errors,
which have accumulated across theNrounds, and mea-
surement errors have equivalent effects and potentially
result in a logical error, which is detected with perfect
precision due to the lack of measurement noise in the
final round of measurement.
The circuit-level noise model is more detailed and aims
to reproduce the noise exhibited by certain hardware
models. Each stabilizer measurement is performed using
an ancilla qubit together with two-qubit Clifford gates
performed between each data qubit in the support of the
stabilizer and the ancilla, and finally the ancilla qubit is
measured. In our simulations, we apply i.i.d. single- and
two-qubit Pauli errors with probabilitypfollowing non-
trivial single- and two-qubit Clifford gates, respectively,
and after reset operations. Data qubits idling during time
steps in which they are not being measured as well as
idling ancilla qubits exhibit errors with probabilityp/10,
simulating the common behavior that idling errors are
far less probable than other types [40].
Simulating circuit-level noise requires generating a cir-
cuit and inserting errors of the appropriate intensity at
right locations. To this end, we use theLDPCpackage
(version 1)1 [24] to generate generic circuits, usingStim
[41], for theXandZcomponents of our CSS codes and
specify the probabilities for each type of error. We note
1 Note that we used thecss code memory circuitfunctionality
recently introduced by Higgott that includes idling errors and
measures both types of stabilizers unlike previous versions.

## PDF page 7

7
that these syndrome extraction circuits have not been
optimized for quantum Tanner codes, a step we leave for
future work.
B. Simulation Results and Pseudo-Thresholds
Simulations provide insight into the performance of ex-
plicit codes at noise levels realistic for near-term devices
and facilitate a comparison with other qLDPC codes, in-
cluding the surface code. We use theBP+OSDdecoder
[35] to compute the logical error rates at a variety of
physical error rates in the presence of both measurement
and circuit-level noise. Logical error ratesL X andL Z
are computed separately for theXandZcomponents of
the code, respectively, and the overall logical error rate
is approximated by
pL = (LX +L Z −L X LZ)/N.(5)
For each distance-dcode, we performN=drounds of
syndrome extraction before measuring the data qubits
in the final round to determine the presence of a logical
error. In our simulations, we use theLDPCpackage [24] to
implement the min-sum variation of BP. We found that
the performance of the decoder was very sensitive to the
min-sum scaling factorα, with some values degrading
the quality of the results significantly, and we usedα=
0.625 as suggested in Ref. [10]. For the post-processing
step, we use OSD-9 with the combination strategy, which
outperformed all other OSD-λforλ∈ {1, . . . ,10}.
In Figure 1(a) we see that, with measurement noise,
all codes exhibit a logical error rate in the regime ofp L
ranging from 10 −7 to 10 −4 at a physical error rate of
p= 10 −3, a level considered achievable by small-scale
near-term hardware. Under circuit-level noise, Figure
1(b), logical error rates range from 10 −4 to 10 −2 at a
physical error rate ofp= 10 −3.
Figure 2 shows a comparison of the performances of
the quantum Tanner codes and surfaces codes of compa-
rable distance. In order to facilitate a comparison with
the [[200,10,10]] and [[250,10,15]] codes, the logical error
rates ofk= 10 copies of the surface codes were computed
via
p′
L = 1−(1−p L)k,(6)
wherep L is the logical error rate of a single copy of the
surface code encoding only a single logical qubit.
Pseudo-thresholds can be used to quantify the perfor-
mance of the quantum Tanner codes in the presence of
phenomenological and circuit level noise. The pseudo-
threshold is the point at which the error rate of the logi-
cal qubits is equal to that of the physical qubits. Below
this point, the system experiences sufficient suppression
of logical errors in the presence of physical noise. In or-
der to facilitate a comparison between physical and log-
ical error rates, we examine the logical error rate per
logical qubit. In the phenomenological case, we compute
the pseudo-threshold as the physical error ratepsatisfy-
ingp L(p) =kp, wherep L(p) is the per-round logical error
rate andkrepresents the number of encoded qubits. The
pseudo-thresholds of our quantum Tanner codes are re-
ported in Table III. Under phenomenological noise, these
vary in the range 1.3% to 6.3%.
[[n, k, d]] (phenomenological)
Pseudo-threshold
(circuit-level)
Pseudo-threshold
[[36, 8, 3]] 0.0634 0.0038
[[54, 11, 4]] 0.0382 0.0056
[[72, 14, 4]] 0.0300 0.0036
[[200, 10, 10]] 0.0198 0.0059
[[250, 10, 15]] 0.0133 0.0040
TABLE III. Pseudo-thresholds represent the break even
points wherep L(p) =kp(phenomenological) orp L(p) =
T kp/10 (circuit-level) for a physical error ratep, wherep L,
k, andTrepresent the logical error rate, number of logical
qubits, and depth of a single round of syndrome extraction,
respectively. Pseudo-thresholds are listed for the quantum
Tanner codes for both the phenomenological and circuit-level
noise settings.
In the case of circuit-level noise, we consider the break
even pointp L(p) =T kp/10, whereTis the number of
time steps, or depth, of a single round of syndrome ex-
traction. We divide by 10 due to the fact that we consider
idling errors with intensityp/10 in this error model. As
can be seen in Table III, the pseudo-thresholds of quan-
tum Tanner codes in the circuit level model are lower
than those in the phenomenological model by approxi-
mately one order of magnitude. Both sets of pseudo-
thresholds remain competitive with those displayed by
other qLDPC codes. These results suggest that quan-
tum Tanner codes are able to suppress errors effectively
on near-term devices consisting of around 200 physical
qubits experiencing physical error rates on the order of
10−3.
C. Overhead Comparison
We examine the space-time overheads of the explicit
quantum Tanner codes generated here and compare these
estimates to those incurred by surface codes which yield
similar logical error rates under both phenomenological
and circuit level noise. The space overhead is computed
as the total number of physical qubitsn+n anc, where
nanc represents the number of ancilla qubits required for
the syndrome extraction circuit. In our case, this co-
incides with the number of stabilizers of the code, but
can potentially be reduced in certain architectures, such
as trapped ions [16]. The time overhead is taken as the
product of the depth of the syndrome extraction circuit
and the number of syndrome extraction rounds. Letd x
represent the maximal weight of any row or column in the
X-parity check matrixH X andd z the maximal weight

## PDF page 8

8
FIG. 1. Performance of our quantum Tanner codes from Table I in simulations with (a) phenomenological noise, and (b)
circuit-level noise. Logical error rate is plotted as a function of physical error rate forN=drounds of syndrome extraction, for
code distanced. Error bars were computed for 95% binomial proportion confidence intervals viap L = ˆpL ± 1.645√η
q ηsηf
η2 , where
ηrepresents the total number of shots andη s andη f the number of successes and failures, respectively. For the combinedp L as
computed in Eq. (5),η=η x +η z. Here,η x, ηz ∈[10 5,10 9], depending on the number of errors encountered. Note the distinct
ranges of physical error rates in plots (a) and (b).
FIG. 2. A comparison of the performances of quantum Tanner
codes with 10 logical qubits andk= 10 copies of various
surface codes of comparable distance. The logical error rates
of the surface codes were computed viap ′
L = 1−(1−p L)k for
k= 10, wherep L is the logical error rate of a single surface
code encoding one logical qubit.
of any row or column inH Z. Then the depth of a single
round of syndrome extraction, in which we measure both
sets of stabilizers, is bounded from above byd x +d z. As
such, we can estimate the time overhead as the product
N(d x +d z), where we doN=drounds of syndrome
extraction for a distance-dcode. Overall, we have
OST = (n+n anc)(dx +d z)d.(7)
Table IV summarizes the overhead findings and offers
a comparison with surface codes of similar distance and
performance. Quantum Tanner codes and distanced-
surface codes are listed in the first column and space-
time overheads per logical qubit are listed for both sets of
codes in the second column. For smaller codes, quantum
Tanner codes require up to 50% less space-time overhead
per logical qubit while achieving a level of error suppres-
sion comparable with their distance-3 and -4 surface code
counterparts. At this scale, quantum Tanner codes rep-
resent a more efficient and equally effective alternative to
the surface code.
On the other hand, surface codes of larger distances
clearly outperform the 200- and 250-qubit quantum Tan-
ner codes in both the phenomenological and circuit-level
noise settings. However, this is achieved with up to
triple the space-time overhead, despite the high stabi-
lizer weights of the [[200,10,10]] and [[250,10,15]] codes,
making the quantum Tanner codes more efficient but less
effective than surface codes in this regime. We note that
these overheads may further be reduced by optimizing
the syndrome extraction circuits and exploring single-
shot error correction, a property which quantum Tanner
codes have been proven to exhibit under adversarial noise
[42].

## PDF page 9

9
Code Space-time overhead per logical qubit
pL/katp= 10 −3
(phenomenological)
pL/katp= 10 −3
(circuit-level)
[[36, 8, 3]] 612 1.71×10 −5 (±6×10 −7) 6.52×10 −4 (±6×10 −6)
[[54, 11, 4]] 891 4.1×10 −6 (±1×10 −7) 2.38×10 −4 (±3×10 −6)
[[72, 14, 4]] 933 1.12×10 −5 (±1×10 −7) 4.83×10 −4 (±3×10 −6)
[[200, 10, 10]] 16 464 1.00×10 −7 (±8×10 −9) 8.2×10 −5 (±2×10 −6)
[[250, 10, 15]] 30 870 5.3×10 −8 (±5×10 −9) 2.44×10 −5 (±9×10 −7)
d= 3 s.c. 600 3.0×10 −5 6.9×10 −4
d= 4 s.c. 1568 5.0×10 −6 2.6×10 −4
d= 5 s.c. 3240 8.0×10 −7 4.8×10 −5
d= 7 s.c. 9464 2.9×10 −9 2.9×10 −6
d= 9 s.c. 20 808 2×10 −10 1×10 −6
d= 15 s.c. 100 920 2.3×10 −18∗ 2.2×10 −10
*This value is an approximation based on a fitting of logical error rates computed at higher physical error rates.
TABLE IV. A comparison of the space-time overheads of quantum Tanner and surface codes of comparable distance and logical
error rate per logical qubit. The surface codes have parameters [[L 2,1, L]]. The valuep L/kwas computed using the BP+OSD
decoder withdrounds of syndrome extraction in the presence of phenomenological and circuit-level noise for both sets of codes.
V. CONCLUSION AND FUTURE WORK
In this work, we have constructed a number of explicit
instances of quantum Tanner codes, a family shown to
have asymptotically good parameters. The codes were
constructed using dihedral groups and random pairs of
classical codes and exhibit high encoding rates and rel-
ative distances. A numerical analysis conducted with
the BP+OSD decoding revealed relatively high pseudo-
thresholds, both in the phenomenological and circuit
level noise models, and good suppression of logical errors
in thep= 10 −3 physical error rate regime. Small codes
exhibited particularly low overheads when compared to
surface codes, due in part to their low stabilizer weights.
The overall performance of these codes suggests that they
are well-suited to experimental implementation on near-
term hardware with around 200 qubits and physical er-
ror rates aroundp= 10 −3. In particular, this includes
trapped-ion-based hardware, which features high connec-
tivity and low idling error rates and therefore lends itself
well to the realization of quantum Tanner codes [16].
Further research is needed to identify a broader class of
codes with improved properties, and to explore the use
of these codes in an end-to-end fault tolerant architec-
ture for quantum computing. In order to find codes with
better parameters and lower stabilizer weights, the search
could be expanded to quantum Tanner codes constructed
with other Frobenius groups and different classes of clas-
sical codes, or based on non-left-right-Cayley complexes,
such as those in [43].
In order to further reduce the overhead incurred by
these codes, it would be of interest to explore optimizing
syndrome extraction circuits and developing a scheme
for single-shot decoding. Improving syndrome extrac-
tion circuits has the potential to reduce idling time and
the propagation of errors and improve the time overhead
required by the error-correcting codes by lowering the
depth of the circuits. A scheme of particular interest
can be found in Ref. [44]. The time overhead incurred
by quantum Tanner codes can also be reduced by taking
advantage of their single shot property, which was proven
for this code family in Ref. [42]. A potential approach to
this problem would be to develop an implementation of
the decoder proposed by Leverrier and Z´ emor for quan-
tum Tanner codes in Refs. [31] or [45]. Finally, it would
be of interest to explore logical gates on quantum Tanner
codes, which could be accomplished by examining their
automorphism groups as proposed in Ref. [46].
VI. ACKNOWLEDGMENTS
We would like to thank Oscar Higgott for many helpful
discussions and support in the numerical work. RKR is
grateful to Tom Scruby and Timo Hillmann for guidance
in earlier stages of the project. This work is supported by
the Australian Research Council via the Centre of Excel-
lence in Engineered Quantum Systems (EQUS) project
number CE170100009, and by the ARO through the
QCISS program W911NF-21-1-0007 and IARPA ELQ
program W911NF-23-2-0223. RKR is supported by the
Sydney Quantum Academy.

## PDF page 10

10
[1] P. W. Shor, Scheme for reducing decoherence in quantum
computer memory, Phys. Rev. A52, R2493 (1995).
[2] A. Y. Kitaev, Quantum computations: algorithms and
error correction, Russian Mathematical Surveys52, 1191
(1997).
[3] S. Krinner, N. Lacroix, A. Remm, A. Di Paolo, E. Genois,
C. Leroux, C. Hellings, S. Lazar, F. Swiadek, J. Her-
rmann, G. J. Norris, C. K. Andersen, M. M¨ uller, A. Blais,
C. Eichler, and A. Wallraff, Realizing repeated quantum
error correction in a distance-three surface code, Nature
605, 669–674 (2022), arXiv:2112.03708.
[4] Y. Zhao, Y. Ye, H.-L. Huang, Y. Zhang, D. Wu,
H. Guan, Q. Zhu, Z. Wei, T. He, S. Cao, F. Chen, T.-
H. Chung, H. Deng, D. Fan, M. Gong, C. Guo, S. Guo,
L. Han, N. Li, S. Li, Y. Li, F. Liang, J. Lin, H. Qian,
H. Rong, H. Su, L. Sun, S. Wang, Y. Wu, Y. Xu,
C. Ying, J. Yu, C. Zha, K. Zhang, Y.-H. Huo, C.-Y.
Lu, C.-Z. Peng, X. Zhu, and J.-W. Pan, Realization
of an error-correcting surface code with superconduct-
ing qubits, Physical Review Letters129, 10.1103/phys-
revlett.129.030501 (2022), arXiv:2112.13505.
[5] R. Acharya, D. A. Abanin, L. Aghababaie-Beni,
I. Aleiner,et al., Quantum error correction below the
surface code threshold, Nature638, 920–926 (2024),
arXiv:2408.13687.
[6] N. P. Breuckmann and J. N. Eberhardt, Quantum low-
density parity-check codes, PRX Quantum2, 040101
(2021), arXiv:2103.06309.
[7] M. Freedman, D. Meyer, and F. Luo, Z2-systolic free-
dom and quantum codes, inMathematics of Quantum
Computation(CRC Press, 2002) pp. 287–320, publisher
Copyright:©2002 by Chapman & Hall/CRC.
[8] J.-P. Tillich and G. Zemor, Quantum LDPC codes
with positive rate and minimum distance proportional
to the square root of the blocklength, IEEE Trans-
actions on Information Theory60, 1193–1202 (2014),
arXiv:0903.0566.
[9] M. B. Hastings, J. Haah, and R. O’Donnell, Fiber bundle
codes: breaking the n 1/2 polylog(n) barrier for quantum
LDPC codes, inProceedings of the 53rd Annual ACM
SIGACT Symposium on Theory of Computing, STOC
’21 (ACM, 2021) p. 1276–1288, arXiv:2009.03921.
[10] P. Panteleev and G. Kalachev, Degenerate quantum
LDPC codes with good finite length performance, Quan-
tum5, 585 (2021), arXiv:1904.02703.
[11] N. P. Breuckmann and J. N. Eberhardt, Balanced prod-
uct quantum codes, IEEE Transactions on Information
Theory67, 6653–6674 (2021), arXiv:2012.09271.
[12] P. Panteleev and G. Kalachev, Asymptotically good
quantum and locally testable classical LDPC codes
(2022), arXiv:2111.03654 [cs.IT].
[13] I. Dinur, S. Evra, R. Livne, A. Lubotzky, and S. Mozes,
Locally testable codes with constant rate, distance, and
locality (2021), arXiv:2111.04808 [cs.IT].
[14] A. Leverrier and G. Z´ emor, Quantum Tanner codes,
in2022 IEEE 63rd Annual Symposium on Founda-
tions of Computer Science (FOCS)(2022) pp. 872–883,
arXiv:2202.13641.
[15] S. Bravyi, A. W. Cross, J. M. Gambetta, D. Maslov,
P. Rall, and T. J. Yoder, High-threshold and low-
overhead fault-tolerant quantum memory, Nature627,
778–782 (2024), arXiv:2308.07915.
[16] M. Ye and N. Delfosse, Quantum error correction for long
chains of trapped ions (2025), arXiv:2503.22071 [quant-
ph].
[17] H.-K. Lin and L. P. Pryadko, Quantum two-block
group algebra codes, Phys. Rev. A109, 022407 (2024),
arXiv:2306.16400.
[18] N. Koukoulekidis, F. ˇSimkovic IV, M. Leib, and F. R. F.
Pereira, Small quantum codes from algebraic extensions
of generalized bicycle codes (2024), arXiv:2401.07583
[quant-ph].
[19] A. Grospellier and A. Krishna, Numerical study of hy-
pergraph product codes (2019), arXiv:1810.03681 [quant-
ph].
[20] O. Higgott and N. P. Breuckmann, Improved single-
shot decoding of higher-dimensional hypergraph-
product codes, PRX Quantum4, 020332 (2023),
arXiv:2206.03122.
[21] V. Guemard and G. Z´ emor, Moderate-length lifted quan-
tum Tanner codes (2025), arXiv:2502.20297 [quant-ph].
[22] T. R. Scruby, T. Hillmann, and J. Roffe, High-threshold,
low-overhead and single-shot decodable fault-tolerant
quantum memory (2024), arXiv:2406.14445 [quant-ph].
[23] N. P. Breuckmann and V. Londe, Single-shot decoding of
linear rate LDPC quantum codes with high performance,
IEEE Transactions on Information Theory68, 272–286
(2022), arXiv:2001.03568.
[24] J. Roffe, LDPC: Python tools for low density parity check
codes (2022).
[25] D. Gottesman,Stabilizer Codes and Quantum Error Cor-
rection, Ph.D. thesis, California Institute of Technology
(1997), arXiv:quant-ph/9705052.
[26] A. Cayley, Desiderata and suggestions: No. 2. the theory
of groups: Graphical representation, American Journal
of Mathematics1, 174 (1878).
[27] A. Steane, Multiple particle interference and quantum er-
ror correction, Proceedings of the Royal Society of Lon-
don. Series A: Mathematical, Physical and Engineering
Sciences452, 2551–2577 (1996), arXiv:9601029.
[28] A. A. Kovalev and L. P. Pryadko, Quantum kronecker
sum-product low-density parity-check codes with finite
rate, Phys. Rev. A88, 012311 (2013).
[29] I. Dinur, M.-H. Hsieh, T.-C. Lin, and T. Vidick, Good
quantum ldpc codes with linear time decoders, inPro-
ceedings of the 55th Annual ACM Symposium on The-
ory of Computing, STOC 2023 (Association for Comput-
ing Machinery, New York, NY, USA, 2023) p. 905–918,
arXiv:2206.07750.
[30] G. Kalachev and P. Panteleev, Two-sided robustly
testable codes (2023), arXiv:2206.09973 [cs.IT].
[31] A. Leverrier and G. Z´ emor, Decoding quantum Tanner
codes, IEEE Trans. Inf. Theor.69, 5100–5115 (2023),
arXiv:2208.05537.
[32] F. Kschischang, B. Frey, and H.-A. Loeliger, Factor
graphs and the sum-product algorithm, IEEE Transac-
tions on Information Theory47, 498 (2001).
[33] B. Criger and I. Ashraf, Multi-path Summation for De-
coding 2D Topological Codes, Quantum2, 102 (2018),
arXiv:1709.02154.
[34] M. Fossorier and S. Lin, Soft-decision decoding of linear
block codes based on ordered statistics, IEEE Transac-

## PDF page 11

11
tions on Information Theory41, 1379 (1995).
[35] J. Roffe, D. R. White, S. Burton, and E. Campbell, De-
coding across the quantum low-density parity-check code
landscape, Physical Review Research2, 10.1103/phys-
revresearch.2.043423 (2020), arXiv:2005.07016.
[36] A. Lubotzky, R. Phillips, and P. Sarnak, Ramanujan
graphs, Combinatorica8, 261 (1988).
[37] M. Hirano, K. Katata, and Y. Yamasaki, Ramanu-
jan cayley graphs of frobenius groups, Bulletin of the
Australian Mathematical Society94, 373–383 (2016),
arXiv:1503.04075.
[38] M. H. Shaw and B. M. Terhal, Lowering connectiv-
ity requirements for bivariate bicycle codes using mor-
phing circuits, Phys. Rev. Lett.134, 090602 (2025),
arXiv:2407.16336.
[39] L. P. Pryadko, V. A. Shabashov, and V. K. Kozin, Qdis-
trnd: A GAP package for computing the distance of
quantum error-correcting codes, Journal of Open Source
Software7, 4120 (2022), arXiv:2308.15140.
[40] J. Conrad, C. Chamberland, N. P. Breuckmann, and
B. M. Terhal, The small stellated dodecahedron code
and friends, Philosophical Transactions of the Royal Soci-
ety A: Mathematical, Physical and Engineering Sciences
376, 20170323 (2018), arXiv:1712.07666.
[41] C. Gidney, Stim: a fast stabilizer circuit simulator, Quan-
tum5, 497 (2021), arXiv:2103.02202.
[42] S. Gu, E. Tang, L. Caha, S. H. Choe, Z. He, and
A. Kubica, Single-shot decoding of good quantum LDPC
codes, Communications in Mathematical Physics405,
10.1007/s00220-024-04951-6 (2024), arXiv:2306.12470.
[43] O. A. Mostad, E. Rosnes, and H.-Y. Lin, Generalizing
quantum Tanner codes (2024), arXiv:2405.07980 [cs.IT].
[44] M. A. Tremblay, N. Delfosse, and M. E. Bever-
land, Constant-overhead quantum error correction
with thin planar connectivity, Physical Review Let-
ters129, 10.1103/physrevlett.129.050504 (2022),
arXiv:2109.14609.
[45] A. Leverrier and G. Z´ emor, Efficient decoding up to a
constant fraction of the code length for asymptotically
good quantum codes (2022), arXiv:2206.07571 [quant-
ph].
[46] H. Sayginel, S. Koutsioumpas, M. Webster, A. Ra-
jput, and D. E. Browne, Fault-tolerant logical clifford
gates from code automorphisms (2025), arXiv:2409.18175
[quant-ph].
[47] H. Weyl, Das asymptotische verteilungsgesetz der eigen-
werte linearer partieller differentialgleichungen (mit einer
anwendung auf die theorie der hohlraumstrahlung),
Mathematische Annalen71, 441 (1912).
[48]GAP – Groups, Algorithms, and Programming, Version
4.13.1, The GAP Group (2024).
Appendix A: Expansion properties of left-right
Cayley complexes
We examine more closely the spectral expansion prop-
erties of left-right Cayley complexes in terms of related
Cayley graphs. LetGbe a group and letA, B⊂G
be sets of generators ofG. Further, letCay(G, A) and
Cay(G, B) be Cayley graphs based on the left action ofA
and the right action ofB, respectively, on elements ofG.
Then the second largest eigenvalue of the left-right Cay-
ley complex, when viewed as a graph, is closely related to
the minimal second largest eigenvalue ofCay(G, A) and
Cay(G, B).
Lemma 1.LetGbe a finite group and letA, B⊂G
such that⟨A, B⟩=Gand|A|=|B|= ∆. LetCay(G, A)
andCay(G, B)denote the Cayley graphs based on left
and right actions onG, respectively. Letλ A
2 andλ B
2
denote the second largest eigenvalues of their respective
adjacency matrices. LetΓ(G, A, B)denote the left-right
Cayley complex defined as in Def. 1. Then we have
λLRCC
2 ≤∆ + min{λ a
2, λb
2},
whereλ LRCC
2 denotes the second largest eigenvalue of
Γ(G, A, B).
Proof.LetA A andA B denote the adjacency ma-
trices ofCay(G, A) andCay(G, B), respectively.
Then spec(A A) ={λ a
1, λa
2, . . . , λa
n}and spec(A B) =
{λb
1, λb
2, . . . , λb
n}, where ∆ =λ m
1 > λm
2 > . . . > λm
n for
m∈ {a, b}andn=|G|.
Consider the graphX(G, A, B) which has vertices cor-
responding to a single copy of the elements ofGand
edges of the form (g, ag) and (g, gb). The adjacency ma-
trix ofX(G, A, B) is thenC=A A +A B. Note that
AA andA B have no overlapping entries due to the total
non-conjugacy condition. Due to Weyl [47], we have
λC
i+j−1 ≤λ a
i +λ b
j,
sinceA A andA B are both Hermitian as symmetric ma-
trices containing only real entries. This, in turn, means
that
λC
2 ≤min{λ a
1 +λ b
2, λa
2 +λ b
1}= ∆ + min{λ a
2, λb
2}.
Finally, as the bipartite double cover ofX(G, A, B), the
adjacency matrix of Γ(G, A, B) is of the form
AΓ =

0C
C0

.
It is easy to show that spec(A Γ) ={±λ|λ∈spec(C)},
so we can conclude that
λLRCC
2 ≤∆ + min{λ a
2, λb
2}.
Appendix B: Restrictions on∆values for the
construction of LRCCs
There are a number of general and group-specific lim-
itations on the ∆ values which can be used to con-
struct left-right Cayly complexes that fulfill the total
non-conjugacy condition from Def. 2. In particular, LR-
CCs constructed based on dihedral groupsD n withnodd
and odd values of ∆ violate the TNC condition.

## PDF page 12

12
Lemma 2.LetGbe a group and letA, B⊂Gsuch
that⟨A, B⟩=Gand|A|=|B|= ∆. IfA∩B̸=∅
then the LRCCΓ(G, A, B)does not satisfy the total non-
conjugacy condition.
Proof.We haveA∩B̸=∅=⇒ ∃a∈A, b∈B:a=
b=⇒ae=a=b=before∈Gthe identity element.
This violates the TNC condition.
Corollary 2.1.In order to generate a valid LRCC which
fulfills the TNC, we must have∆<|G|/2.
Proof.If ∆ =|G|/2, theneis contained in eitherAor
B, which does not yield a valid Cayley graphX(G, A) or
X(G, B), respectively. If ∆>|G|/2, thenA∩B̸=∅and
the TNC condition is violated according to the lemma
above.
Lemma 3.Letn∈Nand∆∈[|D n|]be odd and
letA, B⊂D n be symmetric such that⟨A, B⟩=D n.
Then the LRCCΓ(G, A, B)does not satisfy the total non-
conjugacy condition.
Proof.SinceAandBare symmetric and of odd cardi-
nality, there exist an elementa∈Asuch thata=a −1
andb∈Bsuch thatb=b −1. Sinceaandbare elements
of the dihedral groupD n, they are reflections. As a con-
sequence of the Sylow theorem,nodd implies that all
reflections are conjugate to one another, meaning
g−1ag=b∀g∈G,
which violates the TNC condition.
Appendix C: Construction Details
We provide the specific generating sets and classical
code pairs for the quantum Tanner code constructions in
Table I. Thousands of random instances were generated,
and the best instances, in terms of encoding rate and
distance, are listed here. We use the standard represen-
tation of dihedral groups, whereD n =⟨r, s|s 2 =r n =
e, srs=r −1⟩. The symmetric sets of generators,Aand
B, as well as the resulting left-right-Cayley complexes
were generated usingGAP[48].
The classical codes are given by their parity check
matrices, whose rows represent parity checks and whose
columns correspond to bits. These were generated ran-
domly usingJulia. The quantum Tanner codes were
then constructed inJuliausing theLinearAlgebraand
AbstractAlgebrapackages. Distances were computed
and verified using theLDPCPython package and theGAP
packageQDistRnd.

## PDF page 13

13
[[n, k, d]] Group ∆ A B CA CB
[[36, 8, 3]] D4 3 {s, r, r3} {sr, sr3, r2}
1 1 1  
1 0 0
1 1 1

[[54, 11, 4]] D6 3 {r, r3, r5} {sr2, sr4, sr5}
1 1 1  
1 0 0
1 1 1

[[72, 14, 4]] D8 3 {s, sr4, r4} {sr, sr3, sr7}
1 1 1  
1 0 0
1 1 1

[[200, 10, 10]] D8 5 {sr6, r, r3, r5, r7} {sr, sr3, sr7, r2, r6}

1 0 0 1 1
0 0 1 1 1
 

1 0 0 0 1
0 0 0 1 1
1 1 1 0 0


[[250, 10, 15]] D10 5 {sr, r, r3, r7, r9,} {sr6, r2, r4, r6, r8}

1 0 0 1 1
0 1 1 1 1
 

1 0 0 0 1
0 0 0 1 1
1 0 1 0 1


TABLE V. Explicit instances of quantum Tanner codes are listed along with the specifications of their constructions. We
provide the sets of generatorsAandB, whose elements are given in terms of the standard representation of dihedral groups
Dn =⟨r, s|s 2 =r n =e, srs=r −1⟩. The last two columns contain the generator matrices of the classical codesC A andC B,
respectively, which were generated randomly.
