---
type: Research Paper
title: Ultrahigh Error Threshold for Surface Codes with Biased Noise
description: '- Pinned arXiv record: [1708.08474v3](https://arxiv.org/abs/1708.08474v3)'
resource: https://example.org/qec-arxiv-papers/resource/paper-1708-08474v3/sources%2Fmarkdown%2F1708.08474v3
tags:
- paper-1708-08474v3
- markdown
- rl
concept_id: concepts/paper-1708-08474v3/sources-markdown-1708.08474v3-7bc12558c3
concept_path: concepts/paper-1708-08474v3/sources-markdown-1708.08474v3-7bc12558c3.md
subject_iri: https://example.org/qec-arxiv-papers/resource/paper-1708-08474v3/sources%2Fmarkdown%2F1708.08474v3
ontology_class_iri: https://example.org/ontology/qec-arxiv-papers#Paper
ontology_version_iri: https://example.org/ontology/qec-arxiv-papers/1.0.0
source_id: paper-1708-08474v3
source_kind: markdown
source_path: sources/markdown/1708.08474v3.md
source_content_sha256: 102e84a2c54058fd267efbefc3ab8d0bab1258e30418c2e6625ccd6bbfdc9ebc
record_sha256: 01bd2f40cf375f17efb39c9a70b49c9a198edbc108eed6c9a3e7b2428d482a1e
source_refs:
- https://example.org/qec-arxiv-papers/provenance/record/paper-1708-08474v3/cc39ad95ff26ad5ef1374558
record_id: sources/markdown/1708.08474v3
---

# Ultrahigh Error Threshold for Surface Codes with Biased Noise

## Source citation

