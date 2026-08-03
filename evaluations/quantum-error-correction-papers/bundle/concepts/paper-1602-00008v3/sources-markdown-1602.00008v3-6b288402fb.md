---
type: Research Paper
title: New class of quantum error-correcting codes for a bosonic mode
description: '- Pinned arXiv record: [1602.00008v3](https://arxiv.org/abs/1602.00008v3)'
resource: https://example.org/qec-arxiv-papers/resource/paper-1602-00008v3/sources%2Fmarkdown%2F1602.00008v3
tags:
- paper-1602-00008v3
- markdown
- rl
concept_id: concepts/paper-1602-00008v3/sources-markdown-1602.00008v3-6b288402fb
concept_path: concepts/paper-1602-00008v3/sources-markdown-1602.00008v3-6b288402fb.md
subject_iri: https://example.org/qec-arxiv-papers/resource/paper-1602-00008v3/sources%2Fmarkdown%2F1602.00008v3
ontology_class_iri: https://example.org/ontology/qec-arxiv-papers#Paper
ontology_version_iri: https://example.org/ontology/qec-arxiv-papers/1.0.0
source_id: paper-1602-00008v3
source_kind: markdown
source_path: sources/markdown/1602.00008v3.md
source_content_sha256: 86bde738bf35bb1b1d5c9d9248a3ae9eedb461bda58f6a8aff204b930dec7caa
record_sha256: 0939752e0f73058362b641a988c167d07091247525a3ce83b072fc2d68c2fe57
source_refs:
- https://example.org/qec-arxiv-papers/provenance/record/paper-1602-00008v3/7a57aaca0c1eda2b95114c2f
record_id: sources/markdown/1602.00008v3
---

# New class of quantum error-correcting codes for a bosonic mode

## Source citation

