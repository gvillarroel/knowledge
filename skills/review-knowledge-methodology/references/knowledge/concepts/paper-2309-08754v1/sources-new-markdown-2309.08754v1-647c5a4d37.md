---
type: Research Paper
title: 'Reproducible Domain-Specific Knowledge Graphs in the Life Sciences: a Systematic
  Literature Review'
description: Empirical evidence that domain knowledge graphs are rarely fully reproducible.
resource: https://example.org/knowledge-methodology-papers/resource/paper-2309-08754v1/sources%2Fnew%2Fmarkdown%2F2309.08754v1
tags:
- paper-2309-08754v1
- markdown
- rl
sources:
- id: paper-2309-08754v1
  resource: sources/new/markdown/2309.08754v1.md
  title: paper-2309-08754v1
generated:
  by: process:semantic-okf-python
concept_id: concepts/paper-2309-08754v1/sources-new-markdown-2309.08754v1-647c5a4d37
concept_path: concepts/paper-2309-08754v1/sources-new-markdown-2309.08754v1-647c5a4d37.md
subject_iri: https://example.org/knowledge-methodology-papers/resource/paper-2309-08754v1/sources%2Fnew%2Fmarkdown%2F2309.08754v1
ontology_class_iri: https://example.org/ontology/knowledge-methodology-papers#Paper
ontology_version_iri: https://example.org/ontology/knowledge-methodology-papers/1.0.0
source_id: paper-2309-08754v1
source_kind: markdown
source_path: sources/new/markdown/2309.08754v1.md
source_content_sha256: 2c424656422c7e6122d27c61725badbf3379b8d921ffcf508f9773916d03df5b
record_sha256: 4e18694f18391c8c2a86bf22085e41410d9bf0a93c4c970f000681e1d8e5fe22
source_refs:
- https://example.org/knowledge-methodology-papers/provenance/record/paper-2309-08754v1/4bad6274930f022fed0445a6
record_id: sources/new/markdown/2309.08754v1
---

# Reproducible Domain-Specific Knowledge Graphs in the Life Sciences: a Systematic Literature Review

## Dataset relevance

Empirical evidence that domain knowledge graphs are rarely fully reproducible.

- Coverage lanes: validation-and-reproducibility; knowledge-graphs-and-ontologies
- Relevant skills: build-semantic-okf-*; build-specialized-skill; open-knowledge-format

## Source citation

