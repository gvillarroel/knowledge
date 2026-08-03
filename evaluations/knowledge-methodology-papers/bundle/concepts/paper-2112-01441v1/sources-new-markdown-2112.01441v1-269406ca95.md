---
type: Research Paper
title: 'A Review of SHACL: From Data Validation to Schema Reasoning for RDF Graphs'
description: SHACL semantics, expressiveness, implementation, and its separation from
  ordinary domain facts.
resource: https://example.org/knowledge-methodology-papers/resource/paper-2112-01441v1/sources%2Fnew%2Fmarkdown%2F2112.01441v1
tags:
- paper-2112-01441v1
- markdown
- rl
sources:
- id: paper-2112-01441v1
  resource: sources/new/markdown/2112.01441v1.md
  title: paper-2112-01441v1
generated:
  by: process:semantic-okf-python
concept_id: concepts/paper-2112-01441v1/sources-new-markdown-2112.01441v1-269406ca95
concept_path: concepts/paper-2112-01441v1/sources-new-markdown-2112.01441v1-269406ca95.md
subject_iri: https://example.org/knowledge-methodology-papers/resource/paper-2112-01441v1/sources%2Fnew%2Fmarkdown%2F2112.01441v1
ontology_class_iri: https://example.org/ontology/knowledge-methodology-papers#Paper
ontology_version_iri: https://example.org/ontology/knowledge-methodology-papers/1.0.0
source_id: paper-2112-01441v1
source_kind: markdown
source_path: sources/new/markdown/2112.01441v1.md
source_content_sha256: 807fa23d365d5e9605bb19e9cf9d5283e192df9938f0d7186d78ce5c17089ec1
record_sha256: 88261461ffc74d5482718a388b331cc043b787f09226b28e74c70f518ac7e97d
source_refs:
- https://example.org/knowledge-methodology-papers/provenance/record/paper-2112-01441v1/42e90b264b57884a8a0e7b2d
record_id: sources/new/markdown/2112.01441v1
---

# A Review of SHACL: From Data Validation to Schema Reasoning for RDF Graphs

## Dataset relevance

SHACL semantics, expressiveness, implementation, and its separation from ordinary domain facts.

- Coverage lanes: knowledge-graphs-and-ontologies; validation-and-reproducibility
- Relevant skills: build-semantic-okf-*; extract-ontologies; open-knowledge-format

## Source citation

