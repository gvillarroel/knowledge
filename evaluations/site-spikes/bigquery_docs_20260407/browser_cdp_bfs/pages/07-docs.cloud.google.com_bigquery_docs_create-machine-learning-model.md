---
title: "Create an ML model in BigQuery ML by using SQL \_|\_ Google Cloud Documentation"
url: https://docs.cloud.google.com/bigquery/docs/create-machine-learning-model
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
Create a machine learning model in BigQuery ML by using SQL
This tutorial shows you how to create a logistic regression model by using BigQuery ML SQL queries.
BigQuery ML lets you create and train machine learning models in BigQuery by using SQL queries. This helps make machine learning more approachable by letting you use familiar tools like the BigQuery SQL editor, and also increases development speed by removing the need to move data into a separate machine learning environment.
In this tutorial, you use the sample Google Analytics sample dataset for BigQuery to create a model that predicts whether a website visitor will make a transaction. For information on the schema of the Analytics dataset, see BigQuery export schema in the Analytics Help Center.
To learn how to create models by using the Google Cloud console user interface, see work with models by using a UI.
Objectives
This tutorial shows you how to perform the following tasks:
Using the CREATE MODEL statement to create a binary logistic regression model.
Using the ML.EVALUATE function to evaluate the model.
Using the ML.PREDICT function to make predictions by using the model.
Costs
This tutorial uses billable components of Google Cloud, including the following:
BigQuery
BigQuery ML
For more information on BigQuery costs, see the BigQuery pricing page.
For more information on BigQuery ML costs, see BigQuery ML pricing.
Required roles
To create a model and run inference, you must be granted the following roles:
BigQuery Data Editor (roles/bigquery.dataEditor)
BigQuery User (roles/bigquery.user)
Before you begin
In the Google Cloud console, on the project selector page, select or create a Google Cloud project.
Roles required to select or create a project
Note: If you don't plan to keep the resources that you create in this procedure, create a project instead of selecting an existing project. After you finish these steps, you can delete the project, removing all resources associated with the project.
Go to project selector
Verify that billing is enabled for your Google Cloud project.
Make sure that you have the following role or roles on the project: BigQuery Data Editor, BigQuery Job User, Service Usage Admin
Check for the roles
Grant the roles
BigQuery is automatically enabled in new projects. To activate BigQuery in a pre-existing project, go to
Enable the BigQuery API.
Roles required to enable APIs
Enable the API
Create a dataset
Create a BigQuery dataset to store your ML model.
Create a logistic regression model
Create a logistic regression model using the Analytics sample dataset for BigQuery.
View the model's loss statistics
Machine learning is about creating a model that can use data to make a prediction. The model is essentially a function that takes inputs and applies calculations to the inputs to produce an output — a prediction.
Machine learning algorithms work by taking several examples where the prediction is already known (such as the historical data of user purchases) and iteratively adjusting various weights in the model so that the model's predictions match the true values. It does this by minimizing how wrong the model is using a metric called loss.
The expectation is that for each iteration, the loss should be decreasing, ideally to zero. A loss of zero means the model is 100% accurate.
When training the model, BigQuery ML automatically splits the input data into training and evaluation sets, in order to avoid overfitting the model. This is necessary so that the training algorithm doesn't fit itself so closely to the training data that it can't generalize to new examples.
Use the Google Cloud console to see how the model's loss changes over the model's training iterations:
In the Google Cloud console, go to the BigQuery page.
Go to BigQuery
In the left pane, click explore Explorer:
If you don't see the left pane, click last_page Expand left pane to open the pane.
In the Explorer pane, expand your project, click Datasets, and then click the bqml_tutorial dataset.
Click the Models tab, and then click the sample_model model.
Click the Training tab and look at the Loss graph. The Loss graph shows the change in the loss metric over the iterations on the training dataset. If you hold your cursor over the graph, you can see that there are lines for Training loss and Evaluation loss. Since you performed a logistic regression, the training loss value is calculated as log loss, using the training data. The evaluation loss is the log loss calculated on the evaluation data. Both loss types represent average loss values, averaged over all examples in the respective datasets for each iteration.
You can also see the results of the model training by using the ML.TRAINING_INFO function.
Evaluate the model
Evaluate the performance of the model by using the ML.EVALUATE function. The ML.EVALUATE function evaluates the predicted values generated by the model against the actual data. To calculate logistic regression specific metrics, you can use the ML.ROC_CURVE SQL function or the bigframes.ml.metrics.roc_curve BigQuery DataFrames function.
In this tutorial, you are using a binary classification model that detects transactions. The values in the label column are the two classes generated by the model: 0 (no transactions) and 1 (transaction made).
Use the model to predict outcomes
Use the model to predict the number of transactions made by website visitors from each country.
Predict purchases per user
Predict the number of transactions each website visitor will make.
Clean up
To avoid incurring charges to your Google Cloud account for the resources used on this page, follow these steps.
You can delete the project you created, or keep the project and delete the dataset.
Delete the dataset
Deleting your project removes all datasets and all tables in the project. If you prefer to reuse the project, you can delete the dataset you created in this tutorial:
In the Google Cloud console, go to the BigQuery page.
Go to BigQuery
In the left pane, click explore Explorer:
In the Explorer pane, expand your project, click Datasets, and then click the bqml_tutorial dataset that you created.
Click Delete.
In the Delete dataset dialog, confirm the delete command by typing delete.
Click Delete.
Delete the project
To delete the project:
Caution: Deleting a project has the following effects:
Everything in the project is deleted. If you used an existing project for the tasks in this document, when you delete it, you also delete any other work you've done in the project.
Custom project IDs are lost. When you created this project, you might have created a custom project ID that you want to use in the future. To preserve the URLs that use the project ID, such as an appspot.com URL, delete selected resources inside the project instead of deleting the whole project.
If you plan to explore multiple architectures, tutorials, or quickstarts, reusing projects can help you avoid exceeding project quota limits.
In the Google Cloud console, go to the Manage resources page.
Go to Manage resources
In the project list, select the project that you want to delete, and then click Delete.
In the dialog, type the project ID, and then click Shut down to delete the project.
What's next
To learn more about machine learning, see the Machine learning crash course.
For an overview of BigQuery ML, see Introduction to BigQuery ML.
To learn more about the Google Cloud console, see Using the Google Cloud console.
Send feedback
Except as otherwise noted, the content of this page is licensed under the Creative Commons Attribution 4.0 License, and code samples are licensed under the Apache 2.0 License. For details, see the Google Developers Site Policies. Java is a registered trademark of Oracle and/or its affiliates.
Last updated 2026-04-02 UTC.
