---
title: "BigQuery IAM roles and permissions \_|\_ Google Cloud Documentation"
url: https://docs.cloud.google.com/bigquery/docs/access-control
fetch_mode: browser_cdp_bfs
status_code: 200
blocked_reason: null
---

Home
Documentation
Data analytics
BigQuery
Guides
Send feedback
BigQuery IAM roles and permissions
This document provides a list of Identity and Access Management (IAM) predefined roles and permissions for BigQuery. This page includes roles and permissions for the following:
BigQuery: Roles and permissions that apply to BigQuery resources such as datasets, tables, views, and routines. Many of these roles and permissions can also be granted to Resource Manager resources like projects, folders, and organizations.
BigQuery Connection API: Role that grants a service agent access to a Cloud SQL connection.
BigQuery Continuous Query: Role that grants a service account access to a continuous query.
BigQuery Data Policy: Roles and permissions that apply to Data Policies in BigQuery.
BigQuery Data Transfer Service: Role that grants a service agent access to create jobs that transfer data.
BigQuery Engine for Apache Flink: Roles and permissions that apply to BigQuery Engine for Apache Flink resources.
BigQuery Migration Service API: Roles and permissions that apply to BigQuery Migration Service resources.
BigQuery Omni: Role that grants a service agent access to tables.
BigQuery sharing: Roles and permissions that apply to BigQuery sharing resources.
BigQuery predefined IAM roles
The following tables list the predefined BigQuery IAM roles with a corresponding list of all the permissions each role includes. Note that each permission is applicable to a particular resource type.
Note: When new capabilities are added to BigQuery, new permissions might be added to predefined IAM roles, and new predefined IAM roles might be added to BigQuery. If your organization requires role definitions to remain unchanged, you should create custom IAM roles.
BigQuery roles
This table lists the predefined IAM roles and permissions for BigQuery. To search through all roles and permissions, see the role and permission index.
For information on granting predefined roles on BigQuery resources like datasets, tables, and routines, see Control access to resources with IAM.
Role Permissions
BigQuery Admin
(roles/bigquery.admin)
Provides permissions to manage all resources within the project. Can manage all data within the project, and can cancel jobs from other users running within the project.
It is possible to grant this role to the following lowest-level resources, but it is not recommended. Other predefined roles grant full permissions over these resources and are less permissive. BigQuery Admin is typically granted at the project level.
Lowest-level resources where you can grant this role:
Dataset
These resources within a dataset:
Table
View
Routine
Connection
Saved query
Data canvas
Pipeline
Data preparation
Repository
This role can also be granted on Resource Manager resources (projects, folders, and organizations).
bigquery.bireservations.*
bigquery.capacityCommitments.*
bigquery.config.*
bigquery.connections.*
bigquery.dataPolicies.attach
bigquery.dataPolicies.create
bigquery.dataPolicies.delete
bigquery.dataPolicies.get
bigquery.dataPolicies.getIamPolicy
bigquery.dataPolicies.list
bigquery.dataPolicies.setIamPolicy
bigquery.dataPolicies.update
bigquery.datasets.*
bigquery.jobs.*
bigquery.models.*
bigquery.objectRefs.*
bigquery.readsessions.*
bigquery.reservationAssignments.*
bigquery.reservationGroups.*
bigquery.reservations.*
bigquery.routines.*
bigquery.rowAccessPolicies.create
bigquery.rowAccessPolicies.delete
bigquery.rowAccessPolicies.get
bigquery.rowAccessPolicies.getIamPolicy
bigquery.rowAccessPolicies.list
bigquery.rowAccessPolicies.overrideTimeTravelRestrictions
bigquery.rowAccessPolicies.setIamPolicy
bigquery.rowAccessPolicies.update
bigquery.savedqueries.*
bigquery.tables.*
bigquery.transfers.*
bigquerymigration.translation.translate
cloudkms.keyHandles.*
cloudkms.operations.get
cloudkms.projects.showEffectiveAutokeyConfig
dataform.*
dataplex.datascans.*
dataplex.operations.get
dataplex.operations.list
dataplex.projects.search
resourcemanager.projects.get
resourcemanager.projects.list
Connected Sheets Service Agent
(roles/bigquery.connectedSheetsServiceAgent)
Grants Connected Sheets Service Account access to create and manage BigQuery jobs on the customers resources.
Warning: Do not grant service agent roles to any principals except service agents.
bigquery.datasets.get
bigquery.jobs.create
bigquery.tables.create
bigquery.tables.update
bigquery.tables.updateData
BigQuery Connection Admin
(roles/bigquery.connectionAdmin)
Lowest-level resources where you can grant this role:
Connection
This role can also be granted on Resource Manager resources (projects, folders, and organizations).
bigquery.connections.*
BigQuery Connection User
(roles/bigquery.connectionUser)
Lowest-level resources where you can grant this role:
Connection
This role can also be granted on Resource Manager resources (projects, folders, and organizations).
bigquery.connections.get
bigquery.connections.getIamPolicy
bigquery.connections.list
bigquery.connections.use
BigQuery Data Editor
(roles/bigquery.dataEditor)
When granted on a dataset, this role grants these permissions:
Get metadata and permissions for the dataset.
For tables and views:
Create, update, get, list, and delete the dataset's tables and views.
Read (query), export, replicate, and update table data.
Create, update, and delete indexes.
Create and restore snapshots.
All permissions for the dataset's routines and models.
Note: Principals that are granted the Data Editor role at the project level can also create new datasets and list datasets in the project that they have access to.
When granted on a table or view, this role grants these permissions:
Get metadata, update metadata, get access controls, and delete the table or view.
Get (query), export, replicate, and update table data.
Create, update, and delete indexes.
Create and restore snapshots.
All permissions for the routine.
The Data Editor role cannot be granted to individual models.
Note: The BigQuery Data Editor role is mapped to the WRITER BigQuery basic role. When you grant the BigQuery Data Editor role to a principal at the dataset level, the principal is granted WRITER access to the dataset.
Lowest-level resources where you can grant this role:
Dataset
These resources within a dataset:
Table
View
Routine
This role can also be granted on Resource Manager resources (projects, folders, and organizations).
bigquery.config.get
bigquery.datasets.create
bigquery.datasets.get
bigquery.datasets.getIamPolicy
bigquery.datasets.updateTag
bigquery.models.*
bigquery.routines.*
bigquery.tables.create
bigquery.tables.createIndex
bigquery.tables.createSnapshot
bigquery.tables.delete
bigquery.tables.deleteIndex
bigquery.tables.export
bigquery.tables.get
bigquery.tables.getData
bigquery.tables.getIamPolicy
bigquery.tables.list
bigquery.tables.replicateData
bigquery.tables.restoreSnapshot
bigquery.tables.update
bigquery.tables.updateData
bigquery.tables.updateIndex
bigquery.tables.updateTag
cloudkms.keyHandles.*
cloudkms.operations.get
cloudkms.projects.showEffectiveAutokeyConfig
dataplex.datascans.create
dataplex.datascans.delete
dataplex.datascans.get
dataplex.datascans.getData
dataplex.datascans.getIamPolicy
dataplex.datascans.list
dataplex.datascans.run
dataplex.datascans.update
dataplex.operations.get
dataplex.operations.list
resourcemanager.projects.get
resourcemanager.projects.list
BigQuery Data Owner
(roles/bigquery.dataOwner)
When granted on a dataset, this role grants these permissions:
All permissions for the dataset and for all of the resources within the dataset: tables and views, models, and routines.
Note: Principals that are granted the Data Owner role at the project level can also create new datasets and list datasets in the project that they have access to.
When granted on a table or view, this role grants these permissions:
All permissions for the table or view.
All permissions for row access policies except permission to override time travel restrictions.
Set categories and column-level data policies.
When granted on a routine, this role grants these permissions:
All permissions for the routine.
You shouldn't grant the Data Owner role at the routine level. Data Editor also grants all permissions for the routine and is a less permissive role.
This role cannot be granted to individual models.
Note: The BigQuery Data Owner role is mapped to the OWNER BigQuery basic role. When you grant the BigQuery Data Owner role to a principal at the dataset level, the principal is granted OWNER access to the dataset.
Lowest-level resources where you can grant this role:
Dataset
These resources within a dataset:
Table
View
Routine
This role can also be granted on Resource Manager resources (projects, folders, and organizations).
bigquery.config.get
bigquery.dataPolicies.attach
bigquery.dataPolicies.create
bigquery.dataPolicies.delete
bigquery.dataPolicies.get
bigquery.dataPolicies.getIamPolicy
bigquery.dataPolicies.list
bigquery.dataPolicies.setIamPolicy
bigquery.dataPolicies.update
bigquery.datasets.*
bigquery.models.*
bigquery.routines.*
bigquery.rowAccessPolicies.create
bigquery.rowAccessPolicies.delete
bigquery.rowAccessPolicies.get
bigquery.rowAccessPolicies.getIamPolicy
bigquery.rowAccessPolicies.list
bigquery.rowAccessPolicies.setIamPolicy
bigquery.rowAccessPolicies.update
bigquery.tables.*
cloudkms.keyHandles.*
cloudkms.operations.get
cloudkms.projects.showEffectiveAutokeyConfig
dataplex.datascans.*
dataplex.operations.get
dataplex.operations.list
resourcemanager.projects.get
resourcemanager.projects.list
BigQuery Data Viewer
(roles/bigquery.dataViewer)
When granted on a dataset, this role grants these permissions:
Get metadata and permissions for the dataset.
List a dataset's tables, views, and models.
Get metadata and access controls for the dataset's tables and views.
Get (query), replicate, and export table data and create snapshots.
List and invoke the dataset's routines.
When granted on a table or view, this role provides these permissions:
Get metadata and access controls for the table or view.
Get (query), export, and replicate table data.
Create snapshots.
When granted on a routine, this role grants these permissions:
In a query, reference a routine created by someone else.
This role cannot be granted to individual models.
Note: The BigQuery Data Viewer role is mapped to the READER BigQuery basic role. When you grant the BigQuery Data Viewer role to a principal at the dataset level, the principal is granted READER access to the dataset.
Lowest-level resources where you can grant this role:
Dataset
These resources within a dataset:
Table
View
Routine
This role can also be granted on Resource Manager resources (projects, folders, and organizations).
bigquery.datasets.get
bigquery.datasets.getIamPolicy
bigquery.models.export
bigquery.models.getData
bigquery.models.getMetadata
bigquery.models.list
bigquery.routines.get
bigquery.routines.list
bigquery.tables.createSnapshot
bigquery.tables.export
bigquery.tables.get
bigquery.tables.getData
bigquery.tables.getIamPolicy
bigquery.tables.list
bigquery.tables.replicateData
dataplex.datascans.get
dataplex.datascans.getData
dataplex.datascans.getIamPolicy
dataplex.datascans.list
resourcemanager.projects.get
resourcemanager.projects.list
BigQuery Filtered Data Viewer
(roles/bigquery.filteredDataViewer)
Access to view filtered table data defined by a row access policy. bigquery.filteredDataViewer is a system-managed role. Grant the role by using row-level access policies. Don't apply the role directly to a resource through Identity and Access Management (IAM).
bigquery.rowAccessPolicies.getFilteredData
BigQuery Job User
(roles/bigquery.jobUser)
Provides permissions to run jobs, including queries, within the project.
This role can only be granted on Resource Manager resources (projects, folders, and organizations).
bigquery.config.get
bigquery.jobs.create
dataform.folders.create
dataform.locations.*
dataform.repositories.create
dataform.repositories.list
resourcemanager.projects.get
resourcemanager.projects.list
BigQuery Metadata Viewer
(roles/bigquery.metadataViewer)
When granted on a dataset, this role grants these permissions:
Get metadata and access controls for the dataset.
Get metadata and access controls for tables and views.
Get metadata from the dataset's models and routines.
List tables, views, models, and routines in the dataset.
When granted on a table or view, this role provides these permissions:
Get metadata and access controls for the table or view.
When granted on a routine, this role grants these permissions:
In a query, reference a routine created by someone else.
This role cannot be granted to individual models.
Lowest-level resources where you can grant this role:
Dataset
These resources within a dataset:
Table
View
Routine
This role can also be granted on Resource Manager resources (projects, folders, and organizations).
bigquery.datasets.get
bigquery.datasets.getIamPolicy
bigquery.models.getMetadata
bigquery.models.list
bigquery.routines.get
bigquery.routines.list
bigquery.tables.get
bigquery.tables.getIamPolicy
bigquery.tables.list
dataplex.projects.search
resourcemanager.projects.get
resourcemanager.projects.list
BigQuery ObjectRef Admin
(roles/bigquery.objectRefAdmin)
Administer ObjectRef resources that includes read and write permissions
Lowest-level resources where you can grant this role:
Connection
This role can also be granted on Resource Manager resources (projects, folders, and organizations).
bigquery.objectRefs.*
BigQuery ObjectRef Reader
(roles/bigquery.objectRefReader)
Role for reading referenced objects via ObjectRefs in BigQuery
Lowest-level resources where you can grant this role:
Connection
This role can also be granted on Resource Manager resources (projects, folders, and organizations).
bigquery.objectRefs.read
BigQuery Read Session User
(roles/bigquery.readSessionUser)
Provides the ability to create and use read sessions.
This role can only be granted on Resource Manager resources (projects, folders, and organizations).
bigquery.readsessions.*
resourcemanager.projects.get
resourcemanager.projects.list
BigQuery Resource Admin
(roles/bigquery.resourceAdmin)
Administers BigQuery workloads, including slot assignments, commitments, and reservations.
This role can only be granted on Resource Manager resources (projects, folders, and organizations).
bigquery.bireservations.*
bigquery.capacityCommitments.*
bigquery.jobs.get
bigquery.jobs.list
bigquery.jobs.listAll
bigquery.jobs.listExecutionMetadata
bigquery.reservationAssignments.*
bigquery.reservationGroups.*
bigquery.reservations.*
recommender.bigqueryCapacityCommitmentsInsights.*
recommender.bigqueryCapacityCommitmentsRecommendations.*
resourcemanager.projects.get
resourcemanager.projects.list
BigQuery Resource Editor
(roles/bigquery.resourceEditor)
Manages BigQuery workloads, but is unable to create or modify slot commitments.
This role can only be granted on Resource Manager resources (projects, folders, and organizations).
bigquery.bireservations.get
bigquery.capacityCommitments.get
bigquery.capacityCommitments.list
bigquery.jobs.get
bigquery.jobs.list
bigquery.jobs.listAll
bigquery.jobs.listExecutionMetadata
bigquery.reservationAssignments.*
bigquery.reservationGroups.*
bigquery.reservations.create
bigquery.reservations.delete
bigquery.reservations.get
bigquery.reservations.list
bigquery.reservations.listFailoverDatasets
bigquery.reservations.update
bigquery.reservations.use
resourcemanager.projects.get
resourcemanager.projects.list
BigQuery Resource Viewer
(roles/bigquery.resourceViewer)
Can view BigQuery workloads, but cannot create or modify slot reservations or commitments.
This role can only be granted on Resource Manager resources (projects, folders, and organizations).
bigquery.bireservations.get
bigquery.capacityCommitments.get
bigquery.capacityCommitments.list
bigquery.jobs.get
bigquery.jobs.list
bigquery.jobs.listAll
bigquery.jobs.listExecutionMetadata
bigquery.reservationAssignments.list
bigquery.reservationAssignments.search
bigquery.reservationGroups.get
bigquery.reservationGroups.list
bigquery.reservations.get
bigquery.reservations.list
bigquery.reservations.listFailoverDatasets
resourcemanager.projects.get
resourcemanager.projects.list
BigQuery Authorized Routine Admin Beta
(roles/bigquery.routineAdmin)
Role for Authorized Routine to administer supported resources
bigquery.connections.use
bigquery.datasets.get
bigquery.models.getData
bigquery.models.getMetadata
bigquery.routines.get
bigquery.routines.list
bigquery.tables.create
bigquery.tables.delete
bigquery.tables.get
bigquery.tables.getData
bigquery.tables.list
bigquery.tables.update
bigquery.tables.updateData
BigQuery Authorized Routine Data Editor Beta
(roles/bigquery.routineDataEditor)
Role for Authorized Routine to edit contents of supported resources
bigquery.datasets.get
bigquery.models.getData
bigquery.models.getMetadata
bigquery.routines.get
bigquery.routines.list
bigquery.tables.create
bigquery.tables.delete
bigquery.tables.get
bigquery.tables.getData
bigquery.tables.list
bigquery.tables.update
bigquery.tables.updateData
BigQuery Authorized Routine Data Viewer Beta
(roles/bigquery.routineDataViewer)
Role for Authorized Routine to view data and contents of supported resources
bigquery.datasets.get
bigquery.models.getData
bigquery.models.getMetadata
bigquery.routines.get
bigquery.routines.list
bigquery.tables.get
bigquery.tables.getData
bigquery.tables.list
BigQuery Authorized Routine Metadata Viewer Beta
(roles/bigquery.routineMetadataViewer)
Role for Authorized Routine to view metadata of supported resources
bigquery.datasets.get
bigquery.models.getMetadata
bigquery.routines.get
bigquery.routines.list
bigquery.tables.get
bigquery.tables.list
BigQuery Security Admin Beta
(roles/bigquery.securityAdmin)
Administer all BigQuery security controls
bigquery.dataPolicies.attach
bigquery.dataPolicies.create
bigquery.dataPolicies.delete
bigquery.dataPolicies.get
bigquery.dataPolicies.getIamPolicy
bigquery.dataPolicies.list
bigquery.dataPolicies.setIamPolicy
bigquery.dataPolicies.update
bigquery.datasets.createTagBinding
bigquery.datasets.deleteTagBinding
bigquery.datasets.get
bigquery.datasets.getIamPolicy
bigquery.datasets.listEffectiveTags
bigquery.datasets.listSharedDatasetUsage
bigquery.datasets.listTagBindings
bigquery.datasets.setIamPolicy
bigquery.datasets.update
bigquery.datasets.updateTag
bigquery.rowAccessPolicies.create
bigquery.rowAccessPolicies.delete
bigquery.rowAccessPolicies.get
bigquery.rowAccessPolicies.getIamPolicy
bigquery.rowAccessPolicies.list
bigquery.rowAccessPolicies.setIamPolicy
bigquery.rowAccessPolicies.update
bigquery.tables.createTagBinding
bigquery.tables.deleteTagBinding
bigquery.tables.get
bigquery.tables.getIamPolicy
bigquery.tables.list
bigquery.tables.listEffectiveTags
bigquery.tables.listTagBindings
bigquery.tables.setColumnDataPolicy
bigquery.tables.setIamPolicy
bigquery.tables.update
bigquery.tables.updateTag
dataplex.projects.search
BigQuery Studio Admin
(roles/bigquery.studioAdmin)
Combination role of BigQuery Admin, Dataform Admin, Notebook Runtime Admin and Dataproc Serverless Editor.
It is possible to grant this role to the following lowest-level resources, but it is not recommended. Other predefined roles grant full permissions over these resources and are less permissive. BigQuery Studio Admin is typically granted at the project level.
Lowest-level resources where you can grant this role:
Dataset
These resources within a dataset:
Table
View
Routine
Connection
Saved query
Data canvas
Data preparation
Pipeline
Repository
This role can also be granted on Resource Manager resources (projects, folders, and organizations).
aiplatform.locations.get
aiplatform.notebookRuntimeTemplates.*
aiplatform.notebookRuntimes.*
aiplatform.operations.list
bigquery.bireservations.*
bigquery.capacityCommitments.*
bigquery.config.*
bigquery.connections.*
bigquery.dataPolicies.attach
bigquery.dataPolicies.create
bigquery.dataPolicies.delete
bigquery.dataPolicies.get
bigquery.dataPolicies.getIamPolicy
bigquery.dataPolicies.list
bigquery.dataPolicies.setIamPolicy
bigquery.dataPolicies.update
bigquery.datasets.*
bigquery.jobs.*
bigquery.models.*
bigquery.objectRefs.*
bigquery.readsessions.*
bigquery.reservationAssignments.*
bigquery.reservationGroups.*
bigquery.reservations.*
bigquery.routines.*
bigquery.rowAccessPolicies.create
bigquery.rowAccessPolicies.delete
bigquery.rowAccessPolicies.get
bigquery.rowAccessPolicies.getIamPolicy
bigquery.rowAccessPolicies.list
bigquery.rowAccessPolicies.overrideTimeTravelRestrictions
bigquery.rowAccessPolicies.setIamPolicy
bigquery.rowAccessPolicies.update
bigquery.savedqueries.*
bigquery.tables.*
bigquery.transfers.*
bigquerymigration.translation.translate
cloudaicompanion.aiDevToolsSettings.*
cloudaicompanion.codeToolsSettings.*
cloudaicompanion.companions.*
cloudaicompanion.dataSharingWithGoogleSettings.*
cloudaicompanion.entitlements.get
cloudaicompanion.geminiGcpEnablementSettings.*
cloudaicompanion.instances.*
cloudaicompanion.licenses.selfAssign
cloudaicompanion.loggingSettings.*
cloudaicompanion.operations.get
cloudaicompanion.releaseChannelSettings.*
cloudaicompanion.settingBindings.*
cloudaicompanion.topics.create
cloudkms.keyHandles.*
cloudkms.operations.get
cloudkms.projects.showEffectiveAutokeyConfig
compute.projects.get
compute.regions.*
compute.reservations.get
compute.reservations.list
compute.zones.*
dataform.*
dataplex.datascans.*
dataplex.operations.get
dataplex.operations.list
dataplex.projects.search
dataproc.batches.*
dataproc.operations.cancel
dataproc.operations.delete
dataproc.operations.get
dataproc.operations.list
dataproc.sessionTemplates.*
dataproc.sessions.*
dataprocrm.nodePools.*
dataprocrm.nodes.get
dataprocrm.nodes.heartbeat
dataprocrm.nodes.list
dataprocrm.nodes.update
dataprocrm.operations.get
dataprocrm.operations.list
dataprocrm.workloads.*
geminidataanalytics.locations.useDataEngineeringAgent
resourcemanager.projects.get
resourcemanager.projects.list
BigQuery Studio User
(roles/bigquery.studioUser)
Combination role of BigQuery Job User, BigQuery Read Session User, Dataform Code Creator, Notebook Runtime User and Dataproc Serverless Editor.
Lowest-level resources where you can grant this role:
Saved query
Data canvas
Data preparation
Pipeline
Repository
This role can also be granted on Resource Manager resources (projects, folders, and organizations).
aiplatform.locations.get
aiplatform.notebookRuntimeTemplates.apply
aiplatform.notebookRuntimeTemplates.get
aiplatform.notebookRuntimeTemplates.getIamPolicy
aiplatform.notebookRuntimeTemplates.list
aiplatform.notebookRuntimes.assign
aiplatform.notebookRuntimes.get
aiplatform.notebookRuntimes.list
aiplatform.operations.list
bigquery.config.get
bigquery.jobs.create
bigquery.readsessions.*
cloudaicompanion.companions.*
cloudaicompanion.entitlements.get
cloudaicompanion.instances.*
cloudaicompanion.licenses.selfAssign
cloudaicompanion.operations.get
cloudaicompanion.topics.create
cloudkms.keyHandles.*
cloudkms.operations.get
cloudkms.projects.showEffectiveAutokeyConfig
compute.projects.get
compute.regions.*
compute.zones.*
dataform.commentThreads.get
dataform.commentThreads.list
dataform.comments.get
dataform.comments.list
dataform.folders.create
dataform.locations.*
dataform.repositories.create
dataform.repositories.list
dataplex.projects.search
dataproc.batches.*
dataproc.operations.cancel
dataproc.operations.delete
dataproc.operations.get
dataproc.operations.list
dataproc.sessionTemplates.*
dataproc.sessions.*
dataprocrm.nodePools.*
dataprocrm.nodes.get
dataprocrm.nodes.heartbeat
dataprocrm.nodes.list
dataprocrm.nodes.update
dataprocrm.operations.get
dataprocrm.operations.list
dataprocrm.workloads.*
geminidataanalytics.locations.useDataEngineeringAgent
resourcemanager.projects.get
resourcemanager.projects.list
BigQuery User
(roles/bigquery.user)
When granted on a dataset, this role provides the ability to read the dataset's metadata and list tables in the dataset.
When granted on a project, this role also provides the ability to run jobs, including queries, within the project. A principal with this role can enumerate their own jobs, cancel their own jobs, and enumerate datasets within a project. Additionally, allows the creation of new datasets within the project; the creator is granted the BigQuery Data Owner role (roles/bigquery.dataOwner) on these new datasets.
Lowest-level resources where you can grant this role:
Dataset
These resources within a dataset:
Routine
This role can also be granted on Resource Manager resources (projects, folders, and organizations).
bigquery.bireservations.get
bigquery.capacityCommitments.get
bigquery.capacityCommitments.list
bigquery.config.get
bigquery.datasets.create
bigquery.datasets.get
bigquery.datasets.getIamPolicy
bigquery.jobs.create
bigquery.jobs.list
bigquery.models.list
bigquery.readsessions.*
bigquery.reservationAssignments.list
bigquery.reservationAssignments.search
bigquery.reservationGroups.get
bigquery.reservationGroups.list
bigquery.reservations.get
bigquery.reservations.list
bigquery.reservations.listFailoverDatasets
bigquery.reservations.use
bigquery.routines.list
bigquery.savedqueries.get
bigquery.savedqueries.list
bigquery.tables.list
bigquery.transfers.get
bigquerymigration.translation.translate
cloudkms.keyHandles.*
cloudkms.operations.get
cloudkms.projects.showEffectiveAutokeyConfig
dataform.folders.create
dataform.locations.*
dataform.repositories.create
dataform.repositories.list
dataplex.projects.search
resourcemanager.projects.get
resourcemanager.projects.list
BigQuery Connection API roles
This table lists the predefined IAM roles and permissions for BigQuery Connection API. To search through all roles and permissions, see the role and permission index.
Role Permissions
BigQuery Connection Service Agent
(roles/bigqueryconnection.serviceAgent)
Gives BigQuery Connection Service access to Cloud SQL instances in user projects.
Warning: Do not grant service agent roles to any principals except service agents.
cloudsql.instances.connect
cloudsql.instances.get
logging.logEntries.create
logging.logEntries.route
monitoring.metricDescriptors.create
monitoring.metricDescriptors.get
monitoring.metricDescriptors.list
monitoring.monitoredResourceDescriptors.*
monitoring.timeSeries.create
telemetry.metrics.write
BigQuery Continuous Query roles
This table lists the predefined IAM roles and permissions for BigQuery Continuous Query. To search through all roles and permissions, see the role and permission index.
Role Permissions
BigQuery Continuous Query Service Agent
(roles/bigquerycontinuousquery.serviceAgent)
Gives BigQuery Continuous Query access to the service accounts in the user project.
Warning: Do not grant service agent roles to any principals except service agents.
iam.serviceAccounts.getAccessToken
BigQuery Data Policy roles
This table lists the predefined IAM roles and permissions for BigQuery Data Policy. To search through all roles and permissions, see the role and permission index.
Role Permissions
BigQuery Data Policy Admin
(roles/bigquerydatapolicy.admin)
Role for managing Data Policies in BigQuery
This role can only be granted on Resource Manager resources (projects, folders, and organizations).
bigquery.dataPolicies.attach
bigquery.dataPolicies.create
bigquery.dataPolicies.delete
bigquery.dataPolicies.get
bigquery.dataPolicies.getIamPolicy
bigquery.dataPolicies.list
bigquery.dataPolicies.setIamPolicy
bigquery.dataPolicies.update
Bigquerydatapolicy Editor
(roles/bigquerydatapolicy.editor)
Editor role for bigquerydatapolicy
bigquery.bireservations.*
bigquery.capacityCommitments.get
bigquery.capacityCommitments.list
bigquery.capacityCommitments.update
bigquery.config.*
bigquery.connections.create
bigquery.connections.delete
bigquery.connections.get
bigquery.connections.getIamPolicy
bigquery.connections.list
bigquery.connections.update
bigquery.connections.updateTag
bigquery.connections.use
bigquery.dataPolicies.attach
bigquery.dataPolicies.create
bigquery.dataPolicies.delete
bigquery.dataPolicies.get
bigquery.dataPolicies.getIamPolicy
bigquery.dataPolicies.list
bigquery.dataPolicies.update
bigquery.datasets.create
bigquery.datasets.get
bigquery.datasets.getIamPolicy
bigquery.datasets.listEffectiveTags
bigquery.datasets.listTagBindings
bigquery.datasets.updateTag
bigquery.jobs.create
bigquery.jobs.createGlobalQuery
bigquery.jobs.delete
bigquery.jobs.get
bigquery.jobs.list
bigquery.jobs.listExecutionMetadata
bigquery.models.*
bigquery.objectRefs.*
bigquery.readsessions.*
bigquery.reservationAssignments.*
bigquery.reservationGroups.*
bigquery.reservations.create
bigquery.reservations.delete
bigquery.reservations.get
bigquery.reservations.getIamPolicy
bigquery.reservations.list
bigquery.reservations.listFailoverDatasets
bigquery.reservations.update
bigquery.reservations.use
bigquery.routines.*
bigquery.rowAccessPolicies.create
bigquery.rowAccessPolicies.delete
bigquery.rowAccessPolicies.get
bigquery.rowAccessPolicies.getIamPolicy
bigquery.rowAccessPolicies.list
bigquery.rowAccessPolicies.update
bigquery.savedqueries.*
bigquery.tables.createIndex
bigquery.tables.createSnapshot
bigquery.tables.deleteIndex
bigquery.tables.getIamPolicy
bigquery.tables.listEffectiveTags
bigquery.tables.listTagBindings
bigquery.tables.replicateData
bigquery.tables.restoreSnapshot
bigquery.tables.updateIndex
bigquery.transfers.*
resourcemanager.projects.get
resourcemanager.projects.list
Masked Reader
(roles/bigquerydatapolicy.maskedReader)
Masked read access to sub-resources tagged by the policy tag associated with a data policy, for example, BigQuery columns
This role can only be granted on Resource Manager resources (projects, folders, and organizations).
bigquery.dataPolicies.maskedGet
Raw Data Reader Beta
(roles/bigquerydatapolicy.rawDataReader)
Raw read access to sub-resources associated with a data policy, for example, BigQuery columns
This role can only be granted on Resource Manager resources (projects, folders, and organizations).
bigquery.dataPolicies.getRawData
BigQuery Data Policy Viewer
(roles/bigquerydatapolicy.viewer)
Role for viewing Data Policies in BigQuery
This role can only be granted on Resource Manager resources (projects, folders, and organizations).
bigquery.dataPolicies.get
bigquery.dataPolicies.list
BigQuery Data Transfer Service roles
This table lists the predefined IAM roles and permissions for BigQuery Data Transfer Service. To search through all roles and permissions, see the role and permission index.
Role Permissions
BigQuery Data Transfer Service Agent
(roles/bigquerydatatransfer.serviceAgent)
Gives BigQuery Data Transfer Service access to start BigQuery jobs in consumer project.
Warning: Do not grant service agent roles to any principals except service agents.
bigquery.config.get
bigquery.connections.delegate
bigquery.jobs.create
compute.networkAttachments.get
compute.networkAttachments.update
compute.regionOperations.get
compute.subnetworks.use
dataform.folders.create
dataform.locations.*
dataform.repositories.create
dataform.repositories.list
iam.serviceAccounts.getAccessToken
logging.logEntries.create
logging.logEntries.route
resourcemanager.projects.get
resourcemanager.projects.list
serviceusage.services.use
BigQuery Engine for Apache Flink roles
This table lists the predefined IAM roles and permissions for BigQuery Engine for Apache Flink. To search through all roles and permissions, see the role and permission index.
Role Permissions
Managed Flink Admin Beta
(roles/managedflink.admin)
Full access to Managed Flink resources.
managedflink.*
resourcemanager.projects.get
resourcemanager.projects.list
Managed Flink Developer Beta
(roles/managedflink.developer)
Full access to Managed Flink Jobs and Sessions and read access to Deployments.
managedflink.deployments.get
managedflink.deployments.list
managedflink.jobs.*
managedflink.locations.*
managedflink.operations.get
managedflink.operations.list
managedflink.sessions.*
resourcemanager.projects.get
resourcemanager.projects.list
Managed Flink Service Agent
(roles/managedflink.serviceAgent)
Gives Managed Flink Service Agent access to Cloud Platform resources.
Warning: Do not grant service agent roles to any principals except service agents.
compute.networkAttachments.create
compute.networkAttachments.delete
compute.networkAttachments.get
compute.networkAttachments.list
compute.networkAttachments.update
compute.networks.get
compute.networks.list
compute.regionOperations.get
compute.subnetworks.get
compute.subnetworks.list
compute.subnetworks.use
dns.networks.targetWithPeeringZone
managedkafka.clusters.get
managedkafka.clusters.list
managedkafka.clusters.update
monitoring.metricDescriptors.create
monitoring.metricDescriptors.get
monitoring.metricDescriptors.list
monitoring.monitoredResourceDescriptors.*
monitoring.timeSeries.create
serviceusage.services.use
storage.objects.get
Managed Flink Viewer Beta
(roles/managedflink.viewer)
Readonly access to Managed Flink resources.
managedflink.deployments.get
managedflink.deployments.list
managedflink.jobs.get
managedflink.jobs.list
managedflink.locations.*
managedflink.operations.get
managedflink.operations.list
managedflink.sessions.get
managedflink.sessions.list
resourcemanager.projects.get
resourcemanager.projects.list
BigQuery Migration Service roles
This table lists the predefined IAM roles and permissions for BigQuery Migration Service. To search through all roles and permissions, see the role and permission index.
Role Permissions
Bigquerymigration Admin
(roles/bigquerymigration.admin)
Admin role for bigquerymigration
bigquerymigration.*
resourcemanager.projects.get
resourcemanager.projects.list
MigrationWorkflow Editor
(roles/bigquerymigration.editor)
Editor of EDW migration workflows.
bigquerymigration.subtasks.*
bigquerymigration.workflows.create
bigquerymigration.workflows.delete
bigquerymigration.workflows.enableAiOutputTypes
bigquerymigration.workflows.enableLineageOutputTypes
bigquerymigration.workflows.enableOutputTypePermissions
bigquerymigration.workflows.get
bigquerymigration.workflows.list
bigquerymigration.workflows.update
Task Orchestrator
(roles/bigquerymigration.orchestrator)
Orchestrator of EDW migration tasks.
bigquerymigration.workflows.orchestrateTask
storage.objects.list
Migration Translation User
(roles/bigquerymigration.translationUser)
User of EDW migration interactive SQL translation service.
bigquerymigration.translation.translate
MigrationWorkflow Viewer
(roles/bigquerymigration.viewer)
Viewer of EDW migration MigrationWorkflow.
bigquerymigration.subtasks.*
bigquerymigration.workflows.get
bigquerymigration.workflows.list
Task Worker
(roles/bigquerymigration.worker)
Worker that executes EDW migration subtasks.
storage.objects.create
storage.objects.get
storage.objects.list
BigQuery Omni roles
This table lists the predefined IAM roles and permissions for BigQuery Omni. To search through all roles and permissions, see the role and permission index.
Role Permissions
BigQuery Omni Service Agent
(roles/bigqueryomni.serviceAgent)
Gives BigQuery Omni access to tables in user projects.
Warning: Do not grant service agent roles to any principals except service agents.
bigquery.jobs.create
bigquery.tables.updateData
BigQuery sharing roles
This table lists the predefined IAM roles and permissions for BigQuery sharing. To search through all roles and permissions, see the role and permission index.
Role Permissions
Analytics Hub Admin
(roles/analyticshub.admin)
Administer Data Exchanges and Listings
analyticshub.dataExchanges.create
analyticshub.dataExchanges.delete
analyticshub.dataExchanges.get
analyticshub.dataExchanges.getIamPolicy
analyticshub.dataExchanges.list
analyticshub.dataExchanges.setIamPolicy
analyticshub.dataExchanges.update
analyticshub.dataExchanges.viewSubscriptions
analyticshub.listings.create
analyticshub.listings.delete
analyticshub.listings.get
analyticshub.listings.getIamPolicy
analyticshub.listings.list
analyticshub.listings.setIamPolicy
analyticshub.listings.update
analyticshub.listings.viewSubscriptions
analyticshub.subscriptions.*
resourcemanager.projects.get
resourcemanager.projects.list
Analyticshub Editor
(roles/analyticshub.editor)
Editor role for analyticshub
analyticshub.dataExchanges.create
analyticshub.dataExchanges.delete
analyticshub.dataExchanges.get
analyticshub.dataExchanges.getIamPolicy
analyticshub.dataExchanges.list
analyticshub.dataExchanges.update
analyticshub.listings.create
analyticshub.listings.delete
analyticshub.listings.get
analyticshub.listings.getIamPolicy
analyticshub.listings.list
analyticshub.listings.update
analyticshub.subscriptions.*
resourcemanager.projects.get
resourcemanager.projects.list
Analytics Hub Listing Admin
(roles/analyticshub.listingAdmin)
Grants full control over the Listing, including updating, deleting and setting ACLs
analyticshub.dataExchanges.get
analyticshub.dataExchanges.getIamPolicy
analyticshub.dataExchanges.list
analyticshub.listings.delete
analyticshub.listings.get
analyticshub.listings.getIamPolicy
analyticshub.listings.list
analyticshub.listings.setIamPolicy
analyticshub.listings.update
analyticshub.listings.viewSubscriptions
resourcemanager.projects.get
resourcemanager.projects.list
Analytics Hub Publisher
(roles/analyticshub.publisher)
Can publish to Data Exchanges thus creating Listings
analyticshub.dataExchanges.get
analyticshub.dataExchanges.getIamPolicy
analyticshub.dataExchanges.list
analyticshub.listings.create
analyticshub.listings.get
analyticshub.listings.getIamPolicy
analyticshub.listings.list
resourcemanager.projects.get
resourcemanager.projects.list
Analytics Hub Subscriber
(roles/analyticshub.subscriber)
Can browse Data Exchanges and subscribe to Listings
analyticshub.dataExchanges.get
analyticshub.dataExchanges.getIamPolicy
analyticshub.dataExchanges.list
analyticshub.dataExchanges.subscribe
analyticshub.listings.get
analyticshub.listings.getIamPolicy
analyticshub.listings.list
analyticshub.listings.subscribe
resourcemanager.projects.get
resourcemanager.projects.list
Analytics Hub Subscription Owner
(roles/analyticshub.subscriptionOwner)
Grants full control over the Subscription, including updating and deleting
analyticshub.dataExchanges.get
analyticshub.dataExchanges.getIamPolicy
analyticshub.dataExchanges.list
analyticshub.listings.get
analyticshub.listings.getIamPolicy
analyticshub.listings.list
analyticshub.subscriptions.*
resourcemanager.projects.get
resourcemanager.projects.list
Analytics Hub Viewer
(roles/analyticshub.viewer)
Can browse Data Exchanges and Listings
analyticshub.dataExchanges.get
analyticshub.dataExchanges.getIamPolicy
analyticshub.dataExchanges.list
analyticshub.listings.get
analyticshub.listings.getIamPolicy
analyticshub.listings.list
resourcemanager.projects.get
resourcemanager.projects.list
BigQuery permissions
The following tables list the permissions available in BigQuery. These are included in predefined roles and can be used in custom role definitions. To search through all roles and permissions, see the role and permission index.
BigQuery permissions
This table lists the IAM permissions for BigQuery and the roles that include them. To search through all roles and permissions, see the role and permission index.
Permission Included in roles
bigquery.bireservations.get
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Resource Admin (roles/bigquery.resourceAdmin)
BigQuery Resource Editor (roles/bigquery.resourceEditor)
BigQuery Resource Viewer (roles/bigquery.resourceViewer)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
BigQuery User (roles/bigquery.user)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Databases Admin (roles/iam.databasesAdmin)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.bireservations.update
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Resource Admin (roles/bigquery.resourceAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Databases Admin (roles/iam.databasesAdmin)
Service agent roles
bigquery.capacityCommitments.create
Owner (roles/owner)
BigQuery Admin (roles/bigquery.admin)
BigQuery Resource Admin (roles/bigquery.resourceAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Databases Admin (roles/iam.databasesAdmin)
Service agent roles
bigquery.capacityCommitments.delete
Owner (roles/owner)
BigQuery Admin (roles/bigquery.admin)
BigQuery Resource Admin (roles/bigquery.resourceAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Databases Admin (roles/iam.databasesAdmin)
Service agent roles
bigquery.capacityCommitments.get
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Resource Admin (roles/bigquery.resourceAdmin)
BigQuery Resource Editor (roles/bigquery.resourceEditor)
BigQuery Resource Viewer (roles/bigquery.resourceViewer)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
BigQuery User (roles/bigquery.user)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Databases Admin (roles/iam.databasesAdmin)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.capacityCommitments.list
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Resource Admin (roles/bigquery.resourceAdmin)
BigQuery Resource Editor (roles/bigquery.resourceEditor)
BigQuery Resource Viewer (roles/bigquery.resourceViewer)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
BigQuery User (roles/bigquery.user)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Databases Admin (roles/iam.databasesAdmin)
Security Admin (roles/iam.securityAdmin)
Security Auditor (roles/iam.securityAuditor)
Security Reviewer (roles/iam.securityReviewer)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.capacityCommitments.update
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Resource Admin (roles/bigquery.resourceAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Databases Admin (roles/iam.databasesAdmin)
Service agent roles
bigquery.config.get
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Editor (roles/bigquery.dataEditor)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Job User (roles/bigquery.jobUser)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
BigQuery Studio User (roles/bigquery.studioUser)
BigQuery User (roles/bigquery.user)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Data Scientist (roles/iam.dataScientist)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.config.update
Owner (roles/owner)
Editor (roles/editor)
Assured Workloads Administrator (roles/assuredworkloads.admin)
Assured Workloads Editor (roles/assuredworkloads.editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Databases Admin (roles/iam.databasesAdmin)
Service agent roles
bigquery.connections.create
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Connection Admin (roles/bigquery.connectionAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Databases Admin (roles/iam.databasesAdmin)
Service agent roles
bigquery.connections.delegate
Owner (roles/owner)
BigQuery Admin (roles/bigquery.admin)
BigQuery Connection Admin (roles/bigquery.connectionAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Datastream Bigquery Writer (roles/datastream.bigqueryWriter)
Databases Admin (roles/iam.databasesAdmin)
Service agent roles
bigquery.connections.delete
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Connection Admin (roles/bigquery.connectionAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Databases Admin (roles/iam.databasesAdmin)
Service agent roles
bigquery.connections.get
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Connection Admin (roles/bigquery.connectionAdmin)
BigQuery Connection User (roles/bigquery.connectionUser)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Data Catalog Admin (roles/datacatalog.admin)
Datacatalog Editor (roles/datacatalog.editor)
Data Catalog Viewer (roles/datacatalog.viewer)
Datastream Bigquery Writer (roles/datastream.bigqueryWriter)
Databases Admin (roles/iam.databasesAdmin)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.connections.getIamPolicy
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Connection Admin (roles/bigquery.connectionAdmin)
BigQuery Connection User (roles/bigquery.connectionUser)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Databases Admin (roles/iam.databasesAdmin)
Security Admin (roles/iam.securityAdmin)
Security Auditor (roles/iam.securityAuditor)
Security Reviewer (roles/iam.securityReviewer)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.connections.list
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Connection Admin (roles/bigquery.connectionAdmin)
BigQuery Connection User (roles/bigquery.connectionUser)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Databases Admin (roles/iam.databasesAdmin)
Security Admin (roles/iam.securityAdmin)
Security Auditor (roles/iam.securityAuditor)
Security Reviewer (roles/iam.securityReviewer)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.connections.setIamPolicy
Owner (roles/owner)
BigQuery Admin (roles/bigquery.admin)
BigQuery Connection Admin (roles/bigquery.connectionAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Databases Admin (roles/iam.databasesAdmin)
Security Admin (roles/iam.securityAdmin)
Service agent roles
bigquery.connections.update
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Connection Admin (roles/bigquery.connectionAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Databases Admin (roles/iam.databasesAdmin)
Service agent roles
bigquery.connections.updateTag
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Connection Admin (roles/bigquery.connectionAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Data Catalog Admin (roles/datacatalog.admin)
Data Catalog Tag Editor (roles/datacatalog.tagEditor)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Databases Admin (roles/iam.databasesAdmin)
Service agent roles
bigquery.connections.use
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Connection Admin (roles/bigquery.connectionAdmin)
BigQuery Connection User (roles/bigquery.connectionUser)
BigQuery Authorized Routine Admin (roles/bigquery.routineAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Databases Admin (roles/iam.databasesAdmin)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.dataPolicies.attach
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Security Admin (roles/bigquery.securityAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
BigQuery Data Policy Admin (roles/bigquerydatapolicy.admin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Service agent roles
bigquery.dataPolicies.create
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Security Admin (roles/bigquery.securityAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
BigQuery Data Policy Admin (roles/bigquerydatapolicy.admin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Service agent roles
bigquery.dataPolicies.delete
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Security Admin (roles/bigquery.securityAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
BigQuery Data Policy Admin (roles/bigquerydatapolicy.admin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Service agent roles
bigquery.dataPolicies.get
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Security Admin (roles/bigquery.securityAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
BigQuery Data Policy Admin (roles/bigquerydatapolicy.admin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
BigQuery Data Policy Viewer (roles/bigquerydatapolicy.viewer)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.dataPolicies.getIamPolicy
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Security Admin (roles/bigquery.securityAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
BigQuery Data Policy Admin (roles/bigquerydatapolicy.admin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Security Admin (roles/iam.securityAdmin)
Security Auditor (roles/iam.securityAuditor)
Security Reviewer (roles/iam.securityReviewer)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.dataPolicies.getRawData
Raw Data Reader (roles/bigquerydatapolicy.rawDataReader)
bigquery.dataPolicies.list
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Security Admin (roles/bigquery.securityAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
BigQuery Data Policy Admin (roles/bigquerydatapolicy.admin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
BigQuery Data Policy Viewer (roles/bigquerydatapolicy.viewer)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Security Admin (roles/iam.securityAdmin)
Security Auditor (roles/iam.securityAuditor)
Security Reviewer (roles/iam.securityReviewer)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.dataPolicies.maskedGet
Masked Reader (roles/bigquerydatapolicy.maskedReader)
bigquery.dataPolicies.setIamPolicy
Owner (roles/owner)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Security Admin (roles/bigquery.securityAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
BigQuery Data Policy Admin (roles/bigquerydatapolicy.admin)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Security Admin (roles/iam.securityAdmin)
Service agent roles
bigquery.dataPolicies.update
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Security Admin (roles/bigquery.securityAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
BigQuery Data Policy Admin (roles/bigquerydatapolicy.admin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Service agent roles
bigquery.datasets.create
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Editor (roles/bigquery.dataEditor)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
BigQuery User (roles/bigquery.user)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Commerce Business Enablement Configuration Admin (roles/commercebusinessenablement.admin)
Datastream Bigquery Writer (roles/datastream.bigqueryWriter)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Data Scientist (roles/iam.dataScientist)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Service agent roles
bigquery.datasets.createTagBinding
Owner (roles/owner)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Security Admin (roles/bigquery.securityAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Tag User (roles/resourcemanager.tagUser)
Service agent roles
bigquery.datasets.delete
Owner (roles/owner)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Service agent roles
bigquery.datasets.deleteTagBinding
Owner (roles/owner)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Security Admin (roles/bigquery.securityAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Tag User (roles/resourcemanager.tagUser)
Service agent roles
bigquery.datasets.get
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Editor (roles/bigquery.dataEditor)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Data Viewer (roles/bigquery.dataViewer)
BigQuery Metadata Viewer (roles/bigquery.metadataViewer)
BigQuery Authorized Routine Admin (roles/bigquery.routineAdmin)
BigQuery Authorized Routine Data Editor (roles/bigquery.routineDataEditor)
BigQuery Authorized Routine Data Viewer (roles/bigquery.routineDataViewer)
BigQuery Authorized Routine Metadata Viewer (roles/bigquery.routineMetadataViewer)
BigQuery Security Admin (roles/bigquery.securityAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
BigQuery User (roles/bigquery.user)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Commerce Business Enablement Configuration Admin (roles/commercebusinessenablement.admin)
Data Catalog Admin (roles/datacatalog.admin)
Datacatalog Editor (roles/datacatalog.editor)
Data Catalog Viewer (roles/datacatalog.viewer)
Dataplex Storage Data Owner (roles/dataplex.storageDataOwner)
Dataplex Storage Data Reader (roles/dataplex.storageDataReader)
Datastream Bigquery Writer (roles/datastream.bigqueryWriter)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Data Scientist (roles/iam.dataScientist)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Security Auditor (roles/iam.securityAuditor)
Site Reliability Engineer (roles/iam.siteReliabilityEngineer)
Support User (roles/iam.supportUser)
SLZ BQDW Blueprint Project Level Remediator (roles/securedlandingzone.bqdwProjectRemediator)
Service agent roles
bigquery.datasets.getIamPolicy
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Editor (roles/bigquery.dataEditor)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Data Viewer (roles/bigquery.dataViewer)
BigQuery Metadata Viewer (roles/bigquery.metadataViewer)
BigQuery Security Admin (roles/bigquery.securityAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
BigQuery User (roles/bigquery.user)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Data Scientist (roles/iam.dataScientist)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Security Admin (roles/iam.securityAdmin)
Security Auditor (roles/iam.securityAuditor)
Security Reviewer (roles/iam.securityReviewer)
Site Reliability Engineer (roles/iam.siteReliabilityEngineer)
Support User (roles/iam.supportUser)
SLZ BQDW Blueprint Project Level Remediator (roles/securedlandingzone.bqdwProjectRemediator)
Service agent roles
bigquery.datasets.link
Owner (roles/owner)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Service agent roles
bigquery.datasets.listEffectiveTags
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Security Admin (roles/bigquery.securityAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Security Auditor (roles/iam.securityAuditor)
Support User (roles/iam.supportUser)
Tag User (roles/resourcemanager.tagUser)
Tag Viewer (roles/resourcemanager.tagViewer)
Service agent roles
bigquery.datasets.listSharedDatasetUsage
Owner (roles/owner)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Security Admin (roles/bigquery.securityAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Service agent roles
bigquery.datasets.listTagBindings
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Security Admin (roles/bigquery.securityAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Security Auditor (roles/iam.securityAuditor)
Support User (roles/iam.supportUser)
Tag User (roles/resourcemanager.tagUser)
Tag Viewer (roles/resourcemanager.tagViewer)
Service agent roles
bigquery.datasets.setIamPolicy
Owner (roles/owner)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Security Admin (roles/bigquery.securityAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Security Admin (roles/iam.securityAdmin)
SLZ BQDW Blueprint Project Level Remediator (roles/securedlandingzone.bqdwProjectRemediator)
Service agent roles
bigquery.datasets.update
Owner (roles/owner)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Security Admin (roles/bigquery.securityAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Commerce Business Enablement Configuration Admin (roles/commercebusinessenablement.admin)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
SLZ BQDW Blueprint Project Level Remediator (roles/securedlandingzone.bqdwProjectRemediator)
Service agent roles
bigquery.datasets.updateTag
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Editor (roles/bigquery.dataEditor)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Security Admin (roles/bigquery.securityAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Data Catalog Admin (roles/datacatalog.admin)
Data Catalog Tag Editor (roles/datacatalog.tagEditor)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Data Scientist (roles/iam.dataScientist)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Service agent roles
bigquery.jobs.create
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Job User (roles/bigquery.jobUser)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
BigQuery Studio User (roles/bigquery.studioUser)
BigQuery User (roles/bigquery.user)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Datastream Bigquery Writer (roles/datastream.bigqueryWriter)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Data Scientist (roles/iam.dataScientist)
Databases Admin (roles/iam.databasesAdmin)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.jobs.createGlobalQuery
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Databases Admin (roles/iam.databasesAdmin)
Service agent roles
bigquery.jobs.delete
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Datastream Bigquery Writer (roles/datastream.bigqueryWriter)
Databases Admin (roles/iam.databasesAdmin)
Service agent roles
bigquery.jobs.get
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Resource Admin (roles/bigquery.resourceAdmin)
BigQuery Resource Editor (roles/bigquery.resourceEditor)
BigQuery Resource Viewer (roles/bigquery.resourceViewer)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Datastream Bigquery Writer (roles/datastream.bigqueryWriter)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Databases Admin (roles/iam.databasesAdmin)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.jobs.list
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Resource Admin (roles/bigquery.resourceAdmin)
BigQuery Resource Editor (roles/bigquery.resourceEditor)
BigQuery Resource Viewer (roles/bigquery.resourceViewer)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
BigQuery User (roles/bigquery.user)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Datastream Bigquery Writer (roles/datastream.bigqueryWriter)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Databases Admin (roles/iam.databasesAdmin)
Security Admin (roles/iam.securityAdmin)
Security Auditor (roles/iam.securityAuditor)
Security Reviewer (roles/iam.securityReviewer)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.jobs.listAll
Owner (roles/owner)
BigQuery Admin (roles/bigquery.admin)
BigQuery Resource Admin (roles/bigquery.resourceAdmin)
BigQuery Resource Editor (roles/bigquery.resourceEditor)
BigQuery Resource Viewer (roles/bigquery.resourceViewer)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Databases Admin (roles/iam.databasesAdmin)
Service agent roles
bigquery.jobs.listExecutionMetadata
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Resource Admin (roles/bigquery.resourceAdmin)
BigQuery Resource Editor (roles/bigquery.resourceEditor)
BigQuery Resource Viewer (roles/bigquery.resourceViewer)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Databases Admin (roles/iam.databasesAdmin)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.jobs.update
Owner (roles/owner)
BigQuery Admin (roles/bigquery.admin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Datastream Bigquery Writer (roles/datastream.bigqueryWriter)
Databases Admin (roles/iam.databasesAdmin)
Service agent roles
bigquery.models.create
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Editor (roles/bigquery.dataEditor)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Dataplex Storage Data Owner (roles/dataplex.storageDataOwner)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Data Scientist (roles/iam.dataScientist)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Service agent roles
bigquery.models.delete
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Editor (roles/bigquery.dataEditor)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Dataplex Storage Data Owner (roles/dataplex.storageDataOwner)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Data Scientist (roles/iam.dataScientist)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Service agent roles
bigquery.models.export
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Editor (roles/bigquery.dataEditor)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Data Viewer (roles/bigquery.dataViewer)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Dataplex Storage Data Owner (roles/dataplex.storageDataOwner)
Dataplex Storage Data Reader (roles/dataplex.storageDataReader)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Data Scientist (roles/iam.dataScientist)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Site Reliability Engineer (roles/iam.siteReliabilityEngineer)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.models.getData
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Editor (roles/bigquery.dataEditor)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Data Viewer (roles/bigquery.dataViewer)
BigQuery Authorized Routine Admin (roles/bigquery.routineAdmin)
BigQuery Authorized Routine Data Editor (roles/bigquery.routineDataEditor)
BigQuery Authorized Routine Data Viewer (roles/bigquery.routineDataViewer)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Dataplex Storage Data Owner (roles/dataplex.storageDataOwner)
Dataplex Storage Data Reader (roles/dataplex.storageDataReader)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Data Scientist (roles/iam.dataScientist)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Site Reliability Engineer (roles/iam.siteReliabilityEngineer)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.models.getMetadata
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Editor (roles/bigquery.dataEditor)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Data Viewer (roles/bigquery.dataViewer)
BigQuery Metadata Viewer (roles/bigquery.metadataViewer)
BigQuery Authorized Routine Admin (roles/bigquery.routineAdmin)
BigQuery Authorized Routine Data Editor (roles/bigquery.routineDataEditor)
BigQuery Authorized Routine Data Viewer (roles/bigquery.routineDataViewer)
BigQuery Authorized Routine Metadata Viewer (roles/bigquery.routineMetadataViewer)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Data Catalog Admin (roles/datacatalog.admin)
Datacatalog Editor (roles/datacatalog.editor)
Data Catalog Viewer (roles/datacatalog.viewer)
Dataplex Storage Data Owner (roles/dataplex.storageDataOwner)
Dataplex Storage Data Reader (roles/dataplex.storageDataReader)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Data Scientist (roles/iam.dataScientist)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Security Auditor (roles/iam.securityAuditor)
Site Reliability Engineer (roles/iam.siteReliabilityEngineer)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.models.list
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Editor (roles/bigquery.dataEditor)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Data Viewer (roles/bigquery.dataViewer)
BigQuery Metadata Viewer (roles/bigquery.metadataViewer)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
BigQuery User (roles/bigquery.user)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Dataplex Storage Data Owner (roles/dataplex.storageDataOwner)
Dataplex Storage Data Reader (roles/dataplex.storageDataReader)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Data Scientist (roles/iam.dataScientist)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Security Admin (roles/iam.securityAdmin)
Security Auditor (roles/iam.securityAuditor)
Security Reviewer (roles/iam.securityReviewer)
Site Reliability Engineer (roles/iam.siteReliabilityEngineer)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.models.updateData
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Editor (roles/bigquery.dataEditor)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Dataplex Storage Data Owner (roles/dataplex.storageDataOwner)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Data Scientist (roles/iam.dataScientist)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Service agent roles
bigquery.models.updateMetadata
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Editor (roles/bigquery.dataEditor)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Dataplex Storage Data Owner (roles/dataplex.storageDataOwner)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Data Scientist (roles/iam.dataScientist)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Service agent roles
bigquery.models.updateTag
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Editor (roles/bigquery.dataEditor)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Data Catalog Admin (roles/datacatalog.admin)
Data Catalog Tag Editor (roles/datacatalog.tagEditor)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Data Scientist (roles/iam.dataScientist)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Service agent roles
bigquery.objectRefs.read
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery ObjectRef Admin (roles/bigquery.objectRefAdmin)
BigQuery ObjectRef Reader (roles/bigquery.objectRefReader)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Databases Admin (roles/iam.databasesAdmin)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.objectRefs.write
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery ObjectRef Admin (roles/bigquery.objectRefAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Databases Admin (roles/iam.databasesAdmin)
Service agent roles
bigquery.readsessions.create
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Read Session User (roles/bigquery.readSessionUser)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
BigQuery Studio User (roles/bigquery.studioUser)
BigQuery User (roles/bigquery.user)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Data Scientist (roles/iam.dataScientist)
Databases Admin (roles/iam.databasesAdmin)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.readsessions.getData
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Read Session User (roles/bigquery.readSessionUser)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
BigQuery Studio User (roles/bigquery.studioUser)
BigQuery User (roles/bigquery.user)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Data Scientist (roles/iam.dataScientist)
Databases Admin (roles/iam.databasesAdmin)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.readsessions.update
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Read Session User (roles/bigquery.readSessionUser)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
BigQuery Studio User (roles/bigquery.studioUser)
BigQuery User (roles/bigquery.user)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Data Scientist (roles/iam.dataScientist)
Databases Admin (roles/iam.databasesAdmin)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.reservationAssignments.create
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Resource Admin (roles/bigquery.resourceAdmin)
BigQuery Resource Editor (roles/bigquery.resourceEditor)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Databases Admin (roles/iam.databasesAdmin)
Service agent roles
bigquery.reservationAssignments.delete
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Resource Admin (roles/bigquery.resourceAdmin)
BigQuery Resource Editor (roles/bigquery.resourceEditor)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Databases Admin (roles/iam.databasesAdmin)
Service agent roles
bigquery.reservationAssignments.list
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Resource Admin (roles/bigquery.resourceAdmin)
BigQuery Resource Editor (roles/bigquery.resourceEditor)
BigQuery Resource Viewer (roles/bigquery.resourceViewer)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
BigQuery User (roles/bigquery.user)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Databases Admin (roles/iam.databasesAdmin)
Security Admin (roles/iam.securityAdmin)
Security Auditor (roles/iam.securityAuditor)
Security Reviewer (roles/iam.securityReviewer)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.reservationAssignments.search
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Resource Admin (roles/bigquery.resourceAdmin)
BigQuery Resource Editor (roles/bigquery.resourceEditor)
BigQuery Resource Viewer (roles/bigquery.resourceViewer)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
BigQuery User (roles/bigquery.user)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Databases Admin (roles/iam.databasesAdmin)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.reservationGroups.create
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Resource Admin (roles/bigquery.resourceAdmin)
BigQuery Resource Editor (roles/bigquery.resourceEditor)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Databases Admin (roles/iam.databasesAdmin)
Service agent roles
bigquery.reservationGroups.delete
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Resource Admin (roles/bigquery.resourceAdmin)
BigQuery Resource Editor (roles/bigquery.resourceEditor)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Databases Admin (roles/iam.databasesAdmin)
Service agent roles
bigquery.reservationGroups.get
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Resource Admin (roles/bigquery.resourceAdmin)
BigQuery Resource Editor (roles/bigquery.resourceEditor)
BigQuery Resource Viewer (roles/bigquery.resourceViewer)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
BigQuery User (roles/bigquery.user)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Databases Admin (roles/iam.databasesAdmin)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.reservationGroups.list
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Resource Admin (roles/bigquery.resourceAdmin)
BigQuery Resource Editor (roles/bigquery.resourceEditor)
BigQuery Resource Viewer (roles/bigquery.resourceViewer)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
BigQuery User (roles/bigquery.user)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Databases Admin (roles/iam.databasesAdmin)
Security Admin (roles/iam.securityAdmin)
Security Auditor (roles/iam.securityAuditor)
Security Reviewer (roles/iam.securityReviewer)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.reservations.create
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Resource Admin (roles/bigquery.resourceAdmin)
BigQuery Resource Editor (roles/bigquery.resourceEditor)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Databases Admin (roles/iam.databasesAdmin)
Service agent roles
bigquery.reservations.delete
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Resource Admin (roles/bigquery.resourceAdmin)
BigQuery Resource Editor (roles/bigquery.resourceEditor)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Databases Admin (roles/iam.databasesAdmin)
Service agent roles
bigquery.reservations.get
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Resource Admin (roles/bigquery.resourceAdmin)
BigQuery Resource Editor (roles/bigquery.resourceEditor)
BigQuery Resource Viewer (roles/bigquery.resourceViewer)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
BigQuery User (roles/bigquery.user)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Databases Admin (roles/iam.databasesAdmin)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.reservations.getIamPolicy
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Resource Admin (roles/bigquery.resourceAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Databases Admin (roles/iam.databasesAdmin)
Security Admin (roles/iam.securityAdmin)
Security Auditor (roles/iam.securityAuditor)
Security Reviewer (roles/iam.securityReviewer)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.reservations.list
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Resource Admin (roles/bigquery.resourceAdmin)
BigQuery Resource Editor (roles/bigquery.resourceEditor)
BigQuery Resource Viewer (roles/bigquery.resourceViewer)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
BigQuery User (roles/bigquery.user)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Databases Admin (roles/iam.databasesAdmin)
Security Admin (roles/iam.securityAdmin)
Security Auditor (roles/iam.securityAuditor)
Security Reviewer (roles/iam.securityReviewer)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.reservations.listFailoverDatasets
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Resource Admin (roles/bigquery.resourceAdmin)
BigQuery Resource Editor (roles/bigquery.resourceEditor)
BigQuery Resource Viewer (roles/bigquery.resourceViewer)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
BigQuery User (roles/bigquery.user)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Databases Admin (roles/iam.databasesAdmin)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.reservations.setIamPolicy
Owner (roles/owner)
BigQuery Admin (roles/bigquery.admin)
BigQuery Resource Admin (roles/bigquery.resourceAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Databases Admin (roles/iam.databasesAdmin)
Security Admin (roles/iam.securityAdmin)
Service agent roles
bigquery.reservations.update
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Resource Admin (roles/bigquery.resourceAdmin)
BigQuery Resource Editor (roles/bigquery.resourceEditor)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Databases Admin (roles/iam.databasesAdmin)
Service agent roles
bigquery.reservations.use
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Resource Admin (roles/bigquery.resourceAdmin)
BigQuery Resource Editor (roles/bigquery.resourceEditor)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
BigQuery User (roles/bigquery.user)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Databases Admin (roles/iam.databasesAdmin)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.routines.create
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Editor (roles/bigquery.dataEditor)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Dataplex Storage Data Owner (roles/dataplex.storageDataOwner)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Data Scientist (roles/iam.dataScientist)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Service agent roles
bigquery.routines.delete
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Editor (roles/bigquery.dataEditor)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Dataplex Storage Data Owner (roles/dataplex.storageDataOwner)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Data Scientist (roles/iam.dataScientist)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Service agent roles
bigquery.routines.get
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Editor (roles/bigquery.dataEditor)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Data Viewer (roles/bigquery.dataViewer)
BigQuery Metadata Viewer (roles/bigquery.metadataViewer)
BigQuery Authorized Routine Admin (roles/bigquery.routineAdmin)
BigQuery Authorized Routine Data Editor (roles/bigquery.routineDataEditor)
BigQuery Authorized Routine Data Viewer (roles/bigquery.routineDataViewer)
BigQuery Authorized Routine Metadata Viewer (roles/bigquery.routineMetadataViewer)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Data Catalog Admin (roles/datacatalog.admin)
Datacatalog Editor (roles/datacatalog.editor)
Data Catalog Viewer (roles/datacatalog.viewer)
Dataplex Storage Data Owner (roles/dataplex.storageDataOwner)
Dataplex Storage Data Reader (roles/dataplex.storageDataReader)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Data Scientist (roles/iam.dataScientist)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Security Auditor (roles/iam.securityAuditor)
Site Reliability Engineer (roles/iam.siteReliabilityEngineer)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.routines.list
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Editor (roles/bigquery.dataEditor)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Data Viewer (roles/bigquery.dataViewer)
BigQuery Metadata Viewer (roles/bigquery.metadataViewer)
BigQuery Authorized Routine Admin (roles/bigquery.routineAdmin)
BigQuery Authorized Routine Data Editor (roles/bigquery.routineDataEditor)
BigQuery Authorized Routine Data Viewer (roles/bigquery.routineDataViewer)
BigQuery Authorized Routine Metadata Viewer (roles/bigquery.routineMetadataViewer)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
BigQuery User (roles/bigquery.user)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Dataplex Storage Data Owner (roles/dataplex.storageDataOwner)
Dataplex Storage Data Reader (roles/dataplex.storageDataReader)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Data Scientist (roles/iam.dataScientist)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Security Admin (roles/iam.securityAdmin)
Security Auditor (roles/iam.securityAuditor)
Security Reviewer (roles/iam.securityReviewer)
Site Reliability Engineer (roles/iam.siteReliabilityEngineer)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.routines.update
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Editor (roles/bigquery.dataEditor)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Dataplex Storage Data Owner (roles/dataplex.storageDataOwner)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Data Scientist (roles/iam.dataScientist)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Service agent roles
bigquery.routines.updateTag
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Editor (roles/bigquery.dataEditor)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Data Catalog Admin (roles/datacatalog.admin)
Data Catalog Tag Editor (roles/datacatalog.tagEditor)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Data Scientist (roles/iam.dataScientist)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Service agent roles
bigquery.rowAccessPolicies.create
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Security Admin (roles/bigquery.securityAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Service agent roles
bigquery.rowAccessPolicies.delete
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Security Admin (roles/bigquery.securityAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Service agent roles
bigquery.rowAccessPolicies.get
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Security Admin (roles/bigquery.securityAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.rowAccessPolicies.getFilteredData
BigQuery Filtered Data Viewer (roles/bigquery.filteredDataViewer)
bigquery.rowAccessPolicies.getIamPolicy
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Security Admin (roles/bigquery.securityAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Security Admin (roles/iam.securityAdmin)
Security Auditor (roles/iam.securityAuditor)
Security Reviewer (roles/iam.securityReviewer)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.rowAccessPolicies.list
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Security Admin (roles/bigquery.securityAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Security Admin (roles/iam.securityAdmin)
Security Auditor (roles/iam.securityAuditor)
Security Reviewer (roles/iam.securityReviewer)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.rowAccessPolicies.overrideTimeTravelRestrictions
BigQuery Admin (roles/bigquery.admin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Databases Admin (roles/iam.databasesAdmin)
Service agent roles
bigquery.rowAccessPolicies.setIamPolicy
Owner (roles/owner)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Security Admin (roles/bigquery.securityAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Security Admin (roles/iam.securityAdmin)
Service agent roles
bigquery.rowAccessPolicies.update
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Security Admin (roles/bigquery.securityAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Service agent roles
bigquery.savedqueries.create
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Databases Admin (roles/iam.databasesAdmin)
Service agent roles
bigquery.savedqueries.delete
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Databases Admin (roles/iam.databasesAdmin)
Service agent roles
bigquery.savedqueries.get
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
BigQuery User (roles/bigquery.user)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Databases Admin (roles/iam.databasesAdmin)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.savedqueries.list
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
BigQuery User (roles/bigquery.user)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Databases Admin (roles/iam.databasesAdmin)
Security Admin (roles/iam.securityAdmin)
Security Auditor (roles/iam.securityAuditor)
Security Reviewer (roles/iam.securityReviewer)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.savedqueries.update
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Databases Admin (roles/iam.databasesAdmin)
Service agent roles
bigquery.tables.create
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Editor (roles/bigquery.dataEditor)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Authorized Routine Admin (roles/bigquery.routineAdmin)
BigQuery Authorized Routine Data Editor (roles/bigquery.routineDataEditor)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Dataplex Storage Data Owner (roles/dataplex.storageDataOwner)
Datastream Bigquery Writer (roles/datastream.bigqueryWriter)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Data Scientist (roles/iam.dataScientist)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Service agent roles
bigquery.tables.createIndex
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Editor (roles/bigquery.dataEditor)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Data Scientist (roles/iam.dataScientist)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Service agent roles
bigquery.tables.createSnapshot
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Editor (roles/bigquery.dataEditor)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Data Viewer (roles/bigquery.dataViewer)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Dataplex Storage Data Owner (roles/dataplex.storageDataOwner)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Data Scientist (roles/iam.dataScientist)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Site Reliability Engineer (roles/iam.siteReliabilityEngineer)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.tables.createTagBinding
Owner (roles/owner)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Security Admin (roles/bigquery.securityAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Tag User (roles/resourcemanager.tagUser)
Service agent roles
bigquery.tables.delete
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Editor (roles/bigquery.dataEditor)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Authorized Routine Admin (roles/bigquery.routineAdmin)
BigQuery Authorized Routine Data Editor (roles/bigquery.routineDataEditor)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Dataplex Storage Data Owner (roles/dataplex.storageDataOwner)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Data Scientist (roles/iam.dataScientist)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Service agent roles
bigquery.tables.deleteIndex
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Editor (roles/bigquery.dataEditor)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Data Scientist (roles/iam.dataScientist)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Service agent roles
bigquery.tables.deleteSnapshot
Owner (roles/owner)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Dataplex Storage Data Owner (roles/dataplex.storageDataOwner)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Service agent roles
bigquery.tables.deleteTagBinding
Owner (roles/owner)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Security Admin (roles/bigquery.securityAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Tag User (roles/resourcemanager.tagUser)
Service agent roles
bigquery.tables.export
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Editor (roles/bigquery.dataEditor)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Data Viewer (roles/bigquery.dataViewer)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Dataplex Storage Data Owner (roles/dataplex.storageDataOwner)
Dataplex Storage Data Reader (roles/dataplex.storageDataReader)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Data Scientist (roles/iam.dataScientist)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Site Reliability Engineer (roles/iam.siteReliabilityEngineer)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.tables.get
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Editor (roles/bigquery.dataEditor)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Data Viewer (roles/bigquery.dataViewer)
BigQuery Metadata Viewer (roles/bigquery.metadataViewer)
BigQuery Authorized Routine Admin (roles/bigquery.routineAdmin)
BigQuery Authorized Routine Data Editor (roles/bigquery.routineDataEditor)
BigQuery Authorized Routine Data Viewer (roles/bigquery.routineDataViewer)
BigQuery Authorized Routine Metadata Viewer (roles/bigquery.routineMetadataViewer)
BigQuery Security Admin (roles/bigquery.securityAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Data Catalog Admin (roles/datacatalog.admin)
Datacatalog Editor (roles/datacatalog.editor)
Data Catalog Viewer (roles/datacatalog.viewer)
Dataplex Storage Data Owner (roles/dataplex.storageDataOwner)
Dataplex Storage Data Reader (roles/dataplex.storageDataReader)
Datastream Bigquery Writer (roles/datastream.bigqueryWriter)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Data Scientist (roles/iam.dataScientist)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Security Auditor (roles/iam.securityAuditor)
Site Reliability Engineer (roles/iam.siteReliabilityEngineer)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.tables.getData
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Editor (roles/bigquery.dataEditor)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Data Viewer (roles/bigquery.dataViewer)
BigQuery Authorized Routine Admin (roles/bigquery.routineAdmin)
BigQuery Authorized Routine Data Editor (roles/bigquery.routineDataEditor)
BigQuery Authorized Routine Data Viewer (roles/bigquery.routineDataViewer)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Dataplex Storage Data Owner (roles/dataplex.storageDataOwner)
Dataplex Storage Data Reader (roles/dataplex.storageDataReader)
Datastream Bigquery Writer (roles/datastream.bigqueryWriter)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Data Scientist (roles/iam.dataScientist)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Site Reliability Engineer (roles/iam.siteReliabilityEngineer)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.tables.getIamPolicy
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Editor (roles/bigquery.dataEditor)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Data Viewer (roles/bigquery.dataViewer)
BigQuery Metadata Viewer (roles/bigquery.metadataViewer)
BigQuery Security Admin (roles/bigquery.securityAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Data Scientist (roles/iam.dataScientist)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Security Admin (roles/iam.securityAdmin)
Security Auditor (roles/iam.securityAuditor)
Security Reviewer (roles/iam.securityReviewer)
Site Reliability Engineer (roles/iam.siteReliabilityEngineer)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.tables.list
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Editor (roles/bigquery.dataEditor)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Data Viewer (roles/bigquery.dataViewer)
BigQuery Metadata Viewer (roles/bigquery.metadataViewer)
BigQuery Authorized Routine Admin (roles/bigquery.routineAdmin)
BigQuery Authorized Routine Data Editor (roles/bigquery.routineDataEditor)
BigQuery Authorized Routine Data Viewer (roles/bigquery.routineDataViewer)
BigQuery Authorized Routine Metadata Viewer (roles/bigquery.routineMetadataViewer)
BigQuery Security Admin (roles/bigquery.securityAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
BigQuery User (roles/bigquery.user)
Dataplex Storage Data Owner (roles/dataplex.storageDataOwner)
Dataplex Storage Data Reader (roles/dataplex.storageDataReader)
Datastream Bigquery Writer (roles/datastream.bigqueryWriter)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Data Scientist (roles/iam.dataScientist)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Security Admin (roles/iam.securityAdmin)
Security Auditor (roles/iam.securityAuditor)
Security Reviewer (roles/iam.securityReviewer)
Site Reliability Engineer (roles/iam.siteReliabilityEngineer)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.tables.listEffectiveTags
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Security Admin (roles/bigquery.securityAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Security Auditor (roles/iam.securityAuditor)
Support User (roles/iam.supportUser)
Tag User (roles/resourcemanager.tagUser)
Tag Viewer (roles/resourcemanager.tagViewer)
Service agent roles
bigquery.tables.listTagBindings
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Security Admin (roles/bigquery.securityAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Security Auditor (roles/iam.securityAuditor)
Support User (roles/iam.supportUser)
Tag User (roles/resourcemanager.tagUser)
Tag Viewer (roles/resourcemanager.tagViewer)
Service agent roles
bigquery.tables.replicateData
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Editor (roles/bigquery.dataEditor)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Data Viewer (roles/bigquery.dataViewer)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Data Scientist (roles/iam.dataScientist)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Site Reliability Engineer (roles/iam.siteReliabilityEngineer)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.tables.restoreSnapshot
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Editor (roles/bigquery.dataEditor)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Dataplex Storage Data Owner (roles/dataplex.storageDataOwner)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Data Scientist (roles/iam.dataScientist)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Service agent roles
bigquery.tables.setCategory
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Service agent roles
bigquery.tables.setColumnDataPolicy
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Security Admin (roles/bigquery.securityAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Service agent roles
bigquery.tables.setIamPolicy
Owner (roles/owner)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Security Admin (roles/bigquery.securityAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Security Admin (roles/iam.securityAdmin)
Service agent roles
bigquery.tables.update
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Editor (roles/bigquery.dataEditor)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Authorized Routine Admin (roles/bigquery.routineAdmin)
BigQuery Authorized Routine Data Editor (roles/bigquery.routineDataEditor)
BigQuery Security Admin (roles/bigquery.securityAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Dataplex Storage Data Owner (roles/dataplex.storageDataOwner)
Datastream Bigquery Writer (roles/datastream.bigqueryWriter)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Data Scientist (roles/iam.dataScientist)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Service agent roles
bigquery.tables.updateData
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Editor (roles/bigquery.dataEditor)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Authorized Routine Admin (roles/bigquery.routineAdmin)
BigQuery Authorized Routine Data Editor (roles/bigquery.routineDataEditor)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Dataplex Storage Data Owner (roles/dataplex.storageDataOwner)
Dataplex Storage Data Writer (roles/dataplex.storageDataWriter)
Datastream Bigquery Writer (roles/datastream.bigqueryWriter)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Data Scientist (roles/iam.dataScientist)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Service agent roles
bigquery.tables.updateIndex
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Editor (roles/bigquery.dataEditor)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Data Scientist (roles/iam.dataScientist)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Service agent roles
bigquery.tables.updateTag
BigQuery Admin (roles/bigquery.admin)
BigQuery Data Editor (roles/bigquery.dataEditor)
BigQuery Data Owner (roles/bigquery.dataOwner)
BigQuery Security Admin (roles/bigquery.securityAdmin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Data Catalog Admin (roles/datacatalog.admin)
Data Catalog Tag Editor (roles/datacatalog.tagEditor)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Data Scientist (roles/iam.dataScientist)
Databases Admin (roles/iam.databasesAdmin)
ML Engineer (roles/iam.mlEngineer)
Service agent roles
bigquery.transfers.get
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
BigQuery Admin (roles/bigquery.admin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
BigQuery User (roles/bigquery.user)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Databases Admin (roles/iam.databasesAdmin)
Support User (roles/iam.supportUser)
Service agent roles
bigquery.transfers.update
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
Bigquerydatapolicy Editor (roles/bigquerydatapolicy.editor)
Databases Admin (roles/iam.databasesAdmin)
Service agent roles
BigQuery Connection API permissions
There are no IAM permissions for this service.
BigQuery Continuous Query permissions
There are no IAM permissions for this service.
BigQuery Data Policy permissions
There are no IAM permissions for this service.
BigQuery Data Transfer Service permissions
There are no IAM permissions for this service.
BigQuery Engine for Apache Flink permissions
This table lists the IAM permissions for BigQuery Engine for Apache Flink and the roles that include them. To search through all roles and permissions, see the role and permission index.
Permission Included in roles
managedflink.deployments.create
Owner (roles/owner)
Editor (roles/editor)
Managed Flink Admin (roles/managedflink.admin)
managedflink.deployments.delete
Owner (roles/owner)
Editor (roles/editor)
Managed Flink Admin (roles/managedflink.admin)
managedflink.deployments.get
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
Support User (roles/iam.supportUser)
Managed Flink Admin (roles/managedflink.admin)
Managed Flink Developer (roles/managedflink.developer)
Managed Flink Viewer (roles/managedflink.viewer)
managedflink.deployments.list
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
Security Admin (roles/iam.securityAdmin)
Security Auditor (roles/iam.securityAuditor)
Security Reviewer (roles/iam.securityReviewer)
Support User (roles/iam.supportUser)
Managed Flink Admin (roles/managedflink.admin)
Managed Flink Developer (roles/managedflink.developer)
Managed Flink Viewer (roles/managedflink.viewer)
managedflink.deployments.update
Owner (roles/owner)
Editor (roles/editor)
Managed Flink Admin (roles/managedflink.admin)
managedflink.jobs.create
Owner (roles/owner)
Editor (roles/editor)
Managed Flink Admin (roles/managedflink.admin)
Managed Flink Developer (roles/managedflink.developer)
managedflink.jobs.delete
Owner (roles/owner)
Editor (roles/editor)
Managed Flink Admin (roles/managedflink.admin)
Managed Flink Developer (roles/managedflink.developer)
managedflink.jobs.get
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
Support User (roles/iam.supportUser)
Managed Flink Admin (roles/managedflink.admin)
Managed Flink Developer (roles/managedflink.developer)
Managed Flink Viewer (roles/managedflink.viewer)
managedflink.jobs.list
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
Security Admin (roles/iam.securityAdmin)
Security Auditor (roles/iam.securityAuditor)
Security Reviewer (roles/iam.securityReviewer)
Support User (roles/iam.supportUser)
Managed Flink Admin (roles/managedflink.admin)
Managed Flink Developer (roles/managedflink.developer)
Managed Flink Viewer (roles/managedflink.viewer)
managedflink.jobs.update
Owner (roles/owner)
Editor (roles/editor)
Managed Flink Admin (roles/managedflink.admin)
Managed Flink Developer (roles/managedflink.developer)
managedflink.locations.get
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
Support User (roles/iam.supportUser)
Managed Flink Admin (roles/managedflink.admin)
Managed Flink Developer (roles/managedflink.developer)
Managed Flink Viewer (roles/managedflink.viewer)
managedflink.locations.list
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
Security Admin (roles/iam.securityAdmin)
Security Auditor (roles/iam.securityAuditor)
Security Reviewer (roles/iam.securityReviewer)
Support User (roles/iam.supportUser)
Managed Flink Admin (roles/managedflink.admin)
Managed Flink Developer (roles/managedflink.developer)
Managed Flink Viewer (roles/managedflink.viewer)
managedflink.operations.cancel
Owner (roles/owner)
Editor (roles/editor)
Managed Flink Admin (roles/managedflink.admin)
managedflink.operations.delete
Owner (roles/owner)
Editor (roles/editor)
Managed Flink Admin (roles/managedflink.admin)
managedflink.operations.get
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
Support User (roles/iam.supportUser)
Managed Flink Admin (roles/managedflink.admin)
Managed Flink Developer (roles/managedflink.developer)
Managed Flink Viewer (roles/managedflink.viewer)
managedflink.operations.list
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
Security Admin (roles/iam.securityAdmin)
Security Auditor (roles/iam.securityAuditor)
Security Reviewer (roles/iam.securityReviewer)
Support User (roles/iam.supportUser)
Managed Flink Admin (roles/managedflink.admin)
Managed Flink Developer (roles/managedflink.developer)
Managed Flink Viewer (roles/managedflink.viewer)
managedflink.sessions.create
Owner (roles/owner)
Editor (roles/editor)
Managed Flink Admin (roles/managedflink.admin)
Managed Flink Developer (roles/managedflink.developer)
managedflink.sessions.delete
Owner (roles/owner)
Editor (roles/editor)
Managed Flink Admin (roles/managedflink.admin)
Managed Flink Developer (roles/managedflink.developer)
managedflink.sessions.get
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
Support User (roles/iam.supportUser)
Managed Flink Admin (roles/managedflink.admin)
Managed Flink Developer (roles/managedflink.developer)
Managed Flink Viewer (roles/managedflink.viewer)
managedflink.sessions.list
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
Security Admin (roles/iam.securityAdmin)
Security Auditor (roles/iam.securityAuditor)
Security Reviewer (roles/iam.securityReviewer)
Support User (roles/iam.supportUser)
Managed Flink Admin (roles/managedflink.admin)
Managed Flink Developer (roles/managedflink.developer)
Managed Flink Viewer (roles/managedflink.viewer)
managedflink.sessions.update
Owner (roles/owner)
Editor (roles/editor)
Managed Flink Admin (roles/managedflink.admin)
Managed Flink Developer (roles/managedflink.developer)
BigQuery Migration Service permissions
This table lists the IAM permissions for BigQuery Migration Service and the roles that include them. To search through all roles and permissions, see the role and permission index.
Permission Included in roles
bigquerymigration.subtasks.get
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
Bigquerymigration Admin (roles/bigquerymigration.admin)
MigrationWorkflow Editor (roles/bigquerymigration.editor)
MigrationWorkflow Viewer (roles/bigquerymigration.viewer)
Support User (roles/iam.supportUser)
bigquerymigration.subtasks.list
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
Bigquerymigration Admin (roles/bigquerymigration.admin)
MigrationWorkflow Editor (roles/bigquerymigration.editor)
MigrationWorkflow Viewer (roles/bigquerymigration.viewer)
Security Admin (roles/iam.securityAdmin)
Security Auditor (roles/iam.securityAuditor)
Security Reviewer (roles/iam.securityReviewer)
Support User (roles/iam.supportUser)
bigquerymigration.translation.translate
Owner (roles/owner)
Editor (roles/editor)
BigQuery Admin (roles/bigquery.admin)
BigQuery Studio Admin (roles/bigquery.studioAdmin)
BigQuery User (roles/bigquery.user)
Bigquerymigration Admin (roles/bigquerymigration.admin)
Migration Translation User (roles/bigquerymigration.translationUser)
DLP Organization Data Profiles Driver (roles/dlp.orgdriver)
DLP Project Data Profiles Driver (roles/dlp.projectdriver)
Databases Admin (roles/iam.databasesAdmin)
Service agent roles
bigquerymigration.workflows.create
Owner (roles/owner)
Editor (roles/editor)
Bigquerymigration Admin (roles/bigquerymigration.admin)
MigrationWorkflow Editor (roles/bigquerymigration.editor)
bigquerymigration.workflows.delete
Owner (roles/owner)
Editor (roles/editor)
Bigquerymigration Admin (roles/bigquerymigration.admin)
MigrationWorkflow Editor (roles/bigquerymigration.editor)
bigquerymigration.workflows.enableAiOutputTypes
Owner (roles/owner)
Editor (roles/editor)
Bigquerymigration Admin (roles/bigquerymigration.admin)
MigrationWorkflow Editor (roles/bigquerymigration.editor)
bigquerymigration.workflows.enableLineageOutputTypes
Owner (roles/owner)
Editor (roles/editor)
Bigquerymigration Admin (roles/bigquerymigration.admin)
MigrationWorkflow Editor (roles/bigquerymigration.editor)
bigquerymigration.workflows.enableOutputTypePermissions
Owner (roles/owner)
Editor (roles/editor)
Bigquerymigration Admin (roles/bigquerymigration.admin)
MigrationWorkflow Editor (roles/bigquerymigration.editor)
bigquerymigration.workflows.get
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
Bigquerymigration Admin (roles/bigquerymigration.admin)
MigrationWorkflow Editor (roles/bigquerymigration.editor)
MigrationWorkflow Viewer (roles/bigquerymigration.viewer)
Support User (roles/iam.supportUser)
bigquerymigration.workflows.list
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
Bigquerymigration Admin (roles/bigquerymigration.admin)
MigrationWorkflow Editor (roles/bigquerymigration.editor)
MigrationWorkflow Viewer (roles/bigquerymigration.viewer)
Security Admin (roles/iam.securityAdmin)
Security Auditor (roles/iam.securityAuditor)
Security Reviewer (roles/iam.securityReviewer)
Support User (roles/iam.supportUser)
bigquerymigration.workflows.orchestrateTask
Owner (roles/owner)
Bigquerymigration Admin (roles/bigquerymigration.admin)
Task Orchestrator (roles/bigquerymigration.orchestrator)
bigquerymigration.workflows.update
Owner (roles/owner)
Editor (roles/editor)
Bigquerymigration Admin (roles/bigquerymigration.admin)
MigrationWorkflow Editor (roles/bigquerymigration.editor)
BigQuery Omni permissions
There are no IAM permissions for this service.
BigQuery sharing permissions
This table lists the IAM permissions for BigQuery sharing and the roles that include them. To search through all roles and permissions, see the role and permission index.
Permission Included in roles
analyticshub.dataExchanges.create
Owner (roles/owner)
Editor (roles/editor)
Analytics Hub Admin (roles/analyticshub.admin)
Analyticshub Editor (roles/analyticshub.editor)
analyticshub.dataExchanges.delete
Owner (roles/owner)
Editor (roles/editor)
Analytics Hub Admin (roles/analyticshub.admin)
Analyticshub Editor (roles/analyticshub.editor)
analyticshub.dataExchanges.get
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
Analytics Hub Admin (roles/analyticshub.admin)
Analyticshub Editor (roles/analyticshub.editor)
Analytics Hub Listing Admin (roles/analyticshub.listingAdmin)
Analytics Hub Publisher (roles/analyticshub.publisher)
Analytics Hub Subscriber (roles/analyticshub.subscriber)
Analytics Hub Subscription Owner (roles/analyticshub.subscriptionOwner)
Analytics Hub Viewer (roles/analyticshub.viewer)
Support User (roles/iam.supportUser)
analyticshub.dataExchanges.getIamPolicy
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
Analytics Hub Admin (roles/analyticshub.admin)
Analyticshub Editor (roles/analyticshub.editor)
Analytics Hub Listing Admin (roles/analyticshub.listingAdmin)
Analytics Hub Publisher (roles/analyticshub.publisher)
Analytics Hub Subscriber (roles/analyticshub.subscriber)
Analytics Hub Subscription Owner (roles/analyticshub.subscriptionOwner)
Analytics Hub Viewer (roles/analyticshub.viewer)
Security Admin (roles/iam.securityAdmin)
Security Auditor (roles/iam.securityAuditor)
Security Reviewer (roles/iam.securityReviewer)
Support User (roles/iam.supportUser)
analyticshub.dataExchanges.list
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
Analytics Hub Admin (roles/analyticshub.admin)
Analyticshub Editor (roles/analyticshub.editor)
Analytics Hub Listing Admin (roles/analyticshub.listingAdmin)
Analytics Hub Publisher (roles/analyticshub.publisher)
Analytics Hub Subscriber (roles/analyticshub.subscriber)
Analytics Hub Subscription Owner (roles/analyticshub.subscriptionOwner)
Analytics Hub Viewer (roles/analyticshub.viewer)
Security Admin (roles/iam.securityAdmin)
Security Auditor (roles/iam.securityAuditor)
Security Reviewer (roles/iam.securityReviewer)
Support User (roles/iam.supportUser)
analyticshub.dataExchanges.setIamPolicy
Owner (roles/owner)
Analytics Hub Admin (roles/analyticshub.admin)
Security Admin (roles/iam.securityAdmin)
analyticshub.dataExchanges.subscribe
Owner (roles/owner)
Analytics Hub Subscriber (roles/analyticshub.subscriber)
analyticshub.dataExchanges.update
Owner (roles/owner)
Editor (roles/editor)
Analytics Hub Admin (roles/analyticshub.admin)
Analyticshub Editor (roles/analyticshub.editor)
analyticshub.dataExchanges.viewSubscriptions
Owner (roles/owner)
Analytics Hub Admin (roles/analyticshub.admin)
analyticshub.listings.create
Owner (roles/owner)
Editor (roles/editor)
Analytics Hub Admin (roles/analyticshub.admin)
Analyticshub Editor (roles/analyticshub.editor)
Analytics Hub Publisher (roles/analyticshub.publisher)
analyticshub.listings.delete
Owner (roles/owner)
Editor (roles/editor)
Analytics Hub Admin (roles/analyticshub.admin)
Analyticshub Editor (roles/analyticshub.editor)
Analytics Hub Listing Admin (roles/analyticshub.listingAdmin)
analyticshub.listings.get
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
Analytics Hub Admin (roles/analyticshub.admin)
Analyticshub Editor (roles/analyticshub.editor)
Analytics Hub Listing Admin (roles/analyticshub.listingAdmin)
Analytics Hub Publisher (roles/analyticshub.publisher)
Analytics Hub Subscriber (roles/analyticshub.subscriber)
Analytics Hub Subscription Owner (roles/analyticshub.subscriptionOwner)
Analytics Hub Viewer (roles/analyticshub.viewer)
Support User (roles/iam.supportUser)
analyticshub.listings.getIamPolicy
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
Analytics Hub Admin (roles/analyticshub.admin)
Analyticshub Editor (roles/analyticshub.editor)
Analytics Hub Listing Admin (roles/analyticshub.listingAdmin)
Analytics Hub Publisher (roles/analyticshub.publisher)
Analytics Hub Subscriber (roles/analyticshub.subscriber)
Analytics Hub Subscription Owner (roles/analyticshub.subscriptionOwner)
Analytics Hub Viewer (roles/analyticshub.viewer)
Security Admin (roles/iam.securityAdmin)
Security Auditor (roles/iam.securityAuditor)
Security Reviewer (roles/iam.securityReviewer)
Support User (roles/iam.supportUser)
analyticshub.listings.list
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
Analytics Hub Admin (roles/analyticshub.admin)
Analyticshub Editor (roles/analyticshub.editor)
Analytics Hub Listing Admin (roles/analyticshub.listingAdmin)
Analytics Hub Publisher (roles/analyticshub.publisher)
Analytics Hub Subscriber (roles/analyticshub.subscriber)
Analytics Hub Subscription Owner (roles/analyticshub.subscriptionOwner)
Analytics Hub Viewer (roles/analyticshub.viewer)
Security Admin (roles/iam.securityAdmin)
Security Auditor (roles/iam.securityAuditor)
Security Reviewer (roles/iam.securityReviewer)
Support User (roles/iam.supportUser)
analyticshub.listings.setIamPolicy
Owner (roles/owner)
Analytics Hub Admin (roles/analyticshub.admin)
Analytics Hub Listing Admin (roles/analyticshub.listingAdmin)
Security Admin (roles/iam.securityAdmin)
analyticshub.listings.subscribe
Owner (roles/owner)
Analytics Hub Subscriber (roles/analyticshub.subscriber)
analyticshub.listings.update
Owner (roles/owner)
Editor (roles/editor)
Analytics Hub Admin (roles/analyticshub.admin)
Analyticshub Editor (roles/analyticshub.editor)
Analytics Hub Listing Admin (roles/analyticshub.listingAdmin)
analyticshub.listings.viewSubscriptions
Owner (roles/owner)
Analytics Hub Admin (roles/analyticshub.admin)
Analytics Hub Listing Admin (roles/analyticshub.listingAdmin)
analyticshub.subscriptions.create
Owner (roles/owner)
Editor (roles/editor)
Analytics Hub Admin (roles/analyticshub.admin)
Analyticshub Editor (roles/analyticshub.editor)
Analytics Hub Subscription Owner (roles/analyticshub.subscriptionOwner)
analyticshub.subscriptions.delete
Owner (roles/owner)
Editor (roles/editor)
Analytics Hub Admin (roles/analyticshub.admin)
Analyticshub Editor (roles/analyticshub.editor)
Analytics Hub Subscription Owner (roles/analyticshub.subscriptionOwner)
analyticshub.subscriptions.get
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
Analytics Hub Admin (roles/analyticshub.admin)
Analyticshub Editor (roles/analyticshub.editor)
Analytics Hub Subscription Owner (roles/analyticshub.subscriptionOwner)
Support User (roles/iam.supportUser)
analyticshub.subscriptions.list
Owner (roles/owner)
Editor (roles/editor)
Viewer (roles/viewer)
Analytics Hub Admin (roles/analyticshub.admin)
Analyticshub Editor (roles/analyticshub.editor)
Analytics Hub Subscription Owner (roles/analyticshub.subscriptionOwner)
Security Admin (roles/iam.securityAdmin)
Security Auditor (roles/iam.securityAuditor)
Security Reviewer (roles/iam.securityReviewer)
Support User (roles/iam.supportUser)
analyticshub.subscriptions.update
Owner (roles/owner)
Editor (roles/editor)
Analytics Hub Admin (roles/analyticshub.admin)
Analyticshub Editor (roles/analyticshub.editor)
Analytics Hub Subscription Owner (roles/analyticshub.subscriptionOwner)
Permissions for BigQuery ML tasks
The following table describes the permissions needed for common BigQuery ML tasks.
Permission Description
bigquery.jobs.create
bigquery.models.create
bigquery.models.getData
bigquery.models.updateData
Create a new model using CREATE MODEL statement
bigquery.jobs.create
bigquery.models.create
bigquery.models.getData
bigquery.models.updateData
bigquery.models.updateMetadata
Replace an existing model using CREATE OR REPLACE MODEL statement
bigquery.models.delete Delete model using models.delete API
bigquery.jobs.create
bigquery.models.delete
Delete model using DROP MODEL statement
bigquery.models.getMetadata Get model metadata using models.get API
bigquery.models.list List models and metadata on models using models.list API
bigquery.models.updateMetadata Update model metadata using models.delete API. If setting or updating a non-zero expiration time for Model, bigquery.models.delete permission is also needed
bigquery.jobs.create
bigquery.models.getData Perform evaluation, prediction and model and feature inspections using functions such as ML.EVALUATE, ML.PREDICT, ML.TRAINING_INFO, and ML.WEIGHTS.
bigquery.jobs.create
bigquery.models.export Export a model
bigquery.models.updateTag Update Data Catalog tags for a model.
What's next
For more information about assigning roles at the dataset level, see Controlling access to datasets.
For more information about assigning roles at the table or view level, see Controlling access to tables and views.
Send feedback
Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.
Last updated 2026-04-07 UTC.