- Pinned arXiv record: [2112.01441v1](https://arxiv.org/abs/2112.01441v1)
- Authors: Pareti, Paolo; Konstantinidis, George
- PDF: [https://arxiv.org/pdf/2112.01441v1](https://arxiv.org/pdf/2112.01441v1)
- PDF SHA-256: `0eb67e099b7489da85a74f6d10f9f1614358aa3871282f66e153dbf9c604f16d`
- Extracted pages: 30

The following text was extracted page by page from the pinned PDF. Page headings are stable evidence locators.

## PDF page 1

arXiv:2112.01441v1  [cs.AI]  2 Dec 2021
A Review of SHACL: From Data Validation to
Schema Reasoning for RDF Graphs
Paolo Pareti 1 and George Konstantinidis 2
1 University of Winchester, Winchester, United Kingdom
paolo.pareti@winchester.ac.uk
2 University of Southampton, Southampton, United Kingdom
g.konstantinidis@soton.ac.uk
Abstract. We present an introduction and a review of Shapes Con-
straint Language (shacl), the W3C recommendation language for val-
idating rdf data. A shacl document describes a set of constraints on
rdf nodes, and a graph is valid with respect to the document if its nodes
satisfy these constraints. We revisit the basic concepts of the language,
its constructs and components and their interaction. We rev iew the dif-
ferent formal frameworks used to study this language and the diﬀerent
semantics proposed. We examine a number of related problems , from
containment and satisﬁability to the interaction of shacl with inference
rules, and exhibit how diﬀerent modellings of the language a re useful for
diﬀerent problems. We also cover practical aspects of shacl, discussing
its implementations and state of adoption, to present a holi stic review
useful to practitioners and theoreticians alike.
1 Introduction
The Shapes Constraint Language ( shacl) [23] is a W3C recommendation lan-
guage for the validation of RDF graphs. In shacl, validation is based on shapes,
which deﬁne particular constraints and specify which nodes in a graph should
be validated against these constraints. The ability to vali date data with respect
to a set of constraints is of particular importance for RDF gr aphs, as they are
schemaless by design. Validation can be used to detect probl ems in a dataset
and it can provide data quality guarantees for the purpose of data exchange and
interoperability. A set of constraints can also be interpre ted as a “schema”, func-
tioning as one of the primary descriptors of a graph dataset, thus enhancing its
understandability and usability. A set of shacl shapes is called a shapes graph,
but we refer to it as a shacl document in order not to confuse it with the graphs
that it is used to validate.
In this article we present a review of shacl, which is composed of three main
parts. In the ﬁrst part, in Sections 2 and 3, we review the shacl speciﬁcation.
This part focuses on how shapes are deﬁned, and how they are us ed for the
purpose of validation. We highlight the main peculiarities of this language, and
discuss how shacl validation can be expressed either in terms of sparql queries,
to facilitate its implementation, or in terms of assignments [13], to make it

## PDF page 2

2 Pareti and Konstantinidis
amenable to theoretical study. The syntax of shacl is outside the scope of
this review, and for the precise details on how to encode part icular constraints
we refer the reader to the shacl speciﬁcation [23]. We also do not discuss the
process that lead to the development of shacl, but it should be noted that this
speciﬁcation was built on top of a number of previous constra int languages, the
most inﬂuential of which is Shape Expressions (ShEx) [48].
In the second part of our review, in Sections 5 to 8, we present the formal
properties of this language. This mainly revolves around a d iscussion of recursion.
The semantics of recursion is not deﬁned in the shacl speciﬁcation, and thus
has been the subject of signiﬁcant subsequent research [3]. The formal semantics
of shacl is given as a translation into SCL [37], a ﬁrst order logic language that
captures the entirety of the shacl speciﬁcation. Apart from validation, several
standard decision problems are discussed, such as satisﬁability and containment,
along with an existing study on the interaction of shacl with inference rules.
We try to keep a consistent notation throughout this article and at times this
notation might be diﬀerent from the one in the original artic les.
In Section 9, we review existing implementations of shacl validators and
their integration with mainstream graph databases. We also review prominent
additional tools to manage shacl documents, such as tools designed to auto-
mate or semi-automate the process of creating shacl documents by exploiting
graph data, ontologies, or other constraint languages. The se approaches provide
solutions to the cold start problem, and alleviate reliance on expert knowledge,
which are typical problems of new technologies. We compleme nt a discussion of
these approaches with a review of prominent applications of shacl in several
domains; in summary, the abundance of shacl related tools and applications
highlights the remarkable level of maturity and adoption re ached by this rela-
tively new language.
2 Preliminaries
Before discussing shacl, we brieﬂy introduce our notation for rdf graphs [14].
With the term rdf graph (or just graph) we refer to a set of rdf triples (or
just triples), where each triple <s,p,o> identiﬁes an edge with label p, called
predicate, from a node s, called subject, to a node o, called object. Subjects,
predicates and objects of rdf triples are collectively called rdf terms. The rdf
terms that appear as subject and objects in the triples of a gr aph are called the
nodes of the graph. Graphs in this article are represented in Turtl e syntax using
common XML namespaces, such as sh, rdf and rdfs to refer to, respectively, the
shacl, rdf, and rdfs [7] vocabularies. Queries over rdf graph will be expressed
as sparql [42] queries.
In the rdf data model, subjects, predicates and objects are deﬁned ove r
diﬀerent but overlapping domains. For example, while rdf terms of the iri type
can occupy any position in a triple, rdf terms of the literal type (representing
datatype values) can only appear in the object position. The se diﬀerences are not
central to the topics discussed in this review, and thus, for the sake of simplifying

## PDF page 3

A Review of shacl 3
:EmployeeShape a sh:PropertyShape ;
sh:targetClass :Employee ;
sh:path :hasOfficeNumber ;
sh:minCount 1 .
:Anne a :Employee .
:Bob a :Employee ;
:hasOfficeNumber "18" ;
:hasOfficeNumber "3" .
:Carl a :Employee ;
:hasOfficeNumber "171" .
:David a :Customer .
Fig. 1. (Left) A sample shacl document (shape graph) stating the constraint that
every employee must have at least one oﬃce number. (Right) A s ample rdf graph
(data graph).
notation, we will assume that all elements of a triple are dra wn from a single
and inﬁnite domain of constants. This corresponds to the not ion of generalized
rdf [14].
3 Overview of shacl
The main application of shacl is data validation. Data validation in shacl
requires two inputs: (1) an rdf graph G to be validated and (2) a shacl doc-
ument M that deﬁnes the conditions against which G must be evaluated. The
shacl speciﬁcation deﬁnes the output of the data validation proce ss as a vali-
dation report, detailing all the violations that were found in G of the conditions
set by M . If the violation report contains no violations, a graph G is valid w.r.t.
shacl document M . The shacl validation process can be abstracted into the
following decision problem. Given a graph G and a shacl document M , we de-
note with V alidate(G, M) the decision problem of deciding whether G is valid
w.r.t. shacl document M , that we call validating G against M .
For example, the graph on the left of Figure 1 represents a shacl document
M1, that deﬁnes the condition that every employee must have an o ﬃce number.
Therefore, the validation report for a graph and M1 would list all of the instances
of :Employee in the graph that do not have an oﬃce number. The validation
report for M1 and the data graph G1 on the right of Figure 1 contains a violation
on node rdf:Anne, since she does not have an oﬃce number. Therefore G1 is not
valid w.r.t. M1.
Formally, a shacl document is a set of shapes. Validating a graph against a
shacl document involves validating it against each shape. Shapes restrict the
structure of a valid graph by focusing on certain nodes and ex amining whether
they satisfy their constraints. The main components of a sha pe are a constraint
d and a target deﬁnition t. Constraints can be evaluated on any rdf node to
determine whether that node satisﬁes or not the given constraints. A node that
satisﬁes the constraint of a shape it is said to conform to that shape, or not-
conform otherwise. If a shape has an empty constraint, all nodes triv ially conform
to the shape. Not all nodes of a graph must conform to all the sh apes in the

## PDF page 4

4 Pareti and Konstantinidis
shacl document. The constraint deﬁnition of each shape deﬁnes whi ch rdf
nodes, called target nodes, must conform to that shape in order for the graph to
be valid. A shape with an empty constraint deﬁnition does not have any target
nodes. Through inter-shape referencing, as we will see belo w, additional nodes
might be required to conform to certain shapes (or not, if neg ation is used) for
the validation to succeed. Further irrelevant nodes within the graph do not play
a role in validation of the shape, whether they conform to it o r not. The shacl
document M1 of our previous example, contains shape :EmployeeShape, whose
constraint captures the property of “having an oﬃce number” , and whose target
deﬁnition targets only the rdf nodes of type Employee. Nodes of the Client type
do not generate violations by not having an oﬃce number.
Formally, a shape is a tuple ⟨s,t,d ⟩ deﬁned by three components: (1) the
shape name s, which uniquely identiﬁes the shape; (2) the target deﬁnition t,
and (3) the set of constraints which are used in conjunction, and hence hereafter
referred to as the single constraint d. As demonstrated in Figure 1, a shacl
document is itself an rdf graph. The graph representing a shacl document is
called a shapes graph , while the graph being validated is called a data graph .
This approach to serialisation is similar to how OWL ontolog ies are serialised,
and it serves a similar purpose. Thanks to this approach, a shacl document
does not require any dedicated infrastructure to be stored a nd shared. In fact, a
shacl document can be embedded directly into the very graph it vali dates, thus
combining the shape graph and data graph into a single graph. Interestingly,
with this serialisation, a shapes graph, being an rdf graph, can be itself subject
to validation. The shacl speciﬁcation, in fact, deﬁnes a shapes graph that can
be used to validate shapes graphs.
We will now look in more details at the two major components of shapes,
namely target deﬁnitions and constraints.
3.1 shacl T arget Deﬁnitions
A shacl target deﬁnition, within a constraint, is a set of target declarations.
There are four types of target declarations deﬁned in shacl, each one taking an
rdf term c as a parameter.
Node T argets A node target declaration on c targets that speciﬁc node.
Class-based T argets If a shape has a class-based target on c, then all the
nodes in the graph that are of type ( rdf:type) c are target nodes for that
shape.
Subjects-of T argets If a shape has a subject-of target on c, then the target
nodes for that shape are all the nodes in the graph that appear as subjects
in triples with c as the predicate.
Objects-of T argets If a shape has an object-of target on c, then the target
nodes for that shape are all the nodes in the graph that appear as objects
in triples with c as the predicate.
The shape deﬁned in Figure 1 demonstrates an example of a clas s-based tar-
get targeting class :Employee. Similarly, to target a subject of a property, e.g.,
:worksAt, the second line of the shape deﬁnition would be substituted with:

## PDF page 5

A Review of shacl 5
sh:targetSubjectOf :worksAt.
Typically, a target declaration is used to select, among all the nodes in a
graph, the ones to target for constraint validation. The node target declaration,
however, behaves diﬀerently, as it targets a particular nod e regardless of whether
this node occurs in the graph or not. An important implicatio n of this is that
empty graphs are not trivially valid, since node targets can detect violations
on nodes external to the graph. If a target deﬁnition of a shap e is empty, then
that shape will have no target nodes. However, this does not m ean that the
constraint of that shape will not be evaluated on any nodes si nce, as mentioned,
other shapes can refer to it and “pass it” a node to check for co nformance.
3.2 F ocus nodes and property paths
When a target or another node is considered against a shape fo r conformity,
we call it a focus node. Initially a shape focuses on its target nodes (these ar e
the initial set of focus nodes). Additional focus nodes are o btained by following
shacl property paths, which we also refer to as just paths. shacl property paths
are a subset of sparql property paths and, as the name suggests, deﬁne paths in
the rdf graph. The simplest type of path, called predicate path, cor responds to
a single property IRI c. This path identiﬁes all the nodes that are reachable in
the rdf graph from the current focus node by following a single edge c. In other
words, this path identiﬁes all the rdf nodes in the object position of triples that
have c as the predicate and the current focus node as the subject. Mo re complex
paths can be constructed by inverting the direction of a path , by concatenating
two diﬀerent paths one after the other, or by allowing the rep etition of a path
for a minimum, maximum or arbitrary number of times.
Based on the use of property paths, shacl speciﬁcation distinguishes shapes
into two types: node shapes and property shapes. Intuitively, the constraint of a
node shape is evaluated directly on the focus nodes of the sha pe. Instead, when
using a property path, shapes must be declared as a property s hapes. These are
characterised by a path, and their constraints are evaluate d over all of the nodes
that can be reached from the focus nodes following such path. For example, the
constraint that every employee’s password must be at least 8 characters long can
be represented by a property shape that targets employee nod es, and that has
a relation such as :hasPassword as its path. In this way, the actual nodes that
must satisfy the “at least 8 characters long” constraint are not the target nodes,
but instead those that appear as objects in triples with an em ployee node as a
subject, and :hasPassword as the predicate.
3.3 shacl Constraints
The majority of the shacl recommendation is dedicated to deﬁning the diﬀerent
types of constraint components that can be used in shacl constraints. The main
type of constraint components are called core constraint components. These are
the components that shacl compliant systems typically support, and where

## PDF page 6

6 Pareti and Konstantinidis
most of the existing literature focuses on. The other main ty pe of components are
the sparql-based constraint components, that are used to embed sparql queries
into shacl constraints. This signiﬁcantly increases the expressive p ower of such
constraints. However, the inclusion of arbitrarily comple x sparql queries can
lead to performance issues, and can make such constraints ha rder to understand
and use. It is also worth noting that, outside of the shacl recommendation, a
number of additional shacl features3 are currently being designed, and some of
them might be included in further versions of shacl. In the rest of this paper
we will focus on core constraint components.
In order to better understand shacl core constraint components, we propose
a broad categorisation of these components into three main c ategories, depending
on how they are evaluated on the focus nodes. Notice that most constraint
components can be used in both node shapes and property shape s.
Graph Structure Components. These components deﬁne constraints that
are evaluated at the level of triples of the graph, and focus o n restrictions
such as the minimum and maximum cardinality that the focus no de must
have for certain paths, or the rdf class that the focus node should be a
type of. The shape deﬁned in Figure 1 demonstrates an example of a mini-
mum cardinality constraint for predicate path :hasOfficeNumber. Two other
salient constraints in this category are the property pair e quality and dis-
jointedness, that specify whether the two sets of nodes reac hable from two
diﬀerent paths must be equal or disjoint, respectively.
Filter Components. These components deﬁne constraints that are evaluated
at the level of nodes, and their evaluation is usually indepe ndent from the
triples present in the graph. Filter constraints restrict t he focus node (1) to
be a particular rdf term, (2) to be of a particular type, such as IRI, blank
node or literal, or (3) to be a literal that satisﬁes certain p roperties, such
as being of the integer datatype, or a string produced by a cer tain regular
expression.
Logical Components. Logical components deﬁne the standard logical opera-
tors of conjunction, disjunction and negation over other co nstraints.
While most core constraint components fall into one of these categories, the pair
of constraints sh:lessThan and sh:lessThanOrEquals is a notable exception, as
it is combines the properties of graph structure and ﬁlter co mponents. These
two constraints require all the nodes reachable by one path t o be literals that
are less than (resp. less than or equals) to the nodes reachab le by a second path.
It is worth noting that all constraints but one, namely sh:closed, are not
aﬀected by triples with unknown predicates (i.e. predicate s not occurring in
the shacl document). This means that if a graph is valid with respect to a
set of those constraints, it would still remain valid if new t riples with unknown
predicates are added to the graph. Thus, given a non-empty gr aphG, valid w.r.t.
a SHACL document M , graph G ∪ <s,p,o> is also valid w.r.t. M if (1) p does
not occur in M and (2)M does not contain the sh:closed constraint component.
3 https://w3c.github.io/shacl/shacl-af/ accessed on 18/6/21

## PDF page 7

A Review of shacl 7
:EmployeeShapeB a sh:PropertyShape ;
sh:targetClass :Employee ;
sh:path :hasOfficeNumber ;
sh:qualifiedMinCount 1 ;
sh:qualifiedValueShape :OfficeNumberShape .
:OfficeNumberShape a sh:NodeShape ;
sh:minLength 3 .
Fig. 2. A sample shacl document stating the constraint that every employee must
have at least one 3-characters or longer oﬃce number.
Intuitively, this means that those constraints restrict th e usage of terms from
a particular vocabulary, but they do not restrict in any way t he graph from
containing triples described using other vocabularies. Th e sh:closed component,
on the other hand, restricts the predicates of the triples th at have the focus node
as a subject to belong to a predetermined ﬁnite set. Eﬀective ly, the sh:closed
component can prohibit the use of unknown predicate relatio ns for certain nodes
in the graph, and thus prevent the inclusion of terms from oth er vocabularies.
Interestingly, component sh:closed introduces an asymmety in shacl, since it
only aﬀects triples where the focus node is the subject, and i t is not possible to
deﬁne a similar constraint for nodes in the object position.
A major feature of shacl is that constraints can use the name of a shape
to require a particular set of nodes to conform to that shape. This is called a
shape reference. An example of a shape reference is demonstrated by the shacl
document in Figure 2. This document contains shape :EmployeeShapeB which
references shape :OfficeNumberShape. The former shape restricts all of its target
nodes to having an edge :hasOfficeNumber to a node that conforms to the latter
shape, having a string length of at least three characters. V alidating the data
graph in Figure 1 with the shacl document in Figure 2 results in two violating
nodes for shape :EmployeeShapeB. The ﬁrst one is :Anne, who does not have an
oﬃce number, and the second one is :Bob, whose oﬃce numbers all contain fewer
than three digits.
Shape references can be recursive, that is, the constraint o f a shape can
reference the constraints of a second shape which, in turn, c an reference the
constraints of a third shape, and so on, creating a loop. Let Sd
0 be the set of all
the shape names occurring in a constraint d of a shape ⟨s,t,d ⟩; these are the
directly referenced shapes of s. Let Sd
i+1 be the set of shapes in Sd
i union the
directly referenced shapes of the constraints of the shapes in Sd
i .
Deﬁnition 1. A shape ⟨s,t,d ⟩ is recursive if s ∈Sd
∞; else it is non-recursive.
Deﬁnition 2. A shacl document M is recursive if it contains a recursive
shape, and non-recursive otherwise.
The semantics of recursive shacl documents are not deﬁned in the shacl spec-
iﬁcation. In Section 4 we review the oﬃcial semantics of non- recursive shacl

## PDF page 8

8 Pareti and Konstantinidis
documents, while in Section 5 we review the extended semanti cs for recursive
shacl document that have been proposed in the literature.
4 shacl Validation
In this section we present the semantics of shacl data validation, that is, the
V alidate(G, M) decision problem, for any given graph G and shacl document
M . In Section 4.1 we review how validation is deﬁned in the shacl speciﬁcation,
with the help of sparql queries. While this query-based description of shacl
semantics can be easily translated into a concrete implemen tation, it does not
lend itself well to theoretical investigation. In Section 4 .2 we will discuss an
alternative approach to deﬁning shacl semantics that is instead amenable to a
formal study.
4.1 shacl V alidation by sparql queries
The validation of an rdf graph G against a shacl document M can be per-
formed on a shape-by-shape basis. For each shape ⟨s,t,d ⟩, this process involves
verifying the fact that every node n, targeted by target deﬁnition t, satisﬁes
constraintd. Intuitively, graph G is valid w.r.t. M if and only if this fact is true
for every shape in M .
Given a graph G and a target deﬁnition t, the set of target nodes for t can
be computed by evaluating a sparql query on G for each target declaration in
t, and taking the union of the values returned by these queries . Table 1 details
the corresponding sparql query for each of the four types of target declarations
deﬁned in shacl. It should be noted that, by default, shacl does not enforce
any particular entailment regime. If an entailment regime i s being adopted, then
this should be taken into account when developing a shacl validator. For ex-
ample, if the rdfs entailment regime [7] is being considered, subclass infere nce
should be accounted for when computing the set of entities of a given class. To
accommodate for this entailment regime, the query for the no de target in Table
1 could be updated to the following one.
SELECT ?x WHERE {
?x rdf:type/rdfs:subClassOf* c
}
Once an rdf term has been identiﬁed as being in the target of a shape,
evaluating whether it conforms to the shape can be done using sparql queries. In
the shacl speciﬁcation, in fact, several core constraint components are deﬁned
with respect to sparql queries. Most notably, the semantics of shacl ﬁlter
components is in direct dependence to the semantics of sparql ﬁlter functions.
For example, the sh:minLength constraint component restricts a focus node to
having a string length equal or larger than a given number. Fo rmally, a focus node
n has a sh:minLength of j if and only if the following sparql query evaluates
to true.

## PDF page 9

A Review of shacl 9
T able 1. Target declarations and their corresponding sparql queries to compute the
set of target nodes on a given graph
Target declaration sparql query
Node target (node c) SELECT ?x WHERE { V ALUES ?x { c } }
Class target (class c) SELECT ?x WHERE { ?x rdf:type c . }
Subjects-of target (predicate c) SELECT ?x WHERE { ?x c ?y . }
Objects-of target (relation c) SELECT ?x WHERE { ?y c ?x . }
ASK {
FILTER (STRLEN(str(n)) >= j) .
}
Not all shacl constraints, however, can be easily veriﬁed by a single sparql
query. Evaluating whether a constraint that contains shape references is satisﬁed
by a focus node, in fact, might involve evaluating whether ot her constraints are
satisﬁed by other nodes which, in turn, might require even fu rther constraint
evaluations. For example, in order to evaluate whether node rdf:Carl from the
data graph in Figure 1 conforms to shape rdf:EmployeeShapeB from Figure 2,
we would need to evaluate whether his oﬃce number, namely rdf term “171”,
conforms to shape rdf:OfficeNumberShape. This is especially problematic in
case of recursion, as it could generate an inﬁnite series of c onstraint evaluations.
For non-recursive shacl documents, Corman et al. [12] showed that it is always
possible to check the validity of a graph using a single sparql query. For example,
a graph can be checked against the shacl document of Figure 2 by evaluating
the following sparql query.
SELECT ?x WHERE {
?x a :Employee .
FILTER NOT EXISTS {
?x :hasOfficeNumber ?y .
FILTER (STRLEN(str(?y)) >= 3) .
}
}
This query selects all rdf nodes of type Employee that do not have an oﬃce
number with at least three characters. Thus, any rdf term returned by this
query is a node violating a shape of the shacl document. If this query evaluates
to an empty set, then the graph that it is evaluated on is valid with respect to
the shacl document.
4.2 Shape Assignments: A T ool for Deﬁning shacl V alidation
The sparql-based approach to shacl validation does not provide a concise and
formal description of shacl semantics. Moreover, it does not provide us with a
terminating procedure to check graphs in the face of shacl recursion. In this

## PDF page 10

10 Pareti and Konstantinidis
section we review the concept of shape assignments (or just assignments) [13],
which can be used to address the above mentioned problems.
As deﬁned in Table 1, a target declaration t is a unary query over a graph
G. We denote with G |=t(n) that a node n is in the target oft with respect to a
graphG. If t is empty, no node in any graph is in the target of t. The deﬁnition
of whether a node conforms to a shape, as we previously discus sed, does not
only depend on the graph G, but it might also depend, due to shape references,
on whether other nodes conform to other shapes. Intuitively , the concept of
assignments [13] is used to keep track, for every rdf node, of all the shapes that
it conforms to, and all of those that it does not. Given a docum ent M and a
graph G, we denote nodes(G, M) the set of nodes in G together with any extra
ones referenced by the node target declarations in M . With shapes(M) we refer
to all the shape names in a document M .
Deﬁnition 3. Given a graph G, and a shacl documentM , an assignmentσ for
G andM is a function mapping nodes in nodes(G, M), to subsets of shapes(M) ∪
{¬s|s ∈ shapes(M)}, such that for all nodes n and shape names s,σ (n) does not
contain both s and ¬s.
Expression /llbracketd/rrbracketn,G,σ denotes the evaluation of constraint d on a node n w.r.t. a
graphG under an assignment σ , as deﬁned in [13]. If /llbracketd/rrbracketn,G,σ is True (resp. False)
we say that node n satisﬁes (resp. does not satisfy) constraint d w.r.t. G under
σ . For any graph G and assignment σ , fact s ∈σ (n) (resp. ¬s ∈σ (n)) denotes
the fact that node n conforms (resp. does not conform) to s w.r.t. G under σ .
Expression /llbracketd/rrbracketn,G,σ evaluates to True, False or Undeﬁned values of Kleene’s 3-
valued logic, and the truth value of any shape reference in d is computed using
the assignment (it should be noted that the Undeﬁned value never occurs in non-
recursive shapes, but it is used to deﬁne possible extended s emantics in the face
of recursion). In other words, whenever a truth value in the e valuation of /llbracketd/rrbracketn,G,σ
depends on whether another node j conforms to a shape s′, with constraints d′,
this is not resolved by evaluating /llbracketd′/rrbracketj,G,σ, but instead it is True if s′ ∈ σ (j),
False if ¬s′ ∈σ (j), or else Undeﬁned. This, in turn, eliminates the problem of a
potentially inﬁnite series of constraint evaluations.
The semantics of shacl validation can be deﬁned with respect to a particular
type of assignments, called faithful [13].
Deﬁnition 4. For all graphs G, shacl documents M and assignments σ , as-
signment σ is faithful w.r.t. G and M , denoted with (G,σ ) |= M , if the fol-
lowing two conditions hold for any shape ⟨s,t,d ⟩ in shapes(M) and node n in
nodes(G, M) :
(1) s ∈σ (n) iﬀ /llbracketd/rrbracketn,G,σ is True; and ¬s ∈σ (n) iﬀ /llbracketd/rrbracketn,G,σ is False;
(2) if G |=t(n) then s ∈σ (n).
Condition (1) ensures that the facts denoted by the assignme nt are correct;
while condition (2) ensures that the assignment is compatib le with the target
deﬁnitions. Condition (2) is trivially satisﬁed for shacl documents where all
target deﬁnitions are empty. Later we will want to discuss as signments where

## PDF page 11

A Review of shacl 11
the ﬁrst property of Def. 4 holds, but not necessarily the sec ond, in order to
reason about the existence of alternative assignments that are correct (as in,
they satisfy the ﬁrst part of Def. 4) but that are not faithful . In fact, these
will be faithful assignments to a document that is “stripped empty” of target
deﬁnitions. Let M \t denote the shacl document obtained from substituting
all target deﬁnitions in shacl document M with the empty set. The following
lemma holds:
Lemma 1. For all graphs G, shacl documents M and assignments σ , condi-
tion (1) from Deﬁnition 4 holds for any shape s in shapes(M) and node n in
nodes(G, M) iﬀ (G,σ ) |=M \t.
The existence of a faithful assignment is a necessary and suﬃ cient condition
for validation for non-recursive shacl documents [13]. As we will see later, this
is also necessary condition for all the other extended seman tics.
Deﬁnition 5. A graph G is valid w.r.t. a non-recursive shacl documentM if
there exists an assignment σ such that (G,σ ) |=M .
5 shacl Recursion
The semantics of recursion in shacl documents is left undeﬁned in the shacl
speciﬁcation [23], and this gives rise to several possible i nterpretations. In this
section we consider extended semantics of shacl that deﬁne how to validate
graphs against recursive shacl documents. We focus on existing extended se-
mantics that follow monotone reasoning. These can be charac terised by two
dimensions, namely the choice between partial and total assignments [13] and
between brave and cautious validation [3], which we will subsequently deﬁne.
Put together, these two dimensions deﬁne the four extended s emantics of brave-
partial, brave-total, cautious-partial and cautious-total. We will not go into the
details of the less obvious dimension of stable-model semantics [3], which relates
shacl to non-monotone reasoning in logic programs.
As mentioned in the previous section, assignments can speci fy a truth value
of True, False or Undeﬁned to whether a node conforms to given shape. The truth
value of Undeﬁned, which does not occur in non-recursive shacl documents, can
instead play an important role in validating shacl under recursion. Intuitively,
this happens during validation, when recursion makes it imp ossible for a node n
to either conform or not to conform to a shape s but, at the same time, validity
does not depend on whether n conforms to shape s or not. Consider for example
the following shacl document, containing a single shape ⟨s∗, ∅,d ∗⟩ (with name
:InconsistentS in this example). This shape is deﬁned as the negation of itse lf,
that is, given a node n, a graph G and an assignment σ , fact /llbracketd∗/rrbracketn,G,σ is true iﬀ
¬s∗ ∈σ (n), and false iﬀ s∗ ∈σ (n).
:InconsistentS a sh:NodeShape ;
sh:not :InconsistentS .

## PDF page 12

12 Pareti and Konstantinidis
It is easy to see that any assignment that maps a node to either s∗ or ¬s∗
is not faithful, as it would violate condition (1) of Deﬁniti on 4. However, an
assignment that maps every node of a graph to the empty set wou ld be faithful
for that graph and document {s∗}. Intuitively, this means that nodes in the
graph cannot conform nor not conform to shape s∗, but since this shape does
not have any target node to validate, then the graph can still be valid. The
fact of whether nodes conform or not conform to shape s∗ can thus be left as
“undeﬁned”.
This type of validation, for recursive shacl documents, is called validation
with partial assignments. More speciﬁcally, validation un der brave-partial se-
mantics simply extends the criterion of Def. 5 to recursive shacl documents.
All other extended semantics are constructed by adding addi tional conditions
to brave-partial semantics. The term “partial” should not b e interpreted as the
fact that it describes only “part” of nodes of a graph, or that it describes the
relationship of a node to only “part” of the shapes. Within a p artial assignment,
the conformance of every node to every shape is precisely spe ciﬁed by one of
three truth values, and the term “partial” only indicates th at one of these three
truth values is Undeﬁned.
Deﬁnition 6. A graph G is valid w.r.t. a shacl document M under brave-
partial semantics if there exists an assignment σ such that (G,σ ) |=M .
In the shacl speciﬁcation, nodes either conform to, or not conform to a gi ven
shape, and the concept of an “undeﬁned” level of conformance is arguably alien
to the speciﬁcation. It is natural, therefore, to consider r estricting the evaluation
of a constraint to the True and False values of boolean logic. This is achieved by
restricting assignments to be total.
Deﬁnition 7. An assignment σ is total w.r.t. a graph G and a shacl document
M if, for all nodes n in nodes(G, M) and shapes ⟨s,t,d ⟩ in M , either s ∈σ (n)
or ¬s ∈σ (n).
For any graph G and shacl document M we denote with AG,M and AG,M
T ,
respectively, the set of assignments, and the set of total as signments for G and
M . Trivially,AG,M
T ⊆AG,M holds.
Deﬁnition 8. A graph G is valid w.r.t. a shacl documentM under brave-total
semantics if there exists an assignment σ in AG,M
T such that (G,σ ) |=M .
Since total assignments are a more speciﬁc type of assignmen ts, if a graph
G is valid w.r.t. a shacl document M under brave-total semantics, than it is
also valid w.r.t. M under brave-partial semantics. The reverse, instead, is on ly
true for non-recursive shacl documents. In fact, as shown in [13], if there ex-
ists a faithful assignment for a graph G and a non-recursive document M , then
there exists also a total faithful assignment for G and M . Therefore, the deﬁ-
nition of validity under brave-total semantics (Def. 8), fo r non-recursive shacl
documents, coincides with the standard deﬁnition of valida tion (Def. 5).

## PDF page 13

A Review of shacl 13
While total assignments can be seen as a more natural way of in terpreting
the shacl speciﬁcation, they are not without issues when recursive shacl doc-
uments are considered. Going back to our previous example, w e can notice that
there cannot exist a total faithful assignment for the shacl document containing
shape :InconsistentS, for any non-empty graph. This is a trivial consequence of
the fact that no node can conform to, nor not conform to, shape :InconsistentS.
This, however, is in contradiction with the shacl speciﬁcation, which implies
that a shacl document without target declarations in any of its shapes (s uch
as the one in our example) should trivially validate any grap h. If there are no
target declarations, in fact, there are no target nodes on wh ich to verify the
conformance of certain shapes, and thus no violations shoul d be detected.
The second and last dimension that we consider is the diﬀeren ce between
brave and cautious validation. When a shacl document M is recursive, there
might exist multiple assignments σ satisfying property (1) of deﬁnition 4, that
is, such that (G,σ ) |= M \t. Intuitively, these can be seen as equally “correct”
assignments with respect to the constraints of the shapes, a nd brave validation
only checks whether at least one of them is compatible with th e target deﬁnitions
of the shapes. Cautious validation, instead, represents a s tronger form of valida-
tion, where all such assignments must be compatible with the target deﬁnitions.
Deﬁnition 9. A graph G is valid w.r.t. a shacl documentM under cautious-
partial (resp. cautious-total) semantics if it is (1) valid under brave-partial
(resp. brave-total) semantics and (2) for all assignments σ in AG,M (resp.
AG,M
T ), it is true that if (G,σ ) |=M \t holds then (G,σ ) |=M also holds.
To exemplify this distinction, consider the following shacl document M1.
This document requires the daily special of a restaurant, no de :DailySpecial,
to be vegetarian, that is, to conform to shape :VegDishShape. This shape is
recursively deﬁned as follows. Something is a vegetarian di sh if it contains an
ingredient, and all of its ingredients are vegetarian, that is, entities conforming
to the :VegIngredientShape. A vegetarian ingredient, in turn, is an ingredient
of at least one vegetarian dish.
:VegDishShape a sh:PropertyShape ;
sh:targetNode :DailySpecial ;
sh:path :hasIngredient ;
sh:minCount 1 ;
sh:qualifiedMaxCount 0 ;
sh:qualifiedValueShape [ sh: not :VegIngredientShape ] .
:VegIngredientShape a sh:PropertyShape ;
sh:path [ sh:inversePath :hasIngredient ] ;
sh:node :VegDishShape .
Consider now a graph G1 containing the following triple.
:DailySpecial :hasIngredient :Chicken .

## PDF page 14

14 Pareti and Konstantinidis
Due to the recursive deﬁnition of :VegDishShape, there exist two diﬀerent assign-
mentsσ1 and σ2, which are both faithful for G1 and M \t
1 . In σ1, no node in G1
conforms to any shape, while σ2 diﬀers from σ1 in that node :DailySpecial con-
forms to :VegDishShape and node :Chicken conforms to :VegIngredientShape.
Essentially, either both the dish and the ingredient from gr aph G1 are vege-
tarian, or neither is. Therefore, σ2 is faithful for G1 and M1, while σ1 is not.
The question of whether the daily special is a vegetarian dis h or not can be
approached with diﬀerent levels of “caution”. Under brave v alidation, graph G1
is valid w.r.t. M1, since it is possible that the daily special is vegetarian. C au-
tious validation, instead, takes the more conservative app roach, and under its
deﬁnition G1 is not valid w.r.t. M1, since it is also possible that the daily special
is not vegetarian. When analysing such recursive deﬁnition s, one might want to
exclude “unfounded” assignments, that is, assignments tha t assign certain shapes
to a node for no other reason than to allow the validation of a g raph. This is
achieved by the recursive semantics for shacl proposed in [3], which is based on
the concept of stable models from Answer Set Programming.
For each extended semantics, the deﬁnition of validity of a g raph G with
respect to a shacl document M , denoted by G |= M , is summarised in the
following list.
brave-partial there exists an assignment that is faithful w.r.t. G and M ;
brave-total there exists an assignment that is total and faithful w.r.t. G and
M ;
cautious-partial there exists an assignment that is faithful w.r.t. G and M ,
and every assignment that is faithful w.r.t. G and M \t is also faithful w.r.t.
G and M .
cautious-total there exists an assignment that is total and faithful w.r.t. G
and M , and every assignment that is total and faithful w.r.t. G and M \t is
also faithful w.r.t. G and M .
6 Formal languages for shacl
In this section we review the two main formal languages that h ave been proposed
to model the semantics of shacl. We ﬁrst discuss a complete ﬁrst-order formal-
isation of shacl, which can be used to study a number of decision problems.
We then present a simpliﬁed language that eﬀectively models shacl constraints
for the purpose of validation.
6.1 SCL, A First-Order Language for shacl
In order to formally study shacl, it is convenient to abstract away from the syn-
tax of its rdf and sparql representations. The SCL ﬁrst order language [37,36] is
currently the only complete formalisation of shacl into a formal logical system.
The expressiveness of this language covers all of the shacl target declarations
and all of the shacl core constraint components, including the ﬁlter compo-
nents, which are less commonly studied. This language captu res the semantics

## PDF page 15

A Review of shacl 15
of whole shacl documents, and it can be used to study a number of related
decision problems, including validation. The relation bet ween shacl and SCL
is given by translation τ [36], such that, given a shacl document M , the ﬁrst
order sentence τ(M ) is the translation of M into SCL. We identify the inverse
translation with τ−.
Before deﬁning SCL and its properties, we must deﬁne how rdf graphs and
assignments are modelled in this logical framework. The dom ain of discourse is
assumed to be the set of rdf terms. Triples are modelled as binary relations,
with atom R(s,o ) corresponding to triple <s,R,o> . A minus sign identiﬁes the
inverse role, i.e. R−(s,o ) = R(o,s ). Binary relation name isA represents class
membership triples <s, rdf:type,o> as isA(s,o ). Assignments are modelled
with a set of monadic relations Σ , called shape relations. Each shacl shape s
is associated with a unique shape relation Σ s in SCL. Facts Σ (x) (resp. ¬Σ (x))
describe an assignment σ such that s ∈σ (x) (resp. ¬s ∈σ (x)). Since this logical
framework adopts boolean logic, ∀x.Σ (x) ∨ ¬Σ (x) holds, by the law of excluded
middle. Thus shape relations deﬁne total assignments.
Given a graph G and an assignment σ , we now deﬁne their respective trans-
lations Gτ and σ τ into ﬁrst order structures.
Deﬁnition 10. Given a graph G, fact p(s,o ) is true in the ﬁrst order structure
Gτ iﬀ <s,p,o> ∈G.
Deﬁnition 11. Given a total assignment σ , fact Σ s(n) is true in the ﬁrst order
structureσ τ iﬀ s ∈σ (n).
Deﬁnition 12. Given a graph G and a total assignment σ , the ﬁrst order struc-
tureI induced by G and σ is the disjoint union of structures Gτ and σ τ . Given
a ﬁrst order structure I: (1) the graph G induced by I is the graph that contains
triple <s,p,o> iﬀ I |=p(s,o ) and (2) the assignment σ induced by I is the as-
signment such that, for all nodes n and shape relations Σ s, fact s ∈σ (n) is true
iﬀ I |=Σ s(n) and ¬s ∈σ (n) iﬀ I ̸|=Σ s(n).
The existence of faithful assignments using SCL and its standard model-
theoretic semantics is presented in the following theorem [ 37]. Trivially, this
also deﬁnes what condition, in SCL, corresponds to validation under the brave-
total extended semantics (Def. 8), which also deﬁnes valida tion for non-recursive
shacl documents (Def. 5).
Theorem 1. For any graph G, total assignment σ and shacl documentM , it
is true that (G,σ ) |=M iﬀ I |=τ(M ), whereI is the ﬁrst order structure induced
by G and σ .
For any ﬁrst order structure I and SCL formulaφ, it is true I |=φ iﬀ (G,σ ) |=
τ−(φ), where G and σ are, respectively, the graph and assignment induced by I.
Sentences in the SCL language follow the ϕ grammar in Deﬁnition 13.
Deﬁnition 13. The SHACL ﬁrst order language ( SCL, for short) is the set of
ﬁrst order sentences built according to the following context-free grammar, wher e

## PDF page 16

16 Pareti and Konstantinidis
T able 2. Translation of a shape with name s with a target deﬁnition t, into an SCL
target axiom.
Target declaration in t SCL target axiom
Node target (node c) Σ s(c)
Class target (class c) ∀x. isA(x, c) →Σ s(x)
Subjects-of target (relation R) ∀x,y.R (x,y ) →Σ s(x)
Objects-of target (relation R) ∀x,y.R − (x,y ) →Σ s(x)
c is a constant from the domain of rdf terms,Σ is a shape relation, F is a ﬁlter
relation, with shape relations disjoint from ﬁlter relatio ns, R is a binary-relation
name, ⋆ indicates the transitive closure of the relation induced by π (x,y ), the
superscript ± refers to a relation or its inverse, and n ∈ N.
ϕ := ⊤ | ϕ ∧ϕ
|Σ (c) | ∀x. isA(x, c) →Σ (x) | ∀x,y.R ±(x,y ) →Σ (x)
| ∀x.Σ (x) ↔ψ (x);
ψ (x) := ⊤ | ¬ψ (x) |ψ (x) ∧ψ (x) |x = c |F (x) |Σ (x) | ∃y.π (x,y ) ∧ψ (y)
| ¬∃y.π (x,y ) ∧R(x,y ) [D]
| ∀y.π (x,y ) ↔R(x,y ) [E]
| ∀y,z.π (x,y ) ∧R(x,z ) →ς(y,z ) [O]
| ∃ ≥ny.π (x,y ) ∧ψ (y); [C]
π (x,y ) := R±(x,y )
| ∃z.π (x,z )∧π (z,y ) [S]
|x =y ∨π (x,y ) [Z]
|π (x,y )∨π (x,y ) [A]
| (π (x,y ))⋆; [T]
ς(x,y ) := x< ± y |x ≤± y.
Symbolϕ corresponds to a shacl document. An SCL sentence could be empty
(⊤), a conjunction of documents, a target axiom representing a target deﬁnition
(a production of the 3rd, 4th and 5th production rule) or a constraint axiom rep-
resenting a constraint (a production of the last production rule). Target axioms
take one of three forms, based on the type of target declarati ons. The translation
of shacl target declarations into SCL target axioms is summarised in Table 2.
Letters in square brackets are annotations for naming SCL components and thus
are not part of the grammar. These letters are essentially ﬁr st-letter abbrevia-
tions of prominent shacl components (that together deﬁne fragments of SCL),
and are also listed in Table 3.
The non terminal symbol ψ (x) corresponds to the subgrammar of the shacl
constraints components. Within this subgrammar, ⊤ identiﬁes an empty con-
straint,x = c a constant equivalence constraint and F a monadic ﬁlter relation

## PDF page 17

A Review of shacl 17
T able 3. Relation between prominent shacl components and SCL expressions.
Abbr. Name shacl component Corresponding expression
S Sequence Paths Sequence Paths ∃z.π (x,z ) ∧π (z,y )
Z Zero-or-one Paths sh:zeroOrOnePath x =y ∨π (x,y )
A Alternative Paths sh:alternativePath π (x,y ) ∨π (x,y )
T Transitive Paths sh:zeroOrMorePath
sh:oneOrMorePath (π (x,y ))⋆
D Property Pair Disjointness sh:disjoint ¬∃y.π (x,y ) ∧R(x,y )
E Property Pair Equality sh:equals ∀y.π (x,y ) ↔R(x,y )
O Property Pair Order sh:lessThan
sh:lessThanOrEquals x ≤± y and x< ± y
C Cardinality Constraints
sh:qualifiedValueShape
sh:qualifiedMinCount
sh:qualifiedMaxCount
∃≥ ny.π (x,y ) ∧ψ (y)
with n ̸= 1
(e.g. F IRI(x), true iﬀ x is an IRI). Filters components are captured by F (x)
and the O component. The C component captures qualiﬁed value shape cardinal-
ity constraints. The E, D and O components capture the equality, disjointedness
and order property pair components. The π (x,y ) subgrammar models shacl
property paths. Within this subgrammar S denotes sequence paths, A denotes
alternate paths, Z denotes a zero-or-one path and T denotes a zero-or-more path.
Translationτ results in a subset of SCL formulas, called well-formed deﬁned
subsequently, and the inverse translation τ− only takes well formed sentences as
an input. An SCL formulaφ is well-formed iﬀ for every shape relation Σ , formula
φ contains exactly one constraint axiom with relation Σ on the left-hand side of
the implication. Intuitively, this condition ensures that every shape relation is
“deﬁned” by a corresponding constraint axiom. The translat ion of the document
from Fig. 2, into a well-formed SCL sentence, via τ, is the following. Arguably,
this logic notation might seem easier to read and understand than the SHACL
syntax of Fig. 2.
(
∀x. isA(x, :Employee) →Σ :EmployeeShapeB(x)
)
∧
(
∀x.Σ :EmployeeShapeB(x) ↔ ∃y.R :hasOfficeNumber(x,y ) ∧Σ :OfficeNumberShape(y)
)
∧
(
∀x.Σ :OfficeNumberShape(x) ↔F length≥3(y)
)
The language deﬁned without any of these constructs is calle d the base lan-
guage, denoted ∅ . On top of the base language diﬀerent syntactic fragments of
SCL are deﬁned by considering diﬀerent combinations of feature s allowed. We
name these fragments by concatenating the letters that repr esent the features
allowed, into a single name. For example, SA identiﬁes the fragment that only
allows the base language, sequence paths and alternate path s. This means that
in order to write an SCL document in SA, one can only use the production rules

## PDF page 18

18 Pareti and Konstantinidis
of Def. 13 that are not annotated with any feature (base langu age) or those
identiﬁed by abbreviations S and A.
The shacl speciﬁcation presents an unusual asymmetry in the fact that
equality, disjointedness and order components force one of their two path ex-
pressions to be an atomic relation. This can result in situat ions where the order
constraints can be deﬁned in just one direction, since only t he less-than and less-
than-or-equal property pair constraints are deﬁned in shacl. The O fragment
models a more natural order comparison that includes the > and ≥ compo-
nents. The fragment where the order relations in the ς(x,y ) subgrammar cannot
be inverted is denoted O’.
When interpreting an SCL sentence, particular care should be paid to the
semantics of ﬁlter relation. The interpretation of each ﬁlt er relation, such as
F IRI(x), is the subset of the domain of discourse on which the ﬁlter is true. This
interpretation is constant across all models, and deﬁnes th e semantics of the
ﬁlter. When considering the decision problem of validation , ﬁlter relations in SCL
must be suitably deﬁned by interpreted relations (similarl y to how the equality
operator is). When considering additional decision proble ms, such as satisﬁability
and containment (which will be discussed in Section 7), the s emantics of ﬁlters
can be axiomatisatised, thus removing the need for special i nterpreted relations.
The ﬁlter axiomatisation presented in [37] captures the sem antics of all SHACL
ﬁlters with the single exception of sh:pattern, as this ﬁlter deﬁnes complex
non-standard regular expressions based on the sparql regex function [42].
6.2 L, a Language for shacl Constraint V alidation
Another major language used to study shacl is L which was presented in [13]
and paved the way to subsequent formal studies of shacl. The L language
diﬀers from SCL in scope and purpose. While SCL sentences describe whole shacl
documents, sentences in L describe individual shacl constraints. The L language
is primarily designed to investigate the complexity of shacl validation. As such,
it relies on assumptions that do not hold when studying other decision problems
such as satisﬁability and containment, which, instead, can be studied using SCL.
In particular, L assumes that all ﬁlter components can be evaluated on a node i n
constant time, and thus are all equivalent, for the purposes of validation. Thanks
to this reduced scope, L seems less complex than SCL, and it is a useful formalism
to study the evaluation of shacl constraints. The semantics of an L sentence
φ is deﬁned in [13] through the use of faithful assignments. In particular, [13]
ﬁxes a lookup table that provides the truth value of the evalu ation of φ on a
node n for a graph G and an assignment σ . Instead, SCL relies on the standard
model-theoretic semantics.
The grammar of L sentences is given next. In this grammar s is a shape
name; I is an IRI; r is a shacl property path; n is a positive integer.
φ := ⊤ |s |I |φ 1 ∧φ 2 | ¬φ | ≥ nr.φ | EQ (r1,r 2)
Table 4 deﬁnes the correspondence between L and the ψ (x) sub-grammar of
SCL. It is easy to see that L sentences correspond to a subset of the ψ (x) sub-

## PDF page 19

A Review of shacl 19
T able 4. Correspondence between an L sentence φ , and SCL ψ φ(x) expressions, such
that a constraint φ is satisﬁed on a node n w.r.t. a graph G and an assignment σ iﬀ
I |=ψ φ(n), where I is the ﬁrst order structure induced by G andσ . It is assumed that
paths are expressed using the π (x,y ) subgrammar of SCL, and that r2 is an IRI.
L expression φ Corresponding SCL ψ φ(x)
⊤ ⊤
s Σ s(x)
I x =I
φ 1 ∧φ 2 ψ φ1 (x) ∧ψ φ2 (x)
¬φ ¬ψ φ(x)
≥nr.φ ∃≥ ny.r (x,y ) ∧ψ φ(y)
EQ (r1,r 2) ∀y.r 1(x,y ) ↔r2(x,y )
grammar of SCL, assuming that r2 denotes a predicate path. This assumption
is required as in L both arguments of EQ (r1,r 2), which captures the shacl
equality operator ( sh:equals), are path expressions. This is a generalisation
of shacl, since the shacl speciﬁcation requires one of the two paths to be a
simple predicate path, or in other words, an IRI. It should al so be noted that L
does not model property pair order components (denoted O in SCL), and that the
sh:closed component is modelled using path expression operators not s upported
by shacl paths. The shacl disjoint constraint component (denoted D in SCL) is
only implicitly included in L when considering recursion. It is possible, in fact,
to represent a disjoint constraint component in L using two auxiliary recursive
shapes [13].
7 shacl Decision Problems
Several existing pieces of work in the literature focus on shacl, and several
related decision problems have been investigated. In Secti on 7.1 we review ex-
isting work on the core decision problem for shacl, namely validation. Unlike
validation, which studies the relationship between a shacl document and an
rdf graph, the decision problems of satisﬁability and containment, reviewed in
Section 7.2, focus on intrinsic properties of SHACL documen ts and their com-
ponents.
7.1 V alidation
Validation is a core decision problem for shacl, since the main application of
this language is the validation of rdf graphs. This decision problem is decidable
for all of the semantics discussed in this article, includin g the four extended
semantics. The complexity lower bounds for validation, how ever, depend on the
fragment of shacl being considered. Table 5 lists the data complexity of three
fragments of shacl given in [13,3]. The three fragments are (1) shaclnon−rec,

## PDF page 20

20 Pareti and Konstantinidis
T able 5. Data complexity of shacl validation, results from [12].
Fragment Data complexity of validation
shaclnon− rec NL-c
shacl+ PTIME-c
shaclrec NP-c
the fragment of non-recursive shacl documents built using L constraints; (2)
shacl+, the fragment of shacl documents built using L constraints with a
restricted use of negation, that is, substituting the ¬φ production rule of L into
φ 1 ∨ φ 2; and (3) shaclrec, the fragment of shacl documents built using L
constraints. The most expressive of these fragments, shaclrec, is NP-complete
in data complexity.
7.2 Satisﬁability and Containment
Satisﬁability and containment are standard decision probl ems that have been
investigated in the context of shacl. These two decision problems, unlike vali-
dation, do not take a graph as an input. Instead, they focus on shacl documents,
shapes or constraints. Given any notion of validity from one of the semantics de-
ﬁned earlier, the following decision problems are deﬁned. F or simplicity, when
discussing satistiability and containment, we will assume the use of the semantics
of validation from Deﬁnitions 8 and 5.
Deﬁnition 14. A shacl document M is satisﬁable iﬀ there exists a graph G
such that G |= M . Deciding whether a shacl document is satisﬁable is the
decision problem of shacl satisﬁability .
Deﬁnition 15. shacl Containment: For all shacl documentsM1, M2, we
say that M1 is contained in M2, denoted M1 ⊆ M2, iﬀ for all graphs G, if
G |= M1 then G |= M2. Deciding whether a shacl document is contained in
another is the decision problem of shacl containment.
Two shacl documents M1 and M2 that are contained in each other ( M1 ⊆
M2 and M2 ⊆ M1) are semantically equivalent . Two semantically equivalent
documents are not necessarily equivalent syntactically, s ince in shacl the same
constraint can be expressed using diﬀerent sets of shapes.
The satisﬁability and containment decision problems for shacl can be poly-
nomially reduced to the satisﬁability decision problem for SCL, deﬁned as follows
in the natural way [37].
Deﬁnition 16. An SCL sentenceφ is satisﬁable iﬀ there exists structure Ω such
thatΩ |=φ. Deciding whether a SCL sentence is satisﬁable is the decision problem
of SCL satisﬁability .

## PDF page 21

A Review of shacl 21
∅
AOS C E
S EA OS CS OS A A C E O E C A E
S A ES E OS A CS A O S E C A E O A E C
S Z A ES Z A D S A D E Z A D E
S Z A D ES A E OS Z A D CS Z A D O S A E C Z A D E O Z A D E C
S Z A T ES Z A T D S A T D E Z A T D E
S Z A T D ES Z A T D O S Z A T D C Z A T D E CZ A T D E O
S Z A T D E OS Z A T D O C S Z A T D E C Z A T D E O C
Fig. 3. [37] Decidability and complexity map of SCL satisﬁability. Round (blue) and
square (red) nodes denote decidable and undecidable fragme nts, respectively. Solid bor-
ders on nodes correspond to theorems in this paper, while das hed borders are implied
results. Directed edges indicate inclusion of fragments, w hile bidirectional edges de-
note polynomial-time reducibility. Solid edges are prefer red derivations to obtain tight
results, while dotted ones leads to worst upper-bounds or mo del-theoretic properties.
Finally, a light blue background indicates that the fragmen t enjoys the ﬁnite-model
property, while those with a light red background do not sati sfy this property.
This reduction allows us to study the decidability and compl exity of the
shacl satisﬁability and containment problems for a given shacl fragment by
studying the decidability and complexity of SCL satisﬁability, for the correspond-
ing fragments. The results of this study, published in [37], are summarised in Fig-
ure 3. Negative results indicate the undecidability of both the SCL fragment, and
the corresponding shacl fragment. Positive results, shown in round blue in the
ﬁgure, indicate that both satisﬁability and containment ar e decidable, for that
fragment of non-recursive shacl, and are accompanied with complexity upper-
bounds. Starting from the negative results, shacl satisﬁability and containment
is, in general, undecidable. This was shown even for several non-recursive frag-
ments, through a semi-conservative reduction from the stan dard domino prob-
lem [50,5,39], which is an undecidable decision problem. Mo re speciﬁcally, the
shacl satisﬁability problems for the S O, S A C, S E C, S E O’, and S Z A E fragments
are undecidable [37].

## PDF page 22

22 Pareti and Konstantinidis
Positive results are obtained by noticing that several SCL fragments are in-
cluded in decidable fragments of ﬁrst order logic. For examp le, the S Z A T D
fragment of SCL is included in the extension of the unary-negation fragment
of ﬁrst-order logic with arbitrary transitive relations, w hich can be solved in
2ExpTime [1,20,15]. The complexity upper bounds identiﬁed in [37] for shacl
fragments range from ExpTime to 2ExpTime. Both decision pro blems are de-
ﬁned over shacl documents which, similarly to the schema of a dataset, could
be assumed to be of small or constant size.
Up until this point we considered the satisﬁability and cont ainment prob-
lems deﬁned at the level of shacl documents. However, it is possible to study
variations of these problems at diﬀerent levels of granular ity. For example, the
satisﬁability and containment problems at the level of shacl constraints are
deﬁned in [37], and are shown to be reducible to the problem of shacl satisﬁa-
bility. An approach that uses Description Logics Reasoning is presented in [26]
to compute shape containment, that is, containment at the level of shapes, for a
restrictive fragment of shacl, which however allows recursion.
8 Inference Rules and the Schema Expansion
Datasets are often dynamic objects, which are frequently su bject to modiﬁca-
tion. When an rdf graph is modiﬁed, its validity w.r.t. a shacl document might
change. If the modiﬁcations that a dataset undergoes are com pletely arbitrary,
then it is not possible to make predictions regarding validi ty, and the dataset
might need to be re-validated after each modiﬁcation. Many t ypes of modiﬁca-
tions that can be applied on a dataset, however, are predicta ble or a result of
some reasoning process. In particular, many types of modiﬁc ations can be rep-
resented as inference rules B →H, where a set of facts H, called the head are
added to a dataset whenever a query B, called the body, ﬁnds a match on the
dataset. Given an rdf graph G, and a set of inference rules R, it is possible to
compute graph G′, closure of G under R, by applying the chase algorithm [4].
The chase algorithm, intuitively, consists in repeatedly a pplying the rules of R
on G until convergence. For simplicity, we assume that the chase algorithm is
guaranteed to terminate for the inference rules considered .
Assuming graph G is valid w.r.t. to a shacl document M , the approach
presented in [38], called schema expansion , allows us to predict whether the
graph closure G′ will still be valid w.r.t. M without having to validate G′ against
M . In particular, given a shacl documentM and a set of inference rules R, the
schema expansion process computes the “maximal sub-docume nt” of M which
will still validate G after the rule applications. That is, the schema expansion i s
a shacl document M ′, called schema consequence, such that (1) M ⊆M ′ (i.e.,
M ′ is a subset of the restrictions of M ); (2) validity is preserved after closure,
that is, for any graph G valid w.r.t.M , its closure G′ underR is valid w.r.t. M ′;
and (3)M ′ is “minimally-containing”, i.e., there is no document M ′′ that satisﬁes
conditions (1) and (2) and such that that M ′′ ⊂ M ′. If a schema consequence
M ′ of a shacl document M under inference rules R is semantically equivalent

## PDF page 23

A Review of shacl 23
to M , then any graph G, valid w.r.t. M is guaranteed to remain valid w.r.t.
M after computing its closure under R. In other words, this means that the
application of rules R cannot “invalidate” graphs valid w.r.t. document M .
Consider, for example, the following graph G1, which describes :Eve, a man-
ager of the company in the IT department, and one of her subord inates :Fiona.
:Eve a :Manager ;
:hasDepartment "IT" .
:Fiona a :Employee ;
:hasManager :Eve .
This graph is valid w.r.t. the following shacl document M1, which states that
each employee must have a manager, and each manager must have a department.
:SubordinateS a :PropertyShape ;
sh:targetClass :Employee ;
sh:path :hasManager ;
sh:minCount 1 .
:ManagerS a sh:PropertyShape ;
sh:targetClass :Manager ;
sh:path :hasDepartment ;
sh:minCount 1 .
Consider now the set of inference rules R1 = {r1,r 2}, where rules r1 and r2
are deﬁned as follows. For simplicity, we represent both the head and the body
of rules as sparql graph patterns, which are interpreted as sparql construct
queries where the where and construct clauses are the body and the head,
respectively. Ruler1 states that every manager can be inferred to be an employee,
andr2 states that everyone can be inferred to be in the same departm ent as their
manager.
r1 = {?x rdf:type :Manager} → {?x rdf:type :Employee}
r2 = {?x :hasManager ?y . ?y :hasDepartment ?z} → {?x :hasDepartment ?z}
The closure of graph G1 under rules R1 is the following graph G2.
:Eve a :Manager ;
a :Employee ;
:hasDepartment "IT" .
:Fiona a :Employee ;
:hasManager :Eve ;
:hasDepartment "IT" .
Notice that graph G2 is not valid w.r.t. M1, since :Eve violates :SubordinateS,
but it is valid w.r.t. another document M2 which only contains shape :ManagerS.
In fact, M2 is a schema consequence of M1 andR1. Therefore, we know that the
closure under R1 of any graph valid w.r.t. M1 will validate shape :ManagerS, but
it might not validate :SubordinateS.
Two approaches to compute the schema expansion are presente d in [38], for
datalog [9] inference rules without negation. The ﬁrst base d on the concept

## PDF page 24

24 Pareti and Konstantinidis
of critical instance [30], and the second an optimisation of the ﬁrst. These ap-
proaches are only deﬁned on a fragment of shacl that, although restricted, is suf-
ﬁcient to express common constraints for rdf validation, such as the Data Qual-
ity Test Patterns typedep, typrodep, pvt, rdfs-domain and rdfs-range
in the categorisation by Kontokostas et al. [24]. Intuitive ly, the diﬃculty in com-
puting a schema expansion lies in having to consider all poss ible graphs that are
valid w.r.t. a shacl document, and their interactions with arbitrarily complex
inference rules.
9 Applications, Tools and Implementations
Over a few years since reaching its status as a W3C recommenda tion, the level
of maturity and adoption of the shacl technology has been steadily increasing.
In this section we review existing shacl implementations, tools designed to
facilitate the creation and management of shacl documents, and documented
usages of shacl in practical applications.
9.1 T ools for shacl V alidation
The availability of mature tools is often a crucial requirem ent for the widespread
adoption of a technology. To date, shacl validation has been integrated in a
number of mainstream tools and triplestores. 4 An example of this is RDF4J, 5
a Java framework for managing rdf data, which now includes an engine for
shacl validation. The RDF4J framework is integrated in a number of projects,
most notably the GraphDB 6 triplestore. Other shacl-enabled databases include
AllegroGraph7 by Franz Inc, Apache Jena 8 by Apache, and Stardog 9 by Stardog
Union Inc. A benchmark for the comparison of diﬀerent shacl implementation
was proposed in [41], along with results for four diﬀerent da tabases. A shacl
implementation is also available for Python through the pyS HACL10 library.
One of the ﬁrst tools to enable the validation of recursive shacl graphs was
SHACL2SPARQL [11]. Another tool, Trav-SHACL [18], impleme nts a shacl
engine designed to optimise the evaluation of shacl core constraint components
expressible in fragments of the L language [13]. On these fragments of shacl,
Trav-SHACL was shown to achieve signiﬁcantly faster valida tion times compared
to the SHACL2SPARQL tool.
4 https://w3c.github.io/data-shapes/data-shapes-test- suite/ accessed on
18/6/21
5 https://rdf4j.org/ accessed on 18/6/21
6 https://graphdb.ontotext.com/ accessed on 18/6/21
7 https://allegrograph.com/ accessed on 18/6/21
8 https://jena.apache.org/ accessed on 18/6/21
9 https://www.stardog.com/ accessed on 18/6/21
10 https://pypi.org/project/pyshacl/ accessed on 18/6/21

## PDF page 25

A Review of shacl 25
9.2 T ools for Generating shacl Documents
While eﬃcient tools to perform graph validation are undoubt edly essential to the
widespread adoption of shacl, it is also important to devise practical ways to
generate suitable shacl documents, without which validation would not be pos-
sible. On the one hand, shacl documents can be manually created by experts.
Tools to support this manual process can facilitate this, es pecially when inte-
grated with already established software. An example of thi s is SHACL4P [17],
a plugin for the Protégé ontology editor [31] which includes an editor to create
shacl documents, and a validator that allows users to test the docu ment by val-
idating an ontology with it, and then visualising any constr aint violations. Shape
Designer [6] is another tool to create shacl documents that combines a graphi-
cal editor, and additional algorithms to create constraint s semi-automatically by
analysing the data graph. The beneﬁts of diﬀerent types of vi sualisations as an
aid to the creating and editing of constraints for rdf graphs was studied in [28].
Existing work also investigated the possibility of generat ing shacl documents
from natural language text [43].
A number of approaches have been designed to automate the cre ation of
shacl documents. The SHACLearner [33] approach, generates shacl documents
by learning a kind of rules called Inverse Open Path (IOP) Rul es from the graph
data provided. IOP rules are strongly related to SCL and therefore shacl. An
IOP rule essentially follows the same structure as an SCL constraint axiom, both
syntactically and semantically, with the only exception th at the iﬀ operator is
replaced by a rightward implication. Another approach to au tomate the creation
of shacl documents is the Astrea-KG Mappings [10]. These mappings co nsist of
a set of manually created mappings from OWL [49] to shacl, that can be used
to automatically generate shacl documents from OWL ontologies. As described
in [34], shacl documents can also be generated from the axioms deﬁned by on-
tology design patterns [19]. The approach from [44] generat es shacl documents
for the purpose of quality assessment, using the ontology de sign patterns and
data statistics created by the ABSTAT [45] tool as an input. A nother similar
approach, presented in [8], allows the automatic extractio n of shacl constraints
from a sparql endpoint, and was tested on the dataset of Europeana 11.
Notably, shacl documents can also be seen as describing a desirable “schema ”
for graph data. As such, they can be used as a template to gener ate new RDF
data. An example of this is the Schímatos [51] tool, which gen erates forms for
RDF graph editing based on shacl documents, in order to simplify the graph
editing task, and minimize the chance of error.
9.3 Adoption of shacl
An analysis of existing use cases of shacl can be useful to gain insights on how
this technology is used in practice, and on in its level of ado ption. In a recent
review, 13 existing projects using shacl have been reviewed, and the most com-
mon constraints observed were cardinality, class, datatyp e and disjunction [29].
11 https://www.europeana.eu/en accessed on 18/6/21

## PDF page 26

26 Pareti and Konstantinidis
Several works investigate the use of shacl to verify compliance of a dataset
w.r.t. certain policies, such as GDPR requirements [35,2]. Other applications of
shacl include type checking program code [27] and detecting metad ata errors
in clinical studies [22]. shacl is also used by the European Commission to fa-
cilitate data sharing, for example by validating metadata a bout public services
against the recommended vocabularies [46]. Notably, sever al approaches deﬁne
translations into shacl from other technologies, such as ontologies and other
schema and constraint languages [16,21,25,32,40,47]. The se results show that
shacl tools, and in particular validators, can beneﬁt areas where technologies
other than shacl are already established.
10 Conclusion
Within this review we examined shacl, a constraint language that can be used to
validate rdf graphs. These constraints can be used to describe the proper ties of
a graph, to detect possible errors in the data or provide data quality assurances.
In this review we ﬁrst presented the main concepts of the shacl speciﬁcation,
such as the concept of shapes, and their two main components, targets and
constraints. We discussed the primary way to perform shacl validation, using
sparql queries, and how the semantics of validation can be abstract ed with the
concept of assignments.
While the shacl speciﬁcation describes how validation should be performed ,
its semantics is left implicit and not formally deﬁned. We ha ve extensively dis-
cussed studies that address this problem. In particular, we reviewed a complete
formalisation of shacl into a fragment of ﬁrst order logic called SCL. This for-
malisation lays bare several properties of shacl, and provides decidability and
complexity results for several shacl-related decision problems. Another impor-
tant line of work focuses on deﬁning potential extensions of shacl semantics
that can be used in the face of recursion. The shacl speciﬁcation, in fact, allows
constraints to be recursively deﬁned, but it does not deﬁne i ts semantics. We also
presented existing work studying the interaction of shacl with inference rules.
Datasets are often dynamic objects, and several questions a rise when considering
the eﬀects of this dynamism on the constraints imposed over t hem.
From the point of view of maturity and level of adoption of the shacl tech-
nology, we reviewed several implementations of shacl validators, which are now
integrated in many mainstream rdf databases, and several tools designed to fa-
cilitate the creation and management of shacl documents. Several approaches,
in particular, provide automated or semi-automated ways of generating suitable
shacl documents from a diverse range of sources, such as graph data , ontologies,
or natural language texts. Existing eﬀorts in mapping other constraint/valida-
tion languages into shacl is also worth noting, as it suggests that the usefulness
of shacl could be extended to support other existing technologies. W hile the
true extent of shacl adoption is hard to establish, since not all usages of shacl
are publicly documented, we found evidence of its usage in se veral areas, such

## PDF page 27

A Review of shacl 27
as to facilitate data sharing, to validate dataset against p olicies, and to detect
errors in datasets.
Despite the wealth of work on this topic, shacl is still a recent speciﬁcation,
and a number of important directions for future work still ex ist. For example,
there are opportunities to optimise shacl validators for particular type of con-
straints, or for particular scenarios, like for highly dyna mic databases. More
studies are needed to properly assess the usage of shacl in practical applica-
tions, and what types of constraints are more commonly used a nd how. While the
full semantics of shacl has been formally deﬁned, more work is needed to for-
mally establish its relation with other constraint languag es. It is also important
to notice that most of the pieces of work reviewed in this arti cle limit their scope
to ad-hoc subsets of the shacl speciﬁcation. In addition to the custom require-
ments of each application, this is commonly done in order to a void excessively
complex language components. At the same time, it is often di ﬃcult to under-
stand what these subsets exactly are as they are not always ex plicitly deﬁned.
Therefore, there might be scope to deﬁne reusable fragments of shacl, that
could ﬁll the role of lightweight but expressive alternativ es to the full language,
similarly to how OWL fragments are deﬁned. It might also be be neﬁcial, for sim-
ilar reasons, to converge towards a single standard or “pref erred” semantics for
shacl recursion, which could be deﬁned in a future version of the sp eciﬁcation.
References
1. A. Amarilli and M. Benedikt and P. Bourhis and M. Vanden Boo m: Query Answer-
ing with Transitive and Linear-Ordered Data. In: IJCAI’16. pp. 893–899 (2016)
2. Al Bassit, A., Krasnashchok, K., Skhiri, S., Mustapha, M. : Automated Compliance
Checking with SHACL (2020)
3. Andresel, M., Corman, J., Ortiz, M., Reutter, J.L., Savko vic, O., Simkus, M.: Stable
Model Semantics for Recursive SHACL. In: Proceedings of The Web Conference
2020. p. 1570–1580. WWW ’20 (2020)
4. Benedikt, M., Konstantinidis, G., Mecca, G., Motik, B., P apotti, P., Santoro,
D., Tsamoura, E.: Benchmarking the chase. In: Proceedings o f the 36th ACM
SIGMOD-SIGACT-SIGAI Symposium on Principles of Database S ystems. pp. 37–
52. ACM (2017)
5. Berger, R.: The Undecidability of the Domino Problem. MAM S 66, 1–72 (1966)
6. Boneva, I., Dusart, J., Fernández Alvarez, D., Gayo, J.E. L.: Shape Designer for
ShEx and SHACL Constraints. ISWC 2019 - 18th International S emantic Web
Conference, Poster (Oct 2019)
7. Brickley, D., Guha, R.: RDF schema 1.1. W3C recommendatio n, W3C (Feb 2014),
https://www.w3.org/TR/2014/REC-rdf-schema-20140225/
8. Čer¯ ans, K., Ovčin, n, ikova, J., Boj¯ ars, U., Grasmanis, M., L¯ ace, L., Rom¯ ane, A .:
Schema-Backed Visual Queries over Europeana and other Link ed Data Resources.
In: ESWC2021 Poster and Demo Track (2021)
9. Ceri, S., Gottlob, G., Tanca, L.: What you always wanted to know about datalog
(and never dared to ask). IEEE Transactions on Knowledge and Data Engineering
1(1), 146–166 (1989)

## PDF page 28

28 Pareti and Konstantinidis
10. Cimmino, A., Fernández-Izquierdo, A., García-Castro, R.: Astrea: Automatic Gen-
eration of SHACL Shapes from Ontologies. In: The Semantic We b. pp. 497–513.
Springer International Publishing, Cham (2020)
11. Corman, J., Florenzano, F., Reutter, J.L., Savkovic, O. : SHACL2SPARQL: Val-
idating a SPARQL Endpoint against Recursive SHACL Constrai nts. In: Interna-
tional Semantic Web Conference ISWC Satellite Events. pp. 1 65–168 (2019)
12. Corman, J., Florenzano, F., Reutter, J.L., Savković, O. : Validating SHACL Con-
straints over a Sparql Endpoint. In: The Semantic Web – ISWC 2 019. pp. 145–163
(2019)
13. Corman, J., Reutter, J.L., Savković, O.: Semantics and V alidation of Recursive
SHACL. In: The Semantic Web – ISWC 2018. pp. 318–336 (2018)
14. Cyganiak, R., Wood, D., Markus Lanthaler, G.: RDF 1.1 Con -
cepts and Abstract Syntax. W3C Recommendation, W3C (2014),
http://www.w3.org/TR/2014/REC-rdf11-concepts-20140225/
15. Danielski, D., Kieronski, E.: Finite Satisﬁability of U nary Negation Fragment with
Transitivity. In: MFCS’19. pp. 17:1–15. LIPIcs 138, Leibni z-Zentrum fuer Infor-
matik (2019)
16. Di Ciccio, C., Ekaputra, F.J., Cecconi, A., Ekelhart, A. , Kiesling, E.: Finding Non-
compliances with Declarative Process Constraints Through Semantic Technologies.
In: Cappiello, C., Ruiz, M. (eds.) Information Systems Engi neering in Responsible
Information Systems. pp. 60–74 (2019)
17. Ekaputra, F.J., Lin, X.: SHACL4P: SHACL constraints val idation within Protégé
ontology editor. In: 2016 International Conference on Data and Software Engineer-
ing (ICoDSE). pp. 1–6 (2016)
18. Figuera, M., Rohde, P.D., Vidal, M.E.: Trav-SHACL: Eﬃci ently Validating Net-
works of SHACL Constraints. In: Proceedings of the Web Confe rence 2021. p.
3337–3348. WWW ’21, Association for Computing Machinery, N ew York, NY,
USA (2021)
19. Gangemi, A., Presutti, V.: Ontology Design Patterns, pp . 221–243. Springer Berlin
Heidelberg, Berlin, Heidelberg (2009)
20. Jung, J., Lutz, C., Martel, M., Schneider, T.: Querying t he Unary Negation Frag-
ment with Regular Path Expressions. In: ICDT’18. pp. 15:1–1 8. OpenProceed-
ings.org (2018)
21. K Soman, R.: Modelling construction scheduling constra ints using shapes con-
straint language (SHACL). In: 2019 European Conference on C omputing in Con-
struction. pp. 351–358. University College Dublin (2019)
22. Keuchel, D., Spicher, N.: Automatic Detection of Metada ta Errors in a Registry
of Clinical Studies Using Shapes Constraint Language (SHAC L) Graphs. Studies
in health technology and informatics 281, 372—376 (May 2021)
23. Knublauch, H., Kontokostas, D.: Shapes Constraint Lang uage (SHACL). W3C
Recommendation, W3C (2017), https://www.w3.org/TR/shacl/
24. Kontokostas, D., Westphal, P., Auer, S., Hellmann, S., L ehmann, J., Cornelissen,
R., Zaveri, A.: Test-driven Evaluation of Linked Data Quali ty. In: Proceedings of
the 23rd International Conference on World Wide Web. pp. 747 –758. WWW ’14,
ACM (2014)
25. Larhrib, M., Escribano, M., Cerrada, C., Escribano, J.J .: Converting OCL and
CGMES Rules to SHACL in Smart Grids. IEEE Access 8, 177255–177266 (2020)
26. Leinberger, M., Seifer, P., Rienstra, T., Lämmel, R., St aab, S.: Deciding SHACL
Shape Containment through Description Logics Reasoning. I n: The Semantic Web
– ISWC 2020. Springer International Publishing (2020), ( this volume )

## PDF page 29

A Review of shacl 29
27. Leinberger, M., Seifer, P., Schon, C., Lämmel, R., Staab , S.: Type Checking Pro-
gram Code Using SHACL. In: The Semantic Web – ISWC 2019. pp. 39 9–417.
Springer International Publishing, Cham (2019)
28. Lieber, S., De Meester, B., Heyvaert, P., Brückmann, F., Wambacq, R., Mannens,
E., Verborgh, R., Dimou, A.: Visual Notations for Viewing an d Editing RDF Con-
straints with UnSHACLed. Semantic Web (2021), under review
29. Lieber, S., Dimou, A., Verborgh, R.: Statistics about Da ta Shape Use in RDF
Data. In: ISWC (Demos/Industry) (2020)
30. Marnette, B.: Generalized schema-mappings: from termi nation to tractability. In:
Proc. of the twenty-eighth ACM SIGMOD-SIGACT-SIGART symp. on Principles
of database systems. pp. 13–22. ACM (2009)
31. Musen, M.A., Protégé Team: The Protégé Project: A Look Ba ck and a Look For-
ward. AI matters 1(4), 4—12 (June 2015)
32. Nenadić, K.R., Gavrić, M.M., Ðurđević, V.I.: Validatio n of CIM datasets using
SHACL. In: 2017 25th Telecommunication Forum (TELFOR). pp. 1–4 (2017)
33. Omran, P.G., Taylor, K., Mendez, S.R., Haller, A.: Learn ing SHACL Shapes from
Knowledge Graphs. Semantic Web (2021), under review
34. Pandit, H.J., O’Sullivan, D., Lewis, D.: Using Ontology Design Patterns To Deﬁne
SHACL Shapes. In: 9th Workshop on Ontology Design and Patter ns (WOP2018),
International Semantic Web Conference (ISWC). pp. 67–71 (2 018)
35. Pandit, H.J., O’Sullivan, D., Lewis, D.: Test-Driven Ap proach Towards GDPR
Compliance. In: Semantic Systems. The Power of AI and Knowle dge Graphs. pp.
19–33. Springer International Publishing, Cham (2019)
36. Pareti, P., Konstantinidis, G., Mogavero, F.: Satisﬁab ility and Containment of
Recursive SHACL (2021), arXiv preprint 2108.13063
37. Pareti, P., Konstantinidis, G., Mogavero, F., Norman, T .J.: SHACL Satisﬁability
and Containment. In: The Semantic Web – ISWC 2020. pp. 474–49 3. Springer
International Publishing, Cham (2020)
38. Pareti, P., Konstantinidis, G., Norman, T.J., Şensoy, M .: SHACL Constraints with
Inference Rules. In: The Semantic Web – ISWC 2019. Springer I nternational Pub-
lishing (2019)
39. Robinson, R.: Undecidability and Nonperiodicity for Ti lings of the Plane. IM 12,
177–209 (1971)
40. Savković, O., Kharlamov, E., Lamparter, S.: Validation of SHACL Constraints
over KGs with OWL 2 QL Ontologies via Rewriting. In: The Seman tic Web. pp.
314–329. Springer International Publishing, Cham (2019)
41. Schaﬀenrath, R., Proksch, D., Kopp, M., Albasini, I., Pa nasiuk, O., Fensel, A.:
Benchmark for Performance Evaluation of SHACL Implementat ions in Graph
Databases. In: Rules and Reasoning. pp. 82–96. Springer Int ernational Publish-
ing, Cham (2020)
42. Seaborne, A., Harris, S.: SPARQL 1.1 query language. W3C recommendation,
W3C (Mar 2013), https://www.w3.org/TR/2013/REC-sparql1 1-query-20130321/
43. Šenkýř, D.: SHACL Shapes Generation from Textual Docume nts. In: Enterprise
and Organizational Modeling and Simulation. pp. 121–130. S pringer International
Publishing, Cham (2019)
44. Spahiu, B., Maurino, A., Palmonari, M.: Towards Improvi ng the Quality of Knowl-
edge Graphs with Data-driven Ontology Patterns and SHACL. I n: International
Semantic Web Conference ISWC Sattelite Events. pp. 103–117 (2018)
45. Spahiu, B., Porrini, R., Palmonari, M., Rula, A., Maurin o, A.: ABSTAT: Ontology-
Driven Linked Data Summaries with Pattern Minimalization. In: The Semantic
Web. pp. 381–395. Springer International Publishing, Cham (2016)

## PDF page 30

30 Pareti and Konstantinidis
46. Stani, E.: Design reusable SHACL shapes and implement a l inked data validation
pipeline. Code4Lib Journal 45 (2019)
47. Stolk, S., McGlinn, K.: Validation of IfcOWL datasets us ing SHACL. In: Pro-
ceedings of the 8th Linked Data in Architecture and Construc tion Workshop. pp.
91–104 (2020)
48. Thornton, K., Solbrig, H., Stupp, G.S., Labra Gayo, J.E. , Mietchen, D.,
Prud’hommeaux, E., Waagmeester, A.: Using Shape Expressio ns (ShEx) to Share
RDF Data Models and to Guide Curation with Rigorous Validati on. In: The Se-
mantic Web. pp. 606–620. Springer International Publishin g, Cham (2019)
49. W3C OWL Working Group: OWL 2 Web Ontology Language Docu-
ment Overview (Second Edition). W3C recommendation, W3C (D ec 2012),
https://www.w3.org/TR/2012/REC-owl2-overview-20121211/
50. Wang, H.: Proving Theorems by Pattern Recognition II. BS TJ 40, 1–41 (1961)
51. Wright, J., Rodríguez Méndez, S.J., Haller, A., Taylor, K., Omran, P.G.: Schí-
matos: A SHACL-Based Web-Form Generator for Knowledge Grap h Editing. In:
The Semantic Web – ISWC 2020. pp. 65–80 (2020)
