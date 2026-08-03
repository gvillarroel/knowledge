---
type: Research Paper
title: Bosonic quantum error correction codes in superconducting quantum circuits
description: '- Pinned arXiv record: [2010.08699v1](https://arxiv.org/abs/2010.08699v1)'
resource: https://example.org/qec-arxiv-papers/resource/paper-2010-08699v1/sources%2Fmarkdown%2F2010.08699v1
tags:
- paper-2010-08699v1
- markdown
- rl
concept_id: concepts/paper-2010-08699v1/sources-markdown-2010.08699v1-8f0ab4b2d5
concept_path: concepts/paper-2010-08699v1/sources-markdown-2010.08699v1-8f0ab4b2d5.md
subject_iri: https://example.org/qec-arxiv-papers/resource/paper-2010-08699v1/sources%2Fmarkdown%2F2010.08699v1
ontology_class_iri: https://example.org/ontology/qec-arxiv-papers#Paper
ontology_version_iri: https://example.org/ontology/qec-arxiv-papers/1.0.0
source_id: paper-2010-08699v1
source_kind: markdown
source_path: sources/markdown/2010.08699v1.md
source_content_sha256: 83aee9ada957cda579a8406767a43e20abce6c22e7dd623c3ac20235574d1dd8
record_sha256: f5263234e5d6bda973a6c50e24213346c0e5cace1c1f98eef7b94d7b61a29f06
source_refs:
- https://example.org/qec-arxiv-papers/provenance/record/paper-2010-08699v1/711431d689223002edaaeb4b
record_id: sources/markdown/2010.08699v1
---

# Bosonic quantum error correction codes in superconducting quantum circuits

## Source citation