- Pinned arXiv record: [1602.00008v3](https://arxiv.org/abs/1602.00008v3)
- Authors: Michael, Marios H.; Silveri, Matti; Brierley, R. T.; Albert, Victor V.; Salmilehto, Juha; Jiang, Liang; Girvin, S. M.
- PDF: [https://arxiv.org/pdf/1602.00008v3](https://arxiv.org/pdf/1602.00008v3)
- PDF SHA-256: `d802a8c4f75698a518f2a85447df84695da045aede972c32f165d38016057089`
- Extracted pages: 25

The following text was extracted page by page from the pinned PDF. Page headings are stable evidence locators.

## PDF page 1

New class of quantum error-correcting codes for a bosonic mode
Marios H. Michael,∗Matti Silveri,†R. T. Brierley, Victor V. Albert, Juha Salmilehto, Liang Jiang, and S. M. Girvin
Departments of Physics and Applied Physics, Yale University, New Haven, Connecticut 06520, USA
(Dated: July 19, 2016)
We construct a new class of quantum error-correcting codes for a bosonic mode which are
advantageous for applications in quantum memories, communication, and scalable computation.
These ‘binomial quantum codes’ are formed from a ﬁnite superposition of Fock states weighted with
binomial coeﬃcients. The binomial codes can exactly correct errors that are polynomial up to a
speciﬁc degree in bosonic creation and annihilation operators, including amplitude damping and
displacement noise as well as boson addition and dephasing errors. For realistic continuous-time
dissipative evolution, the codes can perform approximate quantum error correction to any given
order in the timestep between error detection measurements. We present an explicit approximate
quantum error recovery operation based on projective measurements and unitary operations. The
binomial codes are tailored for detecting boson loss and gain errors by means of measurements of the
generalized number parity. We discuss optimization of the binomial codes and demonstrate that by
relaxing the parity structure, codes with even lower unrecoverable error rates can be achieved. The
binomial codes are related to existing two-mode bosonic codes but oﬀer the advantage of requiring
only a single bosonic mode to correct amplitude damping as well as the ability to correct other
errors. Our codes are similar in spirit to ‘cat codes’ based on superpositions of the coherent states,
but oﬀer several advantages such as smaller mean boson number, exact rather than approximate
orthonormality of the code words, and an explicit unitary operation for repumping energy into the
bosonic mode. The binomial quantum codes are realizable with current superconducting circuit
technology and they should prove useful in other quantum technologies, including bosonic quantum
memories, photonic quantum communication, and optical-to-microwave up- and down-conversion.
PACS numbers: 03.67.Pp, 42.50.Ex, 85.25.Cp,
Continuous variable quantum information processing
using bosonic modes [ 1–8] oﬀers an attractive alternative
to two-level qubits. In practice, hybrid systems con-
taining ﬁxed qubits, photons trapped in resonators, as
well as ﬂying photon qubits will likely be essential to
realistic architectures for quantum computation and com-
munication [ 9–11]. There is lively current interest in
novel schemes for robustly encoding quantum informa-
tion in bosonic modes [ 12–22]. In particular, early work
by Chuang et al. [12] developed two-mode bosonic codes
which can protect quantum information against ampli-
tude damping of the bosonic ﬁeld. This paper presents
a new class of codes that are similar but have two dis-
tinct advantages: they require only a single bosonic mode
(not two with identical decay rates), and they can correct
other errors, e.g., dephasing in addition to amplitude
damping. Our codes are also similar in spirit to the
‘cat codes’ [16–19] and indeed asymptotically approach
them in certain parameter limits. However our codes
require a smaller mean boson number to achieve a given
ﬁdelity, and are deﬁned in a ﬁnite Hilbert space, making
explicit construction of the required unitary operations
more straightforward.
Besides extending the lifetimes of bosonic qubits or
quantum memories, we describe how such codes could be
∗Present address: Cavendish Laboratory, University of Cambridge,
JJ Thomson Avenue, Cambridge CB3 0HE, UK
†Present address: Theoretical Physics, University of Oulu, Finland;
matti.silveri@oulu.ﬁ
useful in increasing the ﬁdelity of quantum communica-
tion and remote entanglement between hardware modules
through photon ‘pitch and catch’ protocols [ 23–25] as
well as in improving the ﬁdelity of communication based
on reversible microwave to optical state conversion [ 26].
In general, a bosonic mode can refer to an electromag-
netic, magnetic or mechanical mode. However, the most
likely implementations in the short term are photonic,
so throughout this paper we will use term photon than
the more general boson, for simplicity. These codes are
of general interest for quantum information processing
but we will place particular emphasis on the possibility
of realizing them and the Chuang et al. code [12] using
superconducting qubits dispersively coupled to microwave
resonators. Given the remarkable experimental progress
in circuit QED in the last decade [ 9, 10], such codes are
ideally suited for this architecture and should be feasible
with current technology.
Superconducting qubit phase coherence times have risen
some ﬁve orders of magnitude and can now reach∼100µs
in 3D cavity geometries [ 27, 28] and up to ∼40 µs in
planar geometries [ 29–31]. Superconducting microwave
resonators are simpler than Josephson junction based
qubits and can readily be constructed to have lifetimes
even longer than the best qubits [10, 32–35]. It is therefore
interesting to consider the possibility of using microwave
resonators as qubits or as quantum memories. Experimen-
tal capabilities to arbitrarily control the quantum state of
a hybrid cavity-qubit system are now so advanced [36–44]
that it is time to take the next step and develop optimal
quantum error correction codes that further extend the
arXiv:1602.00008v3  [quant-ph]  18 Jul 2016

## PDF page 2

2
lifetimes of photonic quantum bits and memories.
Because a resonator mode is a simple harmonic oscilla-
tor with equidistant level spacing, the only quantum states
that can be accessed via classical linear drives are simple
coherent states. To create more useful quantum superpo-
sitions of photon Fock states which can store quantum in-
formation, it is necessary to couple the bosonic mode to a
non-linear element, e.g., a superconducting qubit [ 41, 42],
a trapped ion [ 45–48] or a Rydberg atom [ 32, 33]. Exper-
iments have demonstrated coherent mapping of a super-
conducting qubit state onto the corresponding coherent
superposition of 0 and 1 photons in a resonator [ 36] and
the creation of more complex superpositions [ 37]. Later
experiments with superconducting qubits and cavities
demonstrated the ability to transfer the qubit state into
the cavity for a period ∼750 µs much longer than the
qubit lifetime and then return it to the qubit prior to
veriﬁcation via process tomography [ 35]. Remarkably, it
is also now possible to make quantum non-demolition
measurements of photon number parity [39] which can be
used to greatly simplify the measurement of Wigner func-
tions [32, 38, 39]. Such parity measurements are utilized as
the error syndrome measurement in cat codes [ 17, 18, 39]
and will be used in some of the codes presented here. More
generally, by employing optimal control pulses [ 49, 50]
for engineering the driving terms of both a harmonic
oscillator and a coupled non-linear element, one can real-
ize arbitrary unitary operations for the full system with
high experimental ﬁdelity [ 41–44]. The practicality of
the codes presented here relies on recent experimental
progress in realizing this arbitrary unitary control.
Rudimentary quantum error correction (QEC) proto-
cols have been successfully carried out in ion traps [ 45,
47, 48], with nuclear magnetic resonance [ 51–53], with
nitrogen-vacancy centers in diamond [ 54, 55], Rydberg
atoms [33] and superconducting qubits [ 56–59]. However,
it is diﬃcult to reach the ‘break-even point’, where the
coherence time of the logical qubit exceeds the lifetime of
the constituent physical qubits. This has recently been
achieved in cavity photonic logical qubits [ 44] against
photon loss errors and in nitrogen-vacancy centers in di-
amond [ 60] against dephasing errors. For qubit-based
technologies, reaching break-even is challenging because
it takes N = 5 physical qubits for the smallest possi-
ble code [ 61–64], N = 7 qubits for the Steane code [ 65],
and N = 9 qubits for the Shor code [ 66]. If the er-
rors are uncorrelated single-qubit errors, the bare error
rate is N times faster than for a single qubit. Thus the
quantum error correction protocol must overcome this
factor of N in order to reach break-even. If the errors
are highly correlated, e.g. in the case of uniform mag-
netic ﬁeld ﬂuctuations in an ion trap, there may exist a
decoherence-free-subspace encoding which will be advan-
tageous [47, 64, 67–69]. To date there is no evidence that
correlated errors are a signiﬁcant problem for well-shielded
superconducting qubits.
Another potential advantage of resonators is that the
error model appears to be very simple. The dominant
source of decoherence is the energy loss of the cavity as
it slowly emits photons into its output and input ports.
The cavity energy ring-down rate κis the analog of 1/T1
for a qubit. To date, there is no evidence of dephasing
errors associated with frequency ﬂuctuations of 3D metal-
lic superconducting cavities though dephasing has been
seen in coplanar waveguide resonators by the Zmuidzinas
group [70] and attributed to two-level systems in the di-
electric substrate. However dispersive coupling of a qubit
to a resonator will introduce random ﬂuctuations of the
cavity frequency associated with T1 state change events
in the qubit [ 35]. Additionally, there can be, for example,
energy leakage from the driven ancillary qubit to the
resonator that can be result in photon gain errors. We
will focus on correcting cavity photon loss errors but the
constructed codes can be protected also against dephasing
and photon gain errors as well.
The paper is organized as follows. In Sec I, we intro-
duce quantum error correction against discrete photon
loss, photon gain and dephasing errors through simple
bosonic single-mode codes. These are generalized to bino-
mial quantum codes in Sec. II. Next we consider realistic
continuous-time dissipative evolution under these errors.
Since the continuous-time evolution introduces an inﬁnite
set of errors even during a ﬁnite timestep, exact quantum
error correction is impossible. In Sec. III, we prove our
main result—the binomial quantum codes can perform
approximate quantum error correction to any given order
in timestep for realistic continuous-time dissipative evolu-
tion. We introduce an explicit and experimentally relevant
recovery process. In the remainder of the paper, we ana-
lyze the performance of the codes, present comparisons
to related pre-existing codes, and discuss applications in
quantum communication and as logical qubits, respec-
tively in Secs. IV-VII. Further improvements and overall
discussion of the binomial codes are presented in Sec. VIII
before the summary and conclusion of Sec. IX.
I. QUANTUM ERROR CORRECTION
AGAINST PHOTON LOSS, GAIN AND
DEPHASING ERRORS
The generic task of quantum error correction is to ﬁnd
two logical code words—a qubit—embedded in a large
Hilbert space. The code words are required to be robust
such that if any one of the single, independent errors
ˆEk∈¯E occurs, no quantum information is lost and any
quantum superposition of the logical code words can be
faithfully recovered. This is equivalent to ﬁnding two
logical code words|Wσ⟩, where σ=↑,↓, that satisfy the
quantum error correction criteria [ 64, 71], known also as
the Knill-Laﬂamme conditions [62, 72],
⟨Wσ|ˆE†
ℓˆEk|Wσ′⟩=αℓkδσσ′, (1)
for all ˆEℓ,k∈¯E such that αℓkare entries of a Hermitian
matrix and independent of the logical words. The inde-
pendence of entries αℓkfrom the logical code words and

## PDF page 3

3
the structure of the non-diagonal entries guarantee that
the diﬀerent errors are distinguishable and correctable.
We consider a damped harmonic oscillator suﬀering
from photon losses. Our intention is to design logical
code words, which are embedded in the Hilbert space of
the harmonic oscillator and protected up to L photon
loss events occurring in the time interval δtbetween two
consecutive quantum correction stages. The set of discrete
errors is ¯EL =
{ˆI, ˆa, ˆa2,...ˆaL}
[73]. We will see that
satisfying the conditions (1) for these errors is suﬃcient
to produce a code that is systematically correctable up
to a given order in κδtunder the full amplitude damping
operators. Here our primary focus will be on photon loss
errors. Later we will discuss correcting photon gain ˆa†
and dephasing errors ˆn.
Suppose we restrict our attention to the lowest 2 M
Fock states of a single mode of a resonator. This Hilbert
space is the same size as that for M qubits and if one
had complete control over it, one could imagine having
a kind of hardware shortcut in which a single resonator
mode replaces a complex of M physical qubits to form
one or more logical qubits [10]. Notice that increasing the
size of the Hilbert space does not increase the number of
error channels or the minimal number of error syndromes.
Consider the following simple encoding of M qubits into
the state of the resonator. The 2 M Fock states cover
photon numbers 0, 1,..., (2M−1). Let photon Fock state
|n⟩be represented by|n⟩=|bn
M−1bn
M−2...bn
1bn
0⟩, where
bn
M−1bn
M−2...bn
1bn
0 is the binary representation of the
numbern. The jth binary digit represents the eigenvalue
(1 + ˆσz
j )/2 for the corresponding ‘physical qubit. ’ This
appears to be a very simple and satisfactory encoding
but consider what happens when the n = 8 state (say)
loses a single photon ˆa|1000⟩=
√
8|0111⟩. What seems
to be a simple error model in terms of photon loss actu-
ally becomes a model with correlated multi-qubit errors.
Hence typical quantum error correction schemes based on
models of independent single qubit errors cannot be easily
transferred to this problem [ 63, 64]. Because the mean
photon loss rate κ⟨ˆa†ˆa⟩scales exponentially with M, we
will focus here on representing a single logical qubit using
a small number of states in the cavity to permit error
correction.
An example of a code protecting against ¯E1 =
{ˆI, ˆa
}
is
|W↑⟩=|0⟩+|4⟩√
2 , |W↓⟩=|2⟩. (2)
A photon loss error brings the logical code words to a
subspace with odd photon numbers that is clearly dis-
joint from the even-parity subspace of the logical code
words. Therefore, the oﬀ-diagonal parts of the quan-
tum error correction matrix (1) αare identically zero.
The remaining diagonal part of αrequires that the mean
photon number is identical for both of the states, here
¯n =⟨Wσ|ˆn|Wσ⟩= 2. This means that the probability of
a photon jump to occur (or not to occur) is the same for
both of the states, implying that the quantum state is not
deformed under an error. Explicitly, if a quantum state
|ψ⟩=u|W↑⟩+v|W↓⟩suﬀers a photon jump, it is trans-
formed to|ψ1⟩= ˆa|ψ⟩/
√
⟨ψ|ˆa†ˆa|ψ⟩=u|¯E1
↑⟩+v|¯E1
↓⟩,
where|¯E1
↑⟩=|3⟩and|¯E1
↓⟩=|1⟩denote the error words.
The quantum information (the complex coeﬃcients u and
v) is not deformed.
In the optical regime, the photon loss error can be de-
tected by an external photodetector. This is not yet prac-
tical in the microwave regime, but fortunately we have the
capability of very high ﬁdelity quantum non-demolition
measurements of the photon number parity [ 39]. The
original state is recovered by a unitary operation ˆU1 that
performs the state transfer|¯E1
σ⟩↔|Wσ⟩; see Appendix A
for details. Correcting a non-unitary error with a unitary
operation works only because it is conditioned on the
detection outcome of the particular error. Notice that
the code (2) is similar to a code developed in Ref. [ 12] by
Chuang et al. for a multi-mode system. Our code has the
important advantages of requiring only a single bosonic
mode and having rate for uncorrectable errors that is
smaller by a factor of three (see Sec. V).
Generalizations of the code (2) are possible, for example
|W↑⟩=|0⟩+
√
3|6⟩
2 , |W↓⟩=
√
3|3⟩+|9⟩
2 . (3)
In addition to the logical words having the same
mean photon number, the error words |¯E1
σ⟩=
ˆa|Wσ⟩/
√
⟨Wσ|ˆa†ˆa|Wσ⟩,|¯E1
↑⟩=|5⟩and|¯E1
↓⟩= (|2⟩+
|8⟩)/
√
2 also have the same mean photon number. Thus
the code can tolerate another photon loss error and the
protected error set is ¯E2 =
{ˆI, ˆa, ˆa2}
. The photon loss
errors are detected by measuring photon number mod 3;
see Appendix A. The error recovery procedure is similar
to that above: an error detection is followed by a unitary
operation performing a state transfer |Wσ⟩↔|¯Ek
σ⟩. The
error correction matrix αfor the code (3) is diagonal
because of the suﬃciently large spacing of the occupied
Fock states in the logical words such that photon loss
errors ˆaℓ,ℓ≤2, cannot lead to overlap of the error words.
Frequency ﬂuctuations of the cavity ( i.e. noise ξ(t)
coupling to the photon number, ξ(t)ˆn, for example by
transitions of a dispersively coupled ancilla qubit [ 35])
cause dephasing of the quantum memory. In the limit
of fast Markovian noise, the eﬀect of ﬂuctuations is well
approximated by a Lindblad dissipator with a jump op-
erator√γˆn, where γis the dephasing rate. Even in the
case of non-Markovian noise, the errors take the form
ˆU(δt) = exp(−i
∫δt
0 ξ(τ)dτˆn). For small enough timesteps
δtthis error can be expanded as superposition of ˆnk op-
erators. Thus in both cases protection can be achieved
by considering the operator ˆn and its higher powers. In
what follows we will refer to these operators as dephasing
errors.
Due to the spacing of the Fock states and the prop-
erties of bosonic operators, the code (3) protects also
against a dephasing error ˆn, thus the full error set is
¯E2 =
{ˆI, ˆa, ˆa2, ˆn
}
. Since the dephasing error does not
change the photon number, it leads to an error state

## PDF page 4

4
|ψn⟩= ˆn|ψ⟩/
√
⟨ψ|ˆn2|ψ⟩,
|ψn⟩=u
√
3|W↑⟩−|¯En
↑⟩
2 +v
√
3|W↓⟩−|¯En
↓⟩
2 . (4)
which is a superposition of the original words and the error
words related to the dephasing|¯En
↑⟩= (
√
3|0⟩−|6⟩)/2 and
|¯En
↓⟩= (|3⟩−
√
3|9⟩)/2. The only way to detect the de-
phasing error is to make projective measurements into the
logical word basis ˆPW =∑
σ|Wσ⟩⟨Wσ|and if the answer
is negative and no photon loss errors were detected, the
original state is recovered by making a unitary operation
performing a state transfer |¯En
σ⟩↔|Wσ⟩. Remarkably
such complex operations applied to a cavity-ancilla qubit
systems are now technically feasible [41–44].
The code (3) can instead be chosen to be protected
against errors ¯E′
2 =
{ˆI, ˆa, ˆa†, ˆn
}
since a photon gain error
and two-photon loss errors have the same change in the
photon number mod 3 and the logical code words already
obey the quantum error correction condition for the pho-
ton gain error: ⟨Wσ|ˆaˆa†|Wσ′⟩= (¯n + 1)δσσ′. As a special
case, one can choose to protect only against ¯E′
1 =
{ˆI, ˆa, ˆn
}
achieved by the same Fock state coeﬃcients as with the
code (3) but with spacing of the code (2):
|W↑⟩=|0⟩+
√
3|4⟩
2 , |W↓⟩=
√
3|2⟩+|6⟩
2 . (5)
The relationship between the codes (3) and (5) arises from
a general structure, which we exploit in the next section.
II. BINOMIAL QUANTUM CODES
We now generalize the above codes to protect against
the error set,
¯E =
{ˆI, ˆa, ˆa2,..., ˆaL, ˆa†,..., (ˆa†)G, ˆn, ˆn2,..., ˆnD}
, (6)
which includes up toL photon losses, up toG photon gain
errors, and up to D dephasing events. We have found a
simple class of codes which can correct such an error set,
|W↑/↓⟩= 1√
2N
[0,N+1]∑
p even/odd
∫(N + 1
p
{
|p(S + 1)⟩, (7)
where the spacing is S = L +G, maximum order N =
max{L,G, 2D}and the range of the index p is from 0 to
N + 1. The two-parameter (N,S ) code space is shown in
Fig. 1. Because the Fock state coeﬃcients involve binomial
coeﬃcients we refer to this class as the binomial codes .
The spacing between the occupied Fock states is S +
1 such that the correctable L photon loss and G gain
errors can be uniquely distinguished by measuring photon
number modulo S + 1, which we call ’generalized parity’
here. The quantum error correction conditions (1) require
that⟨Wσ|(ˆa†)ℓˆaℓ|Wσ⟩, for all ℓ≤max{L,G}, is equal
for the two logical code words. Satisfaction of Eq. (1)
guarantees that the quantum state is not deformed under
an error and implies as well an existence of a recovery
process—the detectable errors can be recovered using
unitary operations. By using commutation relations it
is equivalent to require that ⟨Wσ|ˆnℓ|Wσ⟩, for all ℓ≤
max{L,G}, be equal for the two logical code words, just
as the mean photon number of the logical code words (2)
was required to be equal. A straightforward way of seeing
that expectation values for moments of the photon number
are equal is to recall the binomial formula and consider
the diﬀerence
∆ ℓ=⟨W↑|ˆnℓ|W↑⟩−⟨W↓|ˆnℓ|W↓⟩
= (S + 1)ℓ
2N
N+1∑
p=0
(N + 1
p
{
pℓ(−1)p
= (S + 1)ℓ
2N
(
x d
dx
{ℓ
(1 +x)N+1
⏐⏐⏐⏐⏐
x=−1
. (8)
The derivative on the last line preserves at least one (1+x)
in each of the terms of the above polynomial such that
∆ ℓ= 0 for all ℓ≤N = max{L,G}; see Appendix B. It
should be noted that the coeﬃcients of the Fock states
in the code words (7) are independent of the spacing
S + 1. The spacing between occupied Fock states enables
the detection of photon loss errors. The values of the
Fock state coeﬃcients are determined by balancing the
moments of the photon number distribution so that the
rate of errors is the same for all logical states.
The basis of the two logical code words can be gen-
eralized to d logical code words, a so-called ‘qudit’, by
utilizing extended binomial coeﬃcients
(N+1
p
{
d [74, 75]
(deﬁned in Appendix C; these are also called polynomial
coeﬃcients [76]),
|Wi⟩= 1√
dN
[0,pm]∑
p=i modd
∫(N + 1
p
{
d
|p(S + 1)⟩, (9)
wherei = 0, 1,...,d−1 andpm = (d−1)(N +1). By using
a similar argument as with the binomial qubit codes in
Eq. (8), one can show that the photon number moments
are equal for all of the d code words; see details in Ap-
pendix C. In what follows we, for simplicity, concentrate
on the binomial qubit codes but all the results can be
extended to the binomial qudit codes as well.
For measuring photon number mod S + 1 the mode
needs to be coupled to an ancillary system, either a su-
perconducting qubit [41, 42], a trapped ion [ 45–48] or a
Rydberg atom [ 32, 33]. With superconducting circuits,
the parity could be measured by utilizing the strong dis-
persive coupling between the cavity and the ancillary
qubit and by using number selective coherent drives simi-
lar to the demonstrated quantum non-demolition parity
measurement [38, 39, 41, 42]; see Appendix A. Encoding
the diﬀerent outcomes of a multi-valued measurement,
such asS≥2, in the higher excited states of the ancillary

## PDF page 5

5
Figure 1. Two-parameter ( N,S ) space of the binomial
codes (7). The largest blue circle denotes the code (2) pro-
tected against a photon loss error L = 1, the blue square
is the code (3) protected against ¯E2 ={ˆI, ˆa, ˆa2, ˆn}or ¯E′
2 =
{ˆI, ˆa, ˆa†, ˆn}, and the green diamond denotes the code (5) pro-
tected against ¯E′
1 ={ˆI, ˆa, ˆn}. The parameter S = L +G
sets the total number of detectable photon loss L and gain G
errors. The parameter N sets the maximum order the code
is protected against photon loss, gain and dephasing errors
N = max{L,G, 2D}. The codes denoted with blue have pro-
tection against photon loss and gain errors set by S =L +G
and in addition they are protected against dephasing up to
ˆn⌊max{L,G}/2⌋. The codes denote with red allow in addition
heralding of S−2N uncorrectable photon loss or gain errors.
The codes denoted with green are protected against a total of
S photon loss and gain errors, as well as against up to ˆnN/2
dephasing errors. In the limit N →∞the binomial codes
asymptotically approach the 2(L + 1)-legged cat codes [17–19]
protected against L photon loss errors.
qubit would allow single-shot measurements. An alterna-
tive is to do S sequential measurements with a two-level
qubit.
Dephasing errors result in mutually non-orthogonal
error states: for them the quantum error correction matrix
is non-diagonal but Hermitian. For that reason, to detect
and recover those errors one needs to make projective
measurements in an orthonormalized basis, as with the
code (3). After a detection of an error, the original state
is recovered by a unitary operation performing a state
transfer between the subspaces of the error and logical
code words.
A. Errors correctable by binomial codes
The binomial code coeﬃcients were derived using the
requirement to be able to correct the photon loss or gain
errors. Considering only photon loss errors, the parameter
L + 1 can be interpreted as the distance of the binomial
quantum codes since it is the minimum number of ˆa
operators needed for mixing the two code words. Inclusion
of dephasing errors makes the quantum error correction
matrix (1) non-diagonal, but it automatically follows from
the binomial coeﬃcients that dephasing errors up to order
⌊max{L,G}/2⌋are also corrected by these codes. The
highest degree of dephasing protection ˆnD does not need
to be limited to the value set by the photon loss/gain
protection. By increasing the length N of the binomial
code words, D can be increased without a limit. This
gives the maximum order as N = max{L,G, 2D}. Note
also that since the binomial codes are protected against
any one of the errors from the error set (6), they are also
protected against any errors that are superpositions of
these. Such errors include, for instance, displacement
‘unitary’ errors
ˆD(β) = exp
(
βˆa†−β∗ˆa
{
(10)
for small unknown β. More precisely, a binomial code
with given values of N, L and G satisﬁes:
⟨Wσ|(ˆa†)n+ˆan−|Wσ′⟩=
{
0, if n+̸=n−,
αn+δσσ′if n+ =n−≤N,
(11)
where|n+−n−|≤G +L with n+,n−≥0 and the αn+
are constants. In particular, if the condition is satisﬁed
for some values ofn+ andn−, it is satisﬁed for all smaller
values. This property means, for example, that the code
can correct all errors of the form
ˆAi =
∑
jk
ξ(i)
jk (ˆa†)jˆak, (12)
if all nonzero ξ(i)
jk satisfy 0≤j−k≤G, 0≤k−j≤L
and j +k≤N. When choosing a code, the minimum
value of N is determined by the term with the largest
total number of ˆa and ˆa†operators. The parameter L (G)
is given by the error term that causes the largest overall
decrease (increase) in excitation number. For example,
to correct ˆA = ˆa†+ ˆn2 requiresG≥1 from the ﬁrst term,
N≥2 from the second term and L≥0 as there are no
number-decreasing terms.
III. APPROXIMATE QUANTUM ERROR
CORRECTION UNDER CONTINUOUS-TIME
DISSIPATIVE EVOLUTION
Up to now we have assumed that the cavity is subject
to a ﬁnite set of discrete errors. In fact, the cavity evolves
continuously in time. For example, the standard Lindblad
time evolution of a density matrix ˆρof a cavity coupled
to a zero-temperature bath with a cavity energy decay
rate κ(represented in the frame rotating at the cavity
frequency) is
dˆρ=κdt
(
ˆaˆρˆa†−ˆa†ˆa
2 ˆρ−ˆρˆa†ˆa
2
{
. (13)
In a ﬁnite time interval δt, continuous-time evolution re-
sults in an inﬁnite set of possible errors. Exact quantum
error correction of the full set of errors is not possible.

## PDF page 6

6
However, the probabilities of the errors scale with powers
of κδtand we can choose to correct only the most impor-
tant errors inκδt. Formally, we will exploit the notion and
theory of approximate quantum error correction [ 21, 77–
84]. We expand each error operator in powers of κδtand
choose to correct up to a given highest order. It is then
enough to satisfy the quantum error correction criteria (1)
only approximately such that the original state can be
recovered with an accuracy given by the same highest
order in κδt.
Initially, we consider only photon loss errors due to
cavity damping and extend the discussion for photon gain
and dephasing processes later. One can ‘unravel’ the Lind-
blad equation (13) for photon loss errors by considering
the conditional quantum evolution of the system based on
the measurement record of a photomultiplier that clicks
whenever a photon leaks out of the cavity. In this quan-
tum trajectory picture [ 85], one views the ﬁrst term in
Eq. (13) representing the photon loss jump of the system
when the detector clicks ˆρ→ˆaˆρˆa†. This is not normalized
because it includes the fact that the click probability is
proportional to Tr(ˆaˆρˆa†) = ¯n. The last two terms inside
the brackets represent time evolution of the system under
the non-Hermitian Hamiltonian ˆV/ ℏ =−iκ
2 ˆa†ˆa when no
photons are detected. We have previously omitted this
no-jump evolution for simplicity, but will now examine
this crucial part of the physical error process.
Much like a Feynman path integral, we can express the
evolution of the density matrix from time 0 to δtin terms
of a sum over all possible trajectories with photon loss
jumps occurring at all possible times during the ﬁnite
time interval δt. We express this time evolution as a
completely positive and trace preserving (CPTP) process
E ={ˆE0, ˆE1, ˆE2,...}:
ˆρ(δt) =E(ˆρ(0))≡
∞∑
ℓ=0
ˆEℓˆρ(0) ˆE†
ℓ, (14)
where ˆEℓare Kraus operators encapsulating the time
evolution generated by exactly ℓphoton losses and the
no-jump evolution. Remarkably, by integrating over all
the possible jump times of exactly ℓphoton jumps during
the time interval δt, we can derive an exact analytic
expression for ˆEℓ[12, 86, 87],
ˆEℓ=
√
(1−e−κδt)ℓ
ℓ! e−κδt
2 ˆnˆaℓ. (15)
See Appendix D for more details of the derivation. An im-
portant feature of the damped simple harmonic oscillator
is that the precise timing of the the photon jumps plays
no role. This can also be seen in the interchangeability of
the order of the operators in Eq. (15): exp(−κδtˆn)ˆaℓ=
exp(κδtℓ)ˆaℓexp(−κδtˆn). Taken together, when correcting
against photon loss errors up to order ( κδt)L, the correct
set of errors the codes should be protected against is (the
Taylor series expansion of) EL ={ˆE0, ˆE1,..., ˆEL}[88].
This set includes contributions of both the jump and
no-jump parts of the non-unitary time evolution.
The measurement backaction of observing no photon
jumps is non-trivial. It reduces the relative probability of
the higher occupied Fock states with respect to the lower
ones, formally expressed with the factor exp
(
−1
2 ˆnκδt
{
in the error operators (15). Others have addressed this
by constructing multimode codes [ 12, 21, 89, 90]. These
codes avoid no-jump evolution by combining two or more
physical elements with identical decay rates and construct-
ing the logical code words such that they are superposi-
tions of states with the same combined total excitation
number. They are essentially entangled versions of the
codes (2)-(5); see Sec. V.
One of our key results is that certain single-mode codes,
such as the binomial codes (7), can correct the no-jump
evolution to the same accuracy as photon loss errors. We
illustrate this ﬁrst to accuracyO(κδt) before giving a gen-
eral description to an arbitrary accuracy in powers of κδt.
A. Approximate quantum error correction to ﬁrst
order in κδt
Let us consider the code (2). When no photon loss
is detected, the quantum state |ψ⟩= u|W↑⟩+v|W↓⟩
transforms under the no-jump evolution given by ˆE0 =
exp
(
−1
2κδtˆn
{
. Code (2) is protected against a photon
loss error occurring with a probability to ﬁrst order inκδt:
P1 =⟨ˆE†
1 ˆE1⟩=κδt¯n +O[(κδt)2]. Thus, it is reasonable
to consider the no-jump evolution to the same accuracy.
Taking into account ˆE0 and the normalization in the
denominator of |ψ0⟩= ˆE0|ψ⟩/⟨ψ|ˆE†
0 ˆE0|ψ⟩
1/2
to ﬁrst
order in κδt, we obtain
|ψ0⟩=
[
1 +κδt
2 (¯n−ˆn)
]
|ψ⟩+O[(κδt)2]
=u
(
|W↑⟩+κδt|E0
↑⟩
{
+v|W↓⟩+O[(κδt)2]. (16)
Here|E0
↑⟩= (|0⟩−|4⟩)/
√
2 is the error word associated
with the no-jump evolution. Notice that the logical code
word|W↓⟩=|2⟩is unaﬀected by the no-jump evolution
as its excitation number is equal to the mean photon
number.
The no-jump error causes deterministic evolution inside
the subspace{|W↑⟩,|E0
↑⟩}which can be inverted to the
desired accuracy by applying a unitary operator,
ˆU0 = sinκδt
(
|W↑⟩⟨E0
↑|−|E0
↑⟩⟨W↑|
{
(17)
+ cosκδt
(
|W↑⟩⟨W↑|+|E0
↑⟩⟨E0
↑|
{
+|W↓⟩⟨W↓|+ ˆUres.
Here, ˆUres is an arbitrary unitary operator on the sub-
space complementary to the logical and error subspaces
in order to complete ˆU0 to a unitary operator in the
entire Hilbert space. It can be taken to be the iden-
tity of the complementary subspace. By combining
detection-correction of both the errors, the total recov-
ery process is R ={ˆR0, ˆR1}. The Kraus operators are
ˆRk = ˆUk ˆΠk mod 2, where ˆΠk mod 2 is a projection into

## PDF page 7

7
the photon number subspace k mod 2 and the correction
unitary ˆU1 is introduced in the text after Eq. (2). The
recovery processes results in the original state to ﬁrst
order in κδtas desired:
R (E(ˆρ)) =
1∑
k=0
ˆRk
(∞∑
ℓ=0
ˆEl ˆρˆE†
ℓ
(
ˆR†
k
=
1∑
k=0
1∑
ℓ=0
ˆRk ˆEℓˆρˆE†
ℓˆR†
k +O[(κδt)2] (18)
=
1∑
ℓ=0
ˆRℓˆEℓˆρˆE†
ℓˆR†
ℓ+O[(κδt)2] = ˆρ+O[(κδt)2].
Here we have ﬁrst ignored all the parts ˆEℓ≥2 of the error
process whose eﬀect isO[(κδt)2]. On the next line we use
the knowledge that the initial state has even parity and
the photon loss error process ˆEℓshifts photon number
by ℓ, formally ˆRk ˆEℓˆΠ 0 mod 2 = ˆUk ˆΠk mod 2 ˆEℓˆΠ 0 mod 2 =
δkℓˆRℓˆEℓˆΠ 0 mod 2, for k,ℓ∈{0, 1}.
Alternatively the recovery can be done by a mea-
surement projecting to the subspace of logical code
words [ 91] such that Rm ={ˆPW, ˆU1(ˆI−ˆPW)}. Here,
ˆPW =∑
σ|Wσ⟩⟨Wσ|is the projection to logical subspace.
If the measurement projects out of the code space, then it
is interpreted as the occurrence of a photon loss error and
it is corrected with the unitary ˆU1 performing the state
transfer from the error subspace of a photon loss to the log-
ical code words. If the measurement projects into the code
space, the state underwent no-jump evolution of Eq. (16)
and has been projected back to its original form by the
measurement backaction ˆPW. With a probability scaling
with (κδt)2 the state|E0
↑⟩, belonging to the compliment of
the logical subspace, is interpreted as a photon loss error.
However, this causes no interference with the approximate
recovery process as it occurs with a probability beyond
the accuracy limit of the code. Recovery by measurement
is reminiscent of the quantum Zeno eﬀect: if the time
evolution of a quantum state is linear (or faster) in δt,
it can be slowed to order δt2 by frequent measurements
projecting to the non-evolved basis [ 85]. The no-jump
evolution scales linearly in κδtand therefore can be cor-
rected by frequent projective measurements. Although
the recovery processRm is conceptually simpler, sophisti-
cated measurements such as ˆPW are presumably harder
to realize at high ﬁdelity than parity measurements [ 39]
(at least with the current technological capabilities).
B. Approximate quantum error correction to Lth
order in κδt
Here, we construct an explicit recovery process in terms
of projective measurements and unitary operations, which
generalizes the above discussion to multiple photon losses
and shows that the binomial codes can protect against the
continuous-time dissipative evolution of Eqs. (14-15) to an
accuracy of (κδt)L. Let us take the binomial code words
|Wσ⟩protected against L photon loss errors, and choose
G = 0 and S =L in Eq. (7). Here we show that they are
protected against the no-jump evolution to the desired
accuracy as well. Our derivation is similar to Ref. [ 21].
However we arrive at a result that is not obvious from
Ref. [21] since we exploit the explicit structure of the error
operators ˆEℓ(15).
The Kraus operators ˆEℓ>Lcan be ignored as they have
an eﬀect of O[(κδt)L+1]. We also ignore the parts of
the remaining Kraus operators that are irrelevant to the
desired accuracy and split the rest into two parts for
convenience,
ˆEℓ= ˆBℓ+ ˆCℓ+O
[
(κδt)L+ 1
2
]
, (19)
for 0 < ℓ≤L. We denote ˆBℓas the important leading-
order part and ˆCℓthe relevant sub-leading part,
ˆBℓ= ˆaℓ
L∑
µ=ℓ
ˆEµ,ℓ(κδt)
µ
2, (20a)
ˆCℓ= ˆaℓ
2L−ℓ∑
µ=L+1
ˆEµ,ℓ(κδt)
µ
2, (20b)
where for clarity we have separated the common pho-
ton loss term. The pure no-jump evolution is handled
diﬀerently [ 81] and we write ˆE0 = exp(−κδtˆn/2) =
ˆB0 +O[(κδt)L+1]. The term ˆEµ,ℓdenotes the µth en-
try of the expansion of
√
(1−e−κδt)ℓ/ℓ! exp(−κδtˆn/2) in
powers of (κδt)
1
2 . They are polynomials of ˆn with highest
degree≤µ/2.
With these preliminaries, the resulting error process is
E(ˆρ) =
L∑
ℓ=0
ˆEℓˆρˆE†
ℓ+O
[
(κδt)L+1]
(21)
=
L∑
ℓ=0
(
ˆBℓˆρˆB†
ℓ+ ˆBℓˆρˆC†
ℓ+ ˆCℓˆρˆB†
ℓ
{
+O
[
(κδt)L+1]
.
Here we see that the part ˆBℓˆρˆB†
ℓneeds to be corrected ex-
actly since it always has an eﬀect larger thanO[(κδt)L+1].
It is not necessary to correct exactly the entire interfer-
ence part ˆBℓρC†
ℓsince its contribution is partly beyond
the accuracy limit. Hence, one can ignore the negligible
O[(κδt)L+1] part of the interference terms and verify only
that the eﬀect of the remaining important part is inde-
pendent of the logical code words. Together, if the error
operators ˆBℓand ˆCℓfor all 0 ≤ℓ≤L satisfy the two
following conditions,
⟨Wσ|ˆB†
ℓˆBℓ|Wσ′⟩=βℓδσσ′, (22a)
⟨Wσ|ˆB†
ℓˆCℓ|Wσ′⟩=νℓδσσ′+O
[
(κδt)L+1]
, (22b)
the original state can be recovered to an accuracy of
(κδt)L. The ﬁrst condition guarantees that the errors ˆBk

## PDF page 8

8
can be recovered exactly, see Eq. (1). The second condi-
tion shows that the eﬀect of the interference is tolerable.
Both ˆB†
ℓˆBℓand ˆB†
ℓˆCℓup to accuracy of (κδt)L can be
written as a polynomial of ˆn with the highest degree of
L. The binomial code words protected against L photon
losses have equal expectation value of ˆnℓ, for all ℓ≤L
and for both of the code words, which implies that the
conditions (22) are satisﬁed for them.
Now we show that the recovery process R =
{ˆR0, ˆR1,..., ˆRL}with the Kraus operators ˆRk =
ˆUk ˆΠk modL+1 results in the original state to the desired
accuracy. The photon number modulo L + 1 is measured
and the measurement result k has a backaction in the
form of the projection ˆΠk modL+1. For k̸= 0, the error
words are|Bk
σ⟩= ˆBk|Wσ⟩/√βk, where βk is deﬁned in
Eq. (22a). Conditioned on the measurement outcome,
one applies a correction unitary ˆUk performing a state
transfer between the logical code words and the error
words|Bk
σ⟩,
ˆUk =
∑
σ
(
|Wσ⟩⟨Bk
σ|−|Bk
σ⟩⟨Wσ|
{
+ ˆUres. (23)
Again ˆUk is completed to a unitary operator in the en-
tire Hilbert space by ˆUres which is an arbitrary unitary
operator on the subspace complementary to the logical
and error subspaces (and diﬀerent for each k). For k = 0,
the error word needs to be orthogonalized with respect to
|Wσ⟩: |B0
σ⟩=
(
1−|Wσ⟩⟨Wσ|
{ˆB0|Wσ⟩/
∑
β0−|⟨ˆB0⟩|2,
where⟨ˆB0⟩=⟨Wσ|ˆB0|Wσ⟩. The correction unitary is
ˆU0 =
∑
σ
)∫
1−|⟨ˆB0⟩|2
β0
(
|Wσ⟩⟨B0
σ|−|B0
σ⟩⟨Wσ|
{
+⟨ˆB0⟩√β0
(|Wσ⟩⟨Wσ|+|B0
σ⟩⟨B0
σ|)
[
+ ˆUres. (24)
These unitary operations ˆUk correct both the photon
loss ˆak and the no-jump evolution by the rest of ˆBk in
Eq. (20a). As in the L = 1 case, the error ˆEℓshifts the
photon number by ℓand the initial state has a known
generalized parity meaning that ˆRk ˆEℓˆΠ 0 modL+1 =
δkℓˆRℓˆEℓˆΠ 0 modL+1, for k,ℓ={0, 1,...,L}. Finally, we
arrive at the approximate quantum error correction re-
covery process with accuracyO[(κδt)L]:
R(E(ˆρ)) =
L∑
ℓ=0
ˆRℓˆBℓˆρˆB†
ℓˆR†
ℓ
+
L∑
ℓ=0
ˆRℓ
(
ˆBℓˆρˆC†
ℓ+ h.c.
{
ˆR†
ℓ+O
[
(κδt)L+1]
=ˆρ
L∑
ℓ=0
(βℓ+ν∗
ℓ+νℓ) +O
[
(κδt)L+1]
=ˆρ+O
[
(κδt)L+1]
. (25)
We have used the form (21) of the error process, the con-
ditions (22) and the form of the correction unitaries (23)-
(24). The last summation is the resolution of the identity,∑∞
ℓ=0 ˆE†
ℓˆEℓ= ˆI, by using Eq. (19) and ignoring terms
that areO[(κδt)L+1]. The residual error terms in Eq. (25)
depend on the binomial code parameters S and N. We
analyze the eﬀects of this dependence on the codes’ per-
formance in Sec. IV.
In summary, we have shown that the single-mode codes
protected against L photon loss errors are approximate
quantum error correction codes protected against the
continuous-time dissipative photon loss channel to an ac-
curacy of (κδt)L. Physically, if observation of photon loss
errors up to a maximum of L times yields no information
on population and relative phases between the logical
code words, then also the observation of no-jump errors
≤L times yields no information and the measurement
backaction does not deform the encoded quantum infor-
mation of the state. This is one of our main results as it
gives an explicit construction recipe for approximate error
correction codes to arbitrary order in κδtfor a damped
bosonic mode.
As discussed in Sec. II, the binomial codes may also be
used to protect against more complicated error operators,
such as ˆn. An analysis of the code parameters required to
achieve such protection in the case of dissipative Lindblad
time evolution under these errors is given in Appendix E.
As in the case of dephasing errors in Sec. I, the recovery
process for more general errors will be more complicated
than that for photon losses alone.
IV. BINOMIAL CODE PERFORMANCE
Ignoring possible experimental inﬁdelities of the recov-
ery process, the performance of a binomial code is deﬁned
by the rate of uncorrectable errors. When including sev-
eral error channels, that is photon loss, photon gain and
dephasing errors with rates κ, κ+ and γ, the exact ex-
pression for the dominant uncorrectable error depends
on the relative ratio of these rates. For simplicity, here
we consider just a single error channel, the photon loss
channel.
Let us consider the binomial code words with S =
N = L and study ﬁrst the mean photon number ¯n =
1
2 (L + 1)2. It scales quadratically with the number of
protected photon loss errors L. This implies faster decay
of the code words of higher-order protection and that
to achieve the advantage of higher-order protection, the
timestep δtmust be made appropriately smaller. More
precisely, the rate of uncorrectable errors is dominated by
the leading uncorrectable photon loss error rate, that is,
the rate of losing L + 1 photons during the timestep δt:
PL+1
δt =⟨ˆE†
L+1 ˆEL+1⟩
δt
∼κ(κδt)L
⟨
(ˆa†)L+1ˆaL+1⟩
(L + 1)! ∼κ(κδt)LLL+1 . (26)

## PDF page 9

9
Figure 2. The rate of entanglement inﬁdelity ˜Fe/δtfor a
fully mixed logical qubit state plotted as a function of the
timestep δt(notice the logarithmic scale of both axes) for
the binomial codes (7) with S = N = L = 1 (black),
2 (gray), 3 (brown), 4 (red) and 5 (orange). Here we have
assumed a perfectly faithful recovery process. The dashed
line shows the performance of the naive encoding L = 0,
|W i
↑/↓⟩=|0/1⟩, whose rate of entanglement inﬁdelity at small
δtapproaches κ/2 corresponding to the rate of a photon
loss with ¯n = 1/2. Entanglement inﬁdelity [ 92] is calcu-
lated as ˜Fe = 1−Fe = 1−
∑L
k=0
∑∞
ℓ=0|Tr( ˆRk ˆEℓˆρc)|2, where
ˆρc = 1
2
∑
σ|Wσ⟩⟨Wσ|is the fully mixed state of the logical
code words. The entanglement inﬁdelity for a fully mixed
state is equal to the process inﬁdelity 1 −χII of a quantum
memory. For an ideal quantum memory χII = 1 and the full
quantum process is just an identity operation [ 64]. At small
timestep δt, the slopes of ˜Fe/δtagree well with the slopes
for the rate of the leading uncorrectable error PL+1/δt. The
binomial code with L = 1 outperforms the naive encoding
for timesteps δt≲ 0.4κ−1 and the codes with L> 1 become
favorable when δt≲ 0.2κ−1.
This scaling result implies that for a ﬁxed timestep δt
there exists an optimal binomial code with ﬁnite L that
minimizes the uncorrectable error rate among diﬀerent
binomial codes. In Fig. 2 we have demonstrated the
performance of the binomial codes for S = N = L =
0,..., 5 via the rate of the entanglement inﬁdelity which,
in the absence of inﬁdelities in the recovery process and
at small timesteps δt, is well approximated by the leading
uncorrectable error rate. As is clearly visible in Fig. 2, for
a given δtthere exists an optimal code and larger codes
are preferable for smaller timesteps.
An experimental inﬁdelityηrelated to a single recovery
stage increases the error rates by η/δtfavoring low-order
binomial codes with longer optimal timesteps; see Ap-
pendix F. The optimality of a code depends also on the
detailed structure of the experimental recovery process
since some of the inﬁdelities can be correctable errors
suppressed by the next round of the recovery process.
In addition, parity measurements often have higher ﬁ-
delity [39] than the unitary operations. The overall ﬁ-
delity of the error recovery could be improved by making
several measurements and using Bayesian estimation to
increase the conﬁdence of the error detection step [93].
If a self-Kerr non-linearity term ∝ˆn2 is present in the
cavity Hamiltonian, then it no longer commutes with the
dissipative evolution. Such terms are diﬃcult to avoid,
either as a result of intrinsic higher-order behavior of the
resonator, or due to hybridization with other non-linear
degrees of freedom, such as superconducting qubits. Dur-
ing timesteps with only no-jump evolution, a non-linearity
just introduces an additional unitary evolution that can
be taken into account by deﬁning a frame of rotating code
words. In this frame the Fock state coeﬃcients in Eq. (7)
acquire time-dependent complex phase factors but still
obey the quantum error correction conditions (1). An-
other possibility is to apply a gate that inverts the unitary
evolution as recently demonstrated experimentally with
superconducting qubit-cavity technology [42].
During timesteps with photon jumps, the non-
commutation of the Hamiltonian and ˆa means precise
timing of the photon jumps matters. Diﬀerent Fock states
acquire diﬀerent, jump-time-dependent phase factors. Af-
ter averaging over possible jump times, this generates
additional dephasing errors, of size ∝δt. However, the
probability of a timestep with a photon jump is only
∼κδt. As a result, the net eﬀect is ∼δt2, which is higher
order than the corresponding photon loss error. Thus,
as long as the non-linearity is not much larger than κ,
it does not break the approximate quantum error cor-
rection arguments of Sec. III. Furthermore, the binomial
codes can protect against additional dephasing errors by
increasing the parameter N in Eq. (7). The cost of the
higher degree of protection is an increase in the error
probabilities, which can be compensated by decreasing
the error correction timestep correspondingly, cf. Fig. 2.
The Kerr eﬀect becomes a limiting factor for codes with
large number variance
⟨
(ˆn−¯n)2⟩
. ¯n only describes the
‘mean ﬁeld’ Stark shift, which does not contribute to the
dephasing of Fock states relative to each other.
V. COMPARISON TO OTHER CODES
A. Two-mode codes
As we have discussed above, even in the event of no
photons being lost, the Kraus operator ˆE0 = exp(−1
2 ˆnκδt)
has a non-trivial eﬀect on the single-mode code words, and
so must be corrected. This can be avoided if the words
are superpositions of states with the same excitation
number by combining multiple physical elements [ 12, 89,
90]. In particular, some of the multimode bosonic codes
in Ref. [12] have the same structure as the binomial single-
mode codes presented here, but are entangled across
multiple photon modes,
|W↑/↓⟩=
[0,N+1]∑
p even/odd
cp|p(S + 1),N tot−p(S + 1)⟩, (27)

## PDF page 10

10
where Ntot = (N + 1)(S + 1) is the excitation number,
cp =
∑(N+1
p
{
/2N and|n,m⟩is a state with n photons in
one mode and m in the other. This code consists of two
copies of the one-mode binomial code of Eq. (7) with the
words entangled between the two modes.
Let us consider the simplest example, two-mode version
of the single-mode code of Eq. (2),
|W↑⟩=|0, 4⟩+|4, 0⟩√
2 , |W↓⟩=|2, 2⟩. (28)
Assuming identical photon decay rates κfor both modes,
the Kraus evolution operator in the absence of photon
losses from either mode is ˆE00 = exp(−1
2(ˆn1 + ˆn2)κδt), so
that ˆE00|Wσ⟩= exp(−2κδt)|Wσ⟩and the code words are
unchanged. The correctable errors are still single photon
losses, which can occur from either of the two modes,
giving rise to diﬀerent error words:
|W↑⟩→|E11
↑⟩=|3, 0⟩or |E21
↑⟩=|0, 3⟩, (29a)
|W↓⟩→|E11
↓⟩=|1, 2⟩or |E21
↓⟩=|2, 1⟩. (29b)
where|Ei1
σ⟩is the error word after a photon loss from
mode i. A parity measurement on each mode can dis-
tinguish from which mode the photon was lost, and so
be used to determine whether to correct the error words
|E11
σ⟩or|E21
σ⟩. The unitary operations required for er-
ror correction are swaps |Ei1
σ⟩↔|Wσ⟩, that is unitary
operations
ˆUi1 =
∑
σ
(
|Ei1
σ⟩⟨Wσ|−|Wσ⟩⟨Ei1
σ|
{
+ ˆUres, (30)
where ˆUres denotes an arbitrary unitary operation that
completes ˆUi1 to a unitary operation in the entire Hilbert
space. These are similar to the one-mode corrections,
except that they involve creating states that are entan-
gled between the two modes. This is realizable using
an experimental setup where one can generate entan-
glement between the modes and has suﬃcient separate
unitary control on the individual modes. However, they
are likely to have lower ﬁdelity than the equivalent one-
mode operations. See Appendix G for a speciﬁc hard-
ware proposal where two cavities (or cavity modes) are
dispersively coupled to a common transmon qubit with
ˆHdisp/ℏ =∑2
j=1χjˆa†
jˆaj ˆσz, where ˆaj is the annihilation
operator for the jth mode. If the dispersive couplings
are ﬁne-tuned to be equal χ1 = χ2, then the codes
of Eq. (27) form a decoherence-free-subspace [ 67, 68]
with respect to qubit excitation induced dephasing er-
rors exp(−χ(ˆn1 + ˆn2)τ) where τis unknown. In practice
high-precision ﬁne-tuning of χj is hard to achieve and one
needs to correct dephasing errors with higher-order codes
similar to the single-mode binomial codes.
As in the single-mode code, the ﬁdelity of the error
correction is determined by the rate of uncorrectable
errors [77] and for small κδtthis is dominated by two-
photon losses. There are three paths for two-photon loss
from the states of the two-mode code, Eq. (28), compared
to one path for the one-mode code, Eq. (2). Assuming
equal κ, the rate of two-photon losses via each path is
the same, so the rate of uncorrectable errors for the two-
mode code is three times larger than the one-mode code.
Which code is preferable will depend on the ﬁdelity of the
no-jump correction for the one-mode code, as the need for
this operation is eliminated in the two-mode case. More
generally, for unequalκ, there will be a no-jump evolution
of the form exp(−1
2(κ1ˆn1+κ2ˆn2)δt) which one would have
to deal with using a similar no-jump correction procedure
as described for the binomial codes.
B. Cat codes
The binomial codes are similar to existing cat codes [16–
19]. Cat codes are also approximate quantum error cor-
rection codes for a damped bosonic mode and consist of
superpositions of well-separated coherent states, “legs”,
evenly distributed in a circle in phase space. Cat codes
with 2(L+1) legs protect against L photon losses, and are
related to the binomial codes with spacingS =L. In both
cases, the diagnosis of errors is performed by measuring
the photon number modulo S + 1. The four-legged cat
code [ 18] protects against single photon losses, and so
is similar to the class of binomial codes with L = 1, of
which the simplest case is Eq. (2). The two logical cat
code words are superpositions of coherent states|±β⟩and
|±iβ⟩,
|Cβ
↑/↓⟩= 1√Z↑/↓
(|β⟩±|iβ⟩+|−β⟩±|−iβ⟩)
= 1√Z↑/↓
[0,∞)∑
p even/odd
∫
e−|β|2β4p
2p!|2p⟩. (31)
The normalization factors Z↑/↓become equal as |β|→
∞. In this limit, the cat codes satisfy ⟨Cβ
↓|ˆnp|Cβ
↓⟩=
⟨Cβ
↑|ˆnp|Cβ
↑⟩for allp, so that in the notation of Eq. (7) cat
codes have N→∞, giving potential protection against
dephasing errors to unlimited order, see Fig. 1. The dif-
ference in normalization constants for diﬀerent cat states
means that the approximate quantum error correction
conditions Eq. (22) are not exactly satisﬁed for generic
values of|β|2:
⟨Cβ
↓|ˆE†
1 ˆE1|Cβ
↓⟩−⟨Cβ
↑|ˆE†
1 ˆE1|Cβ
↑⟩
≃κδt(⟨Cβ
↓|ˆn|Cβ
↓⟩−⟨Cβ
↑|ˆn|Cβ
↑⟩)
≃4κδt|β|2e−|β|2(
sin|β|2 + cos|β|2{
, (32)
where the second approximation neglects termsO(e−2|β|2
).
Similar expressions, with diﬀerent trigonometric functions,
can be found for the higher order Kraus operators. When
the right hand side of Eq. (32) is nonzero, the cat code
is subject to uncorrectable errors O(κδt), which are sup-
pressed by increasing the separation parameter β, at the

## PDF page 11

11
cost of increasing the average photon number and hence
the error rate. Notice in comparison that the binomial
codes with S = 1 exactly suppress all photon loss errors
to ﬁrst order in κδt.
The Fock state distributions of the binomial and cat
codes are binomial and Poissonian, respectively. As the
average number of photons is increased (largerN), both of
these distributions approach a normal distribution, and so
the binomial and cat codes asymptotically approach each
other. Similarly, the qudit binomial codes approach qudit
cat encoding [ 19] since the extended binomial coeﬃcients
also approach the normal distribution [75].
By construction, a photon jump event transforms one
cat state into another cat state. To the order that the
approximate quantum error conditions (22) are satisﬁed,
the quantum information is preserved and, as long as pho-
ton jumps are detected and recorded, there is no further
correction needed. Since no-jump evolution damps co-
herent states, e−κδtˆn|β⟩=|e−κδtβ⟩e−κδtˆn|β⟩=|e−κδtβ⟩,
the only necessary correction is a “re-pumping” of the
cat states. This can be achieved using a discrete unitary
correction operation (analogous to the binomial codes)
or continuous non-linear ampliﬁcation coming from an
engineered reservoir [ 17, 18] (analogous to similar pas-
sive/autonomous error correction schemes [ 94, 95]). The
basic principle of passive schemces is stabilization of a
manifold of codewords as an attractive (stable) ﬁxed-point
of drives and dissipation so that the only remaining task
is to track generalized parity for photon jumps [ 18]. The
cat codes based on equal amplitude coherent state su-
perpositions, cf. Eq. (31), are ‘natural’ candidates for
these purposes since they require only gradual continuous
inversion of the damping of the coherent state amplitude
without active discrete correction stages. The two-leg
cat has already been stabilized by reservoir engineering
to achieve dominant two-photon drive and two-photon
dissipation [96].
The single-mode binomial codes require an explicit
correction gate at every timestep whether or not a photon
jump has occurred. However, binomial codes satisfy the
approximate quantum error correction conditions to order
δtwith a smaller average photon number: ¯n = 2 for the
code of Eq. (2), rather than ¯n≈2.3 for the cat code that
minimizes Eq. (32). Furthermore, the binomial codes
operate in a restricted Hilbert space, which could be
beneﬁcial for the practical construction of the unitary
operators required for error diagnosis and recovery. This
particularly applies to errors involvingˆa†operators, whose
operation on cat codes is less straightforward than ˆa
operators alone.
C. Permutation-invariant codes
The deﬁnition of our codes, Eq. (7) has the same struc-
ture as the permutation-invariant codes, deﬁned for M
qubits [83, 84]:
|PI↑/↓⟩= 1√
2N
[0,N+1]∑
p even/odd
∫(N + 1
p
{
|DM
(S+1)p⟩, (33)
where the Dicke state|DM
n⟩is symmetric superposition
of all permutations of n up spins and M−n down spins,
e.g.|D3
1⟩∝|100⟩+|010⟩+|001⟩in the notation of Sec. I.
Note that the similarity in structure is the same only for
qubit code words; the qudit extension of the permutation-
invariant codes [84] is diﬀerent from ours.
Although the deﬁnition of these codes in terms of excita-
tion number take the same form, the physical and math-
ematical distinctions between the single mode bosonic
oscillator and the many-qubit system distinguishes the
goals and behavior of the two codes. The connection
with the bosonic system can be identiﬁed by taking the
M →∞limit of permutation invariant codes. Then,
by the Holstein-Primakoﬀ transformation [ 97], the col-
lective “giant-spin” subspace of Dicke states with total
spin M/2→∞becomes equivalent to a bosonic system.
Using this mapping, we can identify several important
diﬀerences between the bosonic and qubit code construc-
tions. First, while in the spin system it is important to
consider errors acting on the individual qubits [ 83], the
errors in the bosonic system map to only the giant-spin
operators, symmetric superpositions across all the qubit
operators, e.g.
ˆa∼lim
M→∞
1√
M
ˆΣ−= lim
M→∞
1√
M
M∑
i=1
ˆσ−
i , (34)
where ˆσ−
i is the spin lowering operator for the ith spin.
In addition to the restriction to symmetric errors, the
physical asymmetry between bosonic errors, e.g. ˆa and
ˆa†makes it reasonable to consider a smaller set of errors,
e.g. ¯E =
{ˆI, ˆa
}
, than the qubit case, where being able to
correct any qubit error, i.e.E =
{ˆIq, ˆσ−, ˆσ+, ˆσz
}
, is more
natural. Finally, taking the M→∞limit signiﬁcantly
simpliﬁes the action of the error operators:
1√
M
ˆΣ−|DM
n⟩=
√
n(M−n + 1)
M |DM
n−1⟩,
M→∞
−−−−→√n|DM
n−1⟩.
(35)
The suppression of then2 term in the largeM limit signif-
icantly simpliﬁes the satisfaction of the QEC conditions.
As a result, the bosonic system has considerable addi-
tional ﬂexibility in the construction of QEC codes, with
concomitant performance gains. For example, for ﬁnite
M there is no equivalent of our smallest code, Eq. (2) in
the permutation invariant codes. In general, the average
excitation number in a code that corrects L excitation
losses scales as L2/2 for bosonic binomial codes compared
with 3L2/2 in the permutation-invariant codes [83].

## PDF page 12

12
D. GKP codes
While all codes discussed so far are deﬁned using a dis-
crete (i.e., countable) basis, the Gottesman, Kitaev, and
Preskill (GKP) codes [ 13] are deﬁned using the continu-
ous basis of non-normalizable eigenstates of the position
operator ˆx. A unique resulting feature of GKP codes is
that the correctable errors themselves form a continuous
set. The simplest ideal qubit GKP words are
|GKP↑/↓⟩∝
(−∞,∞)∑
p even/odd
ˆD
(
p
√π
2
{
|ˆx = 0⟩, (36)
where ˆD is the displacement operator from Eq. (10) and
|ˆx = 0⟩is the starting position eigenstate. In position
space, such states are inﬁnite combs of position eigenstates
spaced 2√πapart, so the eﬀective spacing between the
two logical states is S =√π. The same result holds in
momentum (ˆp) space via Fourier transform of Eq. (36).
Naturally, all position and momentum shifts e −iuˆpeivˆx
with|u|,|v|≤√π/2 are correctable. However, the GKP
codes can also correct any error operators expandable
in the basis of correctable shifts. Careful expansion of
photon loss ˆa and other errors [ 20] has conﬁrmed that
GKP codes can in principle ( i.e., for small enough κδt)
correct photon loss, gain, and dephasing errors.
The ideal GKP code words (36) contain both an inﬁ-
nite number of photons and states which are perfectly
squeezed in the ˆx quadrature. To make the codes exper-
imentally realizable, the superposition in Eq. (10) has
to be ﬁltered (to keep the photon number ﬁnite) and a
distribution of states has to be substituted for the sharp
|ˆx = 0⟩state (to account for imperfect squeezing). In the
traditional form of the approximate codes, a p-dependent
Gaussian ﬁlter is put into the sum in Eq. (36) and a Gaus-
sian wavepacket is substituted for|ˆx = 0⟩. However, the
choice of ﬁlter and starting state can be arbitrary. There
are a handful of theoretical proposals [ 98–100] (see also
Ref. [101] for an error analysis of GKP states), including
one based on a clever use of phase estimation [ 20], to re-
alize such approximate GKP states. GKP states are also
useful in designing highly precise gates for other quantum
computing architectures [102].
The approximate code words are not perfectly orthogo-
nal, so one must take into account the error coming from
the non-orthogonality. Since the ideal GKP states have in-
ﬁnite photon number, the approximate GKP states must
contain a suﬃciently high number of photons in order to
manage such imperfections. An optimistic [ 20] estimate
for this photon number is ¯n = 4, which uses the tradi-
tional form of the approximate code words and bounds
the error probability coming from the non-orthogonality
at about 1% (Eq. (38) of Ref. [ 13]). Using the same
approximate code words, a photon number of 2 implies
a 9% error bound. As a result, the traditional form of
the approximate code words is expected to contain more
photons than, e.g., the smallest (¯n = 2) binomial code (2).
However, the GKP code words can protect against a larger
set of errors than the minimal binomial code. Due to the
various choices of starting state and ﬁlter as well as due
to the diﬃculty of comparing continuous correctable error
sets to discrete ones, a detailed comparison of the relative
capabilities of the GKP and binomial/cat classes of codes
remains to be done.
VI. APPLICATIONS IN QUANTUM
COMMUNICATION
Aside from improving lifetimes of quantum memories
and quantum bits, bosonic mode quantum error correction
is also useful for quantum teleportation [ 103, 104] and
quantum communication, which consists of quantum state
transfer and generation of high-ﬁdelity entangled pairs of
quantum bits between two distant nodes in a quantum
network. We consider here a primitive task, namely the
‘pitch-and-catch’ scenario [24, 25, 105] for quantum state
transfer which can be used for quantum repeaters [ 106,
107]. The scenario consists of (see Fig. 3) initialization of
qubit A into a superposition of the ground and excited
state, encoding this superposition into the logical code
words of the send cavity via a unitary swap operation,
letting the cavity state leak in a time-reversal symmetric
manner (‘pitch’) into a transmission line or to other kind of
a ﬂying oscillator mode such that the inverse process into
the receiving cavity (‘catch’) is most eﬃcient [105, 108].
The transfer is ﬁnalized by decoding the received cavity
state via a unitary swap operation to the qubit B. The full
process corresponds to a quantum state transfer between
the qubits through the modes. The remote physical qubits
can be entangled by using the same protocol with the
ﬁrst swap operation being replaced with a CNOT-gate
between the physical qubit A and the logical qubit of the
cavity.
The overall process is vulnerable to various errors and
inﬁdelities at the diﬀerent stages of the transfer pro-
cess [109]. The most obvious imperfection is the attenua-
tion of the state of the ﬂying oscillator mode caused by
the photon loss processes, similar to Eqs. (13-15), during
the transmission. A crucial part of the ‘pitch-and-catch’
process is the engineering of the temporal and spatial
mode of the ﬂying oscillator [ 24, 25, 110–112] so that
the catch by the receiving cavity is as reﬂection less as
possible, but this is unlikely to be perfect. The pitching
process can also include a conversion from microwave to
optical domain or between diﬀerent microwave frequen-
cies [26, 113]. The ﬁdelity of the conversion itself can be
improved by using quantum error correction. In addition,
there can be errors in the encoding and decoding pro-
cesses between the qubits and cavities, as well the cavities
and the ﬂying oscillator mode can suﬀer the same loss
processes we have already discussed for applications to
quantum memories in Secs. I-III. If one uses the naive
encoding|W i
↑/↓⟩, all these error sources lead to unfaithful
quantum state transfer. When using the binomial code

## PDF page 13

13
Figure 3. (a) Sketch of a circuit QED hardware proposal and
(b) Schematic of a quantum state transfer scenario utilizing
quantum error correction for the binomial quantum code words.
First, the state of the qubit A is encoded in the send cavity S
using code words|W S
↑,↓⟩. The state in S is allowed to leak into
the ﬂying oscillator mode F (‘pitch’). By controlling the cavity
decay rate, one can precisely tune a time-reversal symmetric
temporal mode such that the quantum information is fully
absorbed in the receiving cavity R (‘catch’). Before decoding
the received cavity state to the qubit B, the ﬁdelity of the
transfer process can be improved by a round of QEC in the
received cavity state.
words or other quantum codes [ 114] as the logical code
words in the cavities and in the transmission, the ﬁdelity
can be increased by performing a recovery process on the
received cavity state before decoding it to the receiving
qubit B. This way one can improve the ﬁdelity of the pro-
cess by removing the eﬀect of the correctable errors (6)
from the full process. The performance of the diﬀerent bi-
nomial codes can be estimated similarly as in Sec. IV and
Fig. 2 but considering e.g. transmission inﬁdelity instead
of the photon loss probability κδtduring a timestep.
VII. CONTROLLING A LOGICAL QUBIT
IN A CAVITY
In addition to their use for quantum memories and
communication, it would be beneﬁcial if the encoded qubit
state could be unitarily controlled to perform quantum
computation. A naive way to realize single-qubit rotations
would be to decode the cavity state back into an ancilla
qubit, rotate the qubit and then re-encode the state into
the cavity. This is not optimal since the decoherence rate
of the ancilla is higher than that of the cavity [35, 44].
Using optimal control pulses [ 43, 44, 49, 50] it should
be possible to directly realize an arbitrary unitary on the
cavity while minimizing the eﬀects of the short ancilla
lifetime. For example, for the binomial code with S =
N = 1 [see Eq. (2)], the unitary corresponding to a Z gate
is
ˆZ =|W↑⟩⟨W↑|−|W↓⟩⟨W↓|+ ˆUres
=|0⟩⟨0|−|2⟩⟨2|+|4⟩⟨4|+ ˆU′
res. (37)
On the last line we have explicitly written a particular
choice of the action of ˆUres on the non-code-word state
|E0
↑⟩. ˆU′
res completes the remainder of the unitary opera-
tion. The phase gate inherits the diagonal nature of the
Z gate of Eq. (37):
ˆθ= e−iθˆZ
2
=|0⟩⟨0|+ eiθ|2⟩⟨2|+|4⟩⟨4|+ ˆUres. (38)
The structure of the X gate is
ˆX =|W↓⟩⟨W↑|+|W↑⟩⟨W↓|+ ˆUres
= 1√
2 (|2⟩⟨0|+|2⟩⟨4|+ h.c.) + ˆUres, (39)
where the functional part is an addition of 2 mod 4 pho-
tons in the even photon number manifold of max 4 pho-
tons. The diﬃculty of achieving such unitaries is on the
same scale as the gates needed to perform the encoding of
the initial state. Consequently, the universal control of a
binomial logical qubit is achieved with the same resources
as the quantum error correction itself.
Joint conditional and entangling operations on two log-
ical qubits would additionally require an entangling gate
between the logical qubits. In Appendix G, we analyze a
hardware proposal where this would be possible. Progress
is already underway in this direction with the recent ex-
perimental demonstration of ‘a cat in two boxes’ [ 43]
which used complex entangling operations between two
cavities.
VIII. DISCUSSION
So far we have considered code words constructed from
Fock state superpositions with a deﬁnite generalized pho-
ton number parity, resulting in the code word spacing S.
This spacing readily implies a diagonal quantum error
correction matrix for photon loss and gain errors. By
relaxing the parity structure we can ﬁnd codes with
even lower rates for uncorrectable and correctable er-
rors. However, the recovery process for these optimized
codes involves more complicated measurements whose ex-
perimental ﬁdelity is expected to be lower than that of the
relatively straightforward parity measurements. We have
searched for optimized codes by minimizing the largest
uncorrectable error rate, the rate PL+1/δtof losing L + 1
photons. Using this method we have found analytic and
numerical codes with reduced rates for correctable and
uncorrectable errors, some of which we were then able
to transcribe analytically. As with the binomial codes,
these optimized codes are exactly protected against L

## PDF page 14

14
photon losses, implying that they are approximate quan-
tum error correction codes for the photon loss channel on
accuracy of (κδt)L; see Appendix H for details.
The recovery that is presented in Sec. III for the bino-
mial codes is not the optimal recovery; it is merely an
example of a recovery process to the desired accuracy. Ad-
justments of the recovery process cannot beat the overall
accuracy limit set by the code itself, but the prefactors
of the higher-order terms in the inﬁdelity can be made
considerably smaller. A simple way of making an improve-
ment in the sub-leading terms of the inﬁdelity is to add to
the recovery operations a unitary ‘echo’ operationˆUx that
performs state transfer |W↑⟩↔|W↓⟩: ˆR′
ℓ= ˆUx ˆRℓ. The
eﬀect of this is a partial recovery of classical information
from uncorrectable, higher order errors. In general, the
optimal code can be found simultaneously improving both
the code and the recovery processes—a procedure that
may require numerical optimization [79, 92].
The binomial and the optimized codes have several
appealing features compared to the two-mode codes [ 12]
and the cat codes [ 16–19] including smaller rates for cor-
rectable and uncorrectable errors, protection against pho-
ton gain and dephasing errors. It is noteworthy that our
codes operate in a restricted Hilbert space and this may
be a practical advantage in designing unitary controls (in
contrast to, for instance, the cat codes made out of coher-
ent states). To achieve the full performance advantage
provided by the features of the binomial codes one needs
to perform sophisticated high-ﬁdelity unitary control at
a high rate. Low-ﬁdelity unitary control favors codes
with less frequent measurements and unitary operations
which favors cat codes and two-mode codes. The bino-
mial and the optimized codes outperform the cat codes
and two-mode codes when the performance beneﬁt is
larger than the diﬀerence in the total inﬁdelity of the uni-
tary control between the codes. Current superconducting
technology [42–44] is on the verge of this transition.
IX. CONCLUSIONS
We have presented a new class of ‘binomial’ quantum
error correction codes for a bosonic mode. By constructing
an explicit recovery process, we demonstrated that the
binomial codes are protected to given order in the timestep
against continuous dissipative evolution under loss, gain
and dephasing errors. Therefore, any errors which can be
expanded in terms of the creation/destruction operators
of the bosonic mode can be corrected to arbitrary order.
The performance of the codes is characterized by the
largest rate of uncorrectable errors (e.g., the rate of losing
L + 1 photons for a code protecting against L photon
losses). Ignoring the inﬁdelity of the recovery process, our
analysis showed that with timestep δt≲ 0.4/κ, where κ
is the photon loss rate, the naive encoding in Fock states
|0⟩and|1⟩is outperformed by the smallest binomial code.
For even smaller timesteps, higher-order binomial codes
become preferable. Inﬁdelities in the recovery process
favor lower-order binomial codes.
The binomial code words consist of superpositions of
equally spaced number eigenstates and are therefore eigen-
states of a generalized parity. As a result, detection of
loss and gain errors can be performed by measuring this
generalized parity. More generally, the binomial codes,
cat codes [ 16–19] and Gottesman-Kitaev-Preskill (GKP)
codes [13], share this type of structure. Namely, the logical
state pairs of all three codes can be thought of as inter-
leaved combs of eigenstates of some operator (the photon
number operator for binomial/cat codes and the oscilla-
tor position operator for GKP codes) whose coeﬃcients
are related to a distribution (the binomial, Poisson, and
Gaussian in the case of the binomial, cat, and GKP codes,
respectively). Comparison with GKP codes suggests that
it would be useful to identify commuting operators (sta-
bilizers) for detecting errors for the binomial codes [ 115].
We leave this for a future work.
The generalized parity structure is a rather strong re-
striction on the code words and we show in Appendix H
that, for codes built out of number operator eigenstates,
better ideal performance is achieved by relaxing this struc-
ture. In future work it would be very interesting to ﬁnd
more examples of such codes and understand the struc-
ture of these optimized bosonic codes. Taken together, we
foresee that the binomial codes and their relatives will im-
prove the ﬁdelity of quantum memories, communication
and scalable computation based on bosonic modes.
ACKNOWLEDGMENTS
We are grateful for useful discussions with Huaixiu
Zheng, Reinier W. Heeres, Philip Reinhold, Hendrik
Meier, Linshu Li, John Preskill, N. Read, Konrad W.
Lehnert, Mazyar Mirrahimi, Barbara M. Terhal, Michel
H. Devoret and Robert J. Schoelkopf. We acknowledge
support from the Yale Prize Postdoctoral Fellowship,
ARL-CDQI, ARO W911NF-14-1-0011, W911NF-14-1-
0563, NSF DMR-1301798, DGE-1122492, AFOSR MURI
FA9550-14-1-0052, FA9550-14-1-0015, Alfred P. Sloan
Foundation BR2013-049, and the Packard Foundation
2013-39273.
Appendix A: Conditional unitary control of the
binomial code recovery process
We summarize here the required conditional unitary
control for the recovery of the binomial codes under the
photon loss channel. As described in Sec. I-III, the bino-
mial codes are tailored so that the photon loss errors are
detected by measuring changes in the generalized photon
number parity that serves as a proxy for the number of
lost photons in a short timestepδt. With superconducting
circuit QED technology the ability to straightforwardly
measure photon number parity stems from the strong
dispersive coupling of an ancillary qubit to the cavity

## PDF page 15

15
ˆHdisp/ℏ =χˆσzˆa†ˆa. In the strong-dispersive limit, where
the strength of the dispersive coupling χis greater than
the decay rates of the qubit and the cavity, one can drive
the qubit conditioned on given photon number states of
the cavity [116, 117]. This can be then used for photon-
number conditioned qubit operations, such as ﬂipping the
qubit state conditioned on the generalized photon parity
ˆΠk modL+1 =∑[0,∞)
ℓ=k modL+1|ℓ⟩⟨ℓ|:
ˆUk modL+1 = ˆσx ˆΠk modL+1 + ˆIq
(ˆI−ˆΠk modL+1
{
, (A1)
where ˆσx is a Pauli matrix and ˆIq the identity operator
for the qubit. After this operation ˆUk modL+1, the mea-
surement of the qubit state realizes measurement of the
generalized photon parity and projection of the cavity
state by ˆΠk modL+1.
Error detection is followed by a correction unitary ˆUk,
Eqs. (23-24), that performs a state transfer between the
error words|Bk
σ⟩and the logical code words |Wσ⟩. The
exact form of the correction unitary ˆUk depends on the
parameters of the binomial code, Eq. (20). In the strong
dispersive limit, individual qubit and cavity drives are
enough for implementing any unitary on the cavity [41–44],
see also Appendix G. The unitary correction applied to the
cavity state can be combined with the initial conditioned
unitary (A1)
ˆU′
k modL+1 = ˆσx ˆUk ˆΠk modL+1 + ˆIq
(ˆI−ˆΠk modL+1
{
,
(A2)
which, followed by a qubit measurement, implements the
Kraus operator ˆRk = ˆUk ˆΠk modL+1 of the recovery in
Eq. (25). Repetition for all of the values of k realizes the
full recovery processR ={ˆUk ˆΠk modL+1}.
Appendix B: Moments of ˆn for the binomial codes
Here we show from Eq. (7) that the expectation value
of certain moments of the photon number operator ˆn are
identical for both code words |W↑/↓⟩. In other words, we
show that
⟨Wσ|ˆnℓ|Wσ⟩=αℓ, for 0 ≤ℓ≤max{L,G}(B1)
and for some real σ-independent αℓ. The ℓ= 0 case
conveniently takes care of orthonormality between the
code words while the ℓ̸= 0 conditions guarantee that
the the words can be corrected from various errors (up
to the relevant order). In Appendix C, we extend the
deﬁnition (7) to qudits and perform a similar proof for
moments of the qudit code words.
To prove Eq. (B1), we show that the diﬀerence of the
moments of|W↑⟩and|W↓⟩,
∆ ℓ≡⟨W↑|ˆnℓ|W↑⟩−⟨W↓|ˆnℓ|W↓⟩, (B2)
is zero. Using deﬁnition (7), the diﬀerence between the
even and odd populated words is
∆ ℓ= (S + 1)ℓ
2N
N+1∑
p=0
(N + 1
p
{
pℓ(−1)p . (B3)
For ℓ= 0, the sum is equivalent to a binomial expan-
sion of (1 + x)N+1 with x =−1 (which is clearly zero).
The nonzero ℓcase is equivalent to taking derivatives
of the binomial expansion and multiplying by x (before
substituting x =−1). This is because each action of the
derivative brings down a power of p while multiplication
byx brings xp−1 back to xp. In total,
∆ ℓ= (S + 1)ℓ
2N
(
x d
dx
{ℓ
(1 +x)N+1
⏐⏐⏐⏐⏐
x=−1
. (B4)
Each action of the derivative acting on (1 + x)N+1 sub-
tracts one from the power N + 1. Since ℓ≤max{L,G},
the largest subtracted power is max{L,G}. However,
since N = max{L,G, 2D}(where D accounts for dephas-
ing errors and is not relevant here), there will always be a
nonzero power of 1 + x after the action of the derivative.
Therefore, the expression (B4) is a polynomial in x and
1+x containing only nonzero powers of 1+x. Substituting
x =−1 into that polynomial yields ∆ ℓ= 0.
An alternative basis for the binomial codes of Eq. (7)
can be achieved by taking a normalized sum and diﬀerence
of the code words |Wσ⟩,
|˜W↑/↓⟩≡
N+1∑
p=0
(±1)p
√
2N+1
∫(N + 1
p
{
|(S + 1)p⟩. (B5)
In this basis it is obvious that the moments of ˆn are equal
since the number distributions are identical. What is not
obvious is the fact that ⟨˜W↑|ˆnℓ|˜W↓⟩= 0. The proof is
similar to the equal moments in the above case.
Appendix C: Extended binomial qudit codes
We extend the above qubit states to the qudit case
using extended binomial coeﬃcients (see [ 74, 75] and refs.
therein; these are also called polynomial coeﬃcients [ 76]).
Letting d≥1 be the dimension of the logical qudit space,
we deﬁne extended binomial coeﬃcients recursively, start-
ing from the ordinary binomial coeﬃcients. Deﬁning(n
m
{
1≡1 and
(n
m
{
2≡
(n
m
{
for non-negative integersn and
m, the extended binomial coeﬃcients are
(n
m
{
d
≡
n∑
k=0
(n
k
{( k
m−k
{
d−1
. (C1)
These are the coeﬃcients of powers of x in the expan-
sion [76]
(
1 +x +...+xd−1{n
=
(d−1)n∑
k=0
(n
k
{
d
xk. (C2)

## PDF page 16

16
Notice that the largest power of x in such an expansion is
(d−1)n, which reduces to n for the well-known binomial
case. The last ingredient necessary to generalize to qudits
is the generalization of (1 +x)n|x=−1 = 0 used in the
proof above. For this, we introduce the dth root of unity
w≡exp(i 2π
d ) and recall that adding all powers of w from
zero tod−1 gives zero. This reveals a set of identities use-
ful in deﬁning and proving the error correction properties
of the qudit states:
0 =
(
1 +w +...+wd−1{n
=
(d−1)n∑
k=0
(n
k
{
d
wk. (C3)
This sum is also zero for any nonzero power of w, i.e.,
w→wl for nonzero integer l. For the zeroth power, the
sum gives dn.
We now generalize the binomial code words of Eq. (B5)
to
|˜Wµ⟩≡
(d−1)(N+1)∑
p=0
wµp
√
dN+1
∫(N + 1
p
{
d
|(S + 1)p⟩,
(C4)
where the indices µ,ν∈{0, 1,...,d−1}are from now on
evaluated modulo d and d≥2. Similar to the qubit case,
S =L +G andN = max{L,G, 2D}. We call these codes
‘extended binomial codes’ as they are not to be confused
with quantum polynomial codes [118].
1. Moments of ˆn for the extended binomial codes
Similar to the qubit case, it should be clear that the
spacingS + 1 between the nonzero Fock state populations
of|˜Wµ⟩guarantees that ⟨˜Wµ|(ˆa†)ℓˆaℓ′
|˜Wν⟩= 0 for all
|ℓ−ℓ′|<S + 1. Therefore, to satisfy the error correction
criteria, we are once again left with determining the pow-
ers of ˆn which can be used to construct any diagonal (in
Fock space) products of error operators. Here we show
that
⟨ˆnℓ⟩≡⟨˜Wµ|ˆnℓ|˜Wµ+ν⟩=αℓδν0, (C5)
where αℓare real and µ-independent. Using deﬁnition
(C4), we notice that
⟨ˆnℓ⟩= (S + 1)ℓ
dN+1
(d−1)(N+1)∑
p=0
(N + 1
p
{
d
pℓwνp (C6)
and the µ-dependence is immediately canceled. We now
relate this sum to Eq. (C2).
Forℓ= 0, the sum is equivalent to the expansion of
(1 +x +...+xd−1)N+1 with x = wν. Equation (C3)
reveals that this sum is zero unless ν= 0, proving that
{|˜Wµ⟩}d
µ=0 are orthogonal. For the ν= 0 case, wν= 1
and Eq. (C2) yields dN+1, proving that {|˜Wµ⟩}d
µ=0 are
properly normalized.
The nonzero ℓcase is equivalent to taking derivatives
of the expansion (C2) and multiplying by x (before sub-
stituting x =wν). In total,
⟨ˆnℓ⟩= (S + 1)ℓ
dN+1
(
x d
dx
{ℓ(
1 +x +...+xd−1{N+1
⏐⏐⏐⏐⏐
x=wν
.
(C7)
Similar to the ordinary binomial case, each action of the
derivative acting on (1 + x +...+xd−1)N+1 subtracts
one from the power N + 1, but N is large enough so that
there will always be a nonzero power of 1 +x +...+xd−1
remaining after the action of all derivatives. Therefore,
each term in Eq. (C7) contains at least one nonzero power
of 1 +x +...+xd−1. Substituting x =wνinto each term
yields zero unless ν= 0 and so Eq. (C5) holds.
The coeﬃcients αℓof Eq. (C5) for the ﬁrst few ℓcan
be easily determined from this method [76]:
α1 = (S + 1)
2 (d−1) (N + 1), (C8a)
α2 =α1
(S + 1)
6 [(d−1) (3N + 4) + 2]. (C8b)
The coeﬃcient α1 is the mean photon number of the
code words, which we see scales linearly with the spacing
S, the qudit dimension d, and the maximum number of
correctable errors of one type, N.
Appendix D: Derivation of the Kraus operators ˆEℓ
Here, we derive the Kraus operator representation
ˆρ(t) =
∞∑
ℓ=0
ˆρℓ(t) =
∞∑
ℓ=0
ˆEℓˆρ(0) ˆE†
ℓ (D1)
of the time evolution generated by the standard Lindblad
master equation
dˆρ=κdt
(
ˆaˆρˆa†−ˆa†ˆa
2 ˆρ−ˆρˆa†ˆa
2
{
. (13)
The zero-jump contribution consists of only the no-jump
evolution under the non-Hermitian Hamiltonian ˆV/ ℏ =
−iκ
2 ˆa†ˆa,
ˆρ0(t) = e−κt
2 ˆn ˆρ(0)e−κt
2 ˆn. (D2)
The single jump contribution ˆρ1(t) consists of the no-jump
evolution interrupted by a jump and averaged over all
possible jump times,
ˆρ1(t) =
∫t
0
κdτe−κ(t−τ)
2 ˆnˆae−κτ
2 ˆn ˆρ(0)e−κτ
2 ˆnˆa†e−κ(t−τ)
2 ˆn
=
(
1−e−κt{
e−κt
2 ˆnˆaˆρ(0)ˆa†e−κt
2 ˆn, (D3)
where κdτis the probability for a jump during dτ. We
have used the identity
exp (κδtˆn) ˆa exp (−κδtˆn) = ˆa exp (−κδt). (D4)

## PDF page 17

17
Similarly the double jump contribution is
ˆρ2(t) = (1−e−κt)2
2! e−κt
2 ˆnˆa2 ˆρ(0)(ˆa†)2e−κt
2 ˆn, (D5)
and the general term for ℓjumps is
ˆρℓ(t) = (1−e−κt)ℓ
ℓ! e−κt
2 ˆnˆaℓˆρ(0)(ˆa†)ℓe−κt
2 ˆn, (D6)
where we gather the analytic expression for the Kraus
operators
ˆEℓ=√γℓe−κt
2 ˆnˆaℓ=√γℓˆE0ˆaℓ=
√
γℓeℓκtˆaℓe−κt
2 ˆn. (15)
Here γℓ= (1−e−κt)ℓ/ℓ! is related to the probability of
the process ˆρ→ˆEℓˆρˆEℓ. When considering a small time
intervalδtand expanding ˆEℓto the lowest order in κδt,
we see that roughly speaking a photon loss error occurs
with a probability amplitude proportional to
√
κδt.
If this is a proper Kraus representation, it must obey
the identity relation∑∞
ℓ=0 ˆE†
ℓˆEℓ= ˆI. From Eq. (15) we
have
ˆΞ =
∞∑
ℓ=0
ˆE†
ℓˆEℓ=
∞∑
ℓ=0
(1−e−κt)ℓ
ℓ! (ˆa†)ℓe−κtˆnˆaℓ. (D7)
To see if this is the identity, we apply it to an arbitrary
Fock state|m⟩and recognize that the resulting binomial
expansion yields
ˆΞ|m⟩=
) m∑
ℓ=0
(1−e−κt)ℓ(e−κt)m−ℓ
ℓ!
m!
(m−ℓ)!
[
|m⟩
=
) m∑
ℓ=0
(
1−e−κt{ℓ(
e−κt{m−ℓ
(m
ℓ
{[
|m⟩
=|m⟩. (D8)
Since this is true for every m, the identity relation ˆΞ = ˆI
is indeed satisﬁed.
The Kraus operator expansion is not unique. This
particular form organizes the errors according to how
many photons are lost. Because of the no-jump evolution
in between the jumps, the error operator for ℓphoton
losses is ˆEℓand not simply ˆaℓ.
Appendix E: Lindblad evolution correctable by
binomial codes
Here we show how to ﬁnd binomial codes that may
be used to correct non-unitary Lindbladian evolution
generated by operators ˆAi of form
ˆAi =
∑
jk
ξ(i)
jk (ˆa†)jˆak, (12)
occurring with respective error rates κi. Some of this
discussion is similar to that given for a diﬀerent bosonic
encoding in Ref. [20]. For a suﬃciently small time interval
δt, the errors introduced by the dissipative evolution,
dˆρ=
∑
i
D(√κi ˆAi)ˆρdt, (E1)
whereD(ˆc)ρ= ˆcˆρˆc†−1
2{ˆc†ˆc, ˆρ}, can be expanded in the
parameters ϵi = κiδt. For each operator ˆAi, we can
specify that we wish to suppress all errors induced up
toO(ϵxi
i ) where xi can be interpreted as the maximum
number of ˆAi error events in the time interval δt.
The values ofϵxi
i may diﬀer betweenAi and, in general,
the time evolution involves mixtures of these operators.
To represent the diﬀerent combinations ofϵi that occur as
part of the correctable errors, we introduce the shorthand
O(γ) =O
(∏
i
ϵyi/2
i
(
, (E2)
where yi are any integers satisfying:
∑
i
yi
2xi
≤1. (E3)
To achieve this accuracy, the code words must satisfy the
QEC conditions under application of the time evolution
Kraus operatorsE ={ˆEk}to the appropriate order: [ 21]
⟨Wσ|ˆE†
ℓˆEk|Wσ′⟩=αℓkδσσ′+O(√ϵiγ), (E4)
where ϵi may be any of the expansion parameters.
In general, it is not possible to obtain a closed form
for the Kraus operators as in Appendix D. However, the
evolution during a time interval δtcan be unraveled into
diﬀerent quantum trajectories [ 85]. Then, for a given
trajectory, the system dynamics consists of continuous
no-jump evolution described by the operator:
ˆE0(t) = exp
(
−t
2
∑
i
κi ˆA†
i ˆAi
(
(E5)
and a sequence of jumps taken from the set of opera-
tors√κi ˆAi.
1. Jumps alone
Without the no-jump evolution, the sum over trajecto-
ries would produce sums over all possible products of the
jump operators√κi ˆAi, integrated over all possible jump
times in the interval δt, to give Kraus operators
ˆEk∼
∏
i
ˆOi, where ˆOi∈{√ϵi ˆAi}. (E6)
Here, we only need to consider Kraus operators that
are possible up to O(√γ), as any terms that are higher
order will produce errors that are beyond the desired

## PDF page 18

18
accuracy. Putting these operators into the approximate
QEC condition results in conditions of the form
⟨Wσ|
[√ϵi ˆA†
i
√ϵj ˆA†
j...
][√ϵk ˆAk
√ϵl ˆAl...
]
|Wσ′⟩∝δσσ′,
(E7)
where the operator combinations in each square bracket
can be any possible up to O(√γ). By normal ordering,
these conditions can be expressed as sums of terms like the
left hand side of Eq. (11). The normal ordering procedure
may produce operators that cannot be expressed as powers
of ˆAi. However, following the discussion beneath Eq. (11),
we only need to ﬁnd a binomial code that satisﬁes Eq.(E7)
for the terms with the worst-case ( i.e. largest) values of
either n+ =n−or|n+−n−|. All other terms, including
those that may be generated by normal ordering, then
also satisfy Eq. (E7) as a result of Eq. (11).
A binomial code that satisﬁes the worst-case instances
of Eq. (E7) can be found by choosing one that can correct
the highest order error operators:
ˆA′
i =
(√ϵi ˆAi
{xi
=ϵxi/2
i
∑
jk
ζ(i)
jk (ˆa†)jˆak. (E8)
The combinations ˆA′†
i ˆA′
j contain all the worst-case opera-
tors that appear in the conditions of Eq. (E7). We then
ﬁnd a binomial code that can correct this error following
the rationale below Eq. (12).
For example, consider the following (contrived) choices
of Ai and xi:
√ϵ1 ˆA1 =√ϵ1(ˆnˆa + ˆa†), x1 = 1. (E9a)
√ϵ2 ˆA2 =√ϵ2ˆa, x2 = 2, (E9b)
In this case, from Eq. (E2),O(γ) =O(ϵ1,ϵ2
2,√ϵ1ϵ2). Now,
ˆA′
1 = ˆA1 and
ˆA′
2 =ϵ2 ˆA2
2 =ϵ2ˆaˆa. (E10)
To correct Eq. (E10) we needL≥2,N≥2 and Eq. (E9a)
requires L≥1, G≥1 and N≥3. These conditions give
minimal choices ofL = 2,G = 1 andN = 3 for a binomial
code that can correct the errors (E9).
2. Including no-jump evolution
Including the no-jump evolution introduces instances of
the no-jump operator, Eq. (E5), between the individual
jump operators to give the behavior between jump times.
Since all these intervals are∼δt, the no-jump operator
can be expanded in terms that are∼ϵi, so that the Kraus
operators become
ˆEk∼
∏
i
ˆOi, where ˆOi∈{√ϵi ˆAi,ϵi ˆA†
i ˆAi}. (E11)
Since each instance of ˆAi or ˆA†
i still appears with a factor
of√ϵi, the largest combined total of ˆa and ˆa†operators
appearing in the ˆEk toO(γ) is unchanged by inclusion of
the no-jump evolution, and so the appropriate N can be
determined as in the previous section.
However, since the no-jump evolution introduces in-
stances of the operator conjugates ˆA†
i into the Kraus
operators, it can lead to new terms that change the num-
ber of excitations diﬀerently to evolution under jump
events alone. This will alter the required values of L and
G.
For example, consider the choice:
ˆA = ˆa + ˆaˆa, x = 2 (E12)
where the error rate κ=ϵ/δtso that the desired order of
correction isO(ϵ2). In the presence of no-jump evolution,
the set of Kraus operators includes:
ˆE0≈1 −1
2ϵ(ˆa†)2ˆa + (other terms), (E13a)
ˆE2≈ϵˆA2 =ϵ(ˆa4 + 2ˆa3 + ˆa), (E13b)
where we have omitted some terms that areO(ϵ) orO(ϵ2)
because such terms will automatically satisfy the QEC
conditions once we perform the analysis below. From the
analysis of the previous subsection, we would consider
only ˆA2, and conclude that we should use a code with
L +G = 4. However, putting the Kraus operators into
Eq. (E4), we ﬁnd:
⟨Wσ|ˆE†
0 ˆE2|Wσ′⟩=−1
2ϵ2⟨Wσ|ˆa†ˆa6|Wσ′⟩
+ (other terms). (E14)
A binomial code satisfying Eq. (11) for such a term re-
quires L +G = 5. The no-jump evolution introduces new
terms in the expansion of the QEC conditions that must
be included.
As in the above example, the worst-case instances are
introduced from terms of the form ( ϵi ˆA†
i ˆAi)⌊xi/2⌋. We
can then include them with the worst-case error set of
Eq. (E8):
{ˆA′
i}=
{
(√ϵi ˆAi)xi
}
∪
{
(ϵˆA†
i ˆAi)⌊xi
2⌋
}
. (E15)
One can now ﬁnd a binomial code that corrects these
errors, and as a result the non-unitary evolution to the
desired order, by expressing these operators in the form
of Eq. (12) and satisfying the binomial code conditions
for N, L and G.
For the example of Eq. (E12), we obtain:
{ˆA′
i}=
{
ϵ
(
ˆa4 + 2ˆa3 + ˆa2{}
∪
{
ϵ
(
ˆa†ˆn + ˆnˆa + ˆn2{}
,
(E16)
which yields the parameters L = 4, G = 1 and N = 4,
consistent with the above discussion.
We note that in many physical circumstances, either
ˆA†
i ˆAi =f(ˆn), in which case the no-jump evolution does
not change the number of excitations; or the error is Her-
mitian, in which case including no-jump evolution gives

## PDF page 19

19
expressions that are the same as Eq. (E7). In these situa-
tions, only the error set of Eq. (E8) need be considered.
For example, taking the operators from Eqs. (E9), we
obtain for Eq. (E15):
{ˆA′
i}=
{√ϵ1
(
ˆnˆa + ˆa†{
,ϵ2ˆaˆa
}
∪
{
ϵ2ˆa†ˆa
}
. (E17)
Using this error set results in the same conditions as found
without the no-jump evolution, Eqs. (E9) and (E10)
Appendix F: Performance of the binomial codes
under an unfaithful recovery process
In Sec. IV, we showed that the performance of a bi-
nomial code protected against L photon loss errors (7)
is well captured by the largest rate of the unrecoverable
errors, i.e., the rate of losing of L + 1 photons during a
timestep δt,
PL+1
δt =⟨ˆE†
L+1 ˆE†
L+1⟩
δt ∼κ(κδt)LLL+1, (26)
where for simplicity we have assumed that S =L. Prac-
tically, the recovery process is always associated with an
inﬁdelity related to unfaithful gates and imprecise mea-
surements. The total error rate PT can be approximated
by the sum of the largest unrecoverable error and the
inﬁdelityηof the recovery process:
PT
δt≃Nκ(κδt)LLL+1 + η
δt, (F1)
whereN is the prefactor of thePL+1 scaling. The optimal
timestep is δtopt = κ−1(
η/NLL+2{ 1
L+1 which balances
between minimizing the rate of unrecoverable errors and
the inﬁdelity of the recovery process itself. With this
optimal timestep, the best performance of an unfaithfully
recovered binomial code scales as function of ηas
P opt
T
δt≃κη
L
L+1 (1 +L)(NL)
1
L+1∼κηL. (F2)
The performance beneﬁt of higher order codes is achieved
only with small η.
Appendix G: Hardware proposal for the two-mode
codes
The two-mode codes [ 12] or the universal control of
two binomial logical qubits encoded in diﬀerent individual
modes could be realized using two separate modes in the
same cavity or using a recently constructed system [ 43] of
two cavities dispersively coupled to a common transmon
qubit that is used to perform unitary operations on the
combined cavity system (see also a related hardware pro-
posal in Ref. [ 18]). Implementation requires the ability to
perform the necessary measurement and error correction
operations on the two cavity modes, ˆaj, j = 1, 2. Here
Figure 4. Sketch of a two-cavity conﬁguration with a disper-
sively coupled common transmon qubit [43], which is suﬃcient
for realizing the two-mode codes. Each of the elements has
a separate drive, denoted by εj and⃗ n, respectively. Alterna-
tively, one could use two distinct modes of the same cavity.
we show that the single-qubit, two-cavity experimental
conﬁguration, Fig. 4, is in principle suﬃcient to realize
universal control of the two modes.
The dispersive coupling Hamiltonian is of the form
ˆHdisp/ℏ =∑2
j=1χjˆa†
jˆaj ˆσz, where ˆaj is the annihilation
operator for the jth mode. Additional Hamiltonian terms
come from drives on the cavities, ˆHj,d/ℏ = ε∗
j ˆa +εjˆa†
and the qubit ˆHQ/ℏ = ⃗ n·⃗ σ, where the εj and ⃗ nare
externally controlled. The existing Hamiltonian terms
can generate a more complex eﬀective Hamiltonian using
the approximate identities [3]:
ei ˆAδtei ˆBδtei ˆBδtei ˆAδt= e2i( ˆA+ ˆB)δt+O(δt3), (G1a)
e−i ˆAδte−i ˆBδtei ˆAδtei ˆBδt= e[ ˆA, ˆB]δt2
+O(δt3). (G1b)
These identities can be applied and combined multiple
times to produce superpositions of higher order commu-
tators, e.g. [ ˆA, [ ˆA, ˆB]] [3].
To establish universal control of the multimode system,
it is suﬃcient to show that each mode can be universally
controlled, and that it is possible to generate a beamsplit-
ter interaction ˆxj ˆpk−ˆxk ˆpj (equivalent to ˆajˆa†
k + ˆa†
jˆak)
between diﬀerent modes j̸=k [119]. Using the identity
Eq. (G1b), the cavity drives along with the dispersive
interaction generate eﬀective, qubit-dependent drives on
an individual cavity:
i ˆHj,eﬀ =
[
εjˆaj−ε∗
j ˆa†
j, i
2∑
k=1
χkˆa†
kˆakˆσz
]
= iχj ˆσz
(
εjˆaj +ε∗
j ˆa†
j
{
. (G2)
Choosing εj to be real or imaginary results in eﬀective
operators∝ˆpj ˆσz or ˆxj ˆσz. Combining these with pre- and
post-rotations of the qubit yields, e.g. ˆxj ˆσy. Applying
Eq. (G1b) again enables the construction of products of
the mode operators [120], for example:
[iˆxj ˆσy, iˆxkˆσz] = iˆxj ˆxkˆσx, (G3a)
[iˆpj ˆσy, iˆpkˆσz] = iˆpj ˆpkˆσx, (G3b)
[iˆxj ˆσy, iˆpkˆσz] = i(ˆxj ˆpk + ˆpkˆxj)ˆσx. (G3c)
Using Eq. (G1a) to sum Eqs. (G3a) and (G3b) withj =k
gives a single-mode dispersive interaction, which in com-
bination with external cavity drives is enough to produce

## PDF page 20

20
single-mode universal control [41]. Superposing Eq. (G3c)
with the same term with the opposite sign and j↔k
produces the beamsplitter interactions that are suﬃcient
to give universal control of the multimode system [ 119].
For practical applications, having additional, separately
controlled, qubits inside each cavity may simplify the con-
trol pulses, but as this proof demonstrates, in principle
they are not necessary.
Appendix H: Optimized bosonic codes
The performance of a binomial code protected against
loss of L photons is dominated by the rate of losing L + 1
photons, that is, the largest rate of uncorrectable errors.
As noted in Sec. IV, this rate scales quite unfavorably.
This is the cost of the sparse and tidy structure of the
binomial codes; the occupied Fock states of the code
words have deﬁnite generalized photon number parity
{|k⟩|k = 0 mod L + 1}. It is expected that by relaxing
this Fock state structure we can improve the intrinsic
performance of the code and pay a price in ﬁdelity of the
recovery process as the error detection and recovery will
need more sophisticated unitary control.
Here we follow the construction that we used for the
binomial codes: we ﬁrst ﬁnd exact satisfaction of the
quantum error correction criteria for the discrete photon
loss errors≤L times and then demonstrate that we can
ﬁnd a recovery process for the continuous-time photon
loss channel to accuracy (κδt)L. In practice, we ﬁnd code
words|Wσ⟩that simultaneously minimize the dominating
term of the rate for losing L + 1 photons,
PL+1
κδt= Tr
[
ˆaL+1 ˆρc(ˆa†)L+1]
(L + 1)! (κδt)L, (H1)
where ˆρc is the fully mixed state of the code words
|Wσ⟩, and satisfy the constraints of the quantum error
correction criteria (1) for the discrete error set ¯EL =
{ˆI, ˆa, ˆa2,..., ˆaL},
⟨Wσ|ˆE†
ℓˆEk|Wσ′⟩=αℓkδσσ′, (1)
for all ˆEℓ,k∈¯EL such that αℓkare entries of a Hermi-
tian matrix. Most of the solutions we have found to
this optimization problem are numerical and the detailed
exploration and classiﬁcation of them is left as future
work.
For the simplest error set ¯E1 ={ˆI, ˆa}, we have found
an analytic code
|W↑⟩= 1√
6
(∑
7−
√
17|0⟩+
∑√
17−1|3⟩
{
, (H2a)
|W↓⟩= 1√
6
(∑
9−
√
17|1⟩−
∑√
17−3|4⟩
{
. (H2b)
with remarkably low rate for the correctable error
P1/κδt= ¯n = (
√
17−1)/2≈1.56 and rate for the un-
correctable errors P2/κδt=κδt(3
√
17−7)/4≈1.34κδt.
The comparison with values P bin
1 /κδt= ¯nbin = 2 and
P bin
2 /κδt= 2κδtof the corresponding binomial code (2)
shows a performance advantage both in the rate of cor-
rectable and uncorrectable errors. Due to the lack of
deﬁnite parity structure with the codewords (H2), one
has to use general projective measurements to detect loss
of a photon instead of the straightforward parity measure-
ments for the binomial codes (App. A). These general
projections may be realizable using current superconduct-
ing circuit technology [ 41–44] but most likely with lower
ﬁdelity than parity measurements [ 39]. By extending
this code to be protected against a photon gain error,
¯E′
1 ={ˆI, ˆa, ˆa†}, we get
|W↑⟩= 1√
8
(∑
9−
√
21|0⟩+
∑√
21−1|4⟩
{
, (H3a)
|W↓⟩= 1√
8
(∑
11−
√
21|1⟩−
∑√
21−3|5⟩
{
. (H3b)
Here we observe an even more dramatic relative and
absolute improvement in P1/κδt= (
√
21−1)/2 ≈
1.79 and P2/κδt= κδt(4
√
21−9)/4 ≈2.33κδt
in comparison with the values P bin
1 /κδt= 3 and
P bin
2 /κδt= 5.25κδtof the corresponding binomial code(
|W↑⟩= (|0⟩+|6⟩)/
√
2 and |W↓⟩= 3
{
.
1. Approximate quantum error correction under
continuous-time dissipative evolution
Here, we construct a recovery operation for the opti-
mized code (H2) that achieves an accuracy ofO(κδt) in
protecting against the photon loss channel that includes
both the photon loss jump and no-jump errors, as we
did for the binomial code in Sec. III A. The optimized
code (H2) has a diagonal QEC matrix for the discrete
errors ¯E1 ={ˆI, ˆa}. But for the errors (15) that include the
no-jump evolution,E1 ={ˆE0, ˆE1}, there are non diagonal
elements that do not identically vanish and violate the
structure of the QEC matrix due to the mixing caused
by the no-jump evolution:
⟨Wσ|ˆE†
0 ˆE1|Wσ′⟩= (κδt)
3
2⟨Wσ|ˆnˆa|Wσ′⟩+O[(κδt)2]
(H4)
=−δ↑↓2(κδt)
3
2
∑
5−
√
17 +O[(κδt)2].
Notice that the diagonal approximate quantum error cor-
rection criteria (22) was a result of the strict general-
ized parity structure of the binomial codes. Here we
have deliberately broken this structure and may wonder
whether the highest uncorrectable error for E1 is of the
order of (κδt)2 or (κδt)
3
2 as there is a non-vanishing term
(κδt)
3
2⟨W↑|ˆnˆa|W↓⟩in the QEC matrix.
The eﬀect of them is most easily seen by explicitly going
through the error and recovery processes. Remembering
that a quantum state|ψ⟩=u|W↑⟩+v|W↓⟩transforms to
|ψℓ⟩≡ˆEℓ|ψ⟩/⟨ψ|ˆE†
ℓˆEℓ|ψ⟩
1
2
under the action of a Kraus

## PDF page 21

21
operator ˆEℓ, the respective error states under no-jump
evolution and a photon loss error are
|ψ0⟩=|ψ⟩+κδt
(
Γ0u|E0
↑⟩+γ0v|E0
↓⟩
{
, (H5a)
|ψ1⟩=u
(
1−1
2Γ2
0|v|2κδt
{
|E1
↑⟩
+v
(
1−|u|2γ1κδt
{
|E1
↓⟩+vΓ0κδt|W↑⟩, (H5b)
to ﬁrst order in κδt. The coeﬃcients Γ 0 =
∑
(
√
17−3)/2,
γ0 = 1
2
√
3
√
17−11, and γ1 = 2/(3 +
√
17) are indepen-
dent on u and v. The normalized error words for the
no-jump errors are
|E0
↑⟩= 1√
6
(∑√
17−1|0⟩−
∑
7−
√
17|3⟩
{
, (H6a)
|E0
↓⟩= 1√
6
(∑√
17−3|1⟩+
∑
9−
√
17|4⟩
{
, (H6b)
and respectively for the photon loss errors,
|E1
↑⟩=|2⟩, |E1
↓⟩=|E0
↑⟩, (H7)
where one notices that the error words overlap between
the two errors|E1
↓⟩=|E0
↑⟩, captured by the non-vanishing
non-diagonal term (κδt)
3
2⟨W↑|ˆnˆa|W↓⟩.
We adopt now the recovery process of Eq. (18). Be-
cause we cannot use parity to detect a photon loss er-
ror we replace it with a measurement that asks whether
the system is in the subspace of words after a pho-
ton loss error {|E1
σ⟩}. This measurement performs the
projection ˆP1 = ∑
σ|E1
σ⟩⟨E1
σ|. The recovery process
is R = {ˆU0(ˆI−ˆP1), ˆU1 ˆP1}, where the unitary oper-
ation ˆU1 performs state transfer |Wσ⟩ ↔ |E1
σ⟩and
the unitary operation ˆU0 performs the state transfer
|W↓⟩↔|W↓⟩+κδtγ0|E0
↓⟩similarly as with the code (2).
Thus, we get the recovery processes
R(E(ˆρ)) =
1∑
k=0
ˆRk
( 1∑
ℓ=0
ˆEℓˆρˆE†
ℓ
(
ˆR†
k +O
[
(κδt)2]
=
1∑
k=0
ˆRk [(1−¯nκδt)|ψ0⟩⟨ψ0|+ ¯nκδt|ψ1⟩⟨ψ1|] ˆR†
k +O
[
(κδt)2]
=ˆρ+ ˆU1
[
(κδt)2Γ2
0|u|2|E0
↑⟩⟨E0
↑|
]ˆU†
1 +O
[
(κδt)2]
=ˆρ+O
[
(κδt)2]
, (H8)
where we have written the time evolution with the help
of the probabilities of the Kraus operator Tr( ˆE†
0 ˆE0 ˆρ) =
1−¯nκδt+O[(κδt)2] and Tr( ˆE†
1 ˆE1 ˆρ) = ¯nκδt+O[(κδt)2]
and the resulting states |ψi⟩⟨ψi|from Eq. (H5). From
this expression we see that many terms that are ﬁrst
order in|ψi⟩, together with the corresponding probability,
actually produce a higher order term. The second term in
the second line comes from the overlap between the two
errors, indicating a misidentiﬁcation of the errors with a
probability∼(κδt)2. The recovery process fails to order
(κδt)2 because part of the no-jump evolution is corrected
as a photon loss error. However, this can be ignored as
we are protecting to order κδt. Notice that the same
result within the accuracy κδtcan be also achieved by
the recoveryRm ={ˆPW, ˆU1(1−ˆPW)}. Here, the recovery
error∼(κδt)2 comes from incorrectly identifying part of
the photon loss error.
For L = 1, the approximate QEC conditions of the
continuous-time dissipative evolution under photon loss
are equivalent to the QEC conditions of Eq. (1). Hence,
the code of Eq. (H2) can correct the continuous-time
error process to order κδtas was shown above. How-
ever in general, for L > 1, the optimized code words
protecting against the continuous-time error process to
order (κδt)L will be timestep dependent. The error oper-
ators can be written as ˆEℓ∼ˆaℓˆE0. Then by writing the
optimized code words |W′
σ⟩as|W′
σ⟩= ˆE−1
0 |Wσ⟩/√Zσ
we have eﬀectively reduced the problem to ﬁnding code
words|Wσ⟩that satisfy QEC conditions of Eq. (1) for
the bare photon loss errors ¯EL ={ˆI, ˆa, ˆa2,..., ˆaL}. With
the normalization factors Z =Zσ=⟨Wσ|E−2
0 |Wσ⟩, the
operation ˆE−1
0 /
√
Z is unitary for the states|Wσ⟩to order
(κδt)L as a consequence of QEC conditions.
[1] S. L. Braunstein, Error Correction for Continuous Quan-
tum Variables, Phys. Rev. Lett. 80, 4084 (1998).
[2] S. Lloyd and J.-J. E. Slotine, Analog Quantum Error

## PDF page 22

22
Correction, Phys. Rev. Lett. 80, 4088 (1998).
[3] S. Braunstein and P. van Loock, Quantum informa-
tion with continuous variables, Rev. Mod. Phys. 77, 513
(2005).
[4] J. Niset, U. L. Andersen, and N. J. Cerf, Experimentally
Feasible Quantum Erasure-Correcting Code for Continu-
ous Variables, Phys. Rev. Lett. 101, 130503 (2008).
[5] T. Aoki, G. Takahashi, T. Kajiya, J.-i. Yoshikawa, S. L.
Braunstein, P. van Loock, and A. Furusawa, Quan-
tum error correction beyond qubits, Nature Phys. 5, 541
(2009).
[6] M. Lassen, M. Sabuncu, A. Huck, J. Niset, G. Leuchs,
N. J. Cerf, and U. L. Andersen, Quantum optical co-
herence can survive photon losses using a continuous-
variable quantum erasure-correcting code,Nature Photon.
4, 700 (2010).
[7] C. Weedbrook, S. Pirandola, R. Garc´ ıa-Patr´ on, N. J.
Cerf, T. C. Ralph, J. H. Shapiro, and S. Lloyd, Gaussian
quantum information, Rev. Mod. Phys. 84, 621 (2012).
[8] N. C. Menicucci, Fault-Tolerant Measurement-Based
Quantum Computing with Continuous-Variable Cluster
States, Phys. Rev. Lett. 112, 120504 (2014).
[9] R. J. Schoelkopf and S. M. Girvin, Wiring up quantum
systems, Nature 451, 664 (2008).
[10] M. H. Devoret and R. J. Schoelkopf, Superconducting
Circuits for Quantum Information: An Outlook, Science
339, 1169 (2013).
[11] T. Brecht, W. Pfaﬀ, C. Wang, Y. Chu, L. Frunzio, M. H.
Devoret, and R. J. Schoelkopf, Multilayer microwave
integrated quantum circuits for scalable quantum com-
puting, npj Quant. Inf. 2, 16002 (2016).
[12] I. L. Chuang, D. W. Leung, and Y. Yamamoto, Bosonic
quantum codes for amplitude damping, Phys. Rev. A 56,
1114 (1997).
[13] D. Gottesman, A. Yu. Kitaev, and J. Preskill, Encoding
a qubit in an oscillator, Phys. Rev. A 64, 012310 (2001).
[14] S. Glancy, H. M. Vasconcelos, and T. C. Ralph, Trans-
mission of optical coherent-state qubits, Phys. Rev. A
70, 022317 (2004).
[15] W. Wasilewski and K. Banaszek, Protecting an opti-
cal qubit against photon loss, Phys. Rev.A 75, 042316
(2007).
[16] P. T. Cochrane, G. J. Milburn, and W. J. Munro,
Macroscopically distinct quantum-superposition states as
a bosonic code for amplitude damping, Phys. Rev. A 59,
2631 (1999).
[17] Z. Leghtas, G. Kirchmair, B. Vlastakis, R. J. Schoelkopf,
M. H. Devoret, and M. Mirrahimi, Hardware-Eﬃcient
Autonomous Quantum Memory Protection, Phys. Rev.
Lett. 111, 120501 (2013).
[18] M. Mirrahimi, Z. Leghtas, V. V. Albert, S. Touzard,
R. J. Schoelkopf, L. Jiang, and M. H. Devoret, Dynam-
ically protected cat-qubits: a new paradigm for universal
quantum computation, New J. Phys. 16, 045014 (2014).
[19] V. V. Albert, C. Shu, S. Krastanov, C. Shen, R.-B.
Liu, Z.-B. Yang, R. J. Schoelkopf, M. Mirrahimi, M. H.
Devoret, and L. Jiang, Holonomic quantum control with
continous variable systems, Phys. Rev. Lett 116, 140502
(2016).
[20] B. M. Terhal and D. Weigand, Encoding a qubit into
a cavity mode in circuit QED using phase estimation,
Phys. Rev. A 93, 012315 (2016).
[21] M. Grassl, L. Kong, Z. Wei, Z.-Q. Yin, and B. Zeng,
Quantum Error-Correcting Codes for Qudit Amplitude
Damping, arXiv:1509.06829 (2015).
[22] M. Bergmann and P. van Loock, Quantum error
correction against photon loss using NOON states,
arXiv:1512.07605 (2015).
[23] J. I. Cirac, P. Zoller, H. J. Kimble, and H. Mabuchi,
Quantum State Transfer and Entanglement Distribution
among Distant Nodes in a Quantum Network, Phys. Rev.
Lett. 78, 3221 (1997).
[24] J. Wenner, Y. Yin, Y. Chen, R. Barends, B. Chiaro,
E. Jeﬀrey, J. Kelly, A. Megrant, J. Y. Mutus, C. Neill,
P. J. J. O’Malley, P. Roushan, D. Sank, A. Vainsencher,
T. C. White, A. N. Korotkov, A. N. Cleland, and J. M.
Martinis, Catching Time-Reversed Microwave Coherent
State Photons with 99.4% Absorption Eﬃciency, Phys.
Rev. Lett. 112, 210501 (2014).
[25] S. J. Srinivasan, N. M. Sundaresan, D. Sadri, Y. Liu,
J. M. Gambetta, T. Yu, S. M. Girvin, and A. A. Houck,
Time-reversal symmetrization of spontaneous emission
for quantum state transfer, Phys. Rev. A 89, 033857
(2014).
[26] R. W. Andrews, R. W. Peterson, T. P. Purdy, K. Cicak,
R. W. Simmonds, C. A. Regal, and K. W. Lehnert,
Bidirectional and eﬃcient conversion between microwave
and optical light, Nature Phys. 10, 321 (2014).
[27] H. Paik, D. I. Schuster, L. S. Bishop, G. Kirchmair,
G. Catelani, A. P. Sears, B. R. Johnson, M. J. Reagor,
L. Frunzio, L. I. Glazman, S. M. Girvin, M. H. De-
voret, and R. J. Schoelkopf, Observation of high coher-
ence in Josephson junction qubits measured in a three-
dimensional circuit QED architecture, Phys. Rev. Lett.
107, 240501 (2011).
[28] C. Rigetti, J. M. Gambetta, S. Poletto, B. L. T. Plourde,
J. M. Chow, A. D. C´ orcoles, J. A. Smolin, S. T. Merkel,
J. R. Rozen, G. A. Keefe, M. B. Rothwell, M. B. Ketchen,
and M. Steﬀen, Superconducting qubit in a waveguide
cavity with a coherence time approaching 0.1 ms, Phys.
Rev. B 86, 100506 (2012).
[29] J. Chang, M. R. Vissers, A. D. Corcoles, M. Sandberg,
J. Gao, D. W. Abraham, J. M. Chow, J. M. Gambetta,
M. B. Rothwell, G. A. Keefe, M. Steﬀen, and D. P.
Pappas, Improved superconducting qubit coherence using
titanium nitride, App. Phys. Lett. 103, 012602 (2013).
[30] R. Barends, J. Kelly, A. Megrant, D. Sank, E. Jef-
frey, Y. Chen, Y. Yin, B. Chiaro, J. Mutus, C. Neill,
P. O´ Malley, P. Roushan, J. Wenner, T. C. White, A. N.
Cleland, and J. M. Martinis, Coherent Josephson qubit
suitable for scalable quantum integrated circuits, Phys.
Rev. Lett. 111, 080502 (2013).
[31] F. Yan, S. Gustavsson, A. Kamal, J. Birenbaum, A. P.
Sears, D. Hover, T. J. Gudmundsen, J. L. Yoder, T. P.
Orlando, J. Clarke, A. J. Kerman, and W. D. Oliver,
The Flux Qubit Revisited, arXiv:1508.06299 (2015).
[32] P. Bertet, A. Auﬀeves, P. Maioli, S. Osnaghi, T. Meunier,
M. Brune, J. M. Raimond, and S. Haroche, Direct
Measurement of the Wigner Function of a One-Photon
Fock State in a Cavity, Phys. Rev. Lett. 89, 200402
(2002).
[33] C. Sayrin, I. Dotsenko, X. Zhou, B. Peaudecerf, T. Rybar-
czyk, S. Gleyzes, P. Rouchon, M. Mirrahimi, H. Amini,
M. Brune, J.-M. Raimond, and S. Haroche, Real-time
quantum feedback prepares and stabilizes photon number
states, Nature 477, 73 (2011).
[34] M. Reagor, H. Paik, G. Catelani, L. Sun, C. Axline,
E. Holland, I. M. Pop, N. A. Masluk, T. Brecht, L. Frun-

## PDF page 23

23
zio, M. H. Devoret, L. Glazman, and R. J. Schoelkopf,
Reaching 10 ms single photon lifetimes for superconduct-
ing aluminum cavities, App. Phys. Lett. 102, 192604
(2013).
[35] M. Reagor, W. Pfaﬀ, C. Axline, R. W. Heeres, N. Ofek,
K. Sliwa, E. Holland, C. Wang, J. Blumoﬀ, K. Chou,
M. J. Hatridge, L. Frunzio, M. H. Devoret, L. Jiang,
and R. J. Schoelkopf, A quantum memory with near-
millisecond coherence in circuit QED, arXiv: 1508.05882
(2015).
[36] A. A. Houck, D. I. Schuster, J. M. Gambetta, J. A.
Schreier, B. R. Johnson, J. M. Chow, L. Frunzio, J. Ma-
jer, M. H. Devoret, S. M. Girvin, and R. J. Schoelkopf,
Generating single microwave photons in a circuit, Nature
449, 328 (2007).
[37] M. Hofheinz, H. Wang, M. Ansmann, R. C. Bialczak,
E. Lucero, M. Neeley, A. D. O’Connell, D. Sank, J. Wen-
ner, J. M. Martinis, and A. N. Cleland, Synthesizing
arbitrary quantum states in a superconducting resonator,
Nature 459, 546 (2009).
[38] B. Vlastakis, G. Kirchmair, Z. Leghtas, S. E. Nigg,
L. Frunzio, S. M. Girvin, M. Mirrahimi, M. H. De-
voret, and R. J. Schoelkopf, Deterministically Encoding
Quantum Information Using 100-Photon Schr¨ odinger
Cat States, Science 342, 607 (2013).
[39] L. Sun, A. Petrenko, Z. Leghtas, B. Vlastakis, G. Kirch-
mair, K. M. Sliwa, A. Narla, M. Hatridge, S. Shankar,
J. Blumoﬀ, L. Frunzio, M. Mirrahimi, M. H. Devoret,
and R. J. Schoelkopf, Tracking photon jumps with re-
peated quantum non-demolition parity measurements,
Nature 511, 444 (2014).
[40] B. Vlastakis, A. Petrenko, N. Ofek, L. Sun, Z. Leghtas,
K. Sliwa, Y. Liu, M. Hatridge, J. Blumoﬀ, L. Frun-
zio, M. Mirrahimi, L. Jiang, M. H. Devoret, and R. J.
Schoelkopf, Characterizing entanglement of an artiﬁcial
atom and a cavity cat state with Bell’s inequality, Nat.
Commun. 6, 8970 (2015).
[41] S. Krastanov, V. V. Albert, C. Shen, C.-L. Zou, R. W.
Heeres, B. Vlastakis, R. J. Schoelkopf, and L. Jiang,
Universal control of an oscillator with dispersive coupling
to a qubit, Phys. Rev. A 92, 040303(R) (2015).
[42] R. W. Heeres, B. Vlastakis, E. Holland, S. Krastanov,
V. V. Albert, L. Frunzio, L. Jiang, and R. J. Schoelkopf,
Cavity State Manipulation Using Photon-Number Selec-
tive Phase Gates, Phys. Rev. Lett. 115, 137002 (2015).
[43] C. Wang, Y. Y. Gao, P. Reinhold, R. W. Heeres, N. Ofek,
K. Chou, C. Axline, M. Reagor, J. Blumoﬀ, K. M. Sliwa,
L. Frunzio, S. M. Girvin, L. Jiang, M. Mirrahimi, M. H.
Devoret, and R. J. Schoelkopf, A Schr¨ odinger cat living
in two boxes, Science 352, 1087 (2016).
[44] N. Ofek, A. Petrenko, R. Heeres, P. Reinhold, Z. Leghtas,
B. Vlastakis, Y. Liu, L. Frunzio, S. M. Girvin, L. Jiang,
M. Mirrahimi, M. H. Devoret, and R. J. Schoelkopf,
Demonstrating Quantum Error Correction that Extends
the Lifetime of Quantum Information, arXiv:1602.04768
(2016).
[45] J. Chiaverini, D. Leibfried, T. Schaetz, M. D. Barrett,
R. B. Blakestad, J. Britton, W. M. Itano, J. D. Jost,
E. Knill, C. Langer, R. Ozeri, and D. J. Wineland,
Realization of quantum error correction, Nature 432,
602 (2004).
[46] J. P. Home, D. Hanneke, J. D. Jost, J. M. Amini,
D. Leibfried, and D. J. Wineland, Complete methods
set for scalable ion trap quantum information processing,
Science 325, 1227 (2009).
[47] P. Schindler, J. T. Barreiro, T. Monz, V. Nebendahl,
D. Nigg, M. Chwalla, M. Hennrich, and R. Blatt, Exper-
imental Repetitive Quantum Error Correction, Science
332, 1059 (2011).
[48] D. Nigg, M. M¨ uller, E. A. Martinez, P. Schindler, M. Hen-
nrich, T. Monz, M. A. Martin-Delgado, and R. Blatt,
Quantum computations on a topologically encoded qubit,
Science 345, 302 (2014).
[49] N. Khaneja, T. Reiss, C. Kehlet, T. Schulte-Herbr¨ uggen,
and S. J. Glaser, Optimal control of coupled spin dynam-
ics: design of NMR pulse sequences by gradient ascent
algorithms, J. Mag. Res. 172, 296 (2005).
[50] P. de Fouquieres, S. G. Schirmer, S. J. Glaser, and
I. Kuprov, Second order gradient ascent pulse engineer-
ing, J. Mag. Res. 212, 412 (2011).
[51] D. G. Cory, M. D. Price, W. Maas, E. Knill, R. Laﬂamme,
W. H. Zurek, T. F. Havel, and S. S. Somaroo, Experi-
mental Quantum Error Correction, Phys. Rev. Lett. 81,
2152 (1998).
[52] O. Moussa, J. Baugh, C. A. Ryan, and R. Laﬂamme,
Demonstration of Suﬃcient Control for Two Rounds of
Quantum Error Correction in a Solid State Ensemble
Quantum Information Processor, Phys. Rev. Lett. 107,
160501 (2011).
[53] J. Zhang, R. Laﬂamme, and D. Suter, Experimental
Implementation of Encoded Logical Qubit Operations in
a Perfect Quantum Error Correcting Code, Phys. Rev.
Lett. 109, 100503 (2012).
[54] G. Waldherr, Y. Wang, S. Zaiser, M. Jamali, T. Schulte-
Herbr¨ uggen, H. Abe, T. Ohshima, J. Isoya, J. F. Du,
P. Neumann, and J. Wrachtrup, Quantum error cor-
rection in a solid-state hybrid spin register, Nature 506,
204 (2014).
[55] T. H. Taminiau, J. Cramer, T. v. d. Sar, V. V. Do-
brovitski, and R. Hanson, Universal control and error
correction in multi-qubit spin registers in diamond, Na-
ture Nanotech. 9, 171 (2014).
[56] M. D. Reed, L. DiCarlo, S. E. Nigg, L. Sun, L. Frun-
zio, S. M. Girvin, and R. J. Schoelkopf, Realization of
three-qubit quantum error correction with superconduct-
ing circuits, Nature 482, 382 (2012).
[57] J. Kelly, R. Barends, A. G. Fowler, A. Megrant, E. Jef-
frey, T. C. White, D. Sank, J. Y. Mutus, B. Campbell,
Y. Chen, Z. Chen, B. Chiaro, A. Dunsworth, I.-C. Hoi,
C. Neill, P. J. J. O’Malley, C. Quintana, P. Roushan,
A. Vainsencher, J. Wenner, A. N. Cleland, and J. M.
Martinis, State preservation by repetitive error detection
in a superconducting quantum circuit, Nature 519, 66
(2015).
[58] A. D. C´ orcoles, E. Magesan, S. J. Srinivasan, A. W.
Cross, M. Steﬀen, J. M. Gambetta, and J. M. Chow,
Demonstration of a quantum error detection code us-
ing a square lattice of four superconducting qubits, Nat.
Commun. 6, 6979 (2015).
[59] D. Rist´ e, S. Poletto, M.-Z. Huang, A. Bruno, V. Vester-
inen, O.-P. Saira, and L. DiCarlo, Detecting bit-ﬂip
errors in a logical qubit using stabilizer measurements,
Nat. Commun. 6, 6983 (2015).
[60] J. Cramer, N. Kalb, M. A. Rol, B. Hensen, M. S. Blok,
M. Markham, D. J. Twitchen, R. Hanson, and T. H.
Taminiau, Repeated quantum error correction on a con-
tinuously encoded qubit by real-time feedback, Nat. Com-
mun. 7, 11526 (2016).

## PDF page 24

24
[61] R. Laﬂamme, C. Miquel, J. P. Paz, and W. H. Zurek,
Perfect Quantum Error Correcting Code,Phys. Rev. Lett.
77, 198 (1996).
[62] C. H. Bennett, D. P. DiVincenzo, J. A. Smolin, and
W. K. Wootters, Mixed-state entanglement and quantum
error correction, Phys. Rev. A 54, 3824 (1996).
[63] D. Gottesman, An Introduction to Quantum Error Cor-
rection and Fault-Tolerant Quantum Computation, in
Quantum Information Science and Its Contributions to
Mathematics, Proceedings of Symposia in Applied Math-
ematics, Vol. 68 (Amer. Math. Soc., Providence, Rhode
Island, 2010) pp. 13–58, arXiv:0904.2557.
[64] M. A. Nielsen and I. L. Chuang, Quantum Computation
and Quantum Information (Cambridge University Press,
New York, 2010).
[65] A. M. Steane, Error Correcting Codes in Quantum The-
ory, Phys. Rev. Lett. 77, 793 (1996).
[66] P. W. Shor, Scheme for reducing decoherence in quantum
computer memory, Phys. Rev. A 52, R2493 (1995).
[67] P. Zanardi and M. Rasetti, Noiseless quantum codes,
Phys. Rev. Lett. 79, 3306 (1997).
[68] D. A. Lidar, I. L. Chuang, and K. B. Whaley,
Decoherence-free subspaces for quantum computation,
Phys. Rev. Lett. 81, 2594 (1998).
[69] N. Boulant, L. Viola, E. M. Fortunato, and D. G. Cory,
Experimental implementation of a concatenated quan-
tum error-correcting code, Phys. Rev. Lett. 94, 130501
(2005).
[70] J. Gao, J. Zmuidzinas, B. A. Mazin, H. G. LeDuc, and
P. K. Day, Noise properties of superconducting coplanar
waveguide microwave resonators, App. Phys. Lett. 90,
102507 (2007).
[71] B. M. Terhal, Quantum error correction for quantum
memories, Rev. Mod. Phys. 87, 307 (2015).
[72] E. Knill and R. Laﬂamme, Theory of quantum error-
correcting codes, Phys. Rev. A 55, 900 (1997).
[73] Notice that this is not a completely positive and trace
preserving (CPTP) map, completion to such will be done
in Sec. III.
[74] T. Neuschel, A Note on Extended Binomial Coeﬃcients,
arXiv:1407.7429 (2014).
[75] S. Eger, Stirling’s approximation for central extended bi-
nomial coeﬃcients, Am. Math. Monthly 121, 344 (2014).
[76] C. Caiado and P. Rathie, Polynomial coeﬃcients and
distribution of the sum of discrete uniform variables, in
Eighth Annual Conference of the Society of Special Func-
tions and their Applications, edited by A. M. Mathai,
M. A. Pathan, K. K. Jose, and J. Jacob (Society for
Special Functions & their Applications, 2007).
[77] D. W. Leung, M. A. Nielsen, I. L. Chuang, and Y. Ya-
mamoto, Approximate quantum error correction can lead
to better codes, Phys. Rev. A 56, 2567 (1997).
[78] C. Cr´ epeau, D. Gottesman, and A. Smith, Approxi-
mate quantum error-correcting codes and secret sharing,
in Advances in Cryptology–EUROCRYPT 2005, 24th
Annual Conference on the Theory and Applications of
Cryptographic Techniques, Aarhus, Denmark, May 22-
26, 2005, edited by R. Cramer (Springer, Berlin, 2005)
pp. 285–301, arXiv:quant-ph/0503139.
[79] H. K. Ng and P. Mandayam, Simple approach to approx-
imate quantum error correction based on the transpose
channel, Phys. Rev. A 81, 062342 (2010).
[80] C. B´ eny and O. Oreshkov,General Conditions for Ap-
proximate Quantum Error Correction and Near-Optimal
Recovery Channels, Phys. Rev. Lett. 104, 120501 (2010).
[81] C. B´ eny,Perturbative Quantum Error Correction, Phys.
Rev. Lett. 107, 080501 (2011).
[82] P. Mandayam and H. K. Ng,Towards a uniﬁed framework
for approximate quantum error correction, Phys. Rev. A
86, 012335 (2012).
[83] Y. Ouyang, Permutation-invariant quantum codes, Phys.
Rev. A 90, 062317 (2014).
[84] Y. Ouyang and J. Fitzsimons, Permutation-invariant
codes encoding more than one qubit, Phys. Rev. A 93,
042340 (2016).
[85] H.-P. Breuer and F. Petruccione, The Theory of Open
Quantum Systems (Oxford University Press, Oxford,
2002).
[86] M. Ueda, Probability-density-functional description of
quantum photodetection processes, Quantum Opt. 1, 131
(1989).
[87] C. T. Lee, Superoperators and their implications in the
hybrid model for photodetection, Phys. Rev. A 49, 4888
(1994).
[88] This is a CPTP map to the desired accuracy of ( κδt)L.
[89] H. Mabuchi and P. Zoller, Inversion of Quantum Jumps
in Quantum Optical Systems under Continuous Obser-
vation, Phys. Rev. Lett. 76, 3108 (1996).
[90] M. B. Plenio, V. Vedral, and P. L. Knight, Quantum
error correction in the presence of spontaneous emission,
Phys. Rev. A 55, 67 (1997).
[91] J. I. Cirac, T. Pellizzari, and P. Zoller, Enforcing Coher-
ent Evolution in Dissipative Quantum Dynamics, Science
273, 1207 (1996).
[92] A. S. Fletcher, P. W. Shor, and M. Z. Win, Optimum
quantum error recovery using semideﬁnite programming,
Phys. Rev. A 75, 012338 (2007).
[93] H. Zheng, M. Silveri, R. T. Brierley, K. W. Lehnert, and
S. M. Girvin, to be published (2015).
[94] J. Kerckhoﬀ, H. I. Nurdin, D. S. Pavlichin, and
H. Mabuchi, Designing Quantum Memories with Embed-
ded Control: Photonic Circuits for Autonomous Quan-
tum Error Correction, Phys. Rev. Lett. 105, 040502
(2010).
[95] E. Kapit, Hardware-eﬃcient and fully autonomous quan-
tum error correction in superconducting circuits, Phys.
Rev. Lett. 116, 150501 (2016).
[96] Z. Leghtas, S. Touzard, I. M. Pop, A. Kou, B. Vlas-
takis, A. Petrenko, K. M. Sliwa, A. Narla, S. Shankar,
M. J. Hatridge, M. Reagor, L. Frunzio, R. J. Schoelkopf,
M. Mirrahimi, and M. H. Devoret, Conﬁning the state
of light to a quantum manifold by engineered two-photon
loss, Science 347, 853 (2015).
[97] A. Auerbach, Interacting Electrons and Quantum Mag-
netism, edited by J. L. Birman, J. W. Lynn, M. P.
Silverman, H. E. Stanley, and M. Voloshin, Graduate
Texts in Contemporary Physics (Springer, New York,
1994) pp. 69–70.
[98] B. C. Travaglione and G. J. Milburn, Preparing encoded
states in an oscillator, Phys. Rev. A 66, 052322 (2002).
[99] S. Pirandola, S. Mancini, D. Vitali, and P. Tombesi,
Constructing ﬁnite-dimensional codes with optical con-
tinuous variables, Europhys. Lett. 68, 323 (2004).
[100] H. M. Vasconcelos, L. Sanz, and S. Glanzy, All-optical
generation of states for ”Encoding a qubit in a an oscil-
lator”, Opt. Lett. 35, 3261 (2010).
[101] S. Glancy and E. Knill, Error analysis for encoding a
qubit in an oscillator, Phys. Rev. A 73, 012325 (2006).

## PDF page 25

25
[102] P. Brooks, A. Yu. Kitaev, and J. Preskill, Protected gates
for superconducting qubits, Phys. Rev. A 87, 052306
(2013).
[103] S. Takeda, T. Mizuta, M. Fuwa, P. van Loock, and
A. Furusawa, Deterministic quantum teleportation of
photonic quantum bits by a hybrid technique, Nature
500, 315 (2013).
[104] S. Pirandola, J. Eisert, C. Weedbrook, A. Furusawa,
and S. L. Braunstein, Advances in quantum teleportation,
Nature Photon. 9, 641 (2015).
[105] J. I. Cirac, P. Zoller, H. J. Kimble, and H. Mabuchi,
Quantum State Transfer and Entanglement Distribution
among Distant Nodes in a Quantum Network, Phys. Rev.
Lett. 78, 3221 (1997).
[106] W. J. Munro, A. M. Stephens, S. J. Devitt, K. A. Harri-
son, and K. Nemoto, Quantum communication without
the necessity of quantum memories, Nature Photon. 6,
777 (2012).
[107] S. Muralidharan, J. Kim, N. L¨ utkenhaus, M. D. Lukin,
and L. Jiang, Ultrafast and Fault-Tolerant Quantum
Communication across Long Distances, Phys. Rev. Lett.
112, 250501 (2014).
[108] A. N. Korotkov, Flying microwave qubits with nearly per-
fect transfer eﬃciency, Phys. Rev. B 84, 014510 (2011).
[109] S. J. van Enk, J. I. Cirac, and P. Zoller, Ideal Quantum
Communication over Noisy Channels: A Quantum Opti-
cal Implementation, Phys. Rev. Lett. 78, 4293 (1997).
[110] M. Pechal, L. Huthmacher, C. Eichler, S. Zeytinoˇ glu,
A. A. Abdumalikov, S. Berger, A. Wallraﬀ, and S. Fil-
ipp, Microwave-Controlled Generation of Shaped Single
Photons in Circuit Quantum Electrodynamics, Phys. Rev.
X 4, 041010 (2014).
[111] M. Pierre, I.-M. Svensson, S. R. Sathyamoorthy, G. Jo-
hansson, and P. Delsing, Storage and on-demand release
of microwaves using superconducting resonators with
tunable coupling, App. Phys. Lett. 104, 232604 (2014).
[112] E. Flurin, N. Roch, J. D. Pillet, F. Mallet, and B. Huard,
Superconducting Quantum Node for Entanglement and
Storage of Microwave Radiation, Phys. Rev. Lett. 114,
090503 (2015).
[113] R. W. Andrews, A. P. Reed, K. Cicak, J. D. Teufel, and
K. W. Lehnert, Quantum-enabled temporal and spectral
mode conversion of microwave signals, Nat. Commun.
6, 10021 (2015).
[114] L. Jiang, J. M. Taylor, K. Nemoto, W. J. Munro,
R. Van Meter, and M. D. Lukin, Quantum repeater
with encoding, Phys. Rev. A 79, 032325 (2009).
[115] B. M. Terhal, (private communication).
[116] J. Gambetta, A. Blais, D. I. Schuster, A. Wallraﬀ,
L. Frunzio, J. Majer, M. H. Devoret, S. M. Girvin, and
R. J. Schoelkopf, Qubit-photon interactions in a cavity:
Measurement-induced dephasing and number splitting,
Phys. Rev. A 74, 042318 (2006).
[117] D. I. Schuster, A. A. Houck, J. A. Schreier, A. Wallraﬀ,
J. M. Gambetta, A. Blais, L. Frunzio, J. Majer, B. John-
son, M. H. Devoret, S. M. Girvin, and R. J. Schoelkopf,
Resolving photon number states in a superconducting
circuit, Nature 445, 515 (2007).
[118] D. Aharonov and M. Ben-Or, Fault-tolerant quantum
computation with constant error, in Proceedings of the
Twenty-Ninth Annual ACM Symposium on Theory
of Computing (ACM, New York, 1997) pp. 176–188,
arXiv:quant-ph/9906129.
[119] S. Lloyd and S. L. Braunstein, Quantum Computation
over Continuous Variables, Phys. Rev. Lett. 82, 1784
(1999).
[120] K. Jacobs, Engineering Quantum States of a Nanores-
onator via a Simple Auxiliary System, Phys. Rev. Lett.
99, 117203 (2007).
