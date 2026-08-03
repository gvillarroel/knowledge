---
title: "Create custom query quotas \_|\_ BigQuery \_|\_ Google Cloud Documentation"
url: https://docs.cloud.google.com/bigquery/docs/custom-quotas
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
Create custom query quotas
This document describes how to set or modify custom query quotas to control costs. To learn how BigQuery analysts can estimate and control costs, see Estimate and control costs.
If you have multiple BigQuery projects and users, you can manage costs by requesting a custom quota that specifies a limit on the amount of data processed per day. Daily quotas are reset at midnight Pacific Time.
Custom quota is proactive, so you can't run an 11 TB query if you have a 10 TB quota. Creating a custom quota on processed data lets you control costs at the project level or at the user level.
To set custom cost controls, you can update one or both of the following query quotas:
QueryUsagePerDay: Project-level custom quotas limit the aggregate usage of all users in that project.
QueryUsagePerUserPerDay: User-level custom quota is separately applied to all users and service accounts within a project. Regardless of the per user limit, the total usage for all users in the project combined can never exceed the query usage per day limit.
Note: You can't assign a custom quota to an individual user or service account.
The default limit for the QueryUsagePerDay quota is 200 Tebibytes (TiB) of data processed per project per day. The default limit for the QueryUsagePerUserPerDay is unlimited. To check your current limits, see the Quotas page. You can change the limits anytime - custom overrides supersede the default limits.
Query usage quotas apply only to the on-demand query pricing model.
For more information about BigQuery quotas that you can set, see Quotas and limits.
Required role
To get the permission that you need to change your quota, ask your administrator to grant you the Quota Administrator (role/servicemanagement.quotaAdmin) IAM role on your project. For more information about granting roles, see Manage access to projects, folders, and organizations.
This predefined role contains the serviceusage.quotas.update permission, which is required to change your quota.
You might also be able to get this permission with custom roles or other predefined roles.
Set or modify custom quotas
You can set a custom quota or modify an existing custom quota for any quota displayed on the Quotas & System Limits page of the Google Cloud console. When you request a lower quota, the change takes effect within a few minutes. If you request a higher quota, your request goes through an approval process, which can take more time. For more information, see Request a quota adjustment.
Note: Custom quotas are approximate. The custom quotas feature provides an additional safeguard against excessive spending, but is not designed to strictly limit bytes processed. BigQuery might occasionally run a query that exceeds a quota. For greater price consistency, consider a reservation.
To set or update a custom cost control, such as limiting the amount of BigQuery data that can be processed each day, do the following:
In the Google Cloud console, open the IAM & Admin > Quotas & System Limits page:
Go to Quotas & System Limits
Use the Service filter in the Filter search box to filter for the BigQuery API.
Select the quotas that you want to adjust. For example, to limit the amount of data that be queried per day at both the project level and user level, select Query usage per day and Query usage per day per user. You might need to page through the list to find them. After you select a quota, a toolbar appears.
In the toolbar, click edit Edit. The Quota changes dialog opens.
If Unlimited is selected, deselect it.
Enter the quota value in TiB that you want in the New value field.
Click Done.
Click Submit request.
For more information about viewing and managing quotas, see View and manage quotas.
Note: Query usage is an accumulation of billed bytes. The query usage value on the Quotas & System Limits page might not match the billed bytes for the same period obtained from the INFORMATION_SCHEMA.JOBS view if some of the queries are charged at a higher rate compared to regular on-demand pricing. For example, regular query on-demand pricing might be charged at X $ per TiB, whereas another query operation, such as creating a logistic regression model, might be charged at a value of 50X $ per TiB, 50 times more than the regular price. In this case, the INFORMATION_SCHEMA.JOBS view might return 100 GiB of billed bytes, but the query usage reported on the Quotas & System Limits page would show 5 TiB of usage, 50 times more, because values for query usage are normalized against the regular on-demand pricing.
Returned error messages
After you set a custom quota, BigQuery returns an error when you exceed it:
If you exceed a project-level custom quota, BigQuery returns the usageQuotaExceeded error:
Custom quota exceeded: Your usage exceeded the custom quota for
QueryUsagePerDay, which is set by your administrator. For more information,
see https://cloud.google.com/bigquery/cost-controls
If the user exceeds a user-level custom quota, BigQuery returns a usageQuotaExceeded error with a different error message:
Custom quota exceeded: Your usage exceeded the custom quota for
QueryUsagePerUserPerDay, which is set by your administrator. For more
information, see https://cloud.google.com/bigquery/cost-controls
You can run your query from another project that has access to your datasets and that doesn't have a custom quota or hasn't yet exceeded it.
Example
Suppose you set the following custom quotas for a project with 10 users, one of which is a service account:
Project level: 50 TB per day
User level: 10 TB per day
Project-level custom quotas limit the aggregate usage of all users in that project. User-level custom quotas are separately applied to each user or service account within a project.
The following table describes the remaining quota as the 10 users run queries throughout the day.
Usage Remaining quota
Each of the 10 users queries 4 TBs Project level: 10 TBs remain.
User level: 6 TBs per user remain, but only up to 10 TBs total.
The service account queries another 6 TBs Project level: 4 TBs remain.
User level: The service account can no longer use BigQuery. 6 TBs per user remain for the other users, but only up to 4 TBs total.
One user queries another 4 TBs Project level: 0 TBs remain.
User level: Various TBs remain, but no one can use BigQuery because the project-level quota has been exceeded.
With no remaining quota, BigQuery stops working for everyone in that project.
What's next
Learn about BigQuery pricing.
Learn how to estimate and control costs.
Learn how to analyze BigQuery audit logs to monitor query costs and BigQuery usage.
To learn about billing, alerts, and visualizing data, see the following topics:
Create, edit, or delete budgets and budget alerts
Export Cloud Billing data to BigQuery
Visualize your costs with Looker Studio
Send feedback
Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.
Last updated 2026-04-02 UTC.