- Pinned arXiv record: [2010.08699v1](https://arxiv.org/abs/2010.08699v1)
- Authors: Cai, W.; Ma, Y.; Wang, W.; Zou, C. -L.; Sun, L.
- PDF: [https://arxiv.org/pdf/2010.08699v1](https://arxiv.org/pdf/2010.08699v1)
- PDF SHA-256: `0ab4fa0419b4c92eeb79f11d17389086d2b0e972ff5038c507d61497e7c42698`
- Extracted pages: 23

The following text was extracted page by page from the pinned PDF. Page headings are stable evidence locators.

## PDF page 1

Bosonic quantum error correction codes in superconducting quantum circuits
W. Cai,1,∗ Y . Ma,1,∗ W. Wang,1,∗ C.-L. Zou, 2, † and L. Sun 1, ‡
1Center for Quantum Information, Institute for Interdisciplinary Information Sciences, Tsinghua University, Beijing 100084, China
2Key Laboratory of Quantum Information, CAS, University of Science and Technology of China, Hefei, Anhui 230026, P . R. China
Quantum information is vulnerable to environmental noise and experimental imperfections, hindering
the reliability of practical quantum information processors. Therefore, quantum error correction (QEC)
that can protect quantum information against noise is vital for universal and scalable quantum compu-
tation. Among many different experimental platforms, superconducting quantum circuits and bosonic
encodings in superconducting microwave modes are appealing for their unprecedented potential in QEC.
During the last few years, bosonic QEC is demonstrated to reach the break-even point, i.e. the lifetime
of a logical qubit is enhanced to exceed that of any individual components composing the experimen-
tal system. Beyond that, universal gate sets and fault-tolerant operations on the bosonic codes are also
realized, pushing quantum information processing towards the QEC era. In this article, we review the
recent progress of the bosonic codes, including the Gottesman-Kitaev-Preskill codes, cat codes, and bino-
mial codes, and discuss the opportunities of bosonic codes in various quantum applications, ranging from
fault-tolerant quantum computation to quantum metrology. We also summarize the challenges associated
with the bosonic codes and provide an outlook for the potential research directions in the long terms.
I. INTRODUCTION
Quantum computers promise to exponentially or dramat-
ically outperform classical computers on certain problems
(e.g. factoring and unstructured database searching) because
of quantum coherence and true parallel computation [1–4].
However, quantum states are fragile and can be easily de-
stroyed by their inevitable coupling to the uncontrolled en-
vironment, which presents a major obstacle to universal quan-
tum computation [2, 5]. A practical quantum computer that
is capable of large circuit depth, therefore, ultimately calls for
operations on logical qubits protected by quantum error cor-
rection (QEC) against unwanted or uncontrolled errors and is
expected to spend a vast majority of its resources on error cor-
rection [6–11]. The realization of such a logical qubit with a
longer coherence time than its individual physical components
is considered as one of the most challenging and urgent goals
for current quantum information processing [3, 12]. When
universal gate sets on these logical qubits are available, quan-
tum information processing technologies would enter an era
of quantum protection. Finally, universal quantum computa-
tion is realizable by scaling up the system when the error rates
of the logical gates exceed a certain threshold.
Extensive attention has been paid to the qubit-based quan-
tum computation systems. However, the demonstration of
QEC in those systems is extremely challenging due to the
huge physical resource overhead and the difﬁculties in scal-
ing up the number of qubits [9, 13, 14]. So far, qubit-based
QEC encoding and gate operations on the encoded qubits still
remain elusive. Compared with qubits, harmonic oscillators
or bosonic modes provide an alternative route towards uni-
versal quantum computation. The bosonic modes are ben-
eﬁcial to quantum information processing in four aspects.
First, a single bosonic mode can provide an inﬁnitely large
Hilbert space, which allows QEC encoding by only extending
excitation numbers while keeping the noise channels ﬁxed.
Second, bosonic modes could be realized with multiple de-
grees of freedom, e.g. spatial, temporal, frequency, polar-
ization, or their combinations, and thus are scalable. Third,
bosonic modes are convenient in transferring information and
also can easily interface with many different physical systems,
therefore they are inevitable building blocks in quantum net-
works. Lastly, bosonic modes are fundamental and indispens-
able physical systems that cannot be replaced by other qubit
or ﬁnite-level quantum systems.
Therefore, bosonic modes have attracted a lot of interest
in quantum information processing and demonstrated wide
applications in quantum computation, quantum communica-
tion, quantum simulation, and quantum metrology in the last
decades, as shown in Fig. 1. Bosonic modes with QEC pro-
tection would exhibit better quantum properties and thus will
greatly broaden the above applications. As a result, exten-
sive explorations of QEC based on bosonic modes are de-
manded. As mentioned, QEC in a bosonic mode beneﬁts from
the inﬁnite-dimensional Hilbert space of a harmonic oscillator
for redundant information encoding and only one error syn-
drome that needs to be monitored, thus greatly reducing the
requirements on hardware. The bosonic modes could be real-
ized with microwave or optical photons, magnons, phonons,
plasmons, as well as polaritons [26]. Among them, supercon-
ducting circuit quantum electrodynamics (circuit QED) archi-
tecture [3, 27–32] is of particular interest for bosonic QEC
codes due to its unprecedented capability in quantum con-
trol. Three dimensional (3D) cavities [33], especially 3D
coaxial cavities [34], exhibit great quantum coherence with
single-photon lifetimes up to 1-10 ms. In analogy to optical
cavity QED that studies the interaction between atoms and
photons, circuit QED describes the interaction between su-
perconducting qubits (artiﬁcial atoms) and microwave pho-
tons in a cavity with ultrahigh cooperativities. Thus, this ex-
perimental platform allows universal control of the bosonic
mode with high ﬁdelities, and QEC that exceeds or closely
reaches the break-even point [12, 35, 36], logical-qubit oper-
ations [19, 35–38], and fault-tolerant operations [15–17] have
arXiv:2010.08699v1  [quant-ph]  17 Oct 2020

## PDF page 2

2
/uni03C9RO
/uni2223gn/uni27E9
/uni2223en/uni27E9
/uni2223f /uni232A
path independent 
quantum gates
Q2 R2
autonomous 
fault-tolerantnon-fault-tolerant
FT parity 
measurement
–3 –2 –1 0 1 2 3
Re (α)
–3 –2 –10 1 2 3–3 –2 –1 0 1 2 3
–0.6
–0.4
–0.2
0.0
0.2
N = 9
quantum error 
correction
aˆ
bˆ bˆout
κout
g(t)
0.4
0.6
N = 12
|+ZL/uni232A
|–ZL/uni232A
|–XL/uni232A
|–YL/uni232A
|+YL/uni232A
|+XL/uni232A
logical 
data-qubit 
encoding
standing-mode
 propagating 
photon
/uni03C9ge
/uni03C9ef
/uni03C9ET
/uni2223e4/uni27E9/uni2223e3/uni27E9/uni2223e2/uni27E9/uni2223e1/uni27E9/uni2223e0/uni27E9
/uni2223e/uni232A
/uni2223g/uni232A
R Q11
/uni2223g4/uni27E9/uni2223g3/uni27E9/uni2223g2/uni27E9/uni2223g1/uni27E9/uni2223g0/uni27E9
S1 S2
Q3
R3
–3
3
2
1
0
–1
–2
–3 Im (α)
–3 –2 –1 0 1 2 3
Exp
N = 63
2
1
0
–1
–2
Theory
N = 3
error-transparent
gates
O
H H
O
simulating molecular 
vibronic spectra 
topological  invariant 
measurement
O
O
Bosonic 
Mode
Sensing
mode
Readout
mode
Qubit
manipulation
D
N
0
Nϕ
U1 U2 ϕ0
0P
Initial state Dynamic 
process Final state Measurement Estimator
xest
quantum 
parameter 
estimation
single-mode 
sensing
W (α)
FIG. 1. Quantum applications of bosonic modes. Bosonic modes have wide applications in quantum computation, quantum communication,
quantum simulation, and quantum metrology. Here we only list a small portion of them. For quantum computation, QEC and fault-tolerant
operations on bosonic codes have been demonstrated. Adapted from Refs. [15–18]. For quantum communication, quantum state transfer,
remote entanglement, gate teleportation, etc., have been demonstrated. Adapted from Refs. [19, 20]. A single bosonic mode can be employed
for quantum metrology to achieve a measurement precision beyond the shot-noise limit. Moreover, it is promising to achieve quantum-
enhanced sensing by constructing suitable QEC codes. Adapted from Ref. [21, 22]. Bosonic modes also can be used to simulate solid-state
materials and molecular vibrations. Adapted from Refs. [23–25].
already been demonstrated based on bosonic codes.
This article reviews the recent development of bosonic QEC
codes in superconducting quantum circuits. The organization
is as follows. A basic introduction of QEC and bosonic modes
is provided in Sec. II. Details on the three most widely used
bosonic codes, i.e. the Gottesman-Kitaev-Preskill (GKP), cat,
and binomial codes are presented in Sec. III. In Sec. IV, we
summarize the underlying kernel techniques to realize the
bosonic codes as well as the universal control of the codes.
With the basic toolkit available, intriguing potential applica-
tions of bosonic codes and their proof-of-principle demon-
strations in the fault-tolerant quantum computation, quantum
communication, quantum simulation, and quantum metrology
are presented in Sec. V. Finally, future directions and chal-
lenges are discussed in Sec. VI.

## PDF page 3

3
Multi-qubit code Bosonic code(a) (b)
FIG. 2. Multi-qubit architecture vs bosonic-mode architecture.
Enlarged Hilbert space can be constructed with multiple qubits (a) or
one bosonic mode (b). Qubits and harmonic oscillators are critical el-
ements for these two different architectures. However, their roles are
exchanged: in the qubit-based architecture, quantum information is
stored on the qubits while harmonic oscillators are used to couple or
readout the qubits; in the bosonic architecture, quantum information
is stored in the bosonic modes while the qubits provide the necessary
nonlinearity for the control and readout of the bosonic modes.
II. BASICS OF QEC
In this section, we provide a brief introduction of the QEC
codes and the basic properties of a bosonic mode. For more
detailed discussions on QEC and fault-tolerance in the context
of the qubit model, we suggest the review articles Refs. [8, 10,
11, 39, 40] for further reading. We also refer the readers to
Refs. [41, 42] for related reviews on bosonic codes.
The key idea of classical error correction to protect infor-
mation against noise is to encode the information with added
redundancy. By doing so, even if some information in the en-
coded message is corrupted by noise, there is still enough re-
dundancy in the encoded information to fully recover the orig-
inal information. For example, the classical repetition codes
are to use odd multiples of 0’s and 1’s to represent the log-
ical 0 and logical 1 respectively. The only classical error of
bit-ﬂips can be corrected by the majority voting, and this type
of error-correcting codes can suppress the leading orders of
errors.
Similar to the code redundancy in the classical error correc-
tion, QEC is possible by expanding the Hilbert space of a log-
ical qubit [6, 7]. Different from the classical case, quantum in-
formation could be any superposition of codewords that occu-
pies a subspace of the expanded Hilbert space, called the code
space. Restricted by quantum coherence, QEC cannot mea-
sure the codewords directly, but rather measure the so-called
error syndromes to diagnose possible errors without perturb-
ing the encoded information. By constructing QEC codes,
these requirements could be satisﬁed if errors due to noise
could turn the code space into different error spaces. Then,
errors that have occurred could be detected by distinguish-
ing different subspaces, and appropriate recovery operations
can be applied to restore the original quantum information by
mapping the error space back to the code space.
For example, the QEC codes could be constructed with
multiple qubits, as illustrated in Fig. 2a. Quantum information
is encoded with a simple repetition code span{|000⟩ ,|111⟩}.
In such a way, quantum information is essentially stored
non-locally through entanglement among the physical qubits,
while single physical qubits contain no encoded information.
Because noise is generally local and independent, it only cor-
rupts little about the stored information. A bit-ﬂip error on the
code could be detected by measuring the correlations between
neighboring qubits (the error syndromes) instead of projec-
tive measurements of the encoded quantum states. The essen-
tial part for QEC to work is that these error syndrome mea-
surements need to be non-destructive to the encoded informa-
tion, which is realized by introducing and measuring ancillary
qubits or modes that interact with the physical qubits consti-
tuting the QEC codewords.
The above QEC would be properly described by a more
general mathematical framework. The QEC condition is a
sufﬁcient and necessary condition for a QEC code to protect
against errors in a given error set ε ={ ˆEi}:
ˆP ˆEi
† ˆE j ˆP = αi j ˆP (1)
where ˆP is the projection operator onto the code space and
αi j is a Hermitian matrix [2]. Consequently, we have:
⟨0L| ˆEi
† ˆE j|0L⟩ =⟨1L| ˆEi
† ˆE j|1L⟩ , (2)
and
⟨0L| ˆEi
† ˆE j|1L⟩ =⟨1L| ˆEi
† ˆE j|0L⟩ = 0, (3)
where|0L⟩ and|1L⟩ are the basis states of the codewords.
Equation 2 requires that the logical states are indistinguishable
under different errors, independent of the codewords. Oth-
erwise, the codewords will suffer the deformation error and
the environment could potentially distinguish these two basis
states and eventually induces uncorrectable errors. Equation 3
requires that all the spaces are orthogonal to each other.
In the past decades, most of the theoretical and experimen-
tal efforts are spent on the qubit-based QEC codes. The con-
catenated encoding is proposed for fault-tolerance, but it is
tremendously challenging because of the required extremely
low gate error threshold and large resource overhead [6, 7].
The recently developed surface codes [9], which use the
topological property of a large number of qubits in a two-
dimensional grid to protect against external noise, can tolerate
a much higher error rate∼ 1%, but still at the cost of huge re-
source overhead. Both of these approaches need to scale up
the number of physical qubits for achieving QEC. There is a
lot of experimental progress along this line, for example in
trapped-ion systems [43, 44], nitrogen-vacancy centers in di-
amond [45, 46], and superconducting circuits [47, 48]. How-
ever, to have extended lifetime than the physical qubits and to
have logical operations are difﬁcult to achieve with the multi-
qubit encoding because the number of distinct error channels
increases with the number of qubits, and non-local gates on a
collection of physical qubits are required.
Alternatively, there is another strategy which uses a single
quantum system with intrinsically large Hilbert space, instead
of a collection of physical qubits, to redundantly encode quan-
tum information and would signiﬁcantly reduce the required

## PDF page 4

4
Cat Code Binomial Code GKP
2016 20202018 20192017
Coherent oscillation
2015
SNAP GRAPE
Pumped cat Kerr cat
Operation / QEC
on a single mode
Operation
on multiple modes 2018 2020
Geometric cPhaseGate teleportation
2019
State transfer BS eSWAP
GKP
Bosonic Code
1997 2001
... Cat Code
2013
Binomial Code
2016 20202018 20192017
FT error detection
Repetition cat PI gateKerr cat
Code performance
2014
FT on cat
Bosonic code
theory
FT operation
on a single mode 2018 2020
FT error detection
2019
ET gate
PI gate
FT operation
on multiple modes
FIG. 3. Roadmap of bosonic codes. Tremendous progress of the bosonic codes has been made in the last two decades. Theories of bosonic
codes as the foundation are listed at the bottom [49–59]. The above rows list representative steps in the experimental development of bosonic
codes in superconducting circuit QED architectures. QEC and gate operations have been demonstrated based on cat codes [12], binomial
codes [35], and GKP codes [36]. Photon-number-selective arbitrary phase (SNAP) gate [60] and optimal control technique based on gradient
ascent pulse engineering (GRAPE) [37] are important for universal control of the bosonic mode. Pumped and Kerr cat qubits [61–63] have
been developed with biased noise for potentially important QEC applications. Operations on multiple modes such as state transfer [64], gate
teleportation [19], beam-splitter (BS) interaction [65], exponential SW AP gate [66], and geometric controlled-phase gate [38] have also been
demonstrated. Fault-tolerant (FT) error detection [15], path-independent (PI) phase gate [16], and error-transparent (ET) gate [17] on a single
bosonic mode have been developed. In the future, FT control needs to be extended to multiple modes for universal quantum information
processing.
Year Code Ancilla T1 Ancilla T∗
2 Fock{|0⟩ ,|1⟩} encoding Uncorrected code Corrected code
2016 [12] Cat 35 µs 12 µs 287 µs 147 µs 318 µs
2019 [35] Binomial 30 µs 40 µs 216 µs 71 µs 200 µs
2020 [17] Binomial (ET) 35 µs 25 µs - 185 µs 364 µs
2020 [36] GKP (Square) 50 µs 60 µs 245 µs (T1) - 275 µs (XZ ) 160 µs (Y )
2020 [36] GKP (Hex) 50 µs 60 µs 245 µs (T1) - 205 µs
2020 [18] Cat (AQEC) 39 µs 17 µs 440 µs 130 µs 288 µs
TABLE I. Experimental performance of various bosonic codes. The right three columns list the measured process ﬁdelity decay times
except for the GKP experiment (state decay times).
hardware. One can realize QEC ﬁrst and then scale up for
more complicated quantum information processing applica-
tions. A harmonic oscillator or a bosonic mode is just such a
system that supports an inﬁnitely large Hilbert space of Fock
states and has long been proposed to store quantum infor-
mation. Utilizing the redundancy of the Hilbert space, QEC
could be constructed in a single bosonic mode. The main ad-
vantage of such a QEC scheme is that the large Hilbert space
is achieved in only a single degree of freedom so that the as-
sociated errors are restricted.
The basic bosonic code architecture is shown in Fig. 2b. A
coupled non-linear element, typically a two-level qubit, is also
essential for arbitrarily controlling and manipulating quantum
states of the harmonic oscillator. Details about the universal
control of this composite system will be discussed in Sec. IV.
In this article, we will only focus on microwave photons in
superconducting microwave cavities which are excellent har-
monic oscillators with long lifetimes (up to 1-10 ms [34]) and

## PDF page 5

5
ideal for quantum memories or logical qubits in the ﬁrst place.
For a simple case with the error set ε ={ ˆI, ˆa}, where ˆa
denotes the single-photon-loss error due to the damping, there
is obviously only one error syndrome, photon number parity
or generalized parity, that needs to be monitored continuously.
To meet the QEC condition Eq. 2, the basis states of the logical
qubit should satisfy:
⟨0L| ˆa† ˆa|0L⟩ =⟨1L| ˆa† ˆa|1L⟩ . (4)
This requires that the codewords should have equal average
photon numbers. It can also be understood as the environ-
ment should not distinguish the two logical basis states from
a photon loss event in order to preserve the encoded quantum
information. Note that for continuous damping or attenuation
the above error set{ ˆI, ˆa} is only approximate and not bounded
(cannot be normalized to satisfy the condition ∑i ˆEi
† ˆEi = ˆI).
The exact expression of the error set for photon loss errors is:
ˆEl =
√
(1− e−η )l
l! e− η
2 ˆa† ˆa ˆal. (5)
where l = 0,1, ...and η = κt≪ 1 is the photon loss coefﬁcient
for storing quantum information with a mode dissipation rate
κ and a duration t. We can also have η = αd for transmitting
photons over a distance d with a channel attenuation coefﬁ-
cient α [67].
We ﬁnally note that when more photons are added to the mi-
crowave cavity for information redundancy, although no more
type of errors is introduced, the error rate becomes n times
larger ( n is the average photon number in the codewords).
This is the price one has to pay for any QEC schemes: redun-
dantly encoding quantum information always increases either
the number of error channels or the error rate. However, good
control and QEC on the logical qubits hopefully can compen-
sate this negative effect and eventually lead to better protec-
tion of quantum information with extended coherence.
III. QEC BASED ON BOSONIC CODES
Figure 3 summarizes the recent progress of the bosonic
codes including both theoretical and experimental develop-
ments. Here, we concentrate on three bosonic codes based on
a single bosonic mode, i.e. GKP, cat, and binomial codes, and
provide discussions on the related theories and the recent ex-
perimental progress. The experimental achievements of these
three types of codes are summarized in Fig. 4 and Table I.
A. Cat codes
Coherent states are quasi-classical states that can be readily
generated with classical methods, and hence they have been
widely used in communication. Because phase is more robust
against photon loss error, information is typically encoded in
the phase of a coherent state. In analogy to classical phase-
shift keying, quantum information can also be encoded to the
phase of a coherent state. The simplest code (two-component
cat code) is thus to use two coherent states with opposite
phases for its two basis states:
|0⟩ =|α⟩ ,
|1⟩ =|−α⟩ . (6)
However, this code does not have redundancy and is not er-
ror correctable, because when the single-photon-loss error ˆ a
occurs the state remains in the same code space.
The four-component cat code is later proposed to encode
quantum information in a superposition state of coherent
states with four different phases [51], as shown in Fig. 4a.
With the extra degrees of freedom, this code has the neces-
sary redundancy to ﬁght against photon loss errors: two di-
mensions{|0L⟩ ,|1L⟩} for the encoding, while the other two
{|0E⟩ ,|1E⟩} for error detection. The code basis states and er-
ror basis states are respectively:
|0L⟩ = C+
α = N (|α⟩ +|−α⟩),
|1L⟩ = C+
iα = N (|iα⟩ +|−iα⟩), (7)
and
|0E⟩ = C−
α = N (|α⟩−|−α⟩),
|1E⟩ = C−
iα = N (|iα⟩−|−iα⟩), (8)
where N ≈ 1/
√
2 is the normalization factor. The code basis
states have the same average photon number, but are not ex-
actly orthogonal as preferred for information encoding unless
α is sufﬁciently large.
To avoid the non-orthogonality error, the above cat codes
can be made orthogonal by using states with well-deﬁned gen-
eralized parities:
⏐⏐0′
L
⟩
= N0(C+
α +C+
iα ) = N0(|α⟩ +|−α⟩ +|iα⟩ +|−iα⟩),⏐⏐1′
L
⟩
= N0(C+
α−C+
iα ) = N0(|α⟩ +|−α⟩−|iα⟩−|−iα⟩),
(9)
where N0≈ 1/2.|0′
L⟩ contains photon number states that are
multiples of four, while |1′
L⟩ contains photon number states
that are even but not multiples of four. However, these two
basis states do not have the same average photon numbers un-
less α is large enough or at certain sweet spots.
Therefore, at large enoughα both of these two codes satisfy
the QEC conditions (Eqs. 2 and 3), and can both efﬁciently
correct the single-photon-loss error in the error set ε ={ ˆI, ˆa}.
For both codes, the code and error spaces have exact photon-
number parities of even and odd, respectively. Photon parity
is thus the error syndrome for error detection, which can be
readily realized in a quantum non-demolition manner in a cir-
cuit QED architecture [68].
These codes have the following two major properties. First,
single-photon-loss errors cause quantum jumps of the en-
coded state between the code and error spaces and each er-
ror is accompanied by a phase shift of π/2 about the Z axis

## PDF page 6

6
-3 0 3
-3
0
3
-3 0 3
-3
0
3
-3 0 3
 -3 0 3
Cat Binomial GKP
ˆa ˆa  (aˆ)correct correct correct
-3 0 3
-3
0
3
-3 0 3
-3 0 3
-3
0
3
-3 0 3
0L 1L
-3 0 3
-3
0
3
-3 0 3
0L 1L
-3 0 3
-3
0
3
-3 0 3
0L 1L
(a) (b) (c)
(d) (e) (f)
0
–2
2
0
1
0
0–2 20 1
/uni03A8|( q)|2
|/uni03A8˜ (p)|2q/ /uni03C0
p/ /uni03C0
W
|±ZL/uni232A
|±XL/uni232A
2V 2
1
/uni03C0
/uni0394
0.0
0.4
0.8
0.0 0.5 1.0
QEC on
QEC off
Simulation Z
X
Y
|/uni2329Re(()/uni232A|
/uni22231L/uni232A = /uni22232/uni232A
Code space Error space
Ancilla
qubit
/uni2223g/uni27E9
/uni2223e/uni27E9
EN
DE
ED (a)
EC (UR)
/uni2223 /uni22233/uni232A
/uni22231/uni232A
ˆ
/uni22230L/uni232A =
UL
0/uni232A + /uni22234/uni232A
/uni221A2
1.0
0.8
0.6
0.4
0.2
 Process fidelity, F/uni03C7(t)
7006005004003002001000
Time (µs)
Uncorrected Fock 0, 1 encoding
Corrected binomial code for tw = 17.895 µs 
Uncorrected binomial code
Uncorrected transmon
/uni03C4 = 216 ± 2 
µs
/uni03C4 = 200 ± 1 µs
/uni03C4 = 71 ± 2 µs
/uni03C4 = 38 ± 1 µs
Time (ms)
±0³|±C+
D³ ±D³+±–D³ ±C–³=±D³– ±–D³ D
±C+³+±CiDD
+ ³ ±C–³+ iDD ±Ci
– ³
±1³|±C+ ³ ±iD³+±–iD ³ iD ±C– ³ ±iD³–±–iD³ iD
Even
parity
+Zc
+Xc +Yc
+Zc
â
â
â
â
+Xc +Yc
+Zc
+Xc +Yc
+Zc
+Xc +Yc
Odd
parity
1.0
0.9
0.8
0.7
0.6
0.5
0.4
0.3
0.2
Process /f_idelity, F(t)
100806040200
Time, t (/uni03BCs)
0
Number of cat-code syndrome measurements
1 12 34 45 6
 Uncorrected transmon
 Uncorrected Fock 0,1 encoding
 Uncorrected cat code
 Corrected cat code
 Corrected cat code; with post-selection
n¯
0 = 2
W = 17 ± 1 /uni03BCs
W = 318 ± 5 /uni03BCs
W = 287 ± 4 /uni03BCs
W = 570 ± 30 /uni03BCs
W = 147 ± 8 /uni03BCs
n¯0 = 2
FIG. 4. QEC with three typical bosonic codes. (a-c) Wigner functions of the logical qubit basis states in the code and error spaces for the
cat, binomial, and GKP codes, respectively. (d-f) Experimental demonstration of QEC based on these three bosonic codes. Adapted from
Refs. [12, 35, 36].
within the logical space, but without corrupting the encoded
quantum information. The original information is not fully
recovered until after the fourth photon loss error. Remark-
ably, this property makes explicit error correction after each
error detection unnecessary and only requires tracking of the
number of errors and implementing the recovery operation at
the end of the whole QEC process. Therefore, the deleterious
effect of imperfect recovery operations can be eliminated.
Second, in the absence of quantum jumps the quantum state
deterministically shrinks towards the vacuum state. This in-
evitable property demands one to re-pump energy into the
codeword before the coherent states start to overlap and cause
a considerable non-orthogonality error. However, this error
could not be fully corrected by a unitary operation.
To mitigate the non-orthogonality error, there are two
strategies to continuously pump or stabilize the cat codes. One
requires four-photon driven dissipative process with speciﬁ-
cally engineered four-photon dissipation [52]:
dρ
dt = L [√κ4ph( ˆa4− α4)]ρ, (10)
where L is the Lindblad superoperator and κ4ph is the four-

## PDF page 7

7
photon dissipation rate. As a result, the four states |±α⟩ and
|±iα⟩ are the steady states and the logical states will be con-
ﬁned in this manifold.
The other strategy that can achieve the same stabilization is
to engineer a speciﬁc Hamiltonian [55]:
ˆH =−K ˆa†4 ˆa4 + ε4( ˆa†4 + ˆa4), (11)
where K is the coefﬁcient of the high-order Kerr non-linearity
and ε4 is the amplitude of the four-photon drive. Then the four
states|±α⟩ and|±iα⟩ are the eigenstates of this Hamiltonian,
and the adiabatic theorem ensures the logical states to be con-
ﬁned in this manifold. By tracking the photon number parity,
the dynamics can be restricted to the even parity states (or the
code space).
When the cat codes are stabilized by one of the above strate-
gies, fault-tolerant gates can be realized through a two-photon
drive ˆa†2 + ˆa2 for arbitrary rotations around X and a beam-
splitter-like drive ˆa†2
1 ˆa2
2 + ˆa†2
2 ˆa2
1 for the two-qubit entangling
gate [52]. Both strategies share similar principle and face dif-
ﬁculties of relatively strong four-photon drives [69], awaiting
experimental realization.
Cat codes can tolerate more errors by increasing the num-
ber of coherent state components. The basis states of a n-
component cat state can be written as [67]
|0L⟩ ∝
n
∑
k=1
⏐⏐⏐αei2kπ/n
⟩
,
|1L⟩ ∝
n
∑
k=1
ei4kπ/n
⏐⏐⏐αei2kπ/n
⟩
.
(12)
This code can correct photon loss errors up to n/2− 1 order.
But the average photon number should be increased to satisfy
the orthogonality condition required by QEC. Cat codes can
also be extended to multiple modes that can protect against
photon loss via either active syndrome measurement or an au-
tonomous procedure. For example, the pair-cat codes [70] oc-
cupying two modes can protect against arbitrary number of
photon loss errors in one mode given the other one has no
error.
Experimentally, the cat code (Eq. 7) is the ﬁrst bosonic code
that surpasses the break-even point [12], as shown in Fig. 4d,
beneﬁting from its special property that tracking the number
of errors without immediate recover operation is equivalent to
having corrected the state. Universal control of a logical qubit
with the cat coding (Eq. 7) has been realized separately by nu-
merically optimized pulses [37] (see Sec. IV for more details).
A controlled-phase (cPhase) gate between two coherent-state
encodings (Eq. 6) has also been realized [38].
Lastly, we want to mention that simpler ideas than Eqs. 10
and 11 have been experimentally realized for a two-photon
drive case [61–63, 71] based on the two similar strategies:
dρ
dt = L [√κ2ph( ˆa2− α2)]ρ (13)
and
ˆH =−K ˆa†2 ˆa2 + ε2( ˆa†2 + ˆa2). (14)
In these two cases, the stabilized manifold is {|α⟩ ,|−α⟩}.
Since this Hilbert space is not large enough for error correc-
tion, it only deﬁnes the so-called cat qubit.
Although this type of qubit cannot be protected against pho-
ton loss error, it has a very special and interesting property,
i.e., its noise is biased. This can be understood for the cat
qubit deﬁned as:
|0⟩α = 1√
2
(C+
α +C−
α ) =|α⟩ + O(e−2|α|2
),
|1⟩α = 1√
2
(C+
α−C−
α ) =|−α⟩ + O(e−2|α|2
).
(15)
The built-in stabilization mechanism provides a natural pro-
tection of this qubit. The encoded information is non-local in
the phase space of the harmonic oscillator. The distance be-
tween the two basis states thus prevents any noise process that
induces local displacement in phase space. As a result, the bit-
ﬂip error is exponentially suppressed with the average number
of photons, while the phase-ﬂip error only increases linearly.
Therefore, the cat qubit is noise biased and this biased struc-
ture of noise has been observed experimentally [63, 71]. Co-
herent rotations around X on such a stabilized cat qubit have
also been demonstrated [62].
Furthermore, due to the inﬁnite-dimensional Hilbert space
that the cat qubits are embedded in, a universal set of bias-
preserving gates can be realized on the cat qubits [58, 72],
which however is not possible for regular two-level systems.
Fault-tolerant error syndrome detection can also be achieved
based on the biased-noise cat qubit as the ancilla [57]. The cat
qubits can also be the promising building blocks for a surface
code tailored to biased noise with high error thresholds [73–
75]. Therefore, the biased-noise cat qubits are important re-
sources for fault-tolerant quantum computation.
B. Binomial codes
Binomial codes are based on superpositions of truncated
Fock states weighted with binomial coefﬁcients [53]. These
codes are designed to exactly correct errors that are polyno-
mial up to a speciﬁc order in photon loss error ˆa, photon gain
error ˆa†, and photon dephasing error ˆn, i.e., the error set is:
ε ={ ˆI, ˆa, ˆa2, ..., ˆaL, ˆa†, ( ˆa†)2, ..,( ˆa†)G, ˆn, ˆn2, ..., ˆnD}. (16)
The code basis states are:
|0L⟩ = 1√
2N
[0,N+1]
∑
p,even
√
C p
N+1|p(S + 1)⟩ ,
|1L⟩ = 1√
2N
[0,N+1]
∑
p,odd
√
C p
N+1|p(S + 1)⟩ ,
(17)
where C p
N+1 is the binomial coefﬁcient, the spacing is S =
L + G, N = max{L, G,2D}, and p is from 0 to N + 1 with the
maximum Fock number being (N + 1)× (S + 1).

## PDF page 8

8
CNOT Geometric cPhase
eSWAP Teleported CNOT
Control Target
Ancilla
transmon
Control
C1L
C1L
T0L
T1L
Target
CNOT
Read out
𝟏𝑳 𝒆 |𝟏 𝑳〉
𝟏𝑳 𝒈 |𝟏𝑳〉
D1
D2
Z
X
X
ZC1
C2
Module 1
Module 2
Cavity
Transmon
Readout
resonator
Bus mode
Alice
Alice
Bob
Bob
qB
qB
qA
|g⟩|g⟩
|Φ⟩
|Ψ⟩
|Φ⟩
|Ψ⟩
BS BS−1
CPS CPS
H HXθ
BS BS−1
CPS
|+⟩qC
(a)
(c)
(b)
(d)
FIG. 5. Unitary gates on two logical qubits. (a) Controlled-not (CNOT) gate between two logical qubits with the target one is binomially
encoded. Adapted from Ref. [76]. (b) Geometrically controlled phase gate on two binomially encoded logical qubits. Adapted from Ref. [38].
(c) Exponential-SW AP gate on two bosonic qubits. Adapted from Ref. [66]. (d) Teleported CNOT gate between two binomially encoded
logical qubits. Adapted from Ref. [19].
It can be clearly seen that the two basis states contain com-
pletely different series of Fock states, therefore are exactly
orthogonal to each other. It is also easy to check that both
states have exactly the same average photon numbers. As a
result, the QEC conditions Eqs. 2 and 3 are strictly satisﬁed.
The spacing of the occupied Fock states is S + 1, therefore,
the errors can be uniquely distinguished by measuring photon
number modulo S + 1, i.e., the error syndrome is the gener-
alized parity. Because the basis states in the code space and
all error spaces are orthogonal, the binomial codes have the
advantage of having explicit unitary operations for repump-
ing energy into the mode when compared to the cat codes.
Besides, since the occupied Fock states are truncated, unitary
operations on the binomial codes might also be more conve-
nient.
Figure 4b shows the lowest-order binomial code:
|0L⟩ = (|0⟩ +|4⟩)/
√
2,
|1L⟩ =|2⟩ ,
(18)
This code can protect against single-photon-loss error with
ε ={ ˆI, ˆa}. The average photon number is two, smaller than
that of the typical cat code. When an error occurs, the corre-
sponding error space is:
|0E⟩ =|3⟩ ,
|1E⟩ =|1⟩ . (19)
Clearly, these two basis states have different average photon
numbers, not satisfying the QEC condition Eq. 2 anymore.
A unitary recovery operation has to be applied immediately
to correct the error, otherwise, quantum information will be
corrupted. This property is different from the previously dis-
cussed cat codes.
A comparison between the lowest-order binomial code with
the qubit-based four-qubit code [77] can better shed light on
the efﬁciency and advantage of the bosonic codes. The four-
qubit code can correct single amplitude damping errors, ε =
{ ˆI, ˆσ−
1 , ˆσ−
2 , ˆσ−
3 , ˆσ−
4}, with the basis states:
|0L⟩ = 1√
2
(|0000⟩ +|1111⟩),
|1L⟩ = 1√
2
(|1100⟩ +|0011⟩).
(20)
This encoding utilizes 24 = 16 dimensional expanded Hilbert
space. In order to uniquely distinguish the ﬁve errors in the
error set, three error syndromes are required. In marked con-
trast, although both the lowest-order binomial code and the
four-qubit code have the same average excitation of two, the
binomial code occupies only the lowest ﬁve levels of the oscil-
lator’s Hilbert space (ﬁve dimensions) and needs only one er-
ror syndrome for error detection. Therefore, the bosonic codes
are indeed hardware-efﬁcient and can greatly save physical re-
sources.

## PDF page 9

9
According to Eq. 17, in order to correct more errors, for ex-
ample, ε ={ ˆI, ˆa, ˆa2, ˆn}, one has to use a higher-order binomial
code with a larger Fock state dimension for the encoding:
|0L⟩ =|0⟩ +
√
3|6⟩
2 ,
|1L⟩ =
√
3|3⟩ +|9⟩
2 .
(21)
The spacing of the occupied Fock states is three, i.e. the log-
ical states are conserved under the generalized parity oper-
ator ˆΠ = ei 2
3 π ˆa† ˆa. A photon gain error and two-photon-loss
errors have the same change in the photon number modulo 3.
As a result, the above code can also correct errors in the set
ε ={ ˆI, ˆa, ˆa†, ˆn}. For large average photon number in the code-
words, the binomial and cat codes asymptotically approach
each other since both photon number distributions approach a
normal distribution [56].
It is worth noting that even when no error is detected
(no photon loss error) the binomial codes still suffer the
non-unitary backaction associated with no-error evolution
e−(κ/2) ˆa† ˆat (see Eq. 5 for the exact expression of photon loss
errors). This is a nontrivial distortion of the code states and
must be corrected. A two-mode version of the codes with the
same spacing and the same total excitation number but dis-
tributed in different modes can mitigate this problem [49, 53].
Experimentally, the lowest-order binomial code (Eq. 18)
has been demonstrated with repetitive QEC based on real-
time feedback control [35], as shown in Fig. 4e. The QEC
protected quantum information has a lifetime nearly beating
the break-even point. A high-ﬁdelity universal gate set opera-
tion on the logical qubit has also been demonstrated. Towards
universal quantum computation based on binomial codes, a
cPhase gate between two binomial logical qubits has been
realized through a geometric method [38] (Fig. 5b). A tele-
ported CNOT gate between two binomial logical qubits and
a CNOT gate with the target being a binomial logical qubit
have also been realized [19, 76], as illustrated in Figs. 5a and
5c, respectively.
C. GKP codes
The GKP codes were ﬁrst proposed by Gottesman, Kitaev,
and Preskill in 2001 [50]. The general GKP codes can protect
a state of a d-dimensional quantum system (a qudit) encoded
in a harmonic oscillator against most physical noise precesses.
For a typical two-level logical qubit, the GKP code is deﬁned
as coherent superpositions of inﬁnitely squeezed states or the
eigenstates of the position operator ˆq with a spacing of 2√π:
|0L⟩ ∝
∞
∑
s=−∞
⏐⏐q = 2s√π
⟩
,
|1L⟩ ∝
∞
∑
s=−∞
⏐⏐q = (2s + 1)√π
⟩
.
(22)
These two basis states are shifted by√π relative to each other
and their corresponding Wigner functions in the q− p phase
space are square grid patterns.
It is known that the GKP codes belong to the class of stabi-
lizer codes. The grid states of Eq. 22 are in fact stabilized by
two mutually commuting stabilizers:
ˆSq = ˆD(i
√
2π) = ei2√π ˆq,
ˆSp = ˆD(
√
2π) = e−i2√π ˆp,
(23)
where ˆD(α) = eα ˆa†−α∗ ˆa is the displacement operator and ˆp is
the momentum operator. Consequently, the GKP code space
is the simultaneous eigenspace of the above two stabilizers.
The corresponding Pauli operators are simple displacements
of half the grid spacing:
X = ˆD(
√
π/2) = e−i√π ˆp,
Z = ˆD(i
√
π/2) = ei√π ˆq,
Y = ˆD(
√
π/2 + i
√
π/2),
(24)
satisfying the Pauli relations.
In the Fock state representation, the ideal GKP codewords
contain inﬁnite number of photons and correspond to Wigner
functions that extend to inﬁnity in phase space. Therefore, the
ideal GKP codes are not physical. The realistic GKP states
have ﬁnite photon energy and are approximate by replacing
the delta functions with ﬁnitely squeezed Gaussian state and
the uniform superposition proﬁle with a Gaussian envelope
centered around q = 0. The approximate GKP codewords
therefore become [50, 78]:
|0L⟩approx ∝
∞
∑
s=−∞
e−2π ˜∆2s2
ˆD(s
√
2π)|ψ0⟩ ,
|1L⟩approx ∝
∞
∑
s=−∞
e−π ˜∆2(2s+1)2/2 ˆD(s
√
2π) ˆD(
√
π/2)|ψ0⟩ ,
(25)
where 1/ ˜∆ is the width of the Gaussian envelope and|ψ0⟩ =´ dq
(π∆2)1/4 e−q2/(2∆2)|q⟩ is the squeezed vacuum state with ∆
being the squeezing parameter. The corresponding Wigner
functions in the q− p phase space are shown in Fig. 4c.
The square GKP codewords have asymmetric error-
resistance property because of the asymmetric nature of the
three Pauli operators deﬁned in Eq. 24. To get a symmet-
ric protection against errors in all three directions, the lat-
tice of the square code can be transformed into a hexagonal
code. The hexagonal GKP code may be the ultimate optimal
code, because starting from a random initial code, numeri-
cal optimization for both a photon loss channel and a Gaus-
sian thermal loss channel always converges to the hexagonal
GKP code [79]. In addition, compared to other bosonic QEC
codes including cat codes, binomial codes, and numerically
optimized codes, the GKP codes show the best performance
for most values of the photon loss rate [56]. However, for the
same average photon number, the GKP codes have a larger

## PDF page 10

10
bandwidth of photon number distribution or a larger occupied
Hilbert space, and thus suffer more distortion from Kerr effect.
This poses an experimental challenge to high-ﬁdelity recovery
and demands further optimization of the codes including the
Kerr effect [80].
The GKP codes are designed to correct small shift errors
as long as |δ q| <√π/2 and |δ p| <√π/2. Measurements
of the stabilizers (the error syndromes) unambiguously reveal
the underlying errors, which can be corrected by shifting back
with the minimal amount of displacement. A variety of local
errors, such as photon loss, thermal noise, photon dephasing,
and even spurious nonlinearities induced by the coupled an-
cilla qubit, lead to a continuous evolution of the states in phase
space, and hence result in only local effects in the phase space.
Therefore, as long as the stabilizers are measured frequently
enough, the noise-induced shifts will be small and thus can be
detected and corrected. In fact, it is also shown that the local
errors can be expanded into small shift errors in p and q when
the number of photons in the GKP codewords are small [78].
Another advantage of the GKP codes is that the Clifford
gates only require Gaussian operations on the photonic state,
which is usually easy to perform in the experiment. Under
these gate operations, small deviations of q and p remain
small, which means the locality of the errors is preserved. In
this sense, these gates are fault tolerant.
However, the non-Clifford gates are much harder than the
Clifford gates, demanding non-Gaussian operations or re-
sources. One method is to prepare a magic state such as the
eigenstate of the Hadamard gate, and use it as an ancilla. Then
only Clifford gates and homodyne measurement are required
to perform the non-Clifford ˆT gate [50]. The preparation of
the codewords is also challenging and requires non-Gaussian
operations.
It is hard to scale up the GKP codes only by increasing the
squeezing rate in a practical physical system. Besides, the
GKP codes are not designed to protect against rare and large
errors. Therefore, the GKP codes are usually considered to
concatenate with other stabilizer codes for a second layer of
protection [41, 81], for example, the surface codes. The QEC
process for these stabilizer codes only requires Clifford gates
and homodyne measurement. Several theoretical works [41,
82–84] calculate the required squeezing level, about 10-20 dB,
to reach the fault-tolerant threshold of the surface-GKP code
based on different assumptions on the error source.
Although the GKP codes were proposed early, experimen-
tal demonstrations of the GKP codes have been realized only
very recently. Encoding, logical readout, and full control of a
GKP qubit have been demonstrated in the motional mode of
a single trapped ion [85]. QECs of both square and hexag-
onal GKP codes have been demonstrated in a superconduct-
ing microwave cavity [36], where the GKP code states can be
deterministically generated from a vacuum state based on re-
peated stabilizer measurements and QEC protocol facilitated
with feedback technique [78]. Continuous QEC on the GKP
qubit has shown the extension of the coherence of the logical
qubit, demonstrating the capability of suppressing all logical
errors.
IV . UNIVERSAL QUANTUM CONTROL OF BOSONIC
CODES
In the realization of bosonic codes, including encoding,
decoding, universal gate set, and error detection and cor-
rection operations, universal quantum control of a bosonic
mode is crucial. Such a goal is important for not only QEC,
but also the understanding and controlling of quantum sys-
tems. Inspired by the cavity QED experiments [90, 91], the
universal quantum control could be achieved in a so-called
spin-oscillator model by introducing a two-level system to
couple to the bosonic mode. Circuit QED has been exten-
sively studied in the past decades and has become one of the
most promising platforms for quantum computing [3, 27–32].
Tremendous progress on the control of a bosonic mode has
been made in this architecture since its ﬁrst development in
Ref. [28] (Fig. 6a). Here, the results are summarized in two
parts for unitary quantum control of closed systems and quan-
tum channels for open systems, respectively.
The Hamiltonian of a typical circuit QED system consisting
of a transmon qubit and a cavity mode in the largely detuned
regime can be described by [3, 32, 68, 92, 93]
ˆH0/¯h = ωc ˆa† ˆa + ωq|e⟩⟨ e|− χ ˆa† ˆa|e⟩⟨ e|− K
2 ˆa†2 ˆa2. (26)
Here, ωc and ωq are the cavity and qubit frequencies, respec-
tively, ˆa† ( ˆa) is the creation (annihilation) operator for the
bosonic mode, |e⟩ (|g⟩) is the excited (ground) state of the
transmon qubit, and χ and K are the dispersive coupling and
Kerr coefﬁcient originating from the qubit, respectively. The
two-level qubit serving as an ancilla provides the necessary
non-linearity for the universal control of not only the bosonic
mode but also the whole combined system.
The strong dispersive coupling allows the resolving of
Fock states and thus the implementation of photon-number-
selective operations. Universal control of the bosonic mode
can be achieved by using selective number-dependent arbi-
trary phase gates (SNAP) [86] in combination with displace-
ment operations. The SNAP gate reads:
ˆS(⃗θ ) =
∞
∑
n=0
eiθn|n⟩⟨n|. (27)
Here ⃗θ ={θn}∞
n=0 is a list of phases and |n⟩ is the n-photon
Fock state. Each phase gate is generated geometrically as
shown in Fig. 6c. These geometric phase gates preserve pho-
ton numbers, while displacement operations induce the hop-
ping between adjacent Fock states. The combination of both
operations gives a universal control of the cavity. For exam-
ple, a unitary ˆUn that transfers the population between|n⟩ and
|n + 1⟩ is given by
ˆUn = ˆD(α1) ˆRn(π) ˆD(α2) ˆRn(π) ˆD(α3), (28)

## PDF page 11

11
(a) (b)
(c) (d)
T(t)C(t)
MHz MHz Probability 10 p
(n,t⎥g)
1
03
–3
5
–5
8
6n
4
2
0
0 100 200 300 400 500
(e) (f)
(g)
|0>
qudit
|0>|0>
𝑈∅ 𝑈𝑏 1 𝑈𝑏 2
(h)
t  (ns)
FIG. 6. Universal control of individual bosonic mode. (a) First demonstration of circuit QED architecture. Adapted from Ref. [28] (b)
First demonstration of a 3D circuit QED architecture. Adapted from Ref. [33]. (c) Principle of the SNAP gate. Adapted from Ref. [86]. (d)
Experimental results of a SNAP gate. Adapted from Ref. [60]. (e) Schematic representation of a control amplitude consisting of N steps in
the GRAPE method. Adapted from Ref. [87]. (f) Experimental results of the Fock state population evolution and the corresponding GRAPE
pulses. Adapted from Ref. [37]. (g) Quantum circuit for arbitrary channel construction with adaptive control. Adapted from Ref. [88]. (h)
Density matrix of maximally-mixed state ∑7
k=0|k⟩⟨k| generated based on the quantum circuit in (g). Adapted from Ref. [89].
where ˆRn(π) =− ∑n
n′=0|n′⟩⟨n′| + ∑∞
n′=n+1|n′⟩⟨n′| is the SNAP
gate, and α1, α2, α3 in the displacement operators can be op-
timized to maximize the ﬁdelity|⟨n + 1| ˆUn|n⟩|. A one-photon
Fock state |1⟩ has been experimentally generated with this
method [60] (Fig. 6d). A similar idea based on the photon-
number-selective detection for arbitrary state preparation has
also been proposed and demonstrated [94]: A cavity initially
prepared in a coherent state can be projected into an arbitrary
superposition of Fock states with high ﬁdelities but in a prob-
abilistic manner by post-selecting the measurement outcomes
of the ancilla.
The SNAP gate method requires to control the qubit and the
oscillator separately with a series of sequential SNAP gates
and displacement operations. To overcome the drawback of
the relatively long gate time, a more efﬁcient method is pro-
posed recently which involves a hierarchical insertion strat-
egy and gradient-descent technique for parameter optimiza-
tion and shows remarkable improvement [95].
Another efﬁcient approach for realizing universal control
is the optimal control technique, which explores the full
control parameter space to optimize the control pulses and
has been widely used in experiment. Figure 6e shows the
schematic of the gradient ascent pulse engineering (GRAPE)
method [87, 96] to optimize control pulses of a target unitary.

## PDF page 12

12
The evolution time is discretized into small steps and the ini-
tial controls could be completely random. The performance
function is based on the forward and backward propagations
of the initial and target density operators, respectively. At each
step, the gradients of the performance function with respect to
the controls are calculated and a gradient ascent procedure is
followed by updating the control parameters to improve the
performance function. Because of its universality and sim-
plicity, the GRAPE method has been extensively applied in
the encoding of QEC codes and the unitary gates on the logi-
cal qubits [18, 35, 37] (see Fig. 6f as an example).
The spin-oscillator model could be extended to multiple
modes by introducing dispersive couplings between the cen-
tral ancilla qubit and more modes, as well as the direct cross-
Kerr nonlinearities between modes due to the qubit. As an ex-
ample, the simplest two-cavity SNAP gate is demonstrated in
Ref. [38], where a single-photon Bell state between two cavi-
ties is deterministically generated by inducing a π-phase shift
on the|0⟩⊗|0⟩ state of the two cavities. Figure 5 summa-
rizes the recently demonstrated two-cavity gates for bosonic
codes with various approaches [19, 38, 66, 76]. Therefore,
the universal gate set on bosonic codes is available. How-
ever, although both SNAP and GRAPE approaches could be
generalized to gates between logical qubits based on arbitrary
bosonic codes, the signiﬁcant increase of the system Hilbert
space imposes great challenges in numerical optimization of
the control pulse sequences and also difﬁculties in experimen-
tal realization.
The above two approaches for universal control are re-
stricted to closed quantum systems. However, practical quan-
tum systems are open due to their inevitable coupling to the
environment, and their dynamics are described by completely
positive and trace preserving quantum channels [2]. So be-
sides the universal control of a closed quantum system, the
realization of arbitrary quantum channels helps to understand
practical quantum systems and complete our capability in
quantum controls. For instance, the QEC process is a quan-
tum channel that puriﬁes the quantum state of a system by re-
moving the entanglement between the system and the environ-
ment. A universal approach for quantum channel simulations
of a bosonic mode has been proposed [88, 97], holding the
hardware-efﬁciency advantage for bosonic codes and being
promising for a wide range of applications of bosonic modes,
such as system initialization, generalized quantum measure-
ments, open quantum system simulation, and quantum metrol-
ogy. Figure 6g illustrates the kernel idea of the approach: by
repetitively using and resetting the ancilla qubit and also using
the output of the ancilla measurement for feedforward control
of the bosonic mode, arbitrary quantum channels can be im-
plemented.
Preliminary experimental studies on arbitrary quantum
channel simulations of a photonic qubit in a superconducting
circuit, which is encoded in the ﬁrst two levels of an oscil-
lator, have been demonstrated [98]. In this experiment, the
arbitrary single-qubit channel simulations require a fast real-
time feedback control system for adaptive operations condi-
tional on the speciﬁc measurement results. A quantum chan-
nel for maximally-mixed state preparation is demonstrated in
Ref. [89], with the results shown in Fig. 6h. In a different ex-
periment, a speciﬁc quantum channel, i.e. QEC operation on
a binomial code, is implemented without the feedback elec-
tronic circuit. This autonomous QEC (AQEC) does not need
to extract error detection outcomes [17]. Instead, a unitary
transition ˆU is implemented to transfer the error entropy asso-
ciated with the logical state to the ancilla and in the meantime
the logical state in the error space |ψE⟩ is converted back to
the correct one|ψL⟩ in the code space as:
ˆU|ψE⟩|g⟩ =|ψL⟩|e⟩,
ˆU|ψL⟩|g⟩ =|ψL⟩|g⟩.
(29)
Therefore, the correlation between the logical state and the
environment (which induces errors) is erased. Since the real-
time feedback control system is not required, the potential
electronic latency is avoided. A separate experiment realizes
AQEC of single-photon-loss errors on a so-called truncated 4-
component cat code [18]. The unitary transition is realized
through two combs of continuous and selective microwave
drives with no which-path information leaking into the envi-
ronment, while the ancilla reset is through a dissipative pro-
cess. Achieving the full control of an open quantum system
is necessary for the bosonic codes, and more experimental ef-
forts are required in this direction for more advanced quantum
control. For example, besides the standard error correction in
an autonomous manner, fault tolerance to ancilla errors is also
possible by carefully designing the control (see Sec. V A for
more discussions).
Lastly, it is also worth noting that other than the spin-
oscillator model widely studied in the superconducting quan-
tum circuit, the Pockel and Kerr nonlinearities of harmonic
oscillators, which originate from the intrinsic bulky material
nonlinearity, also hold the potential for universal control of the
bosonic modes. As widely studied in the continuous variable
quantum information, these bulky nonlinearities with modest
interaction strength could simulate arbitrary Hamiltonian via
a Trotterization approach [99]. These nonlinearities are more
suitable for continuous variable encodings because there is no
requirement for the approximation of truncated Fock space.
The possibility of using the Pockel nonlinearity in universal
quantum computation is conﬁrmed in recent theoretical stud-
ies [100], which provides an alternative route to applications
of bosonic codes.
V . APPLICA TIONS OF BOSONIC CODES
As all ingredients of bosonic codes are available in super-
conducting quantum circuits, their direct applications in stor-
ing and transferring quantum information, i.e. in realizing
quantum computation and quantum communication, are fore-
seeable. From another perspective, a single bosonic mode
supports an inﬁnitely large Hilbert space, and thus provides

## PDF page 13

13
=
average 
t
fault-tolerant
non-fault-tolerant
AncillaAncilla CavityCavity
(a)
 over 
average 
t over 
(c)
(d)
364(3)
11(4)  µs3
 µs
272(5) µs
185(2) µs
No QEC
RKerr
RET
IET
Process fidelity, F
Time, T (µs)
1.0
0.9
0.8
0.7
0.6
0.5
0.4
0.3
5004003002001000
Probability correct
0
0.50
0.75
1.00
10 20
n
30 40
RB
IRB (SC)
IRB (SNC)
(e) 
Error Space Code Space
Error Transparent
Hilbert Space
ˆEˆE
Hilbert Space
ψ L (0)
(T )Lψ
(t )L
ˆU
(f)
Dephasing
Relaxation
XLYL
No error
Ancilla
event
Logical
operation
Ancilla
state
Start
Repeat
S(/uni03B8)
S(–/uni03B8)
S(/uni03B8)
S(/uni03B8)
/uni2223g/uni232A
/uni2223e/uni232A
/uni2223f /uni232AlL
lL
lL
lLlL
/uni03B8
/uni03B8
(b)
Not Error Transparent
FIG. 7. Fault tolerant operations of bosonic codes. (a) Schematic of a fault-tolerant quantum error detection, where an auxiliary energy
level| f⟩ of the ancilla is employed. (b) Experimental results of the fault-tolerant error detection show a suppression of the ancilla errors by
a factor of ﬁve. (a-b) are adapted from Ref. [15]. (c) The principle of path-independent phase gate. Path independence requires the ancilla
is manipulated in such a way that its populations are independent of the state of the encoded system. (d) Benchmarking results of the logical
gate demonstrate a signiﬁcant improvement due to the path-independent design. (c-d) are adapted from Ref. [16]. (e) Concept of the error-
transparent gate. The tracks of quantum evolution in both the code and the error spaces are deterministic and identical irrespective of the
time when the error occurs. (f) Experimental process ﬁdelity as a function of time with repetitive and interleaved error-transparent gates and
autonomous QEC on the logical qubit demonstrates an improved performance. (e-f) are adapted from Ref. [17].
a unique platform for exploring quantum advantages in quan-
tum simulation and metrology. However, in practical near-
term noisy intermediate-scale quantum (NISQ) [4] platforms,
we should not be restricted to the standard QEC codes that sat-
isfy the QEC condition (Eq. 1). In certain tasks, the bosonic
codes are beneﬁcial to reduce the effects of noise and system
imperfections on the estimation of certain outputs by QEC or
approximate QEC. Although great advantages are promised
by bosonic codes, only preliminary experimental and theoret-
ical results are reported. The potentials of bosonic codes are
awaiting systematic investigations with many techniques and
theoretical problems to be solved. Here, we just summarize
the recent exciting progress and proof-of-principle demonstra-
tions, and point out the opportunities in future studies.
A. Fault-tolerant quantum computation
QECs are developed to protect merely stored quantum in-
formation from the leading orders of errors. However, for a
general purpose of quantum information processing, the er-
rors occurring during the dynamical evolution might not be
correctable by directly applying QEC after the gate. There-
fore, a fault-tolerant universal quantum computer is also re-
quired to protect the dynamics of quantum information dur-
ing each step of computing, which should be carefully de-
signed to keep errors from propagating and accumulating such
that each encoded logical qubit can still be well protected by
QECs. In another words, state preparations, error detections,
gate operations, and measurements are all needed to be fault
tolerant. For qubit-based systems, surface code architecture
and code-concatenation approaches are proposed for achiev-
ing the ultimate fault tolerance and a clear threshold of the
error rate is provided for reliable and scalable quantum com-
putation [9, 101]. However, these schemes are extremely chal-
lenging for experimental realization because they require huge
physical sources that are not available currently. In contrast,
beneﬁting from the hardware-efﬁciency property, the encod-
ing, decoding, error corrections, and universal logical gate set
on encoded logical qubits have been achieved with the bosonic
codes. The experimental explorations of fault-tolerant op-
erations on the bosonic codes are already in progress, and
Fig. 7 summarizes some of the results. Note that the early
attempts towards the fault-tolerant quantum computation are
the demonstrations of the literal meaning of fault tolerance,
i.e. the capability of correcting certain physical errors occur-
ring during the gate operation, instead of achieving the fault-
tolerant threshold.
Because the ancilla plays a signiﬁcant role in realizing
the operations on bosonic codes, the damping and dephas-

## PDF page 14

14
ing errors of the ancilla might induce signiﬁcant errors on the
bosonic codes. For example, error detection on cat codes and
binomial codes is a non-Gaussian operation and thus requires
an ancilla (unlike that for GKP codes). Qubit damping error
ˆσ− in the error-detection circuit will propagate to the encoded
information by causing random phase-shifts which cannot be
corrected, as illustrated in Fig. 7a. Fault-tolerant error detec-
tion hence demands the prevention of the ancilla error from
propagating to and corrupting the encoded system. By intro-
ducing redundant energy levels of the ancilla, a fault-tolerant
error detection scheme against the ancilla damping error is
demonstrated [15]. This scheme is similar to use a QEC-
protected ancilla system, and the experiment demonstrates a
suppression of the ancilla errors by a factor of ﬁve.
An alternative way is to use an ancilla qubit with biased-
noise [57]. As the operator ˆσz commutes with the interaction
Hamiltonian ( χ ˆa† ˆa ˆσz/2), an ancilla with only ˆσz error will
not damage the encoded system, but only inﬂuence the de-
tection result. Cat qubits under continuous parametric drive
are one candidate of realizing such biased-noise qubits. The
phase-ﬂip ( ˆσz) rate is only linearly enhanced but the bit-ﬂip
( ˆσx) rate is exponentially suppressed with the size of the cat
qubit. Using such a stabilized cat qubit as the ancilla, without
intrinsic errors that do not commute with the interaction, the
simulation in Ref. [57] shows the measurement backaction on
the encoded system can indeed be suppressed.
To perform gate operations on the bosonic codes, the an-
cilla system is also necessary. To prevent error propagation
from the ancilla system to the encoded system, a theoretical
work analyzes the conditions on the interaction Hamiltonian
and deﬁnes the concept of “path independence” [59]. When
the ancilla system starts from|i⟩ and ends in|r⟩, the n-th or-
der path-independent gate requires that the encoded system
evolves under a deterministic unitary even when the ancilla
system suffers errors up to the n-th order. A subset of ﬁnal
ancilla states indicate the successful implementation of the
desired gate, while other states herald a failure of the oper-
ation, but the encoded system is not corrupted in this process.
The additional drives and the measurement to distinguish ad-
ditional levels of the ancilla, however, might introduce more
error sources. A path-independent phase gate with the SNAP
technique is demonstrated in the experiment [16], where the
ﬁdelity of the SNAP gate on a three-level ancilla qubit is sig-
niﬁcantly improved by the speciﬁc path-independent design,
as shown in Fig. 7b.
Besides the tolerance of ancilla errors during the desired
gate operations, the errors occurring in the encoded system
should also be considered and prevented from propagation.
To ensure photon loss error will not propagate under arbitrary
unitary evolutions, the concept of “error-transparent” gate is
introduced [103, 104]. The basic idea is the following. Ide-
ally, a quantum state should evolve unitarily in the code space
under the gate Hamiltonian with a ﬁnite gate time. If an error
happens during the gate, the evolution will jump to the er-
ror space, while the subsequent evolution in the error space
is identical to that in the code space up to a global phase.
So this error during the gate operation is tolerable by QEC
at the end of the evolution, and the gate can still be imple-
mented successfully. A recent experiment has demonstrated
error-transparent phase gates on the lowest-order binomial
code [17]. States in both the code and the error spaces are
preserved and the lifetime of the QEC-protected logical state
has better performance under error-transparent gate operation,
as shown in Fig. 7c. In Ref. [17], the authors also show that
the error-transparent gates could be generalized to a universal
gate set. Further extension of this approach could be com-
bined with the AQEC technique. To prevent the ancilla error
propagation in this process, one method is to design the AQEC
Hamiltonian as follows:
ˆH = ∑
i j
|Li⟩| j⟩⟨0|⟨Ei j| + h.c., (30)
where
⏐⏐Ei j
⟩
and|Li⟩ are the i-th logical basis state in the j-th
error space and the code space respectively, and|0⟩ and| j⟩ is
the ground state and the j-th excited state of the ancilla system
respectively. If this Hamiltonian and the ancilla system with a
large damping rate are available, the encoded system will be
protected by the AQEC process while the errors in the ancilla
system will not propagate to the encoded system.
Currently, the experimental efforts mostly concentrate on
the corrections of errors during gate operations, and the uni-
versal get set
{ ˆH, ˆS, ˆT ,cPhase
}
in an error-transparent man-
ner are feasible in experiment. However, the ultimate uni-
versal quantum computation requires the suppression of the
error rate to an arbitrarily small level when the elementary
gate operation ﬁdelities exceed a certain threshold, without
requiring a physical resource overhead scaled exponentially.
Although the fault-tolerant threshold is still lacking for the
bosonic codes, there are opportunities to further extend the
bosonic codes along two directions. One is to promote the
performance of the single-mode codes by increasing the mean
photon number of the codewords and thus utilizing the higher-
order encoding to tolerate more errors [53]. The other one
is to extend the system to multiple modes by repeating the
strategies used in their qubit counterpart and employing the
non-local information encoding for achieving the fault toler-
ance [58].
B. Quantum communications with bosonic codes
In a quantum network [105, 106], quantum information
needs to distribute among quantum nodes (or modules) via
either direct quantum state transfer or quantum teleportation
through shared quantum entanglement. As a result, efﬁcient
quantum state transfer between quantum nodes and on-site
long-lifetime quantum memories are essential for a quantum
network. On one hand, photons are the most practical choice
for high rate communications between distinct nodes. On the
other hand, quantum information encoded by bosonic codes
can be protected by QEC from local noise during storage,
channel noise associated with wavepackets propagating over

## PDF page 15

15
Quantum communication via quantum bus
Coupling stationary to propagating microwaves
Quantum state transfer and entanglement
Teleported CNOT
Cavity drive
ξ1(t) ξ2(t)
aˆ
bˆ
bˆout
κout
g(t)
aˆ
bˆ bˆ
out
κout
g(t)
Data 
qubits (D)
Module 1
Module 2
Communication 
channel or mode
Communication 
qubits (C)
D1
D2
Z
X
X
ZC1
C2
D1
C1
C2
D2
Sender Receiver
30 cm 30 cm
Output
/uni03BEs
2(t) /uni03BEs
1
/uni03BEr
2
(t)/uni03BEr
1
ks
out
kr
out
tˆsaˆs aˆrˆbs tˆrˆb r
(a) (b)
(c) (d)
FIG. 8. Quantum communication via a quantum network. Each node or module represents a small quantum processor consisting of data
qubits and communication qubits. (a) Controlled release of photonic states from one of the module. Adapted from Ref. [102]. (b) Teleported
CNOT circuit between two modules. Adapted from Ref. [19]. (c) Quantum communication between two modules via a quantum bus. Adapted
from Ref. [20]. (d) On-demand quantum state transfer and entanglement. Adapted from Ref. [64].
distances, and the insertion loss at quantum interfaces due to
impedance mismatching. Therefore, the bosonic codes are of
great potential for building quantum networks, and proof-of-
principle experiments of most basic quantum network compo-
nents have been reported.
As sketched in Fig. 8, each node can consist of a stor-
age cavity, a readout cavity, and a transmon qubit disper-
sively coupled to both cavities. The stored bosonic codes in
the storage cavity can be converted to a traveling wavepacket
through a coherent frequency conversion between the two cav-
ities based on two coherent drives and a four-wave mixing
effect [102], as shown in Fig. 8a. Connecting two nodes,
quantum state transfer via a cable coupled to two readout
cavities has been demonstrated with a pitch-and-catch proto-
col. Based on the binomial codes, the dominant error (single
photon loss) in the communication can be detected and cor-
rected, and on-demand entanglement between quantum nodes
has been demonstrated [64], as shown in Fig. 8d. In a different
setup (Fig. 8c), the entanglement between quantum memories
has been realized by a standing mode of a superconducting
coaxial bus resonator [20]. The bosonic mode encoding in
the even parity subspace enables the tracking of photon loss
events during the two-photon interference to promote the ﬁ-
delity of the generated entanglement.
Based on the above demonstrated components, quantum re-
peaters could be realized with superconducting bosonic codes.
Besides, quantum communication can also be realized without
direct interaction between nodes by quantum state teleporta-
tion, which only requires entanglement shared between nodes,
local operation, and classical communication. Equiped with
quantum repeaters and quantum state teleportation, quantum
information could then be delivered over arbitrarily long dis-
tances with high ﬁdelity through practically imperfect quan-
tum communication channels, as required for secure quantum
communication on planetary scale. In addition, distributed
quantum computation could be realized also based on quan-
tum entanglement shared between nodes. This module-based
approach could avoid spurious cross-talks between compo-
nents, as well as the frequency crowding in device engineer-
ing. In distributed quantum computation, teleportation-based
quantum gate operations between separated quantum nodes
are critical. Recently, deterministic teleportation of a CNOT

## PDF page 16

16
Linear molecule(a)
(b)
(c)
(d)
O
H H
Ideal spectra
Single-bit
Sampling
Wave number (cm–1)
Relative intensity
Nuclear configuration 𝑞𝑞
Potential energy
𝑑𝑑
ℏω𝑒𝑒𝑒𝑒
|𝑔𝑔⟩
|𝑒𝑒⟩
Excited state
Ground state
|1⟩
|0⟩
Harmonic  potential
ℏω0|2⟩
Fockstate
Transition
Experiment
FIG. 9. Quantum simulation based on bosonic modes. (a) Principle of a superconducting simulator for the vibronic structure of diatomic
molecules. (b) The absorption spectrum in the molecular system with different Huang-Rhys parameters D, where the initial state is a non-
equilibrium Fock state. (a-b) are adapted from Ref. [24]. (c) Circuit schematic of a two-mode superconducting bosonic processor for simulating
molecular vibronic spectra and extracting Franck-Condon factors for photoelectron processes. (d) Experimental Franck-Condon factors for
photoionization of water. (c-d) are adapted from Ref. [25].
gate between two nodes (both with bosonic encodings) is
demonstrated [19], as illustrated in Fig. 8b (also Fig. 5d).
The limitation of the superconducting bosonic system in
building a practical quantum network is mainly imposed by
the thermal noise at room temperature. In contrast, optical
photons could transmit information over thousands of kilo-
meters [107], while being restricted only by probabilistic
quantum gate operations. Therefore, the ideal microwave-
to-optical transducers [108, 109] are required for taking ad-
vantage of both microwave and optical bosonic codes. For
instance, a theoretical study predicts a high secure key rate
for memory-less one-way quantum communication over long
distances with cat codes [67]. In addition to communications,
quantum networks could also enhance the sensing or measure-
ment by distributing correlated quantum probes. For example,
higher precision could be achieved in a longer-baseline quan-
tum telescope [110].
C. Quantum simulations with bosonic codes
Although the ultimate universal quantum computation is
extremely challenging, the use of noisy quantum systems in
quantum simulation has attracted immediate research inter-
ests [111]. In the NISQ era [4], early quantum simulations
could ﬁnd direct applications in exploring quantum chemistry,
quantum optimization, material engineering, as well as funda-
mental studies of condensed matter physics and high-energy
physics, and could also stimulate further research interest in
the universal quantum computation. Compared with qubit ar-
rays, the bosonic modes are indispensable in many physical
models, including the boson sampling, molecular vibration,
quantum Rabi model, Bose-Hubbard model, and the simula-
tion of a non-Markovian environment. Besides, the bosonic
modes could also be applied directly in analog quantum sim-
ulations.
As an example, the bosonic modes are applied to solve
the vibrational structure problem. To make accurate calcu-
lations of the vibrational structure of large systems is still
very challenging for classical computers. Instead of manip-
ulating qubits in conventional quantum simulators in the ab-
sence of natural properties of elementary particles, bosonic
simulators are competent to establish direct correspondence
between photonic cavity modes and molecular vibrational
modes. Analog quantum algorithms are capable of simulat-
ing molecular vibrations. A proof-of-principle experiment has
demonstrated how superconducting devices can simulate the
vibronic spectra of molecules [24]. The device comprises of
a transmon qubit coupled to a 3D cavity, where the two low-
est energy levels of the qubit are manipulated as the electronic
ground and excited states of a molecule, while the bosonic
mode of the cavity models the nuclear vibrational motion of
the molecule. By offering the vibronic structure of diatomic
molecules, the simulator can obtain the molecular spectra for
both equilibrium and non-equilibrium states. Further exper-

## PDF page 17

17
imental efforts are paid on extending the system to multiple
bosonic modes. A superconducting bosonic processor that
integrates two superconducting microwave cavities and three
transmon qubits has been realized, where each cavity repre-
sents one vibrational mode of a triatomic molecule and the
qubit-mediated coupling represents the interaction between
the modes. Based on a high-ﬁdelity single-shot photon num-
ber detection scheme that is capable of resolving up to 15 pho-
tons, the photoelectron spectra of several triatomic molecules,
including H2O, O3, NO2, and SO2, are simulated [25], prov-
ing a bright future of the bosonic modes in analog quantum
simulations.
The digital quantum simulation of topological phases is
also carried out in the superconducting bosonic system [23],
in which the spin-orbit coupled particles running on a lattice is
efﬁciently simulated. This digital simulator performs a split-
step quantum walk algorithm and directly measures the asso-
ciated topological invariant by using the interference between
two components of a cavity Schr ¨odinger cat state. The di-
rect measurement of such a quantity in solid-state materials
remains a signiﬁcant challenge, owing to the non-local nature
of the topological ordering. This protocol sheds light on the
simulation and characterization of complex quantum materi-
als based on superconducting bosonic modes.
In these previous bosonic quantum simulators, the QEC
codes have not been directly put into use yet. However, we
should point out that the bosonic encoding has huge poten-
tials in digital quantum simulations. Because of hardware ef-
ﬁciency the bosonic modes are suitable for studies of high-
dimensional digital quantum simulations in the ﬁrst place, and
the demonstrated QEC techniques additionally allow a deeper
circuit depth. The circuit depth or the ﬁdelities could also
be further improved by combining the recently proposed error
mitigation method [113–115]. For a coarse estimation, assum-
ing the imperfect logical gate operations have an operation
error of 5% and the bosonic codes allow an error-detection ef-
ﬁciency of 99%, we could suppress the operation error to 1%.
For an expectation ﬁdelity of 80%, we could signiﬁcantly im-
prove the circuit depth from 5 to 20 with a success probability
of about 36%. Therefore, the error correction and mitigation
of the bosonic codes will promote quantum simulations in the
NISQ era.
D. Quantum metrology with bosonic codes
In conventional sensing and metrology applications, atom
and spin ensembles, mechanical oscillators, and microwave
and optical modes are the most used experimental systems
for detecting magnetic ﬁelds, acceleration, rotation, displace-
ment, and distance [116]. These systems could all be de-
scribed or approximated by bosonic modes, and thus the
bosonic codes are of special interest for quantum-enhanced
metrology. Besides, as mentioned in Sec. V B distributed
quantum metrology could be realized in a quantum net-
work [117]. However, these conventional metrology tech-
niques suffer the limited capability of nondeterministic quan-
tum state engineering, processing, or detection. Therefore, the
superconducting systems and their hybridization with spins or
mechanical resonators provide a unique platform for realizing
high-performance quantum metrology.
When estimating a parameter ω through the interaction
Hamiltonian of an oscillator as H(ω) = ωHI and by prepar-
ing the oscillator mode in a coherent state with a mean photon
number N, the precision of the parameter estimation is lim-
ited from two aspects: the classical shot-noise in detecting
photons ∝ 1/
√
N and the coherence time Tc-limited interac-
tion duration ∝ 1/Tc [118]. However, these limits are not as
fundamental as the Heisenberg uncertainty principle, which
imposes an ultimate limit in measurement precision ∝ 1/N,
called the Heisenberg limit (HL) [118–122]. By exploring the
large Hilbert space of a bosonic mode, both above limitations
could be resolved.
On one hand, the shot-noise could be suppressed by prepar-
ing the mode in a quantum state that gives a maximum vari-
ance for HI. The interferometers composed of two bosonic
modes have been implemented on various platforms by uti-
lizing squeezed states, number states, and Schr ¨odinger cat
states [90, 123]. Instead of fragile two-mode states, quantum
metrology schemes based on a single bosonic mode have also
been experimentally implemented in trapped ions and super-
conducting circuits [21, 124]. Especially, an enhanced sensi-
tivity approaching the HL scaling is demonstrated [21].
On the other hand, the Hilbert space intrinsically provides
redundancy to construct a QEC code subspace, which could
be mapped to orthogonal subspaces by errors and recovered
back through error correction. Therefore, the coherence time
of the probing quantum state could be extended by protecting
the code subspace from environment noise via QEC [112].
Combining QEC and universal operation on a binomial code,
a recent work demonstrates a Ramsey experiment on the QEC
protected logical qubit and shows a coherence time twice as
long as that without QEC [35]. Since Ramsey interferom-
etry has been widely used for precision measurements, this
result reveals the potential of bosonic codes in sensing. Al-
though the QEC-enhanced quantum metrology has attracted
considerable attention, it is still challenging for experiments.
One challenge comes from the so-called Hamiltonian-not-in-
Lindblad-span (HNLS) condition for the existence of an op-
timal code that can be constructed for achieving the HL scal-
ing [112]. Recently, by an approximate QEC technique, the
advantage of QEC for a bosonic radiometry has been demon-
strated in a superconducting circuit [125], though the HNLS
condition is not completely satisﬁed. This experiment indi-
cates that the bosonic QEC has considerable potential to be
explored in quantum metrology.
VI. DISCUSSIONS AND OUTLOOK
The bosonic codes in a superconducting quantum system
hold the advantages of hardware efﬁciency, large Hilbert

## PDF page 18

18
-3 -2 -1 0 1 2 3
Re(α)
-3 -2 -1 0 1 2 3
-3 -2 -1 0 1 2 3
3
2
1
0
-1
-2
-3
Im(α)
-3 -2 -1 0 1 2 3
Exp
 -0.6
-0.4
-0.2
0.0
0.2
0.4
0.6
W(α)
N=9
 N=12
N=6
3
2
1
0
-1
-2
-3 Theory
N=3(a)
(b) (c)
9.1 dB
N
0.1
0.0
-0.2
-0.4
-0.6
-0.8
-1.0
-1.2 log10δθ
1 2 3 4 5 6 7 8 9 10 12
1.00.80.60.40.20.0
log10N
/s32/s33/s34/s35/s36/s37/s34/s38/s39/s40/s36/s41/s38/s42/s38/s35
 
/s43/s40/s38/s39/s40/s44/s45/s40/s46/s47/s36/s41/s38/s42/s38/s35
N0 
equbit 
𝜃
HU
Ancillae + probe
Preparation
Measuremet
Control
Control
/afii9830dt /afii9830dt /afii9830dt
Sensing time t
Control
cavity 
FIG. 10. Quantum metrology based on bosonic modes. (a) Theoretical and experimental Wigner functions of the maximum variance states
(|0⟩ + i|N⟩)/
√
2 encoded in a microwave mode. (b) Results of optimal single-mode sensing scheme. Blue dots are experimental results and
green region represents the experimental results that surpass the standard limit by about 9.1 dB at N = 12. (a-b) are adapted from Ref. [21].
(c) The QEC-enhanced metrology scheme. One probe sequentially senses the parameter for time t with quantum controls applied every dt.
Adapted from Ref. [112].
space, and unique capability of long-distance transfer, there-
fore are one of the most promising candidates for future quan-
tum applications. Although great potentials of the bosonic
codes have been revealed by many preliminary experimental
results, there are many challenges to be addressed in the future
studies.
For short-term research, we would expect further exten-
sions of current bosonic systems and demonstrations of quan-
tum advantages brought by the bosonic codes. Even though
universal fault-tolerant quantum information processing is not
available yet, the bosonic QEC technique is beneﬁcial for the
protection of quantum information from temporal, propaga-
tion loss, and gate errors, allowing longer storage time, longer
propagation distance, and deeper quantum circuit depth. So,
we would expect immediate explorations of bosonic codes in
quantum repeater, quantum simulation, quantum metrology,
and quantum machine learning with the near-term NISQ su-
perconducting systems [4]. At this stage, these applications
could unarguably stimulate more research interests from both
experimental and theoretical perspectives, which would en-
courage new ideas about the optimization and applications of
the bosonic codes and might also even reveal new physics of
the bosonic codes.
In addition, we need to further extend the bosonic system
to multiple-oscillator regimes and other bosonic oscillators.
A resonator array has been demonstrated in 2D [126], and the
3D micromachined microwave cavities could also be scalable
by a multilayer integration approach [127]. As required for
long-distance quantum communication and quantum network,
high-efﬁciency and low-noise quantum transducers that con-
vert the microwave signals to optical frequencies are signiﬁ-
cant. Recently, there are exciting progresses along this direc-
tion: direct and coherent transducers based on superconduct-
ing cavity electro-optics [108] and high-frequency phonon-
mediated piezo-electro-optomechanical coupling [109] are
demonstrated, both of which avoid the MHz-frequency me-
chanical noise. On the other hand, the mechanical modes pro-
vide a more compact platform for high-density integration of

## PDF page 19

19
bosonic modes. Such a hybrid phononic architecture allows
the realization of multimode mechanical memory for quan-
tum random accessing memory [128], and is also useful in the
mechanical-oscillator-based force or inertial sensing [129].
Long-term goals of universal quantum computation de-
mand more efforts, and here we summarize the challenges
from three aspects:
(i) Material and fabrication . Superconducting hardware is
the backbone of quantum information technology. Improve-
ments of the superconducting materials and fabrication tech-
niques are always worthwhile. Better understanding of the
loss mechanisms [130–132], such as quasi-particles, radia-
tions, and piezo-mechanical losses would help superconduct-
ing qubit and cavity engineering. Combining sophisticated
integration architecture and packaging technique that avoid
frequency crowding and cross-talks with improved coherence
times, fabrication yield, stability, and robustness, the bosonic
codes could be scalable. To reduce the cost and suppress ther-
mal background noise, it holds great potential to utilize high-
frequency superconducting qubits and resonators at millime-
ter wavelengths for superconducting circuits that can work at
high temperatures [133].
(ii) Theory. For the ultimate goal of universal quantum
computation, there is still a lack of a clear estimation about
the fault-tolerance threshold for the bosonic codes. Other than
extending the single-mode codes to higher energies (higher
mean photon number) and higher-dimension encoding, the
extension of the bosonic codes to multiple modes is neces-
sary. One possible approach is to concatenate the bosonic
codes with the surface codes, i.e, the bosonic codes as the
building blocks of the surface codes [84]. Another feasible
approach is the realization of topological quantum codes in
a distributed quantum network architecture [134], by which
the challenges due to the massive integration of cavities in
a single module to avoid cross-talks and frequency crowding
problem could be relaxed. A hardware-adaptive code could
be numerically optimized according to the practical system
parameters, and the studies on the interconversions between
different bosonic and qubit-based codes are also needed. We
might expect new fault-tolerant bosonic quantum computation
architectures. Besides, efforts are needed for the applications
of bosonic codes in quantum metrology, quantum simulations,
and quantum networks.
(iii) Advanced quantum control techniques . The limited
quantum gate ﬁdelity is actually the main obstacle for demon-
strating high-order bosonic codes that are able to correct more
errors, because the control pulse sequences would be more
complicated due to the larger dimension of the Hilbert space.
The ﬁdelity losses mainly originate from three aspects, i.e.
the system incoherent processes, incomplete physical model
in the numerical optimization of the control parameters, and
parameter errors in the experimental setup. Although these
losses are determined by the hardware imperfections, ad-
vanced quantum control techniques would help. Robust quan-
tum control could minimize the ﬁdelity loss against the pa-
rameter ﬂuctuations, and a more complete physical model by
including open quantum system dynamics as well as higher-
order nonlinear interactions could be developed by a hybrid
quantum-classical approach. By introducing the recently de-
veloped machine learning control methods, device calibration
and quantum algorithms might be implemented with higher
efﬁciency. Additionally, as pointed out in Sec. IV, most cur-
rent studies focus on the spin-oscillator model in the strong
dispersive interaction regime, however, a combination of the
moderate Pockel or Kerr nonlinearities with the spin-oscillator
model might extend our capability of universal quantum con-
trol, especially when extending the bosonic codes to higher
mean photon numbers.
In summary, this article summarizes the recent development
of bosonic QEC codes in a superconducting quantum plat-
form. The bosonic modes are universal in nature, and thus
the demonstrations in the superconducting quantum circuits
could be directly extended to optical frequencies, mechanical
oscillators, and spin wave in spin ensembles. Especially, the
tools demonstrated in the spin-oscillator model could also be
equipped in the spin-phonon systems based on trapped-ions
and NV centers, as well as the optical cavity QED systems.
We believe that the bosonic codes will be fruitful in both short-
term and long-term future and will play an indispensable role
in quantum information technologies.
∗ These authors contributed equally to this work.
† clzou321@ustc.edu.cn
‡ luyansun@tsinghua.edu.cn
[1] J. Preskill, “Reliable quantum computers,” Proc. R. Soc. Lond.
A 454, 385 (1998).
[2] M. A. Nielsen and I. L. Chuang, Quantum Computation and
Quantum Information (Cambridge Univ. Press, 2000).
[3] M. H. Devoret and R. J. Schoelkopf, “Superconducting cir-
cuits for quantum information: an outlook.” Science339, 1169
(2013).
[4] J. Preskill, “Quantum Computing in the NISQ era and be-
yond,” Quantum 2, 79 (2018).
[5] A. Cho, “The biggest ﬂipping challenge in quantum comput-
ing,” Science (2020), 10.1126/science.abd7332.
[6] P. W. Shor, “Scheme for reducing decoherence in quantum
computer memory,” Phys. Rev. A52, 2493 (1995).
[7] A. Steane, “Multiple particle interference and quantum error
correction,” Proc. R. Soc. Lond. A 452, 2551 (1996).
[8] D. Gottsman, “An introduction to quantum error correc-
tion and fault-tolerant quantum computation,” Proc. Sympos.
Appl. Math. 68, 13 (2010).
[9] A. G. Fowler, M. Mariantoni, J. M. Martinis, and A. N. Cle-
land, “Surface codes: Towards practical large-scale quantum
computation,” Phys. Rev. A86, 032324 (2012).
[10] S. J. Devitt, W. J. Munro, and K. Nemoto, “Quantum error
correction for beginners.” Rep. Prog. Phys. Physical Society
(Great Britain) 76, 076001 (2013).
[11] J. Roffe, “Quantum error correction: an introductory guide,”
Contemp. Phys. 60, 226 (2019).
[12] N. Ofek, A. Petrenko, R. Heeres, P. Reinhold, Z. Leghtas,
B. Vlastakis, Y . Liu, L. Frunzio, S. M. Girvin, L. Jiang,
M. Mirrahimi, M. H. Devoret, and R. J. Schoelkopf, “Ex-

## PDF page 20

20
tending the lifetime of a quantum bit with error correction in
superconducting circuits,” Nature 536, 441 (2016).
[13] C. Gidney and M. Eker˚a, “How to factor 2048 bit RSA integers
in 8 hours using 20 million noisy qubits,” arXiv:1905.09749
(2019).
[14] A. D. Corcoles, A. Kandala, A. Javadi-Abhari, D. T. Mc-
Clure, A. W. Cross, K. Temme, P. D. Nation, M. Steffen, and
J. M. Gambetta, “Challenges and Opportunities of Near-Term
Quantum Computing Systems,” Proc. IEEE108, 1338 (2020).
[15] S. Rosenblum, P. Reinhold, M. Mirrahimi, L. Jiang, L. Frun-
zio, and R. J. Schoelkopf, “Fault-tolerant detection of a quan-
tum error,” Science361, 266 (2018).
[16] P. Reinhold, S. Rosenblum, W.-L. Ma, L. Frunzio, L. Jiang,
and R. J. Schoelkopf, “Error-corrected gates on an encoded
qubit,” Nat. Phys. 16, 822 (2020).
[17] Y . Ma, Y . Xu, X. Mu, W. Cai, L. Hu, W. Wang, X. Pan,
H. Wang, Y . P. Song, C.-L. Zou, and et al., “Error-transparent
operations on a logical qubit protected by quantum error cor-
rection,” Nat. Phys. 16, 827 (2020).
[18] J. M. Gertler, B. Baker, J. Li, S. Shirol, J. Koch, and C. Wang,
“Protecting a bosonic qubit with autonomous quantum error
correction,” arXiv:2004.09322 (2020).
[19] K. S. Chou, J. Z. Blumoff, C. S. Wang, P. C. Reinhold, C. J.
Axline, Y . Y . Gao, L. Frunzio, M. H. Devoret, L. Jiang, and
R. J. Schoelkopf, “Deterministic teleportation of a quantum
gate between two logical qubits,” Nature 561, 368 (2018).
[20] L. D. Burkhart, J. Teoh, Y . Zhang, C. J. Axline, L. Frunzio,
M. H. Devoret, L. Jiang, S. M. Girvin, and R. J. Schoelkopf,
“Error-detected state transfer and entanglement in a supercon-
ducting quantum network,” arXiv:2004.06168 (2020).
[21] W. Wang, Y . Wu, Y . Ma, W. Cai, L. Hu, X. Mu, Y . Xu, Z.-
J. Chen, H. Wang, Y . P. Song, H. Yuan, C.-L. Zou, L.-M.
Duan, and L. Sun, “Heisenberg-limited single-mode quan-
tum metrology in a superconducting circuit,” Nat. Commun.
10, 4382 (2019).
[22] B. M. Escher, R. L. de Matos Filho, and L. Davidovich,
“General framework for estimating the ultimate precision limit
in noisy quantum-enhanced metrology,” Nat. Phys. 7, 406
(2011).
[23] E. Flurin, V . V . Ramasesh, S. Hacohen-Gourgy, L. S. Martin,
N. Y . Yao, and I. Siddiqi, “Observing topological invariants
using quantum walks in superconducting circuits,” Phys. Rev.
X 7, 031023 (2017).
[24] L. Hu, Y .-C. Ma, Y . Xu, W.-T. Wang, Y .-W. Ma, K. Liu, H.-Y .
Wang, Y .-P. Song, M.-H. Yung, and L.-Y . Sun, “Simulation of
molecular spectroscopy with circuit quantum electrodynam-
ics,” Sci. Bull. 63, 293 (2018).
[25] C. S. Wang, J. C. Curtis, B. J. Lester, Y . Zhang, Y . Y . Gao,
J. Freeze, V . S. Batista, P. H. Vaccaro, I. L. Chuang, L. Frun-
zio, L. Jiang, S. M. Girvin, and R. J. Schoelkopf, “Efﬁcient
multiphoton sampling of molecular vibronic spectra on a su-
perconducting bosonic processor,” Phys. Rev. X 10, 021060
(2020).
[26] N. Rivera and I. Kaminer, “Light-matter interactions with pho-
tonic quasiparticles,” Nat. Rev. Phys.2, 538 (2020).
[27] A. Blais, R.-S. Huang, A. Wallraff, S. M. Girvin, and R. J.
Schoelkopf, “Cavity quantum electrodynamics for supercon-
ducting electrical circuits: An architecture for quantum com-
putation,” Phys. Rev. A69, 062320 (2004).
[28] A. Wallraff, D. I. Schuster, A. Blais, L. Frunzio, R.-S. Huang,
J. Majer, S. Kumar, S. M. Girvin, and R. J. Schoelkopf,
“Strong coupling of a single photon to a superconducting
qubit using circuit quantum electrodynamics,” Nature 431,
162 (2004).
[29] J. Q. You and F. Nori, “Atomic physics and quantum optics
using superconducting circuits,” Nature 474, 589 (2011).
[30] X. Gu, A. F. Kockum, A. Miranowicz, Y . X. Liu, and
F. Nori, “Microwave photonics with superconducting quantum
circuits,” Phys. Rep. 718-719, 1 (2017).
[31] A. Blais, S. M. Girvin, and W. D. Oliver, “Quantum infor-
mation processing and quantum optics with circuit quantum
electrodynamics,” Nat. Phys. 16, 247 (2020).
[32] A. Blais, A. L. Grimsmo, S. M. Girvin, and A. Wallraff, “Cir-
cuit quantum electrodynamics,” arXiv:2005.12667 (2020).
[33] H. Paik, D. I. Schuster, L. S. Bishop, G. Kirchmair, G. Cate-
lani, a. P. Sears, B. R. Johnson, M. J. Reagor, L. Frunzio, L. I.
Glazman, S. M. Girvin, M. H. Devoret, and R. J. Schoelkopf,
“Observation of High Coherence in Josephson Junction Qubits
Measured in a Three-Dimensional Circuit QED Architecture,”
Phys. Rev. Lett. 107, 240501 (2011).
[34] M. Reagor, H. Paik, G. Catelani, L. Sun, C. Axline, E. Hol-
land, I. M. Pop, N. A. Masluk, T. Brecht, L. Frunzio, M. H.
Devoret, L. I. Glazman, and R. J. Schoelkopf, “Ten millisec-
onds for aluminum cavities in the quantum regime,” Appl.
Phys. Lett. 102, 192604 (2013).
[35] L. Hu, Y . Ma, W. Cai, X. Mu, Y . Xu, W. Wang, Y . Wu,
H. Wang, Y . Song, C. Zou, S. M. Girvin, L.-M. Duan, and
L. Sun, “Quantum error correction and universal gate set on a
binomial bosonic logical qubit,” Nat. Phys. 15, 503 (2019).
[36] P. Campagne-Ibarcq, A. Eickbusch, S. Touzard, E. Zalys-
Geller, N. E. Frattini, V . V . Sivak, P. Reinhold, S. Puri,
S. Shankar, R. J. Schoelkopf, L. Frunzio, M. Mirrahimi, and
M. H. Devoret, “Quantum error correction of a qubit encoded
in grid states of an oscillator,” Nature584, 368 (2020).
[37] R. W. Heeres, P. Reinhold, N. Ofek, L. Frunzio, L. Jiang,
M. H. Devoret, and R. J. Schoelkopf, “Implementing a uni-
versal gate set on a logical qubit encoded in an oscillator,” Nat.
Commun. 8, 94 (2017).
[38] Y . Xu, Y . Ma, W. Cai, X. Mu, W. Dai, W. Wang, L. Hu,
X. Li, J. Han, H. Wang, Y . P. Song, Z.-B. Yang, S.-B. Zheng,
and L. Sun, “Demonstration of controlled-phase gates between
two error-correctable photonic qubits,” Phys. Rev. Lett. 124,
120501 (2020).
[39] B. M. Terhal, “Quantum error correction for quantum memo-
ries,” Rev. Mod. Phys.87, 307 (2015).
[40] E. T. Campbell, B. M. Terhal, and C. Vuillot, “Roads to-
wards fault-tolerant universal quantum computation,” Nature
549, 172 (2017).
[41] B. M. Terhal, J. Conrad, and C. Vuillot, “Towards scalable
bosonic quantum error correction,” Quantum Sci. Technol. 5,
043001 (2020).
[42] A. Joshi, K. Noh, and Y . Y . Gao, “Quantum infor-
mation processing with bosonic qubits in circuit QED,”
arXiv:2008.13471 (2020).
[43] P. Schindler, J. T. Barreiro, T. Monz, V . Nebendahl, D. Nigg,
M. Chwalla, M. Hennrich, and R. Blatt, “Experimental Repet-
itive Quantum Error Correction,” Science332, 1059 (2011).
[44] D. Nigg, M. M ¨uller, E. A. Martinez, P. Schindler, M. Hen-
nrich, T. Monz, M. A. Martin-Delgado, and R. Blatt., “Quan-
tum computations on a topologically encoded qubit,” Science
345, 302 (2014).
[45] T. H. Taminiau, J. Cramer, T. van der Sar, V . V . Dobrovit-
ski, and R. Hanson, “Universal control and error correction in
multi-qubit spin registers in diamond,” Nat. Nanotechnol. 9,
171 (2014).
[46] J. Cramer, N. Kalb, M. A. Rol, B. Hensen, M. S. Blok,
M. Markham, D. J. Twitchen, R. Hanson, and T. H. Taminiau,
“Repeated quantum error correction on a continuously en-

## PDF page 21

21
coded qubit by real-time feedback,” Nat. Commun. 7, 11526
(2016).
[47] M. D. Reed, L. DiCarlo, S. E. Nigg, L. Sun, L. Frunzio,
S. M. Girvin, and R. J. Schoelkopf, “Realization of three-
qubit quantum error correction with superconducting circuits,”
Nature 482, 382 (2012).
[48] J. Kelly, R. Barends, A. G. Fowler, A. Megrant, E. Jeffrey,
T. C. White, D. Sank, J. Y . Mutus, B. Campbell, Y . Chen,
Z. Chen, B. Chiaro, A. Dunsworth, I.-C. Hoi, C. Neill, P. J. J.
O’Malley, C. Quintana, P. Roushan, A. Vainsencher, J. Wen-
ner, A. N. Cleland, and J. M. Martinis, “State preservation by
repetitive error detection in a superconducting quantum cir-
cuit,” Nature 519, 66 (2015).
[49] I. L. Chuang, D. W. Leung, and Y . Yamamoto, “Bosonic quan-
tum codes for amplitude damping,” Phys. Rev. A 56, 1114
(1997).
[50] D. Gottesman, A. Kitaev, and J. Preskill, “Encoding a qubit
in an oscillator,” Phys. Rev. A64, 012310 (2001).
[51] Z. Leghtas, G. Kirchmair, B. Vlastakis, R. J. Schoelkopf,
M. H. Devoret, and M. Mirrahimi, “Hardware-efﬁcient au-
tonomous quantum memory protection,” Phys. Rev. Lett.111,
120501 (2013).
[52] M. Mirrahimi, Z. Leghtas, V . V . Albert, S. Touzard, R. J.
Schoelkopf, L. Jiang, and M. H. Devoret, “Dynamically pro-
tected cat-qubits: a new paradigm for universal quantum com-
putation,” New J. Phys.16, 045014 (2014).
[53] M. H. Michael, M. Silveri, R. T. Brierley, V . V . Albert,
J. Salmilehto, L. Jiang, and S. M. Girvin, “New Class of
Quantum Error-Correcting Codes for a Bosonic Mode,” Phys.
Rev. X 6, 031006 (2016).
[54] J. Cohen, W. C. Smith, M. H. Devoret, and M. Mir-
rahimi, “Degeneracy-preserving quantum nondemolition mea-
surement of parity-type observables for cat qubits,” Phys. Rev.
Lett. 119, 060503 (2017).
[55] S. Puri, S. Boutin, and A. Blais, “Engineering the quantum
states of light in a kerr-nonlinear resonator by two-photon
driving,” npj Quantum Inf.3, 18 (2017).
[56] V . V . Albert, K. Noh, K. Duivenvoorden, D. J. Young, R. T.
Brierley, P. Reinhold, C. Vuillot, L. Li, C. Shen, S. M. Girvin,
B. M. Terhal, and L. Jiang, “Performance and structure of
single-mode bosonic codes,” Phys. Rev. A97, 032346 (2018).
[57] S. Puri, A. Grimm, P. Campagne-Ibarcq, A. Eickbusch,
K. Noh, G. Roberts, L. Jiang, M. Mirrahimi, M. H. Devoret,
and S. M. Girvin, “Stabilized cat in a driven nonlinear cav-
ity: A fault-tolerant error syndrome detector,” Phys. Rev. X9,
041009 (2019).
[58] J. Guillaud and M. Mirrahimi, “Repetition cat qubits for
fault-tolerant quantum computation,” Phys. Rev. X 9, 041053
(2019).
[59] W.-L. Ma, M. Zhang, Y . Wong, K. Noh, S. Rosen-
blum, P. Reinhold, R. J. Schoelkopf, and L. Jiang,
“Path-independent quantum gates with noisy ancilla,”
arXiv:1911.12240 (2019).
[60] R. W. Heeres, B. Vlastakis, E. Holland, S. Krastanov, V . V .
Albert, L. Frunzio, L. Jiang, and R. J. Schoelkopf, “Cav-
ity state manipulation using photon-number selective phase
gates,” Phys. Rev. Lett.115, 137002 (2015).
[61] Z. Leghtas, S. Touzard, I. M. Pop, A. Kou, B. Vlastakis, A. Pe-
trenko, K. M. Sliwa, A. Narla, S. Shankar, M. J. Hatridge, and
et al., “Conﬁning the state of light to a quantum manifold by
engineered two-photon loss,” Science 347, 853 (2015).
[62] S. Touzard, A. Grimm, Z. Leghtas, S. O. Mundhada, P. Rein-
hold, C. Axline, M. Reagor, K. Chou, J. Blumoff, K. M. Sliwa,
S. Shankar, L. Frunzio, R. J. Schoelkopf, M. Mirrahimi, and
M. H. Devoret, “Coherent oscillations inside a quantum mani-
fold stabilized by dissipation,” Phys. Rev. X8, 021005 (2018).
[63] A. Grimm, N. E. Frattini, S. Puri, S. O. Mundhada, S. Touzard,
M. Mirrahimi, S. M. Girvin, S. Shankar, and M. H. Devoret,
“Stabilization and operation of a kerr-cat qubit,” Nature 584,
205 (2020).
[64] C. Axline, L. Burkhart, W. Pfaff, M. Zhang, K. Chou,
P. Campagne-Ibarcq, P. Reinhold, L. Frunzio, S. M. Girvin,
L. Jiang, M. H. Devoret, and R. J. Schoelkopf, “On-demand
quantum state transfer and entanglement between remote mi-
crowave cavity memories,” Nat. Phys.14, 705 (2018).
[65] Y . Y . Gao, B. J. Lester, Y . Zhang, C. Wang, S. Rosenblum,
L. Frunzio, L. Jiang, S. M. Girvin, and R. J. Schoelkopf,
“Programmable interference between two microwave quan-
tum memories,” Phys. Rev. X8, 021073 (2018).
[66] Y . Y . Gao, B. J. Lester, K. S. Chou, L. Frunzio, M. H. De-
voret, L. Jiang, S. M. Girvin, and R. J. Schoelkopf, “Entan-
glement of bosonic modes through an engineered exchange
interaction,” Nature 566, 509 (2019).
[67] L. Li, C.-L. Zou, V . V . Albert, S. Muralidharan, S. M. Girvin,
and L. Jiang, “Cat Codes with Optimal Decoherence Sup-
pression for a Lossy Bosonic Channel,” Phys. Rev. Lett. 119,
030502 (2017).
[68] L. Sun, A. Petrenko, Z. Leghtas, B. Vlastakis, G. Kirchmair,
K. M. Sliwa, A. Narla, M. Hatridge, S. Shankar, J. Blu-
moff, L. Frunzio, M. Mirrahimi, M. H. Devoret, and R. J.
Schoelkopf, “Tracking photon jumps with repeated quan-
tum non-demolition parity measurements,” Nature 511, 444
(2014).
[69] S. Mundhada, A. Grimm, J. Venkatraman, Z. Minev,
S. Touzard, N. Frattini, V . Sivak, K. Sliwa, P. Reinhold,
S. Shankar, M. Mirrahimi, and M. Devoret, “Experimental
implementation of a raman-assisted eight-wave mixing pro-
cess,” Phys. Rev. Appl.12, 054051 (2019).
[70] V . V . Albert, S. O. Mundhada, A. Grimm, S. Touzard, M. H.
Devoret, and L. Jiang, “Pair-cat codes: autonomous error-
correction with low-order nonlinearity,” Quantum Sci. Tech-
nol. 4, 035007 (2019).
[71] R. Lescanne, M. Villiers, T. Peronnin, A. Sarlette, M. Del-
becq, B. Huard, T. Kontos, M. Mirrahimi, and Z. Leghtas,
“Exponential suppression of bit-ﬂips in a qubit encoded in an
oscillator,” Nat. Phy.16, 595 (2020).
[72] S. Puri, L. St-Jean, J. A. Gross, A. Grimm, N. E. Frattini, P. S.
Iyer, A. Krishna, S. Touzard, L. Jiang, A. Blais, S. T. Flammia,
and S. M. Girvin, “Bias-preserving gates with stabilized cat
qubits,” Sci. Adv.6, eaay5901 (2020).
[73] D. K. Tuckett, S. D. Bartlett, and S. T. Flammia, “Ultrahigh
error threshold for surface codes with biased noise,” Phys.
Rev. Lett. 120, 050505 (2018).
[74] D. K. Tuckett, A. S. Darmawan, C. T. Chubb, S. Bravyi,
S. D. Bartlett, and S. T. Flammia, “Tailoring surface codes
for highly biased noise,” Phys. Rev. X9, 041031 (2019).
[75] D. K. Tuckett, S. D. Bartlett, S. T. Flammia, and B. J. Brown,
“Fault-tolerant thresholds for the surface code in excess of 5%
under biased noise,” Phys. Rev. Lett.124, 130501 (2020).
[76] S. Rosenblum, Y . Y . Gao, P. Reinhold, C. Wang, C. J. Ax-
line, L. Frunzio, S. M. Girvin, L. Jiang, M. Mirrahimi, M. H.
Devoret, and R. J. Schoelkopf, “A CNOT gate between multi-
photon qubits encoded in two cavities,” Nat. Commun. 9, 652
(2018).
[77] D. W. Leung, M. A. Nielsen, I. L. Chuang, and Y . Ya-
mamoto, “Approximate quantum error correction can lead to
better codes,” Phys. Rev. A56, 2567 (1997).
[78] B. M. Terhal and D. Weigand, “Encoding a qubit into a cavity

## PDF page 22

22
mode in circuit QED using phase estimation,” Phys. Rev. A
93, 012315 (2016).
[79] K. Noh, V . V . Albert, and L. Jiang, “Quantum capacity bounds
of gaussian thermal loss channels and achievable rates with
Gottesman-Kitaev-Preskill codes,” IEEE Trans. Inf. Theory
65, 2563 (2019).
[80] L. Li, D. J. Young, V . V . Albert, K. Noh, C.-L. Zou, and
L. Jiang, “Designing good bosonic quantum codes via creating
destructive interference,” arXiv:1901.05358 (2019).
[81] H. Yamasaki, K. Fukui, Y . Takeuchi, S. Tani, and M. Koashi,
“Polylog-overhead highly fault-tolerant measurement-based
quantum computation: all-gaussian implementation with
Gottesman-Kitaev-Preskill code,” arXiv:2006.05416 (2020).
[82] K. Fukui, A. Tomita, A. Okamoto, and K. Fujii, “High-
threshold fault-tolerant quantum computation with analog
quantum error correction,” Phys. Rev. X8, 021054 (2018).
[83] Y . Wang, “Quantum error correction with the GKP code
and concatenation with stabilizer codes,” arXiv:1908.00147
(2019).
[84] K. Noh and C. Chamberland, “Fault-tolerant bosonic quantum
error correction with the surface–Gottesman-Kitaev-Preskill
code,” Phys. Rev. A101, 012316 (2020).
[85] C. Fl ¨uhmann, T. L. Nguyen, M. Marinelli, V . Negnevitsky,
K. Mehta, and J. P. Home, “Encoding a qubit in a trapped-ion
mechanical oscillator,” Nature566, 513 (2019).
[86] S. Krastanov, V . V . Albert, C. Shen, C.-L. Zou, R. W. Heeres,
B. Vlastakis, R. J. Schoelkopf, and L. Jiang, “Universal con-
trol of an oscillator with dispersive coupling to a qubit,” Phys.
Rev. A 92, 040303 (2015).
[87] N. Khaneja, T. Reiss, C. Kehlet, T. Schulte-Herbr ¨uggen, and
S. J. Glaser, “Optimal control of coupled spin dynamics: de-
sign of nmr pulse sequences by gradient ascent algorithms,” J.
Magn. Reson. 172, 296 (2005).
[88] C. Shen, K. Noh, V . V . Albert, S. Krastanov, M. H. Devoret,
R. J. Schoelkopf, S. M. Girvin, and L. Jiang, “Quantum chan-
nel construction with circuit quantum electrodynamics,” Phys.
Rev. B 95, 134501 (2017).
[89] W. Wang, J. Han, B. Yadin, Y . Ma, J. Ma, W. Cai, Y . Xu, L. Hu,
H. Wang, Y . P. Song, M. Gu, and L. Sun, “Witnessing quan-
tum resource conversion within deterministic quantum com-
putation using one pure superconducting qubit,” Phys. Rev.
Lett. 123, 220501 (2019).
[90] S. Haroche and J. M. Raimond, Exploring the Quantum:
Atoms, Cavities, and Photons (Oxford Univ. Press, 2006).
[91] S. Haroche, M. Brune, and J. M. Raimond, “From cavity to
circuit quantum electrodynamics,” Nat. Phys. 16, 243 (2020).
[92] G. Kirchmair, B. Vlastakis, Z. Leghtas, S. E. Nigg, H. Paik,
E. Ginossar, M. Mirrahimi, L. Frunzio, S. M. Girvin, and
R. J. Schoelkopf, “Observation of quantum state collapse and
revival due to the single-photon Kerr effect,” Nature 495, 205
(2013).
[93] B. Vlastakis, G. Kirchmair, Z. Leghtas, S. E. Nigg, L. Frun-
zio, S. M. Girvin, M. Mirrahimi, M. H. Devoret, and R. J.
Schoelkopf, “Deterministically encoding quantum informa-
tion using 100-photon Schr ¨odinger cat states.” Science 342,
607 (2013).
[94] W. Wang, L. Hu, Y . Xu, K. Liu, Y . Ma, S.-B. Zheng, R. Vijay,
Y . P. Song, L.-M. Duan, and L. Sun, “Converting quasiclas-
sical states into arbitrary fock state superpositions in a super-
conducting circuit,” Phys. Rev. Lett.118, 223604 (2017).
[95] T. F ¨osel, S. Krastanov, F. Marquardt, and L. Jiang, “Efﬁcient
cavity control with snap gates,” arXiv:2004.14256 (2020).
[96] P. De Fouquieres, S. Schirmer, S. Glaser, and I. Kuprov, “Sec-
ond order gradient ascent pulse engineering,” J. Magn. Reson.
212, 412 (2011).
[97] S. Lloyd and L. Viola, “Engineering quantum dynamics,”
Phys. Rev. A 65, 010101 (2001).
[98] L. Hu, X. Mu, W. Cai, Y . Ma, Y . Xu, H. Wang, Y . Song, C.-L.
Zou, and L. Sun, “Experimental repetitive quantum channel
simulation,” Sci. Bull. 63, 29 (2018).
[99] C. Weedbrook, S. Pirandola, R. Garc´ıa-Patr´on, N. J. Cerf, T. C.
Ralph, J. H. Shapiro, and S. Lloyd, “Gaussian quantum infor-
mation,” Rev. Mod. Phys.84, 621 (2012).
[100] M. Y . Niu, I. L. Chuang, and J. H. Shapiro, “Qudit-basis uni-
versal quantum computation using χ (2) interactions,” Phys.
Rev. Lett. 120, 160502 (2018).
[101] T. Jochym-O’Connor and R. Laﬂamme, “Using Concatenated
Quantum Codes for Universal Fault-Tolerant Quantum Gates,”
Phys. Rev. Lett. 112, 010505 (2014).
[102] W. Pfaff, C. J. Axline, L. D. Burkhart, U. V ool, P. Reinhold,
L. Frunzio, L. Jiang, M. H. Devoret, and R. J. Schoelkopf,
“Controlled release of multiphoton quantum states from a mi-
crowave cavity memory,” Nat. Phys.13, 882 (2017).
[103] O. Vy, X. Wang, and K. Jacobs, “Error-transparent evolution:
the ability of multi-body interactions to bypass decoherence,”
New J. Phys. 15, 053002 (2013).
[104] E. Kapit, “Error-transparent quantum gates for small logical
qubit architectures,” Phys. Rev. Lett.120, 050503 (2018).
[105] H. J. Kimble, “The quantum internet,” Nature 453, 1023
(2008).
[106] A. Reiserer and G. Rempe, “Cavity-based quantum networks
with single atoms and optical photons,” Rev. Mod. Phys. 87,
1379 (2015).
[107] J.-G. Ren, P. Xu, H.-L. Yong, L. Zhang, S.-K. Liao, J. Yin, W.-
Y . Liu, W.-Q. Cai, M. Yang, L. Li,et al., “Ground-to-satellite
quantum teleportation,” Nature 549, 70 (2017).
[108] L. Fan, C.-L. Zou, R. Cheng, X. Guo, X. Han, Z. Gong,
S. Wang, and H. X. Tang, “Superconducting cavity electro-
optics: A platform for coherent photon conversion between
superconducting and photonic circuits,” Sci. Adv.4, eaar4994
(2018).
[109] X. Han, W. Fu, C. Zhong, C.-l. Zou, Y . Xu, A. A. Sayem,
M. Xu, S. Wang, R. Cheng, L. Jiang, and H. X. Tang, “Cavity
piezo-mechanics for superconducting-nanophotonic quantum
interface,” Nat. Commun. 11, 3237 (2020).
[110] D. Gottesman, T. Jennewein, and S. Croke, “Longer-baseline
telescopes using quantum repeaters,” Phys. Rev. Lett. 109,
070503 (2012).
[111] A. A. Houck, H. E. T ¨ureci, and J. Koch, “On-chip quantum
simulation with superconducting circuits,” Nat. Phys. 8, 292
(2012).
[112] S. Zhou, M. Zhang, J. Preskill, and L. Jiang, “Achieving the
Heisenberg limit in quantum metrology using quantum error
correction,” Nat. Commun. 9, 78 (2018).
[113] K. Temme, S. Bravyi, and J. M. Gambetta, “Error mitiga-
tion for short-depth quantum circuits,” Phys. Rev. Lett. 119,
180509 (2017).
[114] Y . Li and S. C. Benjamin, “Efﬁcient variational quantum sim-
ulator incorporating active error minimization,” Phys. Rev. X
7, 021050 (2017).
[115] S. McArdle, S. Endo, A. Aspuru-Guzik, S. C. Benjamin,
and X. Yuan, “Quantum computational chemistry,” Rev. Mod.
Phys. 92, 015003 (2020).
[116] C. L. Degen, F. Reinhard, and P. Cappellaro, “Quantum sens-
ing,” Rev. Mod. Phys.89, 035002 (2017).
[117] X. Guo, C. R. Breum, J. Borregaard, S. Izumi, M. V . Larsen,
T. Gehring, M. Christandl, J. S. Neergaard-Nielsen, and U. L.
Andersen, “Distributed quantum sensing in a continuous-

## PDF page 23

23
variable entangled network,” Nat. Phys.16, 281 (2020).
[118] V . Giovannetti, S. Lloyd, and L. Maccone, “Advances in quan-
tum metrology,” Nat. Photonics5, 222 (2011).
[119] C. W. Helstrom, Quantum detection and estimation theory
(Academic Press, 1976) pp. 231–252.
[120] A. S. Holevo, Probabilistic and Statistical Aspect of Quantum
Theory (North-Holland Publishing. Company, 1982).
[121] V . Giovannetti, “Quantum-Enhanced Measurements: Beating
the Standard Quantum Limit,” Science 306, 1330 (2004).
[122] V . Giovannetti, S. Lloyd, and L. Maccone, “Quantum metrol-
ogy,” Phys. Rev. Lett.96, 010401 (2006).
[123] E. Polino, M. Valeri, N. Spagnolo, and F. Sciarrino, “Pho-
tonic quantum metrology,” A VS Quantum Science2, 024703
(2020).
[124] K. C. McCormick, J. Keller, S. C. Burd, D. J. Wineland, A. C.
Wilson, and D. Leibfried, “Quantum-enhanced sensing of a
single-ion mechanical oscillator,” Nature572, 86 (2019).
[125] W. Wang et al. , “Approximate quantum error correction en-
hanced phase measurement,” .
[126] R. Naik, N. Leung, S. Chakram, P. Groszkowski, Y . Lu,
N. Earnest, D. McKay, J. Koch, and D. Schuster, “Random ac-
cess quantum information processors using multimode circuit
quantum electrodynamics,” Nat. Commun. 8, 1904 (2017).
[127] T. Brecht, W. Pfaff, C. Wang, Y . Chu, L. Frunzio, M. H. De-
voret, and R. J. Schoelkopf, “Multilayer microwave integrated
quantum circuits for scalable quantum computing,” npj Quan-
tum Inf. 2, 16002 (2016).
[128] C. T. Hann, C.-L. Zou, Y . Zhang, Y . Chu, R. J. Schoelkopf,
S. M. Girvin, and L. Jiang, “Hardware-Efﬁcient Quantum
Random Access Memory with Hybrid Quantum Acoustic Sys-
tems,” Phys. Rev. Lett.123, 250501 (2019).
[129] K. Jacobs, R. Balu, and J. D. Teufel, “Quantum-enhanced ac-
celerometry with a nonlinear electromechanical circuit,” Phys.
Rev. A 96, 023858 (2017).
[130] P. Krantz, M. Kjaergaard, F. Yan, T. P. Orlando, S. Gustavsson,
and W. D. Oliver, “A quantum engineer’s guide to supercon-
ducting qubits,” Appl. Phys. Rev.6, 021318 (2019).
[131] M. Kjaergaard, M. E. Schwartz, J. Braum ¨uller, P. Krantz, J. I.-
J. Wang, S. Gustavsson, and W. D. Oliver, “Superconducting
Qubits: Current State of Play,” Annu. Rev. Condens. Matter
Phys. 11, 369 (2020).
[132] J. Zmuidzinas, “Superconducting Microresonators: Physics
and Applications,” Annu. Rev. Condens. Matter Phys. 3, 169
(2012).
[133] A. Anferov, A. Suleymanzade, A. Oriani, J. Simon, and
D. I. Schuster, “Millimeter-Wave Four-Wave Mixing via Ki-
netic Inductance for Quantum Devices,” Phys. Rev. Appl. 13,
024056 (2020).
[134] N. H. Nickerson, Y . Li, and S. C. Benjamin, “Topological
quantum computing with a very noisy network and local error
rates approaching one percent,” Nat. Commun.4, 1756 (2013).
