---
type: Research Paper
title: Neural Belief-Propagation Decoders for Quantum Error-Correcting Codes
description: '- Pinned arXiv record: [1811.07835v2](https://arxiv.org/abs/1811.07835v2)'
resource: https://example.org/qec-arxiv-papers/resource/paper-1811-07835v2/sources%2Fmarkdown%2F1811.07835v2
tags:
- paper-1811-07835v2
- markdown
- rl
concept_id: concepts/paper-1811-07835v2/sources-markdown-1811.07835v2-6a510356b0
concept_path: concepts/paper-1811-07835v2/sources-markdown-1811.07835v2-6a510356b0.md
subject_iri: https://example.org/qec-arxiv-papers/resource/paper-1811-07835v2/sources%2Fmarkdown%2F1811.07835v2
ontology_class_iri: https://example.org/ontology/qec-arxiv-papers#Paper
ontology_version_iri: https://example.org/ontology/qec-arxiv-papers/1.0.0
source_id: paper-1811-07835v2
source_kind: markdown
source_path: sources/markdown/1811.07835v2.md
source_content_sha256: bae0a8a930b188f64203a0b47d08c7c06c50e755fdaf1949190ae4031bb2ef3f
record_sha256: 07eebc23ef7b34ddab2226563db72eafed542f8c74328e2097fcd05560b505e0
source_refs:
- https://example.org/qec-arxiv-papers/provenance/record/paper-1811-07835v2/c3c218e7ae18df8d4f57dc50
record_id: sources/markdown/1811.07835v2
---

# Neural Belief-Propagation Decoders for Quantum Error-Correcting Codes

## Source citation