- Pinned arXiv record: [2309.08754v1](https://arxiv.org/abs/2309.08754v1)
- Authors: Babalou, Samira; Samuel, Sheeba; König-Ries, Birgitta
- PDF: [https://arxiv.org/pdf/2309.08754v1](https://arxiv.org/pdf/2309.08754v1)
- PDF SHA-256: `41bb9b4058342be7407703dc7b78fab2a0205c805f426b5f0daeb27d653bbcd5`
- Extracted pages: 8

The following text was extracted page by page from the pinned PDF. Page headings are stable evidence locators.

## PDF page 1

Reproducible Domain-Specific Knowledge Graphs in the Life
Sciences: a Systematic Literature Review
Samira Babaloua,b,∗, Sheeba Samuela,c and Birgitta König-Riesa,b,c
aHeinz Nixdorf Chair for Distributed Information Systems, Institute for Computer Science, Friedrich Schiller University Jena, Germany
bGerman Center for Integrative Biodiversity Research (iDiv), Halle-Jena-Leipzig, Germany
cMichael Stifel Center Jena
ARTICLE INFO
Keywords:
Knowledge Graphs
Reproducibility
Semantic Web
Life Sciences
ABSTRACT
Knowledge graphs (KGs) are widely used for representing and organizing structured knowledge in
diversedomains.However,thecreationandupkeepofKGsposesubstantialchallenges.Developinga
KG demands extensive expertise in data modeling, ontology design, and data curation. Furthermore,
KGsaredynamic,requiringcontinuousupdatesandqualitycontroltoensureaccuracyandrelevance.
Theseintricaciescontributetotheconsiderableeffortrequiredfortheirdevelopmentandmaintenance.
One critical dimension of KGs that warrants attention is reproducibility. The ability to replicate and
validateKGsisfundamentalforensuringthetrustworthinessandsustainabilityoftheknowledgethey
represent.ReproducibleKGsnotonlysupportopensciencebyallowingotherstobuilduponexisting
knowledge but also enhance transparency and reliability in disseminating information. Despite the
growing number of domain-specific KGs, a comprehensive analysis concerning their reproducibility
hasbeenlacking.Thispaperaddressesthisgapbyofferingageneraloverviewofdomain-specificKGs
and comparing them based on various reproducibility criteria. Our study over 19 different domains
shows only eight out of 250 domain-specific KGs (3.2%) provide publicly available source code.
Amongthese,onlyonesystemcouldsuccessfullypassourreproducibilityassessment(14.3%).These
findings highlight the challenges and gaps in achieving reproducibility across domain-specific KGs.
Ourfindingthatonly0.4%ofpublisheddomain-specificKGsarereproducibleshowsaclearneedfor
further research and a shift in cultural practices.
1. Introduction
At their core, Knowledge Graphs (KGs) are structured
information about a particular domain in the form of
entitiesandrelations.Theyareusedindifferentapplications
suchasrecommendationsystems[1],healthmisinformation
detection [2], or disease characteristics identification [3].
While different definitions of KGs exist, we use the
definition provided by Hogan et al. [4]. According to their
definition,KGsaregraphofdataintendedtoaccumulateand
convey knowledge of the real world, whose nodes represent
entities of interest and whose edges represent potentially
different relations between these entities.
Differentdefinitionsofthetermreproducibilityexist[5–
10].Accordingto[5,6,10],reproducibilityisthecapability
of getting the same (or close-by) results whenever an
experiment is carried out by an independent experimenter
usingdifferentconditionsofmeasurementwhichincludethe
method, location, or time of measurement. Reproducibility
is defined as obtaining consistent computational results
usingthesameinputdata,steps,methods,code,andanalysis
conditions,accordingto[8,9].Theimportanceofachieving
reproducibility is underlined by the many studies and
surveys that have been done to check the reproducibility of
∗Corresponding author; Address: Leutragraben 1, Jentower, Room
17N05, 07743 Jena, Germany
samira.babalou@uni-jena.de (S. Babalou);
sheeba.samuel@uni-jena.de (S. Samuel);birgitta.koenig-ries@uni-jena.de
(B. König-Ries)
ORCID(s): 0000-0002-4203-1329(S. Babalou);0000-0002-7981-8504(S.
Samuel); 0000-0002-2382-9722(B. König-Ries)
publishedresultsindifferentfields[11–14].Moresignificant
insights were brought into the reproducibility crisis by the
survey conducted by Nature in 2016 [13]. The difficulty
in reproducing published results can also be seen in
computational science [14–16]. These works indicate the
continued existence of a problem in reproducing published
results in different disciplines.
KGs can facilitate a greater alignment between data and
expertiseineverydomain,makingdatamoreaccessibleand
usable. Although KGs are useful in various domains, their
broaduptakeisstillhinderedbythesubstantialeffortandthe
high semantic web expertise needed to create them. While
reproducibility should be a standard practice in scientific
endeavors, most existing KGs do not offer the ability to
recreate or reproduce them. Despite increased awareness of
the problem and the rising availability of data and code
used in publications, reproducing published results remains
challenging. This holds true for KGs as well. However, a
reproducibleKGcanfostertrustintheinformationprovided
and support open data and open science practices. The
significance of ensuring reproducibility in knowledge graph
generation has been highlighted in [17].
With the popularity of KGs, nowadays, many KGs are
generated for different domains and in various applications.
Accordingly, numerous researchers surveyed the existing
KGs exploring multiple aspects such as embeddings
(cf. [18–21]), refinements [22], applications [23],
architectures [24], privacy-preservation [25], completion
(cf. [26, 27], question answering [28], among others.
Page 1 of 8
arXiv:2309.08754v1  [cs.IR]  15 Sep 2023

## PDF page 2

A Survey on Reproducible Domain-Specific Knowledge Graphs
To the best of our knowledge, the only research
on surveying domain-specific KGs was introduced by
Abu-Salih in [29], which differs from our study as we
specifically focus on the reproducibility aspects of KGs.
In this paper, we take the first step towards analyzing the
existing KGs with respect to their reproducibility. We first
provide an overview of the existing domain-specific KGs
and compare them based on general criteria, including the
respective domain, resource type, and construction method.
This comparative analysis gives readers more insights into
the existing domain-specific KGs. We then investigate the
extent to which the KGs are reproducible using a defined
set of criteria that reflect the reproducibility aspect. In this
paper, we attempt to reproduce knowledge graphs using the
same data and methods provided by the original authors in
an experimental setup closely resembling theirs.
Although the main focus of this study is the
reproducibility of existing domain-specific KGs, it is worth
noting that the aspects of findability, accessibility, and
interoperability,asemphasizedbytheFAIRprinciples[30],
constitute an interesting research direction. However,
analyzing these aspects is beyond the scope of the current
study and could be a potential avenue for future research.
The remainder of this paper is structured as follows:
Section2showsthesurveymethodology.Section3presents
the existing domain-specific Knowledge Graphs and the
criteria for their reproducibility, followed by the discussion
inSection4.Theconclusionandfutureworksarepresented
in Section 5.
2. Survey Methodology
We first searched for the keyword “domain knowledge
graph” in the Google Scholar search engine1. We limited
our search to papers published until the end of 2021. At the
time of querying (Jan 01, 2022), this search resulted in 713
papers.Welookedattheirdomainnames(e.g.,biodiversity,
geoscience, biomedical, etc.) and then extended our search
for those specific domain names that appear on the first
result,e.g.,for“biodiversityknowledgegraph”,“biomedical
knowledge graph”, and so on. To ensure the exclusion of
duplicate entries for the "domain knowledge graph" that
mayhaveappearedinmultiplecategories,weremovedsuch
duplicates. As a result, we identified a collection of 603
unique papers focused on the "domain knowledge graph."
Overall, our research encompassed a total of 1759 papers
across 19 distinct domains. Note that we excluded the paper
by Kim [31] from our analysis as we were unable to access
and ascertain whether it pertained to KG creation, despite
attempts to contact the author.
We have selected a subset of the papers listed in
the search results by considering these criteria: (i) we
chose articles written in English only, (ii) we selected
papers that focused on the creation or construction of
knowledge graphs (KGs). Papers that primarily addressed
theusageorotheraspectsofKGswereexcluded.Moreover,
the search results from Google Scholar displayed papers
where the keywords appeared in the title, introduction, or
state-of-the-art sections. Some papers do not focus on the
topic of our keywords. However, some papers only briefly
mentionedthekeywordsinthestateoftheart,indicatingthat
they did not primarily focus on generating KGs. Therefore,
we disregarded such papers. The selection process was
carried out manually, thoroughly examining each paper to
determine its relevance to KG construction. As a result,
out of the initial 1759 papers listed in Google Scholar, we
identified 250 papers that met our selection criteria.
From this subset, we further narrowed down our
selection to papers that provided open-source code. We
checked all 250 papers manually by looking at the paper
content, whether they have a link to the GitHub repository
or any web pages where their code is published. We also
checked the data availability statement section in papers, if
available. Surprisingly, we only found eight papers out of
250 with open-source code.
We use a script to download the articles to ensure the
reproducibility of our experimental results. The script, the
original search results obtained from Google Scholar, and
ouranalysisoftheresults(whethereachpaperisselectedor
not, and whether they are open-source or not) are published
in our repository2.
Table 1 presents a summary of our keyword search
results, indicating the number of published papers found
on each respective topic as retrieved from Google Scholar.
The third column shows the number of papers on Google
Scholar for each keyword. The fourth column specifies the
countofselectedpapersrelevanttoKnowledgeGraph(KG)
construction, while the final column denotes the number of
papers accompanied by open-source code. The last row of
thistableshowsthetotalnumberofpapersforeachcategory.
3. Reproducibility of domain-specific
Knowledge Graphs
This paper centers its focus on the aspect of
reproducibility. Consequently, as an initial step, we
scrutinized all the selected papers to determine the
availability of publicly accessible code for the Knowledge
Graphs (KGs) they developed. It emerged that only eight
papers out of the total 250 (3.2%) met this criterion.
Note that AliCG (Alibaba Conceptual Graph) [32] 3
and the KG proposed by Hoa et al., [33] (for surveying
and remote-sensing applications) 4, published only the
raw data and not the code. So, these papers were not
considered within the category of open-source code.
Moreover,inthebiomedicaldomain,wefoundtwodifferent
publications [34, 35] related to CROssBAR-KG. We
consider them as one unique KG for our further analysis.
In this section, we first summarize the domain-specific
KGs that provide open-source code. We then provide a
generaloverviewoftheminsubsection3.1anddiscusstheir
reproducibility aspect in Subsection 3.2. Existing KGs with
open-source code:
• CKGG [36] (Chinese Knowledge Graph for
Geography) is a KG covering the core geographical
Page 2 of 8

## PDF page 3

A Survey on Reproducible Domain-Specific Knowledge Graphs
Table 1
Keyword search on the Google Scholar. |Papers| denotes the
total number of papers retrieved for a given keyword; |Selected|
shows the number of selected papers related to building KGs;
|Open-source code| shows the number of papers that provides
open-source code.
Keyword |Open-no. search |Papers| |Selected| source|
1 “Domain knowledge graph”602 88 2
2 “Agriculture knowledge graph”16 5 0
3 “Biodiversity knowledge graph”87 5 1
4 “Biomedical knowledge graph”214 12 2
5 “Cultural knowledge graph” 17 6 0
6 “E-commerce knowledge graph”16 7 0
7 “Education knowledge graph”32 14 0
8 “Financial knowledge graph”64 3 0
9 “Geographic knowledge graph”117 20 1
10 “Geoscience knowledge graph”9 4 1
11 “Healthcare knowledge graph”45 5 0
12 “Industrial knowledge graph”37 8 0
13 “Medical knowledge graph”291 38 0
14 “Military knowledge graph” 26 8 0
15 “Movie knowledge graph” 48 6 0
16 “Political knowledge graph” 6 0 0
17 “Robotic knowledge graph” 4 1 0
18 “Security knowledge graph” 80 10 0
19 “Tourism knowledge graph”42 9 1
20 “Water knowledge graph” 3 1 0
Total 1756 250 8
knowledge at the high-school level, containing 1.5
billion triples. The authors used a variety of NLP
tools to integrate various kinds of geographical
data in different formats from diverse sources (such
as GeoNames 5, Wikipedia). They conducted a
preliminary evaluation of CKGG and showed a
prototype educational information system based on
CKGG.
• CROssBAR-KG[34, 35] Knowledge graph presents
biologicaltermsasnodesandtheirknownorpredicted
pairwise relationships as edges. They are directly
obtained from their integrated large-scale database,
builtuponasetofbiomedicaldataresources.Thedata
is enriched with a deep-learning-based prediction of
relations between numerous biomedical entities. At
first, the data is stored in a non-relational database.
Then, biologically relevant small-scale knowledge
graphs are constructed on the fly, triggered by users’
queries with a single or multiple term(s). The system
istestedbyause-casestudyoftheCOVID-19dataset.
• ETKG(Event-centricTourismKnowledgeGraph)[1]
isaKGtomodelthetemporalandspatialdynamicsof
tourist trips. The authors extracted information from
over 18000 travel notes (structured and unstructured
information) crawled from the Internet, and defined
anETKGschematomodeltourism-relatedeventsand
their key properties. The schema of ETKG is built
upon the Simple Event Model [37] with augmented
properties and classes. The authors constructed an
ETKG of Hainan and realized an application of POI
recommendation based on it.
• FarsBase [38] is a cross-domain knowledge graph
in the Farsi language, consisting of more than 500K
entities and 7 million relations. Its data is extracted
from the Farsi edition of Wikipedia in addition to
its structured data, such as infoboxes and tables. To
build Farsi Knowledge Graph (FKG), the authors
first developed an ontology retrieved from DBpedia
ontology, based on resources from Farsi Wikipedia.
Then, they mapped Wikipedia templates to their
built ontology. They consider Wikipedia as input of
the FKG system. To enhance the performance and
flexibility of the knowledge base, they stored data in
two-level architecture: a NoSQL database for storing
data and metadata, and a triplestore for storing the
final data. Most entities in the FKG have been linked
toDBpedia 6 andWikidata 7 resourcesbyowl:sameAs
property. A SPARQL endpoint provides access to the
knowledge graph.
• GAKG (GeoScience Academic Knowledge
Graph) [39] is a large-scale multimodal academic
KG, consisting of more than 68 million triples
based on 1.12 million papers published in various
geoscience-related journals. The entities of GAKG
have been extracted under a Human-In-the-Loop
framework, using machine reading and information
retrieval techniques with manual annotation of
geoscientists in the loop. The schema of GAKG
consists of 11 concepts connected by 19 relations.
GAKG is updated regularly and can be queried at the
SPARQL query Endpoint. It is evaluated using two
benchmarks.
• MDKG[40] stands for Microbe-Disease Knowledge
Graph and is built by integrating multi-source
heterogeneous data from Wikipedia text and other
related databases. Through a series of natural
language processing, they split the text of Wikipedia
pagesintosentences.Then,usinganexistingtool,they
perform named entity recognition and relationship
extraction on the sentences and obtain the interaction
triplets.Afterward,otherdatabasesareintegratedinto
their KG. Moreover, they used the representation
learning method for knowledge inference and link
prediction.
• Ozymandias [41], a biodiversity knowledge graph,
combines scholarly data about the Australian fauna
from different sources, including the Atlas of
Living Australia8, the Biodiversity Heritage Library,
ORCID9,andlinkstoexternalKGslikeWikidataand
GBIF10.
• RTX-KG2 [42] is an open-source software system
for building and hosting a web API for querying
a biomedical knowledge graph. The data from 70
Page 3 of 8

## PDF page 4

A Survey on Reproducible Domain-Specific Knowledge Graphs
Table 2
General overview of domain-specific KGs.
KG Domain Resource Type Construction Method Reasoning Cross Linking Evaluation Year
CKGG Geography Data resources Machine Learning Not declared Wikipedia Yes 2021
CROssBAR-KG Biomedical Data resources Machine Learning Yes Not declared Yes 2020
ETKG Tourism Web pages Machine Learning Not declared Not declared Yes 2020
FarsBase Cross-domain Wikipedia Heuristic Not declared DBpedia, Wikidata Not provided 2021
GAKG Geoscience Publication Machine Learning Not declared Wikidata Yes 2021
MDKG Biomedical Wikipedia text Machine Learning Yes Not declared Not provided 2020
Ozymandias Biodiversity Publication Heuristic Not declared Wikidata, GBIF Not provided 2019
RTX-KG2 Biomedical Data resources Heuristic Yes Not declared Not provided 2021
core biomedical knowledge-bases are extracted via
a set of Extract-Transform-Load (ETL) modules. Its
schemaisbuiltbasedonanexistingmetamodelinthe
biological domain. RTX-KG version 2.7.3 contains
10.2 million nodes and 54.0 million edges.
3.1. Comparison of KGs
In this section, we summarize the key features of
each KG mentioned in Section 3. Table 2 shows the
comparison of domain-specific KGs with respect to their
domain, resource type, construction method, reasoning,
cross-linking,evaluation,andyear.Thecross-linkingaspect
indicates whether the elements of the KG are connected
to external resources or other KGs such as Wikidata or
DBpedia. Note that if the KG is built based on some
resources, i.e., the elements of KG are mapped to other data
resources, we do not consider them as cross-linking.
3.2. Criteria for reproducibility of KGs
Reproducibility is one of the important principles of
scientific progress. It emphasizes that a result obtained
by an experiment or observational study should be
consistently obtained with a high degree of agreement
when differentresearchers replicate thestudy with thesame
methodology. Indeed, reproducing an experiment is one
importantapproachscientistsusetogainconfidenceintheir
conclusions [43].
Over time, the scientific community has put forth
various guidelines and recommendations for conducting
reproducible research [10, 30, 44–46]. Based on the current
literature, we develop a set of criteria that affects the
reproducibility of Knowledge Graph construction. Here, we
present them as our suggested guidelines in the context of
reproducibilityoftheconstructionofKnowledgeGraphs,as
follows:
• Availability of code and data: One of the essential
requirementsforensuringreproducibleresearchisthe
availability of code and data used for constructing
the KG. This is one of the key requirements for
conducting reproducible research [45, 46]. This rule
is applied to all computational research [14–16]. So,
forthereproducibleresearch,publicaccesstoscripts,
runs, and results should be provided. The data used
for generating KG should be available or accessible
for querying. To construct a knowledge graph, not
only the code but also the data should be accessible.
Therefore, the published papers should deposit data
in public repositories where available and link data
bi-directionallytothepublishedpaper.Dataandcode
sharedonpersonalwebsitesareconsideredaccessible
as long as the websites are maintained [46].
• Code License: The code used for KG construction
should be accompanied by an appropriate license for
reuse or reproduction. Since we found no particular
mentionoflicensesfordatasetsinmostofthesystems,
we do not report about them in this paper.
• DOI for code and data: To ensure findability, the
code and data should have persistent identifiers [10].
The materials used for KG construction should be
findable and linked to the published research with a
permanent Digital Object Identifier (DOI). Archiving
data in online repositories is one way to ensure the
findability of the code and data.
• Availability of execution environment : The
execution environment should be available in
any format such as configuration, setup, yaml, or
requirement files. The format for the execution
environment can vary based on the programming
language used for the construction of KG. For
example, for Python, the execution environment is
generally addressed by defining dependencies in
standard files like requirements.txt, setup.py, and
pipfile[15,16].Accordingto[47],thelackofversions
of imported libraries may cause incompatibilities
and prevent the usage in other systems. Hence,
the libraries and their version used are important
information for the reproducibility of KGs.
• Run instruction: Comprehensive instructions for
running the code should be provided. In order to
reproduce the results, it is important to document the
process. For computational experiments, the process
of generating the results is often provided through
instructions in a format like README files in the
code repositories.
• Online demo: It is desirable to have the KG
itself available for use through an online demo.
Page 4 of 8

## PDF page 5

A Survey on Reproducible Domain-Specific Knowledge Graphs
However, this criterion does not directly impact the
reproducibility of KG systems.
• SPARQL endpoint: Having a SPARQL Endpoint
to access and query the data within the Knowledge
Graph offers significant advantages.
• Successful regeneration : The code should be
executable, allowing successful regeneration of the
KG.
• Provenance information: Provenance plays a key
role in the reproducibility of results. Provenance
support can be used to maintain, analyze, and debug
evolving knowledge graphs [48]. Both prospective
and retrospective provenance offer insights into
the steps required and the events that happened
during the development of knowledge graphs. This
information includes the addition, deletion, and
updation of RDF statements [49] in the construction
of KGs. Additionally, it includes details regarding
dataset versions, code, libraries, modules, SPARQL
endpoints, etc.
Table 3 shows the comparison between KGs in terms
of the mentioned reproducibility criteria. Our experiments
yield the following findings:
• KGs such as MDKG and CKGG are not reproducible
because, despite their code being publicly accessible,
the necessary data for constructing these specific
knowledge graphs remains inaccessible.
• FarseBase, MDKG, CROssBAR, and ETKG do not
provideruninstructionsontheirrepository.Although
their code is publicly available, it requires extra
expertise to be familiar with that system to make
their systems run. Therefore, we cannot assert their
reproducibility.
• Reproducing RTX-KG2 is challenging due to its
high computational requirements. Currently, we lack
resources with system specifications comparable to
those of RTX-KG2. Therefore, we cannot draw any
conclusions regarding its reproducibility at this time.
• Ozymandias was regenerated successfully.
In the RTX-KG2 repository, the authors provide links
to all 70 original data sources used in its construction.
However,wecannotconcludethatthedataofRTX-KG2has
a DOI, as some of those data sources do not have a DOI.
Moreover, a read-only endpoint11 for RTX KG2 as a graph
databasewasnotavailableatthetimeofouraccess.Further
demo pages were not found. Thus, we marked it with “-” in
column 7 of Table 3.
FarseBase derives its source data from Wikipedia
articles composed in the Farsi language. While the
repository linked with it contains the code for acquiring
the source data, the actual data is not included. Since
downloading the source data may not yield identical results
to the data utilized in generating FarseBase, we cannot
conclude whether that data is available.
4. Discussion
From our comparison in terms of general criteria
(Table 2), we can conclude that:
• Within our dataset, the fields of medicine,
biomedicine, and healthcare, which are encompassed
withinthebroaderrealmofmedicalscience,standout
as the most prevalent domains for Knowledge Graphs
(KGs). This prominence can likely be attributed to
the substantial volume of available data within this
domain and the numerous applications that make use
of KGs. Out of the 250 selected papers focusing on
KGs, 56 of them (comprising 39 from medical, 12
from biomedical, and 5 from healthcare domains)
account for approximately 22% of the total (refer to
Table 1). There is a growing trend in constructing
KGs for geographic and education domains.
• Most existing KGs are built based on textual data
(publication) and different data sources. Interestingly,
there were no KGs in our selected ones that target
the tabular data. However, there is a trend to build
KGs based on the tabular data. The Semantic Web
Challenge on Tabular Data to Knowledge Graph
Matching [50] is held annually to understand the
semantic structure and meaning of tabular data.
• Although the heuristic approaches are used to build
some KGs, the machine learning approaches are the
most popular construction method.
• Although reasoning capabilities can help discover
additional relationships, most KGs do not explicitly
mention their use of reasoning.
• KGs are widely regarded as one of the most
promising ways to link information in the age of
Big Data. According to the linked open data (LOD)
principles [51], each knowledge resource on the web
receives a stable, unique and resolvable identifier.
Because of the unique identifiers, KGs can be
interlinked. However, most KGs did not provide
cross-linkage. Three KGs out of eight provide the
cross-link (see Table 2).
• The evaluation of KGs remains a challenge in
this domain, as it requires the establishment of
benchmarks,whichisalaboriousandtime-consuming
task. Although the criteria introduced in [52] can
partially be applied in this context, KGs’ evaluation
seeks its own specific strategy.
• Constructing domain-specific Knowledge Graphs
(KGs) using open-source code has gained popularity
inrecentyears.AsillustratedinTable2,allthestudied
platforms were developed recently.
Page 5 of 8

## PDF page 6

A Survey on Reproducible Domain-Specific Knowledge Graphs
Table 3
Comparing KGs in terms of reproducbility criteria.
Code Data Online SPARQL Execution Run SuccessfulName Availability License doi Availability doi demo endpoint environment instruction regenerating
CKGG Yes12 No No No No Yes13 No No Yes No
CROssBAR-KG Yes14 Yes No Yes Yes Yes15 Yes No No No
ETKGCN Yes16 No No Yes No No No No No No
FarsBase Yes17 No No - - Yes18 Yes Yes No No
GAKG Yes19 Yes No No No Yes20 Yes21 No Yes No
MDKG Yes22 No No No No No No No No No
Ozymandias Yes23 Yes No Yes Yes Yes24 Yes No Yes Yes
RTX-KG2 Yes25 Yes No Yes - - Yes26 Yes Yes -
Following this general comparison of the studied
KGs, this section explores a detailed discussion about the
reproducibilitytestwehaveconducted.Tocarryoutthistest,
we examined the repository of each studied KG (as listed in
Table 2) and carefully followed the provided instructions, if
available,torunthesystem.Notethatmorethanoneperson
hastestedeachsystemtoensurethereliabilityoftheresults.
We draw our findings as:
• Only 3.2% (8 out of 250) of selected KGs have
publicly available source code, indicating the need
for greater encouragement towards open science and
sharing data and code.
• Only one system out of seven open-source KGs
(not considering RTX-KG2) could successfully run.
This shows that only 0.4% of selected 250 KGs
(14.3% of open-source KGs) are reproducible. This
finding opens a new door for further research. It
also indicates that the availability of open-source
code alone does not guarantee the reproducibility
of KGs. The availability of run instructions and the
execution environment also have a significant impact
on reproducibility.
• Tracking provenance of KG construction is rarely
addressed in most papers, indicating a potential gap
in this aspect.
• Only publishing the code cannot conclude the
system’s reproducibility. It is essential to provide
the code along with detailed run instructions and
informationabouttherequiredexecutionenvironment
to facilitate reproducibility.
• Access to the data on which a KG is built presents
another challenge for reproducibility. But, mostly
domain-specific KGs are built within a project or
an organization, where their data is not publicly
available.
• It is worth mentioning that the usage of the code
and data will require the corresponding licenses and
considering their usage restriction.
5. Conclusion & Future work
Domain-specific knowledge graphs (KGs) have
gained popularity due to their usability in different
applications. However, the process of KG development
is often challenging and time-consuming. Thus, their
reproducibility can facilitate the usage of KGs in various
applications.Inthispaper,wehaveconductedananalysisof
existing domain-specific KGs across 19 domains, focusing
on their reproducibility aspects. Our study reveals that only
0.4% (1 out of 250) of the published domain-specific KGs
is reproducible.
An important future direction involves assessing the
extenttowhichKGseffectivelyrecordtheirprovenance.The
process of maintaining KGs in alignment with their data
sources can be made effortless through the establishment of
acomprehensiverecordofsourcecode,inputdata,methods,
andresults.Thisnotonlyallowsotherscientiststoreproduce
the results, but also enables the seamless re-execution of
workflows with modified input data, ensuring that KGs
remain synchronized with evolving data sources.
CRediT authorship contribution statement
Samira Babalou: Conceptualization of this study,
existing Knowledge Graphs analysis, Original draft
preparation. Sheeba Samuel: Conceptualization of this
study, existing Knowledge Graphs analysis, Original draft
preparation. Birgitta König-Ries:Supervision, Validation,
review & editing.
Declaration of competing interest
The authors declare that they have no known competing
financial interests or personal relationships that could have
appeared to influence the work reported in this paper.
Acknowledgements
SB’s work has been funded by the iKNOW Flexpool
project of iDiv, the German Centre for Integrative
Biodiversity Research, funded by DFG (Project number
202548816). SS’s work has been funded by the Carl Zeiss
Foundation for the financial support of the project “A
Virtual Werkstatt for Digitization in the Sciences (K3)”
Page 6 of 8

## PDF page 7

A Survey on Reproducible Domain-Specific Knowledge Graphs
within the scope of the program line “Break-throughs:
Exploring Intelligent Systems for Digitization - explore the
basics, use applications”. We also thank Badr El Haouni,
Erik Kleinsteuber, and Anirudh Kumbakunam Ashok for
testing the systems.
Notes
1https://scholar.google.de/ accessed on 17.01.2022
2https://github.com/fusion-jena/iKNOW/tree/main/
Reproducibility-Survey
3https://github.com/alibaba-research/ConceptGraph
4https://github.com/hao1661282457/Knowledge-graphs
5https://www.geonames.org/.
6https://www.dbpedia.org/
7https://www.wikidata.org
8https://www.ala.org.au
9https://orcid.org
10https://www.gbif.org/what-is-gbif
11http://kg2endpoint.rtx.ai:7474
12https://github.com/nju-websoft/CKGG
13http://ws.nju.edu.cn/CKGG/1.0/demo
14https://github.com/cansyl/CROssBAR
15https://crossbar.kansil.org/
16https://github.com/xcwujie123/Hainan_KG
17https://github.com/IUST-DMLab/wiki-extractor
18http://farsbase.net/sparql
19https://github.com/davendw49/gakg
20https://gakg.acemap.info/
21https://www.acekg.cn/sparql
22https://github.com/ccszbd/MDKG
23https://github.com/rdmpage/ozymandias-demo
24https://ozymandias-demo.herokuapp.com/
25https://github.com/RTXteam/RTX-KG2
26https://arax.ncats.io/api/rtxkg2/v1.2/openapi.json
References
[1] J. Wu, X. Zhu, C. Zhang, and Z. Hu, “Event-centric tourism
knowledge graph—a case study of hainan,” in International
Conference on Knowledge Science, Engineering and Management,
pp. 3–15, Springer, 2020.
[2] L. Cui, H. Seo, M. Tabar, F. Ma, S. Wang, and D. Lee,
“Deterrent: Knowledge guided graph attention network for detecting
healthcare misinformation,” in Proceedings of the 26th ACM
SIGKDD International Conference on Knowledge Discovery & Data
Mining, pp. 492–502, 2020.
[3] Q.Zhu,D.-T.Nguyen,I.Grishagin,N.Southall,E.Sid,andA.Pariser,
“An integrative knowledge graph for rare diseases, derived from
the genetic and rare diseases information center (gard),”Journal of
Biomedical Semantics, vol. 11, no. 1, pp. 1–13, 2020.
[4] A. Hogan, E. Blomqvist, M. Cochez, C. D’amato, G. D. Melo,
C. Gutierrez, S. Kirrane, J. E. L. Gayo, R. Navigli, S. Neumaier,
A.-C.N.Ngomo,A.Polleres,S.M.Rashid,A.Rula,L.Schmelzeisen,
J. Sequeda, S. Staab, and A. Zimmermann, “Knowledge graphs,”
ACM Comput. Surv., vol. 54, jul 2021.
[5] B. N. Taylor, C. E. Kuyatt,et al., Guidelines for evaluating and
expressing the uncertainty of NIST measurement results, vol. 1297.
US Department of Commerce, Technology Administration, National
Institute of Standards and Technology, 1994.
[6] ACM, “Artifact review and badging.” https://www.acm.org/
publications/policies/artifact-review-badging, 2017.
[7] H. E. Plesser, “Reproducibility vs. replicability: a brief history of a
confused terminology,”Frontiers in neuroinformatics, vol. 11, p. 76,
2018.
[8] N. A. of Sciences Engineering and Medicine,Reproducibility and
Replicability in Science. Washington, DC: The National Academies
Press, 2019.
[9] ACM, “Artifact review and badging version 1.1.”https://www.acm.
org/publications/policies/artifact-review-and-badging-current ,
2020.
[10] S. Samuel and B. König-Ries, “Understanding experiments and
research practices for reproducibility: an exploratory study,”PeerJ,
vol. 9, p. e11140, Apr. 2021.
[11] J. P. Ioannidis, D. B. Allison, C. A. Ball, I. Coulibaly, X. Cui, A. C.
Culhane, M. Falchi, C. Furlanello, L. Game, G. Jurman, J. Mangion,
T. Mehta, M. Nitzberg, G. P. Page, E. Petretto, and V. van Noort,
“Repeatability of published microarray gene expression analyses,”
Nature genetics, vol. 41, no. 2, pp. 149–155, 2009.
[12] C. Begley and L. Ellis, “Drug development: Raise standards for
preclinical cancer research. nature.[online]. 483 (7391),” 2012.
[13] M. Baker, “1,500 scientists lift the lid on reproducibility,”Nature
News, vol. 533, no. 7604, p. 452, 2016.
[14] E. Raff, “A step toward quantifying independently reproducible
machine learning research,” in Advances in Neural Information
Processing Systems 32: Annual Conference on Neural Information
Processing Systems 2019, NeurIPS 2019, 8-14 December 2019,
Vancouver, BC, Canada, pp. 5486–5496, 2019.
[15] J. F. Pimentel, L. Murta, V. Braganholo, and J. Freire, “A large-scale
study about quality and reproducibility of jupyter notebooks,”
in Proceedings of the 16th International Conference on MSR ,
pp. 507–517, 2019.
[16] S. Samuel and D. Mietchen, “Computational reproducibility
of jupyter notebooks from biomedical publications,” CoRR,
vol. abs/2308.07333, 2023.
[17] D. Van Assche, G. Haesendonck, G. De Mulder, T. Delva,
P.Heyvaert,B.DeMeester,andA.Dimou,“Leveragingwebofthings
w3c recommendations for knowledge graphs generation,” inWeb
Engineering: 21st International Conference, ICWE 2021, Biarritz,
France,May18–21,2021,Proceedings ,pp.337–352,Springer,2021.
[18] G. A. Gesese, R. Biswas, M. Alam, and H. Sack, “A survey on
knowledge graph embeddings with literals: Which model links better
literal-ly?,”Semantic Web, no. Preprint, pp. 1–31, 2019.
[19] F. Lu, P. Cong, and X. Huang, “Utilizing textual information in
knowledgegraphembedding:Asurveyofmethodsandapplications,”
IEEE Access, vol. 8, pp. 92072–92088, 2020.
[20] M. Wang, L. Qiu, and X. Wang, “A survey on knowledge graph
embeddings for link prediction,”Symmetry, vol. 13, no. 3, p. 485,
2021.
[21] Y. Dai, S. Wang, N. N. Xiong, and W. Guo, “A survey on knowledge
graph embedding: Approaches, applications and benchmarks,”
Electronics, vol. 9, no. 5, p. 750, 2020.
[22] H. Paulheim, “Knowledge graph refinement: A survey of approaches
and evaluation methods,”Semantic web, vol. 8, no. 3, pp. 489–508,
2017.
[23] X. Zou, “A survey on application of knowledge graph,” inJournal
of Physics: Conference Series, vol. 1487, p. 012016, IOP Publishing,
2020.
[24] Z. Zhao, S.-K. Han, and I.-M. So, “Architecture of knowledge graph
construction techniques,”International Journal of Pure and Applied
Mathematics, vol. 118, no. 19, pp. 1869–1883, 2018.
[25] C. Chen, J. Cui, G. Liu, J. Wu, and L. Wang, “Survey and
open problems in privacy preserving knowledge graph: Merging,
query, representation, completion and applications,”arXiv preprint
arXiv:2011.10180, 2020.
[26] D. Q. Nguyen, “A survey of embedding models of entities and
relationships for knowledge graph completion,” arXiv preprint
arXiv:1703.08098, 2017.
[27] S. Arora, “A survey on graph neural networks for knowledge graph
completion,”arXiv preprint arXiv:2007.12374, 2020.
[28] M. Yani and A. A. Krisnadhi, “Challenges, techniques, and trends of
simpleknowledgegraphquestionanswering:Asurvey,” Information,
vol. 12, no. 7, p. 271, 2021.
[29] B. Abu-Salih, “Domain-specific knowledge graphs: A survey,”
Journal of Network and Computer Applications, vol. 185, p. 103076,
2021.
Page 7 of 8

## PDF page 8

A Survey on Reproducible Domain-Specific Knowledge Graphs
[30] M. D. Wilkinson, M. Dumontier, I. J. Aalbersberg, G. Appleton,
M.Axton,A.Baak,N.Blomberg,J.-W.Boiten,L.B.daSilvaSantos,
P. E. Bourne,et al., “The fair guiding principles for scientific data
management and stewardship,”Scientific data, vol. 3, no. 1, pp. 1–9,
2016.
[31] H.Kim,“Aknowledgegraphofmedicalinstitutionsinkorea,”in Web
Semantics, pp. 55–68, Elsevier, 2021.
[32] N. Zhang, Q. Jia, S. Deng, X. Chen, H. Ye, H. Chen, H. Tou,
G.Huang,Z.Wang,N.Hua, etal.,“Alicg:Fine-grainedandevolvable
conceptual graph construction for semantic search at alibaba,” in
Proceedings of the 27th ACM SIGKDD Conference on Knowledge
Discovery & Data Mining, pp. 3895–3905, 2021.
[33] X. Hao, Z. Ji, X. Li, L. Yin, L. Liu, M. Sun, Q. Liu, and
R. Yang, “Construction and application of a knowledge graph,”
Remote Sensing, vol. 13, no. 13, p. 2511, 2021.
[34] T. Doğan, H. Atas, V. Joshi, A. Atakan, A. S. Rifaioglu, E. Nalbat,
A. Nightingale, R. Saidi, V. Volynkin, H. Zellner,et al., “Crossbar:
Comprehensive resource of biomedical relations with deep learning
applications and knowledge graph representations,”bioRxiv, 2020.
[35] T. Doğan, H. Atas, V. Joshi, A. Atakan, A. S. Rifaioglu, E. Nalbat,
A. Nightingale, R. Saidi, V. Volynkin, H. Zellner,et al., “Crossbar:
comprehensive resource of biomedical relations with knowledge
graph representations,” Nucleic Acids Research, vol. 49, no. 16,
pp. e96–e96, 2021.
[36] Y. Shen, Z. Chen, G. Cheng, and Y. Qu, “Ckgg: A chinese
knowledge graph for high-school geography education and beyond,”
in International Semantic Web Conference, pp. 429–445, Springer,
2021.
[37] W.R.VanHage,V.Malaisé,R.Segers,L.Hollink,andG.Schreiber,
“Design and use of the simple event model (sem),”Journal of Web
Semantics, vol. 9, no. 2, pp. 128–136, 2011.
[38] M. B. Sajadi, B. Minaei, and A. Hadian, “Farsbase: A cross-domain
farsi knowledge graph.,” inSEMANTICS Posters&Demos, 2018.
[39] C. Deng, Y. Jia, H. Xu, C. Zhang, J. Tang, L. Fu, W. Zhang,
H. Zhang, X. Wang, and C. Zhou, “Gakg: A multimodal geoscience
academic knowledge graph,” in Proceedings of the 30th ACM
InternationalConferenceonInformation&KnowledgeManagement ,
pp. 4445–4454, 2021.
[40] C. Fu, R. Zhong, X. Jiang, T. He, and X. Jiang, “An integrated
knowledge graph for microbe-disease associations,” inInternational
Conference on Health Information Science, pp. 79–90, Springer,
2020.
[41] R. D. Page, “Ozymandias: a biodiversity knowledge graph,”PeerJ,
vol. 7, p. e6739, 2019.
[42] E. Wood, A. K. Glen, L. G. Kvarfordt, F. Womack, L. Acevedo, T. S.
Yoon, C. Ma, V. Flores, M. Sinha, J. C. Roach,et al., “Rtx-kg2: a
system for building a semantically standardized knowledge graph for
translational biomedicine,”bioRxiv, 2021.
[43] M. McNutt, “Reproducibility,” 2014.
[44] N.Research,“Reportingstandardsandavailabilityofdata,materials,
code and protocols,” 2014.
[45] G. K. Sandve, A. Nekrutenko, J. Taylor, and E. Hovig, “Ten simple
rulesforreproduciblecomputationalresearch,” PLOSComputational
Biology, vol. 9, pp. 1–4, 10 2013.
[46] J. M. Alston and J. A. Rick, “A beginner’s guide to conducting
reproducible research,” The Bulletin of the Ecological Society of
America, vol. n/a, no. n/a, p. e01801, 2020.
[47] J.a.F.Pimentel,L.Murta,V.Braganholo,andJ.Freire,“Alarge-scale
study about quality and reproducibility of jupyter notebooks,” in
Proceedingsofthe16thInternationalConferenceonMiningSoftware
Repositories, MSR ’19, p. 507–517, IEEE Press, 2019.
[48] K. Belhajjame and M.-Y. Mejri, “Online maintenance of evolving
knowledge graphs with rdfs-based saturation and why-provenance
support,”Journal of Web Semantics, p. 100796, 2023.
[49] A. Avgoustaki, G. Flouris, I. Fundulaki, and D. Plexousakis,
“Provenance management for evolving RDF datasets,” in The
Semantic Web. Latest Advances and New Domains - 13th
International Conference, ESWC 2016, Heraklion, Crete, Greece,
May 29 - June 2, 2016, Proceedings (H. Sack, E. Blomqvist,
M.d’Aquin,C.Ghidini,S.P.Ponzetto,andC.Lange,eds.),vol.9678
of Lecture Notes in Computer Science, pp. 575–592, Springer, 2016.
[50] E. Jiménez-Ruiz, O. Hassanzadeh, V. Efthymiou, J. Chen, and
K. Srinivas, “Semtab 2019: Resources to benchmark tabular data
to knowledge graph matching systems,” inEuropean Semantic Web
Conference, pp. 514–530, Springer, 2020.
[51] C.Bizer,“Theemergingweboflinkeddata,” IEEEintelligentsystems ,
vol. 24, no. 5, pp. 87–92, 2009.
[52] M. Färber, F. Bartscherer, C. Menne, and A. Rettinger, “Linked data
quality of dbpedia, freebase, opencyc, wikidata, and yago,”Semantic
Web, vol. 9, no. 1, pp. 77–129, 2018.
Page 8 of 8
