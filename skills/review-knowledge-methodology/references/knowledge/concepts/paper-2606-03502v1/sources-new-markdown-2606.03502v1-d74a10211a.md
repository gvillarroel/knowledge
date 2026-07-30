---
type: Research Paper
title: 'A Community Survey on SHACL and ShEx: Briding Gaps in RDF Validation'
description: Current practitioner evidence on RDF validation benefits, documentation,
  performance, tooling, and expressiveness gaps.
resource: https://example.org/knowledge-methodology-papers/resource/paper-2606-03502v1/sources%2Fnew%2Fmarkdown%2F2606.03502v1
tags:
- paper-2606-03502v1
- markdown
- rl
sources:
- id: paper-2606-03502v1
  resource: sources/new/markdown/2606.03502v1.md
  title: paper-2606-03502v1
generated:
  by: process:semantic-okf-python
concept_id: concepts/paper-2606-03502v1/sources-new-markdown-2606.03502v1-d74a10211a
concept_path: concepts/paper-2606-03502v1/sources-new-markdown-2606.03502v1-d74a10211a.md
subject_iri: https://example.org/knowledge-methodology-papers/resource/paper-2606-03502v1/sources%2Fnew%2Fmarkdown%2F2606.03502v1
ontology_class_iri: https://example.org/ontology/knowledge-methodology-papers#Paper
ontology_version_iri: https://example.org/ontology/knowledge-methodology-papers/1.0.0
source_id: paper-2606-03502v1
source_kind: markdown
source_path: sources/new/markdown/2606.03502v1.md
source_content_sha256: 4b9f154508886847658eae69a54deb377453d26a1304ae40d792a8f04de0c9df
record_sha256: 23cb2c82fa94f0aac3cdaf8d5211f37fe1ef2289be80087e64ec12771fa293e2
source_refs:
- https://example.org/knowledge-methodology-papers/provenance/record/paper-2606-03502v1/b5d9c37fb91e1d935e234d3c
record_id: sources/new/markdown/2606.03502v1
---

# A Community Survey on SHACL and ShEx: Briding Gaps in RDF Validation

## Dataset relevance

Current practitioner evidence on RDF validation benefits, documentation, performance, tooling, and expressiveness gaps.

- Coverage lanes: validation-and-reproducibility; knowledge-graphs-and-ontologies
- Relevant skills: build-semantic-okf-*; extract-ontologies; open-knowledge-format

## Source citation