- Pinned arXiv record: [1811.07835v2](https://arxiv.org/abs/1811.07835v2)
- Authors: Liu, Ye-Hua; Poulin, David
- PDF: [https://arxiv.org/pdf/1811.07835v2](https://arxiv.org/pdf/1811.07835v2)
- PDF SHA-256: `09f7c1f7776628a72530554d8cbaf08bf6b87205328014e7edfa82228b27d7da`
- Extracted pages: 6

The following text was extracted page by page from the pinned PDF. Page headings are stable evidence locators.

## PDF page 1

Neural Belief-Propagation Decoders for Quantum Error-Correcting Codes
Ye-Hua Liu1 and David Poulin1, 2
1Département de Physique & Institut Quantique,
Université de Sherbrooke, J1K 2R1 Sherbrooke, Québec, Canada
2Canadian Institute for Advanced Research, M5G 1Z8 Toronto, Ontario, Canada
Belief-propagation (BP) decoders play a vital role in modern coding theory, but they are not
suitable to decode quantum error-correcting codes because of a unique quantum feature called error
degeneracy. Inspired by an exact mapping between BP and deep neural networks, we train neural
BP decoders for quantum low-density parity-check (LDPC) codes with a loss function tailored to
error degeneracy. Training substantially improves the performance of BP decoders for all families
of codes we tested and may solve the degeneracy problem which plagues the decoding of quantum
LDPC codes.
Statistical inference on a graph is an important
paradigm in many areas of science, and equivalent heuris-
ticalgorithmshavebeendevelopedbydiﬀerentcommuni-
ties, including the cavity method in statistical physics [1]
and the belief propagation (BP) algorithm in information
science [2]. In the latter case, BP is the standard decod-
ing algorithm for low-density parity-check (LDPC) codes
[3], which form the backbone of modern coding theory
and are widely used in wireless communication [4]. With
the growing interest for quantum technologies, quantum
generalizations of LDPC codes have been proposed [5–7],
but BP was found to be inadequate for their decoding [8]
because of error degeneracy, a feature unique to quantum
codes. Despite many improvements [8–10] to BP, there is
still no accurate decoding algorithm for general quantum
LDPCcodes. Thiscontrastwithstatisticalphysicswhere
the cavity method has been generalized to the quantum
setting with some success [11–14].
Recently, an exact mapping between BP and artiﬁcial
neural networks has been revealed [15], which implies a
general machine-learning strategy to adapt BP to any
speciﬁc task. In this article, we use this strategy for
the decoding of quantum LDPC codes. Neural-network-
based decoders for quantum error-correcting codes have
attracted great interest recently, particularly in the con-
text of topological codes [16–27]. But near optimal (or
very fast suboptimal) decoding algorithms are already
proposed for these codes [28–31], which exploit their reg-
ular lattice structure. In contrast, for quantum LDPC
codes, which are deﬁned on random graphs, only recently
has a decoding algorithm been found for the special fam-
ily of expander codes [7, 32, 33] and the general case
remains open. Our main motivation to study this prob-
lem is that quantum LDPC codes have the potential of
greatly reducing the overhead required to realize robust
quantum processors [34, 35].
In this paper, we train neural BP (NBP) decoders for
quantum LDPC codes. To guide the learning process,
we construct a loss function that takes into account error
degeneracy. We present results for the toric code [36], the
quantum bicycle code [5] and the quantum hypergraph-
product code [6]. Decoding accuracy improves up to 3
orders of magnitude compared with the untrained BP
decoder, and the improvement is even more substantial
when we ignore detected but uncorrected errors. While
we do not completely solve the LDPC decoding prob-
lem here, our results suggest that an important step for-
wardwasrealized, andthestrategycouldbeappliedmore
broadly, for instance in many-body physics. That general
strategy consists in training a neural network to solve a
quantum problem, with initial conditions corresponding
to the BP algorithm that solves the classical counterpart.
LDPC codes.—A linear error-correcting code can be
represented by its parity-check matrixH with binary (0
or 1) matrix elements. Codewordsc’s satisfyingHc = 0
mod 2. As a result, when an error patterne is imposed
on the codeword c→ c′ = c + e mod 2, there will be
a measurable syndrome patterns = Hc′ = He mod 2,
which signals the occurrence of the error e. The role
of the decoder is to infer the error patterne from the
measured syndrome patterns. Classical LDPC codes are
error-correcting codes with sparse parity-check matrices,
i.e., where the number of 1’ in each column and row are
bounded by constants independent of the matrix size.
Belief propagation.— The Tanner graph is a graphi-
cal representation of the parity-check matrixH, with a
set of variable nodes{ev|v = 1,...,n } (containing the er-
ror pattern) and a set of check nodes{sc|c = 1,...,m }
(containing the syndrome pattern). There is an edge
between ev and sc if Hcv = 1. Neighborhoods of vari-
ables and checks are deﬁned byN (v) ={c|Hcv = 1} and
N (c) ={v|Hcv=1}, respectively.
Belief propagation (BP) is an iterative algorithm for
approximating the average value of each variable node
ev, over all error patterns e’s that are consistent with
the given syndrome patterns (meaningHe = s). In per-
forming the average, each error patterneis weighted by a
probability P (e) = ∏
vP (ev), which should accurately
model the noise statistics of the physical device carry-
ing the information. Mathematically speaking, BP solves
the posterior marginal probability for each variable node
P (ev = 1|s)∝∑
e/evP (s|e/ev,e v = 1)P (e/ev,e v = 1).
This goal is achieved by iterating the following simple BP
arXiv:1811.07835v2  [quant-ph]  7 May 2019

## PDF page 2

2
× 𝑁𝑐
CVVC
 VCCV
syndrome
prior
Residual Connection
Marginalization & Multi-Loss
t t+1𝜇𝑐→𝑣 𝜇𝑣→𝑐 𝜇𝑐→𝑣
Figure 1. Schematics of the NBP decoder. The main cycle
in the gray box is repeatedNc times. Inside one cycle there
are two phases of computation, thecv → vc and vc → cv
phases which are governed by Eqs. (4) and (5) respectively.
The inputs to the neural network are denoted by the green
boxes, where the prior and syndrome correspond to{lv} in
Eq. (4) and{sc} in Eq. (5) respectively. After each cycle,
the set of output{µc→v} is marginalized by Eq. (6) and the
resulting{µv} is sent to the loss function Eq. (8). We also
introduce residual connections to facilitate training of deep
networks [37]. (See SM for details.)
equations:
µ(t+1)
v→c =lv +
∑
c′∈N (v)\c
µ(t)
c′→v, (1)
µ(t+1)
c→v = (−1)sc
2 tanh−1 ∏
v′∈N (c)\v
tanhµ(t)
v′→c
2 , (2)
wherelv = log
(
P (ev=0)
P (ev=1)
)
is the prior log-likelihood ratio
for variableev andN (x)\y is the set of all neighbors ofx
except fory [4]. The initial condition for the iteration is
µ(t=0)
v→c = 0, and afterT steps (suﬃciently long), one stops
the iteration and performs the following marginalization
for the posterior log-likelihood ratio:
µv =lv +
∑
c∈N (v)
µ(T )
c→v. (3)
The posterior marginal probability relates toµv accord-
ing to log
(
P (ev=0|s)
P (ev=1|s)
)
=µv. EquivalentlyP (ev = 1|s) =
σ (µv) and P (ev = 0|s) = 1 − σ (µv), where σ (x) =
1/ (ex + 1) is the Fermi function (or horizontally-ﬂipped
sigmoid function). The inferred error pattern maximizes
these marginal probabilities, i.e.,ev is inferred to be 0/1
when µv is positive/negative.
Neural belief propagation.—The above iterative pro-
cedure can be exactly mapped to a deep neural network,
where each neuron represents a messageµc→v or µv→c
[15]. (See Fig. 1.) This permits generalization of the
original BP algorithm by introducing additional “train-
able” weightsw(t)
c′v,vc andw(T )
cv,v, and “trainable” biasesb(t)
v
andb(T )
v . Speciﬁcally, in this NBP algorithm, Eqs. (1, 2,
3) are modiﬁed to:
µ(t+1)
v→c =lvb(t)
v +
∑
c′∈N (v)\c
µ(t)
c′→vw(t)
c′v,vc, (4)
a
(
µ(t+1)
c→v
)
=iπsc +
∑
v′∈N (c)\v
a
(
µ(t)
v′→c
)
, (5)
µv =lvb(T )
v +
∑
c∈N (v)
µ(T )
c→vw(T )
cv,v, (6)
respectively [15, 38]. Notice that all equations above
have the form of weighted sum plus bias, interleaved with
the nonlinear functiona (x) = log (tanh (x/2)). This is
the canonical form of feed-forward neural networks [39].
When setting all newly introduced parameters to 1, these
equations became the standard BP equations [40].
To train these weights, one minimizes a carefully de-
signed loss functionL by back-propagating its gradients
w.r.t. all trainable parameters. E.g., biases are updated
accordingto ∆b(t)
v =−lr×∂L/∂b(t)
v , wherelr isthelearn-
ing rate. For classical codes, one aims for reproducing the
whole error pattern exactly, so the natural choice of the
loss function is the binary cross entropy function between
the inferred error pattern and the true error pattern:
L (⃗ µ; e) =−
∑
v
ev logσ (µv) + (1−ev) log [1−σ (µv)].
(7)
Quantum setting.— Quantum noise can be modeled
by random Pauli operators I, ˆX, ˆY, and ˆZ on the
qubits. A convenient way of bookkeeping aN-qubit er-
ror uses a 2N-bit string e representing the Pauli oper-
ator: ˆP (e) = ∏
1≤i≤N
[
ˆXi
]ei[
ˆZi
]ei+N
. In this repre-
sentation, two Pauli-strings operators ˆP (a) and ˆP (b)
commute/anticommute when aTM b is even/odd, where
the symplectic inner product is deﬁned with M =( 1N×N
1N×N
)
. Note that all Pauli-string operators
satisfy ˆP 2 = 1.
Likewise, the quantum codewords|ψ⟩ are deﬁned by
a set of constraintsSj|ψ⟩ = +|ψ⟩ where each stabilizer
generator Sj is a Pauli-string operator. For these equa-
tions to have a solution, it is necessary for the Sj to
mutually commute and to not generate−1 under multi-
plication. Using the above bookkeeping, we can represent
each stabilizer generatorSj by a 2N-bit string, and as-
semble these strings as rows of a parity-check matrixH.
A quantum LDPC code is one whose parity-check matrix
is row- and column-sparse.
There is a crucial diﬀerence between classical and
quantum error correction. In the classical case, success-
ful decoding means the inferred erroreinf. is exactly the
same as the true errore; while in the quantum case, one
only requires the total erroretot. = e+einf. mod 2 to be-
long to the “stabilizer group” – the set of all Pauli-string
operators spanned by the rows ofH. This is because two

## PDF page 3

3
10 5
10 4
10 3
10 2
10 1
logical error rate
(a)
10 5
10 4
10 3
10 2
10 1
flagged error rate
(b)
4 6 8 10 12 14 16 18
L
0.00
0.05
0.10
0.15degen. decoding rate
(c)
4 6 8 10 12 14 16 18
L
10 6
10 5
10 4
10 3
10 2
unflagged error rate
 (d)
no code
BP
NBP
Figure 2. Training the NBP decoder for the toric code with
diﬀerent code sizes. (a) The logical error rate decreases sub-
stantially after training (tested atperr = 0.01). Here the log-
ical error rate is broken up into two terms in (b) and (d), cor-
responding to “ﬂagged” and “unﬂagged” errors, respectively.
(See main text for details.) (c) The NBP decoder exploits
degeneracy by correctly decoding with an error pattern that
is not exactly the same as the true error pattern. Training
parameters: Nc = 25, lr = 2× 10−4.
Pauli-string operatorsE and F = ESj that diﬀer by a
stabilizer have identical action on all codestates. To test
if etot. belongs to the stabilizer group, one simply needs
to check that it commutes with all the operators that
commute with the stabilizers, i.e., thatH⊥M etot. = 0
mod 2 where H⊥ is the matrix that generates the or-
thogonal complement ofH with respect to the symplectic
inner product,HM
(
H⊥)T
= 0 mod 2.
The above analysis motivates the design the following
loss function tailored for quantum error correction:
L (⃗ µ; e) =
∑
i
f

∑
jk
H⊥
ijMjk [ek +σ (µk)]

. (8)
Note the parity checkparity (x) = x mod 2 is replaced
by the continuous and diﬀerentiable functionf (x) =
|sin (πx/2)| to facilitate gradient-based machine-learning
techniques. This loss is minimized when the true errore
and the inferred erroreinf. sum to a stabilizer.
The loss function can also be averaged over all NBP-
cycles ¯L = 1
Nc
∑Nc
i=1L
(
⃗ µ(i); e
)
, which requires marginal-
ization after each cycle. In this work we use a variation
of this form. See SM for more details.
Toric code.—We ﬁrst study the toric code [36] on an
L×L square lattice, which is a simple and widely studied
quantum LDPC. (See Fig. 3 for the local Tanner graph.)
During training, we generate error patterns consisting of
independentX andZ errors with physical error rateperr,
i.e., P (ev = 1) = perr for allv. In each minibatch, 120
error patterns are drawn from 6 physical error rates that
are uniformly distributed in the rangeperr∈ [0.01, 0.05].
X
V
X
Z
V
Z
Figure 3. (Top panels) One of the observed patterns of the
learned weights for the toric code. To obtain this clear pat-
tern, we implemented weights sharing (see main text) with
G = (2i, 2j),i,j = 0, 1,... A noisy version of the same pat-
tern is observed when weight sharing is turned oﬀ. (Bottom
panels) Tanner graph of the toric code and the position of
cvvc weights (yellow star). Correspondence to the top panels
is marked by the black box.
After∼ 10000 minibatches, we test the performance of
the trained decoder. Figure 2 compares the original BP
decoder (before training) and the trained NBP decoder
at perr = 0.01 for various code sizes. Training signif-
icantly enhances decoding accuracy up to three orders
of magnitude (Fig. 2a), and we observe that the train-
ing time required for convergence depends weakly on the
code sizeL. (See SM for details.)
We can distinguish two types of decoding failure.
“Flagged” failures occur when the correction inferred by
the decoder does not return the system to the code space
– there remains a non-trivial syndrome after decoding.
“Unﬂagged” failures occur when the correction return the
system to the wrong code state. These two contributions
to the overall logical error rate are shown in Fig. 2b and
2d, respectively. We observe that training greatly re-
duces ﬂagged failures at the expense of slightly increas-
ing unﬂagged failures, and overall there is a signiﬁcant
net decrease of failures. It should be noted that ﬂagged
failures are benign because they can be re-decoded, using
either a more accurate but more expensive decoder (e.g.
the minimum-weight perfect matching [41]) or a higher
layer of code for erasure errors. Such a mixed decoding
strategy would combine the speed and ﬂexibility of BP
decoder and reliability of a more expensive decoder used
on a very small fraction (e.g.10−4) of instance.
The loss function Eq. (8) takes into account error de-
generacy, and we see on Fig. 2c that the frequency of
successful decoding where the actual and the inferred er-
ror diﬀer by a stabilizer increases with the code length.
This rate was nearly zero with the untrained decoder (see

## PDF page 4

4
0.02 0.04 0.06 0.08 0.10
physical error rate
10 1
100
logical error rate
(a)
BP
0.02 0.04 0.06 0.08 0.10
physical error rate
10 4
10 3
10 2
10 1
100
(b)
NBP
L=4
L=6
L=8
L=10
Figure 4. Evolution of the logical error rate as a function of
the physical error rate, for the BP/NBP decoder before/after
training. (a) Before training the performance of the BP de-
coder is worse for larger code sizes at all physical error rates.
(b) After training, the performance improves substantially for
all code sizes at all physical error rates, and the performance
curves start to cross each other. This indicates the develop-
ment of a threshold.
SM for examples of learned stabilizers).
The periodic nature of the toric code inspired us to
utilize a weight-sharing technique, where the weights
wc′
1v1,v1c1 andwc′
2v2,v2c2 are invariant under lattice trans-
lation G. We can control the amount of sharing by the
size of G (similar to the ﬁlter-size in convolutional neu-
ral networks). Fig. 3 is a graphical representation of
the trained weights, and suggests that symmetry break-
ing improves BP for quantum codes. We also observe
that weights trained on one code size can also increase
the performance when applied to codes of diﬀerent sizes,
which implies that the learning is universal/transferable
(see SM for more details).
Figure 4 shows that signiﬁcant improvement can be
achieved across a range of physical error rates. Using
the original BP, increasing the code size leads to worse
performance. After training, performance improves with
size for suﬃciently low error rates, and the trend indi-
cates that further improved training might lead to a BP
decoder with a ﬁnite threshold.
When the neural network is initialized away from BP,
training gets stuck at a much worse local minimum.
This illustrates the importance of incorporating domain
knowledge (when possible) before using general machine-
learning methods as black boxes, which contrasts with
prior uses of neural net decoding of the toric code [16, 18].
Quantum LDPC codes with high rate.—The toric code
encodes a constant numberK = 2 of qubits in a growing
numberN of physical qubits, thus achieving a vanishing
rate r = K/N. We now turn to quantum LDPC codes
with constant rates.
The quantum bicycle code [5] is a quantum LDPC
code constructed from a random binary vectorA of size
N/2. First, all cyclic permutations ofA are collected as
columns in a matrixC. Then C is concatenated with
its transpose to form H0 =
[
C,C T]
, from which K/2
10 4
 10 3
 10 2
physical error rate
10 5
10 4
10 3
10 2
10 1
logical error rate
(a)
bicycle code
no code
BP
NBP
10 4
 10 3
 10 2
physical error rate
10 4
10 3
10 2
10 1
(b)
hypergraph-product code
no code
BP
NBP
Figure 5. Training greatly improves the BP decoder for quan-
tum LDPC codes with high rates. (a) Quantum bicycle code
with code parameter [[256, 32]] and rate r = 0.125. Train-
ing parameters: Nc = 12 , lr = 1 × 10−4. (b) Quantum
hypergraph-product code with code parameter[[129, 28]] and
rate r∼ 0.2. Training parameters:Nc = 12, lr = 1× 10−4.
rows are chosen randomly and removed. After these con-
structions, H0 is a self-dual matrix (meaningH0H T
0 = 0
mod 2) of size (N−K)/2×N. The ﬁnal parity-check
matrix for the quantum bicycle code isH =
(H0
H0
)
.
The sparsity of this matrix can be controlled by the num-
ber of nonzero elements inA. Training the NBP decoder
for a quantum bicycle code withN = 256, K = 32 and∑
iAi = 8 improves the accuracy up to 3 orders of mag-
nitude (Fig. 5a).
The quantum hypergraph-product code [6] is con-
structed from two classical codes with parity-check ma-
trices [H1]m1×n1
and [H2]m2×n2
. The following products
are constructed HX =
[
H1⊗In2×m2, Im1×n1⊗H T
2
]
and HZ =
[
In1×m1⊗H2 ,H T
1 ⊗Im2×n2
]
, and the
parity-check matrix of the quantum code followsH =(
HX
HZ
)
, which performsm =m1n2 +n1m2 checks
on n = m1m2 +n1n2 qubits. In this paper, we study a
hypergraph-product code, for whichH1 and H2 are the
classical [7, 4, 3] and [15, 7, 5] BCH codes, respectively.
This code has rater = 28/129∼ 0.2. Training the NBP
decoder for this code improves the accuracy up to one
order of magnitude (Fig. 5b).
Conclusions.— We signiﬁcantly improved the belief-
propagation decoders for quantum LDPC codes by train-
ing them as deep neural networks. Our results on the
toric code, the quantum bicycle code and the quantum
hypergraph-product code all show orders of magnitude
of enhancement in decoding accuracy. The original be-
lief propagation is known to have bad performance for
quantum error-correcting codes [8]. On the other hand,
training a neural decoder with general architecture has
been reported to be hard for large codes [20, 42]. Our
results indicate that combining the general framework of
machine learning and the speciﬁc domain knowledge of
quantum error correction is a promising approach, when
neither works well individually.

## PDF page 5

5
The signiﬁcance of this result is supported by the
tremendous success of BP with classical LDPC codes [4],
and the fact that quantum LDPC codes promise a low-
overhead fault-tolerant quantum computation architec-
ture [34]. In addition, our techniques could be adapted
to uses of BP in other quantum many-body problems,
such as improving the quantum cavity method [11–14].
Acknowledgments.— Y.H.L would like to thank help-
ful discussions with Pavithran Iyer, Anirudh Krishna,
Xin Li, Alex Rigby, and Colin Trout. Special thanks go
to Liang Jiang and Stefan Krastanov, who shared simi-
lar ideas. This research was undertaken thanks in part
to funding from the Canada First Research Excellence
Fund. Computations were made on the supercomputer
Helios managed by Calcul Québec and Compute Canada.
The operation of this supercomputer is funded by the
Canada Foundation for Innovation (CFI), the ministère
de l’Économie, de la science et de l’innovation du Québec
(MESI) and the Fonds de recherche du Québec - Nature
et technologies (FRQ-NT). We usedTensorFlow [43] to
build and train neural belief-propagation decoders.
[1] M Mezard, G Parisi, and M Virasoro,Spin Glass Theory
and Beyond , World Scientiﬁc Lecture Notes in Physics,
Vol. 9 (WORLD SCIENTIFIC, 1986).
[2] Judea Pearl, “Reverend Bayes on inference engines: A
distributed hierarchical approach,” Proc. Second Natl.
Conf. Artif. Intell.AAAI-82, 133–136 (1982).
[3] R. G Gallager, “Low-density parity-check codes,” IEEE
Trans. Inf. Theory8, 21–28 (1962).
[4] Tom Richardson and Ruediger Urbanke,Modern Coding
Theory (Cambridge University Press, Cambridge, 2008).
[5] D.J.C. MacKay, Graeme Mitchison, and P.L. McFad-
den, “Sparse-Graph Codes for Quantum Error Correc-
tion,” IEEE Trans. Inf. Theory50, 2315–2330 (2004).
[6] Jean-Pierre Tillich and Gilles Zemor, “Quantum LDPC
Codes With Positive Rate and Minimum Distance Pro-
portional to the Square Root of the Blocklength,” IEEE
Trans. Inf. Theory60, 1193–1202 (2014).
[7] Anthony Leverrier, Jean-Pierre Tillich, and Gilles Ze-
mor, “Quantum Expander Codes,” in2015 IEEE 56th
Annu. Symp. Found. Comput. Sci. , Vol. 2015-Decem
(IEEE, 2015) pp. 810–824.
[8] David Poulin and Yeojin Chung, “On the iterative decod-
ing of sparse quantum codes,” arXiv:0801.1241 (2008).
[9] Yun-Jiang Wang, Barry C Sanders, Bao-ming Bai, and
Xin-mei Wang, “Enhanced Feedback Iterative Decoding
of Sparse Quantum Codes,” IEEE Trans. Inf. Theory58,
1231–1241 (2012).
[10] Zunaira Babar, Panagiotis Botsinis, Dimitrios Alanis,
Soon Xin Ng, and Lajos Hanzo, “Fifteen Years of Quan-
tum LDPC Coding and Improved Decoding Strategies,”
IEEE Access 3, 2492–2519 (2015).
[11] M. B. Hastings, “Quantum belief propagation: An algo-
rithm for thermal quantum systems,” Phys. Rev. B76,
201102 (2007).
[12] David Poulin and Ersen Bilgin, “Belief propagation al-
gorithm for computing correlation functions in ﬁnite-
temperature quantum many-body systems on loopy
graphs,” Phys. Rev. A77, 052318 (2008).
[13] C. Laumann, A. Scardicchio, and S. L. Sondhi, “Cavity
method for quantum spin glasses on the Bethe lattice,”
Phys. Rev. B78, 134424 (2008).
[14] DavidPoulinandMatthewBHastings,“MarkovEntropy
Decomposition: A Variational Dual for Quantum Belief
Propagation,” Phys. Rev. Lett.106, 080403 (2011).
[15] Eliya Nachmani, Yair Be’ery, and David Burshtein,
“Learning to decode linear codes using deep learning,” in
2016 54th Annu. Allert. Conf. Commun. Control. Com-
put. (IEEE, 2016) pp. 341–346.
[16] Giacomo Torlai and Roger G. Melko, “Neural Decoder for
Topological Codes,” Phys. Rev. Lett.119, 030501 (2017).
[17] Paul Baireuther, Thomas E. O’Brien, Brian Tarasin-
ski, and Carlo W. J. Beenakker, “Machine-learning-
assisted correction of correlated qubit errors in a topo-
logical code,” Quantum2, 48 (2018).
[18] Stefan Krastanov and Liang Jiang, “Deep Neural Net-
work Probabilistic Decoder for Stabilizer Codes,” Sci.
Rep. 7, 11003 (2017).
[19] Savvas Varsamopoulos, Ben Criger, and Koen Bertels,
“Decoding small surface codes with feedforward neural
networks,” Quantum Sci. Technol.3, 015004 (2018).
[20] Nishad Maskara, Aleksander Kubica, and
Tomas Jochym-O’Connor, “Advantages of versa-
tile neural-network decoding for topological codes,”
arXiv:1802.08680 (2018).
[21] Christopher Chamberland and Pooya Ronagh, “Deep
neural decoders for near term fault-tolerant experi-
ments,” Quantum Sci. Technol.3, 044002 (2018).
[22] Thomas Fösel, Petru Tighineanu, Talitha Weiss, and
Florian Marquardt, “Reinforcement Learning with Neu-
ral Networks for Quantum Feedback,” arXiv:1802.05267
(2018).
[23] Amarsanaa Davaasuren, Yasunari Suzuki, Keisuke Fujii,
and Masato Koashi, “General framework for constructing
fast and near-optimal machine-learning-based decoder
of the topological stabilizer codes,” arXiv:1801.04377
(2018).
[24] P.Baireuther, M.D.Caio, B.Criger, C.W.J.Beenakker,
and T. E. O’Brien, “Neural network decoder for topologi-
cal color codes with circuit level noise,” arXiv:1804.02926
(2018).
[25] Nikolas P. Breuckmann and Xiaotong Ni, “Scalable Neu-
ral Network Decoders for Higher Dimensional Quantum
Codes,” Quantum2, 68 (2017).
[26] Xiaotong Ni, “Neural Network Decoders for Large-
Distance 2D Toric Codes,” arXiv:1809.06640 (2018).
[27] Ryan Sweke, Markus S. Kesselring, Evert P. L. van
Nieuwenburg, and Jens Eisert, “Reinforcement learn-
ing decoders for fault-tolerant quantum computation,”
arXiv:1810.07207 (2018).
[28] Sergey Bravyi, Martin Suchara, and Alexander Vargo,
“Eﬃcient algorithms for maximum likelihood decoding in
the surface code,” Phys. Rev. A90, 032326 (2014).
[29] Andrew S. Darmawan and David Poulin, “Linear-time
general decoding algorithm for the surface code,” Phys.
Rev. E 97, 051302 (2018).
[30] Nicolas Delfosse and Naomi H. Nickerson, “Almost-
linear time decoding algorithm for topological codes,”
arXiv:1709.06218 (2017).
[31] Guillaume Duclos-Cianci and David Poulin, “Fast De-

## PDF page 6

6
coders for TopologicalQuantumCodes,” Phys.Rev. Lett.
104, 050504 (2010).
[32] Omar Fawzi, Antoine Grospellier, and Anthony Lever-
rier, “Eﬃcient decoding of random errors for quantum
expander codes,” arXiv:1711.08351 (2017).
[33] Antoine Grospellier and Anirudh Krishna, “Numerical
study of hypergraph product codes,” arXiv:1810.03681
(2018).
[34] Daniel Gottesman, “Fault-tolerant quantum computa-
tion with constant overhead,” Quant. Info. and Comp.
14, 1338 (2014).
[35] Omar Fawzi, Antoine Grospellier, and Anthony Lever-
rier, “Constant overhead quantum fault-tolerance with
quantum expander codes,” arXiv:1808.03821 (2018).
[36] Alexei Kitaev, “Anyons in an exactly solved model and
beyond,” Ann. Phys. (N. Y).321, 2–111 (2006).
[37] Kaiming He, Xiangyu Zhang, Shaoqing Ren, and Jian
Sun, “Deep Residual Learning for Image Recognition,”
arXiv:1512.03385 (2015).
[38] Henk Wymeersch, Federico Penna, and Vladimir Savic,
“Uniformly reweighted belief propagation: A factor
graph approach,” in2011 IEEE Int. Symp. Inf. Theory
Proc., 2 (IEEE, 2011) pp. 2000–2004.
[39] I Goodfellow, Y Bengio, and A Courville,Deep Learning
(MIT Press, 2016).
[40] For numerical stability, argument oftanh−1(·) is trun-
cated to (−1 + ϵ, 1−ϵ) and we choose ϵ = 10−4. De-
creasing ϵ does not change the main conclusion of the
paper.
[41] J. Edmonds, “Paths, trees and ﬂowers,” Canad. J. Math.
17 (1965).
[42] Tobias Gruber, Sebastian Cammerer, Jakob Hoydis, and
Stephan ten Brink, “On Deep Learning-Based Channel
Decoding,” arXiv1701.07738 (2017).
[43] Martín Abadi, Ashish Agarwal, Paul Barham, Eu-
gene Brevdo, Zhifeng Chen, Craig Citro, Greg S. Cor-
rado, Andy Davis, Jeﬀrey Dean, Matthieu Devin, San-
jay Ghemawat, Ian Goodfellow, Andrew Harp, Geof-
frey Irving, Michael Isard, Yangqing Jia, Rafal Jozefow-
icz, Lukasz Kaiser, Manjunath Kudlur, Josh Levenberg,
Dan Mane, Rajat Monga, Sherry Moore, Derek Mur-
ray, Chris Olah, Mike Schuster, Jonathon Shlens, Benoit
Steiner, Ilya Sutskever, Kunal Talwar, Paul Tucker,
Vincent Vanhoucke, Vijay Vasudevan, Fernanda Viegas,
Oriol Vinyals, Pete Warden, Martin Wattenberg, Mar-
tin Wicke, Yuan Yu, and Xiaoqiang Zheng, “Tensor-
Flow: Large-Scale Machine Learning on Heterogeneous
Distributed Systems,” arXiv:1603.04467 (2016).