- Pinned arXiv record: [1708.08474v3](https://arxiv.org/abs/1708.08474v3)
- Authors: Tuckett, David K.; Bartlett, Stephen D.; Flammia, Steven T.
- PDF: [https://arxiv.org/pdf/1708.08474v3](https://arxiv.org/pdf/1708.08474v3)
- PDF SHA-256: `10546148e908dc786f95e16152b0d5e36f9625a89a45f3c6a1340b1ada732f39`
- Extracted pages: 6

The following text was extracted page by page from the pinned PDF. Page headings are stable evidence locators.

## PDF page 1

Ultrahigh Error Threshold for Surface Codes with Biased Noise
David K. Tuckett, 1 Stephen D. Bartlett, 1 and Steven T. Flammia 1, 2
1Centre for Engineered Quantum Systems, School of Physics,
The University of Sydney, Sydney, NSW 2006, Australia
2Center for Theoretical Physics, Massachusetts Institute of Technology, Cambridge, Massachusetts 02139, USA
(Dated: 15 December 2017)
We show that a simple modiﬁcation of the surface code can exhibit an enormous gain in the error correction
threshold for a noise model in which Pauli Z errors occur more frequently than X orY errors. Such biased
noise, where dephasing dominates, is ubiquitous in many quantum architectures. In the limit of pure dephasing
noise we ﬁnd a threshold of 43.7(1)% using a tensor network decoder proposed by Bravyi, Suchara and Vargo.
The threshold remains surprisingly large in the regime of realistic noise bias ratios, for example 28.2(2)% at a
bias of 10. The performance is, in fact, at or near the hashing bound for all values of the bias. The modiﬁed
surface code still uses only weight-4 stabilizers on a square lattice, but merely requires measuring products ofY
instead ofZ around the faces, as this doubles the number of useful syndrome bits associated with the dominant
Z errors. Our results demonstrate that large efﬁciency gains can be found by appropriately tailoring codes and
decoders to realistic noise models, even under the locality constraints of topological codes.
For quantum computing to be possible, fragile quantum in-
formation must be protected from errors by encoding it in a
suitable quantum error correcting code. The surface code [1]
(and related topological stabilizer codes [2]) are quite remark-
able among the diverse range of quantum error correcting
codes in their ability to protect quantum information against
local noise. Topological codes can have surprisingly large er-
ror thresholds—the break-even error rate below which errors
can be corrected with arbitrarily high probability—despite us-
ing stabilizers that act on only a small number of neighboring
qubits [3]. It is the combination of these high error thresh-
olds and local stabilizers that make topological codes, and the
surface code in particular, popular choices for many quantum
computing architectures.
Here we demonstrate a signiﬁcant increase in the error
threshold for a surface code when the noise is biased, i.e.,
when one Pauli error occurs at a higher rate than others. For
qubits deﬁned by nondegenerate energy levels with a Hamilto-
nian proportional toZ, the noise model is typically described
by a dephasing ( Z-error) rate that is much greater than the
rates for relaxation and other energy-nonpreserving errors.
Such biased noise is common in many quantum architectures,
including superconducting qubits [4], quantum dots [5], and
trapped ions [6], among others. The increased error thresh-
old is achieved by tailoring the standard surface code stabi-
lizers to the noise in an extremely simple way and by em-
ploying a decoder that accounts for correlations in the error
syndrome. In particular, using the tensor network decoder of
Bravyi, Suchara and Vargo (BSV) [7], we give evidence that
the error correction threshold of this tailored surface code with
pureZ noise is pc = 43.7(1)%, a fourfold increase over the
optimal surface code threshold for pureZ noise of 10.9% [7].
These gains result from the following simple observations.
For aZ error in the standard formulation of the surface code,
the stabilizers consisting of products ofZ around each plaque-
tte of the square lattice contribute no useful syndrome infor-
mation. Exchanging theseZ-type stabilizers with products of
Y around each plaquette still results in a valid quantum sur-
face code, since these Y -type stabilizers will commute with
the original X-type stabilizers. But now there are twice as
many bits of syndrome information about the Z errors. Tak-
ing advantage of these extra syndrome bits requires an opti-
mized decoder that can use the correlations between the two
syndrome types. The standard decoder based on minimum-
weight matching breaks down at this point, but the BSV de-
coder is speciﬁcally designed to handle such correlations. We
show that the parameterχ, which deﬁnes the scale of correla-
tion in the BSV decoder, needs to be large to achieve optimal
decoding, so in that sense accounting for these correlations is
actually necessary. These two ideas—doubling the number of
useful syndrome bits and a decoder that makes optimal use of
them—give an intuition that captures the essential reason for
the increased threshold. It is nonetheless remarkable just how
large an effect this simple change makes.
We also consider more general Pauli error models, where
Z errors occur more frequently than X and Y errors with a
nonzero bias ratio of the error rates. We show that the tai-
lored surface code exhibits these signiﬁcant gains in the error
threshold even for modest error biases in physically relevant
regimes: for biases of 10 (meaning dephasing errors occur 10
times more frequently than all other errors), the error thresh-
old is already 28.2(2)%. Figure 1 presents our main result of
the threshold scaling as a function of bias. Notably, we ﬁnd
that the tailored surface code together with the BSV decoder
performs near the hashing bound for all values of the bias.
Error correction with the surface code.— The surface
code [1] is deﬁned by a 2D square lattice having qubits on
the edges with a set of local stabilizer generators. In the usual
prescription, for each vertex (or plaquette), the stabilizer con-
sists of the product of the X (or Z) operators acting on the
neighboring edges. We simply exchange the roles of Z and
Y , as shown in Fig. 2. By choosing appropriate “rough” and
“smooth” boundary conditions along the vertical and horizon-
tal edges, the code space encodes one logical qubit into the
joint +1 eigenspace of all the commuting stabilizers with a
code distanced given by the linear size of the lattice.
arXiv:1708.08474v3  [quant-ph]  6 Feb 2018

## PDF page 2

2
100 101 102 103
0.2
0.3
0.4
0.5
0.01
0.001
Bias:η
Threshold error rate: pc
∞
FIG. 1. Threshold error rate pc as a function of bias η. The dark
gray line is the zero-rate hashing bound for the associated Pauli er-
ror channel. Lighter gray lines show the hashing bound for rates
R = 0.001 and 0.01 for comparison; the surface code family has
rate 1/n forn qubits. Blue points show the estimates for the thresh-
old using the ﬁtting procedure described in the main text together
with 1-standard-deviation error bars. The point at the largest bias
value corresponds to inﬁnite bias, i.e., onlyZ errors.
A large effort has been devoted to understanding error
correction of the surface code and the closely related toric
code [8]. The majority of this effort has focused on the cases
of either pureZ noise, or depolarizing noise whereX,Y , and
Z errors happen with equal probability; see Refs. [2, 9] for
recent literature reviews. Once a noise model is ﬁxed, one
must deﬁne a decoder, and the most popular choice is based
on minimum-weight matching (MWM). This decoder treats
X and Z noise independently, and it has an error threshold
of around 10.3% for pure Z noise with a naive implementa-
tion [3, 10], or 10.6% with some further optimization [11].
Many other decoders have been proposed, however, and these
are judged according to their various strengths and weak-
nesses, including the threshold error rate, the logical failure
rate below threshold, robustness to measurement errors (fault
tolerance), speed, and parallelizability. Of particular note are
the decoders of Refs. [12–20], since these either can handle, or
can be modiﬁed to handle, correlations beyond the paradigm
of independentX andZ errors.
The BSV decoder .— Our choice of the BSV decoder [7]
is motivated by the fact that it gives an efﬁcient approxima-
tion to the optimal maximum likelihood (ML) decoder, which
maximizes the a posteriori probability of a given logical er-
ror conditioned on an observed syndrome. This decoder has
also previously been used to do nearly optimal decoding of
depolarizing noise [7], achieving an error threshold close to
estimates from statistical physics arguments that the thresh-
old should be 18.9% [21]. [In fact, our own estimate of the
depolarizing threshold using the BSV decoder is 18.7(1)%.]
Because it approximates the ML decoder, the BSV decoder is
X
X
X
X
Y Y Y Y
X X
X
X X
X
X
Y
Y
Y
Y Y
Y
Y
FIG. 2. The modiﬁed surface code, tailored for biased Z noise, with
logical operators given by a product of Y along the top edge and a
product ofX along the left edge. The stabilizers are shown at right.
a natural choice for ﬁnding the maximum value of the thresh-
old for biased noise models.
The decoder works by deﬁning a tensor network with local
tensors associated with the qubits and stabilizers of the code.
The geometry of the tensor network respects the geometry of
the code. Each index on the local tensors has dimension 2
initially, but during the contraction sequence, this dimension
grows until it is bounded by χ, called the bond dimension.
When χ is exponentially large in n, the number of physical
qubits, then the contraction value of the tensor network returns
the exact probabilities conditioned on the syndrome of each of
the four logical error classes. Such an implementation would
be highly inefﬁcient, but using a truncation procedure during
the tensor contraction allows one to work with any ﬁxed value
ofχ≥ 2 with a polynomial runtime of O(nχ3). In this way,
the algorithm provides an efﬁcient and tunable approximation
of the exact ML decoder, and in practice small values of χ
were observed to work well [7]. We refer the reader to Ref. [7]
for the full details of this decoder.
Biased Pauli error model.— A Pauli error channel is de-
ﬁned by an array p = (1−p,px,py,pz) corresponding to the
probabilities for each Pauli operatorI (no error),X,Y , andZ,
respectively. We deﬁnep =px +py +pz to be the probability
of any single-qubit error, and we always consider the case of
independent, identically distributed noise. We deﬁne the bias
η to be the ratio of the probability of a Z error occurring to
the total probability of a non-Z Pauli error occurring, so that
η = pz/(px +py). For simplicity, we consider the special
casepx = py in what follows. Then for total error probabil-
ityp,Z errors occur with probability pz = [η/(η + 1)], and
px = py = [1/2(η + 1)]p. When η = 1/2, this gives the
standard depolarizing channel with probability p/3 for each
nontrivial Pauli error, and taking the limit η→∞ gives only
Z errors with probability p. Biased Pauli error models have
been considered by a number of authors [4, 22–27], but we
note that there are several different conventions for the deﬁni-
tion of bias. Comparison between channels with different bias
but the same total error rate is facilitated by the fact that the
channel ﬁdelity to the identity is a function only ofp.
Hashing bound.— The quantum capacity is the maximum
achievable rate at which one can transmit quantum informa-
tion through a noisy channel [28]. The hashing bound [29–31]
is an achievable rate which is generally less than the quantum

## PDF page 3

3
5 10 15 2010−3
10−2
10−1
Code distance: d
Logical failure rate: f
p = 0 .4
p = 0 .35
p = 0 .3
p = 0 .25
FIG. 3. Exponential decay of the logical failure rate f with respect
to code distance d in the regime p < pc forη = 100 andχ = 48 .
We observe scaling behavior of the form f ∼ exp(−αd) whereα
depends on the bias and is an increasing function of (pc−p). In this
bias regime, the decoder performance is likely farthest from optimal,
but the decay is still clearly exponential over this range. Other values
ofη show the same general scaling behavior, though with different
decay ratesα. The statistical error bars from 30 000 trials per point
are smaller than the individual plot points in every case.
capacity [32]. For Pauli error channels, the hashing bound
takes a particularly simple form [28] and says that there exist
quantum stabilizer codes that achieve a rate R = 1−H(p),
withH being the Shannon entropy. The proof of achievability
involves using random codes, and it is generally hard to ﬁnd
explicit codes and decoders that perform at or above this rate
for an arbitrary channel, especially if one wishes to impose
additional constraints such as local stabilizers. The quantum
capacity itself is still unknown for any Pauli channel where at
least two of (px,py,pz) are nonzero.
Numerics.— Our numerical implementation makes only
a minor modiﬁcation to the BSV decoder. To avoid changing
the deﬁnitions of the tensors used in Ref. [7], we use the sym-
metry by which we can exchange the role of Z noise in the
modiﬁed surface code with the role ofY noise in the standard
surface code. Then all of the deﬁnitions in Ref. [7] carry over
unchanged. The only difference is that we perform two ten-
sor network contractions for each decoding sequence. There
is an arbitrary choice as to whether to contract the network
row-wise or column-wise. Rather than pick just one, we av-
erage the values of both contractions. We empirically observe
improved performance with this modiﬁcation.
For each value of the bias η ∈ {0.5, 1, 3, 10, 30, 100,
300, 1000,∞}, we estimate the logical failure rate f using
the BSV decoder to obtain the sample mean failure rate on
30 000 random trials for a selection of physical error rates p
in the region near the threshold pc for code distancesd∈{ 9,
13, 17, 21}. We use a rather large value of the bond dimen-
sionχ for our simulations, speciﬁcally χ = 48 , although for
bias η < 30 we already observe that the decoder converges
well with χ = 36 . However, we still do not observe com-
plete convergence of the decoder at χ = 48 in the regime of
intermediate bias around η = 100 . The decoder convergence
withχ is displayed in Fig. 4, which shows the estimate of the
logical failure rate for the d = 21 code near the threshold.
0.5
(0.19)
1
(0.19)
3
(0.22)
10
(0.28)
30
(0.35)
100
(0.4)
300
(0.42)
1000
(0.43)
∞
(0.44)
0.00
0.02
0.04
0.06
0.08
Bias:η, (Physical error rate: p)
fχ−f48
χ = 12
χ = 24
χ = 36
χ = 48
FIG. 4. Convergence of the decoder as a function of χ near the
threshold for distance d = 21 . We observe that the logical failure
rates fχ stabilize with increasing χ for both low and high biases.
However, in the intermediate bias regime fχ is still decreasing no-
ticeably between increments ofχ, suggesting thatχ> 48 would be
required for a good approximation to the optimal ML decoder.
Performance of the decoder and convergence with χ gener-
ally improve as bias increases again beyond η = 300 , but it
is likely that further improvements are possible in the inter-
mediate bias regime. Although the decoder at χ = 48 is not
achieving an optimal failure rate in the intermediate regime,
we see excellent convergence for most of the range of bias
and across the full range of bias we observe threshold behav-
ior. Moreover, this threshold is at the hashing bound for all
η≤ 100. In the regions that are a ﬁxed distance below the
threshold, as in Fig. 3, we observe an exponential decay in
the logical failure rate f∼ exp(−αd), where α may depend
on the bias and is an increasing function of (pc−p). This
constitutes strong evidence of an error correction threshold.
We note that χ = 48 was the largest used in our simu-
lations, so we do not know if the saturation of the decoder
performance for bias η≥ 300 is a real effect, or a side effect
of having too small a value of χ. Although we observe con-
vergence and threshold behavior, we do not know how much
the performance might improve for larger values of χ since,
as seen in Fig. 4, there is apparently still some room for im-
provement. It is possible that the saturation is a real effect,
however, since even at inﬁnite bias there are still logical er-
rors of weight 2d = O(√n) that consist only of Z errors.
This is in contrast to the classical repetition code, which has
a threshold of 50% and a distance O(n). One possibility to
address this is to use a surface code with side lengthsL×W ,
whereL andW are relatively prime, for example just choos-
ingW = L + 1. We empirically observe that the Z-distance
(i.e., the distance when restricted only toZ errors) of the code
scales likeO(n) for this modiﬁcation of the surface code. In
fact, on a toric code with L and W both odd and relatively
prime, theZ-distance is provablyO(n) [33]. These observa-
tions are currently being explored, and will be addressed in
more detail in forthcoming work.
To obtain an explicit estimate of the threshold pc, we use
the critical exponent method of Ref. [10]. If we deﬁne a

## PDF page 4

4
−0.1 −0.05 0 0.05 0.1
0.1
0.2
0.3
0.4
Rescaled physical error rate:(p−pc)d1/ν
Logical failure rate:f
η= 10,χ= 48,pc = 0.282(2)
d= 9
d= 13
d= 17
d= 21
0.26 0.28 0.3 0.1
0.2
0.3
0.4
p
f
−0.2 −0.1 0 0.1
0.3
0.4
0.5
Rescaled physical error rate:(p−pc)d1/ν
Logical failure rate:f
η= 100,χ= 48,pc = 0.403(8)
d= 9
d= 13
d= 17
d= 21
0.38 0.4 0.42
0.2
0.3
0.4
0.5
p
f
−0.1 0 0.1 0.2
0.35
0.4
0.45
Rescaled physical error rate:(p−pc)d1/ν
Logical failure rate:f
η=∞,χ= 48,pc = 0.437(1)
d= 9
d= 13
d= 17
d= 21
0.42 0.44 0.46
0.35
0.4
0.45
p
f
FIG. 5. Logical failure ratef as a function of the rescaled error ratex = (p−pc)d1/ν for biasesη∈{ 10, 100,∞}. The solid line is the best
ﬁt to the model f = A +Bx +Cx 2. The insets show the raw sample means over 30 000 runs for various values of p, and the dotted gray
vertical line indicates the hashing bound. Even for the case of η = 100 where the decoder performance was likely furthest from optimal we
still see good agreement with the ﬁt model.
correlation length ξ = ( p− pc)−ν for some critical expo-
nent ν, then in the regime where d ≫ ξ we expect that
the behavior of the code is scale invariant. In this regime,
since the code distance d corresponds to a physical length,
the failure probability should depend only on the dimension-
less ratio d/ξ, a conjecture that was ﬁrst empirically veri-
ﬁed in Ref. [10]. This suggests deﬁning a rescaled variable
x = ( d/ξ)1/ν = ( p− pc)d1/ν so that the failure rate ex-
panded as a power series in x is explicitly scale invariant at
the critical pointpc corresponding tox = 0. It is then natural
to consider a model for the failure rate given by a truncated
Taylor expansion in the neighborhood around pc. We use a
quadratic model, f = A +Bx +Cx 2, and then ﬁt to this
model to ﬁnd pc,ν and the nuisance parameters A,B,C . A
discussion on the limits of the validity of this universal scaling
hypothesis can be found in Ref. [34]. We plot our estimates
off for various values ofp andd for the representative cases
ofη∈{ 10, 100,∞} in Fig. 5 together with rescaled data as
a function ofx. A visual inspection conﬁrms good qualitative
agreement with the model.
The critical exponents method gives precise estimates of
pc with low statistical uncertainty. However, systematic bi-
ases might affect the accuracy of the estimate and must be ac-
counted for. Finite-size effects typically cause threshold esti-
mates to decrease as larger and larger code distances are added
to the estimate. Additionally, the suboptimality of the decoder
due to smallχ values in the intermediate bias regime may have
overestimated each individual logical failure rate. This latter
effect does not directly imply that we have also overestimated
the threshold pc, and the data remain consistent with the ﬁt
model in spite of this as can be seen in Fig. 5. On balance,
we expect that our estimates might decrease somewhat in the
intermediate bias regime. Our ﬁnal error bars were obtained
by jackknife resampling, i.e. by computing, for each ﬁxed η,
the spread in estimates forpc when rerunning the ﬁt procedure
with a single distance d removed, for each choice of d. Our
results are summarized in Fig. 1.
Fault tolerant syndrome extraction.— Our study has fo-
cused on the error correction threshold under the assumption
of ideal syndrome extraction. To see if the gains observed in
this setting carry over to applications in fault-tolerant quantum
computing, one would need to consider the effects of faulty
syndrome measurements and gates. A full fault-tolerant anal-
ysis is beyond the scope of this work, but we brieﬂy consider
the key issues here.
First, the BSV decoder that we have used to investigate
this ultrahigh error threshold is not fault tolerant, but some
clustering decoders are [13]. Developing efﬁcient, practical
fault-tolerant decoders with the highest achievable thresholds
remains a signiﬁcant challenge for the ﬁeld.
An added complication with a biased noise model is that
the gates that perform the syndrome extraction must at least
approximately preserve the noise bias in order to maintain an
advantage [4]. For the tailored surface code studied here, one
could appeal to the techniques of Refs. [4, 25], where we note
thatY -type syndromes can be measured using a minor mod-
iﬁcation of the X-syndrome measurement scheme. We note
that these syndrome extraction circuits are signiﬁcantly more
complex (involving the use of both ancilla cat states and gate
teleportation) compared with the standard approach for the
surface code with unbiased noise, and this added complexity
will undoubtedly reduce the threshold.
More optimistically, we note that the standard method for
syndrome extraction in the surface code [35] can be directly
adapted to this tailored code and maintains biased noise on the
data qubits. Ancilla qubits are placed in the centers of both
the plaquette and vertex stabilizers of Fig. 2, and they will
be both initialized and measured in the X basis. Sequences
of controlled-X (vertex) and controlled-Y (plaquette) gates,
with the ancilla as the control and data qubits as the target,
yield the required syndrome measurements analogous to the
standard method. In this scheme, we note that high-rate Z

## PDF page 5

5
errors on the ancilla are never mapped to the data qubits; low-
rate X and Y errors on the ancilla can cause errors on the
data qubits but the noise remains biased. Measurement errors
will occur at the high rate, but this can be accommodated by
repeated measurement. Note that, as argued by Aliferis and
Preskill [4], native controlled-X and controlled-Y gates are
perhaps not well motivated in a system with a noise bias, but
nonetheless this simple scheme illustrates that, in principle,
syndromes can be extracted in this code while preserving the
noise bias. To develop a full fault-tolerant syndrome extrac-
tion circuit in a noise-biased system would require a complete
speciﬁcation of the native gates in the system and an under-
standing of their associated noise models.
Discussion.— Our numerical results strongly suggest that
in systems that exhibit an error bias, there are signiﬁcant gains
to be had for quantum error correction with codes and de-
coders that are tailored to exploit this bias. It is remarkable
that the tailored surface code performs at the hashing bound
across a large range of biases. This means that it is not just a
good code for a particular error model, but broadly good for
any local Pauli error channel once it is tailored to the speciﬁc
noise bias. It is also remarkable that a topological code, lim-
ited to local stabilizers, does so well in this regard.
Many realizations of qubits based on nondegenerate en-
ergy levels of some quantum system have a bias—often quite
signiﬁcant—towards dephasing ( Z errors) relative to energy-
nonconserving errors (X andY errors). This suggests tailor-
ing other codes, and in particular other topological codes, to
have error syndromes generated byX- andY -type stabilizers.
Even larger gains might be had by considering biased noise in
qudit surface codes [36, 37].
For qubit topological stabilizer codes, the threshold for ex-
act ML decoding with general Pauli noise can be determined
using the techniques of Ref. [21], which mapped the ML de-
coder’s threshold to a phase transition in a pair of coupled
random-bond Ising models. It would be interesting to explore
this phase boundary for general Pauli noise beyond the depo-
larizing channel that was studied numerically in Ref. [21].
We have employed the BSV decoder to obtain our thresh-
old estimates because of its near-optimal performance, but it is
not the most efﬁcient or practical decoder for many purposes.
One outstanding challenge is to ﬁnd good practical decoders
that can work as well or nearly as well across a range of bi-
ases. The clustering-type decoders [12, 13] appear well suited
for this task, and they have the added advantage that some ver-
sions of these decoders (e.g., Ref. [38]) generalize naturally to
all Abelian anyon models such as the qudit surface codes.
The most pressing open question related to this work is
whether the substantial gains observed here can be preserved
in the context of fault-tolerant quantum computing.
Acknowledgements.— This work is supported by the
Australian Research Council (ARC) via Centre of Excel-
lence in Engineered Quantum Systems (EQuS) Project No.
CE110001013 and Future Fellowship No. FT130101744, by
the U.S. Army Research Ofﬁce Grants No. W911NF-14-1-
0098 and No. W911NF-14-1-0103, and by the Sydney In-
formatics Hub for access to high-performance computing re-
sources.
[1] S. B. Bravyi and A. Y . Kitaev, “Quantum codes on a lattice with
boundary,” (1998), quant-ph/9811052.
[2] B. M. Terhal, “Quantum error correction for quantum memo-
ries,” Rev. Mod. Phys.87, 307 (2015), arXiv:1302.3428.
[3] E. Dennis, A. Kitaev, A. Landahl, and J. Preskill, “Topologi-
cal quantum memory,” J. Math. Phys. (N.Y .) 43, 4452 (2002),
quant-ph/0110143.
[4] P. Aliferis, F. Brito, D. P. DiVincenzo, J. Preskill, M. Stef-
fen, and B. M. Terhal, “Fault-tolerant computing with biased-
noise superconducting qubits: A case study,” New J. Phys. 11,
013061 (2009), arXiv:0806.0383.
[5] M. D. Shulman, O. E. Dial, S. P. Harvey, H. Bluhm, V . Uman-
sky, and A. Yacoby, “Demonstration of entanglement of elec-
trostatically coupled singlet-triplet qubits,” Science 336, 202
(2012), arXiv:1202.1828.
[6] D. Nigg, M. M ¨uller, E. A. Martinez, P. Schindler, M. Hennrich,
T. Monz, M. A. Martin-Delgado, and R. Blatt, “Quantum com-
putations on a topologically encoded qubit,” Science 345, 302
(2014), arXiv:1403.5426.
[7] S. Bravyi, M. Suchara, and A. Vargo, “Efﬁcient algorithms for
maximum likelihood decoding in the surface code,” Phys. Rev.
A 90, 032326 (2014), arXiv:1405.4883.
[8] A. Y . Kitaev, “Fault-tolerant quantum computation by anyons,”
Ann. Phys. (Amsterdam) 303, 2 (2003), quant-ph/9707021.
[9] B. J. Brown, D. Loss, J. K. Pachos, C. N. Self, and J. R.
Wootton, “Quantum memories at ﬁnite temperature,” Rev. Mod.
Phys. 88, 045005 (2016), arXiv:1411.6643.
[10] C. Wang, J. Harrington, and J. Preskill, “Conﬁnement-Higgs
transition in a disordered gauge theory and the accuracy thresh-
old for quantum memory,” Ann. Phys. (Amsterdam) 303, 31
(2003), quant-ph/0207088.
[11] T. M. Stace and S. D. Barrett, “Error correction and degener-
acy in surface codes suffering loss,” Phys. Rev. A 81, 022317
(2010), arXiv:0912.1159.
[12] G. Duclos-Cianci and D. Poulin, “Fast Decoders for Topolog-
ical Quantum Codes,” Phys. Rev. Lett. 104, 050504 (2010),
arXiv:0911.0581.
[13] G. Duclos-Cianci and D. Poulin, “Fault-tolerant renormaliza-
tion group decoder for Abelian topological codes,” Quantum
Inf. Comput. 14, 0721 (2014), arXiv:1304.6100.
[14] A. G. Fowler, “Optimal complexity correction of correlated er-
rors in the surface code,” (2013), arXiv:1310.0863.
[15] J. R. Wootton and D. Loss, “High Threshold Error Correction
for the Surface Code,” Phys. Rev. Lett. 109, 160503 (2012),
arXiv:1202.4316.
[16] N. Delfosse and J.-P. Tillich, “A decoding algorithm for
CSS codes using the X/Z correlations,” in 2014 IEEE In-
ternational Symposium on Information Theory (IEEE, 2014)
arXiv:1401.6975.
[17] A. Hutter, J. R. Wootton, and D. Loss, “Efﬁcient Markov chain
Monte Carlo algorithm for the surface code,” Phys. Rev. A 89,
022326 (2014), arXiv:1302.2669.
[18] G. Torlai and R. G. Melko, “Neural Decoder for Topo-
logical Codes,” Phys. Rev. Lett. 119, 030501 (2017),
arXiv:1610.04238.
[19] P. Baireuther, T. E. O’Brien, B. Tarasinski, and C. W. J.
Beenakker, “Machine-learning-assisted correction of correlated

## PDF page 6

6
qubit errors in a topological code,” (2017), arXiv:1705.07855.
[20] S. Krastanov and L. Jiang, “Deep neural network probabilis-
tic decoder for stabilizer codes,” Sci. Rep. 7, 11003 (2017),
arXiv:1705.09334.
[21] H. Bombin, R. S. Andrist, M. Ohzeki, H. G. Katzgraber,
and M. A. Martin-Delgado, “Strong Resilience of Topologi-
cal Codes to Depolarization,” Phys. Rev. X 2, 021004 (2012),
arXiv:1202.1852.
[22] P. Aliferis and J. Preskill, “Fault-tolerant quantum computa-
tion against biased noise,” Phys. Rev. A 78, 052331 (2008),
arXiv:0710.1301.
[23] B. R ¨othlisberger, J. R. Wootton, R. M. Heath, J. K. Pachos,
and D. Loss, “Incoherent dynamics in the toric code subject to
disorder,” Phys. Rev. A85, 022313 (2012), arXiv:1112.1613.
[24] J. Napp and J. Preskill, “Optimal Bacon-Shor codes,” Quantum
Inf. Comput. 13, 0490 (2013), arXiv:1209.0794.
[25] P. Brooks and J. Preskill, “Fault-tolerant quantum computation
with asymmetric Bacon-Shor codes,” Phys. Rev. A 87, 032310
(2013), arXiv:1211.1400.
[26] P. Webster, S. D. Bartlett, and D. Poulin, “Reducing the over-
head for quantum computation when noise is biased,” Phys.
Rev. A 92, 062309 (2015), arXiv:1509.05032.
[27] A. Robertson, C. Granade, S. D. Bartlett, and S. T. Flammia,
“Tailored Codes for Small Quantum Memories,” Phys. Rev. Ap-
plied 8, 064004 (2017), arXiv:1703.08179.
[28] M. Wilde, Quantum Information Theory (Cambridge Univer-
sity Press, Cambridge, England, 2013) arXiv:1106.1445.
[29] S. Lloyd, “Capacity of the noisy quantum channel,” Phys. Rev.
A 55, 1613 (1997), quant-ph/9604015.
[30] P. W. Shor, “The quantum channel capacity and coherent infor-
mation,” lecture notes, MSRI Workshop on Quantum Compu-
tation, San Francisco (November 2002).
[31] I. Devetak, “The private classical capacity and quantum ca-
pacity of a quantum channel,” IEEE Trans. Inf. Theory 51, 44
(2005), quant-ph/0304127.
[32] D. P. DiVincenzo, P. W. Shor, and J. A. Smolin, “Quantum-
channel capacity of very noisy channels,” Phys. Rev. A57, 830
(1998), quant-ph/9706061.
[33] S. Bravyi, private communication (2017).
[34] F. H. E. Watson and S. D. Barrett, “Logical error rate scal-
ing of the toric code,” New J. Phys. 16, 093045 (2014),
arXiv:1312.5213.
[35] A. G. Fowler, M. Mariantoni, J. M. Martinis, and
A. N. Cleland, “Surface codes: Towards practical large-scale
quantum computation,” Phys. Rev. A 86, 032324 (2012),
arXiv:1208.0928.
[36] H. Anwar, B. J. Brown, E. T. Campbell, and D. E. Browne,
“Fast decoders for qudit topological codes,” New J. Phys. 16,
063038 (2014), arXiv:1311.4895.
[37] F. H. E. Watson, H. Anwar, and D. E. Browne, “Fast fault-
tolerant decoder for qubit and qudit surface codes,” Phys. Rev.
A 92, 032309 (2015), arXiv:1411.3028.
[38] S. Bravyi and J. Haah, “Quantum Self-Correction in the 3D
Cubic Code Model,” Phys. Rev. Lett. 111, 200501 (2013),
arXiv:1112.3252.