- Pinned arXiv record: [2606.03502v1](https://arxiv.org/abs/2606.03502v1)
- Authors: Jakubowski, Maxime; Tomaszuk, Dominik; Hose, Katja
- PDF: [https://arxiv.org/pdf/2606.03502v1](https://arxiv.org/pdf/2606.03502v1)
- PDF SHA-256: `bbc5fafe39cb1135c9adcf6fd3c57d96d5f962cf8a1b9551c706865d078dbc35`
- Extracted pages: 17

The following text was extracted page by page from the pinned PDF. Page headings are stable evidence locators.

## PDF page 1

A Community Survey on SHACL and ShEx:
Briding Gaps in RDF Validation
Maxime Jakubowskia, Dominik Tomaszuka,b, and Katja Hosea
aTU Wien ,firstname.lastname@tuwien.ac.at
bUniversity of Bialystok ,d.lastname@uwb.edu.pl
Abstract
This paper examines RDF validation practices and challenges to understand
stakeholder applications, their needs, and identify areas for improvement in tech-
nologies and methodologies, thereby guiding future research and standardization
efforts. A community survey was conducted, targeting a diverse group of RDF
validation technology users across academia and industry. The survey collected
data on current practices, tool usage, perceived benefits, limitations, and desired
enhancements to gain a broad overview of the validation landscape. Our analy-
sis shows that while RDF validation is widely adopted and valued for enhancing
data quality, significant challenges remain. In particular, users report a need for
better documentation, improved tool support, enhanced performance, and greater
language expressiveness to handle complex large-scale validation tasks effectively.
This work provides crucial insights into the RDF validation landscape, highlight-
ing current practices and key areas for development. It offers a foundation for
researchers, developers, and standardization bodies to address current limitations
and advance validation technologies, ultimately improving data quality and usabil-
ity in knowledge graphs.
1 Introduction
Knowledge Graphs (KGs) have become a ubiquitous data representation paradigm
used across the public Web, and within numerous organizational contexts [21]. Their
inherent flexibility and broad applicability across diverse domains have driven this
widespread adoption. Recently, its relevance is further established by the growing
importance in grounding AI systems in facts, using techniques like Graph Retrieval-
Augmented Generation (GraphRAG) in relation to LLMs [22, 38, 10]. Prominent ex-
amples of publicly available KGs include WikiData [36], Y AGO [32], and DBpedia [3].
Many of these public KGs leverage the Resource Description Framework (RDF) [28] as
their underlying storage model, which offers advantages such as a flexible and schema-
less approach to data modeling.
1
arXiv:2606.03502v1  [cs.DB]  2 Jun 2026

## PDF page 2

As the KG landscape matured and the volume of RDF data grew, the need for
mechanisms to enforce structural constraints and ensure data quality became increas-
ingly apparent. This requirement led to the development of so-calledshape languages,
which provide a means to defineshapesthat express structural constraints on RDF
graphs. These shapes enable the specification of expected patterns and properties
within the graph data. The two most prominent shape languages are the Shapes Con-
straint Language (SHACL) [16] and Shape Expressions (ShEx) [25], which have gar-
nered significant attention and adoption within the community. While SHACL and
ShEx present syntactic differences, the primary function of these technologies isvali-
dation, i.e., checking whether a given RDF graph adheres to the defined shapes.
Since the World Wide Web Consortium’s (W3C) recommendation of SHACL in
2017, interest and adoption of shape languages have grown steadily in both practical
applications and academic research. This increasing relevance is evidenced by the
continually expanding body of related literature and, notably, the recent establishment
of a new W3C working group dedicated to developing the next version of SHACL
(SHACL 1.2) [6].
Despite this clear momentum and ongoing evolution of standards, a deeper under-
standing of the current RDF validation landscape from the community’s perspective
is needed. Specifically, detailed insights are often lacking regarding which aspects of
shape languages like SHACL and ShEx are most valued or challenging in practice,
how validation techniques are being applied across diverse contexts (particularly in
industry), and what primary obstacles hinder wider adoption or more effective use.
Therefore, this paper aims to investigate these practical applications, perceived com-
munity needs, and challenges related to RDF validation. Understanding these nuances
is crucial not only for informing standardization efforts but also for helping guide fu-
ture research towards real-world requirements and bridging identified gaps. To gather
this information, we conducted a comprehensive community survey targeting a diverse
audience across both industry and academic settings involved with RDF validation.
This paper is structured as follows. Section 2 discusses essential details about the
survey’s structure and data collection. While Section 3 presents insights into the current
state of the RDF validation landscape, Section 4 highlights the needs and opportunities
for further research and development. Then, Section 5 presents our open dataset, how
to reproduce our charts and tables, and how to derrive your own insights. Section 6 con-
cludes the paper, distilling overarching insights and implications for both practitioners
and researchers.
2 Survey Design and Data Collection
To gain insights into current practices, challenges, and community needs surrounding
RDF validation technologies (primarily SHACL and ShEx), we conducted a compre-
hensive online survey between December 2024 and March 2025, yielding 94 responses.
The survey utilized a mix of multiple-choice and free-text questions, allowing us to
gather both quantitative data and richer qualitative perspectives. Outreach efforts used
relevant technical mailing lists and social media platforms to reach interested prac-
titioners and researchers, supplemented by direct invitations to active SHACL/ShEx
2

## PDF page 3

researchers identified via the DBLP SPARQL endpoint1.
The survey investigated several key areas to build a holistic picture: respondents’
backgrounds and experience levels; the contexts and domains where validation is ap-
plied; specifics of validation usage including tooling, data scale, perceived benefits,
and limitations; adoption patterns for specific SHACL features; methodologies used
for shape creation; and desired future developments or improvements. Several ques-
tions were adapted from the earlier work by Rabbani et al. [26], enabling comparison
and providing insights into how practices, particularly around shape creation, may have
evolved since 2022.
Throughout this paper, specific findings are sometimes linked to the survey question
numbers for clarity. The survey can still be accessed online 2 for reference and is also
still open to collect future responses.
Supplementary MaterialThe data from the survey can be found on GitHub 3. All
relevant graphs, data needed to reproduce the figures from this paper, as well as further
details on the survey methodology, can be found on our website4. We also exposed the
survey data as a DuckDB SQL database that can be queried in a browser5.
3 Validation Landscape: Insights and Trends
In this section, we will address three main themes extracted from the survey data.
Profiling the users.The survey data allows us to profile the community engaging
with RDF validation, shedding light onwho the users are and the contexts in which
these technologies are applied. A key aspect of the user profile is the growing scale
and establishment of the user base, evidenced by the strong response to the current
survey (94 respondents) compared to the 30 respondents in the 2022 survey [26]. Fig-
ure 1a reveals a notable growth in participation from the academic community com-
pared to 2022. Additionally, Figure 1c suggests that adoption within academic circles
has particularly accelerated in the last one to three years, likely influenced in part by the
maturity and standardization of SHACL since its recommendation in 2017. Neverthe-
less, we also observe a strong industry presence. Additionally, there is notable usage
within government contexts, with government data being one of the most frequently
cited domains (Figure 1b), potentially reflecting drivers like open data initiatives or
data quality mandates. Generally, we see that validation technologies are used over a
varied number of domains, highlighting their broad applicability.
Another key characteristic revealed in the user profile concerns experience with dif-
ferent validation languages. Among the available shape languages, SHACL is clearly
the most widely used within the surveyed community, with the vast majority of respon-
dents indicating familiarity (Figure 1d). This pattern of widespread experience with
1The query can be found here:https://sparql.dblp.org/ux1k67.
2https://forms.gle/LdXsG644obcgSsAE6
3https://github.com/dmki-tuwien/rdf-validation-community-survey/
4https://dmki-tuwien.github.io/rdf-validation-community-survey/
5https://dmki-tuwien.github.io/rdf-validation-community-survey/databaseshell
3

## PDF page 4

AcademiaAcademia & IndustryIndustryGovernment
20252022
45%26%
24%4%1% 27%
20%
53%
(a) Professional Background
01020304050Government dataIoT/sensor dataBiomedical dataGeographic dataFinancial dataCultural dataSocial dataEducational dataNot domain specific dataEnterprise dataManufacturing dataSoftware dataLegal dataOther (b) Application Domains
024681012141618
Less than 1year1 to 3 years3 to 5 yearsMore than 5yearsAcademiaAcademia & IndustryIndustry
(c) Years of Experience
91 198SHACLShExOther (d) Language Familiarity
Figure 1: User Background and Usage Profile
SHACL appears consistent across different professional backgrounds observed in the
survey. While we cannot pinpoint the exact reasons for this extensive familiarity using
the survey data, it is likely influenced significantly by SHACL’s W3C recommendation
status, alongside factors like perceived technical advantages or available tooling.
In summary, the user profile emerging from the survey indicates that validation
technologies are maturing beyond early adopters, establishing a strong foothold in in-
dustry while gaining significant traction within academia. Their application spans di-
verse domains, with notable government usage suggesting potential roles in ensuring
data quality and compliance. While SHACL is the dominant language, likely boosted
by standardization and familiarity, ShEx maintains a relevant user base.
Shape Creation Practices.Our survey also provides insights into thecommon prac-
tices surrounding shape creation, revealing the methods and tools currently in use.
As can be seen in Figure 2, manual authoring remains the predominant method. How-
ever, automated generation techniques are also widely employed. Compared to findings
from 2022 [26], there is a notable increase in generating shapes directly from instance
data. Interestingly, this holds when looking accross backgrounds, and levels of experi-
ence, indicating that this is a general trend.
Free-text responses also highlighted the practice of generating validation shapes
from diverse non-RDF artifacts, most frequently citing sources like JSON Schema [23]
and LinkML [19]. This suggests a need to bridge RDF validation with other schema
specifications or higher-level conceptual models. This is an area with potential for
4

## PDF page 5

01020304050607080
OtherFrom Instance DataFrom OntologiesManual20252022
Figure 2: Methods for Shape Creation
new tooling and investigation, which currently appears under-explored. Furthermore,
respondents explicitly noted a need for clearer mappings between OWL ontologies and
SHACL shapes.
Regarding shape authoring tooling (Table 1a), general text editors, Prot ´eg´e, and
commercial solutions like TopBraid EDG are the most common tools reported for au-
thoring shapes. Conversely, while there has been active research [11, 27], the land-
scape fortoolsspecifically targeting shape extraction (e.g., from data) appears more
fragmented. This may indicate a less mature or more diverse tooling ecosystem for this
specific task compared to general shape authoring.
In summary, whilemanual authoring persists, automated methods, particularly
data-driven shape generation, are gaining ground. The practice of generating shapes
from various non-RDF artifacts and the limited state of shape extraction tooling repre-
sent key opportunities for future research and development.
Validation Practices and Tooling.The survey leads to valuable insights into theop-
erational aspects of RDF validation. Looking at the validation tooling (Table 1b),
the survey reveals a diverse ecosystem where tool prominence issignificantly influ-
enced by underlying programming languages and their established library support.
For instance, widely adopted SHACL solutions like Apache Jena (Java) and PySHACL
(Python) as well as popular ShEx tools like PyShEx and Apache Jena ShEx, are tied
to these mainstream ecosystems, likely facilitating their integration. Beyond these, the
significant presence of commercially supported tools like TopBraid EDG (TopQuad-
rant) and rdf-validate-shacl (Zazuko), especially in industry, underscores the influence
of dedicated vendor support on tool selection.
This diverse tooling supports a spectrum of validation intensities. Notably, vali-
dation ismore frequently integrated into operational workflows in industry, with daily
or weekly use being common, compared to more varied or sporadic application in aca-
demic settings (Figure 3). Such regular usage in industry naturally demands more from
both the languages and the tools. This is also reflected inhow deeply language features
are utilized: high-frequency SHACL users, often in the industry context, are signifi-
5

## PDF page 6

Generator/Extraction 2025 2022
Astrea [7] 1 2
Prot´eg´e [20] 10 6
RDFShape [14] 1 5
SHACL Play [13] 5 1
SHACLGEN [1] 2 1
Shape Designer [5] 1 1
SheXer [11] 0 3
Spahiu et al. [30] 1 1
Text Editor 39 8
TopBraid EDG [35] 5 10
UnSHACLed [18] 1 1
(a) Shape Generation/Extraction
Validator Academia Industry Both
Apache Jena SHACL [2] 16 12 12
PySHACL [29] 17 8 13
TopBraid EDG [35] 10 9 6
RDF4J [33] 10 6 3
rdf-validate-shacl [37] 1 5 3
shacl-engine [4] 3 2 4
shacl-js [34] 4 0 4
maplib [9] 1 2 0
Corese SHACL [8] 2 0 0
Stardog SHACL [31] 0 1 1
rudof [17] 1 0 0
(b) Validators
Table 1: Tools for SHACL Extraction and Validation
Advanced Feature Acad. Ind. Both
Expression constraints 7 4 5
Node expressions 9 6 6
SHACL functions 8 10 4
SHACL rules 13 13 10
(a) Advanced SHACL Feature Usage
Graph Size Acad. Ind. Both
1 to 100K triples 22 7 14
100K to 1M triples 8 6 3
1M to 100M triples 8 7 4
More than 100M triples 4 3 3
(b) Graph Size at Validation Time
Table 2: Operational Context
cantly more likely to employ advanced6 capabilities like SHACL Rules and Functions
(Table 2a). These advanced features are not part of the W3C SHACL Recommenda-
tion, but are a collection of useful extensioins of SHACL. This reliance on the advan-
vced features indicates that standard features alone can be insufficient in some data
engineering contexts, pushing users towards more expressive features.
These practices are applied across varied dataset sizes (Table 2b), from manageable
academic datasets to the very large knowledge graphs increasingly found in industry
settings. The interplay of frequent validation cycles, the need for advanced features,
and the challenge posed by large datasets collectively defines the demanding opera-
tional context that current and future validation technologies should address.
In essence, the way validation is practiced, particularly the higher frequency, greater
use of advanced features, and often larger data scales in industry, shapes the demands
on both languages and tools. This operational context reveals aneed for robust, expres-
sive, and scalable validation solutions, supported by a diverse tooling ecosystem that
caters to varying levels of complexity and integration requirements.
6https://www.w3.org/TR/shacl-af/
6

## PDF page 7

05101520253035
DailyWeeklyMonthlyRarelyNeverTotalAcademiaIndustryBoth
Figure 3: Validation Usage Frequency
Perceived Advantage Ac. Ind. Both
Compatibility with RDF 34 22 20
Strong validation capabilities 21 17 20
Flexible constraints 23 13 17
Integration with existing tools 14 10 12
Ease of use 16 10 7
Advanced constraints 9 6 13
Documentation quality 12 6 7
Community support 13 6 5
Comprehensive documenta-
tion
5 4 2
Performance and scalability 3 3 4
Issue / Limitation Ac. Ind. Both
Documentation and tutorials 22 8 11
Community and tool support 20 11 8
Performance and scalability 17 9 11
Lack of features and func-
tionality
14 11 8
Limited constraint types 11 11 10
No major challenges 8 5 10
Interoperability 12 4 0
Usability 2 0 3
Lack of implementations 1 2 1
Cumbersome syntax 0 1 2
Table 3: Perceived Advantages and Reported Issues with Validation Technologies
4 Current Challenges and Future Opportunities
Charting the future trajectory for RDF validation requires a clear understanding of its
current standing within the community. Therefore, we explore identified limitations
and desired enhancements to pinpoint key opportunities for advancement and research.
To get a more complete picture, we start with analizing the perceived advantages of
current validation technologies (Table 3). Two primary themes emerge; first, respon-
dents frequently mentioned thestrong validation capabilitiesandflexibilityoffered for
defining constraints, indicating general satisfaction with the core expressive power and
design principles of languages like SHACL and ShEx. Second, the benefit of integra-
tion within the widerRDF ecosystemand compatibility with existing tooling was often
highlighted, underscoring the practical value derived from standardization efforts.
Complementing these advantages, the investigation into desired features and cur-
rent limitations reveals key areas needing attention by the community (Table 3). Signif-
icant hurdles to wider adoption and more effective use appear to be the current state of
support, usability, and documentation. Survey respondents frequently cited inadequate
documentation and tutorials, alongside gaps in comprehensive tool support, as promi-
7

## PDF page 8

051015202530
AlwaysFrequentlyOccasionallyRarelyNever
(a) Frequency of Use
70%
23%7%The shape is notexpressible inSHACL-coreIt is easier towrite the shape inSHACL-SPARQLOther (b) Motivation for Use
Figure 4: SHACL-SPARQL Usage
nent challenges. The absence of foundational learning resources, such as an official
W3C SHACL Primer comparable to those for other RDF standards, was specifically
highlighted as a notable shortcoming.
Furthermore, two critical technical challenges emerged from the survey:ensuring
adequate performance, particularly for large datasets, and addressing perceivedgaps
in the expressiveness of the core validation languages. Scalability remains a press-
ing concern, with performance bottlenecks frequently reported by users working with
large graphs (Figure 6a). While some initial research has moved in the direction of ad-
dressing these issues [15, 12], the survey indicates that significant challenges remain.
Simultaneously, the survey indicates that the expressive power of core SHACL is often
found insufficient for complex validation needs. Figure 4a shows that users often resort
to SHACL-SPARQL7, which allows for writing SPARQL-based constraints beyond the
standard components. Moreover, Figure 4b shows the primary reason is the increased
expressiveness. Furthermore, Figure 6b shows that frequent users of SHACL, also tend
to more frequently rely on non-standard SHACL Advanced Features8.
Additionally, specifically desired language extensions, such as robust support for
validating named graphs, were also voiced in free-text answers. Consequently, the call
for better tooling, specifically for SHACL-SPARQL and these Advanced Features, not
only underscores the general tool support gap but also the community’s need for mature
implementations of these more complex and expressive features.
Table 4b shows specific areas for future development. A clear call from the com-
munity is for these languages to evolve in alignment with broader RDF advancements
and to address current functional gaps. This is evidenced by strong interest insupport
for RDF 1.2/RDF-Star, ensuring validation tools can handle the latest RDF advance-
ments. Another prominent request is the high demand forexplicit support for recursive
shape constraints in SHACL, where we highlight the strong reaction from respondents
with a background in industry. Given that recursion is a capability in ShEx but remains
undefined in the SHACL specification, this signals a need for standardized, compre-
hensive feature sets, a topic noted for consideration by the W3C Data Shapes working
group [6].
Beyond language features,improving the usability of validation reportsalso emerged
7https://www.w3.org/TR/shacl/#sparql-constraints
8https://www.w3.org/TR/shacl-af/
8

## PDF page 9

Statement Count
5 - It is too detailed 1
4 - It is sufficient but too verbose 7
3 - It is adequate 40
2 - It needs to be more informative 25
1 - It requires significant enhancement 11
(a) Validation Report Usefulness
Desired Feature Acad. Ind. Both
Support for RDF 1.2 13 18 12
Support for recursive shapes 15 12 9
Support for Property Graphs 12 5 5
Other 4 4 4
None 4 1 2
(b) Desired Future Language Features
Table 4: User Feedback on Validation Reports and Desired Language Features
Not working withEvolving KGsBy adjusting theshapes over timeBy writing flexibleshapesBy automatingshape updates
Figure 5: Methods for Validating Evolving KGs
as an opportunity. Table 4a indicates that while SHACL validation reports are gener-
ally satisfactory, there is considerable scope for enhancing their usability, potentially
through more informative error details or better integration with debugging workflows.
Finally, the survey touched upon the increasingly relevant challenge of managing
evolving knowledge graphs [24]. A significant majority (67%) of respondents reported
working with evolving graph data in their validation workflows (Figure 5). Many in-
dicated that changes to the graph often necessitate manual adjustments to their shape
constraints, highlighting a need for more robust methods or tooling to manage the co-
evolution of data and constraints in dynamic environments. This presents a key area
for future research and innovation.
In summary, while RDF validation technologies like SHACL and ShEx are valued
for their core capabilities and ecosystem integration, our survey indicates paths for en-
hancement crucial for both practitioners and researchers. Firstly,improving the support
9

## PDF page 10

01020304050
1 to 100Ktriples100K to 1Mtriples1M to 100MtriplesMore than100M triplesTotal respondentsPerformance concern
(a) Graph Size vs. Performance Concerns
05101520253035
DailyWeeklyMonthlyRarelyNeverTotal respondentsAdvanced features (b) Frequency of Use vs. Advanced Features
Figure 6: Advanced Analysis
infrastructure and usabilityremains vital for effective adoption. This includes better
documentation and tutorials (e.g., official primers), more mature tooling, and enhanced
validation report utility to aid debugging and understanding of existing features.
5 Interactive Data Exploration
In our commitment to open science and fostering community engagement, this section
details the methodology behind our data analysis and introduces the survey dataset as
an interactive resource. All figures, tables, and quantitative analyses presented in this
paper are the direct result of SQL queries executed against a structured and publicly
available version of our survey data.
5.1 From Raw Responses to Queryable Data
The journey from the initial survey responses, collected via Google Forms, to a queryable
dataset involved a systematic preparation process. Firstly, predefined answer options
for multiple-choice questions were assigned consistent codes (e.g., the tool “Apache
Jena SHACL” as an answer to Q11 was coded as “apache”). Secondly, free-text an-
swers were manually reviewed. Where responses clearly corresponded to existing
coded options, they were mapped accordingly. For frequently occurring and distinct
free-text answers relevant to our analysis, new codes were introduced. This curated
and coded dataset was then loaded into a DuckDB 9 database. The complete dataset,
including the raw CSV files, and the DuckDB database file are publicly available10.
5.2 Navigating the Survey Data: A Glimpse into the Schema
The database is structured to facilitate our analysis through querying. The primary
tables are:
9https://duckdb.org/
10https://github.com/dmki-tuwien/rdf-validation-community-survey/blob/main/
README.md
10

## PDF page 11

answersThe central table where each row corresponds to a unique respondent. Columns
represent individual questions (e.g.,q01for professional background,q11for
SHACL tools used). For questions allowing multiple selections, answers are
stored as arrays of codes.
answers historicalThis table contains responses from the 2022 survey [26], which
had a smaller scope. This allows for longitudinal comparisons for questions that
were part of both survey editions.
question ltA lookup table that maps the question IDs (used as column names in
answers) to their full, textual descriptions (e.g., “What is your professional
background?”).
qXX ltA series of lookup tables, one for each questionqXX(e.g.,q01 lt). These
tables translate the internal codes used for answers (e.g., “apache” for Q11) back
to their descriptive labels (e.g., “Apache Jena SHACL”).
This relational structure allows for flexible data aggregation, filtering, and joining to
extract insights.
5.3 Illustrative Queries
The quantitative results presented throughout this paper were derived using SQL queries.
For instance, to generate the data for Figure 1a (Professional Background of respon-
dents), the following query was used:
WITH current_answer_counts AS (
SELECT q01, COUNT(respondent_id) AS current_respondent_count
FROM answers
GROUP BY q01 ),
historical_answer_counts AS (
SELECT q01, COUNT(*) AS historical_respondent_count
FROM answers_historical
GROUP BY q01 )
SELECT qlt.label AS "Background",
COALESCE(cac.current_respondent_count, 0) AS "Count 2025",
COALESCE(hac.historical_respondent_count, 0) AS "Count 2022"
FROM q01_lt qlt
LEFT JOIN current_answer_counts cac ON qlt.identifier = cac.q01
LEFT JOIN historical_answer_counts hac ON qlt.identifier = hac.q01
ORDER BY "Count 2025";
This query counts respondents based on their professional background (Q01), joining
with theq01 lttable to display human-readable labels. The results of this query are
then visualized in Figure 1a.
The true power of this open dataset lies in its potential for novel explorations, al-
lowing for deeper dives into the characteristics and needs of specific user segments.
For instance, one might want to understand the “expressiveness chasm” more acutely
by focusing on SHACL power users. We can pose a research question such as: ”What
are the common professional backgrounds, primary motivations for using SHACL-
SPARQL, and most desired SHACL language extensions among those who not only
11

## PDF page 12

use SHACL-SPARQL ‘Frequently’ or ‘Always’ but also specifically employ ‘SHACL
Rules’?”
To answer this, a SQL query can be constructed to first filter our answers table for
respondents matching this precise profile (heavy SHACL-SPARQL users via Q17 and
SHACL Rules users via Q20). For this identified segment, the query then aggregates
their responses regarding professional background (Q01), their stated reasons for using
SHACL-SPARQL (Q18), and the future SHACL language features they desire (Q21).
The provided example query demonstrates exactly this, aiming to count how many
users within this advanced segment share particular combinations of these characteris-
tics. We can formulate this as follows:
WITH TargetUserSegment AS (
-- Identify respondents who are heavy SHACL-SPARQL users (Q17)
-- AND use SHACL Rules (Q20).
SELECT a.respondent_id,
a.q01, -- background
a.q18, -- SHACL-SPARQL usage motivation
a.q21 -- desired SHACL extensions
FROM answers a
JOIN q17_lt q17lt
ON a.q17 = q17lt.identifier -- SHACL-SPARQL usage frequency
WHERE q17lt.label IN (’Always’, ’Frequently’) -- heavy usage
AND EXISTS ( -- Check if they use SHACL rules
SELECT 1 FROM UNNEST(a.q20) AS u20(code)
JOIN q20_lt ON q20_lt.identifier = u20.code
WHERE q20_lt.label = ’SHACL rules’ ) ),
SegmentNeedsAndMotivations AS (
-- For the target user segment, unnest their desired extensions (Q21)
-- and join to get labels for their background (Q01) and motivation (Q18).
SELECT tus.respondent_id,
q01lt.label AS background_label,
q18lt.label AS sparql_motivation_label,
unnested_q21.extension_code
FROM TargetUserSegment tus
JOIN q01_lt q01lt ON tus.q01 = q01lt.identifier
JOIN q18_lt q18lt ON tus.q18 = q18lt.identifier,
UNNEST(tus.q21) AS unnested_q21(extension_code)
)
-- Count unique respondents within the segment for combinations of
-- prof. backgr., SHACL-SPARQL motivation, and desired SHACL extension.
SELECT snm.background_label AS "Prof. Backgr. (Q01)",
snm.sparql_motivation_label AS "SHACL-SPARQL Motive (Q18)",
q21lt.label AS "SHACL Extension (Q21)",
COUNT(DISTINCT snm.respondent_id) AS "Respondent Count"
FROM SegmentNeedsAndMotivations snm
JOIN q21_lt q21lt ON snm.extension_code = q21lt.identifier
GROUP BY "Prof. Backgr. (Q01)",
"SHACL-SPARQL Motive (Q18)",
"SHACL Extension (Q21)"
-- Show only combinations with actual respondents
HAVING COUNT(DISTINCT snm.respondent_id) > 0
-- Show most common combinations first
ORDER BY "Respondent Count" DESC;
The results from this query are shown in Table 5. It illustrates the dataset’s poten-
12

## PDF page 13

tial to highlight patterns even within niche subgroups. In the example, we observe
that for users employing both frequent SHACL-SPARQL and SHACL Rules, the pre-
dominant motivation appears to be the perceived limitations of SHACL-core, and their
desired extensions frequently include support for RDF 1.2, recursive shapes, and prop-
erty graphs. This demonstrates how the dataset can be used to connect different facets
of user experience for highly specific cohorts.
Prof. Backgr. (Q01) SHACL-SPARQL Motive (Q18) SHACL Extension (Q21) Count
Academia The shape is not expressible in SHACL-core Support for property graphs 3
Academia The shape is not expressible in SHACL-core Support for RDF 1.2 2
Academia The shape is not expressible in SHACL-core Support for recursive shapes 2
Both The shape is not expressible in SHACL-core Support for RDF 1.2 2
Both The shape is not expressible in SHACL-core Support for recursive shapes 2
Industry The shape is not expressible in SHACL-core Support for RDF 1.2 2
Industry The shape is not expressible in SHACL-core Support for recursive shapes 2
Academia The shape is not expressible in SHACL-core None 1
Both The shape is not expressible in SHACL-core Other 1
Both It is easier to write Support for recursive shapes 1
Both Other Support for RDF 1.2 1
Both Other Support for property graphs 1
Industry The shape is not expressible in SHACL-core Other 1
Industry The shape is not expressible in SHACL-core Support for property graphs 1
Table 5: Profile of Advanced SHACL Users
While the example query showcases the dataset’s ability to identify and profile
niche user segments, the small respondent counts in such granular analyses mean these
specific findings are more indicative than statistically definitive. The dataset’s true
value here is in demonstrating its potential as a starting point for diverse research in-
quiries, which could then be explored further, perhaps with qualitative methods.
5.4 Your Turn: Access the Data and Tools
To immediately explore the data and begin deriving your own insights, we invite you
to use the in-browser queryable instance of our survey data available on our website.
You can write your SQL queries directly in the browser and see results interactively11.
For those who prefer to work locally or integrate the data into other analysis environ-
ments, the complete dataset, including the DuckDB file, is also available for download.
DuckDB is a lightweight, file-based SQL database that requires no complex setup,
making it easy to query using various tools.
We encourage you to explore the data, replicate our findings, challenge our inter-
pretations, and, most importantly,derive your own insights!
6 Conclusions
In this paper, we presented an analysis of the RDF validation landscape, drawing upon
our recent community survey. Our findings offer a contemporary snapshot of how
11https://dmki-tuwien.github.io/rdf-validation-community-survey/databaseshell
13

## PDF page 14

SHACL and ShEx are adopted, the methods used for creating shapes and executing
validation, and the prevailing challenges and needs. The survey highlights the matu-
ration of RDF validation, particularly the widespread experience with SHACL across
diverse domains and user backgrounds, including a notable recent growth in academia
alongside persistent industry engagement. While validation is widely perceived to en-
hance data quality, and automated shape generation from instance data is gaining trac-
tion, significant challenges persist. Our analysis underscores a consistent demand for
improved usability (especially better documentation and more intuitive tooling), en-
hanced performance at scale, and greater language expressiveness to meet complex
real-world requirements.
To foster further exploration of these nuances and encourage community-driven
insights, we have made our survey dataset publicly available. This data, which un-
derpins all quantitative results in this paper, is provided as a queryable DuckDB SQL
database. While an RDF representation of such survey data might be an ideal for di-
rect integration within the RDF ecosystems (a step that would involve an additional
mapping effort) we chose DuckDB for its immediate practicality. It offers an effi-
cient, integrated, in-memory environment for readily using the cleaned data, and no-
tably supports in-browser querying through W ASM, facilitating broad accessibility.
This approach streamlined our analysis, and we hope it empowers others; indeed, a
direct, DuckDB-like interactive querying experience tailored for RDF datasets could
be a valuable avenue for future tooling development within our field.
Building on the insights from our study, our work underscores several key direc-
tions for the community, encompassing researchers, tool developers, standards bod-
ies, and practitioners. There is a clear need to improve performance for large-scale
validation and to advance shape creation tooling, making it more sophisticated and
user-friendly. Extending the expressiveness of SHACL, for instance, by standardizing
support for recursive shapes and comprehensive validation of named graphs, remains a
demand. Furthermore, enhancing both documentation (perhaps with official primers)
and the utility of validation reporting is vital for wider adoption and effective use. Sup-
porting validation in evolving knowledge graphs also emerges as a critical area for
future research and development, focusing on strategies for the co-evolution of data
and constraints. Addressing these areas will be crucial for the continued growth and
effectiveness of RDF validation in ensuring data quality and the trustworthiness of
knowledge graphs
References
[1] AKSW. SHACLGEN.https://github.com/AKSW/shaclgen, 2025.
[2] Apache Software Foundation. Apache jena shacl, 2025.
[3] S ¨oren Auer, Christian Bizer, Georgi Kobilarov, Jens Lehmann, Richard Cyganiak,
and Zachary Ives. Dbpedia: a nucleus for a web of open data. InISWC, pages
722–735. Springer-Verlag, 2007.
[4] Thomas Bergwinkl. shacl-engine, 2025. Accessed: May 15, 2025.
14

## PDF page 15

[5] Iovka Boneva, J ´er´emie Dusart, Daniel Fern´andez Alvarez, and Jose Emilio Labra
Gayo. Shape designer for shex and shacl constraints. InISWC, 2019.
[6] Nicholas Car and Eliana Papoutsoglou. Data shapes working group charter. W3C
Working Group Charter, December 2024.
[7] Andrea Cimmino, Alba Fern ´andez-Izquierdo, and Ra ´ul Garc´ıa-Castro. Astrea:
Automatic generation of shacl shapes from ontologies. InThe Semantic Web,
pages 497–513. Springer International Publishing, 2020.
[8] Corese. Corese core, 2025. Accessed: May 15, 2025.
[9] DataTreeHouse. maplib, 2025. Accessed: May 15, 2025.
[10] Darren Edge, Ha Trinh, Newman Cheng, Joshua Bradley, Alex Chao, Apurva
Mody, Steven Truitt, and Jonathan Larson. From local to global: A graph RAG
approach to query-focused summarization.CoRR, abs/2404.16130, 2024.
[11] Daniel Fernandez- ´Alvarez, Jose Emilio Labra-Gayo, and Daniel Gayo-Avello.
Automatic extraction of shapes using shexer.Knowledge-Based Systems,
238:107975, 2022.
[12] M ´onica Figuera, Philipp D. Rohde, and Maria-Esther Vidal. Trav-shacl: Effi-
ciently validating networks of SHACL constraints. InWWW, pages 3337–3348.
ACM / IW3C2, 2021.
[13] Thomas Francart. SHACL Play!https://github.com/sparna-git/
shacl-play, 2025.
[14] Jos ´e Emilio Labra Gayo, Daniel Fern ´andez- ´Alvarez, and Herminio Garc ´ıa-
Gonz´alez. Rdfshape: An RDF playground based on shapes. InISWC Posters &
Demonstrations, volume 2180 ofCEUR Workshop Proceedings. CEUR-WS.org,
2018.
[15] Maxime Jakubowski and Jan Van den Bussche. Compiling SHACL into SQL.
InISWC (2), volume 15232 ofLecture Notes in Computer Science, pages 59–77.
Springer, 2024.
[16] Dimitris Kontokostas and Holger Knublauch. Shapes constraint
language (SHACL). W3C recommendation, W3C, July 2017.
https://www.w3.org/TR/2017/REC-shacl-20170720/.
[17] Jose Emilio Labra-Gayo. rudof, 2025. Accessed: May 15, 2025.
[18] Sven Lieber, Ben De Meester, Pieter Heyvaert, Femke Br ¨uckmann, Ruben
Wambacq, Erik Mannens, Ruben Verborgh, and Anastasia Dimou. Visual nota-
tions for viewing rdf constraints with unshacled.Semantic Web, 13(5):757–792,
2022.
15

## PDF page 16

[19] Sierra AT Moxon, Harold Solbrig, Deepak R Unni, Dazhi Jiao, Richard M
Bruskiewich, James P Balhoff, Gaurav Vaidya, William D Duncan, Harshad
Hegde, Mark Miller, et al. The linked data modeling language (linkml): A
general-purpose data modeling framework grounded in machine-readable seman-
tics.ICBO, 3073:148–151, 2021.
[20] Mark A. Musen. The prot ´eg´e project: a look back and a look forward.AI Matters,
1(4):4–12, June 2015.
[21] Natasha Noy, Yuqing Gao, Anshu Jain, Anant Narayanan, Alan Patterson, and
Jamie Taylor. Industry-scale knowledge graphs: lessons and challenges.CACM,
62(8):36–43, July 2019.
[22] Boci Peng, Yun Zhu, Yongchao Liu, Xiaohe Bo, Haizhou Shi, Chuntao Hong,
Yan Zhang, and Siliang Tang. Graph retrieval-augmented generation: A survey.
arXiv preprint arXiv:2408.08921, 2024.
[23] Felipe Pezoa, Juan L Reutter, Fernando Suarez, Mart ´ın Ugarte, and Domagoj
Vrgoˇc. Foundations of json schema. InThe Web Conference, pages 263–273,
2016.
[24] Axel Polleres, Romana Pernisch, Angela Bonifati, Daniele Dell’Aglio, Daniil
Dobriy, Stefania Dumbrava, Lorena Etcheverry, Nicolas Ferranti, Katja Hose,
Ernesto Jim´enez-Ruiz, Matteo Lissandrini, Ansgar Scherp, Riccardo Tommasini,
and Johannes Wachs. How does knowledge evolve in open knowledge graphs?
TGDK, 1(1):11:1–11:59, 2023.
[25] Eric Prud’hommeaux, Iovka Boneva, Jose Emilio Labra Gayo, and Gregg Kel-
logg. Shape expressions language 2.1. Final community group report, W3C,
October 2019.
[26] Kashif Rabbani, Matteo Lissandrini, and Katja Hose. Shacl and shex in the wild:
a community survey on validating shapes generation and adoption. InCompanion
Proceedings of the Web Conference 2022, pages 260–263, 2022.
[27] Kashif Rabbani, Matteo Lissandrini, and Katja Hose. Extraction of validating
shapes from very large knowledge graphs.Proc. VLDB Endow., 16(5):1023–
1032, 2023.
[28] RDF 1.1 concepts and abstract syntax. W3C Recommendation, February 2014.
[29] Ashley Sommer and Nicholas Car. pySHACL, March 2025.
[30] Blerina Spahiu, Andrea Maurino, and Matteo Palmonari. Towards improving the
quality of knowledge graphs with data-driven ontology patterns and shacl. In
Emerging Topics in Semantic Technologies, pages 103–117. IOS Press, 2018.
[31] Stardog. Stardog enterprise knowledge graph platform, 2025. Accessed: May 15,
2025.
16

## PDF page 17

[32] Fabian M Suchanek, Mehwish Alam, Thomas Bonald, Lihu Chen, Pierre-Henri
Paris, and Jules Soria. Yago 4.5: A large and clean knowledge base with a rich
taxonomy. InACM SIGIR, pages 131–140, 2024.
[33] The Eclipse Foundation. Eclipse RDF4J, 2025. Accessed: May 15, 2025.
[34] TopQuadrant. shacl-js. Accessed: May 15, 2025.
[35] TopQuadrant. TopBraid EDG, 2025. Accessed: May 15, 2025.
[36] Denny Vrande ˇci´c and Markus Kr ¨otzsch. Wikidata: a free collaborative knowl-
edgebase.Communications of the ACM, 57(10):78–85, 2014.
[37] Zazuko. rdf-validate-shacl, 2025. Accessed: May 15, 2025.
[38] Qinggang Zhang, Shengyuan Chen, Yuanchen Bei, Zheng Yuan, Huachi Zhou,
Zijin Hong, Junnan Dong, Hao Chen, Yi Chang, and Xiao Huang. A survey
of graph retrieval-augmented generation for customized large language models.
arXiv preprint arXiv:2501.13958, 2025.
17
