---
title: "What is the BigQuery Data Transfer Service? \_|\_ Google Cloud Documentation"
url: https://docs.cloud.google.com/bigquery/docs/dts-introduction
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
What is the BigQuery Data Transfer Service?
The BigQuery Data Transfer Service automates data movement into BigQuery on a scheduled, managed basis. Your analytics team can lay the foundation for a BigQuery data warehouse without writing a single line of code.
You can access the BigQuery Data Transfer Service using the:
Google Cloud console
bq command-line tool
BigQuery Data Transfer Service API
Tip: You can also use the Pipelines & Connections page to create a transfer using a streamlined workflow. This feature is in preview.
After you configure a data transfer, the BigQuery Data Transfer Service automatically loads data into BigQuery on a regular basis. You can also initiate data backfills to recover from any outages or gaps. You cannot use the BigQuery Data Transfer Service to transfer data out of BigQuery.
In addition to loading data into BigQuery, BigQuery Data Transfer Service is used for two BigQuery operations: dataset copies and scheduled queries.
Note: Subscribe to the BigQuery DTS announcements group to receive announcements related to the BigQuery Data Transfer Service.
Supported data sources
The BigQuery Data Transfer Service supports loading data from the following data sources:
SaaS platforms:
Salesforce
Salesforce Marketing Cloud
ServiceNow
Marketing platforms:
Facebook Ads
HubSpot (Preview)
Klaviyo (Preview)
Mailchimp (Preview)
Payment platforms:
PayPal (Preview)
Stripe (Preview)
Shopify (Preview)
Databases and data warehouses:
Amazon Redshift
Apache Hive (Preview)
Microsoft SQL Server (Preview)
MySQL
Oracle
PostgreSQL
Snowflake (Preview)
Teradata
Cloud storage:
Cloud Storage
Amazon Simple Storage Service (Amazon S3)
Azure Blob Storage
Google Services:
Campaign Manager
Comparison Shopping Service (CSS)Center (Preview)
Display & Video 360
Google Ads
Google Ad Manager
Google Analytics 4
Google Merchant Center (Preview)
Search Ads 360
Google Play
YouTube Channel
YouTube Content Owner
Data delivery SLO considerations
The Data Delivery SLO applies to automatically scheduled data transfers using the BigQuery Data Transfer Service from sources within Google Cloud.
For data transfers involving third-party or non-Google Cloud sources, service outages with these sources can impact performance with the BigQuery Data Transfer Service. As such, the Data Delivery SLO does not apply to BigQuery Data Transfer Service data transfers from non-Google Cloud sources.
Supported regions
Like BigQuery, the BigQuery Data Transfer Service is a multi-regional resource, with many additional single regions available.
A BigQuery dataset's locality is specified when you create a destination dataset to store the data transferred by the BigQuery Data Transfer Service. When you set up a transfer, the transfer configuration itself is set to the same location as the destination dataset. The BigQuery Data Transfer Service processes and stages data in the same location as the destination dataset.
The BigQuery Data Transfer Service supports data transfers from any region where your data is stored to any location where your destination dataset is located.
For detailed information about transfers and region compatibility for BigQuery Data Transfer Service, see Dataset locations and transfers. For supported regions for BigQuery, see Dataset locations.
Using reservation slots with data transfers
Jobs triggered by the BigQuery Data Transfer Service only use reservation slots if the project, folder, or organization is assigned to a reservation with any of the following job types:
Query jobs using QUERY
Load jobs using PIPELINE
Jobs that copy datasets don't use reservation slots.
Pricing
For information on BigQuery Data Transfer Service pricing, see the Pricing page.
Once data is transferred to BigQuery, standard BigQuery storage and query pricing applies.
Quotas
For information on BigQuery Data Transfer Service quotas, see the Quotas and limits page.
What's next
To learn how to create a transfer, see the documentation for your data source.
Send feedback
Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.
Last updated 2026-04-02 UTC.
