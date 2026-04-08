BigQuery release notes | Google Cloud Documentation
Skip to main content
Technology areas
close
AI and ML
Application development
Application hosting
Compute
Data analytics and pipelines
Databases
Distributed, hybrid, and multicloud
Industry solutions
Migration
Networking
Observability and monitoring
Security
Storage
Cross-product tools
close
Access and resources management
Costs and usage management
Infrastructure as code
SDK, languages, frameworks, and tools
/
Console
English
Deutsch
Español – América Latina
Français
Português – Brasil
中文 – 简体
日本語
한국어
BigQuery
Start free
Overview
Guides
Reference
Samples
Resources
Technology areas
More
Overview
Guides
Reference
Samples
Resources
Cross-product tools
More
Console
BigQuery
Release notes
Release notes archive
Locations
Error messages
Get support
Billing
Pricing
Committed use discounts
Billing questions
Pre-built datasets
Commercial datasets
Public datasets
Google Cloud Ready - BigQuery
Overview
Validated partner solutions
White papers
Multi-tenant workloads
Continuous data integration
Service level agreement
AI and ML
Application development
Application hosting
Compute
Data analytics and pipelines
Databases
Distributed, hybrid, and multicloud
Industry solutions
Migration
Networking
Observability and monitoring
Security
Storage
Access and resources management
Costs and usage management
Infrastructure as code
SDK, languages, frameworks, and tools
Home
Documentation
Data analytics
BigQuery
Resources
Send feedback
BigQuery release notes
Stay organized with collections
Save and categorize content based on your preferences.
This page documents production updates to BigQuery. We recommend
that BigQuery developers periodically check this list for any
new announcements. BigQuery automatically updates to the latest
release and cannot be downgraded to a previous version.
For older release notes, see the
Release notes archive .
You can see the latest product updates for all of Google Cloud on the
Google Cloud page, browse and filter all release notes in the
Google Cloud console ,
or programmatically access release notes in
BigQuery .
To get the latest product updates delivered to you, add the URL of this page to your
feed
reader , or add the
feed URL directly.
April 06, 2026
Feature
You can now use the
AI.AGG function
to semantically aggregate unstructured input data based on natural language
instructions. This feature is in
Preview .
Feature
You can now use a custom organization policy
to allow or deny specific operations on these BigQuery resources:
tables, data policies, and row access policies. This feature is in preview .
April 02, 2026
Feature
You can now use the
CREATE CONNECTION ,
ALTER CONNECTION SET OPTIONS ,
and DROP CONNECTION
data definition language (DDL) statements to manage Cloud resource connections
with GoogleSQL. Additionally, you can now use the
connection user type
and PROJECT resource type
with GRANT and REVOKE data control language (DCL) statements to manage
connection and project access. These features are
generally available
(GA).
Feature
The BigQuery Migration Service supports SQL translations from Snowflake
SQL to GoogleSQL .
This feature is now generally available (GA).
With this change, the translation service supports a wider variety of
Snowflake SQL and has improved support for several data types.
Among other changes, the translation service maps Snowflake
INTEGER and zero-scale NUMERIC types up to precision 38 to INT64 type in
GoogleSQL for improved performance by default.
Feature
You can set the
column granularity when you
create a search index ,
which stores additional column information in your search index to further
optimize your search query performance. This feature is
generally available
(GA).
March 31, 2026
Feature
BigQuery ObjectRef values
now support the following:
You can run ObjectRef functions
with either
direct access or delegated access .
The
OBJ.MAKE_REF function
automatically fetches the latest Cloud Storage metadata and populates this in
the ref.details field.
The
OBJ.GET_READ_URL function
returns a STRUCT value with a read URL and status columns and renders image
results in the Cloud console. Use this function when you don't require a
write URL.
These features are
generally available
(GA).
March 30, 2026
Feature
The following forecasting and anomaly detection functions and updates are
generally available
(GA):
The
AI.DETECT_ANOMALIES function
supports providing a custom context window that determines how many of the
most recent data points should be used by the model.
The
AI.FORECAST function
supports specifying the latest timestamp value for forecasting.
The
AI.EVALUATE function
supports the following:
You can provide a custom context window that determines how many of the most
recent data points should be used by the model.
The function outputs the
mean absolute scaled error
for the time series.
Feature
You can now create BigQuery non-incremental materialized views over Spanner data
to improve query performance by periodically caching results. This feature is
generally available (GA).
March 26, 2026
Feature
You can now use
Cloud resource connections with EXPORT DATA statements
to reverse ETL BigQuery data to Spanner. This
feature is
generally available (GA).
March 25, 2026
Announcement
The Gemini for Google Cloud API
(cloudaicompanion.googleapis.com) is now enabled for existing
BigQuery projects in the European jurisdiction.
Feature
You can now use the BigQuery Migration Service MCP server
to perform SQL translation tasks, including translating SQL queries into
GoogleSQL syntax, generating DDL statements from SQL input queries, and getting
explanations of SQL translations.
This feature is in
preview .
Feature
In BigQuery Data Transfer Service, you can
monitor resource-level status reporting for Hive managed tables
to track progress and view granular error details for individual tables.
This feature is in
preview .
Feature
You can use the BigQuery migration assessment for
Snowflake to assess the complexity of
migrating from Snowflake to BigQuery. This feature is
generally available
(GA).
March 24, 2026
Feature
You can now use the BigQuery Data Transfer Service remote MCP
server to enable AI agents to
create, manage, and run data transfers. This feature is in
Preview .
March 23, 2026
Feature
The following functions are now
generally available
(GA):
AI.EMBED :
create embeddings from text or image data.
AI.SIMILARITY :
compute the semantic similarity between pairs of text, pairs of images, or
across text and images.
Feature
You can clean, transform, and enrich data from files in Cloud Storage and Google
Drive in your BigQuery data preparations. For more information, see
Prepare data with Gemini .
This feature is generally available
(GA).
March 19, 2026
Feature
You can now use a custom organization policy
to allow or deny specific operations on routines. This feature is in
preview .
March 17, 2026
Feature
In BigQuery ML, you can now
automatically deploy
open models to Vertex AI endpoints. Automatically deployed models offer the
following benefits:
Automatic Vertex AI resource management
Reserve open model resources by
using Compute Engine reservations
Automatic or immediate open model undeployment
to save costs
This feature is generally available
(GA).
March 16, 2026
Feature
BigQuery now lets you configure a global default location .
This setting is used if the location isn't set or can't be inferred from the
request. You can set the default location at the organization or project level.
This feature is generally available
(GA).
March 12, 2026
Change
BigQuery advanced runtime is now enabled as
the default runtime for all projects.
March 11, 2026
Feature
You can now understand and debug BigQuery query performance with
a
visual mapping of your SQL query in the query execution graph .
A heatmap highlights the steps that consume more slot-time. This feature is
generally available
(GA).
March 09, 2026
Feature
Updates to conversational analytics include the following improvements:
ObjectRef support: BigQuery conversational analytics now
integrates with Google Cloud Storage through ObjectRef functions .
This lets you reference and interact with unstructured data such as images and
PDFs in Cloud Storage buckets in your conversational analysis.
BQML support: BigQuery conversational analytics now supports a set of BigQuery ML functions ,
including AI.FORECAST, AI.DETECT_ANOMALIES, and AI.GENERATE. These functions
let you perform advanced analytics tasks with simple conversational prompts.
Chat with BigQuery results: You can now start conversations and chat with
query results in BigQuery Studio (SQL editor).
Enhanced support for partitioned tables: BigQuery conversational analytics can
now use BigQuery table partitioning. The agent can optimize SQL queries by
using partitioned columns such as date ranges on a date-partitioned table.
This can improve query performance and reduce costs.
Labels for agent-generated queries: BigQuery jobs initiated by the
conversational analytics agent are now labeled in BigQuery Job History
in the Google Cloud Console. You can identify, filter, and analyze the jobs
run by the conversational analytics agent by referencing labels similar to
{'ca-bq-job': 'true'} . These labels can help with the following tasks:
Monitor and attribute cost.
Audit agent activity.
Analyze agent-generated query performance.
Suggest next questions (clickable): When working with BigQuery
conversational analytics, the agent now suggests questions that are directly
clickable in the Google Cloud console.
This feature is available in Preview .
March 06, 2026
Feature
You can create a remote model
based on the Vertex AI gemini-embedding-001 model, or a
remote model
based on an open embedding model from Vertex Model Garden or Hugging Face that
is deployed to Vertex AI.
You can then use the
AI.GENERATE_EMBEDDING function
with these remote models to generate embeddings. You can also use the
AI.EMBED function
directly with the gemini-embedding-001 model endpoint.
These features are
generally available
(GA).
Feature
You can now use the Pipelines & Connections page
to streamline your data integration tasks by using guided,
BigQuery-specific configuration workflows for services like
BigQuery Data Transfer Service, Datastream, and Pub/Sub.
This feature is in Preview .
March 05, 2026
Change
An updated version of the
Simba ODBC driver for BigQuery
is now available.
Feature
You can now use an alternate syntax when you call the
VECTOR_SEARCH function
to improve query performance when you search for a single vector. This feature
is in Preview .
March 04, 2026
Feature
Monitor dataset replication latency and network egress bytes in Cloud Monitoring
for BigQuery cross-region replication
and managed disaster recovery .
These metrics are generally available
(GA).
Feature
You can now use continuous queries to stream BigQuery data to Spanner in real
time . This feature is
generally available
(GA).
February 25, 2026
Change
Effective June 1, 2026 , BigQuery will limit legacy SQL use. This depends on
whether your organization or project uses it from November 1, 2025, to June 1,
2026. If you don't use legacy SQL during this time, you won't be able to use it
after June 1, 2026. If you do use it, your existing workloads
will keep running, but new ones might not. For more information, see
Legacy SQL feature availability .
February 24, 2026
Feature
You can now create and review
custom glossary terms in BigQuery for a conversational
analytics agent and you can review business glossary terms imported from
Dataplex Universal Catalog for an agent. These terms help an agent interpret your
prompts.
This feature is now in Preview .
February 23, 2026
Feature
You can now undelete a dataset that
is within your time travel window to recover it to the state that it was in when
it was deleted. This feature is generally
available (GA).
February 17, 2026
Feature
You can now run global queries , which let you
reference data stored in more than one region in a single query. This feature is
in Preview .
Change
After March 17, 2026, when you enable BigQuery, the BigQuery MCP server is
automatically enabled.
Deprecated
Control of MCP use with organization policies is deprecated. After
March 17, 2026, organization policies that use the
gcp.managed.allowedMCPServices constraint won't work, and you can control
MCP use with IAM deny policies. For more information about controlling MCP use,
see Control MCP use with IAM deny policies .
February 12, 2026
Feature
The
AI.CLASSIFY function
now supports classifying your input into multiple categories. This feature is in
Preview .
Feature
You can now provide descriptions for the fields in your custom output schema
when you use the
AI.GENERATE
and
AI.GENERATE_TABLE
functions.
This feature is generally available
(GA).
Feature
You can now use dataset insights
to understand relationships between tables in a dataset by generating
relationship graphs and cross-table queries. You can automatically generate
dataset summaries, infer relationships across tables, and receive suggestions
for analytical questions. This feature is in
Preview .
February 11, 2026
Feature
You can now run pipelines with three distinct execution methods: running all
tasks, running selected tasks, and running tasks with selected tags. For more
information, see
Run a pipeline .
This feature is generally available
(GA).
February 09, 2026
Feature
You can now customize the scope of data documentation scans for BigQuery tables
to generate specific insights. You can choose to generate only SQL queries,
only table and column descriptions, or all insights.
You can also create one-time data scans that execute immediately upon creation,
removing the need for a separate run command. These scans support a
Time to Live (TTL) setting to automatically delete the scan resource after
completion.
For more information, see
Generate insights for a BigQuery table .
February 04, 2026
Change
Data transfers from the YouTube Channel
and YouTube Content Owner
data sources now support reach reports. For more information, see
YouTube Channel report transformation
and YouTube Content Owner report transformation .
Feature
You can now associate data policies directly on
columns . This
feature enables direct database administration for controlling access and
applying masking and transformation rules at the column level. This feature is
now generally
available (GA).
February 03, 2026
Announcement
Gemini in BigQuery now processes data in the same jurisdiction ( US or EU ) as
your BigQuery datasets, or based upon user-specified location settings. For more
information, see Where Gemini BigQuery processes your
data .
February 02, 2026
Feature
You can now pass parameterized queries
from the BigQuery query editor in the Google Cloud console.
This feature is generally available
(GA).
January 29, 2026
Feature
BigQuery now supports a RANDOM_HASH predefined masking rule. This rule returns
a hash of the column's value using a salted hash algorithm, and it provides
stronger security than the standard Hash (SHA-256) rule.
For more information, see Data masking rules .
Feature
BigQuery now offers conversational analytics ,
which accelerates data analysis by enabling insights through natural language.
Users can view a predefined sample agent, chat with their BigQuery data or
custom agents, and access those agents even outside of BigQuery. They can also
use supported BigQuery ML functions
in verified queries and in chat. This feature is in
Preview .
Feature
You can now create BigQuery ML models by using the
Google Cloud console .
This feature is generally available
(GA).
January 28, 2026
Change
The BigQuery change data capture feature has been renamed to
BigQuery change data capture ingestion .
Feature
The BigQuery Data Transfer Service can now
transfer data from Shopify to BigQuery .
This feature is in Preview .
January 27, 2026
Change
An updated version of the
Simba JDBC driver for BigQuery
is now available.
Feature
The BigQuery Data Transfer Service can now
transfer data from Mailchimp to BigQuery .
This feature is in Preview .
January 26, 2026
Feature
You can now use Gemini Cloud Assist to
discover resources
across your projects. For example, you can ask about a specific table's schema,
or which tables contain demographic information about new users. This feature is
in Preview .
January 23, 2026
Change
You can now optionally specify which model to use by passing an endpoint
argument to the
AI.IF ,
AI.SCORE ,
and
AI.CLASSIFY
functions.
January 22, 2026
Fixed
Support for
table parameters in table-valued functions
is restored.
Change
You can now run queries that use the
AI.IF ,
AI.SCORE ,
and
AI.CLASSIFY
functions by using your
end-user credentials instead of a
BigQuery connection.
January 21, 2026
Change
BigQuery is now available in the Bangkok ( asia-southeast3 ) region .
Feature
You can now use Gemini Cloud Assist to
get information about your job history ,
such as why a particular query was slow or which queries were the most
resource-intensive in the past day. This feature is in
Preview .
January 19, 2026
Breaking
Dataform workflows ,
BigQuery notebooks ,
pipelines ,
and
data preparations
are enforcing strict act-as mode at the project level. To avoid failures and
maintain automatic releases, you must use custom service accounts instead of the
default Dataform service agent across all repositories. You must also grant the
Service Account User role ( roles/iam.serviceAccountUser ) to the default
Dataform service agent and relevant principals. For more information and to
verify act-as permissions, see
Use strict act-as mode .
January 07, 2026
Feature
You can now use the Google-developed, open source
Java Database Connectivity (JDBC) driver for BigQuery
to connect your Java applications to BigQuery. This feature is in
Preview .
January 06, 2026
Feature
The CREATE EXTERNAL TABLE
and LOAD DATA
statements now support the following options:
time_zone : specify a time zone to use when loading data
date_format , datetime_format , time_format , and timestamp_format : define how date and time values are formatted in your source files
null_markers : define the strings that represent NULL values in CSV files.
source_column_match : specify how loaded columns are matched to the schema. You can match columns by position or by name.
These features are generally
available (GA).
December 22, 2025
Feature
The BigQuery Data Transfer Service can now transfer data from PostgreSQL to
BigQuery . This feature is generally
available (GA).
Libraries
Java
2.58.0-rc1 (2025-12-17)
Features
Add ability to specify RetryOptions and BigQueryRetryConfig when create job and waitFor ( #3398 ) ( 1f91ae7 )
add additional parameters to CsvOptions and ParquetOptions ( #3370 ) ( 34f16fb )
add columnNameCharacterMap to LoadJobConfiguration ( #3356 ) ( 2f3cbe3 )
add max staleness to ExternalTableDefinition ( #3499 ) ( f1ebd5b )
add MetadataCacheMode to ExternalTableDefinition ( #3351 ) ( 2814dc4 )
add remaining Statement Types ( #3381 ) ( 5f39b19 )
add WRITE_TRUNCATE_DATA as an enum value for write disposition ( #3752 ) ( acea61c )
bigquery: Add custom ExceptionHandler to BigQueryOptions ( #3937 ) ( de0914d )
bigquery: Add OpenTelemetry Samples ( #3899 ) ( e3d9ed9 )
bigquery: Add OpenTelemetry support to BQ rpcs ( #3860 ) ( e2d23c1 )
bigquery: Add otel metrics to request headers ( #3900 ) ( 4071e4c )
bigquery: Add support for custom timezones and timestamps ( #3859 ) ( e5467c9 )
bigquery: Add support for reservation field in jobs. ( #3768 ) ( 3e97f7c )
bigquery: Implement getArray in BigQueryResultImpl ( #3693 ) ( e2a3f2c )
bigquery: Integrate Otel in client lib ( #3747 ) ( 6e3e07a )
bigquery: Integrate Otel into retries, jobs, and more ( #3842 ) ( 4b28c47 )
bigquery: job creation mode GA ( #3804 ) ( a21cde8 )
bigquery: Support Fine Grained ACLs for Datasets ( #3803 ) ( bebf1c6 )
bigquery: support IAM conditions in datasets in Java client. ( #3602 ) ( 6696a9c )
bigquery: Support resource tags for datasets in java client ( #3647 ) ( 01e0b74 )
configure rc releases to be on prerelease mode ( 93700c8 )
Enable Lossless Timestamps in BQ java client lib ( #3589 ) ( c0b874a )
Enable maxTimeTravelHours in BigQuery java client library ( #3555 ) ( bd24fd8 )
implement wasNull for BigQueryResultSet ( #3650 ) ( c7ef94b )
introduce java.time methods and variables ( #3586 ) ( 31fb15f )
new queryWithTimeout method for customer-side wait ( #3995 ) ( 9c0df54 )
next release from main branch is 2.49.0 ( #3706 ) ( b46a6cc )
next release from main branch is 2.53.0 ( #3879 ) ( c47a062 )
Relax client-side validation for BigQuery entity IDs ( #4000 ) ( c3548a2 )
update with latest from main ( #4034 ) ( ec447b5 )
Bug Fixes
adapt graalvm config to arrow update ( #3928 ) ( ecfabc4 )
add clustering value to ListTables result ( #3359 ) ( 5d52bc9 )
Add labels to converter for listTables method ( #3735 ) ( #3736 ) ( 8634822 )
bigquery: Add MY_VIEW_DATASET_NAME TEST to resource clean up sample ( #3838 ) ( b1962a7 )
bigquery: Remove ReadAPI bypass in executeSelect() ( #3624 ) ( fadd992 )
Close bq read client ( #3644 ) ( 8833c97 )
executeSelect now use provided credentials instead of GOOGLE_APP… ( #3465 ) ( cd82235 )
load jobs preserve ascii control characters configuration ( #3876 ) ( 5cfdf85 )
next release candidate ( d01971e )
NPE for executeSelect nonFast path with empty result ( #3445 ) ( d0d758a )
NPE when reading BigQueryResultSet from empty tables ( #3627 ) ( 9a0b05a )
null field mode inconsistency ( #2863 ) ( b9e96e3 )
retry ExceptionHandler not retrying on IOException ( #3668 ) ( 83245b9 )
test: Force usage of ReadAPI ( #3625 ) ( 5ca7d4a )
test: Update schema for broken ConnImplBenchmark test ( #3574 ) ( 8cf4387 )
Update experimental methods documentation to @internalapi ( #3552 ) ( 20826f1 )
Dependencies
exclude io.netty:netty-common from org.apache.arrow:arrow-memor… ( #3715 ) ( 11b5809 )
fix update dependency com.google.cloud:google-cloud-bigquerystorage-bom to v3.17.2 ( b25095d )
remove version declaration of open-telemetry-bom ( #3855 ) ( 6f9f77d )
rollback netty.version to v4.1.119.Final ( #3827 ) ( 94c71a0 )
update actions/checkout action to v4.1.6 ( #3309 ) ( c7d6362 )
update actions/checkout action to v4.1.7 ( #3349 ) ( 0857234 )
update actions/checkout action to v4.2.0 ( #3495 ) ( b57fefb )
update actions/checkout action to v4.2.1 ( #3520 ) ( ad8175a )
update actions/checkout action to v4.2.2 ( #3541 ) ( c36c123 )
update actions/upload-artifact action to v4.3.4 ( #3382 ) ( efa1aef )
update actions/upload-artifact action to v4.3.5 ( #3420 ) ( d5ec87d )
update actions/upload-artifact action to v4.3.5 ( #3422 ) ( c7d07b3 )
update actions/upload-artifact action to v4.3.5 ( #3424 ) ( a9d6869 )
update actions/upload-artifact action to v4.3.5 ( #3427 ) ( 022eb57 )
update actions/upload-artifact action to v4.3.5 ( #3430 ) ( c7aacba )
update actions/upload-artifact action to v4.3.5 ( #3432 ) ( b7e8244 )
update actions/upload-artifact action to v4.3.5 ( #3436 ) ( ccefd6e )
update actions/upload-artifact action to v4.3.5 ( #3440 ) ( 916fe9a )
update actions/upload-artifact action to v4.3.5 ( #3443 ) ( 187f099 )
update actions/upload-artifact action to v4.3.5 ( #3444 ) ( 04aea5e )
update actions/upload-artifact action to v4.3.5 ( #3449 ) ( c6e93cd )
update actions/upload-artifact action to v4.3.5 ( #3455 ) ( fbfc106 )
update actions/upload-artifact action to v4.3.5 ( #3456 ) ( f00977c )
update actions/upload-artifact action to v4.3.5 ( #3462 ) ( e1c6e92 )
update actions/upload-artifact action to v4.3.6 ( #3463 ) ( ba91227 )
update actions/upload-artifact action to v4.4.0 ( #3467 ) ( 08b28c5 )
update actions/upload-artifact action to v4.4.1 ( #3521 ) ( dc21975 )
update actions/upload-artifact action to v4.4.2 ( #3524 ) ( 776a554 )
update actions/upload-artifact action to v4.4.3 ( #3530 ) ( 2f87fd9 )
update actions/upload-artifact action to v4.5.0 ( #3620 ) ( cc25099 )
update actions/upload-artifact action to v4.6.0 ( #3633 ) ( ca20aa4 )
update actions/upload-artifact action to v4.6.1 ( #3691 ) ( 9c0edea )
update actions/upload-artifact action to v4.6.2 ( #3724 ) ( 426a59b )
update actions/upload-artifact action to v4.6.2 ( #3724 ) ( 483f930 )
update bigquerystorage-bom to 3.20.0-rc1 ( #4035 ) ( cb44b5f )
update dependency com.google.api.grpc:proto-google-cloud-bigqueryconnection-v1 to v2.46.0 ( #3328 ) ( a6661ad )
update dependency com.google.api.grpc:proto-google-cloud-bigqueryconnection-v1 to v2.47.0 ( #3342 ) ( 79e34c2 )
update dependency com.google.api.grpc:proto-google-cloud-bigqueryconnection-v1 to v2.48.0 ( #3374 ) ( 45b7f20 )
update dependency com.google.api.grpc:proto-google-cloud-bigqueryconnection-v1 to v2.49.0 ( #3417 ) ( 66336a8 )
update dependency com.google.api.grpc:proto-google-cloud-bigqueryconnection-v1 to v2.50.0 ( #3448 ) ( 2c12839 )
update dependency com.google.api.grpc:proto-google-cloud-bigqueryconnection-v1 to v2.51.0 ( #3480 ) ( 986b036 )
update dependency com.google.api.grpc:proto-google-cloud-bigqueryconnection-v1 to v2.53.0 ( #3504 ) ( 57ce901 )
update dependency com.google.api.grpc:proto-google-cloud-bigqueryconnection-v1 to v2.54.0 ( #3532 ) ( 25be311 )
update dependency com.google.api.grpc:proto-google-cloud-bigqueryconnection-v1 to v2.55.0 ( #3559 ) ( 950ad0c )
update dependency com.google.api.grpc:proto-google-cloud-bigqueryconnection-v1 to v2.56.0 ( #3582 ) ( 616ee2a )
update dependency com.google.api.grpc:proto-google-cloud-bigqueryconnection-v1 to v2.57.0 ( #3617 ) ( 51370a9 )
update dependency com.google.api.grpc:proto-google-cloud-bigqueryconnection-v1 to v2.58.0 ( #3631 ) ( b0ea0d5 )
update dependency com.google.api.grpc:proto-google-cloud-bigqueryconnection-v1 to v2.59.0 ( #3660 ) ( 3a6228b )
update dependency com.google.api.grpc:proto-google-cloud-bigqueryconnection-v1 to v2.60.0 ( #3680 ) ( 6d9a40d )
update dependency com.google.api.grpc:proto-google-cloud-bigqueryconnection-v1 to v2.61.0 ( #3703 ) ( 53b07b0 )
update dependency com.google.api.grpc:proto-google-cloud-bigqueryconnection-v1 to v2.62.0 ( #3726 ) ( 38e004b )
update dependency com.google.api.grpc:proto-google-cloud-bigqueryconnection-v1 to v2.63.0 ( #3770 ) ( 934389e )
update dependency com.google.api.grpc:proto-google-cloud-bigqueryconnection-v1 to v2.65.0 ( #3787 ) ( 0574ecc )
update dependency com.google.api.grpc:proto-google-cloud-bigqueryconnection-v1 to v2.66.0 ( #3835 ) ( 69be5e7 )
update dependency com.google.api.grpc:proto-google-cloud-bigqueryconnection-v1 to v2.68.0 ( #3858 ) ( d4ca353 )
update dependency com.google.api.grpc:proto-google-cloud-bigqueryconnection-v1 to v2.69.0 ( #3870 ) ( a7f1007 )
update dependency com.google.api.grpc:proto-google-cloud-bigqueryconnection-v1 to v2.70.0 ( #3890 ) ( 84207e2 )
update dependency com.google.apis:google-api-services-bigquery to v2-rev20240602-2.0.0 ( #3273 ) ( 7b7e52b )
update dependency com.google.apis:google-api-services-bigquery to v2-rev20240616-2.0.0 ( #3368 ) ( ceb270c )
update dependency com.google.apis:google-api-services-bigquery to v2-rev20240623-2.0.0 ( #3384 ) ( e1de34f )
update dependency com.google.apis:google-api-services-bigquery to v2-rev20240629-2.0.0 ( #3392 ) ( 352562d )
update dependency com.google.apis:google-api-services-bigquery to v2-rev20240714-2.0.0 ( #3412 ) ( 8a48fd1 )
update dependency com.google.apis:google-api-services-bigquery to v2-rev20240727-2.0.0 ( #3421 ) ( 91d780b )
update dependency com.google.apis:google-api-services-bigquery to v2-rev20240727-2.0.0 ( #3423 ) ( 16f350c )
update dependency com.google.apis:google-api-services-bigquery to v2-rev20240727-2.0.0 ( #3428 ) ( 9ae6eca )
update dependency com.google.apis:google-api-services-bigquery to v2-rev20240803-2.0.0 ( #3435 ) ( b4e20db )
update dependency com.google.apis:google-api-services-bigquery to v2-rev20240815-2.0.0 ( #3454 ) ( 8796aee )
update dependency com.google.apis:google-api-services-bigquery to v2-rev20240905-2.0.0 ( #3483 ) ( a6508a2 )
update dependency com.google.apis:google-api-services-bigquery to v2-rev20240919-2.0.0 ( #3514 ) ( 9fe3829 )
update dependency com.google.apis:google-api-services-bigquery to v2-rev20241013-2.0.0 ( #3544 ) ( 0c42092 )
update dependency com.google.apis:google-api-services-bigquery to v2-rev20241027-2.0.0 ( #3568 ) ( b5ccfcc )
update dependency com.google.apis:google-api-services-bigquery to v2-rev20241111-2.0.0 ( #3591 ) ( 3eef3a9 )
update dependency com.google.apis:google-api-services-bigquery to v2-rev20241115-2.0.0 ( #3601 ) ( 41f9adb )
update dependency com.google.apis:google-api-services-bigquery to v2-rev20241222-2.0.0 ( #3623 ) ( 4061922 )
update dependency com.google.apis:google-api-services-bigquery to v2-rev20250112-2.0.0 ( #3651 ) ( fd06100 )
update dependency com.google.apis:google-api-services-bigquery to v2-rev20250128-2.0.0 ( #3667 ) ( 0b92af6 )
update dependency com.google.apis:google-api-services-bigquery to v2-rev20250216-2.0.0 ( #3688 ) ( e3beb6f )
update dependency com.google.apis:google-api-services-bigquery to v2-rev20250302-2.0.0 ( #3720 ) ( c0b3902 )
update dependency com.google.apis:google-api-services-bigquery to v2-rev20250313-2.0.0 ( #3723 ) ( b8875a8 )
update dependency com.google.apis:google-api-services-bigquery to v2-rev20250404-2.0.0 ( #3754 ) ( 1381c8f )
update dependency com.google.apis:google-api-services-bigquery to v2-rev20250427-2.0.0 ( #3773 ) ( c0795fe )
update dependency com.google.apis:google-api-services-bigquery to v2-rev20250511-2.0.0 ( #3794 ) ( d3bf724 )
update dependency com.google.apis:google-api-services-bigquery to v2-rev20250615-2.0.0 ( #3872 ) ( f081589 )
update dependency com.google.apis:google-api-services-bigquery to v2-rev20250706-2.0.0 ( #3910 ) ( ae5c971 )
update dependency com.google.apis:google-api-services-bigquery to v2-rev20251012-2.0.0 ( #3923 ) ( 1d8977d )
update dependency com.google.cloud:google-cloud-bigquerystorage-bom to v3.10.0 ( 0bd3c86 )
update dependency com.google.cloud:google-cloud-bigquerystorage-bom to v3.10.1 ( c03a63a )
update dependency com.google.cloud:google-cloud-bigquerystorage-bom to v3.10.2 ( 19fc184 )
update dependency com.google.cloud:google-cloud-bigquerystorage-bom to v3.17.0 ( #3954 ) ( e73deed )
update dependency com.google.cloud:google-cloud-bigquerystorage-bom to v3.9.0 ( c4afbef )
update dependency com.google.cloud:google-cloud-datacatalog-bom to v1.50.0 ( #3330 ) ( cabb0ab )
update dependency com.google.cloud:google-cloud-datacatalog-bom to v1.51.0 ( #3343 ) ( e3b934f )
update dependency com.google.cloud:google-cloud-datacatalog-bom to v1.52.0 ( #3375 ) ( 2115c04 )
update dependency com.google.cloud:google-cloud-datacatalog-bom to v1.53.0 ( #3418 ) ( 6cff7f0 )
update dependency com.google.cloud:google-cloud-datacatalog-bom to v1.54.0 ( #3450 ) ( cc9da95 )
update dependency com.google.cloud:google-cloud-datacatalog-bom to v1.55.0 ( #3481 ) ( 8908cfd )
update dependency com.google.cloud:google-cloud-datacatalog-bom to v1.57.0 ( #3505 ) ( 6e78f56 )
update dependency com.google.cloud:google-cloud-datacatalog-bom to v1.58.0 ( #3533 ) ( cad2643 )
update dependency com.google.cloud:google-cloud-datacatalog-bom to v1.59.0 ( #3561 ) ( 1bd24a1 )
update dependency com.google.cloud:google-cloud-datacatalog-bom to v1.60.0 ( #3583 ) ( 34dd8bc )
update dependency com.google.cloud:google-cloud-datacatalog-bom to v1.61.0 ( #3618 ) ( 6cba626 )
update dependency com.google.cloud:google-cloud-datacatalog-bom to v1.62.0 ( #3632 ) ( e9ff265 )
update dependency com.google.cloud:google-cloud-datacatalog-bom to v1.63.0 ( #3661 ) ( 9bc8c01 )
update dependency com.google.cloud:google-cloud-datacatalog-bom to v1.64.0 ( #3681 ) ( 9e4e261 )
update dependency com.google.cloud:google-cloud-datacatalog-bom to v1.65.0 ( #3704 ) ( 53b68b1 )
update dependency com.google.cloud:google-cloud-datacatalog-bom to v1.66.0 ( #3727 ) ( 7339f94 )
update dependency com.google.cloud:sdk-platform-java-config to v3.31.0 ( #3335 ) ( 0623455 )
update dependency com.google.cloud:sdk-platform-java-config to v3.32.0 ( #3360 ) ( 4420996 )
update dependency com.google.cloud:sdk-platform-java-config to v3.33.0 ( #3405 ) ( a4a9999 )
update dependency com.google.cloud:sdk-platform-java-config to v3.34.0 ( #3433 ) ( 801f441 )
update dependency com.google.cloud:sdk-platform-java-config to v3.35.0 ( #3472 ) ( fa9ac5d )
update dependency com.google.cloud:sdk-platform-java-config to v3.36.0 ( #3490 ) ( a72c582 )
update dependency com.google.cloud:sdk-platform-java-config to v3.36.1 ( #3496 ) ( 8f2e5c5 )
update dependency com.google.cloud:sdk-platform-java-config to v3.37.0 ( bf4d37a )
update dependency com.google.cloud:sdk-platform-java-config to v3.38.0 ( #3542 ) ( 16448ee )
update dependency com.google.cloud:sdk-platform-java-config to v3.39.0 ( #3548 ) ( 616b2f6 )
update dependency com.google.cloud:sdk-platform-java-config to v3.40.0 ( #3576 ) ( d5fa951 )
update dependency com.google.cloud:sdk-platform-java-config to v3.41.0 ( #3607 ) ( 11499d1 )
update dependency com.google.cloud:sdk-platform-java-config to v3.41.1 ( #3628 ) ( 442d217 )
update dependency com.google.cloud:sdk-platform-java-config to v3.42.0 ( #3653 ) ( 1a14342 )
update dependency com.google.cloud:sdk-platform-java-config to v3.43.0 ( #3669 ) ( 4d9e0ff )
update dependency com.google.cloud:sdk-platform-java-config to v3.44.0 ( #3694 ) ( f69fbd3 )
update dependency com.google.cloud:sdk-platform-java-config to v3.45.1 ( #3714 ) ( e4512aa )
update dependency com.google.cloud:sdk-platform-java-config to v3.46.0 ( #3753 ) ( a335927 )
update dependency com.google.cloud:sdk-platform-java-config to v3.46.2 ( #3756 ) ( 907e39f )
update dependency com.google.cloud:sdk-platform-java-config to v3.46.3 ( #3772 ) ( ab166b6 )
update dependency com.google.cloud:sdk-platform-java-config to v3.47.0 ( #3779 ) ( b27434b )
update dependency com.google.cloud:sdk-platform-java-config to v3.48.0 ( #3790 ) ( 206f06d )
update dependency com.google.cloud:sdk-platform-java-config to v3.49.0 ( #3811 ) ( 2c5ede4 )
update dependency com.google.cloud:sdk-platform-java-config to v3.49.2 ( #3853 ) ( cf864df )
update dependency com.google.cloud:sdk-platform-java-config to v3.50.0 ( #3861 ) ( eb26dee )
update dependency com.google.cloud:sdk-platform-java-config to v3.50.1 ( #3878 ) ( 0e971b8 )
update dependency com.google.cloud:sdk-platform-java-config to v3.50.2 ( #3901 ) ( 8205623 )
update dependency com.google.cloud:sdk-platform-java-config to v3.51.0 ( #3924 ) ( cb66be5 )
update dependency com.google.cloud:sdk-platform-java-config to v3.52.0 ( #3939 ) ( 794bf83 )
update dependency com.google.cloud:sdk-platform-java-config to v3.52.1 ( #3952 ) ( 79b7557 )
update dependency com.google.cloud:sdk-platform-java-config to v3.52.2 ( #3964 ) ( 6775fce )
update dependency com.google.cloud:sdk-platform-java-config to v3.52.3 ( #3971 ) ( f8cf508 )
update dependency com.google.cloud:sdk-platform-java-config to v3.53.0 ( #3980 ) ( a961247 )
update dependency com.google.cloud:sdk-platform-java-config to v3.54.1 ( #3994 ) ( 4e09f6b )
update dependency com.google.oauth-client:google-oauth-client-java6 to v1.36.0 ( #3305 ) ( d05e554 )
update dependency com.google.oauth-client:google-oauth-client-java6 to v1.37.0 ( #3614 ) ( f5faa69 )
update dependency com.google.oauth-client:google-oauth-client-java6 to v1.38.0 ( #3685 ) ( 53bd7af )
update dependency com.google.oauth-client:google-oauth-client-java6 to v1.39.0 ( #3710 ) ( c0c6352 )
update dependency com.google.oauth-client:google-oauth-client-jetty to v1.36.0 ( #3306 ) ( 0eeed66 )
update dependency com.google.oauth-client:google-oauth-client-jetty to v1.37.0 ( #3615 ) ( a6c7944 )
update dependency com.google.oauth-client:google-oauth-client-jetty to v1.38.0 ( #3686 ) ( d71b2a3 )
update dependency com.google.oauth-client:google-oauth-client-jetty to v1.39.0 ( #3711 ) ( 43b86e9 )
update dependency io.opentelemetry:opentelemetry-api to v1.52.0 ( #3902 ) ( 772407b )
update dependency io.opentelemetry:opentelemetry-bom to v1.51.0 ( #3840 ) ( 51321c2 )
update dependency io.opentelemetry:opentelemetry-bom to v1.52.0 ( #3903 ) ( 509a6fc )
update dependency io.opentelemetry:opentelemetry-context to v1.52.0 ( #3904 ) ( 96c1bae )
update dependency io.opentelemetry:opentelemetry-exporter-logging to v1.52.0 ( #3905 ) ( 28ee4c9 )
update dependency node to v22 ( #3713 ) ( 251def5 )
update dependency org.graalvm.buildtools:junit-platform-native to v0.10.2 ( #3311 ) ( 3912a92 )
update dependency org.graalvm.buildtools:native-maven-plugin to v0.10.2 ( #3312 ) ( 9737a5d )
update dependency org.junit.vintage:junit-vintage-engine to v5.10.3 ( #3371 ) ( 2e804c5 )
update dependency ubuntu to v24 ( #3498 ) ( 4f87ade )
update github/codeql-action action to v2.25.10 ( #3348 ) ( 8b6feff )
update github/codeql-action action to v2.25.11 ( #3376 ) ( f1e0014 )
update github/codeql-action action to v2.25.12 ( #3387 ) ( af60b30 )
update github/codeql-action action to v2.25.13 ( #3395 ) ( 95c8d6f )
update github/codeql-action action to v2.25.15 ( #3402 ) ( a61ce7d )
update github/codeql-action action to v2.25.6 ( #3307 ) ( 8999d33 )
update github/codeql-action action to v2.25.7 ( #3334 ) ( 768342d )
update github/codeql-action action to v2.25.8 ( #3338 ) ( 8673fe5 )
update github/codeql-action action to v2.26.10 ( #3506 ) ( ca71294 )
update github/codeql-action action to v2.26.11 ( #3517 ) ( ac736bb )
update github/codeql-action action to v2.26.12 ( #3522 ) ( fdf8dc4 )
update github/codeql-action action to v2.26.13 ( #3536 ) ( 844744f )
update github/codeql-action action to v2.26.2 ( #3426 ) ( 0a6574f )
update github/codeql-action action to v2.26.3 ( #3438 ) ( 390e182 )
update github/codeql-action action to v2.26.5 ( #3446 ) ( 58aacc5 )
update github/codeql-action action to v2.26.6 ( #3464 ) ( 2aeb44d )
update github/codeql-action action to v2.26.7 ( #3482 ) ( e2c94b6 )
update github/codeql-action action to v2.26.8 ( #3488 ) ( a6d75de )
update github/codeql-action action to v2.26.9 ( #3494 ) ( 8154043 )
update github/codeql-action action to v2.27.0 ( #3540 ) ( 1616a0f )
update github/codeql-action action to v2.27.1 ( #3567 ) ( e154ee3 )
update github/codeql-action action to v2.27.3 ( #3569 ) ( 3707a40 )
update github/codeql-action action to v2.27.4 ( #3572 ) ( 2c7b4f7 )
update github/codeql-action action to v2.27.5 ( #3588 ) ( 3f94075 )
update github/codeql-action action to v2.27.6 ( #3597 ) ( bc1f3b9 )
update github/codeql-action action to v2.27.7 ( #3603 ) ( 528426b )
update github/codeql-action action to v2.27.9 ( #3608 ) ( 567ce01 )
update github/codeql-action action to v2.28.0 ( #3621 ) ( e0e09ec )
update github/codeql-action action to v2.28.1 ( #3637 ) ( 858e517 )
update netty.version to v4.1.119.final ( #3717 ) ( 08a290a )
update netty.version to v4.2.0.final ( #3745 ) ( bb811c0 )
update netty.version to v4.2.1.final ( #3780 ) ( 6dcd858 )
update ossf/scorecard-action action to v2.4.0 ( #3408 ) ( 66777a2 )
update ossf/scorecard-action action to v2.4.1 ( #3690 ) ( cdb61fe )
update ossf/scorecard-action action to v2.4.2 ( #3810 ) ( 414f61d )
update sdk-platform-java-config to 3.55.0-rc1 ( #4033 ) ( 580427d )
Documentation
add short mode query sample ( #3397 ) ( 6dca6ff )
add simple query connection read api sample ( #3394 ) ( d407baa )
bigquery: Add javadoc description of timestamp() parameter. ( #3604 ) ( 6ee0c10 )
bigquery: Update TableResult.getTotalRows() docstring ( #3785 ) ( 6483588 )
fix BigQuery documentation formatting ( #3565 ) ( 552f491 )
reformat javadoc ( #3545 ) ( 4763f73 )
update CONTRIBUTING.md for users without branch permissions ( #3670 ) ( 009b9a2 )
update error handling comment to be more precise in samples ( #3712 ) ( 9eb555f )
update iam policy sample user to be consistent with other languages ( #3429 ) ( 2fc15b3 )
update maven format command ( #3877 ) ( d2918da )
Update SimpleApp to explicitly set project id ( #3534 ) ( 903a0f7 )
December 19, 2025
Feature
The BigQuery Data Transfer Service can now transfer data from MySQL to
BigQuery . This feature is generally
available (GA).
Feature
The BigQuery Data Transfer Service can now transfer data from Microsoft SQL
Server to BigQuery . This feature is in
Preview .
December 18, 2025
Feature
The BigQuery Data Transfer Service can now transfer data from the following data
sources to BigQuery:
Klaviyo
HubSpot
These features are in Preview .
Feature
You can now use the BigQuery Data Transfer Service to transfer data from blob
storage sources , such as Amazon Simple
Storage Service (Amazon S3), Azure Blob Storage, and Cloud Storage, into BigLake
Iceberg tables in BigQuery. This feature is in
Preview .
December 16, 2025
Feature
The BigQuery Data Transfer Service can now transfer data from Oracle to
BigQuery . This feature is generally available (GA).
December 15, 2025
Libraries
Java
2.57.0 (2025-12-11)
Features
Add timestamp_precision to Field ( #4014 ) ( 57ffe1d )
Introduce DataFormatOptions to configure the output of BigQuery data types ( #4010 ) ( 6dcc900 )
Relax client-side validation for BigQuery entity IDs ( #4000 ) ( c3548a2 )
Dependencies
Update dependency com.google.cloud:sdk-platform-java-config to v3.54.2 ( #4022 ) ( d2f2057 )
Java
2.57.1 (2025-12-12)
Dependencies
Update actions/upload-artifact action to v6 ( #4027 ) ( 5d389cf )
December 10, 2025
Feature
You can now use the BigQuery remote MCP server
to enable LLM agents to perform a range of data-related tasks.
This feature is in
Preview .
December 02, 2025
Change
An updated version of the
ODBC driver for BigQuery
is now available.
Feature
You can now enable
autonomous embedding generation
on tables that you make with the
CREATE TABLE statement .
When you do this, BigQuery maintains a column of embeddings on
the table based on a source column. When you add or modify data in the source
column, BigQuery automatically generates or updates the embedding
column for that data.
You can also use the
AI.SEARCH
function, enabling semantic search on tables that have autonomous embedding
generation enabled.
These features are in
Preview .
December 01, 2025
Feature
Search results in the Explorer
pane in BigQuery Studio now show
results in the current organization. You can use a drop-down menu to switch
between organizations. This feature is generally
available (GA).
November 26, 2025
Feature
The BigQuery Data Transfer Service now supports incremental data transfers
when transferring data from Salesforce to BigQuery. This feature is supported in
Preview .
November 25, 2025
Change
An updated version of the
JDBC driver for BigQuery
is now available.
November 24, 2025
Feature
You can
set the default project and dataset for your pipeline
in the SQLX options section, which simplifies task configuration by using
these defaults for all tasks. This feature is
generally available
(GA).
November 20, 2025
Feature
You can now use the BigQuery Agent Analytics plugin within the Agent Development
Kit to export agent interaction data directly into BigQuery. This plugin
captures comprehensive logs of your agent's prompts, tool usage, and responses,
enabling you to analyze and visualize agent performance metrics. The plugin
leverages the BigQuery Storage Write API for efficient high-throughput
streaming. For more information on how to leverage this plugin in your agent,
see the
Announcing BigQuery Agent Analytics for the Google ADK .
November 19, 2025
Feature
You can use the
JSON_FLATTEN function
to extract all non-array values that are either directly in the input JSON
value or children of one or more consecutively nested arrays in the input
JSON value. This function is available in
Preview .
Feature
You can now use Gemini in BigQuery to
fix and explain errors
in your SQL queries. This feature is in
Preview .
November 18, 2025
Feature
You can now use Gemini 3.0
when you call generative AI functions in BigQuery,
such as AI.GENERATE .
You must use the full global endpoint argument:
https://aiplatform.googleapis.com/v1/projects/PROJECT_ID/locations/global/publishers/google/models/gemini-3-pro-preview .
Feature
Dataform now lets you automate the creation of
BigLake tables for Apache Iceberg in BigQuery .
This feature is
generally available
(GA).
Feature
BigQuery ML now supports the following
generative AI functions :
AI.GENERATE :
generate free text to accomplish a wide range of tasks, such as
translation, summarization, and classification, on any unstructured data,
including images, audio, video, and documents. It can also perform entity
extraction and generate structured output. This function is
generally available
(GA).
AI.EMBED :
turn text, image, audio, video, or documents into embeddings. This function
is in Preview .
AI.SIMILARITY :
compute the semantic similarity between pairs of text, pairs of images, or
across text and images. This function is in
Preview .
You can use the
AI.GENERATE_BOOL ,
AI.GENERATE_DOUBLE ,
and
AI.GENERATE_INT
functions to generate scalar values, which are convenient for filtering,
scoring, and counting purposes.
Each of these functions supports
authentication with end-user credentials (EUC)
to set up the necessary Vertex AI permissions.
BigQuery ML now supports the following table-valued generative AI functions:
AI.GENERATE_TABLE :
generate a table of structured output from unstructured data including
text, images, audio, and video.
AI.GENERATE_TEXT
is the new, preferred version of ML.GENERATE_TEXT , which has the same
functionality but with simplified column output names.
AI.GENERATE_EMBEDDING
is the new, preferred version of ML.GENERATE_EMBEDDING , which has the same
functionality but with simplified column output names.
These functions are all
generally available
(GA).
Feature
You can now publish data insights ,
including query recommendations and
auto-generated table and column descriptions, to the Dataplex Universal Catalog.
This feature is in
Preview .
November 17, 2025
Feature
You can use folders to organize and control
access to single file code assets, such as notebooks, saved queries, data
canvases, and data preparation files. This feature is in
Preview .
Feature
In the query execution graph, you can now use the query text
heatmap to identify
which query text contributes to stages that consume more slot time, and to see
query plan details for those stages. This feature is in
Preview .
Feature
You can now
share SQL stored procedures in BigQuery sharing listings
and enable
role-based authorization for stored procedures .
These features are in preview .
Libraries
Java
2.56.0 (2025-11-15)
Features
New queryWithTimeout method for customer-side wait ( #3995 ) ( 9c0df54 )
Dependencies
Update dependency com.google.apis:google-api-services-bigquery to v2-rev20251012-2.0.0 ( #3923 ) ( 1d8977d )
Update dependency com.google.cloud:sdk-platform-java-config to v3.54.1 ( #3994 ) ( 4e09f6b )
November 11, 2025
Feature
The BigQuery Overview page
is now your hub for discovering tutorials, features, and resources to help you
get the most out of BigQuery. It provides guided paths for users
of all skill levels. This feature is in
Preview .
Feature
You can now use the
interactive SQL translator , the
translation API , and the
batch SQL translator to translate the
following SQL dialects into GoogleSQL:
Apache Impala SQL
GoogleSQL (BigQuery)
Impala SQL translation can be used to migrate Cloudera and Apache Hadoop SQL
workloads that use Impala as a query engine.
GoogleSQL (BigQuery) translation can be used to verify and iteratively customize
your translated SQL queries after an initial translation from an external
dialect. For example, you can apply systematic query rewrites using YAML
configurations
to customize and optimize your GoogleSQL queries before deploying it.
These features are in Preview .
Feature
You can now use custom constraints with an
Organization Policy to provide more granular control over specific fields for
BigQuery dataset resources. This feature is generally available (GA).
November 10, 2025
Feature
You can aggregate
and deduplicate
table data with Gemini assistance in your
BigQuery data preparations .
These features are generally available (GA).
Feature
Partitioning is now available for
BigLake tables for Apache Iceberg in BigQuery .
This feature is in
Preview .
Feature
BigQuery ML now supports the TimesFM 2.5
time series foundational model .
You can use the TimesFM 2.5 model in the
AI.FORECAST ,
AI.EVALUATE ,
and
AI.DETECT_ANOMALIES
functions to achieve better forecasting accuracy and lower latency.
Feature
BigQuery ML now offers the
AI.DETECT_ANOMALIES function .
Use the AI.DETECT_ANOMALIES function with a TimesFM model to
detect anomalies
in time series data, using historical data as a baseline.
This feature is in
Preview .
November 06, 2025
Announcement
The research paper ARIMA_PLUS: Large-scale, Accurate, Automatic and
Interpretable In-Database Time Series Forecasting and Anomaly Detection in
Google BigQuery is now publicly available.
This paper describes the algorithms behind the
ARIMA_PLUS
and
ARIMA_PLUS_XREG
models for time series forecasting and anomaly detection, and demonstrates the
high performance, scalability, explainability, and customizability of the
models.
November 05, 2025
Feature
You can use the
MATCH_RECOGNIZE clause
in your SQL queries to filter and aggregate matches across rows in a table.
This feature is
generally available
(GA).
Announcement
The BigQuery Data Transfer Service for Google Ads now supports Google Ads API v21 .
Feature
You can now
generate table and column descriptions
in all supported Gemini languages when you generate data insights.
This feature is
generally available
(GA).
Feature
You can now generate data insights when you
create a
DataScan
using the Dataplex API. This feature is
generally available
(GA).
November 04, 2025
Feature
You can now use custom organization policies with the BigQuery migration
service to allow or deny specific
operations during a BigQuery migration to meet your organization's compliance
and security requirements. This includes an option to disable AI suggestions
during a migration. This feature is in
Preview .
November 03, 2025
Libraries
Go
1.72.0 (2025-10-28)
Features
bigquery/reservation: Add new BACKGROUND_CHANGE_DATA_CAPTURE , BACKGROUND_COLUMN_METADATA_INDEX , and BACKGROUND_SEARCH_INDEX_REFRESH reservation assignment types ( 182df61 )
bigquery/reservation: Add new reservation IAM policy get/set/test methods ( 182df61 )
bigquery/reservation: Add support for creation and modification of new reservation groups ( 182df61 )
bigquery: Expose continuous query in config ( #13130 ) ( 2f0942b )
Bug Fixes
bigquery/v2: Upgrade gRPC service registration func ( 8fffca2 )
bigquery: Upgrade gRPC service registration func ( 8fffca2 )
October 31, 2025
Feature
We have increased the row capacity
for pivot tables backed by BigQuery in Connected Sheets
from 100,000 to 200,000 rows.
October 30, 2025
Feature
The
Apache Iceberg REST catalog in BigLake metastore
is now
generally available
(GA) with several new features, including BigQuery catalog federation,
credential vending, and catalog management in the Google Cloud console.
October 29, 2025
Feature
You can now group
reservations
together to prioritize idle slot sharing within the group. Reservations within a
reservation group share idle slots with each other before making them available
to other reservations in the project, giving you more control over slot
allocation for high-priority workloads. This feature is in
Preview .
October 28, 2025
Feature
The BigQuery Data Transfer Service can now transfer data from the
following data sources:
Facebook Ads
Salesforce
Salesforce Marketing Cloud
ServiceNow
Transfers from these data sources are now generally available
(GA).
Feature
Subscriber email logging lets you log the principal identifiers of users
who execute jobs and queries against linked datasets. You can enable
logging at the
listing level
and the
data exchange level .
The logged data is available in the job_principal_subject field of the
INFORMATION_SCHEMA.SHARED_DATASET_USAGE view .
This feature is
generally available .
October 27, 2025
Feature
The administrative jobs explorer now includes a job details
page to help you diagnose
and troubleshoot queries. The Performance tab compiles query information
including the execution graph, SQL text, execution history, performance
variance, and system load during execution. You can also compare two
jobs to identify discrepancies
and potential areas to improve query performance.
This feature is in Preview .
Feature
BigQuery now offers the following
managed AI functions
that use Gemini to help you filter, join, rank, and classify your data:
AI.IF :
Filter and join text or multimodal data based on a condition described in natural language.
AI.SCORE :
Rate text or multimodal input to rank your data by quality, similarity, or other criteria.
AI.CLASSIFY :
Classify text into user-defined categories.
These functions are in Preview .
Feature
You can now use the Data Engineering Agent
to use Gemini in BigQuery to build and modify data
pipelines to ingest data into BigQuery. This feature is in
preview .
Feature
You can now use the Apache Arrow format to
stream data to BigQuery with the Storage Write API .
This feature is
generally available
(GA).
Libraries
Java
2.55.3 (2025-10-21)
Dependencies
Update dependency com.google.cloud:sdk-platform-java-config to v3.53.0 ( #3980 ) ( a961247 )
October 23, 2025
Feature
BigQuery is now offering
early access
to conversational analytics. Conversational analytics accelerates data analysis
by enabling quick insights through natural language. Users can chat with their
BigQuery data, create custom agents, and access those agents even outside of
BigQuery. To enroll in conversational analytics early access, fill out the
request form .
October 22, 2025
Issue
Support for
table parameters in table-value functions (TVFs)
has been temporarily disabled. We are working to restore this feature as soon
as possible.
Feature
You can now use custom constraints with Organization Policy to provide more
granular control over specific fields for some BigQuery sharing
resources. For more information, see
Manage Sharing data exchanges and listings using custom constraints .
This feature is in
preview .
Feature
BigQuery ML now offers a built-in
TimesFM univariate time series forecasting model
that implements Google Research's open source TimesFM model. You can use
BigQuery ML's built-in TimesFM model with the following functions:
Use
AI.FORECAST
to perform forecasting. This function now supports a larger context window.
Use
AI.EVALUATE
to evaluate forecasted data against a reference time series based on
historical data.
To try using a TimesFM model with the AI.FORECAST function, see
Forecast a time series with a TimesFM univariate model .
This feature is
generally available
(GA).
October 21, 2025
Feature
BigQuery now supports TransUnion for
entity resolution .
This feature is
generally available
(GA).
October 20, 2025
Feature
In BigQuery ML, you can now fully manage open models as Vertex AI endpoints.
BigQuery-managed open models offer the following benefits:
Manage Vertex AI resource by using SQL queries
Automatic or immediate open model undeployment
to save costs
Customize model deployment machine types
or reserve open model resources by
using Compute Engine reservations
This feature is in Preview .
Feature
You can now use visualization cells to
automatically
generate a visualization
of any DataFrame in your notebook.
You can customize the columns, chart type, aggregations, colors , labels, and
title.
This feature is in Preview .
October 16, 2025
Feature
You can now access repositories by clicking Repositories in the Explorer pane.
A new tab opens that displays a list of repositories. The Explorer pane no
longer has a bottom pane for repositories. When you open a workspace in a
repository, it opens in the Git repository pane in the left pane. These
features are available in BigQuery Studio in
preview .
Feature
The following features are now generally available (GA) in BigQuery Studio:
To streamline resource discovery and access, the left Explorer
pane has been reorganized
into three sections: Explorer, Classic Explorer, and Git repository. You can
still use the Classic Explorer, which provides the complete resources tree.
In the Explorer pane, you can use the search
feature to find BigQuery
resources in your organization. The results appear in a new tab in the
details pane. You can use filters to narrow your search.
You can access job histories by clicking Job
history in the Explorer pane. A new tab opens
that displays a list of job histories. BigQuery Studio no longer has a
bottom pane for job history.
To reduce tab proliferation, clicking a resource opens it within the same
tab. To open the resource in a separate tab, press Ctrl (or
Command on macOS) and click the resource. To prevent the current
tab from getting its content replaced, double-click the tab. The name
changes from italicized to regular font. If you still
lose your resource, you can click tab_recent Recent tabs in the
details pane to find the resource.
You can use breadcrumbs to navigate through different tabs and
resources in the details pane.
In the Home tab, the What's new section
contains a list of new capabilities and changes to the BigQuery Studio.
The notebook action bar is consolidated by default to give you more screen
space for writing code.
October 15, 2025
Feature
You can
visualize your geospatial query results
on an interactive map in BigQuery Studio. This feature is
generally available
(GA).
Feature
You can use the dbt-bigquery adapter to run Python code that's defined in
BigQuery DataFrames. For more information, see
Use BigQuery DataFrames in dbt .
This feature is
generally available
(GA).
October 14, 2025
Feature
You can now use SQL cells to write,
edit, and run SQL queries on your BigQuery data directly from your
notebooks. This feature is in
Preview .
Announcement
The BigQuery Data Transfer API (bigquerydatatransfer.googleapis.com) is now
enabled by default for every new Google Cloud project. This feature is
generally available
(GA).
Feature
You can now embed natural language as comments in existing SQL to refine and
transform your code .
This feature is preview .
October 13, 2025
Libraries
Java
2.55.2 (2025-10-08)
Dependencies
Fix update dependency com.google.cloud:google-cloud-bigquerystorage-bom to v3.17.2 ( b25095d )
Update dependency com.google.cloud:sdk-platform-java-config to v3.52.3 ( #3971 ) ( f8cf508 )
October 09, 2025
Change
An updated version of the ODBC driver for BigQuery is now available.
Feature
You can set a maximum slot
limit for a
reservation. You can configure the maximum reservation size when creating or
updating a reservation. This feature is now generally
available (GA).
Feature
You can allocate idle slots fairly across
reservations within a single admin project. This ensures each reservation
receives an approximately equal share of available capacity. This feature is now
generally available
(GA).
Announcement
Security, privacy, and compliance for Gemini in
BigQuery details how
customer data is protected and processed by Gemini in BigQuery.
October 08, 2025
Breaking
The default limit of QueryUsagePerDay for
on-demand pricing has changed. The default limit of all new projects is now 200
TiB. For existing projects, the default limit has been set based on your
project's usage over the last 30 days. Projects that have custom cost
controls configured or that use
reservations aren't affected.
If the new limit might affect your workload, create a custom cost
control based on your workload needs.
Feature
You can specify which reservation a query uses at
runtime , and set IAM
policies directly on
reservations . This
provides more flexibility and fine-grained control over resource management.
This feature is generally
available (GA).
Feature
You can set labels on reservations. These labels
can be used to organize your reservations and for billing analysis. This feature
is generally
available (GA).
October 07, 2025
Announcement
As of February 25, 2025, enhancements to the workload management
autoscaler that were announced on July
31, 2024 have rolled out to all users.
These enhancements are generally
available (GA).
October 06, 2025
Feature
The INFORMATION_SCHEMA.SHARED_DATASET_USAGE view
now includes the following schema fields to support usage metrics for
external tables and routines:
shared_resource_id : the ID of the queried resource
shared_resource_type : the type of the queried resource
referenced_tables : Contains project_id ,
dataset_id , table_id , and processed_bytes
fields of the base table.
These fields are
generally available (GA).
Feature
You can now set the priority of BigQuery jobs initiated by
Dataform workflows to run queries as interactive jobs that start
running as quickly as possible or as batch jobs with lower priority. For more
information, see
Create a pipeline schedule
and
InvocationConfig .
This feature is
generally available
(GA).
Feature
The BigQuery Data Transfer Service can now transfer reporting data from Google Analytics 4
into BigQuery. You can also include custom reports from
Google Analytics 4 in your data transfer. This feature is
generally available (GA).
Feature
The BigQuery Data Transfer Service can now transfer data from the
following data sources:
PayPal
Stripe
Transfers from these data sources are supported in preview .
Libraries
Go
1.71.0 (2025-09-30)
Features
bigquery/analyticshub: You can now configure listings for multiple regions for shared datasets and linked dataset replicas in BigQuery sharing ( 10e67ef )
bigquery/reservation: Add a new field failover_mode to .google.cloud.bigquery.reservation.v1.FailoverReservationRequest that allows users to choose between the HARD or SOFT failover modes when they initiate a failover operation on a reservation ( 10e67ef )
bigquery/reservation: Add a new field soft_failover_start_time in the existing replication_status in .google.cloud.bigquery.reservation.v1.Reservation to provide visibility into the state of ongoing soft failover operations on the reservation ( 10e67ef )
bigquery: Add support for MaxSlots ( #12958 ) ( a3c0aca )
Announcement
Starting March 17, 2026, the BigQuery Data Transfer Service will require the
bigquery.datasets.setIamPolicy and the bigquery.datasets.getIamPolicy
permissions on the target dataset to create or update a transfer configuration.
For more information, see Changes to dataset-level access controls .
October 02, 2025
Feature
You can now use the notebook gallery
in the BigQuery web UI as your central hub for discovering and using prebuilt notebook
templates. This feature is in preview .
October 01, 2025
Feature
You can now apply
SQL query generated in the Gemini Cloud Assist chat
to the query open in your editor. This feature is in
Preview .
September 29, 2025
Feature
To simplify access management for your Iceberg tables, you
can use credential vending mode with the Apache Iceberg REST catalog in BigLake metastore. Credential vending removes
the need for catalog users to have direct access to Cloud Storage buckets. This
feature is in Preview .
Feature
You can now create BigQuery
non-incremental materialized views over Spanner data
to improve query performance by periodically caching results.
This feature is in Preview .
Feature
BigQuery data preparation supports unnesting arrays, which expands each
array element into its own row for easier analysis. For more information, see
Unnest arrays .
This feature is generally
available (GA).
Announcement
History-based query optimizations
are now enabled by default. If history-based optimizations have been previously
disabled, you can re-enable history-based optimizations
for your project or organization.
September 25, 2025
Feature
The
ARRAY_FIRST ,
ARRAY_LAST ,
and
ARRAY_SLICE
GoogleSQL functions are now
generally available (GA).
Feature
BigQuery data
canvas now
supports destination table nodes. Destination table nodes let you persist query
results to a new or existing table. This feature is generally
available (GA).
September 24, 2025
Feature
BigQuery ML now supports
visualization of model monitoring metrics .
This feature lets you use charts and graphs to
analyze model monitoring function output .
You can use metric visualization with the
ML.VALIDATE_DATA_SKEW
and
ML.VALIDATE_DATA_DRIFT
functions. This feature is
generally available
(GA).
Feature
For command-line users, BigQuery is now integrated with the Gemini CLI to provide an agentic CLI experience. Using the dedicated Gemini CLI extensions for BigQuery , you can search, explore, analyze, and gain insights from your data by asking natural language questions, generating forecasts, and running contribution analysis directly from the command line. This feature is available in beta.
September 22, 2025
Libraries
Python
3.38.0 (2025-09-15)
Features
Add additional query stats ( #2270 ) ( 7b1b718 )
Feature
You can now run federated queries against PostgreSQL dialect databases in Spanner using BigQuery external datasets with GoogleSQL; this includes cross-region federated queries . This feature is generally available (GA).
September 16, 2025
Feature
You can now access snapshots of Apache Iceberg external tables that are retained in your Iceberg metadata by using the FOR SYSTEM_TIME AS OF clause. This feature is generally available (GA).
Feature
You can use the JSON_KEYS function to extract unique JSON keys from a JSON expression, and you can specify a mode for some JSON functions that take a JSONPath to allow more flexibility in how the path matches the JSON structure. These features are generally available (GA).
Feature
SQL code completion is now available for all BigQuery projects. To learn how to enable and activate Gemini in BigQuery features, see Set up Gemini in BigQuery . This feature is available in preview .
September 15, 2025
Libraries
Java
2.55.0 (2025-09-12)
Features
bigquery: Add custom ExceptionHandler to BigQueryOptions ( #3937 ) ( de0914d )
Dependencies
Update dependency com.google.cloud:google-cloud-bigquerystorage-bom to v3.17.0 ( #3954 ) ( e73deed )
Update dependency com.google.cloud:sdk-platform-java-config to v3.52.1 ( #3952 ) ( 79b7557 )
Libraries
Python
3.37.0 (2025-09-08)
Features
Updates to fastpath query execution ( #2268 ) ( ef2740a )
Bug Fixes
Remove deepcopy while setting properties for _QueryResults ( #2280 ) ( 33ea296 )
Documentation
Clarify that the presence of XyzJob.errors doesn't necessarily mean that the job has not completed or was unsuccessful ( #2278 ) ( 6e88d7d )
Clarify the api_method arg for client.query() ( #2277 ) ( 8a13c12 )
Feature
In the BigQuery Studio, in the Explorer pane, you can now open saved queries in Connected Sheets . This feature is generally available (GA).
Feature
You can now enable the BigQuery advanced runtime to improve query execution time and slot usage. This feature is generally available (GA).
Between September 15, 2025 and early 2026, the BigQuery advanced runtime will become the default runtime for all projects.
September 11, 2025
Feature
Gemini now recommends natural language prompts for you in the SQL generation tool . This feature is in Preview .
Feature
When you use the Data Science Agent in BigQuery, you can now use the Apache Spark or PySpark keywords in your prompt. The Data Science Agent is in Preview .
Feature
Use the BigQuery migration assessment for Informatica to assess the complexity of migrating data from your Informatica platform to BigQuery. This feature is in Preview .
September 10, 2025
Feature
You can load files from Cloud Storage in BigQuery data preparations . This feature is in Preview .
September 09, 2025
Feature
You can configure reusable, default Cloud resource connections in a project. Default connections are generally available (GA).
Feature
The batch and interactive translators now caches your metadata, which can improve latency when you run a SQL translation. This feature is generally available (GA).
Change
You can now perform supervised tuning on a BigQuery ML remote model based on a Vertex AI gemini-2.5-pro or gemini-2.5-flash-lite model.
September 08, 2025
Feature
When you use the Data Science Agent in BigQuery, you can now use the @ symbol to search for BigQuery tables in your project, and you can use the + symbol to search for files to upload. The Data Science Agent is in Preview .
Feature
You can now add tables and views as tasks to BigQuery pipelines. For more information, see Add a pipeline task . This feature is in Preview .
Feature
You can now include table parameters when you create a table-valued function (TVF). This feature is in Preview .
September 03, 2025
Feature
The INFORMATION_SCHEMA.RESERVATIONS_TIMELINE view now includes the per_second_details schema field . This new field provides information regarding reservation capacity and usage on a per-second basis, and also includes details on autoscale utilization. This feature is generally available (GA).
Feature
BigQuery now supports soft failover with managed disaster recovery. This feature is generally available (GA).
Feature
You can flatten records in BigQuery data preparation with a single operation. This feature is generally available (GA).
September 02, 2025
Feature
You can now configure listings for multiple regions for shared datasets and linked dataset replicas in BigQuery sharing. For more information, see Create a listing . This feature is in preview .
Feature
You can now reference BigQuery ML and DataFrames in your prompts when you use the Data Science Agent in a BigQuery notebook. The Data Science Agent is in Preview .
Feature
You can now create a remote model based on the Vertex AI gemini-embedding-001 model. You can then use the ML.GENERATE_EMBEDDING function with this remote model to generate embeddings. This feature is in Preview .
Feature
You can now enable the automatic selection of a processing location in your pipeline configurations. For more information, see Create pipelines . This feature is generally available (GA).
Feature
You can now create a remote model based on an open embedding model from Vertex Model Garden or Hugging Face that is deployed to Vertex AI . Options include E5 Embedding and other leading open embedding generation models. You can then use the ML.GENERATE_EMBEDDING function with this remote model to generate embeddings.
Try this feature with the Generate text embeddings by using an open model and the ML.GENERATE_EMBEDDING function tutorial.
This feature is in Preview .
September 01, 2025
Libraries
Java
2.54.2 (2025-08-26)
Dependencies
Update dependency com.google.cloud:sdk-platform-java-config to v3.52.0 ( #3939 ) ( 794bf83 )
Libraries
Go
1.70.0 (2025-08-28)
Features
bigquery/reservation: Add Reservation.max_slots field to Reservation proto, indicating the total max number of slots this reservation can use up to ( f1de706 )
bigquery/reservation: Add Reservation.scaling_mode field and its corresponding enum message ScalingMode. This field should be used together with Reservation.max_slots ( f1de706 )
bigquery/storage/managedwriter: Allow overriding proto conversion mapping ( #12579 ) ( ce9d29b ), refs #12578
bigquery: Add load/extract job completion ratio ( #12471 ) ( 3dab483 )
bigquery: Load job and external table opts for custom time format, null markers and source column match ( #12470 ) ( 67b0320 )
August 28, 2025
Feature
For additional layers of security and control, you can now use query templates to predefine and limit the queries that can be run in data clean rooms. For more information, see Use query templates . This feature is in preview .
August 26, 2025
Feature
You can deduplicate table data with Gemini assistance in your BigQuery data preparations . Deduplication is in Preview .
August 25, 2025
Libraries
Python
3.36.0 (2025-08-20)
Features
Add created/started/ended properties to RowIterator. ( #2260 ) ( 0a95b24 )
Retry query jobs if jobBackendError or jobInternalError are encountered ( #2256 ) ( 3deff1d )
Documentation
Add a TROUBLESHOOTING.md file with tips for logging ( #2262 ) ( b684832 )
Update README to break infinite redirect loop ( #2254 ) ( 8f03166 )
Feature
You can use the ST_REGIONSTATS geography function to combine raster data using Earth Engine with your vector data stored in BigQuery. For more information, see Work with raster data and try the tutorial that shows you how to use raster data to analyze global temperature . This feature is generally available .
Feature
You can now use data insights to have Gemini generate table and column descriptions from table metadata . This feature is generally available (GA).
August 22, 2025
Feature
Multi-statement transactions are now available for BigLake Iceberg tables in BigQuery . This feature is in Preview .
August 21, 2025
Announcement
Starting September 25, 2025, the BigQuery Data Transfer Service for third-party SAAS and database connectors will update to a consumption-based pricing model. With this new pricing model, you will be charged based on the compute resources consumed by your data transfers, measured in slot-hours. For more information, see Data Transfer Service pricing . This pricing update applies to the following third-party connectors when they are generally available (GA) :
Facebook Ads
MySQL
Oracle
PostgreSQL
Salesforce
Salesforce Marketing Cloud
ServiceNow
Other third-party connectors planned for future releases
August 18, 2025
Libraries
Java
2.54.1 (2025-08-13)
Bug Fixes
Adapt graalvm config to arrow update ( #3928 ) ( ecfabc4 )
Dependencies
Update dependency com.google.cloud:sdk-platform-java-config to v3.51.0 ( #3924 ) ( cb66be5 )
Feature
In the BigQuery console, you can now use the Reference panel to do the following:
In the query editor, you can use the Reference panel to preview the schema details of tables, snapshots, views, and materialized views, or open these resources in a new tab. You can also use the panel to construct new queries or edit existing queries by inserting query snippets or field names.
In the notebook editor, you can use the Reference panel to preview the schema details of tables, snapshots, views, or materialized views, or open these resources in a new tab.
This feature is generally available (GA).
Feature
When you use the Data Science Agent in BigQuery, you can now use the table selector to choose one or more BigQuery tables to analyze. The Data Science Agent is in Preview .
August 14, 2025
Feature
You can use cross region federated queries to query Spanner tables from regions other than the source BigQuery region. These cross region queries incur additional Spanner network egress charges . This feature is generally available (GA).
Feature
You can now visualize your geospatial query results on an interactive map in BigQuery studio. This feature is in preview .
August 13, 2025
Feature
You can aggregate table data with Gemini assistance in your BigQuery data preparations . Aggregations in data preparations are in Preview .
August 12, 2025
Feature
You can now save query results to Cloud Storage . This feature is generally available (GA).
August 11, 2025
Feature
BigQuery resource utilization charts are generally available (GA).
Feature
You can now use chained function call syntax in GoogleSQL to make deeply nested function calls easier to read. This feature is generally available (GA).
Feature
You can now use WITH expressions in your GoogleSQL queries to create temporary variables. This feature is generally available (GA).
Change
BigQuery data preparations are now represented in the SQLX format and in the pipe query syntax to simplify the CI/CD code review process. For more information, see Manage data preparations .
August 06, 2025
Feature
Enabling the advanced runtime now includes short query optimizations . This feature is in preview .
August 04, 2025
Libraries
Java
2.54.0 (2025-07-31)
Features
bigquery: Add OpenTelemetry Samples ( #3899 ) ( e3d9ed9 )
bigquery: Add otel metrics to request headers ( #3900 ) ( 4071e4c )
Dependencies
update dependency com.google.cloud:google-cloud-bigquerystorage-bom to v3.16.1 (#3912) (https://github.com/googleapis/java-bigquery/commit/bb6f6dcb90b1ddf72e630c4dc64737cf2c2ebd2e)
Update dependency com.google.api.grpc:proto-google-cloud-bigqueryconnection-v1 to v2.70.0 ( #3890 ) ( 84207e2 )
Update dependency com.google.apis:google-api-services-bigquery to v2-rev20250706-2.0.0 ( #3910 ) ( ae5c971 )
Update dependency com.google.cloud:sdk-platform-java-config to v3.50.2 ( #3901 ) ( 8205623 )
Update dependency io.opentelemetry:opentelemetry-api to v1.52.0 ( #3902 ) ( 772407b )
Update dependency io.opentelemetry:opentelemetry-bom to v1.52.0 ( #3903 ) ( 509a6fc )
Update dependency io.opentelemetry:opentelemetry-context to v1.52.0 ( #3904 ) ( 96c1bae )
Update dependency io.opentelemetry:opentelemetry-exporter-logging to v1.52.0 ( #3905 ) ( 28ee4c9 )
Feature
You can now use the new Data Science Agent (DSA) for Colab Enterprise and BigQuery to automate exploratory data analysis, perform
machine learning tasks, and deliver insights all within a
Colab Enterprise notebook. This feature is in preview .
July 31, 2025
Feature
You can manage data profile scans and data quality scans across your project by using the Metadata curation page in the Google Cloud console. For more information, see Profile your data and Scan for data quality issues . This feature is generally available (GA).
Change
BigQuery ML now can automatically detect model quota increases in Vertex AI, and automatically adjusts the quota for any BigQuery ML functions that use those models. You no longer need to email the BigQuery ML team to increase model quota.
Change
BigQuery ML has improved throughput by more than 100x for the following
generative AI functions:
ML.GENERATE_TEXT
AI.GENERATE_TABLE
AI.GENERATE
AI.GENERATE_BOOL
AI.GENERATE_DOUBLE
AI.GENERATE_INT
Actual performance varies based on the number of input and output tokens in the
request, but a typical 6-hour job can now process millions of rows. For more
information, see
Generative AI functions .
Feature
You can now use continuous queries to export BigQuery data to Spanner in real time . This feature is in Preview .
July 30, 2025
Announcement
The Gemini for Google Cloud API (cloudaicompanion.googleapis.com) is now enabled by default for most BigQuery projects. Exceptions include projects where customers have opted out, and those linked to accounts based in EMEA regions including BigQuery Europe, Middle East, and Africa regions .
July 28, 2025
Libraries
Python
3.35.1 (2025-07-21)
Documentation
Specify the inherited-members directive for job classes ( #2244 ) ( d207f65 )
Libraries
Node.js
8.1.1 (2025-07-23)
Bug Fixes
Remove is package as dependency ( #1500 ) ( 926c9f8 )
Feature
You can now associate data policies directly on columns . This feature enables direct database administration for controlling access and applying masking and transformation rules at the column level. This feature is in Preview .
July 22, 2025
Feature
You can now use the MATCH_RECOGNIZE clause in your SQL queries to filter and aggregate matches across rows in a table. This feature is in Preview .
Feature
The CREATE EXTERNAL TABLE and LOAD DATA statements now support the following options in Preview :
null_markers : define the strings that represent NULL values in CSV files.
source_column_match : specify how loaded columns are matched to the schema. You can match columns by position or by name.
Feature
Access Transparency supports BigQuery data preparation in the GA stage.
Feature
You can now use the
VECTOR_INDEX.STATISTICS function to calculate how much an indexed table's data has drifted between when a
vector index was created and the present. If table data has changed enough
to require a vector index rebuild , you can use the
ALTER VECTOR INDEX REBUILD statement
to rebuild the vector index. This feature is in Preview .
July 21, 2025
Libraries
Python
3.35.0 (2025-07-15)
Features
Add null_markers property to LoadJobConfig and CSVOptions ( #2239 ) ( 289446d )
Add total slot ms to RowIterator ( #2233 ) ( d44bf02 )
Add UpdateMode to update_dataset ( #2204 ) ( eb9c2af )
Adds dataset_view parameter to get_dataset method ( #2198 ) ( 28a5750 )
Adds date_format to load job and external config ( #2231 ) ( 7d31828 )
Adds datetime_format as an option ( #2236 ) ( 54d3dc6 )
Adds source_column_match and associated tests ( #2227 ) ( 6d5d236 )
Adds time_format and timestamp_format and associated tests ( #2238 ) ( 371ad29 )
Adds time_zone to external config and load job ( #2229 ) ( b2300d0 )
Bug Fixes
Adds magics.context.project to eliminate issues with unit tests … ( #2228 ) ( 27ff3a8 )
Fix rows returned when both start_index and page_size are provided ( #2181 ) ( 45643a2 )
Make AccessEntry equality consistent with from_api_repr ( #2218 ) ( 4941de4 )
Update type hints for various BigQuery files ( #2206 ) ( b863291 )
Documentation
Improve clarity of "Output Only" fields in Dataset class ( #2201 ) ( bd5aba8 )
Libraries
Java
2.53.0 (2025-07-14)
Features
bigquery: Add OpenTelemetry support to BQ rpcs ( #3860 ) ( e2d23c1 )
bigquery: Add support for custom timezones and timestamps ( #3859 ) ( e5467c9 )
Next release from main branch is 2.53.0 ( #3879 ) ( c47a062 )
Bug Fixes
Load jobs preserve ascii control characters configuration ( #3876 ) ( 5cfdf85 )
Dependencies
Update dependency com.google.api.grpc:proto-google-cloud-bigqueryconnection-v1 to v2.69.0 ( #3870 ) ( a7f1007 )
Update dependency com.google.apis:google-api-services-bigquery to v2-rev20250615-2.0.0 ( #3872 ) ( f081589 )
Update dependency com.google.cloud:sdk-platform-java-config to v3.50.1 ( #3878 ) ( 0e971b8 )
Documentation
Update maven format command ( #3877 ) ( d2918da )
Java
2.53.0 (2025-07-14)
Features
bigquery: Add OpenTelemetry support to BQ rpcs ( #3860 ) ( e2d23c1 )
bigquery: Add support for custom timezones and timestamps ( #3859 ) ( e5467c9 )
Next release from main branch is 2.53.0 ( #3879 ) ( c47a062 )
Bug Fixes
Load jobs preserve ascii control characters configuration ( #3876 ) ( 5cfdf85 )
Dependencies
Update dependency com.google.api.grpc:proto-google-cloud-bigqueryconnection-v1 to v2.69.0 ( #3870 ) ( a7f1007 )
Update dependency com.google.apis:google-api-services-bigquery to v2-rev20250615-2.0.0 ( #3872 ) ( f081589 )
Update dependency com.google.cloud:sdk-platform-java-config to v3.50.1 ( #3878 ) ( 0e971b8 )
Documentation
Update maven format command ( #3877 ) ( d2918da )
Feature
You can now use the DISTINCT pipe operator to select distinct rows from a table in your pipe syntax queries. This feature is generally available (GA).
July 17, 2025
Feature
You can now use the WITH pipe operator to define common table expressions in your pipe syntax queries. This feature is generally available (GA).
Feature
You can now use named windows in your pipe syntax queries. This feature is generally available (GA).
July 16, 2025
Feature
You can now create BigQuery ML models by using the
Google Cloud console user interface . This feature is in Preview .
Feature
You can now add comments to notebooks , data canvases , data preparation files , or saved queries . You can also reply to existing comments or get a link to them. This feature is in Preview .
July 15, 2025
Feature
You can flatten JSON columns in BigQuery data preparation with a single operation. This feature is generally available (GA).
Feature
You can now commercialize your BigQuery sharing listings on Google Cloud Marketplace . This feature is generally available (GA).
July 08, 2025
Announcement
Starting August 1, 2025, GoogleSQL will become the default dialect for queries run from the command line interface (CLI) or API. To use LegacySQL, you will need to explicitly specify it in your requests or set the configuration setting default_sql_dialect_option to 'default_legacy_sql' at the project or organization level.
July 07, 2025
Feature
You can now use your Google Account user credentials to authorize the execution of a data preparation in development. For more information, see
Manually run a data preparation in development . This feature is in preview .
July 01, 2025
Feature
You can now update a Cloud KMS encryption key by updating the table with the same key. This feature is generally available (GA).
Feature
You can use the @@location system variable to set the location in which to run a query. This feature is generally available (GA).
Feature
BigQuery now supports the following Apache Hadoop migration features in Preview :
Use the dwh-migration-dumper tool to migrate the metadata necessary for a Hadoop permissions and data migration.
Migrate permissions from Apache Hadoop, Apache Hive, and Ranger HDFS to BigQuery.
Migrate tables from a HDFS data lake to Google Cloud.
June 30, 2025
Libraries
Java
2.52.0 (2025-06-25)
Features
bigquery: Integrate Otel in client lib ( #3747 ) ( 6e3e07a )
bigquery: Integrate Otel into retries, jobs, and more ( #3842 ) ( 4b28c47 )
Bug Fixes
bigquery: Add MY_VIEW_DATASET_NAME TEST to resource clean up sample ( #3838 ) ( b1962a7 )
Dependencies
Remove version declaration of open-telemetry-bom ( #3855 ) ( 6f9f77d )
Update dependency com.google.api.grpc:proto-google-cloud-bigqueryconnection-v1 to v2.66.0 ( #3835 ) ( 69be5e7 )
Update dependency com.google.api.grpc:proto-google-cloud-bigqueryconnection-v1 to v2.68.0 ( #3858 ) ( d4ca353 )
Update dependency com.google.cloud:sdk-platform-java-config to v3.49.2 ( #3853 ) ( cf864df )
Update dependency com.google.cloud:sdk-platform-java-config to v3.50.0 ( #3861 ) ( eb26dee )
Update dependency io.opentelemetry:opentelemetry-bom to v1.51.0 ( #3840 ) ( 51321c2 )
Update ossf/scorecard-action action to v2.4.2 ( #3810 ) ( 414f61d )
Feature
You can now create and manage scheduled notebooks using the Schedule details pane in BigQuery Studio. This feature is generally available (GA).
June 26, 2025
Feature
BigQuery search indexes provide free index management until your organization reaches the limit in a given region. You can now use the INFORMATION_SCHEMA.SEARCH_INDEXES_BY_ORGANIZATION view to understand your current consumption towards that limit, broken down by projects and tables. This feature is generally available (GA).
Feature
You can now use the
use the PARTITION BY clause of the
CREATE VECTOR INDEX statement to partition TreeAH vector indexes . Partitioning enables partition pruning and can decrease I/O costs. This feature is in preview .
June 23, 2025
Feature
You can now use the Apache Iceberg REST catalog in BigLake metastore to create interoperability between your query engines by allowing your open source engines to access Iceberg data in Cloud Storage. This feature is in Preview .
Feature
Colab Enterprise notebooks in BigQuery let you do the following in Preview :
Explain code with Gemini assistance
Fix and explain errors with Gemini assistance
June 18, 2025
Feature
You can now publish the results of a data quality scan as Dataplex Universal Catalog metadata . Previously, data quality scan results were published only to the Google Cloud console. The latest results are saved to the entry that represents the source table. You can view the results in the Google Cloud console. If you want to enable catalog publishing for an existing data quality scan, you must edit the scan and re-enable the publishing option. This feature is generally available (GA).
Feature
You can now use data insights to have Gemini generate table and column descriptions from table metadata . This feature is in Preview .
June 16, 2025
Feature
The BigQuery migration assessment is now available for workflows that use Cloudera and Apache Hadoop . This feature is in Preview .
Feature
You can now manage IAM tags on BigQuery datasets and tables using SQL. This feature is generally available (GA).
Feature
The Merchant Center best sellers report supports multi-client accounts (MCAs). If you have an MCA, you can use the aggregator_id to query the tables. The BestSellersEntityProductMapping table maps the best-selling entities to the products in the sub-accounts' inventory. This provides a consolidated view of best-selling products, which you can then join with product data for more detailed insights. This feature is generally available (GA).
Feature
In BigQuery ML, you can now forecast multiple time series at once by using the TIME_SERIES_ID_COL option that is available in ARIMA_PLUS_XREG multivariate time series models. Try this feature with the Forecast multiple time series with a multivariate model tutorial. This feature is generally available (GA).
Feature
BigQuery now offers the following Gemini-enhanced SQL translation features:
Create Gemini-based configuration YAML files to generate AI suggestions for batch or interactive SQL translations. This feature is now generally available (GA).
After making a batch SQL translation, review your translation output, including Gemini-based suggestions, using the code tab and configuration tab . This feature is now generally available (GA).
When making an interactive SQL translation, create and apply Gemini-enhanced translation rules to customize your SQL inputs. This feature is in Preview .
June 12, 2025
Feature
Dark theme is now available for BigQuery in Preview . To enable the dark theme, in the Google Cloud console, click Settings and utilities > Preferences . In the navigation menu, click Appearance , and then select your color theme and click Save .
June 11, 2025
Feature
The following GoogleSQL functions are now available in preview :
The ARRAY_FIRST function returns the first element of the input array.
The ARRAY_LAST function returns the last element of the input array.
The ARRAY_SLICE function returns an array that contains consecutive elements from the input array.
June 10, 2025
Change
An updated version of the ODBC driver for BigQuery is now available.
Feature
For supported Gemini models , you can now use Vertex AI Provisioned Throughput with the ML.GENERATE_TEXT and AI.GENERATE functions to provide consistent high throughput for requests.
This feature is generally available (GA).
June 09, 2025
Libraries
Java
2.51.0 (2025-06-06)
Features
bigquery: Job creation mode GA ( #3804 ) ( a21cde8 )
bigquery: Support Fine Grained ACLs for Datasets ( #3803 ) ( bebf1c6 )
Dependencies
Rollback netty.version to v4.1.119.Final ( #3827 ) ( 94c71a0 )
Update dependency com.google.api.grpc:proto-google-cloud-bigqueryconnection-v1 to v2.65.0 ( #3787 ) ( 0574ecc )
Update dependency com.google.apis:google-api-services-bigquery to v2-rev20250511-2.0.0 ( #3794 ) ( d3bf724 )
Update dependency com.google.cloud:sdk-platform-java-config to v3.49.0 ( #3811 ) ( 2c5ede4 )
Feature
You can reference Iceberg external tables in materialized views instead of migrating that data to BigQuery-managed storage. This feature is generally available (GA).
June 04, 2025
Change
The organization-level configuration settings for default_sql_dialect_option and query_runtime are unsupported.
June 03, 2025
Feature
BigQuery metastore has been renamed BigLake metastore and is now generally available (GA). The feature formerly known as BigLake metastore has been renamed BigLake metastore (classic).
Feature
You can now use the BigQuery advanced runtime to improve query execution time and slot usage. This feature is in Preview .
Feature
BigQuery tables for Apache Iceberg have been renamed BigLake tables for Apache Iceberg in BigQuery . This feature is now generally available (GA).
June 02, 2025
Libraries
Go
1.69.0 (2025-05-27)
Features
bigquery/analyticshub: Add support for Analytics Hub & Marketplace Integration ( 2aaada3 )
bigquery/analyticshub: Adding allow_only_metadata_sharing to Listing resource ( 2aaada3 )
bigquery/analyticshub: Adding CommercialInfo message to the Listing and Subscription resources ( 2aaada3 )
bigquery/analyticshub: Adding delete_commercial and revoke_commercial to DeleteListingRequest and RevokeSubscriptionRequest ( 2aaada3 )
bigquery/analyticshub: Adding DestinationDataset to the Subscription resource ( 2aaada3 )
bigquery/analyticshub: Adding routine field to the SharedResource message ( 2aaada3 )
bigquery: Add support for dataset view and update modes ( #12290 ) ( 7c1f961 )
bigquery: Job creation mode GA ( #12225 ) ( 1d8990d )
Libraries
Node.js
8.1.0 (2025-05-29)
Features
Job creation mode GA ( #1480 ) ( b51359a )
Support per-job reservation assignment ( #1477 ) ( 8151e72 )
Libraries
Python
3.34.0 (2025-05-27)
Features
Job creation mode GA ( #2190 ) ( 64cd39f )
Bug Fixes
deps: Update all dependencies ( #2184 ) ( 12490f2 )
Documentation
Update query.py ( #2192 ) ( 9b5ee78 )
Use query_and_wait in the array parameters sample ( #2202 ) ( 28a9994 )
Feature
BigQuery now supports using Spanner external datasets with authorized views , authorized routines , and Cloud resource connections . This feature is generally available (GA).
Feature
The CREATE EXTERNAL TABLE and LOAD DATA statements now support the following options in preview :
time_zone : specify a time zone to use when loading data
date_format , datetime_format , time_format , and timestamp_format : define how date and time values are formatted in your source files
Feature
In the navigation menu, you can now go to Settings and select Configuration settings to customize the BigQuery Studio experience for users within the selected project or organization. This is achieved by showing or hiding user interface elements. This feature is in preview .
Feature
In the BigQuery console, in the Welcome tab, you can now try the Apache Spark demo notebook that walks you through the basics of Spark notebook and showcases serverless Spark in BigQuery . This feature is generally available (GA).
May 29, 2025
Feature
You can now use the dbt-bigquery adapter to run Python code that's defined in BigQuery DataFrames. For more information, see Use BigQuery DataFrames in dbt . This feature is in preview .
Feature
You can now use your Google Account user credentials to authorize the creation, scheduling, and running of pipelines as well as the scheduling of notebooks and data preparations. For more information, see Create a pipeline schedule . This feature is in preview .
Feature
You can now create event-driven transfers when transferring data from Cloud Storage to BigQuery. Event-driven transfers can automatically trigger transfer runs when data in your Cloud Storage bucket has been modified or added. This feature is generally available (GA).
May 28, 2025
Feature
You can now create a serverless Spark session and run PySpark code in a BigQuery notebook . This feature is generally available (GA).
Feature
Column metadata indexing is now available for both BigQuery tables and external tables . This feature is generally available (GA).
May 27, 2025
Feature
BigQuery offers optional job creation mode to speed up small queries that you use in your dashboards, data exploration, and other workflows. This mode automatically optimizes eligible queries and uses a cache to improve latency. This feature is generally available (GA).
Feature
You can now share Pub/Sub streaming data through BigQuery sharing with additional client libraries support and provider usage metrics. This feature is generally available (GA).
May 26, 2025
Libraries
Java
2.50.1 (2025-05-16)
Dependencies
Update dependency com.google.cloud:sdk-platform-java-config to v3.48.0 ( #3790 ) ( 206f06d )
Update netty.version to v4.2.1.final ( #3780 ) ( 6dcd858 )
Documentation
bigquery: Update TableResult.getTotalRows() docstring ( #3785 ) ( 6483588 )
Libraries
Python
3.33.0 (2025-05-19)
Features
Add ability to set autodetect_schema query param in update_table ( #2171 ) ( 57f940d )
Add dtype parameters to to_geodataframe functions ( #2176 ) ( ebfd0a8 )
Support job reservation ( #2186 ) ( cb646ce )
Bug Fixes
Ensure AccessEntry equality and repr uses the correct entity_type ( #2182 ) ( 0217637 )
Ensure SchemaField.field_dtype returns a string ( #2188 ) ( 7ec2848 )
May 22, 2025
Change
Starting March 17 2026, the bigquery.datasets.getIamPolicy
IAM permission is required to view a dataset's access controls and to query the
INFORMATION_SCHEMA.OBJECT_PRIVILEGES
view. The bigquery.datasets.setIamPolicy permission is required to update a
dataset's access controls or to create a dataset with access controls using the
API . For more information on this change and how to opt into early enforcement, see Changes to dataset-level access controls .
Feature
When you migrate Teradata data to BigQuery using the BigQuery Data Transfer Service, you can now specify the outputs of the BigQuery translation engine to use as schema mapping . This feature is in preview .
Feature
You can use custom constraints with Organization Policy to provide more granular control over specific fields for some BigQuery resources. This feature is available in Preview .
Feature
When you Set up Gemini in BigQuery you are now prompted to grant the BigQuery Studio User and BigQuery Studio Admin roles. These roles now include permission to use Gemini in BigQuery features. This feature is generally available (GA).
Feature
You can select multiple columns and perform data preparation tasks on them, including dropping columns. For more information, see Prepare data with Gemini . This feature is generally available (GA).
May 21, 2025
Change
You can now perform supervised tuning on a BigQuery ML remote model based on a Vertex AI gemini-2.0-flash-001 or gemini-2.0-flash-lite-001 model.
Feature
You are now able to set access controls on routines . This feature is in Preview .
May 19, 2025
Libraries
Go
1.68.0 (2025-05-12)
Features
bigquery/analyticshub: Support new feature Sharing Cloud Pubsub Streams via AH (GA) and Subscriber Email logging feature ( #11908 ) ( a21d596 )
bigquery/storage: Increased the number of partitions can be written in a single request ( 43bc515 )
bigquery: Add performance insights ( #12101 ) ( aef68ab )
bigquery: Add some missing fields to BQ stats ( #12212 ) ( 77b08e8 )
bigquery: Add WriteTruncateData write disposition ( #12013 ) ( b1126a3 )
bigquery: New client(s) ( #12228 ) ( f229bd9 )
bigquery: Support managed iceberg tables ( #11931 ) ( 35e0774 )
bigquery: Support per-job reservation assignment ( #12078 ) ( c9cebcc )
Bug Fixes
bigquery: Cache total rows count ( #12230 ) ( 202dce0 ), refs #11874 #11873
bigquery: Parse timestamps with timezone info ( #11950 ) ( 530d522 )
bigquery: Update google.golang.org/api to 0.229.0 ( 3319672 )
bigquery: Upgrade gRPC service registration func ( 7c01015 )
Documentation
bigquery/storage: Updated the number of partitions (from 100 to 900) can be inserted, updated and deleted in a single request ( 43bc515 )
Libraries
Python
3.32.0 (2025-05-12) - YANKED
Reason this release was yanked:
PR #2154 caused a performance regression.
Features
Add dataset access policy version attribute ( #2169 ) ( b7656b9 )
Add preview support for incremental results ( #2145 ) ( 22b80bb )
Add WRITE_TRUNCATE_DATA enum ( #2166 ) ( 4692747 )
Adds condition class and assoc. unit tests ( #2159 ) ( a69d6b7 )
Support BigLakeConfiguration (managed Iceberg tables) ( #2162 ) ( a1c8e9a )
Update the AccessEntry class with a new condition attribute and unit tests ( #2163 ) ( 7301667 )
Bug Fixes
query() now warns when job_id is set and the default job_retry is ignored ( #2167 ) ( ca1798a )
Empty record dtypes ( #2147 ) ( 77d7173 )
Table iterator should not use bqstorage when page_size is not None ( #2154 ) ( e89a707 )
Feature
Continuous queries let you build long-lived, continuously processing SQL statements that can analyze, process, and perform machine learning (ML) inference on incoming data in BigQuery in real time.
To monitor your continuous queries, you can use a custom job ID prefix to simplify filtering or view metrics specific to continuous queries in Cloud Monitoring.
Continuous queries can use slot autoscaling to dynamically scale allocated capacity to accommodate your workload.
This feature is generally available (GA).
Feature
Spanner now supports cross regional federated queries from BigQuery which allow BigQuery users to query Spanner tables from regions other than their BigQuery region. Users don't incur Spanner network egress charges during the preview period. This feature is in preview .
May 14, 2025
Feature
You can now schedule automated data transfers from Snowflake to BigQuery using the BigQuery Data Transfer Service. This feature is in preview .
Feature
Vector indexes support the TreeAH index type , which uses Google's ScaNN algorithm. The TreeAH index is optimized for efficient batch processing, capable of handling anywhere from a few thousand to hundreds of thousands of embeddings at once. This feature is generally available (GA).
Feature
BigQuery now supports cross-region transfers for batch loading and exporting data. You can load or export your data from any region or multi-region to any other region or multi-region using a single bq load , LOAD DATA , bq extract , or EXPORT DATA statement. This feature is generally available (GA).
May 13, 2025
Feature
The following SQL features are now generally available (GA) in BigQuery:
GROUP BY STRUCT and the SELECT DISTINCT clause.
GROUP BY ARRAY and the SELECT DISTINCT clause.
GROUP BY ALL clause.
May 12, 2025
Libraries
Java
2.50.0 (2025-05-06)
Features
Add WRITE_TRUNCATE_DATA as an enum value for write disposition ( #3752 ) ( acea61c )
bigquery: Add support for reservation field in jobs. ( #3768 ) ( 3e97f7c )
Dependencies
Update dependency com.google.api.grpc:proto-google-cloud-bigqueryconnection-v1 to v2.63.0 ( #3770 ) ( 934389e )
Update dependency com.google.apis:google-api-services-bigquery to v2-rev20250404-2.0.0 ( #3754 ) ( 1381c8f )
Update dependency com.google.apis:google-api-services-bigquery to v2-rev20250427-2.0.0 ( #3773 ) ( c0795fe )
Update dependency com.google.cloud:sdk-platform-java-config to v3.46.3 ( #3772 ) ( ab166b6 )
Update dependency com.google.cloud:sdk-platform-java-config to v3.47.0 ( #3779 ) ( b27434b )
Feature
You can now view the Query text section in a BigQuery execution graph to understand how the stage steps are related to the query text. This feature is in preview .
Feature
BigQuery resource utilization charts have the following changes:
The default timeline shown in the event timeline chart has changed from one to six hours.
Several improvements have been made to the views, including a new reservation slot usage view. This view helps monitor idle, baseline, and autoscaled slot usage.
This feature is in Preview .
Feature
You can now use BigQuery and BigQuery DataFrames to enable multimodal analysis, transformation, and data engineering (ELT) workflows in both SQL and Python. Use multimodal data features to do the following:
Integrate unstructured data into standard tables by using ObjectRef values, and then work with this data in analysis and transformation workflows by using ObjectRefRuntime values.
Use generative AI to analyze multimodal data and generate embeddings by using
BigQuery ML SQL functions or BigQuery DataFrames methods
with Gemini and multimodal embedding models.
Create multimodal DataFrames in BigQuery DataFrames, and then use object transformation methods to transform images and chunk PDF files.
Use Python user-defined functions (UDFs) to transform images and chunk PDF files.
This feature is in Preview .
May 06, 2025
Change
In the Google Cloud console, Analytics Hub has been renamed BigQuery sharing (Analytics Hub) .
May 05, 2025
Libraries
Node.js
8.0.0 (2025-04-23)
⚠ BREAKING CHANGES
migrate to node 18 ( #1458 )
Miscellaneous Chores
Migrate to node 18 ( #1458 ) ( 6cd706b )
Feature
Changes that you make to your saved queries are now automatically saved . This feature is in preview .
April 28, 2025
Libraries
Java
2.49.1 (2025-04-24)
Bug Fixes
Add labels to converter for listTables method ( #3735 ) ( #3736 ) ( 8634822 )
Dependencies
Update dependency com.google.cloud:sdk-platform-java-config to v3.46.0 ( #3753 ) ( a335927 )
Update netty.version to v4.2.0.final ( #3745 ) ( bb811c0 )
Libraries
Java
2.49.2 (2025-04-26)
Dependencies
Update dependency com.google.cloud:sdk-platform-java-config to v3.46.2 ( #3756 ) ( 907e39f )
Java
2.49.1 (2025-04-24)
Bug Fixes
Add labels to converter for listTables method ( #3735 ) ( #3736 ) ( 8634822 )
Dependencies
Update dependency com.google.cloud:sdk-platform-java-config to v3.46.0 ( #3753 ) ( a335927 )
Update netty.version to v4.2.0.final ( #3745 ) ( bb811c0 )
Feature
Dataplex automatic discovery in BigQuery scans your data in Cloud Storage buckets to extract and catalog metadata, creating BigLake, external, or object tables for analytics and AI for insights, security, and governance. This feature is generally available (GA).
Feature
When you translate SQL queries from your source database, you can use configuration YAML files to optimize and improve the performance of your translated SQL . This feature is generally available (GA).
April 24, 2025
Feature
You can now work with a Gemini powered assistant in a BigQuery data canvas. The data canvas assistant is an agent-like tool, capable of constructing and modifying a data canvas to answer data analytics questions from user prompting. This feature is now in Preview .
April 23, 2025
Feature
You can now specify which reservation a query uses at runtime , and set IAM policies directly on reservations . This provides more flexibility and fine-grained control over resource management. This feature is in public preview .
Feature
You can now set a maximum slot limit for a reservation. You can configure the maximum reservation size when creating or updating a reservation. This feature is in public preview .
Feature
You can now allocate idle slots fairly across reservations within a single admin project. This ensures each reservation receives an approximately equal share of available capacity. This feature is in public preview .
April 21, 2025
Libraries
Node.js
7.9.4 (2025-04-02)
Bug Fixes
MergeSchemaWithRows can be called with empty schema if result set is empty ( #1455 ) ( e608601 )
Announcement
BigQuery now provides spend-based committed use discounts (CUDs). Spend-based committed use discounts provide a discount in exchange for your commitment to spend a minimum amount per hour on PAYG compute resources listed here . You can purchase CUDs with a one or three year commitment period.
Feature
You can now enable fine-grained access control on BigQuery metastore Iceberg tables . This feature is generally available (GA).
Change
You can get the required permissions to use BigQuery data preparation through the BigQuery Studio User ( roles/bigquery.studioUser ) and Gemini for Google Cloud User ( roles/cloudaicompanion.user ) roles, and permission to access the data you're preparing.
BigQuery data preparation no longer requires that you have the permissions granted by the following IAM roles:
BigQuery Data Editor ( roles/bigquery.dataEditor )
Service Usage Consumer ( roles/serviceusage.serviceUsageConsumer )
For more information about the required roles, see Manage data preparations .
April 17, 2025
Feature
You can use partial ordering mode in BigQuery DataFrames to generate efficient queries. This feature is generally available (GA).
Feature
You can now use BigQuery DataFrames version 2.0 , which makes security and performance improvements to the BigQuery DataFrames API, adds new features, and introduces breaking changes.
April 09, 2025
Announcement
Dataplex Catalog has been renamed BigQuery universal catalog . You'll see this new name in the product page of the Google Cloud console, the documentation set, and the marketing collateral. Universal catalog brings together the data catalog capabilities of Dataplex Catalog and the runtime metastore capabilities of BigQuery metastore . For more information, see Introduction to data governance in BigQuery .
Change
Updated pricing, packaging, and setup guidance is now available for Gemini in BigQuery .
Feature
You can now use the Apache Arrow format to stream data to BigQuery with the Storage Write API . This feature is available in preview .
Change
Analytics Hub has been renamed BigQuery sharing . You'll see this new name in the documentation set and the marketing collateral. The product functionality and endpoints remain the same. For more information, see Introduction to data governance in BigQuery .
Feature
You can now combine raster and vector data with the ST_REGIONSTATS geography function to perform geospatial analysis in BigQuery. For more information, see Work with raster data and try the tutorial that shows you how to use raster data to analyze global temperature by country . This feature is in preview .
April 08, 2025
Feature
You can now create, view, modify, and delete Apache Iceberg resources in BigQuery metastore . This feature is generally available (GA).
Feature
You can now connect BigQuery metastore to Apache Flink . This feature is generally available (GA).
Feature
BigQuery ML now offers a built-in TimesFM univariate time series forecasting model that implements Google Research's open source TimesFM model. You can use BigQuery ML's built-in TimesFM model with the AI.FORECAST function to perform forecasting without having to create and train your own model. This lets you avoid the need for model management.
To try using a TimesFM model with the AI.FORECAST function, see Forecast a time series with a TimesFM univariate model .
This feature is in preview .
April 07, 2025
Feature
You can now create remote models in BigQuery ML based on Llama and Mistral AI models in Vertex AI.
Use the ML.GENERATE_TEXT function with these remote models to perform generative natural language tasks for text stored in BigQuery tables. Try this feature with the Generate text by using the ML.GENERATE_TEXT function tutorial.
This feature is generally available (GA).
Change
An updated version of JDBC driver for BigQuery is now available.
Feature
BigQuery data preparation is generally available (GA). It offers AI-powered suggestions from Gemini for data cleansing, transformation, and enrichment. BigQuery supports visual data preparation pipelines and pipeline scheduling with Dataform.
Feature
Smart-tuning is now supported for materialized views when they are in the same project as one of their base tables, or when they are in the project running the query. This feature is generally available (GA).
Change
BigQuery ML now uses dynamic token-based batching for embedding generation requests. Dynamic token-based batching puts as many rows as possible into one request. This change boosts per-request utilization and improves scalability for any queries per minute (QPM) quota . Actual performance varies based on the embedding content length, with an average 10x improvement.
April 04, 2025
Feature
BigQuery ML now supports the following generative AI functions , which let you analyze text using a Vertex AI Gemini model. The function output includes a response that matches the type in the function name:
AI.GENERATE
AI.GENERATE_BOOL
AI.GENERATE_INT
AI.GENERATE_DOUBLE
This feature is in preview .
April 03, 2025
Feature
BigQuery migration assessment now includes support for Amazon Redshift Serverless. This feature is in preview .
Feature
You can now generate structured data by using BigQuery ML's AI.GENERATE_TABLE function with Gemini 1.5 Pro, Gemini 1.5 Flash, and Gemini 2.0 Flash models. You can use the AI.GENERATE_TABLE function's output_schema argument to more easily format the model's response. The output_schema argument lets you specify a SQL schema for formatting, similar to the schema used in the CREATE TABLE statement. By creating structured output, you can more easily convert the function output into a BigQuery table.
Try this feature with the Generate structured data by using the AI.GENERATE_TABLE function tutorial.
This feature is in preview .
April 02, 2025
Feature
You can now create and use Python user-defined functions (UDFs) in BigQuery. Python UDFs support the use of additional libraries and external APIs. This feature is in preview .
Change
The Python code that you generate using Gemini in BigQuery Notebooks is now much more likely to leverage your data. With this change, BigQuery Notebooks can intelligently pull relevant table names directly from your BigQuery project, resulting in personalized, executable Python code.
Feature
You can now generate Dataframes code in BigQuery Notebooks that use BigFrames libraries. In your code generation prompt, include the word BigFrames to generate code that uses BigQuery DataFrames . This feature is in preview .
April 01, 2025
Feature
You can use a CREATE MODEL statement to create a contribution analysis model in BigQuery ML. The top_k_insights_by_apriori_support and pruning_method model options are now supported. You can use a contribution analysis model with the ML.GET_INSIGHTS function to generate insights about changes to key metrics in your multi-dimensional data. The following metric types are supported:
Summable metric
Summable ratio metric
Summable by category metric
This feature is generally available (GA).
Feature
Pipe syntax supports a linear query structure designed to make your queries easier to read, write, and maintain. This feature is generally available (GA).
March 31, 2025
Feature
Iceberg external tables now support merge-on-read. You can query Iceberg tables with position deletes and equality deletes. This feature is generally available (GA).
Libraries
Python
3.31.0 (2025-03-20)
Features
Add query text and total bytes processed to RowIterator ( #2140 ) ( 2d5f932 )
Add support for Python 3.13 ( 0842aa1 )
Bug Fixes
Adding property setter for table constraints, #1990 ( #2092 ) ( f8572dd )
Allow protobuf 6.x ( 0842aa1 )
Avoid "Unable to determine type" warning with JSON columns in to_dataframe ( #1876 ) ( 968020d )
Remove setup.cfg configuration for creating universal wheels ( #2146 ) ( d7f7685 )
Dependencies
Remove Python 3.7 and 3.8 as supported runtimes ( #2133 ) ( fb7de39 )
Feature
BigQuery now supports subqueries in row level access policies . It also includes support for BigLake managed tables and the BigQuery Storage Read API. This feature is now generally available (GA).
Feature
You can now configure the repeat frequency of BigQuery Data Transfer Service for Google Ad Manager . This option has a default of every 8 hours and a minimum of every 4 hours. This feature is generally available (GA).
Feature
You can build BigQuery pipelines (formerly workflows), composed of SQL queries or notebooks, in BigQuery Studio. You can then run these pipelines on a schedule. You can also configure notebook runtimes for a pipeline, share a pipeline, or share a pipeline link. This feature is generally available (GA).
Feature
You can now skip loading match tables for BigQuery Data Transfer Service for Google Ad Manager . If match tables are not needed, you can set parameter load_match_tables to FALSE . This feature is generally available (GA).
Feature
You can now use BigQuery Data Transfer Service for Search Ads to view Performance Max (PMax) campaign data for the following tables:
CartDataSalesStats
ProductAdvertised
ProductAdvertisedDeviceStats
ProductAdvertisedConversionActionAndDeviceStats
This feature is generally available (GA).
Feature
On the Scheduling page, you can now view existing schedules, create new schedules, and perform other actions for data preparations, notebooks, BigQuery pipelines, and scheduled queries. For more information, see Create a pipeline schedule . This feature is generally available (GA).
Feature
You can now define a _CHANGE_SEQUENCE_NUMBER for BigQuery change data capture (CDC) to manage streaming UPSERT ordering for BigQuery. This feature is generally available (GA).
Feature
You can include data preparation tasks in BigQuery pipelines that execute your code assets in sequence at a scheduled time. This feature is in Preview .
March 27, 2025
Feature
You can now enable metadata caching for SQL translation , which can significantly reduce latency for subsequent translation requests. This feature is in preview .
March 26, 2025
Feature
You can now set the column granularity when you create a search index , which stores additional column information in your search index to further optimize your search query performance. This feature is in preview .
March 25, 2025
Feature
BigQuery ML now supports visualization of model monitoring metrics . This feature lets you use charts and graphs to analyze model monitoring function output . The following functions support metric visualization:
ML.VALIDATE_DATA_SKEW : compute the statistics for a set of serving data, and then compare them to the statistics for the data used to train a BigQuery ML model in order to identify anomalous differences between the two data sets.
ML.VALIDATE_DATA_DRIFT : compute and compare the statistics for two sets of serving data in order to identify anomalous differences between the two data sets.
This feature is in preview .
March 24, 2025
Libraries
Node.js
7.9.3 (2025-03-17)
Bug Fixes
Make sure to pass selectedFields to tabledata.list method ( #1449 ) ( 206aff9 )
Libraries
Java
2.49.0 (2025-03-20)
Features
bigquery: Implement getArray in BigQueryResultImpl ( #3693 ) ( e2a3f2c )
Next release from main branch is 2.49.0 ( #3706 ) ( b46a6cc )
Bug Fixes
Retry ExceptionHandler not retrying on IOException ( #3668 ) ( 83245b9 )
Dependencies
Exclude io.netty:netty-common from org.apache.arrow:arrow-memor… ( #3715 ) ( 11b5809 )
Update actions/upload-artifact action to v4.6.2 ( #3724 ) ( 426a59b )
Update actions/upload-artifact action to v4.6.2 ( #3724 ) ( 483f930 )
Update dependency com.google.api.grpc:proto-google-cloud-bigqueryconnection-v1 to v2.61.0 ( #3703 ) ( 53b07b0 )
Update dependency com.google.api.grpc:proto-google-cloud-bigqueryconnection-v1 to v2.62.0 ( #3726 ) ( 38e004b )
Update dependency com.google.apis:google-api-services-bigquery to v2-rev20250302-2.0.0 ( #3720 ) ( c0b3902 )
Update dependency com.google.apis:google-api-services-bigquery to v2-rev20250313-2.0.0 ( #3723 ) ( b8875a8 )
Update dependency com.google.cloud:google-cloud-datacatalog-bom to v1.65.0 ( #3704 ) ( 53b68b1 )
Update dependency com.google.cloud:google-cloud-datacatalog-bom to v1.66.0 ( #3727 ) ( 7339f94 )
Update dependency com.google.cloud:sdk-platform-java-config to v3.45.1 ( #3714 ) ( e4512aa )
Update dependency com.google.oauth-client:google-oauth-client-java6 to v1.39.0 ( #3710 ) ( c0c6352 )
Update dependency com.google.oauth-client:google-oauth-client-jetty to v1.39.0 ( #3711 ) ( 43b86e9 )
Update dependency node to v22 ( #3713 ) ( 251def5 )
Update netty.version to v4.1.119.final ( #3717 ) ( 08a290a )
Documentation
Update error handling comment to be more precise in samples ( #3712 ) ( 9eb555f )
Libraries
Go
1.67.0 (2025-03-14)
Features
bigquery/reservation: Add a new field enable_gemini_in_bigquery to .google.cloud.bigquery.reservation.v1.Assignment that indicates if "Gemini in Bigquery"(https ( 601e742 )
bigquery/reservation: Add a new field replication_status to .google.cloud.bigquery.reservation.v1.Reservation to provide visibility into errors that could arise during Disaster Recovery(DR) replication ( #11666 ) ( 601e742 )
bigquery/reservation: Add the CONTINUOUS Job type to .google.cloud.bigquery.reservation.v1.Assignment.JobType for continuous SQL jobs ( 601e742 )
bigquery: Support MetadataCacheMode for ExternalDataConfig ( #11803 ) ( af5174d ), refs #11802
Bug Fixes
bigquery: Increase timeout for storage api test and remove usage of deprecated pkg ( #11810 ) ( f47e038 ), refs #11801
bigquery: Update golang.org/x/net to 0.37.0 ( 1144978 )
Documentation
bigquery/reservation: Remove the section about EDITION_UNSPECIFIED in the comment for slot_capacity in .google.cloud.bigquery.reservation.v1.Reservation to clarify that ( 601e742 )
bigquery/reservation: Update the google.api.field_behavior for the .google.cloud.bigquery.reservation.v1.Reservation.primary_location and .google.cloud.bigquery.reservation.v1.Reservation.original_primary_location fields to clarify that they are OUTPUT_ONLY ( 601e742 )
Feature
We have redesigned the Add Data dialog to guide you through loading data into BigQuery with a source-first experience and enhanced search and filtering capabilities. This feature is generally available (GA).
Feature
You can now set labels on reservations. These labels can be used to organize your reservations and for billing analysis. This feature is in preview .
Feature
The BigQuery Data Transfer Service can now transfer reporting and configuration data from Google Analytics 4 into BigQuery. This feature is in preview .
Feature
You can now use KLL quantile functions to efficiently compute approximate quantiles. This feature is in preview .
March 20, 2025
Feature
You can now create remote models in BigQuery ML based on the Anthropic Claude model in Vertex AI.
Use the ML.GENERATE_TEXT function with these remote models to perform generative natural language tasks for text stored in BigQuery tables. Try this feature with the Generate text by using the ML.GENERATE_TEXT function tutorial.
You can also evaluate Claude models by using the ML.EVALUATE function .
This feature is generally available (GA).
Feature
You can now use repositories and workspaces in BigQuery to perform version control.
Repositories perform version control on files by using Git to record changes and manage file versions. You can use workspaces within repositories to edit the code stored in the repository.
You can have a repository use Git directly on BigQuery, or you can connect a repository to a third-party Git provider .
This feature is in preview .
Announcement
BigQuery workflows have been renamed to BigQuery pipelines in the Google Cloud console. For more information, see Introduction to BigQuery pipelines .
March 17, 2025
Feature
You can now use EXPORT DATA statements to reverse ETL BigQuery data to Spanner . This feature is generally available (GA).
Feature
You can now use the TYPEOF function to determine the data type of an expression. This feature is generally available (GA).
Feature
You can now create an external dataset in BigQuery that links to an existing database in Spanner . This feature is generally available (GA).
March 13, 2025
Feature
Dataform now supports the CMEK organization policy .
Feature
You can now use Gemini Cloud Assist chat to generate SQL queries and Python code . This feature is in preview .
March 12, 2025
Feature
You can configure reusable, default Cloud resource connections in a project. Default connections are available in Preview .
Change
An updated version of ODBC driver for BigQuery is now available.
March 10, 2025
Announcement
Analytics Hub egress controls and data clean room subscriptions are now available in all BigQuery editions and on-demand pricing.
March 06, 2025
Feature
BigQuery Data Transfer Service now supports custom reports for Google Ads . You can use Google Ads Query Language (GAQL) queries in your transfer configuration to ingest custom Google Ads reports and fields beyond those available in the standard reports and fields . This feature is now generally available (GA).
March 04, 2025
Change
BigQuery is now available in the Stockholm (europe-north2) region .
March 03, 2025
Libraries
Python
3.30.0 (2025-02-26)
Features
Add roundingmode enum, wiring, and tests ( #2121 ) ( 3a48948 )
Adds foreign_type_info attribute to table class and adds unit tests. ( #2126 ) ( 2c19681 )
Support resource_tags for table ( #2093 ) ( d4070ca )
Bug Fixes
Avoid blocking in download thread when using BQ Storage API ( #2034 ) ( 54c8d07 )
Retry 404 errors in Client.query(...) ( #2135 ) ( c6d5f8a )
Dependencies
Updates required checks list in github ( #2136 ) ( fea49ff )
Use pandas-gbq to determine schema in load_table_from_dataframe ( #2095 ) ( 7603bd7 )
Documentation
Update magics.rst ( #2125 ) ( b5bcfb3 )
Libraries
Java
2.48.1 (2025-02-26)
Dependencies
Update actions/upload-artifact action to v4.6.1 ( #3691 ) ( 9c0edea )
Update dependency com.google.api.grpc:proto-google-cloud-bigqueryconnection-v1 to v2.60.0 ( #3680 ) ( 6d9a40d )
Update dependency com.google.apis:google-api-services-bigquery to v2-rev20250216-2.0.0 ( #3688 ) ( e3beb6f )
Update dependency com.google.cloud:google-cloud-datacatalog-bom to v1.64.0 ( #3681 ) ( 9e4e261 )
Update dependency com.google.cloud:sdk-platform-java-config to v3.44.0 ( #3694 ) ( f69fbd3 )
Update dependency com.google.oauth-client:google-oauth-client-java6 to v1.38.0 ( #3685 ) ( 53bd7af )
Update dependency com.google.oauth-client:google-oauth-client-jetty to v1.38.0 ( #3686 ) ( d71b2a3 )
Update ossf/scorecard-action action to v2.4.1 ( #3690 ) ( cdb61fe )
Feature
Gemini in BigQuery can help you complete Python code with contextually appropriate recommendations that are based on content in the query editor. This feature is now generally available (GA).
Feature
You can create a SQL user-defined aggregate function by using the CREATE AGGREGATE FUNCTION statement . This feature is generally available (GA).
February 25, 2025
Feature
BigQuery resource utilization charts provide metrics views and more chart configuration options in Preview .
Feature
You can use the best sellers and price competitiveness migration guides to transition to the newer version of the reports. This feature is in preview .
Announcement
You can now see a list of BigQuery API and service dependencies . You can also review the effects of disabling an API or service.
February 24, 2025
Feature
You can now use the @@location system variable to set the location in which to run a query. This feature is in preview .
February 17, 2025
Libraries
Node.js
7.9.2 (2025-02-12)
Bug Fixes
Avoid schema field mutation when passing selectedFields opt ( #1437 ) ( 27044d5 )
Java
2.48.0 (2025-02-13)
Features
Implement wasNull for BigQueryResultSet ( #3650 ) ( c7ef94b )
Dependencies
Update dependency com.google.api.grpc:proto-google-cloud-bigqueryconnection-v1 to v2.59.0 ( #3660 ) ( 3a6228b )
Update dependency com.google.apis:google-api-services-bigquery to v2-rev20250128-2.0.0 ( #3667 ) ( 0b92af6 )
Update dependency com.google.cloud:google-cloud-datacatalog-bom to v1.63.0 ( #3661 ) ( 9bc8c01 )
Update dependency com.google.cloud:sdk-platform-java-config to v3.43.0 ( #3669 ) ( 4d9e0ff )
Documentation
Update CONTRIBUTING.md for users without branch permissions ( #3670 ) ( 009b9a2 )
Libraries
Java
2.48.0 (2025-02-13)
Features
Implement wasNull for BigQueryResultSet ( #3650 ) ( c7ef94b )
Dependencies
Update dependency com.google.api.grpc:proto-google-cloud-bigqueryconnection-v1 to v2.59.0 ( #3660 ) ( 3a6228b )
Update dependency com.google.apis:google-api-services-bigquery to v2-rev20250128-2.0.0 ( #3667 ) ( 0b92af6 )
Update dependency com.google.cloud:google-cloud-datacatalog-bom to v1.63.0 ( #3661 ) ( 9bc8c01 )
Update dependency com.google.cloud:sdk-platform-java-config to v3.43.0 ( #3669 ) ( 4d9e0ff )
Documentation
Update CONTRIBUTING.md for users without branch permissions ( #3670 ) ( 009b9a2 )
Feature
Subscriber email logging lets you log the principal identifiers of users who execute jobs and queries against linked datasets. You can enable logging at the listing level and the data exchange level (for all the listings in the data exchange). Once you enable and save subscriber email logging, this setting cannot be edited. This feature is in preview .
February 10, 2025
Libraries
Go
1.66.1 (2025-02-03)
Bug Fixes
bigquery: Move MaxStaleness field to table level ( #10066 ) ( 164492d )
Libraries
Go
1.66.2 (2025-02-04)
Bug Fixes
bigquery: Broken github.com/envoyproxy/go-control-plane/envoy dep ( #11556 ) ( e70d63b ), refs #11542
Feature
BigQuery data preparation provides context-aware join operation recommendations from Gemini . Data preparation is available in Preview .
February 06, 2025
Feature
You can create a JavaScript user-defined aggregate function by using the CREATE AGGREGATE FUNCTION statement . This feature is generally available (GA).
February 03, 2025
Libraries
Java
2.47.0 (2025-01-29)
Features
bigquery: Support resource tags for datasets in java client ( #3647 ) ( 01e0b74 )
Bug Fixes
bigquery: Remove ReadAPI bypass in executeSelect() ( #3624 ) ( fadd992 )
Close bq read client ( #3644 ) ( 8833c97 )
Dependencies
Update dependency com.google.apis:google-api-services-bigquery to v2-rev20250112-2.0.0 ( #3651 ) ( fd06100 )
Update dependency com.google.cloud:sdk-platform-java-config to v3.42.0 ( #3653 ) ( 1a14342 )
Update github/codeql-action action to v2.28.1 ( #3637 ) ( 858e517 )
Feature
You can now use the BY NAME and CORRESPONDING modifiers with set operations to match columns by name instead of by position. This feature is generally available (GA).
Change
The BigQuery ML ML.BUCKETIZE and ML.QUANTILE_BUCKETIZE functions now support formatting of the function output. You can use the output_format argument to format the function output as one of the following:
A string in the format bin_<bucket_index>
A string in interval notation
A JSON-formatted string
January 28, 2025
Feature
You can now view stored column usage information for a query job that performs vector search using stored columns. This feature is generally available (GA).
January 27, 2025
Libraries
Python
3.29.0 (2025-01-21)
Features
Add ExternalCatalogTableOptions class and tests ( #2116 ) ( cdc1a6e )
Bug Fixes
Add default value in SchemaField.from_api_repr() ( #2115 ) ( 7de6822 )
Libraries
Go
1.66.0 (2025-01-20)
Features
bigquery/storage/managedwriter: Graceful connection drains ( #11463 ) ( b29912f )
Bug Fixes
bigquery: Update golang.org/x/net to v0.33.0 ( e9b0b69 )
Feature
You can now set conditional IAM access on BigQuery datasets with access control lists (ACLs). This feature is generally available (GA).
Feature
The following BigQuery ML generative AI features are now available:
Creating a
remote model
based on an
open model from Vertex Model Garden or Hugging Face that is deployed to Vertex AI .
Options include Llama, Gemma, and other leading open text generation models.
Using the
ML.GENERATE_TEXT function
with this remote model to perform a broad range of generative AI tasks.
Using the
ML.EVALUATE function
to evaluate the remote model.
Try these features with the
Generate text by using the ML.GENERATE_TEXT function
how-to topic and the
Generate text by using a Gemma open model and the ML.GENERATE_TEXT function
tutorial.
These features are
generally available
(GA).
Announcement
We previously communicated that after January 27, 2025, a purchase would be required to use Gemini in BigQuery features . We are temporarily delaying enforcement of these procurement methods, and no purchase is required at this time. For more information, see Gemini for Google Cloud pricing .
January 22, 2025
Feature
BigQuery metastore lets you access and manage metadata from a variety of processing engines, including BigQuery and Apache Spark. BigQuery metastore supports BigQuery tables and open formats such as Apache Iceberg. This feature is in preview .
January 21, 2025
Feature
You can use natural language to prepare data with Gemini in BigQuery .
Feature
In BigQuery ML, you can now evaluate Anthropic Claude models by using the
ML.EVALUATE function .
The quotas
for use of Anthropic Claude models in BigQuery ML have also been brought into
parity with Vertex AI quotas.
This feature is in
preview .
Feature
Data preparation in BigQuery lets you test data preparations you're developing before you deploy and schedule runs in production. For more information, see Develop a data preparation .
January 20, 2025
Libraries
Python
3.28.0 (2025-01-15) - YANKED
Reason this release was yanked:
This turned out to be incompatible with pandas-gbq . For more details, see issue .
Features
Add property for allowNonIncrementalDefinition for materialized view ( #2084 ) ( 3359ef3 )
Add property for maxStaleness in table definitions ( #2087 ) ( 729322c )
Add type hints to Client ( #2044 ) ( 40529de )
Adds ExternalCatalogDatasetOptions and tests ( #2111 ) ( b929a90 )
Adds ForeignTypeInfo class and tests ( #2110 ) ( 55ca63c )
Adds new input validation function similar to isinstance. ( #2107 ) ( a2bebb9 )
Adds StorageDescriptor and tests ( #2109 ) ( 6be0272 )
Adds the SerDeInfo class and tests ( #2108 ) ( 62960f2 )
Migrate to pyproject.toml ( #2041 ) ( 1061611 )
Preserve unknown fields from the REST API representation in SchemaField ( #2097 ) ( aaf1eb8 )
Resource tags in dataset ( #2090 ) ( 3e13016 )
Support setting max_stream_count when fetching query result ( #2051 ) ( d461297 )
Bug Fixes
Allow geopandas 1.x ( #2065 ) ( f2ab8cb )
Documentation
Render fields correctly for update calls ( #2055 ) ( a4d9534 )
Libraries
Java
2.46.0 (2025-01-11)
Features
bigquery: Support IAM conditions in datasets in Java client. ( #3602 ) ( 6696a9c )
Bug Fixes
NPE when reading BigQueryResultSet from empty tables ( #3627 ) ( 9a0b05a )
test: Force usage of ReadAPI ( #3625 ) ( 5ca7d4a )
Dependencies
Update actions/upload-artifact action to v4.5.0 ( #3620 ) ( cc25099 )
Update actions/upload-artifact action to v4.6.0 ( #3633 ) ( ca20aa4 )
Update dependency com.google.api.grpc:proto-google-cloud-bigqueryconnection-v1 to v2.57.0 ( #3617 ) ( 51370a9 )
Update dependency com.google.api.grpc:proto-google-cloud-bigqueryconnection-v1 to v2.58.0 ( #3631 ) ( b0ea0d5 )
Update dependency com.google.apis:google-api-services-bigquery to v2-rev20241222-2.0.0 ( #3623 ) ( 4061922 )
Update dependency com.google.cloud:google-cloud-datacatalog-bom to v1.61.0 ( #3618 ) ( 6cba626 )
Update dependency com.google.cloud:google-cloud-datacatalog-bom to v1.62.0 ( #3632 ) ( e9ff265 )
Update dependency com.google.cloud:sdk-platform-java-config to v3.41.1 ( #3628 ) ( 442d217 )
Update dependency com.google.oauth-client:google-oauth-client-java6 to v1.37.0 ( #3614 ) ( f5faa69 )
Update dependency com.google.oauth-client:google-oauth-client-jetty to v1.37.0 ( #3615 ) ( a6c7944 )
Update github/codeql-action action to v2.27.9 ( #3608 ) ( 567ce01 )
Update github/codeql-action action to v2.28.0 ( #3621 ) ( e0e09ec )
January 17, 2025
Feature
In the navigation menu , you can now go to the Settings page to set default settings that are applied when you start a session in BigQuery Studio. This feature is in preview .
Feature
The BigQuery Data Transfer Service can now transfer data from the following data sources:
MySQL
PostgreSQL
Transfers from these data sources are supported in Preview .
January 16, 2025
Feature
The BigQuery migration assessment for Oracle now includes a total cost of ownership (TCO) calculator that provides an estimation of compute and storage costs for migrating your Oracle data warehouse to BigQuery. This feature is in preview .
Feature
We have rearranged the navigation menu into new categories. This feature is generally available (GA).
January 13, 2025
Feature
You can now use BigQuery Omni Virtual Private Cloud (VPC) allowlists to restrict access to AWS S3 buckets and Azure Blob Storage from specific BigQuery Omni VPCs. This feature is generally available (GA).
Feature
In BigQuery ML, you can now forecast multiple time series at once by using the
new
TIME_SERIES_ID_COL option
that is available in ARIMA_PLUS_XREG multivariate time series models. Try this
feature with the
Forecast multiple time series with a multivariate model
tutorial.
This feature is in
preview .
January 02, 2025
Change
An updated version of JDBC driver for BigQuery is now available.
Send feedback
Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License , and code samples are licensed under the Apache 2.0 License . For details, see the Google Developers Site Policies . Java is a registered trademark of Oracle and/or its affiliates.
Last updated 2026-04-02 UTC.
Need to tell us more?
[[["Easy to understand","easyToUnderstand","thumb-up"],["Solved my problem","solvedMyProblem","thumb-up"],["Other","otherUp","thumb-up"]],[["Hard to understand","hardToUnderstand","thumb-down"],["Incorrect information or sample code","incorrectInformationOrSampleCode","thumb-down"],["Missing the information/samples I need","missingTheInformationSamplesINeed","thumb-down"],["Other","otherDown","thumb-down"]],["Last updated 2026-04-02 UTC."],[],[]]
Products and pricing
See all products
Google Cloud pricing
Google Cloud Marketplace
Contact sales
Support
Community forums
Support
Release Notes
System status
Resources
GitHub
Getting Started with Google Cloud
Code samples
Cloud Architecture Center
Training and Certification
Engage
Blog
Events
X (Twitter)
Google Cloud on YouTube
Google Cloud Tech on YouTube
About Google
Privacy
Site terms
Google Cloud terms
Manage cookies
Our third decade of climate action: join us
Sign up for the Google Cloud newsletter
Subscribe
English
Deutsch
Español – América Latina
Français
Português – Brasil
中文 – 简体
日本語
한국어
