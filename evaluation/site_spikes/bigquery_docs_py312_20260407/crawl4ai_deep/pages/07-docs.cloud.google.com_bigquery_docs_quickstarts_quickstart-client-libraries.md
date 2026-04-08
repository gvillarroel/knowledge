---
title: https://docs.cloud.google.com/bigquery/docs/quickstarts/quickstart-client-libraries
url: https://docs.cloud.google.com/bigquery/docs/quickstarts/quickstart-client-libraries
fetch_mode: crawl4ai
status_code: null
blocked_reason: null
---

<html>
<head>
    <title>Query a public dataset with the BigQuery client libraries  |  Google Cloud Documentation</title>


  </head>
  <body class="color-scheme--light viewport--desktop tenant--clouddocs">
  
    <a href="#main-content" class="skip-link button">
      
      Skip to main content
    </a>
    <section class="devsite-wrapper">
      <devsite-header>
  
    





















<div class="devsite-header--inner">
  <div class="devsite-top-logo-row-wrapper-wrapper">
    <div class="devsite-top-logo-row-wrapper">
      <div class="devsite-top-logo-row">
        <div class="devsite-product-name-wrapper">

  <a href="/" class="devsite-site-logo-link gc-analytics-event">
  
  <picture>
    
    <img src="https://www.gstatic.com/devrel-devsite/prod/v369eac9380f92e8fedc492e2689927bb3475d758266c381eee326d0b49a77481/clouddocs/images/lockup.svg" class="devsite-site-logo" alt="Google Cloud Documentation" width="300" height="71">
  </picture>
  
</a>



</div>
        <div class="devsite-top-logo-row-middle">
          <div class="devsite-header-upper-tabs">
            
              
              
  <devsite-tabs class="upper-tabs">

    <nav class="devsite-tabs-wrapper">
      
        
          <tab class="devsite-dropdown
    
    devsite-active
    devsite-clickable
    ">
  
    <a href="https://docs.cloud.google.com/docs" class="devsite-tabs-content gc-analytics-event ">
    Technology areas
  
    </a>
    
      <div class="devsite-tabs-dropdown">
    <div class="devsite-tabs-dropdown-content">
      
        <button class="devsite-tabs-close-button material-icons button-flat gc-analytics-event">close</button>
      
      
        <div class="devsite-tabs-dropdown-column
                    ">
          
            <ul class="devsite-tabs-dropdown-section
                       ">
              
              
              
                <li class="devsite-nav-item">
                  <a href="https://docs.cloud.google.com/docs/ai-ml">
                    
                    <div class="devsite-nav-item-title">
                      AI and ML
                    </div>
                    
                  </a>
                </li>
              
                <li class="devsite-nav-item">
                  <a href="https://docs.cloud.google.com/docs/application-development">
                    
                    <div class="devsite-nav-item-title">
                      Application development
                    </div>
                    
                  </a>
                </li>
              
                <li class="devsite-nav-item">
                  <a href="https://docs.cloud.google.com/docs/application-hosting">
                    
                    <div class="devsite-nav-item-title">
                      Application hosting
                    </div>
                    
                  </a>
                </li>
              
                <li class="devsite-nav-item">
                  <a href="https://docs.cloud.google.com/docs/compute-area">
                    
                    <div class="devsite-nav-item-title">
                      Compute
                    </div>
                    
                  </a>
                </li>
              
                <li class="devsite-nav-item">
                  <a href="https://docs.cloud.google.com/docs/data">
                    
                    <div class="devsite-nav-item-title">
                      Data analytics and pipelines
                    </div>
                    
                  </a>
                </li>
              
                <li class="devsite-nav-item">
                  <a href="https://docs.cloud.google.com/docs/databases">
                    
                    <div class="devsite-nav-item-title">
                      Databases
                    </div>
                    
                  </a>
                </li>
              
                <li class="devsite-nav-item">
                  <a href="https://docs.cloud.google.com/docs/dhm-cloud">
                    
                    <div class="devsite-nav-item-title">
                      Distributed, hybrid, and multicloud
                    </div>
                    
                  </a>
                </li>
              
                <li class="devsite-nav-item">
                  <a href="https://docs.cloud.google.com/docs/industry">
                    
                    <div class="devsite-nav-item-title">
                      Industry solutions
                    </div>
                    
                  </a>
                </li>
              
                <li class="devsite-nav-item">
                  <a href="https://docs.cloud.google.com/docs/migration">
                    
                    <div class="devsite-nav-item-title">
                      Migration
                    </div>
                    
                  </a>
                </li>
              
                <li class="devsite-nav-item">
                  <a href="https://docs.cloud.google.com/docs/networking">
                    
                    <div class="devsite-nav-item-title">
                      Networking
                    </div>
                    
                  </a>
                </li>
              
                <li class="devsite-nav-item">
                  <a href="https://docs.cloud.google.com/docs/observability">
                    
                    <div class="devsite-nav-item-title">
                      Observability and monitoring
                    </div>
                    
                  </a>
                </li>
              
                <li class="devsite-nav-item">
                  <a href="https://docs.cloud.google.com/docs/security">
                    
                    <div class="devsite-nav-item-title">
                      Security
                    </div>
                    
                  </a>
                </li>
              
                <li class="devsite-nav-item">
                  <a href="https://docs.cloud.google.com/docs/storage">
                    
                    <div class="devsite-nav-item-title">
                      Storage
                    </div>
                    
                  </a>
                </li>
              
            </ul>
          
        </div>
      
    </div>
  </div>
</tab>
        
      
        
          <tab class="devsite-dropdown
    
    
    devsite-clickable
    ">
  
    <a href="https://docs.cloud.google.com/docs/cross-product-overviews" class="devsite-tabs-content gc-analytics-event ">
    Cross-product tools
  
    </a>
    
      <div class="devsite-tabs-dropdown">
    <div class="devsite-tabs-dropdown-content">
      
        <button class="devsite-tabs-close-button material-icons button-flat gc-analytics-event">close</button>
      
      
        <div class="devsite-tabs-dropdown-column
                    ">
          
            <ul class="devsite-tabs-dropdown-section
                       ">
              
              
              
                <li class="devsite-nav-item">
                  <a href="https://docs.cloud.google.com/docs/access-resources">
                    
                    <div class="devsite-nav-item-title">
                      Access and resources management
                    </div>
                    
                  </a>
                </li>
              
                <li class="devsite-nav-item">
                  <a href="https://docs.cloud.google.com/docs/costs-usage">
                    
                    <div class="devsite-nav-item-title">
                      Costs and usage management
                    </div>
                    
                  </a>
                </li>
              
                <li class="devsite-nav-item">
                  <a href="https://docs.cloud.google.com/docs/iac">
                    
                    <div class="devsite-nav-item-title">
                      Infrastructure as code
                    </div>
                    
                  </a>
                </li>
              
                <li class="devsite-nav-item">
                  <a href="https://docs.cloud.google.com/docs/devtools">
                    
                    <div class="devsite-nav-item-title">
                      SDK, languages, frameworks, and tools
                    </div>
                    
                  </a>
                </li>
              
            </ul>
          
        </div>
      
    </div>
  </div>
</tab>
        
      
    </nav>

  </devsite-tabs>

            
           </div>
          
<devsite-search>
  <form class="devsite-search-form">
    <div class="devsite-search-container">
      <div class="devsite-searchbox">
        <input class="devsite-search-field devsite-search-query">
          <div class="devsite-search-shortcut-icon-container">
            <kbd class="devsite-search-shortcut-icon">/</kbd>
          </div>
      </div>
    </div>
  </form>
  </devsite-search>

        </div>

        

  

  
    <a class="devsite-header-link devsite-top-button button gc-analytics-event button-with-icon" href="//console.cloud.google.com/">
  Console
</a>
  

  
    <devsite-language-selector>
  <ul>
    
    
    <li>
      <a>English</a>
    </li>
    
    <li>
      <a>Deutsch</a>
    </li>
    
    <li>
      <a>Español</a>
    </li>
    
    <li>
      <a>Español – América Latina</a>
    </li>
    
    <li>
      <a>Français</a>
    </li>
    
    <li>
      <a>Indonesia</a>
    </li>
    
    <li>
      <a>Italiano</a>
    </li>
    
    <li>
      <a>Português</a>
    </li>
    
    <li>
      <a>Português – Brasil</a>
    </li>
    
    <li>
      <a>עברית</a>
    </li>
    
    <li>
      <a>中文 – 简体</a>
    </li>
    
    <li>
      <a>中文 – 繁體</a>
    </li>
    
    <li>
      <a>日本語</a>
    </li>
    
    <li>
      <a>한국어</a>
    </li>
    
  </ul>
</devsite-language-selector>




        
          </div>
    </div>
  </div>



  <div class="devsite-collapsible-section
    ">
    <div class="devsite-header-background">
      
        
          <div class="devsite-product-id-row">
            <div class="devsite-product-description-row">
              
                
                <div class="devsite-product-id">
                  
                    
  
  <a href="https://docs.cloud.google.com/bigquery/docs">
    
  <div class="devsite-product-logo-container">
  
    <picture>
      
      <img class="devsite-product-logo" alt="" src="https://docs.cloud.google.com/_static/clouddocs/images/icons/products/bigquery-color.svg">
    </picture>
  
  </div>
  
  </a>
  

                  
                  
                  
                    <ul class="devsite-breadcrumb-list">
  
  <li class="devsite-breadcrumb-item
             ">
    
    
    
      
        
  <a href="https://docs.cloud.google.com/bigquery/docs" class="devsite-breadcrumb-link gc-analytics-event">
    
          BigQuery
        
  </a>
  
      
    
  </li>
  
</ul>
                </div>
                
              
              
            </div>
            
              <div class="devsite-product-button-row">
  

  
  <a href="//console.cloud.google.com/freetrial" class="cloud-free-trial-button button button-primary
      ">Start free</a>

</div>
            
          </div>
          
        
      
      
        <div class="devsite-doc-set-nav-row">
          
          
            
            
  <devsite-tabs class="lower-tabs">

    <nav class="devsite-tabs-wrapper">
      
        
          <tab>
            
    <a href="https://docs.cloud.google.com/bigquery/docs" class="devsite-tabs-content gc-analytics-event ">
    Overview
  
    </a>
    
  
          </tab>
        
      
        
          <tab class="devsite-active">
            
    <a href="https://docs.cloud.google.com/bigquery/docs/introduction" class="devsite-tabs-content gc-analytics-event ">
    Guides
  
    </a>
    
  
          </tab>
        
      
        
          <tab>
            
    <a href="https://docs.cloud.google.com/bigquery/quotas" class="devsite-tabs-content gc-analytics-event ">
    Reference
  
    </a>
    
  
          </tab>
        
      
        
          <tab>
            
    <a href="https://docs.cloud.google.com/bigquery/docs/samples" class="devsite-tabs-content gc-analytics-event ">
    Samples
  
    </a>
    
  
          </tab>
        
      
        
          <tab>
            
    <a href="https://docs.cloud.google.com/bigquery/docs/release-notes" class="devsite-tabs-content gc-analytics-event ">
    Resources
  
    </a>
    
  
          </tab>
        
      
    </nav>

  </devsite-tabs>

          
          
        </div>
      
    </div>
  </div>

</div>



  

  
</devsite-header>
      <devsite-book-nav>
        
          





















<div class="devsite-book-nav-filter">
  <input>
  
  </div>

<nav class="devsite-book-nav devsite-nav nocontent">
  <div class="devsite-mobile-header">
    <div class="devsite-product-name-wrapper">

  <a href="/" class="devsite-site-logo-link gc-analytics-event">
  
  <picture>
    
    <img src="https://www.gstatic.com/devrel-devsite/prod/v369eac9380f92e8fedc492e2689927bb3475d758266c381eee326d0b49a77481/clouddocs/images/lockup.svg" class="devsite-site-logo" alt="Google Cloud Documentation">
  </picture>
  
</a>


</div>
  </div>

  <div class="devsite-book-nav-wrapper">
    <div class="devsite-mobile-nav-top">
      
        <ul class="devsite-nav-list">
          
            <li class="devsite-nav-item">
              
  
  <a href="/docs" class="devsite-nav-title gc-analytics-event
              
              devsite-nav-active">
  
    <span class="devsite-nav-text">
      Technology areas
   </span>
    
  
  </a>
  

  
    <ul class="devsite-nav-responsive-tabs devsite-nav-has-menu
               ">
      
<li class="devsite-nav-item">

  
  <span class="devsite-nav-title">
  
    <span class="devsite-nav-text">
      More
   </span>
    
    </span>
  

</li>

    </ul>
  
              
                <ul class="devsite-nav-responsive-tabs">
                  
                    
                    
                    
                    <li class="devsite-nav-item">
                      
  
  <a href="/bigquery/docs" class="devsite-nav-title gc-analytics-event
              
              ">
  
    <span class="devsite-nav-text">
      Overview
   </span>
    
  
  </a>
  

  
                    </li>
                  
                    
                    
                    
                    <li class="devsite-nav-item">
                      
  
  <a href="/bigquery/docs/introduction" class="devsite-nav-title gc-analytics-event
              
              devsite-nav-active">
  
    <span class="devsite-nav-text">
      Guides
   </span>
    
  
  </a>
  

  
                    </li>
                  
                    
                    
                    
                    <li class="devsite-nav-item">
                      
  
  <a href="/bigquery/quotas" class="devsite-nav-title gc-analytics-event
              
              ">
  
    <span class="devsite-nav-text">
      Reference
   </span>
    
  
  </a>
  

  
                    </li>
                  
                    
                    
                    
                    <li class="devsite-nav-item">
                      
  
  <a href="/bigquery/docs/samples" class="devsite-nav-title gc-analytics-event
              
              ">
  
    <span class="devsite-nav-text">
      Samples
   </span>
    
  
  </a>
  

  
                    </li>
                  
                    
                    
                    
                    <li class="devsite-nav-item">
                      
  
  <a href="/bigquery/docs/release-notes" class="devsite-nav-title gc-analytics-event
              
              ">
  
    <span class="devsite-nav-text">
      Resources
   </span>
    
  
  </a>
  

  
                    </li>
                  
                </ul>
              
            </li>
          
            <li class="devsite-nav-item">
              
  
  <a href="/docs/cross-product-overviews" class="devsite-nav-title gc-analytics-event
              
              ">
  
    <span class="devsite-nav-text">
      Cross-product tools
   </span>
    
  
  </a>
  

  
    <ul class="devsite-nav-responsive-tabs devsite-nav-has-menu
               ">
      
<li class="devsite-nav-item">

  
  <span class="devsite-nav-title">
  
    <span class="devsite-nav-text">
      More
   </span>
    
    </span>
  

</li>

    </ul>
  
              
            </li>
          
          
    
    
<li class="devsite-nav-item">

  
  <a href="//console.cloud.google.com/" class="devsite-nav-title gc-analytics-event button-with-icon">
  
    <span class="devsite-nav-text">
      Console
   </span>
    
  
  </a>
  

</li>

  
          
        </ul>
      
    </div>
    
      <div class="devsite-mobile-nav-bottom">
        
          
          <ul class="devsite-nav-list">
            <li class="devsite-nav-item
           devsite-nav-heading"><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Discover</span>
      </div></li>

  <li class="devsite-nav-item"><a href="/bigquery/docs/introduction" class="devsite-nav-title"><span class="devsite-nav-text">Product overview</span></a></li>

  <li class="devsite-nav-item"><a href="/bigquery/docs/sandbox" class="devsite-nav-title"><span class="devsite-nav-text">Try BigQuery using the sandbox</span></a></li>

  <li class="devsite-nav-item
           devsite-nav-heading"><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Get started</span>
      </div></li>

  <li class="devsite-nav-item"><a href="/bigquery/docs/console-video-learning" class="devsite-nav-title"><span class="devsite-nav-text">Console walkthroughs and videos</span></a></li>

  <li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Use the console</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/bigquery-web-ui" class="devsite-nav-title"><span class="devsite-nav-text">Explore the console</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/quickstarts/load-data-console" class="devsite-nav-title"><span class="devsite-nav-text">Load and query data</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/reservations-get-started" class="devsite-nav-title"><span class="devsite-nav-text">Create reservations</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/dataframes-quickstart" class="devsite-nav-title"><span class="devsite-nav-text">Try DataFrames</span></a></li>
</ul>
</div></li>

  <li class="devsite-nav-item"><a href="/bigquery/docs/quickstarts/load-data-bq" class="devsite-nav-title"><span class="devsite-nav-text">Use the bq CLI tool</span></a></li>

  <li class="devsite-nav-item"><a href="/bigquery/docs/quickstarts/quickstart-client-libraries" class="devsite-nav-title"><span class="devsite-nav-text">Use the client libraries</span></a></li>

  <li class="devsite-nav-item
           devsite-nav-heading"><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Plan</span>
      </div></li>

  <li class="devsite-nav-item"><a href="/bigquery/docs/resource-hierarchy" class="devsite-nav-title"><span class="devsite-nav-text">Organize resources</span></a></li>

  <li class="devsite-nav-item"><a href="/bigquery/docs/service-dependencies" class="devsite-nav-title"><span class="devsite-nav-text">API dependencies</span></a></li>

  <li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Datasets</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/datasets-intro" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/datasets" class="devsite-nav-title"><span class="devsite-nav-text">Create datasets</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/listing-datasets" class="devsite-nav-title"><span class="devsite-nav-text">List datasets</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/data-replication" class="devsite-nav-title"><span class="devsite-nav-text">Cross-region replication</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/managed-disaster-recovery" class="devsite-nav-title"><span class="devsite-nav-text">Managed disaster recovery</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/disaster-recovery-migration" class="devsite-nav-title"><span class="devsite-nav-text">Migrate to managed disaster recovery</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/time-travel" class="devsite-nav-title"><span class="devsite-nav-text">Dataset data retention</span></a></li>
</ul>
</div></li>

  <li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Tables</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">BigQuery tables</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/tables-intro" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/tables" class="devsite-nav-title"><span class="devsite-nav-text">Create and use tables</span></a></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Specify table schemas</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/schemas" class="devsite-nav-title"><span class="devsite-nav-text">Specify a schema</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/nested-repeated" class="devsite-nav-title"><span class="devsite-nav-text">Specify nested and repeated columns</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/default-values" class="devsite-nav-title"><span class="devsite-nav-text">Specify default column values</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/objectref-columns" class="devsite-nav-title"><span class="devsite-nav-text">Specify ObjectRef values</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Segment with partitioned tables</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/partitioned-tables" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/creating-partitioned-tables" class="devsite-nav-title"><span class="devsite-nav-text">Create partitioned tables</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/managing-partitioned-tables" class="devsite-nav-title"><span class="devsite-nav-text">Manage partitioned tables</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/querying-partitioned-tables" class="devsite-nav-title"><span class="devsite-nav-text">Query partitioned tables</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Optimize with clustered tables</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/clustered-tables" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/creating-clustered-tables" class="devsite-nav-title"><span class="devsite-nav-text">Create clustered tables</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/manage-clustered-tables" class="devsite-nav-title"><span class="devsite-nav-text">Manage clustered tables</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/querying-clustered-tables" class="devsite-nav-title"><span class="devsite-nav-text">Query clustered tables</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/metadata-indexing-managed-tables" class="devsite-nav-title"><span class="devsite-nav-text">Use metadata indexing</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">External tables</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/external-data-sources" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Types of external tables</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/biglake-intro" class="devsite-nav-title"><span class="devsite-nav-text">BigLake external tables</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/omni-introduction" class="devsite-nav-title"><span class="devsite-nav-text">BigQuery Omni</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/object-table-introduction" class="devsite-nav-title"><span class="devsite-nav-text">Object tables</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/external-tables" class="devsite-nav-title"><span class="devsite-nav-text">External tables</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/external-table-definition" class="devsite-nav-title"><span class="devsite-nav-text">External table definition file</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/hive-partitioned-queries" class="devsite-nav-title"><span class="devsite-nav-text">Externally partitioned data</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/metadata-caching-external-tables" class="devsite-nav-title"><span class="devsite-nav-text">Use metadata caching</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/omni-aws-create-external-table" class="devsite-nav-title"><span class="devsite-nav-text">Amazon S3 BigLake external tables</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/iceberg-external-tables" class="devsite-nav-title"><span class="devsite-nav-text">Apache Iceberg external tables</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/omni-azure-create-external-table" class="devsite-nav-title"><span class="devsite-nav-text">Azure Blob Storage BigLake tables</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/create-bigtable-external-table" class="devsite-nav-title"><span class="devsite-nav-text">Bigtable external table</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/create-cloud-storage-table-biglake" class="devsite-nav-title"><span class="devsite-nav-text">BigLake external tables for Cloud Storage</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/object-tables" class="devsite-nav-title"><span class="devsite-nav-text">Cloud Storage object tables</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/external-data-cloud-storage" class="devsite-nav-title"><span class="devsite-nav-text">Cloud Storage external tables</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/create-delta-lake-table" class="devsite-nav-title"><span class="devsite-nav-text">Delta Lake BigLake tables</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/external-data-drive" class="devsite-nav-title"><span class="devsite-nav-text">Google Drive external tables</span></a></li>
</ul>
</div></li>
</ul>
</div></li>

  <li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Views</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/logical-materialized-view-overview" class="devsite-nav-title"><span class="devsite-nav-text">Overview</span></a></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Logical views</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/views-intro" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/views" class="devsite-nav-title"><span class="devsite-nav-text">Create logical views</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Materialized views</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/materialized-views-intro" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/materialized-views-create" class="devsite-nav-title"><span class="devsite-nav-text">Create materialized views</span></a></li>
</ul>
</div></li>
</ul>
</div></li>

  <li class="devsite-nav-item
           devsite-nav-heading"><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Load, transform, and export</span>
      </div></li>

  <li class="devsite-nav-item"><a href="/bigquery/docs/load-transform-export-intro" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>

  <li class="devsite-nav-item
           devsite-nav-preview"><a href="/bigquery/docs/data-engineering-agent-pipelines" class="devsite-nav-title"><span class="devsite-nav-text">Build a data pipeline with Data Engineering Agent</span></a></li>

  <li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Migrate data</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/migration/migration-overview" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/migration-intro" class="devsite-nav-title"><span class="devsite-nav-text">BigQuery Migration Service</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/migration-assessment" class="devsite-nav-title"><span class="devsite-nav-text">Migration assessment</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/migration/schema-data-overview" class="devsite-nav-title"><span class="devsite-nav-text">Migrate schema and data</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/migration/pipelines" class="devsite-nav-title"><span class="devsite-nav-text">Migrate data pipelines</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/migration-custom-org-policies" class="devsite-nav-title"><span class="devsite-nav-text">Use custom organization policies</span></a></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Migrate SQL</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/interactive-sql-translator" class="devsite-nav-title"><span class="devsite-nav-text">Translate SQL queries interactively</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/api-sql-translator" class="devsite-nav-title"><span class="devsite-nav-text">Translate SQL queries using the API</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/batch-sql-translator" class="devsite-nav-title"><span class="devsite-nav-text">Translate SQL queries in batch</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/generate-metadata" class="devsite-nav-title"><span class="devsite-nav-text">Generate metadata for translation and assessment</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/config-yaml-translation" class="devsite-nav-title"><span class="devsite-nav-text">Transform SQL translations with YAML</span></a></li>
<li class="devsite-nav-item
           devsite-nav-preview"><a href="/bigquery/docs/output-name-mapping" class="devsite-nav-title"><span class="devsite-nav-text">Map SQL object names for batch translation</span></a></li>
</ul>
</div></li>
</ul>
</div></li>

  <li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Load data</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/loading-data" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/pipeline-connection-page" class="devsite-nav-title"><span class="devsite-nav-text">Create data integration workflows using the BigQuery web UI</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/storage_overview" class="devsite-nav-title"><span class="devsite-nav-text">Storage overview</span></a></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">BigQuery Data Transfer Service</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/dts-introduction" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/dts-data-sources-intro" class="devsite-nav-title"><span class="devsite-nav-text">Supported data sources</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/dts-locations" class="devsite-nav-title"><span class="devsite-nav-text">Data location and transfers</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/dts-authentication-authorization" class="devsite-nav-title"><span class="devsite-nav-text">Authorize transfers</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/enable-transfer-service" class="devsite-nav-title"><span class="devsite-nav-text">Enable transfers</span></a></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Set up network connections</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/cloud-sql-instance-access" class="devsite-nav-title"><span class="devsite-nav-text">Cloud SQL instance access</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/aws-vpn-network-attachment" class="devsite-nav-title"><span class="devsite-nav-text">AWS VPN and network attachment</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/azure-vpn-network-attachment" class="devsite-nav-title"><span class="devsite-nav-text">Azure VPN and network attachment</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/working-with-transfers" class="devsite-nav-title"><span class="devsite-nav-text">Manage transfers</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/transfer-run-notifications" class="devsite-nav-title"><span class="devsite-nav-text">Transfer run notifications</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/transfer-troubleshooting" class="devsite-nav-title"><span class="devsite-nav-text">Troubleshoot transfer configurations</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/use-service-accounts" class="devsite-nav-title"><span class="devsite-nav-text">Use service accounts</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/third-party-transfer" class="devsite-nav-title"><span class="devsite-nav-text">Use third-party transfers</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/transfer-custom-constraints" class="devsite-nav-title"><span class="devsite-nav-text">Use custom organization policies</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/transfer-changes" class="devsite-nav-title"><span class="devsite-nav-text">Data source change log</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/event-driven-transfer" class="devsite-nav-title"><span class="devsite-nav-text">Event-driven transfers</span></a></li>
<li class="devsite-nav-item
           devsite-nav-preview"><a href="/bigquery/docs/iceberg-ingestion" class="devsite-nav-title"><span class="devsite-nav-text">Transfer data into BigLake Iceberg tables</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Batch load data</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/batch-loading-data" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/schema-detect" class="devsite-nav-title"><span class="devsite-nav-text">Auto-detect schemas</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/loading-data-cloud-storage-avro" class="devsite-nav-title"><span class="devsite-nav-text">Load Avro data</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/loading-data-cloud-storage-parquet" class="devsite-nav-title"><span class="devsite-nav-text">Load Parquet data</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/loading-data-cloud-storage-orc" class="devsite-nav-title"><span class="devsite-nav-text">Load ORC data</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/loading-data-cloud-storage-csv" class="devsite-nav-title"><span class="devsite-nav-text">Load CSV data</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/loading-data-cloud-storage-json" class="devsite-nav-title"><span class="devsite-nav-text">Load JSON data</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/hive-partitioned-loads-gcs" class="devsite-nav-title"><span class="devsite-nav-text">Load externally partitioned data</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/loading-data-cloud-datastore" class="devsite-nav-title"><span class="devsite-nav-text">Load data from a Datastore export</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/loading-data-cloud-firestore" class="devsite-nav-title"><span class="devsite-nav-text">Load data from a Firestore export</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/write-api-batch-load" class="devsite-nav-title"><span class="devsite-nav-text">Load data using the Storage Write API</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/load-data-partitioned-tables" class="devsite-nav-title"><span class="devsite-nav-text">Load data into partitioned tables</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Write and read data with the Storage API</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/reference/storage" class="devsite-nav-title"><span class="devsite-nav-text">Read data with the Storage Read API</span></a></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Write data with the Storage Write API</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/write-api" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/write-api-streaming" class="devsite-nav-title"><span class="devsite-nav-text">Stream data with the Storage Write API</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/write-api-batch" class="devsite-nav-title"><span class="devsite-nav-text">Batch load data with the Storage Write API</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/write-api-best-practices" class="devsite-nav-title"><span class="devsite-nav-text">Best practices</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/supported-data-types" class="devsite-nav-title"><span class="devsite-nav-text">Supported protocol buffer and Arrow data types</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/change-data-capture" class="devsite-nav-title"><span class="devsite-nav-text">Stream updates with change data capture ingestion</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/streaming-data-into-bigquery" class="devsite-nav-title"><span class="devsite-nav-text">Use the legacy streaming API</span></a></li>
</ul>
</div></li>
</ul>
</div></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/load-data-google-services" class="devsite-nav-title"><span class="devsite-nav-text">Load data from other Google services</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/automatic-discovery" class="devsite-nav-title"><span class="devsite-nav-text">Discover and catalog Cloud Storage data</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/load-data-third-party" class="devsite-nav-title"><span class="devsite-nav-text">Load data using third-party apps</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/load-data-using-cross-cloud-transfer" class="devsite-nav-title"><span class="devsite-nav-text">Load data using cross-cloud operations</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/optimize-load-jobs" class="devsite-nav-title"><span class="devsite-nav-text">Optimize load jobs</span></a></li>
</ul>
</div></li>

  <li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Transform data</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/transform-intro" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Prepare data</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/data-prep-introduction" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/data-prep-get-suggestions" class="devsite-nav-title"><span class="devsite-nav-text">Prepare data with Gemini</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/data-manipulation-language" class="devsite-nav-title"><span class="devsite-nav-text">Transform with DML</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/using-dml-with-partitioned-tables" class="devsite-nav-title"><span class="devsite-nav-text">Transform data in partitioned tables</span></a></li>
<li class="devsite-nav-item
           devsite-nav-preview"><a href="/bigquery/docs/change-history" class="devsite-nav-title"><span class="devsite-nav-text">Work with change history</span></a></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Transform data with pipelines</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/pipelines-introduction" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/create-pipelines" class="devsite-nav-title"><span class="devsite-nav-text">Create pipelines</span></a></li>
</ul>
</div></li>
</ul>
</div></li>

  <li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Export data</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/export-intro" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/export-file" class="devsite-nav-title"><span class="devsite-nav-text">Export query results</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/exporting-data" class="devsite-nav-title"><span class="devsite-nav-text">Export to Cloud Storage</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/export-to-bigtable" class="devsite-nav-title"><span class="devsite-nav-text">Export to Bigtable</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/export-to-spanner" class="devsite-nav-title"><span class="devsite-nav-text">Export to Spanner</span></a></li>
<li class="devsite-nav-item
           devsite-nav-preview"><a href="/bigquery/docs/export-to-pubsub" class="devsite-nav-title"><span class="devsite-nav-text">Export to Pub/Sub</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/protobuf-export" class="devsite-nav-title"><span class="devsite-nav-text">Export as Protobuf columns</span></a></li>
</ul>
</div></li>

  <li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">ELT tutorials</span>
      </div>
<ul class="devsite-nav-section"><li class="devsite-nav-item"><a href="/bigquery/docs/elt-tutorial-marketing" class="devsite-nav-title"><span class="devsite-nav-text">Build ELT for marketing analytics data</span></a></li></ul>
</div></li>

  <li class="devsite-nav-item
           devsite-nav-heading"><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Analyze</span>
      </div></li>

  <li class="devsite-nav-item"><a href="/bigquery/docs/query-overview" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>

  <li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Explore your data</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item
           devsite-nav-preview"><a href="/bigquery/docs/search-resources" class="devsite-nav-title"><span class="devsite-nav-text">Search for resources</span></a></li>
<li class="devsite-nav-item
           devsite-nav-preview"><a href="/bigquery/docs/table-explorer" class="devsite-nav-title"><span class="devsite-nav-text">Use table explorer</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/data-profile-scan" class="devsite-nav-title"><span class="devsite-nav-text">Profile your data</span></a></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Data insights</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/data-insights" class="devsite-nav-title"><span class="devsite-nav-text">About data insights</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/generate-table-insights" class="devsite-nav-title"><span class="devsite-nav-text">Generate table insights</span></a></li>
<li class="devsite-nav-item
           devsite-nav-preview"><a href="/bigquery/docs/generate-dataset-insights" class="devsite-nav-title"><span class="devsite-nav-text">Generate dataset insights</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/data-canvas" class="devsite-nav-title"><span class="devsite-nav-text">Analyze with a data canvas</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/gemini-analyze-data" class="devsite-nav-title"><span class="devsite-nav-text">Analyze data with Gemini</span></a></li>
<li class="devsite-nav-item
           devsite-nav-preview"><a href="/bigquery/docs/develop-with-gemini-cli" class="devsite-nav-title"><span class="devsite-nav-text">Analyze data with the Gemini CLI</span></a></li>
</ul>
</div></li>

  <li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Analyze your data</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/running-queries" class="devsite-nav-title"><span class="devsite-nav-text">Run a query</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/write-sql-gemini" class="devsite-nav-title"><span class="devsite-nav-text">Write queries with Gemini</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/writing-results" class="devsite-nav-title"><span class="devsite-nav-text">Write query results</span></a></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Query data with SQL</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/introduction-sql" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/arrays" class="devsite-nav-title"><span class="devsite-nav-text">Arrays</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/json-data" class="devsite-nav-title"><span class="devsite-nav-text">JSON data</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/multi-statement-queries" class="devsite-nav-title"><span class="devsite-nav-text">Multi-statement queries</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/parameterized-queries" class="devsite-nav-title"><span class="devsite-nav-text">Parameterized queries</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/pipe-syntax-guide" class="devsite-nav-title"><span class="devsite-nav-text">Pipe syntax</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/analyze-data-pipe-syntax" class="devsite-nav-title"><span class="devsite-nav-text">Analyze data using pipe syntax</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/recursive-ctes" class="devsite-nav-title"><span class="devsite-nav-text">Recursive CTEs</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/sketches" class="devsite-nav-title"><span class="devsite-nav-text">Sketches</span></a></li>
<li class="devsite-nav-item
           devsite-nav-preview"><a href="/bigquery/docs/table-sampling" class="devsite-nav-title"><span class="devsite-nav-text">Table sampling</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/working-with-time-series" class="devsite-nav-title"><span class="devsite-nav-text">Time series</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/transactions" class="devsite-nav-title"><span class="devsite-nav-text">Transactions</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/querying-wildcard-tables" class="devsite-nav-title"><span class="devsite-nav-text">Wildcard tables</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Use notebooks</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/programmatic-analysis" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Use Colab notebooks</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/notebooks-introduction" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/create-notebooks" class="devsite-nav-title"><span class="devsite-nav-text">Create notebooks</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/explore-data-colab" class="devsite-nav-title"><span class="devsite-nav-text">Explore query results</span></a></li>
<li class="devsite-nav-item
           devsite-nav-preview"><a href="/bigquery/docs/visualize-data-colab" class="devsite-nav-title"><span class="devsite-nav-text">Visualize query results</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/use-spark" class="devsite-nav-title"><span class="devsite-nav-text">Use Spark</span></a></li>
<li class="devsite-nav-item
           devsite-nav-preview"><a href="/bigquery/docs/colab-data-science-agent" class="devsite-nav-title"><span class="devsite-nav-text">Use Colab Data Science Agent</span></a></li>
</ul>
</div></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Use DataFrames</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/bigquery-dataframes-introduction" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/install-dataframes" class="devsite-nav-title"><span class="devsite-nav-text">Install DataFrames</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/dataframes-data-manipulation" class="devsite-nav-title"><span class="devsite-nav-text">Manipulate data</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/dataframes-custom-python-functions" class="devsite-nav-title"><span class="devsite-nav-text">Customize Python functions</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/dataframes-ml-ai" class="devsite-nav-title"><span class="devsite-nav-text">Use ML and AI</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/dataframes-data-types" class="devsite-nav-title"><span class="devsite-nav-text">Use the data type system</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/dataframes-sessions-io" class="devsite-nav-title"><span class="devsite-nav-text">Manage sessions and I/O</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/dataframes-visualizations" class="devsite-nav-title"><span class="devsite-nav-text">Visualize graphs</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/dataframes-dbt" class="devsite-nav-title"><span class="devsite-nav-text">Use DataFrames in dbt</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/dataframes-performance" class="devsite-nav-title"><span class="devsite-nav-text">Optimize performance</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/migrate-dataframes" class="devsite-nav-title"><span class="devsite-nav-text">Migrate to DataFrames version 2.0</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Use geospatial analytics</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/geospatial-intro" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/geospatial-data" class="devsite-nav-title"><span class="devsite-nav-text">Work with geospatial analytics</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/raster-data" class="devsite-nav-title"><span class="devsite-nav-text">Work with raster data</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/best-practices-spatial-analysis" class="devsite-nav-title"><span class="devsite-nav-text">Best practices for spatial analysis</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/geospatial-visualize" class="devsite-nav-title"><span class="devsite-nav-text">Visualize geospatial data</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/grid-systems-spatial-analysis" class="devsite-nav-title"><span class="devsite-nav-text">Grid systems for spatial analysis</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/reference/standard-sql/geography_functions" class="devsite-nav-title"><span class="devsite-nav-text">Geospatial analytics syntax reference</span></a></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Geospatial analytics tutorials</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/geospatial-get-started" class="devsite-nav-title"><span class="devsite-nav-text">Get started with geospatial analytics</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/geospatial-tutorial-hurricane" class="devsite-nav-title"><span class="devsite-nav-text">Use geospatial analytics to plot a hurricane's path</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/geospatial-visualize-colab" class="devsite-nav-title"><span class="devsite-nav-text">Visualize geospatial analytics data in a Colab notebook</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/raster-tutorial-weather" class="devsite-nav-title"><span class="devsite-nav-text">Use raster data to analyze temperature</span></a></li>
</ul>
</div></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Routines</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/routines-intro" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/routines" class="devsite-nav-title"><span class="devsite-nav-text">Manage routines</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/user-defined-functions" class="devsite-nav-title"><span class="devsite-nav-text">User-defined functions</span></a></li>
<li class="devsite-nav-item
           devsite-nav-preview"><a href="/bigquery/docs/user-defined-functions-python" class="devsite-nav-title"><span class="devsite-nav-text">User-defined functions in Python</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/user-defined-aggregates" class="devsite-nav-title"><span class="devsite-nav-text">User-defined aggregate functions</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/table-functions" class="devsite-nav-title"><span class="devsite-nav-text">Table functions</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/remote-functions" class="devsite-nav-title"><span class="devsite-nav-text">Remote functions</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/procedures" class="devsite-nav-title"><span class="devsite-nav-text">SQL stored procedures</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/spark-procedures" class="devsite-nav-title"><span class="devsite-nav-text">Stored procedures for Apache Spark</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/object-table-remote-function" class="devsite-nav-title"><span class="devsite-nav-text">Analyze object tables by using remote functions</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/remote-functions-translation-tutorial" class="devsite-nav-title"><span class="devsite-nav-text">Remote functions and Translation API tutorial</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Analyze multimodal data</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/analyze-multimodal-data" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/work-with-objectref" class="devsite-nav-title"><span class="devsite-nav-text">Work with ObjectRef values</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/multimodal-data-sql-tutorial" class="devsite-nav-title"><span class="devsite-nav-text">Analyze multimodal data with SQL and BigQuery DataFrames</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Search indexes</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/search-intro" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/search-index" class="devsite-nav-title"><span class="devsite-nav-text">Manage search indexes</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/search" class="devsite-nav-title"><span class="devsite-nav-text">Search indexed data</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/text-analysis-search" class="devsite-nav-title"><span class="devsite-nav-text">Work with text analyzers</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-preview"><a href="/bigquery/docs/global-queries" class="devsite-nav-title"><span class="devsite-nav-text">Run global queries</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/access-historical-data" class="devsite-nav-title"><span class="devsite-nav-text">Access historical data</span></a></li>
</ul>
</div></li>

  <li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Manage queries</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Save queries</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/saved-queries-introduction" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/work-with-saved-queries" class="devsite-nav-title"><span class="devsite-nav-text">Create saved queries</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Continuous queries</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/continuous-queries-introduction" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/continuous-queries" class="devsite-nav-title"><span class="devsite-nav-text">Create continuous queries</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/cached-results" class="devsite-nav-title"><span class="devsite-nav-text">Use cached results</span></a></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Use sessions</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/sessions-intro" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/sessions" class="devsite-nav-title"><span class="devsite-nav-text">Work with sessions</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/sessions-write-queries" class="devsite-nav-title"><span class="devsite-nav-text">Write queries in sessions</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/troubleshoot-queries" class="devsite-nav-title"><span class="devsite-nav-text">Troubleshoot queries</span></a></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Optimize queries</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/best-practices-performance-overview" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/query-plan-explanation" class="devsite-nav-title"><span class="devsite-nav-text">Use the query plan explanation</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/query-insights" class="devsite-nav-title"><span class="devsite-nav-text">Get query performance insights</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/best-practices-performance-compute" class="devsite-nav-title"><span class="devsite-nav-text">Optimize query computation</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/history-based-optimizations" class="devsite-nav-title"><span class="devsite-nav-text">Use history-based optimizations</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/best-practices-storage" class="devsite-nav-title"><span class="devsite-nav-text">Optimize storage for query performance</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/materialized-views-use" class="devsite-nav-title"><span class="devsite-nav-text">Use materialized views</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/bi-engine-query" class="devsite-nav-title"><span class="devsite-nav-text">Use BI Engine</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/best-practices-performance-nested" class="devsite-nav-title"><span class="devsite-nav-text">Use nested and repeated data</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/best-practices-performance-functions" class="devsite-nav-title"><span class="devsite-nav-text">Optimize functions</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/advanced-runtime" class="devsite-nav-title"><span class="devsite-nav-text">Use the advanced runtime</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/primary-foreign-keys" class="devsite-nav-title"><span class="devsite-nav-text">Use primary and foreign keys</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/paging-results" class="devsite-nav-title"><span class="devsite-nav-text">Paginate with the BigQuery API</span></a></li>
</ul>
</div></li>

  <li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Query external data sources</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/connections-api-intro" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Use external tables and datasets</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Create connections</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/omni-aws-create-connection" class="devsite-nav-title"><span class="devsite-nav-text">Amazon S3 connection</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/connect-to-spark" class="devsite-nav-title"><span class="devsite-nav-text">Apache Spark connection</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/omni-azure-create-connection" class="devsite-nav-title"><span class="devsite-nav-text">Azure Blob Storage connection</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/create-cloud-resource-connection" class="devsite-nav-title"><span class="devsite-nav-text">Cloud resource connection</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/connect-to-spanner" class="devsite-nav-title"><span class="devsite-nav-text">Spanner connection</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/connect-to-sql" class="devsite-nav-title"><span class="devsite-nav-text">Cloud SQL connection</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/connect-to-alloydb" class="devsite-nav-title"><span class="devsite-nav-text">AlloyDB connection</span></a></li>
<li class="devsite-nav-item
           devsite-nav-preview"><a href="/bigquery/docs/connect-to-sap-datasphere" class="devsite-nav-title"><span class="devsite-nav-text">SAP Datasphere connection</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/working-with-connections" class="devsite-nav-title"><span class="devsite-nav-text">Manage connections</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/connections-with-network-attachment" class="devsite-nav-title"><span class="devsite-nav-text">Configure connections with network attachments</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/default-connections" class="devsite-nav-title"><span class="devsite-nav-text">Default connections</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Amazon S3 data</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/query-aws-data" class="devsite-nav-title"><span class="devsite-nav-text">Query Amazon S3 data</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/omni-aws-export-results-to-s3" class="devsite-nav-title"><span class="devsite-nav-text">Export query results to Amazon S3</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/query-iceberg-data" class="devsite-nav-title"><span class="devsite-nav-text">Query Apache Iceberg data</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/query-open-table-format-using-manifest-files" class="devsite-nav-title"><span class="devsite-nav-text">Query open table formats with manifests</span></a></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Azure Blob Storage data</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/query-azure-data" class="devsite-nav-title"><span class="devsite-nav-text">Query Azure Blob Storage data</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/omni-azure-export-results-to-azure-storage" class="devsite-nav-title"><span class="devsite-nav-text">Export query results to Azure Blob Storage</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/external-data-bigtable" class="devsite-nav-title"><span class="devsite-nav-text">Query Cloud Bigtable data</span></a></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Cloud Storage data</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/query-cloud-storage-using-biglake" class="devsite-nav-title"><span class="devsite-nav-text">Query Cloud Storage data in BigLake tables</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/query-cloud-storage-data" class="devsite-nav-title"><span class="devsite-nav-text">Query Cloud Storage data in external tables</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/salesforce-quickstart" class="devsite-nav-title"><span class="devsite-nav-text">Work with Salesforce Data Cloud data</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/query-drive-data" class="devsite-nav-title"><span class="devsite-nav-text">Query Google Drive data</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/glue-federated-datasets" class="devsite-nav-title"><span class="devsite-nav-text">Create and manage AWS Glue federated datasets</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/spanner-external-datasets" class="devsite-nav-title"><span class="devsite-nav-text">Create Spanner external datasets</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Run federated queries</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/federated-queries-intro" class="devsite-nav-title"><span class="devsite-nav-text">Federated queries</span></a></li>
<li class="devsite-nav-item
           devsite-nav-preview"><a href="/bigquery/docs/sap-datasphere-federated-queries" class="devsite-nav-title"><span class="devsite-nav-text">Query SAP Datasphere data</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/alloydb-federated-queries" class="devsite-nav-title"><span class="devsite-nav-text">Query AlloyDB data</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/spanner-federated-queries" class="devsite-nav-title"><span class="devsite-nav-text">Query Spanner data</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/cloud-sql-federated-queries" class="devsite-nav-title"><span class="devsite-nav-text">Query Cloud SQL data</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Use Jupyter notebooks</span>
      </div>
<ul class="devsite-nav-section"><li class="devsite-nav-item"><a href="/bigquery/docs/jupyterlab-plugin" class="devsite-nav-title"><span class="devsite-nav-text">Use the BigQuery JupyterLab plugin</span></a></li></ul>
</div></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/python-libraries" class="devsite-nav-title"><span class="devsite-nav-text">Use open source Python libraries</span></a></li>
</ul>
</div></li>

  <li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Use analysis and BI tools</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/data-analysis-tools-intro" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/connected-sheets" class="devsite-nav-title"><span class="devsite-nav-text">Use Connected Sheets</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/analyze-data-tableau" class="devsite-nav-title"><span class="devsite-nav-text">Use Tableau Desktop</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/looker" class="devsite-nav-title"><span class="devsite-nav-text">Use Looker</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/visualize-looker-studio" class="devsite-nav-title"><span class="devsite-nav-text">Use Looker Studio</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/third-party-integration" class="devsite-nav-title"><span class="devsite-nav-text">Use third-party tools</span></a></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Google Cloud Ready - BigQuery</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item
           devsite-nav-external"><a href="/bigquery/docs/bigquery-ready-overview" class="devsite-nav-title"><span class="devsite-nav-text">Overview</span></a></li>
<li class="devsite-nav-item
           devsite-nav-external"><a href="/bigquery/docs/bigquery-ready-partners" class="devsite-nav-title"><span class="devsite-nav-text">Partners</span></a></li>
</ul>
</div></li>
</ul>
</div></li>

  <li class="devsite-nav-item
           devsite-nav-heading"><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">BigQuery AI</span>
      </div></li>

  <li class="devsite-nav-item"><a href="/bigquery/docs/ai-introduction" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>

  <li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Generative AI functions</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/generative-ai-overview" class="devsite-nav-title"><span class="devsite-nav-text">Overview</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/e2e-journey-genai" class="devsite-nav-title"><span class="devsite-nav-text">End-to-end user journeys for generative AI models</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/choose-text-generation-function" class="devsite-nav-title"><span class="devsite-nav-text">Choose a text generation function</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/permissions-for-ai-functions" class="devsite-nav-title"><span class="devsite-nav-text">Set permissions for generative AI functions</span></a></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Cloud AI API functions</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/ai-application-overview" class="devsite-nav-title"><span class="devsite-nav-text">Overview</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/choose-ml-text-function" class="devsite-nav-title"><span class="devsite-nav-text">Choose a natural language processing function</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/choose-document-processing-function" class="devsite-nav-title"><span class="devsite-nav-text">Choose a document processing function</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Tutorials</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Generate text</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/generate-text-tutorial-gemini" class="devsite-nav-title"><span class="devsite-nav-text">Generate text using AI.GENERATE_TEXT and Gemini</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/generate-text-tutorial-gemma" class="devsite-nav-title"><span class="devsite-nav-text">Generate text using AI.GENERATE_TEXT and Gemma</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/generate-text" class="devsite-nav-title"><span class="devsite-nav-text">Generate text using AI.GENERATE_TEXT and any supported model</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/generate-text-scalar" class="devsite-nav-title"><span class="devsite-nav-text">Generate text using AI.GENERATE</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/iterate-generate-text-calls" class="devsite-nav-title"><span class="devsite-nav-text">Handle quota errors by calling ML.GENERATE_TEXT iteratively</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/image-analysis" class="devsite-nav-title"><span class="devsite-nav-text">Analyze images with a Gemini model</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/semantic-analysis" class="devsite-nav-title"><span class="devsite-nav-text">Perform semantic analysis with managed AI functions</span></a></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Tune text generation models</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/generate-text-tuning" class="devsite-nav-title"><span class="devsite-nav-text">Tune a model using your data</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/tune-evaluate" class="devsite-nav-title"><span class="devsite-nav-text">Use tuning and evaluation to improve model performance</span></a></li>
</ul>
</div></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Generate structured data</span>
      </div>
<ul class="devsite-nav-section"><li class="devsite-nav-item"><a href="/bigquery/docs/generate-table" class="devsite-nav-title"><span class="devsite-nav-text">Generate structured data</span></a></li></ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Natural language processing</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/understand-text" class="devsite-nav-title"><span class="devsite-nav-text">Understand text</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/translate-text" class="devsite-nav-title"><span class="devsite-nav-text">Translate text</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Document processing</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/process-document" class="devsite-nav-title"><span class="devsite-nav-text">Process documents</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/rag-pipeline-pdf" class="devsite-nav-title"><span class="devsite-nav-text">Parse PDFs in a retrieval-augmented generation pipeline</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Speech recognition</span>
      </div>
<ul class="devsite-nav-section"><li class="devsite-nav-item"><a href="/bigquery/docs/transcribe" class="devsite-nav-title"><span class="devsite-nav-text">Transcribe audio files</span></a></li></ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Computer vision</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/annotate-image" class="devsite-nav-title"><span class="devsite-nav-text">Annotate images</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/object-table-inference" class="devsite-nav-title"><span class="devsite-nav-text">Run inference on image data</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/inference-tutorial-resnet" class="devsite-nav-title"><span class="devsite-nav-text">Analyze images with an imported classification model</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/inference-tutorial-mobilenet" class="devsite-nav-title"><span class="devsite-nav-text">Analyze images with an imported feature vector model</span></a></li>
</ul>
</div></li>
</ul>
</div></li>
</ul>
</div></li>

  <li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Embeddings and vector search</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/vector-search-intro" class="devsite-nav-title"><span class="devsite-nav-text">Overview</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/vector-index-intro" class="devsite-nav-title"><span class="devsite-nav-text">Vector indexes</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/vector-index" class="devsite-nav-title"><span class="devsite-nav-text">Manage vector indexes</span></a></li>
<li class="devsite-nav-item
           devsite-nav-preview"><a href="/bigquery/docs/autonomous-embedding-generation" class="devsite-nav-title"><span class="devsite-nav-text">Automate embedding generation</span></a></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Tutorials</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Generate embeddings</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/generate-text-embedding" class="devsite-nav-title"><span class="devsite-nav-text">Generate text embeddings using a remote model</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/generate-text-embedding-tutorial-open-models" class="devsite-nav-title"><span class="devsite-nav-text">Generate text embeddings using an open model</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/generate-visual-content-embedding" class="devsite-nav-title"><span class="devsite-nav-text">Generate image embeddings using an LLM</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/generate-video-embedding" class="devsite-nav-title"><span class="devsite-nav-text">Generate video embeddings using an LLM</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/iterate-generate-embedding-calls" class="devsite-nav-title"><span class="devsite-nav-text">Handle quota errors by calling ML.GENERATE_EMBEDDING iteratively</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/generate-multimodal-embeddings" class="devsite-nav-title"><span class="devsite-nav-text">Generate and search multimodal embeddings</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/generate-embedding-with-tensorflow-models" class="devsite-nav-title"><span class="devsite-nav-text">Generate text embeddings using pretrained TensorFlow models</span></a></li>
<li class="devsite-nav-item
           devsite-nav-preview"><a href="/bigquery/docs/generate-embeddings-onnx-format" class="devsite-nav-title"><span class="devsite-nav-text">Generate embeddings with transformer models in ONNX format</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Vector search</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/vector-search" class="devsite-nav-title"><span class="devsite-nav-text">Search embeddings with vector search</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/vector-index-text-search-tutorial" class="devsite-nav-title"><span class="devsite-nav-text">Perform semantic search and retrieval-augmented generation</span></a></li>
</ul>
</div></li>
</ul>
</div></li>
</ul>
</div></li>

  <li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Assistive AI</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/gemini-overview" class="devsite-nav-title"><span class="devsite-nav-text">Gemini in BigQuery overview</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/gemini-set-up" class="devsite-nav-title"><span class="devsite-nav-text">Set up Gemini in BigQuery</span></a></li>
<li class="devsite-nav-item
           devsite-nav-preview"><a href="/bigquery/docs/use-cloud-assist" class="devsite-nav-title"><span class="devsite-nav-text">Use Cloud Assist</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/gemini-security-privacy-compliance" class="devsite-nav-title"><span class="devsite-nav-text">Security and privacy</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/gemini-locations" class="devsite-nav-title"><span class="devsite-nav-text">Gemini in BigQuery locations</span></a></li>
</ul>
</div></li>

  <li class="devsite-nav-item
           devsite-nav-expandable
           devsite-nav-preview"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Analyze with conversational analytics agent</span>
</div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/conversational-analytics" class="devsite-nav-title"><span class="devsite-nav-text">Overview</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/create-data-agents" class="devsite-nav-title"><span class="devsite-nav-text">Create data agents</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/create-conversations" class="devsite-nav-title"><span class="devsite-nav-text">Analyze data with conversations</span></a></li>
</ul>
</div></li>

  <li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Machine learning</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/bqml-introduction" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Understand user journeys</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/e2e-journey" class="devsite-nav-title"><span class="devsite-nav-text">End-to-end user journeys for ML models</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/e2e-journey-forecast" class="devsite-nav-title"><span class="devsite-nav-text">End-to-end user journeys for forecasting models</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/e2e-journey-import" class="devsite-nav-title"><span class="devsite-nav-text">End-to-end user journeys for imported models</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/timesfm-model" class="devsite-nav-title"><span class="devsite-nav-text">The TimesFM time series forecasting model</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/reference-patterns" class="devsite-nav-title"><span class="devsite-nav-text">Reference patterns</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">ML models and MLOps</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/model-overview" class="devsite-nav-title"><span class="devsite-nav-text">Model creation</span></a></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Feature engineering and management</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/preprocess-overview" class="devsite-nav-title"><span class="devsite-nav-text">Feature preprocessing overview</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/input-feature-types" class="devsite-nav-title"><span class="devsite-nav-text">Supported input feature types</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/auto-preprocessing" class="devsite-nav-title"><span class="devsite-nav-text">Automatic preprocessing</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/manual-preprocessing" class="devsite-nav-title"><span class="devsite-nav-text">Manual preprocessing</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/feature-serving" class="devsite-nav-title"><span class="devsite-nav-text">Feature serving</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/bigqueryml-transform" class="devsite-nav-title"><span class="devsite-nav-text">Perform feature engineering with the TRANSFORM clause</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/hp-tuning-overview" class="devsite-nav-title"><span class="devsite-nav-text">Hyperparameter tuning overview</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/evaluate-overview" class="devsite-nav-title"><span class="devsite-nav-text">Model evaluation overview</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/inference-overview" class="devsite-nav-title"><span class="devsite-nav-text">Model inference overview</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/xai-overview" class="devsite-nav-title"><span class="devsite-nav-text">Explainable AI overview</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/weights-overview" class="devsite-nav-title"><span class="devsite-nav-text">Model weights overview</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/ml-pipelines-overview" class="devsite-nav-title"><span class="devsite-nav-text">ML pipelines overview</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/model-monitoring-overview" class="devsite-nav-title"><span class="devsite-nav-text">Model monitoring overview</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/managing-models-vertex" class="devsite-nav-title"><span class="devsite-nav-text">Manage BigQueryML models in Vertex AI</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Work with models</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/listing-models" class="devsite-nav-title"><span class="devsite-nav-text">List models</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/managing-models" class="devsite-nav-title"><span class="devsite-nav-text">Manage models</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/getting-model-metadata" class="devsite-nav-title"><span class="devsite-nav-text">Get model metadata</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/updating-model-metadata" class="devsite-nav-title"><span class="devsite-nav-text">Update model metadata</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/exporting-models" class="devsite-nav-title"><span class="devsite-nav-text">Export models</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/deleting-models" class="devsite-nav-title"><span class="devsite-nav-text">Delete models</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/classification-overview" class="devsite-nav-title"><span class="devsite-nav-text">Classification</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/regression-overview" class="devsite-nav-title"><span class="devsite-nav-text">Regression</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/dimensionality-reduction-overview" class="devsite-nav-title"><span class="devsite-nav-text">Dimensionality reduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/clustering-overview" class="devsite-nav-title"><span class="devsite-nav-text">Clustering</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/recommendation-overview" class="devsite-nav-title"><span class="devsite-nav-text">Recommendation</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/forecasting-overview" class="devsite-nav-title"><span class="devsite-nav-text">Forecasting</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/anomaly-detection-overview" class="devsite-nav-title"><span class="devsite-nav-text">Anomaly detection</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/contribution-analysis" class="devsite-nav-title"><span class="devsite-nav-text">Contribution analysis</span></a></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Tutorials</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Getting started</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/create-machine-learning-model" class="devsite-nav-title"><span class="devsite-nav-text">Get started with BigQuery ML using SQL</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/create-machine-learning-model-console" class="devsite-nav-title"><span class="devsite-nav-text">Get started with BigQuery ML using the Cloud console</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Regression and classification</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/linear-regression-tutorial" class="devsite-nav-title"><span class="devsite-nav-text">Create a linear regression model</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/logistic-regression-prediction" class="devsite-nav-title"><span class="devsite-nav-text">Create a logistic regression classification model</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/boosted-tree-classifier-tutorial" class="devsite-nav-title"><span class="devsite-nav-text">Create a boosted trees classification model</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Clustering</span>
      </div>
<ul class="devsite-nav-section"><li class="devsite-nav-item"><a href="/bigquery/docs/kmeans-tutorial" class="devsite-nav-title"><span class="devsite-nav-text">Cluster data with a k-means model</span></a></li></ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Recommendation</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/bigqueryml-mf-explicit-tutorial" class="devsite-nav-title"><span class="devsite-nav-text">Create recommendations based on explicit feedback with a matrix factorization model</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/bigqueryml-mf-implicit-tutorial" class="devsite-nav-title"><span class="devsite-nav-text">Create recommendations based on implicit feedback with a matrix factorization model</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Forecasting</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/arima-single-time-series-forecasting-tutorial" class="devsite-nav-title"><span class="devsite-nav-text">Forecast a single time series with an ARIMA_PLUS univariate model</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/arima-multiple-time-series-forecasting-tutorial" class="devsite-nav-title"><span class="devsite-nav-text">Forecast multiple time series with an ARIMA_PLUS univariate model</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/timesfm-time-series-forecasting-tutorial" class="devsite-nav-title"><span class="devsite-nav-text">Forecast time series with a TimesFM univariate model</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/arima-speed-up-tutorial" class="devsite-nav-title"><span class="devsite-nav-text">Scale an ARIMA_PLUS univariate model to millions of time series</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/arima-plus-xreg-single-time-series-forecasting-tutorial" class="devsite-nav-title"><span class="devsite-nav-text">Forecast a single time series with a multivariate model</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/arima-plus-xreg-multiple-time-series-forecasting-tutorial" class="devsite-nav-title"><span class="devsite-nav-text">Forecast multiple time series with a multivariate model</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/time-series-forecasting-holidays-tutorial" class="devsite-nav-title"><span class="devsite-nav-text">Use custom holidays with an ARIMA_PLUS univariate model</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/arima-time-series-forecasting-with-limits-tutorial" class="devsite-nav-title"><span class="devsite-nav-text">Limit forecasted values for an ARIMA_PLUS univariate model</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/arima-time-series-forecasting-with-hierarchical-time-series" class="devsite-nav-title"><span class="devsite-nav-text">Forecast hierarchical time series with an ARIMA_PLUS univariate model</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Anomaly detection</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/timesfm-anomaly-detection-tutorial" class="devsite-nav-title"><span class="devsite-nav-text">Anomaly detection with a TimesFM univariate model</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/time-series-anomaly-detection-tutorial" class="devsite-nav-title"><span class="devsite-nav-text">Anomaly detection with a multivariate time series</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Imported and remote models</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/making-predictions-with-imported-tensorflow-models" class="devsite-nav-title"><span class="devsite-nav-text">Make predictions with imported TensorFlow models</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/making-predictions-with-sklearn-models-in-onnx-format" class="devsite-nav-title"><span class="devsite-nav-text">Make predictions with scikit-learn models in ONNX format</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/making-predictions-with-pytorch-models-in-onnx-format" class="devsite-nav-title"><span class="devsite-nav-text">Make predictions with PyTorch models in ONNX format</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/bigquery-ml-remote-model-tutorial" class="devsite-nav-title"><span class="devsite-nav-text">Make predictions with remote models on Vertex AI</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Hyperparameter tuning</span>
      </div>
<ul class="devsite-nav-section"><li class="devsite-nav-item"><a href="/bigquery/docs/hyperparameter-tuning-tutorial" class="devsite-nav-title"><span class="devsite-nav-text">Improve model performance with hyperparameter tuning</span></a></li></ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Export models</span>
      </div>
<ul class="devsite-nav-section"><li class="devsite-nav-item"><a href="/bigquery/docs/export-model-tutorial" class="devsite-nav-title"><span class="devsite-nav-text">Export a BigQuery ML model for online prediction</span></a></li></ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Augmented analytics</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/get-contribution-analysis-insights" class="devsite-nav-title"><span class="devsite-nav-text">Get data insights from contribution analysis using a summable metric</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/get-contribution-analysis-insights-sum-ratio" class="devsite-nav-title"><span class="devsite-nav-text">Get data insights from contribution analysis using a summable ratio metric</span></a></li>
</ul>
</div></li>
</ul>
</div></li>
</ul>
</div></li>

  <li class="devsite-nav-item
           devsite-nav-heading"><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Administer</span>
      </div></li>

  <li class="devsite-nav-item"><a href="/bigquery/docs/admin-intro" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>

  <li class="devsite-nav-item"><a href="/bigquery/docs/editions-intro" class="devsite-nav-title"><span class="devsite-nav-text">Understand editions</span></a></li>

  <li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Manage resources</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/resource-hierarchy" class="devsite-nav-title"><span class="devsite-nav-text">Organize resources</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/reliability-intro" class="devsite-nav-title"><span class="devsite-nav-text">Understand reliability</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/default-configuration" class="devsite-nav-title"><span class="devsite-nav-text">Manage configuration settings</span></a></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Manage code assets</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/manage-data-preparations" class="devsite-nav-title"><span class="devsite-nav-text">Manage data preparations</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/manage-notebooks" class="devsite-nav-title"><span class="devsite-nav-text">Manage notebooks</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/manage-saved-queries" class="devsite-nav-title"><span class="devsite-nav-text">Manage saved queries</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/manage-pipelines" class="devsite-nav-title"><span class="devsite-nav-text">Manage pipelines</span></a></li>
<li class="devsite-nav-item
           devsite-nav-expandable
           devsite-nav-preview"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Organize code assets with folders</span>
</div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/code-asset-folders" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/create-manage-folders" class="devsite-nav-title"><span class="devsite-nav-text">Create and manage folders</span></a></li>
</ul>
</div></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Manage tables</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/managing-tables" class="devsite-nav-title"><span class="devsite-nav-text">Manage tables</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/managing-table-data" class="devsite-nav-title"><span class="devsite-nav-text">Manage table data</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/managing-table-schemas" class="devsite-nav-title"><span class="devsite-nav-text">Modify table schemas</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/restore-deleted-tables" class="devsite-nav-title"><span class="devsite-nav-text">Restore deleted tables</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Manage table clones</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/table-clones-intro" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/table-clones-create" class="devsite-nav-title"><span class="devsite-nav-text">Create table clones</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Manage table snapshots</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/table-snapshots-intro" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/table-snapshots-create" class="devsite-nav-title"><span class="devsite-nav-text">Create table snapshots</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/table-snapshots-restore" class="devsite-nav-title"><span class="devsite-nav-text">Restore table snapshots</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/table-snapshots-list" class="devsite-nav-title"><span class="devsite-nav-text">List table snapshots</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/table-snapshots-metadata" class="devsite-nav-title"><span class="devsite-nav-text">View table snapshot metadata</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/table-snapshots-update" class="devsite-nav-title"><span class="devsite-nav-text">Update table snapshot metadata</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/table-snapshots-delete" class="devsite-nav-title"><span class="devsite-nav-text">Delete table snapshots</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/table-snapshots-scheduled" class="devsite-nav-title"><span class="devsite-nav-text">Create periodic table snapshots</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Manage datasets</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/managing-datasets" class="devsite-nav-title"><span class="devsite-nav-text">Manage datasets</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/updating-datasets" class="devsite-nav-title"><span class="devsite-nav-text">Update dataset properties</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/restore-deleted-datasets" class="devsite-nav-title"><span class="devsite-nav-text">Restore deleted datasets</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Manage views and materialized views</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/view-metadata" class="devsite-nav-title"><span class="devsite-nav-text">Get information about views</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/managing-views" class="devsite-nav-title"><span class="devsite-nav-text">Manage views</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/materialized-views-manage" class="devsite-nav-title"><span class="devsite-nav-text">Manage materialized views</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/materialized-view-replicas-manage" class="devsite-nav-title"><span class="devsite-nav-text">Manage materialized view replicas</span></a></li>
</ul>
</div></li>
</ul>
</div></li>

  <li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Schedule resources</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/orchestrate-workloads" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Schedule code assets</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/orchestrate-data-preparations" class="devsite-nav-title"><span class="devsite-nav-text">Schedule data preparations</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/orchestrate-notebooks" class="devsite-nav-title"><span class="devsite-nav-text">Schedule notebooks</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/schedule-pipelines" class="devsite-nav-title"><span class="devsite-nav-text">Schedule pipelines</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/orchestrate-dags" class="devsite-nav-title"><span class="devsite-nav-text">Schedule DAGs</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Schedule jobs and queries</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/running-jobs" class="devsite-nav-title"><span class="devsite-nav-text">Run jobs programmatically</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/scheduling-queries" class="devsite-nav-title"><span class="devsite-nav-text">Schedule queries</span></a></li>
</ul>
</div></li>
</ul>
</div></li>

  <li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Workload management</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/reservations-intro" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/slots" class="devsite-nav-title"><span class="devsite-nav-text">Understand slots</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/reservations-workload-management" class="devsite-nav-title"><span class="devsite-nav-text">Understand reservations</span></a></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Manage workloads</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/reservations-tasks" class="devsite-nav-title"><span class="devsite-nav-text">Work with slot reservations</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/reservations-assignments" class="devsite-nav-title"><span class="devsite-nav-text">Manage assignments</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/reservations-commitments" class="devsite-nav-title"><span class="devsite-nav-text">Manage commitments</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/managing-jobs" class="devsite-nav-title"><span class="devsite-nav-text">Manage jobs</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/query-queues" class="devsite-nav-title"><span class="devsite-nav-text">Manage query queues</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Plan workloads</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/slot-estimator" class="devsite-nav-title"><span class="devsite-nav-text">Estimate capacity requirements</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/slot-recommender" class="devsite-nav-title"><span class="devsite-nav-text">View slot recommendations</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Legacy reservations</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/reservations-intro-legacy" class="devsite-nav-title"><span class="devsite-nav-text">Introduction to legacy reservations</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/reservations-details-legacy" class="devsite-nav-title"><span class="devsite-nav-text">Legacy slot commitments</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/reservations-commitments-legacy" class="devsite-nav-title"><span class="devsite-nav-text">Purchase and manage legacy slot commitments</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/reservations-tasks-legacy" class="devsite-nav-title"><span class="devsite-nav-text">Work with legacy slot reservations</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Manage BI Engine</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/bi-engine-intro" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/bi-engine-reserve-capacity" class="devsite-nav-title"><span class="devsite-nav-text">Reserve BI Engine capacity</span></a></li>
</ul>
</div></li>
</ul>
</div></li>

  <li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Monitor workloads</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/monitoring" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/admin-resource-charts" class="devsite-nav-title"><span class="devsite-nav-text">Monitor resource utilization</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/admin-jobs-explorer" class="devsite-nav-title"><span class="devsite-nav-text">Monitor jobs</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/analytics-hub-monitor-listings" class="devsite-nav-title"><span class="devsite-nav-text">Monitor sharing listings</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/bi-engine-monitor" class="devsite-nav-title"><span class="devsite-nav-text">Monitor BI Engine</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/dts-monitor" class="devsite-nav-title"><span class="devsite-nav-text">Monitor Data Transfer Service</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/materialized-views-monitor" class="devsite-nav-title"><span class="devsite-nav-text">Monitor materialized views</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/reservations-monitoring" class="devsite-nav-title"><span class="devsite-nav-text">Monitor reservations</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/continuous-queries-monitor" class="devsite-nav-title"><span class="devsite-nav-text">Monitor continuous queries</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/monitoring-dashboard" class="devsite-nav-title"><span class="devsite-nav-text">Dashboards, charts, and alerts</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/create-alert-scheduled-query" class="devsite-nav-title"><span class="devsite-nav-text">Set up alerts with scheduled queries</span></a></li>
</ul>
</div></li>

  <li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Optimize resources</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Control costs</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/best-practices-costs" class="devsite-nav-title"><span class="devsite-nav-text">Estimate and control costs</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/custom-quotas" class="devsite-nav-title"><span class="devsite-nav-text">Create custom query quotas</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Optimize with recommendations</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/recommendations-intro" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/manage-partition-cluster-recommendations" class="devsite-nav-title"><span class="devsite-nav-text">Manage cluster and partition recommendations</span></a></li>
<li class="devsite-nav-item
           devsite-nav-preview"><a href="/bigquery/docs/manage-materialized-recommendations" class="devsite-nav-title"><span class="devsite-nav-text">Manage materialized view recommendations</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Organize with labels</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/labels-intro" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/adding-labels" class="devsite-nav-title"><span class="devsite-nav-text">Add labels</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/viewing-labels" class="devsite-nav-title"><span class="devsite-nav-text">View labels</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/updating-labels" class="devsite-nav-title"><span class="devsite-nav-text">Update labels</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/filtering-labels" class="devsite-nav-title"><span class="devsite-nav-text">Filter using labels</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/deleting-labels" class="devsite-nav-title"><span class="devsite-nav-text">Delete labels</span></a></li>
</ul>
</div></li>
</ul>
</div></li>

  <li class="devsite-nav-item
           devsite-nav-heading"><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Govern</span>
      </div></li>

  <li class="devsite-nav-item"><a href="/bigquery/docs/data-governance" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>

  <li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Manage data quality</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/data-quality-scan" class="devsite-nav-title"><span class="devsite-nav-text">Scan for data quality issues</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/data-catalog-overview" class="devsite-nav-title"><span class="devsite-nav-text">Data Catalog overview</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/data-catalog" class="devsite-nav-title"><span class="devsite-nav-text">Work with Data Catalog</span></a></li>
</ul>
</div></li>

  <li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Control access to resources</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/access-control-intro" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/access-control" class="devsite-nav-title"><span class="devsite-nav-text">IAM roles and permissions</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/dataset-access-control" class="devsite-nav-title"><span class="devsite-nav-text">Changes to dataset-level access controls</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/access-control-basic-roles" class="devsite-nav-title"><span class="devsite-nav-text">Basic roles and permissions</span></a></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Control access with IAM</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/control-access-to-resources-iam" class="devsite-nav-title"><span class="devsite-nav-text">Control access to resources with IAM</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/tags" class="devsite-nav-title"><span class="devsite-nav-text">Control access with tags</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/conditions" class="devsite-nav-title"><span class="devsite-nav-text">Control access with conditions</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/custom-constraints" class="devsite-nav-title"><span class="devsite-nav-text">Control access with custom constraints</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/troubleshoot-access-control" class="devsite-nav-title"><span class="devsite-nav-text">Troubleshoot IAM permissions</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Control access with authorization</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/authorized-datasets" class="devsite-nav-title"><span class="devsite-nav-text">Authorized datasets</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/authorized-routines" class="devsite-nav-title"><span class="devsite-nav-text">Authorized routines</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/authorized-views" class="devsite-nav-title"><span class="devsite-nav-text">Authorized views</span></a></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Tutorials</span>
      </div>
<ul class="devsite-nav-section"><li class="devsite-nav-item"><a href="/bigquery/docs/create-authorized-views" class="devsite-nav-title"><span class="devsite-nav-text">Create an authorized view</span></a></li></ul>
</div></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Restrict network access</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/vpc-sc" class="devsite-nav-title"><span class="devsite-nav-text">Control access with VPC service controls</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/regional-endpoints" class="devsite-nav-title"><span class="devsite-nav-text">Regional endpoints</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Control column and row access</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Control access to table columns</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/column-level-security-intro" class="devsite-nav-title"><span class="devsite-nav-text">Introduction to column-level access control</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/column-level-security" class="devsite-nav-title"><span class="devsite-nav-text">Restrict access with column-level access control</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/column-level-security-writes" class="devsite-nav-title"><span class="devsite-nav-text">Impact on writes</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Control access to table rows</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/row-level-security-intro" class="devsite-nav-title"><span class="devsite-nav-text">Introduction to row-level security</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/managing-row-level-security" class="devsite-nav-title"><span class="devsite-nav-text">Work with row-level security</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/using-row-level-security-with-features" class="devsite-nav-title"><span class="devsite-nav-text">Use row-level security with other BigQuery features</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/best-practices-row-level-security" class="devsite-nav-title"><span class="devsite-nav-text">Best practices for row-level security</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Manage policy tags</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/managing-policy-tags-across-locations" class="devsite-nav-title"><span class="devsite-nav-text">Manage policy tags across locations</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/best-practices-policy-tags" class="devsite-nav-title"><span class="devsite-nav-text">Best practices for using policy tags</span></a></li>
</ul>
</div></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Protect sensitive data</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Mask data in table columns</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/column-data-masking-intro" class="devsite-nav-title"><span class="devsite-nav-text">Introduction to data masking</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/column-data-masking" class="devsite-nav-title"><span class="devsite-nav-text">Mask column data</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Anonymize data with differential privacy</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/differential-privacy" class="devsite-nav-title"><span class="devsite-nav-text">Use differential privacy</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/extend-differential-privacy" class="devsite-nav-title"><span class="devsite-nav-text">Extend differential privacy</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/analysis-rules" class="devsite-nav-title"><span class="devsite-nav-text">Restrict data access using analysis rules</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/scan-with-dlp" class="devsite-nav-title"><span class="devsite-nav-text">Use Sensitive Data Protection</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Manage encryption</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/encryption-at-rest" class="devsite-nav-title"><span class="devsite-nav-text">Encryption at rest</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/customer-managed-encryption" class="devsite-nav-title"><span class="devsite-nav-text">Customer-managed encryption keys</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/column-key-encrypt" class="devsite-nav-title"><span class="devsite-nav-text">Column-level encryption with Cloud KMS</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/aead-encryption-concepts" class="devsite-nav-title"><span class="devsite-nav-text">AEAD encryption</span></a></li>
</ul>
</div></li>
</ul>
</div></li>

  <li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Share data</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/analytics-hub-introduction" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/analytics-hub-grant-roles" class="devsite-nav-title"><span class="devsite-nav-text">Configure user roles</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/analytics-hub-manage-exchanges" class="devsite-nav-title"><span class="devsite-nav-text">Manage data exchanges</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/analytics-hub-manage-listings" class="devsite-nav-title"><span class="devsite-nav-text">Manage listings</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/analytics-hub-manage-subscriptions" class="devsite-nav-title"><span class="devsite-nav-text">Manage subscriptions</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/analytics-hub-view-subscribe-listings" class="devsite-nav-title"><span class="devsite-nav-text">View and subscribe to listings</span></a></li>
<li class="devsite-nav-item
           devsite-nav-preview"><a href="/bigquery/docs/analytics-hub-custom-constraints" class="devsite-nav-title"><span class="devsite-nav-text">Manage resources with custom constraints</span></a></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Data clean rooms</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/data-clean-rooms" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/query-templates" class="devsite-nav-title"><span class="devsite-nav-text">Use query templates</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Entity resolution</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/entity-resolution-intro" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/entity-resolution-setup" class="devsite-nav-title"><span class="devsite-nav-text">Use entity resolution</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/analytics-hub-vpc-sc-rules" class="devsite-nav-title"><span class="devsite-nav-text">VPC Service Controls for Sharing</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/analytics-hub-stream-sharing" class="devsite-nav-title"><span class="devsite-nav-text">Stream sharing with Pub/Sub</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/analytics-hub-cloud-marketplace" class="devsite-nav-title"><span class="devsite-nav-text">Commercialize listings on Cloud Marketplace</span></a></li>
</ul>
</div></li>

  <li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Audit</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/introduction-audit-workloads" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/auditing-policy-tags" class="devsite-nav-title"><span class="devsite-nav-text">Audit policy tags</span></a></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">View audit logs</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/column-data-masking-audit-logging" class="devsite-nav-title"><span class="devsite-nav-text">Data Policy audit logs</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/audit-logging" class="devsite-nav-title"><span class="devsite-nav-text">Data Transfer Service audit logs</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/analytics-hub-audit-logging" class="devsite-nav-title"><span class="devsite-nav-text">Sharing audit logs</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/biglake-audit-logging" class="devsite-nav-title"><span class="devsite-nav-text">BigLake API audit logs</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/reference/auditlogs/audit-logging-bq-migration" class="devsite-nav-title"><span class="devsite-nav-text">BigQuery Migration API audit logs</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/reference/auditlogs/migration" class="devsite-nav-title"><span class="devsite-nav-text">Migrate audit logs</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/reference/auditlogs" class="devsite-nav-title"><span class="devsite-nav-text">BigQuery audit logs reference</span></a></li>
</ul>
</div></li>

  <li class="devsite-nav-item
           devsite-nav-heading"><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Develop</span>
      </div></li>

  <li class="devsite-nav-item"><a href="/bigquery/docs/developer-overview" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>

  <li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Authenticate to BigQuery</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/authentication" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/authentication/getting-started" class="devsite-nav-title"><span class="devsite-nav-text">Get started</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/authentication/end-user-installed" class="devsite-nav-title"><span class="devsite-nav-text">Authenticate as an end user</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/json-web-tokens" class="devsite-nav-title"><span class="devsite-nav-text">Authenticate with JSON Web Tokens</span></a></li>
</ul>
</div></li>

  <li class="devsite-nav-item
           devsite-nav-preview"><a href="/bigquery/docs/use-bigquery-mcp" class="devsite-nav-title"><span class="devsite-nav-text">Use the BigQuery MCP server</span></a></li>

  <li class="devsite-nav-item"><a href="/bigquery/docs/use-bigquery-migration-mcp" class="devsite-nav-title"><span class="devsite-nav-text">Use the Migration Service MCP server</span></a></li>

  <li class="devsite-nav-item"><a href="/bigquery/docs/pre-built-tools-with-mcp-toolbox" class="devsite-nav-title"><span class="devsite-nav-text">Connect LLMs with MCP toolbox for databases</span></a></li>

  <li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Use ODBC and JDBC drivers</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/reference/odbc-jdbc-drivers" class="devsite-nav-title"><span class="devsite-nav-text">Use the Simba ODBC and JDBC drivers</span></a></li>
<li class="devsite-nav-item
           devsite-nav-preview"><a href="/bigquery/docs/jdbc-for-bigquery" class="devsite-nav-title"><span class="devsite-nav-text">Use the Google JDBC driver</span></a></li>
</ul>
</div></li>

  <li class="devsite-nav-item
           devsite-nav-expandable
           devsite-nav-preview"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Version control with repositories and workspaces</span>
</div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Use repositories</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/repository-intro" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/repositories" class="devsite-nav-title"><span class="devsite-nav-text">Create and manage repositories</span></a></li>
</ul>
</div></li>
<li class="devsite-nav-item
           devsite-nav-expandable"><div class="devsite-expandable-nav">
      <a class="devsite-nav-toggle"></a><div class="devsite-nav-title devsite-nav-title-no-path">
        <span class="devsite-nav-text">Use workspaces</span>
      </div>
<ul class="devsite-nav-section">
<li class="devsite-nav-item"><a href="/bigquery/docs/workspaces-intro" class="devsite-nav-title"><span class="devsite-nav-text">Introduction</span></a></li>
<li class="devsite-nav-item"><a href="/bigquery/docs/workspaces" class="devsite-nav-title"><span class="devsite-nav-text">Create and manage workspaces</span></a></li>
</ul>
</div></li>
</ul>
</div></li>

  <li class="devsite-nav-item
           devsite-nav-preview"><a href="/bigquery/docs/vs-code-extension" class="devsite-nav-title"><span class="devsite-nav-text">Use the VS Code extension</span></a></li>
          </ul>
        
        
          
    
      
      <ul class="devsite-nav-list">
        
          
            
            
              
<li class="devsite-nav-item">

  
  <a href="/docs/ai-ml" class="devsite-nav-title gc-analytics-event
              
              ">
  
    <span class="devsite-nav-text">
      AI and ML
   </span>
    
  
  </a>
  

</li>

            
              
<li class="devsite-nav-item">

  
  <a href="/docs/application-development" class="devsite-nav-title gc-analytics-event
              
              ">
  
    <span class="devsite-nav-text">
      Application development
   </span>
    
  
  </a>
  

</li>

            
              
<li class="devsite-nav-item">

  
  <a href="/docs/application-hosting" class="devsite-nav-title gc-analytics-event
              
              ">
  
    <span class="devsite-nav-text">
      Application hosting
   </span>
    
  
  </a>
  

</li>

            
              
<li class="devsite-nav-item">

  
  <a href="/docs/compute-area" class="devsite-nav-title gc-analytics-event
              
              ">
  
    <span class="devsite-nav-text">
      Compute
   </span>
    
  
  </a>
  

</li>

            
              
<li class="devsite-nav-item">

  
  <a href="/docs/data" class="devsite-nav-title gc-analytics-event
              
              ">
  
    <span class="devsite-nav-text">
      Data analytics and pipelines
   </span>
    
  
  </a>
  

</li>

            
              
<li class="devsite-nav-item">

  
  <a href="/docs/databases" class="devsite-nav-title gc-analytics-event
              
              ">
  
    <span class="devsite-nav-text">
      Databases
   </span>
    
  
  </a>
  

</li>

            
              
<li class="devsite-nav-item">

  
  <a href="/docs/dhm-cloud" class="devsite-nav-title gc-analytics-event
              
              ">
  
    <span class="devsite-nav-text">
      Distributed, hybrid, and multicloud
   </span>
    
  
  </a>
  

</li>

            
              
<li class="devsite-nav-item">

  
  <a href="/docs/industry" class="devsite-nav-title gc-analytics-event
              
              ">
  
    <span class="devsite-nav-text">
      Industry solutions
   </span>
    
  
  </a>
  

</li>

            
              
<li class="devsite-nav-item">

  
  <a href="/docs/migration" class="devsite-nav-title gc-analytics-event
              
              ">
  
    <span class="devsite-nav-text">
      Migration
   </span>
    
  
  </a>
  

</li>

            
              
<li class="devsite-nav-item">

  
  <a href="/docs/networking" class="devsite-nav-title gc-analytics-event
              
              ">
  
    <span class="devsite-nav-text">
      Networking
   </span>
    
  
  </a>
  

</li>

            
              
<li class="devsite-nav-item">

  
  <a href="/docs/observability" class="devsite-nav-title gc-analytics-event
              
              ">
  
    <span class="devsite-nav-text">
      Observability and monitoring
   </span>
    
  
  </a>
  

</li>

            
              
<li class="devsite-nav-item">

  
  <a href="/docs/security" class="devsite-nav-title gc-analytics-event
              
              ">
  
    <span class="devsite-nav-text">
      Security
   </span>
    
  
  </a>
  

</li>

            
              
<li class="devsite-nav-item">

  
  <a href="/docs/storage" class="devsite-nav-title gc-analytics-event
              
              ">
  
    <span class="devsite-nav-text">
      Storage
   </span>
    
  
  </a>
  

</li>

            
          
        
      </ul>
    
  
    
      
      <ul class="devsite-nav-list">
        
          
            
            
              
<li class="devsite-nav-item">

  
  <a href="/docs/access-resources" class="devsite-nav-title gc-analytics-event
              
              ">
  
    <span class="devsite-nav-text">
      Access and resources management
   </span>
    
  
  </a>
  

</li>

            
              
<li class="devsite-nav-item">

  
  <a href="/docs/costs-usage" class="devsite-nav-title gc-analytics-event
              
              ">
  
    <span class="devsite-nav-text">
      Costs and usage management
   </span>
    
  
  </a>
  

</li>

            
              
<li class="devsite-nav-item">

  
  <a href="/docs/iac" class="devsite-nav-title gc-analytics-event
              
              ">
  
    <span class="devsite-nav-text">
      Infrastructure as code
   </span>
    
  
  </a>
  

</li>

            
              
<li class="devsite-nav-item">

  
  <a href="/docs/devtools" class="devsite-nav-title gc-analytics-event
              
              ">
  
    <span class="devsite-nav-text">
      SDK, languages, frameworks, and tools
   </span>
    
  
  </a>
  

</li>

            
          
        
      </ul>
    
  
        
        
          
    
  
    
  
    
  
    
  
    
  
        
      </div>
    
  </div>
</nav>
        
      </devsite-book-nav>
      <section id="gc-wrapper">
        <main id="main-content" class="devsite-main-content">
          <devsite-content>
            
              










<article class="devsite-article">
  
  
  
  
  

  <div class="devsite-article-meta nocontent">
    
    
    <ul class="devsite-breadcrumb-list">
  
  <li class="devsite-breadcrumb-item
             ">
    
    
    
      
        
  <a href="https://docs.cloud.google.com/" class="devsite-breadcrumb-link gc-analytics-event">
    
          Home
        
  </a>
  
      
    
  </li>
  
  <li class="devsite-breadcrumb-item
             ">
    
      
      <a href="https://docs.cloud.google.com/docs" class="devsite-breadcrumb-link gc-analytics-event">
    
          Documentation
        
  </a>
  
      
    
  </li>
  
  <li class="devsite-breadcrumb-item
             ">
    
      
      <a href="https://docs.cloud.google.com/docs/data" class="devsite-breadcrumb-link gc-analytics-event">
    
          Data analytics
        
  </a>
  
      
    
  </li>
  
  <li class="devsite-breadcrumb-item
             ">
    
      
      <a href="https://docs.cloud.google.com/bigquery/docs" class="devsite-breadcrumb-link gc-analytics-event">
    
          BigQuery
        
  </a>
  
      
    
  </li>
  
  <li class="devsite-breadcrumb-item
             ">
    
      
      <a href="https://docs.cloud.google.com/bigquery/docs/introduction" class="devsite-breadcrumb-link gc-analytics-event">
    
          Guides
        
  </a>
  
      
    
  </li>
  
</ul>
    
      
    </div>
  
    <devsite-feedback class="nocontent">

  <button>
  
    
    Send feedback
  
  </button>
</devsite-feedback>
  <devsite-actions><devsite-feature-tooltip class="devsite-page-bookmark-tooltip nocontent" id="devsite-collections-dropdown">

    
    
      <span>
      
      Stay organized with collections
    </span>
    <span>
      
      Save and categorize content based on your preferences.
    </span>
  </devsite-feature-tooltip></devsite-actions>
  
    
  

  <div class="devsite-article-body clearfix
  devsite-no-page-title">

  
    
    
    
  <div class="quickstart">
    <h1 class="devsite-page-title" id="query-a-public-dataset-with-the-bigquery-client-libraries">Query a public dataset with the BigQuery client libraries</h1>

  <section class="intro">
    

<p>Learn how to query a public dataset with the BigQuery client
libraries.</p>

<hr>

<p>To follow step-by-step guidance for this task directly in the
Google Cloud console, select your preferred programming language:</p>
<div class="ds-selector-tabs">
<section><h3 id="c"> C# </h3>
<p><a href="https://console.cloud.google.com/?walkthrough_id=bigquery--csharp-client-library" class="button button-primary">Take the C# tour</a></p></section>
<section><h3 id="go"> Go </h3>
<p><a href="https://console.cloud.google.com/?walkthrough_id=bigquery--go-client-library" class="button button-primary">Take the Go tour</a></p></section>
<section><h3 id="java"> Java </h3>
<p><a href="https://console.cloud.google.com/?walkthrough_id=bigquery--java-client-library" class="button button-primary">Take the Java tour</a></p></section>
<section><h3 id="node.js"> Node.js </h3>
<p><a href="https://console.cloud.google.com/?walkthrough_id=bigquery--node-client-library" class="button button-primary">Take the Node.js tour</a></p></section>
<section><h3 id="php"> PHP </h3>
<p><a href="https://console.cloud.google.com/?walkthrough_id=bigquery--php-client-library" class="button button-primary">Take the PHP tour</a></p></section>
<section><h3 id="python"> Python </h3>
<p><a href="https://console.cloud.google.com/?walkthrough_id=bigquery--python-client-library" class="button button-primary">Take the Python tour</a></p></section>
<section><h3 id="ruby"> Ruby </h3>
<p><a href="https://console.cloud.google.com/?walkthrough_id=bigquery--ruby-client-library" class="button button-primary">Take the Ruby tour</a></p></section>
</div>
<hr>


  </section>

  <section class="prereqs">
    <h2 id="before-you-begin">Before you begin</h2>
    








<ol>
<li>






















  
  
  
    <p><a href="https://cloud.google.com/resource-manager/docs/creating-managing-projects">Create or select a Google Cloud project</a>.</p>
    
<devsite-expandable>
  <p class="showalways"><b>Roles required to select or create a project</b></p>
  <ul>
    <li>
      <b>Select a project</b>: Selecting a project doesn't require a specific
      IAM role—you can select any project that you've been
      granted a role on.
    </li>
    <li>
      <b>Create a project</b>: To create a project, you need the Project Creator role
      (<code>roles/resourcemanager.projectCreator</code>), which contains the
      <code>resourcemanager.projects.create</code> permission. <a href="/iam/docs/granting-changing-revoking-access">Learn how to grant
      roles</a>.
    </li>
  </ul>
</devsite-expandable>

      
        
  <aside class="note"><b>Note</b>: If you don't plan to keep the
    resources that you create in this procedure, create a project instead of
    selecting an existing project. After you finish these steps, you can
    delete the project, removing all resources associated with the project.</aside>

      
    <ul>
      <li>
        <p>Create a Google Cloud project:</p>
        <devsite-code><pre class="devsite-click-to-copy">gcloud projects create <var>PROJECT_ID</var></pre></devsite-code>
        <p>Replace <code><var>PROJECT_ID</var></code> with a name for the Google Cloud project you are creating.</p>
      </li>
      <li>
        <p>Select the Google Cloud project that you created:</p>
        <devsite-code><pre class="devsite-click-to-copy">gcloud config set project <var>PROJECT_ID</var></pre></devsite-code>
        <p>Replace <code><var>PROJECT_ID</var></code> with your Google Cloud project name.</p>
      </li>
    </ul>
  
  



</li>
<li>


<p>Choose whether to
<a href="/bigquery/docs/sandbox">use the BigQuery sandbox at no charge</a>,
or to
<a href="/billing/docs/how-to/modify-project">enable billing for your Google Cloud project</a>.</p>


<p>If you do not enable billing for a project, you automatically work in the
BigQuery sandbox. The BigQuery sandbox lets you learn
BigQuery with a limited set of BigQuery
features at no charge. If you do not plan to use your project beyond this
document, we recommend that you use the BigQuery sandbox.</p>
</li>
<li>















  





  
    
        <p>
          Grant roles to your user account. Run the following command once for each of the following
          IAM roles:
          <code>roles/serviceusage.serviceUsageAdmin, roles/bigquery.jobUser</code>
        </p>
        
        <devsite-code><pre class="devsite-click-to-copy">gcloud<span class="devsite-syntax-w"> </span>projects<span class="devsite-syntax-w"> </span>add-iam-policy-binding<span class="devsite-syntax-w"> </span><var>PROJECT_ID</var><span class="devsite-syntax-w"> </span>--member<span class="devsite-syntax-o">=</span><span class="devsite-syntax-s2">"user:<var>USER_IDENTIFIER</var>"</span><span class="devsite-syntax-w"> </span>--role<span class="devsite-syntax-o">=</span><var>ROLE</var></pre></devsite-code>
        <p>Replace the following:</p>
        <ul>
          <li>
<code><var>PROJECT_ID</var></code>: Your project ID.</li>
        
          <li>
<code><var>USER_IDENTIFIER</var></code>: The identifier for your user
          
            account. For example, <code>myemail@example.com</code>.
           
          </li>
          <li>
<code><var>ROLE</var></code>: The IAM role that you grant to your user account.</li>
        </ul>
    
  


  








</li>
<li>







<p>
        
          
            Enable the BigQuery API:
          
        
      </p>
<devsite-expandable><p class="showalways"><b>Roles required to enable APIs</b></p>
<p>
      To enable APIs, you need the Service Usage Admin IAM
      role (<code>roles/serviceusage.serviceUsageAdmin</code>), which contains the
      <code>serviceusage.services.enable</code> permission. <a href="/iam/docs/granting-changing-revoking-access">Learn how to grant
      roles</a>.
    </p></devsite-expandable><devsite-code><pre class="devsite-click-to-copy">gcloud<span class="devsite-syntax-w"> </span>services<span class="devsite-syntax-w"> </span><span class="devsite-syntax-nb">enable</span><span class="devsite-syntax-w"> </span>bigquery</pre></devsite-code><p>For new projects, the BigQuery API is automatically enabled.</p>
</li>
<li>
















  





  
    
  
    
    <p>In one of the following development environments, set up the gcloud CLI:</p>
    <ul>
      <li>
        <p><b>Cloud Shell</b>: to use an online terminal with the gcloud CLI
          already set up, activate Cloud Shell.</p>
          </li>
      <li>
        <p><b>Local shell</b>: to use a local development environment,
        <a href="/sdk/docs/install">install</a> and
        <a href="/sdk/docs/initializing">
          initialize</a> the gcloud CLI.</p>
          <p>
            If you're using an external identity provider (IdP), you must first
            <a href="/iam/docs/workforce-log-in-gcloud">
              sign in to the gcloud CLI with your federated identity</a>.
          </p>
          













      </li>
    </ul>
    
  

  








</li>
<li>
<p>Activate your Google Cloud project in Cloud Shell:</p>
<devsite-code><pre class="devsite-click-to-copy"><code>gcloud<span class="devsite-syntax-w"> </span>config<span class="devsite-syntax-w"> </span><span class="devsite-syntax-nb">set</span><span class="devsite-syntax-w"> </span>project<span class="devsite-syntax-w"> </span><var>PROJECT_ID</var>
</code></pre></devsite-code>
<p>Replace <var>PROJECT_ID</var> with the project that you selected for
this walkthrough.</p>

<p>The output is similar to the following:</p>

<devsite-code><pre class="console">Updated property [core/project].
</pre></devsite-code>
</li>
</ol>


  </section>

  <section class="steps">
    

<h2 id="query_a_public_dataset">Query a public dataset</h2>

<p>Select one of the following languages:</p>
<div class="ds-selector-tabs">
<section><h3 id="c_1"> C# </h3>
<ol>
<li>
<p>In Cloud Shell, create a new C# project and file:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate">dotnet<span class="devsite-syntax-w"> </span>new<span class="devsite-syntax-w"> </span>console<span class="devsite-syntax-w"> </span>-n<span class="devsite-syntax-w"> </span>BigQueryCsharpDemo</pre></devsite-code>

<p>The output is similar to the following. Several lines are omitted to
simplify the output.</p>

<devsite-code><pre class="console">Welcome to .NET 6.0!
---------------------
SDK Version: 6.0.407
...
The template "Console App" was created successfully.
...
</pre></devsite-code>

<p>This command creates a C# project that's named
<code>BigQueryCsharpDemo</code> and a file that's named <code>Program.cs</code>.</p>
</li>
<li>
<p>Open the Cloud Shell Editor:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate">cloudshell<span class="devsite-syntax-w"> </span>workspace<span class="devsite-syntax-w"> </span>BigQueryCsharpDemo</pre></devsite-code>
</li>
<li><p>To open a terminal in the Cloud Shell Editor, click
<strong>Open Terminal</strong>.</p></li>
<li>
<p>Open your project directory:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate"><span class="devsite-syntax-nb">cd</span><span class="devsite-syntax-w"> </span>BigQueryCsharpDemo</pre></devsite-code>
</li>
<li>
<p>Install the BigQuery client library for C#:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate">dotnet<span class="devsite-syntax-w"> </span>add<span class="devsite-syntax-w"> </span>package<span class="devsite-syntax-w"> </span>Google.Cloud.BigQuery.V2</pre></devsite-code>

<p>The output is similar to the following. Several lines are omitted to
simplify the output.</p>

<devsite-code><pre class="console">Determining projects to restore...
Writing /tmp/tmpF7EKSd.tmp
...
info : Writing assets file to disk.
...
</pre></devsite-code>
</li>
<li>
<p>Set the variable <code>GOOGLE_PROJECT_ID</code> to the value <code>GOOGLE_CLOUD_PROJECT</code>
and export the variable:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate"><span class="devsite-syntax-nb">export</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nv">GOOGLE_PROJECT_ID</span><span class="devsite-syntax-o">=</span><span class="devsite-syntax-nv">$GOOGLE_CLOUD_PROJECT</span></pre></devsite-code>
</li>
<li><p>Click <strong>Open Editor</strong>.</p></li>
<li><p>In the <strong>Explorer</strong> pane, locate your <code>BIGQUERYCSHARPDEMO</code>
project.</p></li>
<li><p>Click the <code>Program.cs</code> file to open it.</p></li>
<li>
<p>To create a query against the
<code>bigquery-public-data.stackoverflow</code> dataset that returns the
top 10 most viewed Stack Overflow pages and their view counts, replace
the contents of the file with the following code:</p>

<section>
  
  
  
  
  






  
  














  



<div class="github-docwidget-gitinclude-code">

  
    
  
  











  









  




  



  


  <devsite-code><pre class="devsite-click-to-copy"><code>
<span class="devsite-syntax-k">using</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nn">System</span><span class="devsite-syntax-p">;</span>
<span class="devsite-syntax-k">using</span><span class="devsite-syntax-w"> </span><a class="devsite-xref-link" href="https://docs.cloud.google.com/dotnet/docs/reference/Google.Cloud.BigQuery.V2/latest/Google.Cloud.BigQuery.V2.html"><span class="devsite-syntax-nn">Google.Cloud.BigQuery.V2</span></a><span class="devsite-syntax-p">;</span>

<span class="devsite-syntax-k">namespace</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nn">GoogleCloudSamples</span>
<span class="devsite-syntax-p">{</span>
<span class="devsite-syntax-w">    </span><span class="devsite-syntax-k">public</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-k">class</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nc">Program</span>
<span class="devsite-syntax-w">    </span><span class="devsite-syntax-p">{</span>
<span class="devsite-syntax-w">        </span><span class="devsite-syntax-k">public</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-k">static</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-k">void</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nf">Main</span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-kt">string</span><span class="devsite-syntax-p">[]</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-n">args</span><span class="devsite-syntax-p">)</span>
<span class="devsite-syntax-w">        </span><span class="devsite-syntax-p">{</span>
<span class="devsite-syntax-w">            </span><span class="devsite-syntax-kt">string</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-n">projectId</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">=</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-n">Environment</span><span class="devsite-syntax-p">.</span><span class="devsite-syntax-n">GetEnvironmentVariable</span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-s">"GOOGLE_PROJECT_ID"</span><span class="devsite-syntax-p">);</span>
<span class="devsite-syntax-w">            </span><span class="devsite-syntax-kt">var</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-n">client</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">=</span><span class="devsite-syntax-w"> </span><a class="devsite-xref-link" href="https://docs.cloud.google.com/dotnet/docs/reference/Google.Cloud.BigQuery.V2/latest/Google.Cloud.BigQuery.V2.BigQueryClient.html"><span class="devsite-syntax-n">BigQueryClient</span></a><span class="devsite-syntax-p">.</span><a class="devsite-xref-link" href="https://docs.cloud.google.com/dotnet/docs/reference/Google.Cloud.BigQuery.V2/latest/Google.Cloud.BigQuery.V2.BigQueryClient.html#Google_Cloud_BigQuery_V2_BigQueryClient_Create_System_String_Google_Apis_Auth_OAuth2_GoogleCredential_"><span class="devsite-syntax-n">Create</span></a><span class="devsite-syntax-p">(</span><span class="devsite-syntax-n">projectId</span><span class="devsite-syntax-p">);</span>
<span class="devsite-syntax-w">            </span><span class="devsite-syntax-kt">string</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-n">query</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">=</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-s">@"SELECT</span>
<span class="devsite-syntax-s">                CONCAT(</span>
<span class="devsite-syntax-s">                    'https://stackoverflow.com/questions/',</span>
<span class="devsite-syntax-s">                    CAST(id as STRING)) as url, view_count</span>
<span class="devsite-syntax-s">                FROM `bigquery-public-data.stackoverflow.posts_questions`</span>
<span class="devsite-syntax-s">                WHERE tags like '%google-bigquery%'</span>
<span class="devsite-syntax-s">                ORDER BY view_count DESC</span>
<span class="devsite-syntax-s">                LIMIT 10"</span><span class="devsite-syntax-p">;</span>
<span class="devsite-syntax-w">            </span><span class="devsite-syntax-kt">var</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-n">result</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">=</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-n">client</span><span class="devsite-syntax-p">.</span><a class="devsite-xref-link" href="https://docs.cloud.google.com/dotnet/docs/reference/Google.Cloud.BigQuery.V2/latest/Google.Cloud.BigQuery.V2.BigQueryClient.html#Google_Cloud_BigQuery_V2_BigQueryClient_ExecuteQuery_System_String_System_Collections_Generic_IEnumerable_Google_Cloud_BigQuery_V2_BigQueryParameter__Google_Cloud_BigQuery_V2_QueryOptions_Google_Cloud_BigQuery_V2_GetQueryResultsOptions_"><span class="devsite-syntax-n">ExecuteQuery</span></a><span class="devsite-syntax-p">(</span><span class="devsite-syntax-n">query</span><span class="devsite-syntax-p">,</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-n">parameters</span><span class="devsite-syntax-p">:</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-k">null</span><span class="devsite-syntax-p">);</span>
<span class="devsite-syntax-w">            </span><span class="devsite-syntax-n">Console</span><span class="devsite-syntax-p">.</span><span class="devsite-syntax-n">Write</span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-s">"\nQuery Results:\n------------\n"</span><span class="devsite-syntax-p">);</span>
<span class="devsite-syntax-w">            </span><span class="devsite-syntax-k">foreach</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-kt">var</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-n">row</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-k">in</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-n">result</span><span class="devsite-syntax-p">)</span>
<span class="devsite-syntax-w">            </span><span class="devsite-syntax-p">{</span>
<span class="devsite-syntax-w">                </span><span class="devsite-syntax-n">Console</span><span class="devsite-syntax-p">.</span><span class="devsite-syntax-n">WriteLine</span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-s">$"{row["</span><span class="devsite-syntax-n">url</span><span class="devsite-syntax-s">"]}: {row["</span><span class="devsite-syntax-n">view_count</span><span class="devsite-syntax-s">"]} views"</span><span class="devsite-syntax-p">);</span>
<span class="devsite-syntax-w">            </span><span class="devsite-syntax-p">}</span>
<span class="devsite-syntax-w">        </span><span class="devsite-syntax-p">}</span>
<span class="devsite-syntax-w">    </span><span class="devsite-syntax-p">}</span>
<span class="devsite-syntax-p">}</span>
</code></pre></devsite-code>
</div>



























  
  
</section>


  
  
  
  
  
  
  
  
  
  



</li>
<li><p>Click <strong>Open Terminal</strong>.</p></li>
<li>
<p>In the terminal, run the <code>Program.cs</code> script. If you are prompted to
authorize Cloud Shell and agree to the terms, click
<strong>Authorize</strong>.</p>

<devsite-code><pre class="devsite-click-to-copy notranslate">dotnet<span class="devsite-syntax-w"> </span>run</pre></devsite-code>

<p>The result is similar to the following:</p>

<devsite-code><pre class="console">Query Results:
------------
https://stackoverflow.com/questions/35159967: 170023 views
https://stackoverflow.com/questions/22879669: 142581 views
https://stackoverflow.com/questions/10604135: 132406 views
https://stackoverflow.com/questions/44564887: 128781 views
https://stackoverflow.com/questions/27060396: 127008 views
https://stackoverflow.com/questions/12482637: 120766 views
https://stackoverflow.com/questions/20673986: 115720 views
https://stackoverflow.com/questions/39109817: 108368 views
https://stackoverflow.com/questions/11057219: 105175 views
https://stackoverflow.com/questions/43195143: 101878 views
</pre></devsite-code>
</li>
</ol>

<p>You have successfully queried a public dataset with the
BigQuery C# client library.</p></section>
<section><h3 id="go_1"> Go </h3>
<ol>
<li>
<p>In Cloud Shell, create a new Go project and file:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate">mkdir<span class="devsite-syntax-w"> </span>bigquery-go-quickstart<span class="devsite-syntax-w"> </span><span class="devsite-syntax-se">\</span>
<span class="devsite-syntax-w">    </span><span class="devsite-syntax-o">&amp;&amp;</span><span class="devsite-syntax-w"> </span>touch<span class="devsite-syntax-w"> </span><span class="devsite-syntax-se">\</span>
<span class="devsite-syntax-w">    </span>bigquery-go-quickstart/app.go</pre></devsite-code>

<p>This command creates a Go project that's named
<code>bigquery-go-quickstart</code> and a file that's named <code>app.go</code>.</p>
</li>
<li>
<p>Open the Cloud Shell Editor:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate">cloudshell<span class="devsite-syntax-w"> </span>workspace<span class="devsite-syntax-w"> </span>bigquery-go-quickstart</pre></devsite-code>
</li>
<li><p>To open a terminal in the Cloud Shell Editor, click
<strong>Open Terminal</strong>.</p></li>
<li>
<p>Open your project directory:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate"><span class="devsite-syntax-nb">cd</span><span class="devsite-syntax-w"> </span>bigquery-go-quickstart</pre></devsite-code>
</li>
<li>
<p>Create a <code>go.mod</code> file:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate">go<span class="devsite-syntax-w"> </span>mod<span class="devsite-syntax-w"> </span>init<span class="devsite-syntax-w"> </span>quickstart</pre></devsite-code>

<p>The output is similar to the following:</p>

<devsite-code><pre class="console">go: creating new go.mod: module quickstart
go: to add module requirements and sums:
        go mod tidy
</pre></devsite-code>
</li>
<li>
<p>Install the BigQuery client library for Go:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate">go<span class="devsite-syntax-w"> </span>get<span class="devsite-syntax-w"> </span>cloud.google.com/go/bigquery</pre></devsite-code>

<p>The output is similar to the following. Several lines are omitted to
simplify the output.</p>

<devsite-code><pre class="console">go: downloading cloud.google.com/go/bigquery v1.49.0
go: downloading cloud.google.com/go v0.110.0
...
go: added cloud.google.com/go/bigquery v1.49.0
go: added cloud.google.com/go v0.110.0
</pre></devsite-code>
</li>
<li><p>Click <strong>Open Editor</strong>.</p></li>
<li><p>In the <strong>Explorer</strong> pane, locate your <code>BIGQUERY-GO-QUICKSTART</code>
project.</p></li>
<li><p>Click the <code>app.go</code> file to open it.</p></li>
<li>
<p>To create a query against the
<code>bigquery-public-data.stackoverflow</code> dataset that returns the
top 10 most viewed Stack Overflow pages and their view counts, copy the
following code into the <code>app.go</code> file:</p>

<section>
  
  
  
  
  






  
  














  



<div class="github-docwidget-gitinclude-code">

  
    
  
  











  









  




  



  


  <devsite-code><pre class="devsite-click-to-copy"><code>
<span class="devsite-syntax-c1">// Command simpleapp queries the Stack Overflow public dataset in Google BigQuery.</span>
<span class="devsite-syntax-kn">package</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">main</span>

<span class="devsite-syntax-kn">import</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-p">(</span>
<span class="devsite-syntax-w">	</span><span class="devsite-syntax-s">"context"</span>
<span class="devsite-syntax-w">	</span><span class="devsite-syntax-s">"fmt"</span>
<span class="devsite-syntax-w">	</span><span class="devsite-syntax-s">"io"</span>
<span class="devsite-syntax-w">	</span><span class="devsite-syntax-s">"log"</span>
<span class="devsite-syntax-w">	</span><span class="devsite-syntax-s">"os"</span>

<span class="devsite-syntax-w">	</span><span class="devsite-syntax-s">"cloud.google.com/go/bigquery"</span>
<span class="devsite-syntax-w">	</span><span class="devsite-syntax-s">"google.golang.org/api/iterator"</span>
<span class="devsite-syntax-p">)</span>


<span class="devsite-syntax-kd">func</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">main</span><span class="devsite-syntax-p">()</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-p">{</span>
<span class="devsite-syntax-w">	</span><span class="devsite-syntax-nx">projectID</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">:=</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">os</span><span class="devsite-syntax-p">.</span><span class="devsite-syntax-nx">Getenv</span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-s">"GOOGLE_CLOUD_PROJECT"</span><span class="devsite-syntax-p">)</span>
<span class="devsite-syntax-w">	</span><span class="devsite-syntax-k">if</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">projectID</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">==</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-s">""</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-p">{</span>
<span class="devsite-syntax-w">		</span><span class="devsite-syntax-nx">fmt</span><span class="devsite-syntax-p">.</span><span class="devsite-syntax-nx">Println</span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-s">"GOOGLE_CLOUD_PROJECT environment variable must be set."</span><span class="devsite-syntax-p">)</span>
<span class="devsite-syntax-w">		</span><span class="devsite-syntax-nx">os</span><span class="devsite-syntax-p">.</span><span class="devsite-syntax-nx">Exit</span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-mi">1</span><span class="devsite-syntax-p">)</span>
<span class="devsite-syntax-w">	</span><span class="devsite-syntax-p">}</span>

<span class="devsite-syntax-w">	</span><span class="devsite-syntax-nx">ctx</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">:=</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">context</span><span class="devsite-syntax-p">.</span><span class="devsite-syntax-nx">Background</span><span class="devsite-syntax-p">()</span>

<span class="devsite-syntax-w">	</span><span class="devsite-syntax-nx">client</span><span class="devsite-syntax-p">,</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">err</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">:=</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">bigquery</span><span class="devsite-syntax-p">.</span><span class="devsite-syntax-nx">NewClient</span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-nx">ctx</span><span class="devsite-syntax-p">,</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">projectID</span><span class="devsite-syntax-p">)</span>
<span class="devsite-syntax-w">	</span><span class="devsite-syntax-k">if</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">err</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">!=</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-kc">nil</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-p">{</span>
<span class="devsite-syntax-w">		</span><span class="devsite-syntax-nx">log</span><span class="devsite-syntax-p">.</span><span class="devsite-syntax-nx">Fatalf</span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-s">"bigquery.NewClient: %v"</span><span class="devsite-syntax-p">,</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">err</span><span class="devsite-syntax-p">)</span>
<span class="devsite-syntax-w">	</span><span class="devsite-syntax-p">}</span>
<span class="devsite-syntax-w">	</span><span class="devsite-syntax-k">defer</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">client</span><span class="devsite-syntax-p">.</span><span class="devsite-syntax-nx">Close</span><span class="devsite-syntax-p">()</span>

<span class="devsite-syntax-w">	</span><span class="devsite-syntax-nx">rows</span><span class="devsite-syntax-p">,</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">err</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">:=</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">query</span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-nx">ctx</span><span class="devsite-syntax-p">,</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">client</span><span class="devsite-syntax-p">)</span>
<span class="devsite-syntax-w">	</span><span class="devsite-syntax-k">if</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">err</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">!=</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-kc">nil</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-p">{</span>
<span class="devsite-syntax-w">		</span><span class="devsite-syntax-nx">log</span><span class="devsite-syntax-p">.</span><span class="devsite-syntax-nx">Fatal</span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-nx">err</span><span class="devsite-syntax-p">)</span>
<span class="devsite-syntax-w">	</span><span class="devsite-syntax-p">}</span>
<span class="devsite-syntax-w">	</span><span class="devsite-syntax-k">if</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">err</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">:=</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">printResults</span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-nx">os</span><span class="devsite-syntax-p">.</span><span class="devsite-syntax-nx">Stdout</span><span class="devsite-syntax-p">,</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">rows</span><span class="devsite-syntax-p">);</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">err</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">!=</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-kc">nil</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-p">{</span>
<span class="devsite-syntax-w">		</span><span class="devsite-syntax-nx">log</span><span class="devsite-syntax-p">.</span><span class="devsite-syntax-nx">Fatal</span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-nx">err</span><span class="devsite-syntax-p">)</span>
<span class="devsite-syntax-w">	</span><span class="devsite-syntax-p">}</span>
<span class="devsite-syntax-p">}</span>

<span class="devsite-syntax-c1">// query returns a row iterator suitable for reading query results.</span>
<span class="devsite-syntax-kd">func</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">query</span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-nx">ctx</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">context</span><span class="devsite-syntax-p">.</span><span class="devsite-syntax-nx">Context</span><span class="devsite-syntax-p">,</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">client</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">*</span><span class="devsite-syntax-nx">bigquery</span><span class="devsite-syntax-p">.</span><span class="devsite-syntax-nx">Client</span><span class="devsite-syntax-p">)</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-o">*</span><span class="devsite-syntax-nx">bigquery</span><span class="devsite-syntax-p">.</span><a class="devsite-xref-link" href="https://docs.cloud.google.com/go/docs/reference/cloud.google.com/go/bigquery/latest/index.html#cloud_google_com_go_bigquery_RowIterator"><span class="devsite-syntax-nx">RowIterator</span></a><span class="devsite-syntax-p">,</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-kt">error</span><span class="devsite-syntax-p">)</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-p">{</span>

<span class="devsite-syntax-w">	</span><span class="devsite-syntax-nx">query</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">:=</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">client</span><span class="devsite-syntax-p">.</span><span class="devsite-syntax-nx">Query</span><span class="devsite-syntax-p">(</span>
<span class="devsite-syntax-w">		</span><span class="devsite-syntax-s">`SELECT</span>
<span class="devsite-syntax-s">			CONCAT(</span>
<span class="devsite-syntax-s">				'https://stackoverflow.com/questions/',</span>
<span class="devsite-syntax-s">				CAST(id as STRING)) as url,</span>
<span class="devsite-syntax-s">			view_count</span>
<span class="devsite-syntax-s">		FROM `</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">+</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-s">"`bigquery-public-data.stackoverflow.posts_questions`"</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">+</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-s">`</span>
<span class="devsite-syntax-s">		WHERE tags like '%google-bigquery%'</span>
<span class="devsite-syntax-s">		ORDER BY view_count DESC</span>
<span class="devsite-syntax-s">		LIMIT 10;`</span><span class="devsite-syntax-p">)</span>
<span class="devsite-syntax-w">	</span><span class="devsite-syntax-k">return</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">query</span><span class="devsite-syntax-p">.</span><span class="devsite-syntax-nx">Read</span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-nx">ctx</span><span class="devsite-syntax-p">)</span>
<span class="devsite-syntax-p">}</span>

<span class="devsite-syntax-kd">type</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">StackOverflowRow</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-kd">struct</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-p">{</span>
<span class="devsite-syntax-w">	</span><span class="devsite-syntax-nx">URL</span><span class="devsite-syntax-w">       </span><span class="devsite-syntax-kt">string</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-s">`bigquery:"url"`</span>
<span class="devsite-syntax-w">	</span><span class="devsite-syntax-nx">ViewCount</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-kt">int64</span><span class="devsite-syntax-w">  </span><span class="devsite-syntax-s">`bigquery:"view_count"`</span>
<span class="devsite-syntax-p">}</span>

<span class="devsite-syntax-c1">// printResults prints results from a query to the Stack Overflow public dataset.</span>
<span class="devsite-syntax-kd">func</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">printResults</span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-nx">w</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">io</span><span class="devsite-syntax-p">.</span><span class="devsite-syntax-nx">Writer</span><span class="devsite-syntax-p">,</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">iter</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">*</span><span class="devsite-syntax-nx">bigquery</span><span class="devsite-syntax-p">.</span><a class="devsite-xref-link" href="https://docs.cloud.google.com/go/docs/reference/cloud.google.com/go/bigquery/latest/index.html#cloud_google_com_go_bigquery_RowIterator"><span class="devsite-syntax-nx">RowIterator</span></a><span class="devsite-syntax-p">)</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-kt">error</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-p">{</span>
<span class="devsite-syntax-w">	</span><span class="devsite-syntax-k">for</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-p">{</span>
<span class="devsite-syntax-w">		</span><span class="devsite-syntax-kd">var</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">row</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">StackOverflowRow</span>
<span class="devsite-syntax-w">		</span><span class="devsite-syntax-nx">err</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">:=</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">iter</span><span class="devsite-syntax-p">.</span><span class="devsite-syntax-nx">Next</span><span class="devsite-syntax-p">(</span>&amp;<span class="devsite-syntax-nx">row</span><span class="devsite-syntax-p">)</span>
<span class="devsite-syntax-w">		</span><span class="devsite-syntax-k">if</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">err</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">==</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">iterator</span><span class="devsite-syntax-p">.</span><span class="devsite-syntax-nx">Done</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-p">{</span>
<span class="devsite-syntax-w">			</span><span class="devsite-syntax-k">return</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-kc">nil</span>
<span class="devsite-syntax-w">		</span><span class="devsite-syntax-p">}</span>
<span class="devsite-syntax-w">		</span><span class="devsite-syntax-k">if</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">err</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">!=</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-kc">nil</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-p">{</span>
<span class="devsite-syntax-w">			</span><span class="devsite-syntax-k">return</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">fmt</span><span class="devsite-syntax-p">.</span><span class="devsite-syntax-nx">Errorf</span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-s">"error iterating through results: %w"</span><span class="devsite-syntax-p">,</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">err</span><span class="devsite-syntax-p">)</span>
<span class="devsite-syntax-w">		</span><span class="devsite-syntax-p">}</span>

<span class="devsite-syntax-w">		</span><span class="devsite-syntax-nx">fmt</span><span class="devsite-syntax-p">.</span><span class="devsite-syntax-nx">Fprintf</span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-nx">w</span><span class="devsite-syntax-p">,</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-s">"url: %s views: %d\n"</span><span class="devsite-syntax-p">,</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">row</span><span class="devsite-syntax-p">.</span><span class="devsite-syntax-nx">URL</span><span class="devsite-syntax-p">,</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">row</span><span class="devsite-syntax-p">.</span><span class="devsite-syntax-nx">ViewCount</span><span class="devsite-syntax-p">)</span>
<span class="devsite-syntax-w">	</span><span class="devsite-syntax-p">}</span>
<span class="devsite-syntax-p">}</span>
</code></pre></devsite-code>
</div>



























  
  
</section>


  
  
  
  
  
  
  
  
  
  



</li>
<li><p>Click <strong>Open Terminal</strong>.</p></li>
<li>
<p>In the terminal, run the <code>app.go</code> script. If you are prompted to
authorize Cloud Shell and agree to the terms, click
<strong>Authorize</strong>.</p>

<devsite-code><pre class="devsite-click-to-copy notranslate">go<span class="devsite-syntax-w"> </span>run<span class="devsite-syntax-w"> </span>app.go</pre></devsite-code>

<p>The result is similar to the following:</p>

<devsite-code><pre class="console">https://stackoverflow.com/questions/35159967 : 170023 views
https://stackoverflow.com/questions/22879669 : 142581 views
https://stackoverflow.com/questions/10604135 : 132406 views
https://stackoverflow.com/questions/44564887 : 128781 views
https://stackoverflow.com/questions/27060396 : 127008 views
https://stackoverflow.com/questions/12482637 : 120766 views
https://stackoverflow.com/questions/20673986 : 115720 views
https://stackoverflow.com/questions/39109817 : 108368 views
https://stackoverflow.com/questions/11057219 : 105175 views
https://stackoverflow.com/questions/43195143 : 101878 views
</pre></devsite-code>
</li>
</ol>

<p>You have successfully queried a public dataset with the
BigQuery Go client library.</p></section>
<section><h3 id="java_1"> Java </h3>
<ol>
<li>
<p>In Cloud Shell, create a new Java project using Apache Maven:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate">mvn<span class="devsite-syntax-w"> </span>archetype:generate<span class="devsite-syntax-w"> </span><span class="devsite-syntax-se">\</span>
<span class="devsite-syntax-w">    </span>-DgroupId<span class="devsite-syntax-o">=</span>com.google.app<span class="devsite-syntax-w"> </span><span class="devsite-syntax-se">\</span>
<span class="devsite-syntax-w">    </span>-DartifactId<span class="devsite-syntax-o">=</span>bigquery-java-quickstart<span class="devsite-syntax-w"> </span><span class="devsite-syntax-se">\</span>
<span class="devsite-syntax-w">    </span>-DinteractiveMode<span class="devsite-syntax-o">=</span><span class="devsite-syntax-nb">false</span></pre></devsite-code>

<p>This command creates a Maven project that's named
<code>bigquery-java-quickstart</code>.</p>

<p>The output is similar to the following. Several lines are omitted to
simplify the output.</p>

<devsite-code><pre class="console">[INFO] Scanning for projects...
...
[INFO] Building Maven Stub Project (No POM) 1
...
[INFO] BUILD SUCCESS
...
</pre></devsite-code>

<p>There are many dependency management systems that you can use other than
Maven. For more information, learn how to
<a href="/java/docs/setup">set up a Java development environment</a> to use with
client libraries.</p>
</li>
<li>
<p>Rename the <code>App.java</code> file that Maven creates by default:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate">mv<span class="devsite-syntax-w"> </span><span class="devsite-syntax-se">\</span>
<span class="devsite-syntax-w">    </span>bigquery-java-quickstart/src/main/java/com/google/app/App.java<span class="devsite-syntax-w"> </span><span class="devsite-syntax-se">\</span>
<span class="devsite-syntax-w">    </span>bigquery-java-quickstart/src/main/java/com/google/app/SimpleApp.java</pre></devsite-code>
</li>
<li>
<p>Open the Cloud Shell Editor:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate">cloudshell<span class="devsite-syntax-w"> </span>workspace<span class="devsite-syntax-w"> </span>bigquery-java-quickstart</pre></devsite-code>
</li>
<li>
<p>If you are prompted whether to synchronize the Java
classpath or configuration, click <strong>Always</strong>.</p>

<p>If you are not prompted and encounter an error that is
related to the classpath during this walkthrough, do the following:</p>

<ol>
<li>Click <strong>File <span>&gt;</span> Preferences <span>&gt;</span> Open Settings (UI)</strong>.</li>
<li>Click <strong>Extensions <span>&gt;</span> Java</strong>.</li>
<li>Scroll to <strong>Configuration: Update Build Configuration</strong> and select
<strong>automatic</strong>.</li>
</ol>
</li>
<li><p>In the <strong>Explorer</strong> pane, locate your <code>BIGQUERY-JAVA-QUICKSTART</code>
project.</p></li>
<li><p>Click the <code>pom.xml</code> file to open it.</p></li>
<li>
<p>Inside the <code>&lt;dependencies&gt;</code> tag, add the following dependency
after any existing ones. Do not replace any existing dependencies.</p>
<devsite-code><pre class="devsite-click-to-copy"><code>&lt;dependency&gt;
<span class="devsite-syntax-w">  </span>&lt;groupId&gt;com.google.cloud&lt;/groupId&gt;
<span class="devsite-syntax-w">  </span>&lt;artifactId&gt;google-cloud-bigquery&lt;/artifactId&gt;
&lt;/dependency&gt;
</code></pre></devsite-code>
</li>
<li>
<p>On the line following the closing tag (<code>&lt;/dependencies&gt;</code>), add the
following:</p>
<devsite-code><pre class="devsite-click-to-copy"><code>&lt;dependencyManagement&gt;
<span class="devsite-syntax-w">  </span>&lt;dependencies&gt;
<span class="devsite-syntax-w">    </span>&lt;dependency&gt;
<span class="devsite-syntax-w">      </span>&lt;groupId&gt;com.google.cloud&lt;/groupId&gt;
<span class="devsite-syntax-w">      </span>&lt;artifactId&gt;libraries-bom&lt;/artifactId&gt;
<span class="devsite-syntax-w">      </span>&lt;version&gt;26.1.5&lt;/version&gt;
<span class="devsite-syntax-w">      </span>&lt;type&gt;pom&lt;/type&gt;
<span class="devsite-syntax-w">      </span>&lt;scope&gt;import&lt;/scope&gt;
<span class="devsite-syntax-w">    </span>&lt;/dependency&gt;
<span class="devsite-syntax-w">  </span>&lt;/dependencies&gt;
&lt;/dependencyManagement&gt;
</code></pre></devsite-code>
</li>
<li><p>In the <strong>Explorer</strong> pane, in your <code>BIGQUERY-JAVA-QUICKSTART</code> project,
click <strong>src <span>&gt;</span> main/java/com/google/app <span>&gt;</span> SimpleApp.java</strong>.
The file opens.</p></li>
<li>
<p>To create a query against the
<code>bigquery-public-data.stackoverflow</code> dataset, leave the
first line of the file (<code>package com.google.app;</code>), and replace the
remaining contents of the file with the following code:</p>

<section>
  
  
  
  
  






  
  














  



<div class="github-docwidget-gitinclude-code">

  
    
  
  











  









  




  



  


  <devsite-code><pre class="devsite-click-to-copy"><code>
<span class="devsite-syntax-kn">import</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nn">com.google.cloud.bigquery.<a class="devsite-xref-link" href="https://docs.cloud.google.com/java/docs/reference/google-cloud-bigquery/latest/com.google.cloud.bigquery.BigQuery.html">BigQuery</a></span><span class="devsite-syntax-p">;</span>
<span class="devsite-syntax-kn">import</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nn">com.google.cloud.bigquery.<a class="devsite-xref-link" href="https://docs.cloud.google.com/java/docs/reference/google-cloud-bigquery/latest/com.google.cloud.bigquery.BigQueryException.html">BigQueryException</a></span><span class="devsite-syntax-p">;</span>
<span class="devsite-syntax-kn">import</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nn">com.google.cloud.bigquery.<a class="devsite-xref-link" href="https://docs.cloud.google.com/java/docs/reference/google-cloud-bigquery/latest/com.google.cloud.bigquery.BigQueryOptions.html">BigQueryOptions</a></span><span class="devsite-syntax-p">;</span>
<span class="devsite-syntax-kn">import</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nn">com.google.cloud.bigquery.<a class="devsite-xref-link" href="https://docs.cloud.google.com/java/docs/reference/google-cloud-bigquery/latest/com.google.cloud.bigquery.FieldValueList.html">FieldValueList</a></span><span class="devsite-syntax-p">;</span>
<span class="devsite-syntax-kn">import</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nn">com.google.cloud.bigquery.<a class="devsite-xref-link" href="https://docs.cloud.google.com/java/docs/reference/google-cloud-bigquery/latest/com.google.cloud.bigquery.Job.html">Job</a></span><span class="devsite-syntax-p">;</span>
<span class="devsite-syntax-kn">import</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nn">com.google.cloud.bigquery.<a class="devsite-xref-link" href="https://docs.cloud.google.com/java/docs/reference/google-cloud-bigquery/latest/com.google.cloud.bigquery.JobId.html">JobId</a></span><span class="devsite-syntax-p">;</span>
<span class="devsite-syntax-kn">import</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nn">com.google.cloud.bigquery.<a class="devsite-xref-link" href="https://docs.cloud.google.com/java/docs/reference/google-cloud-bigquery/latest/com.google.cloud.bigquery.JobInfo.html">JobInfo</a></span><span class="devsite-syntax-p">;</span>
<span class="devsite-syntax-kn">import</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nn">com.google.cloud.bigquery.<a class="devsite-xref-link" href="https://docs.cloud.google.com/java/docs/reference/google-cloud-bigquery/latest/com.google.cloud.bigquery.QueryJobConfiguration.html">QueryJobConfiguration</a></span><span class="devsite-syntax-p">;</span>
<span class="devsite-syntax-kn">import</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nn">com.google.cloud.bigquery.<a class="devsite-xref-link" href="https://docs.cloud.google.com/java/docs/reference/google-cloud-bigquery/latest/com.google.cloud.bigquery.TableResult.html">TableResult</a></span><span class="devsite-syntax-p">;</span>


<span class="devsite-syntax-kd">public</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-kd">class</span> <span class="devsite-syntax-nc">SimpleApp</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-p">{</span>

<span class="devsite-syntax-w">  </span><span class="devsite-syntax-kd">public</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-kd">static</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-kt">void</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nf">main</span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-n">String</span><span class="devsite-syntax-p">...</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-n">args</span><span class="devsite-syntax-p">)</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-kd">throws</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-n">Exception</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-p">{</span>
<span class="devsite-syntax-w">    </span><span class="devsite-syntax-c1">// TODO(developer): Replace these variables before running the app.</span>
<span class="devsite-syntax-w">    </span><span class="devsite-syntax-n">String</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-n">projectId</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">=</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-s">"MY_PROJECT_ID"</span><span class="devsite-syntax-p">;</span>
<span class="devsite-syntax-w">    </span><span class="devsite-syntax-n">simpleApp</span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-n">projectId</span><span class="devsite-syntax-p">);</span>
<span class="devsite-syntax-w">  </span><span class="devsite-syntax-p">}</span>

<span class="devsite-syntax-w">  </span><span class="devsite-syntax-kd">public</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-kd">static</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-kt">void</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nf">simpleApp</span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-n">String</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-n">projectId</span><span class="devsite-syntax-p">)</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-p">{</span>
<span class="devsite-syntax-w">    </span><span class="devsite-syntax-k">try</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-p">{</span>
<span class="devsite-syntax-w">      </span><a class="devsite-xref-link" href="https://docs.cloud.google.com/java/docs/reference/google-cloud-bigquery/latest/com.google.cloud.bigquery.BigQuery.html"><span class="devsite-syntax-n">BigQuery</span></a><span class="devsite-syntax-w"> </span><span class="devsite-syntax-n">bigquery</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">=</span><span class="devsite-syntax-w"> </span><a class="devsite-xref-link" href="https://docs.cloud.google.com/java/docs/reference/google-cloud-bigquery/latest/com.google.cloud.bigquery.BigQueryOptions.html"><span class="devsite-syntax-n">BigQueryOptions</span></a><span class="devsite-syntax-p">.</span><span class="devsite-syntax-na">getDefaultInstance</span><span class="devsite-syntax-p">().</span><span class="devsite-syntax-na">getService</span><span class="devsite-syntax-p">();</span>
<span class="devsite-syntax-w">      </span><a class="devsite-xref-link" href="https://docs.cloud.google.com/java/docs/reference/google-cloud-bigquery/latest/com.google.cloud.bigquery.QueryJobConfiguration.html"><span class="devsite-syntax-n">QueryJobConfiguration</span></a><span class="devsite-syntax-w"> </span><span class="devsite-syntax-n">queryConfig</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">=</span>
<span class="devsite-syntax-w">          </span><a class="devsite-xref-link" href="https://docs.cloud.google.com/java/docs/reference/google-cloud-bigquery/latest/com.google.cloud.bigquery.QueryJobConfiguration.html"><span class="devsite-syntax-n">QueryJobConfiguration</span></a><span class="devsite-syntax-p">.</span><span class="devsite-syntax-na">newBuilder</span><span class="devsite-syntax-p">(</span>
<span class="devsite-syntax-w">                  </span><span class="devsite-syntax-s">"SELECT CONCAT('https://stackoverflow.com/questions/', "</span>
<span class="devsite-syntax-w">                      </span><span class="devsite-syntax-o">+</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-s">"CAST(id as STRING)) as url, view_count "</span>
<span class="devsite-syntax-w">                      </span><span class="devsite-syntax-o">+</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-s">"FROM `bigquery-public-data.stackoverflow.posts_questions` "</span>
<span class="devsite-syntax-w">                      </span><span class="devsite-syntax-o">+</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-s">"WHERE tags like '%google-bigquery%' "</span>
<span class="devsite-syntax-w">                      </span><span class="devsite-syntax-o">+</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-s">"ORDER BY view_count DESC "</span>
<span class="devsite-syntax-w">                      </span><span class="devsite-syntax-o">+</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-s">"LIMIT 10"</span><span class="devsite-syntax-p">)</span>
<span class="devsite-syntax-w">              </span><span class="devsite-syntax-c1">// Use standard SQL syntax for queries.</span>
<span class="devsite-syntax-w">              </span><span class="devsite-syntax-c1">// See: https://cloud.google.com/bigquery/sql-reference/</span>
<span class="devsite-syntax-w">              </span><span class="devsite-syntax-p">.</span><span class="devsite-syntax-na">setUseLegacySql</span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-kc">false</span><span class="devsite-syntax-p">)</span>
<span class="devsite-syntax-w">              </span><span class="devsite-syntax-p">.</span><span class="devsite-syntax-na">build</span><span class="devsite-syntax-p">();</span>

<span class="devsite-syntax-w">      </span><a class="devsite-xref-link" href="https://docs.cloud.google.com/java/docs/reference/google-cloud-bigquery/latest/com.google.cloud.bigquery.JobId.html"><span class="devsite-syntax-n">JobId</span></a><span class="devsite-syntax-w"> </span><span class="devsite-syntax-n">jobId</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">=</span><span class="devsite-syntax-w"> </span><a class="devsite-xref-link" href="https://docs.cloud.google.com/java/docs/reference/google-cloud-bigquery/latest/com.google.cloud.bigquery.JobId.html"><span class="devsite-syntax-n">JobId</span></a><span class="devsite-syntax-p">.</span><span class="devsite-syntax-na">newBuilder</span><span class="devsite-syntax-p">().</span><span class="devsite-syntax-na">setProject</span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-n">projectId</span><span class="devsite-syntax-p">).</span><span class="devsite-syntax-na">build</span><span class="devsite-syntax-p">();</span>
<span class="devsite-syntax-w">      </span><a class="devsite-xref-link" href="https://docs.cloud.google.com/java/docs/reference/google-cloud-bigquery/latest/com.google.cloud.bigquery.Job.html"><span class="devsite-syntax-n">Job</span></a><span class="devsite-syntax-w"> </span><span class="devsite-syntax-n">queryJob</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">=</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-n">bigquery</span><span class="devsite-syntax-p">.</span><a class="devsite-xref-link" href="https://docs.cloud.google.com/java/docs/reference/google-cloud-bigquery/latest/com.google.cloud.bigquery.BigQuery.html#com_google_cloud_bigquery_BigQuery_create_com_google_cloud_bigquery_DatasetInfo_com_google_cloud_bigquery_BigQuery_DatasetOption____"><span class="devsite-syntax-na">create</span></a><span class="devsite-syntax-p">(</span><span class="devsite-syntax-n">JobInfo</span><span class="devsite-syntax-p">.</span><span class="devsite-syntax-na">newBuilder</span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-n">queryConfig</span><span class="devsite-syntax-p">).</span><span class="devsite-syntax-na">setJobId</span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-n">jobId</span><span class="devsite-syntax-p">).</span><span class="devsite-syntax-na">build</span><span class="devsite-syntax-p">());</span>

<span class="devsite-syntax-w">      </span><span class="devsite-syntax-c1">// Wait for the query to complete.</span>
<span class="devsite-syntax-w">      </span><span class="devsite-syntax-n">queryJob</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">=</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-n">queryJob</span><span class="devsite-syntax-p">.</span><a class="devsite-xref-link" href="https://docs.cloud.google.com/java/docs/reference/google-cloud-bigquery/latest/com.google.cloud.bigquery.Job.html#com_google_cloud_bigquery_Job_waitFor_com_google_cloud_bigquery_BigQueryRetryConfig_com_google_cloud_RetryOption____"><span class="devsite-syntax-na">waitFor</span></a><span class="devsite-syntax-p">();</span>

<span class="devsite-syntax-w">      </span><span class="devsite-syntax-c1">// Check for errors</span>
<span class="devsite-syntax-w">      </span><span class="devsite-syntax-k">if</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-n">queryJob</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">==</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-kc">null</span><span class="devsite-syntax-p">)</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-p">{</span>
<span class="devsite-syntax-w">        </span><span class="devsite-syntax-k">throw</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-k">new</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-n">RuntimeException</span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-s">"Job no longer exists"</span><span class="devsite-syntax-p">);</span>
<span class="devsite-syntax-w">      </span><span class="devsite-syntax-p">}</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-k">else</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-k">if</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-n">queryJob</span><span class="devsite-syntax-p">.</span><span class="devsite-syntax-na">getStatus</span><span class="devsite-syntax-p">().</span><a class="devsite-xref-link" href="https://docs.cloud.google.com/java/docs/reference/google-cloud-bigquery/latest/com.google.cloud.bigquery.JobStatus.html#com_google_cloud_bigquery_JobStatus_getExecutionErrors__"><span class="devsite-syntax-na">getExecutionErrors</span></a><span class="devsite-syntax-p">()</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">!=</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-kc">null</span>
<span class="devsite-syntax-w">          &amp;&amp; </span><span class="devsite-syntax-n">queryJob</span><span class="devsite-syntax-p">.</span><span class="devsite-syntax-na">getStatus</span><span class="devsite-syntax-p">().</span><span class="devsite-syntax-na">getExecutionErrors</span><span class="devsite-syntax-p">().</span><span class="devsite-syntax-na">size</span><span class="devsite-syntax-p">()</span><span class="devsite-syntax-w"> &gt; </span><span class="devsite-syntax-mi">0</span><span class="devsite-syntax-p">)</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-p">{</span>
<span class="devsite-syntax-w">        </span><span class="devsite-syntax-c1">// TODO(developer): Handle errors here. An error here do not necessarily mean that the job</span>
<span class="devsite-syntax-w">        </span><span class="devsite-syntax-c1">// has completed or was unsuccessful.</span>
<span class="devsite-syntax-w">        </span><span class="devsite-syntax-c1">// For more details: https://cloud.google.com/bigquery/troubleshooting-errors</span>
<span class="devsite-syntax-w">        </span><span class="devsite-syntax-k">throw</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-k">new</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-n">RuntimeException</span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-s">"An unhandled error has occurred"</span><span class="devsite-syntax-p">);</span>
<span class="devsite-syntax-w">      </span><span class="devsite-syntax-p">}</span>

<span class="devsite-syntax-w">      </span><span class="devsite-syntax-c1">// Get the results.</span>
<span class="devsite-syntax-w">      </span><a class="devsite-xref-link" href="https://docs.cloud.google.com/java/docs/reference/google-cloud-bigquery/latest/com.google.cloud.bigquery.TableResult.html"><span class="devsite-syntax-n">TableResult</span></a><span class="devsite-syntax-w"> </span><span class="devsite-syntax-n">result</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">=</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-n">queryJob</span><span class="devsite-syntax-p">.</span><a class="devsite-xref-link" href="https://docs.cloud.google.com/java/docs/reference/google-cloud-bigquery/latest/com.google.cloud.bigquery.Job.html#com_google_cloud_bigquery_Job_getQueryResults_com_google_cloud_bigquery_BigQuery_QueryResultsOption____"><span class="devsite-syntax-na">getQueryResults</span></a><span class="devsite-syntax-p">();</span>

<span class="devsite-syntax-w">      </span><span class="devsite-syntax-c1">// Print all pages of the results.</span>
<span class="devsite-syntax-w">      </span><span class="devsite-syntax-k">for</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-p">(</span><a class="devsite-xref-link" href="https://docs.cloud.google.com/java/docs/reference/google-cloud-bigquery/latest/com.google.cloud.bigquery.FieldValueList.html"><span class="devsite-syntax-n">FieldValueList</span></a><span class="devsite-syntax-w"> </span><span class="devsite-syntax-n">row</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-p">:</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-n">result</span><span class="devsite-syntax-p">.</span><a class="devsite-xref-link" href="https://docs.cloud.google.com/java/docs/reference/google-cloud-bigquery/latest/com.google.cloud.bigquery.TableResult.html#com_google_cloud_bigquery_TableResult_iterateAll__"><span class="devsite-syntax-na">iterateAll</span></a><span class="devsite-syntax-p">())</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-p">{</span>
<span class="devsite-syntax-w">        </span><span class="devsite-syntax-c1">// String type</span>
<span class="devsite-syntax-w">        </span><span class="devsite-syntax-n">String</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-n">url</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">=</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-n">row</span><span class="devsite-syntax-p">.</span><span class="devsite-syntax-na">get</span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-s">"url"</span><span class="devsite-syntax-p">).</span><span class="devsite-syntax-na">getStringValue</span><span class="devsite-syntax-p">();</span>
<span class="devsite-syntax-w">        </span><span class="devsite-syntax-n">String</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-n">viewCount</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">=</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-n">row</span><span class="devsite-syntax-p">.</span><span class="devsite-syntax-na">get</span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-s">"view_count"</span><span class="devsite-syntax-p">).</span><span class="devsite-syntax-na">getStringValue</span><span class="devsite-syntax-p">();</span>
<span class="devsite-syntax-w">        </span><span class="devsite-syntax-n">System</span><span class="devsite-syntax-p">.</span><span class="devsite-syntax-na">out</span><span class="devsite-syntax-p">.</span><span class="devsite-syntax-na">printf</span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-s">"%s : %s views\n"</span><span class="devsite-syntax-p">,</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-n">url</span><span class="devsite-syntax-p">,</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-n">viewCount</span><span class="devsite-syntax-p">);</span>
<span class="devsite-syntax-w">      </span><span class="devsite-syntax-p">}</span>
<span class="devsite-syntax-w">    </span><span class="devsite-syntax-p">}</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-k">catch</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-p">(</span><a class="devsite-xref-link" href="https://docs.cloud.google.com/java/docs/reference/google-cloud-bigquery/latest/com.google.cloud.bigquery.BigQueryException.html"><span class="devsite-syntax-n">BigQueryException</span></a><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">|</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-n">InterruptedException</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-n">e</span><span class="devsite-syntax-p">)</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-p">{</span>
<span class="devsite-syntax-w">      </span><span class="devsite-syntax-n">System</span><span class="devsite-syntax-p">.</span><span class="devsite-syntax-na">out</span><span class="devsite-syntax-p">.</span><span class="devsite-syntax-na">println</span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-s">"Simple App failed due to error: \n"</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">+</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-n">e</span><span class="devsite-syntax-p">.</span><span class="devsite-syntax-na">toString</span><span class="devsite-syntax-p">());</span>
<span class="devsite-syntax-w">    </span><span class="devsite-syntax-p">}</span>
<span class="devsite-syntax-w">  </span><span class="devsite-syntax-p">}</span>
<span class="devsite-syntax-p">}</span></code></pre></devsite-code>
</div>



























  
  
</section>


  
  
  
  
  
  
  
  
  
  



<p>The query returns the top 10 most viewed Stack Overflow pages and
their view counts.</p>
</li>
<li>
<p>Right-click <strong>SimpleApp.java</strong> and click <strong>Run Java</strong>. If you are
prompted to authorize Cloud Shell and agree to the terms, click
<strong>Authorize</strong>.</p>

<p>The result is similar to the following:</p>

<devsite-code><pre class="console">https://stackoverflow.com/questions/35159967 : 170023 views
https://stackoverflow.com/questions/22879669 : 142581 views
https://stackoverflow.com/questions/10604135 : 132406 views
https://stackoverflow.com/questions/44564887 : 128781 views
https://stackoverflow.com/questions/27060396 : 127008 views
https://stackoverflow.com/questions/12482637 : 120766 views
https://stackoverflow.com/questions/20673986 : 115720 views
https://stackoverflow.com/questions/39109817 : 108368 views
https://stackoverflow.com/questions/11057219 : 105175 views
https://stackoverflow.com/questions/43195143 : 101878 views
</pre></devsite-code>
</li>
</ol>

<p>You have successfully queried a public dataset with the
BigQuery Java client library.</p></section>
<section><h3 id="node.js_1"> Node.js </h3>
<ol>
<li>
<p>In Cloud Shell, create a new Node.js project and file:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate">mkdir<span class="devsite-syntax-w"> </span>bigquery-node-quickstart<span class="devsite-syntax-w"> </span><span class="devsite-syntax-se">\</span>
<span class="devsite-syntax-w">    </span><span class="devsite-syntax-o">&amp;&amp;</span><span class="devsite-syntax-w"> </span>touch<span class="devsite-syntax-w"> </span><span class="devsite-syntax-se">\</span>
<span class="devsite-syntax-w">    </span>bigquery-node-quickstart/app.js</pre></devsite-code>

<p>This command creates a Node.js project that's named
<code>bigquery-node-quickstart</code> and a file that's named <code>app.js</code>.</p>
</li>
<li>
<p>Open the Cloud Shell Editor:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate">cloudshell<span class="devsite-syntax-w"> </span>workspace<span class="devsite-syntax-w"> </span>bigquery-node-quickstart</pre></devsite-code>
</li>
<li><p>To open a terminal in the Cloud Shell Editor, click
<strong>Open Terminal</strong>.</p></li>
<li>
<p>Open your project directory:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate"><span class="devsite-syntax-nb">cd</span><span class="devsite-syntax-w"> </span>bigquery-node-quickstart</pre></devsite-code>
</li>
<li>
<p>Install the BigQuery client library for Node.js:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate">npm<span class="devsite-syntax-w"> </span>install<span class="devsite-syntax-w"> </span>@google-cloud/bigquery</pre></devsite-code>

<p>The output is similar to the following:</p>

<devsite-code><pre class="console">added 63 packages in 2s
</pre></devsite-code>
</li>
<li><p>Click <strong>Open Editor</strong>.</p></li>
<li><p>In the <strong>Explorer</strong> pane, locate your <code>BIGQUERY-NODE-QUICKSTART</code>
project.</p></li>
<li><p>Click the <code>app.js</code> file to open it.</p></li>
<li>
<p>To create a query against the
<code>bigquery-public-data.stackoverflow</code> dataset that returns the
top 10 most viewed Stack Overflow pages and their view counts, copy the
following code into the <code>app.js</code> file:</p>

<section>
  
  
  
  
  






  
  














  



<div class="github-docwidget-gitinclude-code">

  
    
  
  











  









  




  



  


  <devsite-code><pre class="devsite-click-to-copy"><code><span class="devsite-syntax-c1">// Import the Google Cloud client library</span>
<span class="devsite-syntax-kd">const</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-p">{</span><span class="devsite-syntax-nx">BigQuery</span><span class="devsite-syntax-p">}</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">=</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">require</span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-s1">'<a class="devsite-xref-link" href="https://docs.cloud.google.com/nodejs/docs/reference/bigquery/latest/overview.html">@google-cloud/bigquery</a>'</span><span class="devsite-syntax-p">);</span>

<span class="devsite-syntax-k">async</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-kd">function</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">queryStackOverflow</span><span class="devsite-syntax-p">()</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-p">{</span>
<span class="devsite-syntax-w">  </span><span class="devsite-syntax-c1">// Queries a public Stack Overflow dataset.</span>

<span class="devsite-syntax-w">  </span><span class="devsite-syntax-c1">// Create a client</span>
<span class="devsite-syntax-w">  </span><span class="devsite-syntax-kd">const</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">bigqueryClient</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">=</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-ow">new</span><span class="devsite-syntax-w"> </span><a class="devsite-xref-link" href="https://docs.cloud.google.com/nodejs/docs/reference/bigquery/latest/bigquery/bigquery.html"><span class="devsite-syntax-nx">BigQuery</span></a><span class="devsite-syntax-p">();</span>

<span class="devsite-syntax-w">  </span><span class="devsite-syntax-c1">// The SQL query to run</span>
<span class="devsite-syntax-w">  </span><span class="devsite-syntax-kd">const</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">sqlQuery</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">=</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-sb">`SELECT</span>
<span class="devsite-syntax-sb">    CONCAT(</span>
<span class="devsite-syntax-sb">      'https://stackoverflow.com/questions/',</span>
<span class="devsite-syntax-sb">      CAST(id as STRING)) as url,</span>
<span class="devsite-syntax-sb">    view_count</span>
<span class="devsite-syntax-sb">    FROM \`bigquery-public-data.stackoverflow.posts_questions\`</span>
<span class="devsite-syntax-sb">    WHERE tags like '%google-bigquery%'</span>
<span class="devsite-syntax-sb">    ORDER BY view_count DESC</span>
<span class="devsite-syntax-sb">    LIMIT 10`</span><span class="devsite-syntax-p">;</span>

<span class="devsite-syntax-w">  </span><span class="devsite-syntax-kd">const</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">options</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">=</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-p">{</span>
<span class="devsite-syntax-w">    </span><span class="devsite-syntax-nx">query</span><span class="devsite-syntax-o">:</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">sqlQuery</span><span class="devsite-syntax-p">,</span>
<span class="devsite-syntax-w">    </span><span class="devsite-syntax-c1">// Location must match that of the dataset(s) referenced in the query.</span>
<span class="devsite-syntax-w">    </span><span class="devsite-syntax-nx">location</span><span class="devsite-syntax-o">:</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-s1">'US'</span><span class="devsite-syntax-p">,</span>
<span class="devsite-syntax-w">  </span><span class="devsite-syntax-p">};</span>

<span class="devsite-syntax-w">  </span><span class="devsite-syntax-c1">// Run the query</span>
<span class="devsite-syntax-w">  </span><span class="devsite-syntax-kd">const</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-p">[</span><span class="devsite-syntax-nx">rows</span><span class="devsite-syntax-p">]</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">=</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-k">await</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">bigqueryClient</span><span class="devsite-syntax-p">.</span><span class="devsite-syntax-nx">query</span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-nx">options</span><span class="devsite-syntax-p">);</span>

<span class="devsite-syntax-w">  </span><span class="devsite-syntax-nx">console</span><span class="devsite-syntax-p">.</span><span class="devsite-syntax-nx">log</span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-s1">'Query Results:'</span><span class="devsite-syntax-p">);</span>
<span class="devsite-syntax-w">  </span><span class="devsite-syntax-nx">rows</span><span class="devsite-syntax-p">.</span><span class="devsite-syntax-nx">forEach</span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-nx">row</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">=</span>&gt;<span class="devsite-syntax-w"> </span><span class="devsite-syntax-p">{</span>
<span class="devsite-syntax-w">    </span><span class="devsite-syntax-kd">const</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">url</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">=</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">row</span><span class="devsite-syntax-p">[</span><span class="devsite-syntax-s1">'url'</span><span class="devsite-syntax-p">];</span>
<span class="devsite-syntax-w">    </span><span class="devsite-syntax-kd">const</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">viewCount</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">=</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nx">row</span><span class="devsite-syntax-p">[</span><span class="devsite-syntax-s1">'view_count'</span><span class="devsite-syntax-p">];</span>
<span class="devsite-syntax-w">    </span><span class="devsite-syntax-nx">console</span><span class="devsite-syntax-p">.</span><span class="devsite-syntax-nx">log</span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-sb">`url: </span><span class="devsite-syntax-si">${</span><span class="devsite-syntax-nx">url</span><span class="devsite-syntax-si">}</span><span class="devsite-syntax-sb">, </span><span class="devsite-syntax-si">${</span><span class="devsite-syntax-nx">viewCount</span><span class="devsite-syntax-si">}</span><span class="devsite-syntax-sb"> views`</span><span class="devsite-syntax-p">);</span>
<span class="devsite-syntax-w">  </span><span class="devsite-syntax-p">});</span>
<span class="devsite-syntax-p">}</span>
<span class="devsite-syntax-nx">queryStackOverflow</span><span class="devsite-syntax-p">();</span></code></pre></devsite-code>
</div>



























  
  
</section>


  
  
  
  
  
  
  
  
  
  



</li>
<li><p>Click <strong>Open Terminal</strong>.</p></li>
<li>
<p>In the terminal, run the <code>app.js</code> script. If you are prompted to
authorize Cloud Shell and agree to the terms, click
<strong>Authorize</strong>.</p>

<devsite-code><pre class="devsite-click-to-copy notranslate">node<span class="devsite-syntax-w"> </span>app.js</pre></devsite-code>

<p>The result is similar to the following:</p>

<devsite-code><pre class="console">Query Results:
url: https://stackoverflow.com/questions/35159967, 170023 views
url: https://stackoverflow.com/questions/22879669, 142581 views
url: https://stackoverflow.com/questions/10604135, 132406 views
url: https://stackoverflow.com/questions/44564887, 128781 views
url: https://stackoverflow.com/questions/27060396, 127008 views
url: https://stackoverflow.com/questions/12482637, 120766 views
url: https://stackoverflow.com/questions/20673986, 115720 views
url: https://stackoverflow.com/questions/39109817, 108368 views
url: https://stackoverflow.com/questions/11057219, 105175 views
url: https://stackoverflow.com/questions/43195143, 101878 views
</pre></devsite-code>
</li>
</ol>

<p>You have successfully queried a public dataset with the
BigQuery Node.js client library.</p></section>
<section><h3 id="php_1"> PHP </h3>
<ol>
<li>
<p>In Cloud Shell, create a new PHP project and file:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate">mkdir<span class="devsite-syntax-w"> </span>bigquery-php-quickstart<span class="devsite-syntax-w"> </span><span class="devsite-syntax-se">\</span>
<span class="devsite-syntax-w">    </span><span class="devsite-syntax-o">&amp;&amp;</span><span class="devsite-syntax-w"> </span>touch<span class="devsite-syntax-w"> </span><span class="devsite-syntax-se">\</span>
<span class="devsite-syntax-w">    </span>bigquery-php-quickstart/app.php</pre></devsite-code>

<p>This command creates a PHP project that's named
<code>bigquery-php-quickstart</code> and a file that's named <code>app.php</code>.</p>
</li>
<li>
<p>Open the Cloud Shell Editor:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate">cloudshell<span class="devsite-syntax-w"> </span>workspace<span class="devsite-syntax-w"> </span>bigquery-php-quickstart</pre></devsite-code>
</li>
<li><p>To open a terminal in the Cloud Shell Editor, click
<strong>Open Terminal</strong>.</p></li>
<li>
<p>Open your project directory:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate"><span class="devsite-syntax-nb">cd</span><span class="devsite-syntax-w"> </span>bigquery-php-quickstart</pre></devsite-code>
</li>
<li>
<p>Install the BigQuery client library for PHP:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate">composer<span class="devsite-syntax-w"> </span>require<span class="devsite-syntax-w"> </span>google/cloud-bigquery</pre></devsite-code>

<p>The output is similar to the following. Several lines are omitted to
simplify the output.</p>

<devsite-code><pre class="console">Running composer update google/cloud-bigquery
Loading composer repositories with package information
Updating dependencies
...
No security vulnerability advisories found
Using version ^1.24 for google/cloud-bigquery
</pre></devsite-code>
</li>
<li><p>Click <strong>Open Editor</strong>.</p></li>
<li><p>In the <strong>Explorer</strong> pane, locate your <code>BIGQUERY-PHP-QUICKSTART</code>
project.</p></li>
<li><p>Click the <code>app.php</code> file to open it.</p></li>
<li>
<p>To create a query against the
<code>bigquery-public-data.stackoverflow</code> dataset that returns the
top 10 most viewed Stack Overflow pages and their view counts, copy the
following code into the <code>app.php</code> file:</p>

<section>
  
  
  
  
  






  
  














  



<div class="github-docwidget-gitinclude-code">

  
    
  
  











  









  




  



  


  <devsite-code><pre class="devsite-click-to-copy"><code>&lt;<span class="devsite-syntax-x">?php</span>
<span class="devsite-syntax-x"># ...</span>

<span class="devsite-syntax-x">require __DIR__ . '/vendor/autoload.php';</span>

<span class="devsite-syntax-x">use Google\Cloud\BigQuery\BigQueryClient;</span>


<span class="devsite-syntax-x">$bigQuery = new BigQueryClient();</span>
<span class="devsite-syntax-x">$query = &lt;&lt;&lt;ENDSQL</span>
<span class="devsite-syntax-x">SELECT</span>
<span class="devsite-syntax-x">  CONCAT(</span>
<span class="devsite-syntax-x">    'https://stackoverflow.com/questions/',</span>
<span class="devsite-syntax-x">    CAST(id as STRING)) as url,</span>
<span class="devsite-syntax-x">  view_count</span>
<span class="devsite-syntax-x">FROM `bigquery-public-data.stackoverflow.posts_questions`</span>
<span class="devsite-syntax-x">WHERE tags like '%google-bigquery%'</span>
<span class="devsite-syntax-x">ORDER BY view_count DESC</span>
<span class="devsite-syntax-x">LIMIT 10;</span>
<span class="devsite-syntax-x">ENDSQL;</span>
<span class="devsite-syntax-x">$queryJobConfig = $bigQuery-&gt;query($query);</span>
<span class="devsite-syntax-x">$queryResults = $bigQuery-&gt;runQuery($queryJobConfig);</span>

<span class="devsite-syntax-x">if ($queryResults-&gt;isComplete()) {</span>
<span class="devsite-syntax-x">    $i = 0;</span>
<span class="devsite-syntax-x">    $rows = $queryResults-&gt;rows();</span>
<span class="devsite-syntax-x">    foreach ($rows as $row) {</span>
<span class="devsite-syntax-x">        printf('--- Row %s ---' . PHP_EOL, ++$i);</span>
<span class="devsite-syntax-x">        printf('url: %s, %s views' . PHP_EOL, $row['url'], $row['view_count']);</span>
<span class="devsite-syntax-x">    }</span>
<span class="devsite-syntax-x">    printf('Found %s row(s)' . PHP_EOL, $i);</span>
<span class="devsite-syntax-x">} else {</span>
<span class="devsite-syntax-x">    throw new Exception('The query failed to complete');</span>
<span class="devsite-syntax-x">}</span></code></pre></devsite-code>
</div>



























  
  
</section>


  
  
  
  
  
  
  
  
  
  



</li>
<li><p>Click <strong>Open Terminal</strong>.</p></li>
<li>
<p>In the terminal, run the <code>app.php</code> script. If you are prompted to
authorize Cloud Shell and agree to the terms, click
<strong>Authorize</strong>.</p>

<devsite-code><pre class="devsite-click-to-copy notranslate">php<span class="devsite-syntax-w"> </span>app.php</pre></devsite-code>

<p>The result is similar to the following:</p>

<devsite-code><pre class="console">--- Row 1 ---
url: https://stackoverflow.com/questions/35159967, 170023 views
--- Row 2 ---
url: https://stackoverflow.com/questions/22879669, 142581 views
--- Row 3 ---
url: https://stackoverflow.com/questions/10604135, 132406 views
--- Row 4 ---
url: https://stackoverflow.com/questions/44564887, 128781 views
--- Row 5 ---
url: https://stackoverflow.com/questions/27060396, 127008 views
--- Row 6 ---
url: https://stackoverflow.com/questions/12482637, 120766 views
--- Row 7 ---
url: https://stackoverflow.com/questions/20673986, 115720 views
--- Row 8 ---
url: https://stackoverflow.com/questions/39109817, 108368 views
--- Row 9 ---
url: https://stackoverflow.com/questions/11057219, 105175 views
--- Row 10 ---
url: https://stackoverflow.com/questions/43195143, 101878 views
Found 10 row(s)
</pre></devsite-code>
</li>
</ol>

<p>You have successfully queried a public dataset with the
BigQuery PHP client library.</p></section>
<section><h3 id="python_1"> Python </h3>
<ol>
<li>
<p>In Cloud Shell, create a new Python project and file:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate">mkdir<span class="devsite-syntax-w"> </span>bigquery-python-quickstart<span class="devsite-syntax-w"> </span><span class="devsite-syntax-se">\</span>
<span class="devsite-syntax-w">    </span><span class="devsite-syntax-o">&amp;&amp;</span><span class="devsite-syntax-w"> </span>touch<span class="devsite-syntax-w"> </span><span class="devsite-syntax-se">\</span>
<span class="devsite-syntax-w">    </span>bigquery-python-quickstart/app.py</pre></devsite-code>

<p>This command creates a Python project that's named
<code>bigquery-python-quickstart</code> and a file that's named <code>app.py</code>.</p>
</li>
<li>
<p>Open the Cloud Shell Editor:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate">cloudshell<span class="devsite-syntax-w"> </span>workspace<span class="devsite-syntax-w"> </span>bigquery-python-quickstart</pre></devsite-code>
</li>
<li><p>To open a terminal in the Cloud Shell Editor, click
<strong>Open Terminal</strong>.</p></li>
<li>
<p>Open your project directory:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate"><span class="devsite-syntax-nb">cd</span><span class="devsite-syntax-w"> </span>bigquery-python-quickstart</pre></devsite-code>
</li>
<li>
<p>Install the BigQuery client library for Python:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate">pip<span class="devsite-syntax-w"> </span>install<span class="devsite-syntax-w"> </span>--upgrade<span class="devsite-syntax-w"> </span>google-cloud-bigquery</pre></devsite-code>

<p>The output is similar to the following. Several lines are omitted to
simplify the output.</p>

<devsite-code><pre class="console">Installing collected packages: google-cloud-bigquery
...
Successfully installed google-cloud-bigquery-3.9.0
...
</pre></devsite-code>
</li>
<li><p>Click <strong>Open Editor</strong>.</p></li>
<li><p>In the <strong>Explorer</strong> pane, locate your <code>BIGQUERY-PYTHON-QUICKSTART</code>
project.</p></li>
<li><p>Click the <code>app.py</code> file to open it.</p></li>
<li>
<p>To create a query against the
<code>bigquery-public-data.stackoverflow</code> dataset that returns the
top 10 most viewed Stack Overflow pages and their view counts, copy the
following code into the <code>app.py</code> file:</p>

<section>
  
  
  
  
  






  
  














  



<div class="github-docwidget-gitinclude-code">

  
    
  
  











  









  




  



  


  <devsite-code><pre class="devsite-click-to-copy"><code><span class="devsite-syntax-kn">from</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nn">google.cloud</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-kn">import</span> <a class="devsite-xref-link" href="https://docs.cloud.google.com/python/docs/reference/bigquery/latest"><span class="devsite-syntax-n">bigquery</span></a>



<span class="devsite-syntax-k">def</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-nf">query_stackoverflow</span><span class="devsite-syntax-p">()</span> <span class="devsite-syntax-o">-</span>&gt; <span class="devsite-syntax-kc">None</span><span class="devsite-syntax-p">:</span>
    <span class="devsite-syntax-n">client</span> <span class="devsite-syntax-o">=</span> <a class="devsite-xref-link" href="https://docs.cloud.google.com/python/docs/reference/bigquery/latest"><span class="devsite-syntax-n">bigquery</span></a><span class="devsite-syntax-o">.</span><a class="devsite-xref-link" href="https://docs.cloud.google.com/python/docs/reference/bigquery/latest/google.cloud.bigquery.client.Client.html"><span class="devsite-syntax-n">Client</span></a><span class="devsite-syntax-p">()</span>
    <span class="devsite-syntax-n">results</span> <span class="devsite-syntax-o">=</span> <span class="devsite-syntax-n">client</span><span class="devsite-syntax-o">.</span><a class="devsite-xref-link" href="https://docs.cloud.google.com/python/docs/reference/bigquery/latest/google.cloud.bigquery.client.Client.html#google_cloud_bigquery_client_Client_query_and_wait"><span class="devsite-syntax-n">query_and_wait</span></a><span class="devsite-syntax-p">(</span>
<span class="devsite-syntax-w">        </span><span class="devsite-syntax-sd">"""</span>
<span class="devsite-syntax-sd">        SELECT</span>
<span class="devsite-syntax-sd">          CONCAT(</span>
<span class="devsite-syntax-sd">            'https://stackoverflow.com/questions/',</span>
<span class="devsite-syntax-sd">            CAST(id as STRING)) as url,</span>
<span class="devsite-syntax-sd">          view_count</span>
<span class="devsite-syntax-sd">        FROM `bigquery-public-data.stackoverflow.posts_questions`</span>
<span class="devsite-syntax-sd">        WHERE tags like '%google-bigquery%'</span>
<span class="devsite-syntax-sd">        ORDER BY view_count DESC</span>
<span class="devsite-syntax-sd">        LIMIT 10"""</span>
    <span class="devsite-syntax-p">)</span>  <span class="devsite-syntax-c1"># Waits for job to complete.</span>

    <span class="devsite-syntax-k">for</span> <span class="devsite-syntax-n">row</span> <span class="devsite-syntax-ow">in</span> <span class="devsite-syntax-n">results</span><span class="devsite-syntax-p">:</span>
        <span class="devsite-syntax-nb">print</span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-s2">"</span><span class="devsite-syntax-si">{}</span><span class="devsite-syntax-s2"> : </span><span class="devsite-syntax-si">{}</span><span class="devsite-syntax-s2"> views"</span><span class="devsite-syntax-o">.</span><span class="devsite-syntax-n">format</span><span class="devsite-syntax-p">(</span><span class="devsite-syntax-n">row</span><span class="devsite-syntax-o">.</span><span class="devsite-syntax-n">url</span><span class="devsite-syntax-p">,</span> <span class="devsite-syntax-n">row</span><span class="devsite-syntax-o">.</span><span class="devsite-syntax-n">view_count</span><span class="devsite-syntax-p">))</span>


<span class="devsite-syntax-k">if</span> <span class="devsite-syntax-vm">__name__</span> <span class="devsite-syntax-o">==</span> <span class="devsite-syntax-s2">"__main__"</span><span class="devsite-syntax-p">:</span>
    <span class="devsite-syntax-n">query_stackoverflow</span><span class="devsite-syntax-p">()</span></code></pre></devsite-code>
</div>



























  
  
</section>


  
  
  
  
  
  
  
  
  
  



</li>
<li><p>Click <strong>Open Terminal</strong>.</p></li>
<li>
<p>In the terminal, run the <code>app.py</code> script. If you are prompted to
authorize Cloud Shell and agree to the terms, click
<strong>Authorize</strong>.</p>

<devsite-code><pre class="devsite-click-to-copy notranslate">python<span class="devsite-syntax-w"> </span>app.py</pre></devsite-code>

<p>The result is similar to the following:</p>

<devsite-code><pre class="console">https://stackoverflow.com/questions/35159967 : 170023 views
https://stackoverflow.com/questions/22879669 : 142581 views
https://stackoverflow.com/questions/10604135 : 132406 views
https://stackoverflow.com/questions/44564887 : 128781 views
https://stackoverflow.com/questions/27060396 : 127008 views
https://stackoverflow.com/questions/12482637 : 120766 views
https://stackoverflow.com/questions/20673986 : 115720 views
https://stackoverflow.com/questions/39109817 : 108368 views
https://stackoverflow.com/questions/11057219 : 105175 views
https://stackoverflow.com/questions/43195143 : 101878 views
</pre></devsite-code>
</li>
</ol>

<p>You have successfully queried a public dataset with the
BigQuery Python client library.</p></section>
<section><h3 id="ruby_1"> Ruby </h3>
<ol>
<li>
<p>In Cloud Shell, create a new Ruby project and file:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate">mkdir<span class="devsite-syntax-w"> </span>bigquery-ruby-quickstart<span class="devsite-syntax-w"> </span><span class="devsite-syntax-se">\</span>
<span class="devsite-syntax-w">    </span><span class="devsite-syntax-o">&amp;&amp;</span><span class="devsite-syntax-w"> </span>touch<span class="devsite-syntax-w"> </span><span class="devsite-syntax-se">\</span>
<span class="devsite-syntax-w">    </span>bigquery-ruby-quickstart/app.rb</pre></devsite-code>

<p>This command creates a Ruby project that's named
<code>bigquery-ruby-quickstart</code> and a file that's named <code>app.rb</code>.</p>
</li>
<li>
<p>Open the Cloud Shell Editor:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate">cloudshell<span class="devsite-syntax-w"> </span>workspace<span class="devsite-syntax-w"> </span>bigquery-ruby-quickstart</pre></devsite-code>
</li>
<li><p>To open a terminal in the Cloud Shell Editor, click
<strong>Open Terminal</strong>.</p></li>
<li>
<p>Open your project directory:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate"><span class="devsite-syntax-nb">cd</span><span class="devsite-syntax-w"> </span>bigquery-ruby-quickstart</pre></devsite-code>
</li>
<li>
<p>Install the BigQuery client library for Ruby:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate">gem<span class="devsite-syntax-w"> </span>install<span class="devsite-syntax-w"> </span>google-cloud-bigquery</pre></devsite-code>

<p>The output is similar to the following. Several lines are omitted to
simplify the output.</p>

<devsite-code><pre class="console">23 gems installed
</pre></devsite-code>
</li>
<li><p>Click <strong>Open Editor</strong>.</p></li>
<li><p>In the <strong>Explorer</strong> pane, locate your <code>BIGQUERY-RUBY-QUICKSTART</code>
project.</p></li>
<li><p>Click the <code>app.rb</code> file to open it.</p></li>
<li>
<p>To create a query against the
<code>bigquery-public-data.stackoverflow</code> dataset that returns the
top 10 most viewed Stack Overflow pages and their view counts, copy the
following code into the <code>app.rb</code> file:</p>

<section>
  
  
  
  
  






  
  














  



<div class="github-docwidget-gitinclude-code">

  
    
  
  











  









  




  



  


  <devsite-code><pre class="devsite-click-to-copy"><code><span class="devsite-syntax-nb">require</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-s2">"google/cloud/bigquery"</span>

<span class="devsite-syntax-c1"># This uses Application Default Credentials to authenticate.</span>
<span class="devsite-syntax-c1"># @see https://cloud.google.com/bigquery/docs/authentication/getting-started</span>
<span class="devsite-syntax-n">bigquery</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">=</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-no">Google</span><span class="devsite-syntax-o">::</span><span class="devsite-syntax-no">Cloud</span><span class="devsite-syntax-o">::</span><a class="devsite-xref-link" href="https://docs.cloud.google.com/ruby/docs/reference/google-cloud-bigquery-data_policies/latest/Google-Cloud-Bigquery.html"><span class="devsite-syntax-no">Bigquery</span></a><span class="devsite-syntax-o">.</span><a class="devsite-xref-link" href="https://docs.cloud.google.com/ruby/docs/reference/google-cloud-bigquery/latest/Google-Cloud-Bigquery.html"><span class="devsite-syntax-n">new</span></a>

<span class="devsite-syntax-n">sql</span><span class="devsite-syntax-w">     </span><span class="devsite-syntax-o">=</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-s2">"SELECT "</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-p">\</span>
<span class="devsite-syntax-w">          </span><span class="devsite-syntax-s2">"CONCAT('https://stackoverflow.com/questions/', CAST(id as STRING)) as url, view_count "</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-p">\</span>
<span class="devsite-syntax-w">          </span><span class="devsite-syntax-s2">"FROM `bigquery-public-data.stackoverflow.posts_questions` "</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-p">\</span>
<span class="devsite-syntax-w">          </span><span class="devsite-syntax-s2">"WHERE tags like '%google-bigquery%' "</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-p">\</span>
<span class="devsite-syntax-w">          </span><span class="devsite-syntax-s2">"ORDER BY view_count DESC LIMIT 10"</span>
<span class="devsite-syntax-n">results</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">=</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-n">bigquery</span><span class="devsite-syntax-o">.</span><span class="devsite-syntax-n">query</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-n">sql</span>

<span class="devsite-syntax-n">results</span><span class="devsite-syntax-o">.</span><span class="devsite-syntax-n">each</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-k">do</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-o">|</span><span class="devsite-syntax-n">row</span><span class="devsite-syntax-o">|</span>
<span class="devsite-syntax-w">  </span><span class="devsite-syntax-nb">puts</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-s2">"</span><span class="devsite-syntax-si">#{</span><a class="devsite-xref-link" href="https://docs.cloud.google.com/ruby/docs/reference/google-cloud-bigquery/latest/Google-Cloud-Bigquery-InsertResponse-InsertError.html"><span class="devsite-syntax-n">row</span></a><span class="devsite-syntax-o">[</span><span class="devsite-syntax-ss">:url</span><span class="devsite-syntax-o">]</span><span class="devsite-syntax-si">}</span><span class="devsite-syntax-s2">: </span><span class="devsite-syntax-si">#{</span><a class="devsite-xref-link" href="https://docs.cloud.google.com/ruby/docs/reference/google-cloud-bigquery/latest/Google-Cloud-Bigquery-InsertResponse-InsertError.html"><span class="devsite-syntax-n">row</span></a><span class="devsite-syntax-o">[</span><span class="devsite-syntax-ss">:view_count</span><span class="devsite-syntax-o">]</span><span class="devsite-syntax-si">}</span><span class="devsite-syntax-s2"> views"</span>
<span class="devsite-syntax-k">end</span></code></pre></devsite-code>
</div>



























  
  
</section>


  
  
  
  
  
  
  
  
  
  



</li>
<li><p>Click <strong>Open Terminal</strong>.</p></li>
<li>
<p>In the terminal, run the <code>app.rb</code> script. If you are prompted to
authorize Cloud Shell and agree to the terms, click
<strong>Authorize</strong>.</p>

<devsite-code><pre class="devsite-click-to-copy notranslate">ruby<span class="devsite-syntax-w"> </span>app.rb</pre></devsite-code>

<p>The result is similar to the following:</p>

<devsite-code><pre class="console">https://stackoverflow.com/questions/35159967: 170023 views
https://stackoverflow.com/questions/22879669: 142581 views
https://stackoverflow.com/questions/10604135: 132406 views
https://stackoverflow.com/questions/44564887: 128781 views
https://stackoverflow.com/questions/27060396: 127008 views
https://stackoverflow.com/questions/12482637: 120766 views
https://stackoverflow.com/questions/20673986: 115720 views
https://stackoverflow.com/questions/39109817: 108368 views
https://stackoverflow.com/questions/11057219: 105175 views
https://stackoverflow.com/questions/43195143: 101878 views
</pre></devsite-code>
</li>
</ol>

<p>You have successfully queried a public dataset with the
BigQuery Ruby client library.</p></section>
</div>
<h2 id="clean_up">Clean up</h2>

<p>To avoid incurring charges to your Google Cloud account, either delete
your Google Cloud project, or delete the resources that you created in
this walkthrough.</p>

<h3 id="delete_the_project">Delete the project</h3>


























<p>
  The easiest way to eliminate billing is to delete the project that you
  created for the tutorial.
</p>

<p>To delete the project:
  </p>
<ol>












 <aside class="caution">
  <strong>Caution</strong>: Deleting a project has the following effects:
  <ul>
    <li>
      <strong>Everything in the project is deleted.</strong> If you used an existing project for
      the tasks in this document, when you delete it, you also delete any other work you've
      done in the project.
    </li>
    <li>
      <strong>Custom project IDs are lost.</strong>
      When you created this project, you might have created a custom project ID that you want to use in
      the future. To preserve the URLs that use the project ID, such as an <code>appspot.com</code>
      URL, delete selected resources inside the project instead of deleting the whole project.
    </li>
  </ul>
  
  <p>
    If you plan to explore multiple architectures, tutorials, or quickstarts, reusing projects
    can help you avoid exceeding project quota limits.
  </p>
  
</aside>






  
  <li>
    In the Google Cloud console, go to the <b>Manage resources</b> page.
    <p><a href="https://console.cloud.google.com/iam-admin/projects" class="button button-primary">Go to Manage resources</a></p>
  </li>
  
  <li>
    In the project list, select the project that you
    want to delete, and then click <b>Delete</b>.
  </li>
  <li>
    In the dialog, type the project ID, and then click
    <b>Shut down</b> to delete the project.
  </li>




  </ol>
<h3 id="delete_the_resources">Delete the resources</h3>

<p>If you used an existing project, delete the resources that you created:</p>
<div class="ds-selector-tabs">
<section><h3 id="c_2"> C# </h3>
<ol>
<li>
<p>In Cloud Shell, move up a directory:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate"><span class="devsite-syntax-nb">cd</span><span class="devsite-syntax-w"> </span>..</pre></devsite-code>
</li>
<li>
<p>Delete the <code>BigQueryCsharpDemo</code> folder that you created:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate">rm<span class="devsite-syntax-w"> </span>-R<span class="devsite-syntax-w"> </span>BigQueryCsharpDemo</pre></devsite-code>

<p>The <code>-R</code> flag deletes all assets in a folder.</p>
</li>
</ol></section>
<section><h3 id="go_2"> Go </h3>
<ol>
<li>
<p>In Cloud Shell, move up a directory:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate"><span class="devsite-syntax-nb">cd</span><span class="devsite-syntax-w"> </span>..</pre></devsite-code>
</li>
<li>
<p>Delete the <code>bigquery-go-quickstart</code> folder that you created:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate">rm<span class="devsite-syntax-w"> </span>-R<span class="devsite-syntax-w"> </span>bigquery-go-quickstart</pre></devsite-code>

<p>The <code>-R</code> flag deletes all assets in a folder.</p>
</li>
</ol></section>
<section><h3 id="java_2"> Java </h3>
<ol>
<li>
<p>In Cloud Shell, move up a directory:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate"><span class="devsite-syntax-nb">cd</span><span class="devsite-syntax-w"> </span>..</pre></devsite-code>
</li>
<li>
<p>Delete the <code>bigquery-java-quickstart</code> folder that you created:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate">rm<span class="devsite-syntax-w"> </span>-R<span class="devsite-syntax-w"> </span>bigquery-java-quickstart</pre></devsite-code>

<p>The <code>-R</code> flag deletes all assets in a folder.</p>
</li>
</ol></section>
<section><h3 id="node.js_2"> Node.js </h3>
<ol>
<li>
<p>In Cloud Shell, move up a directory:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate"><span class="devsite-syntax-nb">cd</span><span class="devsite-syntax-w"> </span>..</pre></devsite-code>
</li>
<li>
<p>Delete the <code>bigquery-node-quickstart</code> folder that you created:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate">rm<span class="devsite-syntax-w"> </span>-R<span class="devsite-syntax-w"> </span>bigquery-node-quickstart</pre></devsite-code>

<p>The <code>-R</code> flag deletes all assets in a folder.</p>
</li>
</ol></section>
<section><h3 id="php_2"> PHP </h3>
<ol>
<li>
<p>In Cloud Shell, move up a directory:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate"><span class="devsite-syntax-nb">cd</span><span class="devsite-syntax-w"> </span>..</pre></devsite-code>
</li>
<li>
<p>Delete the <code>bigquery-php-quickstart</code> folder that you created:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate">rm<span class="devsite-syntax-w"> </span>-R<span class="devsite-syntax-w"> </span>bigquery-php-quickstart</pre></devsite-code>

<p>The <code>-R</code> flag deletes all assets in a folder.</p>
</li>
</ol></section>
<section><h3 id="python_2"> Python </h3>
<ol>
<li>
<p>In Cloud Shell, move up a directory:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate"><span class="devsite-syntax-nb">cd</span><span class="devsite-syntax-w"> </span>..</pre></devsite-code>
</li>
<li>
<p>Delete the <code>bigquery-python-quickstart</code> folder that you created:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate">rm<span class="devsite-syntax-w"> </span>-R<span class="devsite-syntax-w"> </span>bigquery-python-quickstart</pre></devsite-code>

<p>The <code>-R</code> flag deletes all assets in a folder.</p>
</li>
</ol></section>
<section><h3 id="ruby_2"> Ruby </h3>
<ol>
<li>
<p>In Cloud Shell, move up a directory:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate"><span class="devsite-syntax-nb">cd</span><span class="devsite-syntax-w"> </span>..</pre></devsite-code>
</li>
<li>
<p>Delete the <code>bigquery-ruby-quickstart</code> folder that you created:</p>

<devsite-code><pre class="devsite-click-to-copy notranslate">rm<span class="devsite-syntax-w"> </span>-R<span class="devsite-syntax-w"> </span>bigquery-ruby-quickstart</pre></devsite-code>

<p>The <code>-R</code> flag deletes all assets in a folder.</p>
</li>
</ol></section>
</div>

  </section>

  

  <section class="whatsnext">
    <h2 id="whats-next">What's next</h2>
    

<ul>
<li>Learn more about using the
<a href="/bigquery/docs/reference/libraries">BigQuery client libraries</a>.</li>
<li>Learn more about
<a href="/bigquery/public-data">BigQuery public datasets</a>.</li>
<li>Learn how to
<a href="/bigquery/docs/loading-data">load data into BigQuery</a>.</li>
<li>Learn more about
<a href="/bigquery/docs/query-overview">querying data in BigQuery</a>.</li>
<li>Get <a href="/bigquery/docs/release-notes">updates about BigQuery</a>.</li>
<li>Learn about <a href="https://cloud.google.com/bigquery/pricing">BigQuery pricing</a>.</li>
<li>Learn about <a href="/bigquery/quotas">BigQuery quotas and limits</a>.</li>
</ul>


  </section>

  </div>
  
  

  
    </div>

  
    
    
      
    <devsite-feedback class="nocontent">

  <button>
  
    
    Send feedback
  
  </button>
</devsite-feedback>
       
    
    
  

  </article>


<devsite-content-footer class="nocontent">
  <p>Except as otherwise noted, the content of this page is licensed under the <a href="https://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 License</a>, and code samples are licensed under the <a href="https://www.apache.org/licenses/LICENSE-2.0">Apache 2.0 License</a>. For details, see the <a href="https://developers.google.com/site-policies">Google Developers Site Policies</a>. Java is a registered trademark of Oracle and/or its affiliates.</p>
  <p>Last updated 2026-04-02 UTC.</p>
</devsite-content-footer>


<div class="devsite-content-data">
  
    
    
    <template class="devsite-thumb-rating-feedback">
      <devsite-feedback class="nocontent">

  <button>
  
    Need to tell us more?
  
  </button>
</devsite-feedback>
    </template>
  
  
    <template class="devsite-content-data-template">
      [[["Easy to understand","easyToUnderstand","thumb-up"],["Solved my problem","solvedMyProblem","thumb-up"],["Other","otherUp","thumb-up"]],[["Hard to understand","hardToUnderstand","thumb-down"],["Incorrect information or sample code","incorrectInformationOrSampleCode","thumb-down"],["Missing the information/samples I need","missingTheInformationSamplesINeed","thumb-down"],["Other","otherDown","thumb-down"]],["Last updated 2026-04-02 UTC."],[],[]]
    </template>
  
</div>
            
          </devsite-content>
        </main>
        <devsite-footer-linkboxes class="devsite-footer">
          
            
<nav class="devsite-footer-linkboxes nocontent">
  
  <ul class="devsite-footer-linkboxes-list">
    
    <li class="devsite-footer-linkbox ">
    <h3 class="devsite-footer-linkbox-heading no-link">Products and pricing</h3>
      <ul class="devsite-footer-linkbox-list">
        
        <li class="devsite-footer-linkbox-item">
          
          <a href="//cloud.google.com/products/" class="devsite-footer-linkbox-link gc-analytics-event">
            
          
            See all products
          
          </a>
          
          
        </li>
        
        <li class="devsite-footer-linkbox-item">
          
          <a href="//cloud.google.com/pricing/" class="devsite-footer-linkbox-link gc-analytics-event">
            
          
            Google Cloud pricing
          
          </a>
          
          
        </li>
        
        <li class="devsite-footer-linkbox-item">
          
          <a href="//cloud.google.com/marketplace/" class="devsite-footer-linkbox-link gc-analytics-event">
            
          
            Google Cloud Marketplace
          
          </a>
          
          
        </li>
        
        <li class="devsite-footer-linkbox-item">
          
          <a href="//cloud.google.com/contact/" class="devsite-footer-linkbox-link gc-analytics-event">
            
              
              
            
          
            Contact sales
          
          </a>
          
          
        </li>
        
      </ul>
    </li>
    
    <li class="devsite-footer-linkbox ">
    <h3 class="devsite-footer-linkbox-heading no-link">Support</h3>
      <ul class="devsite-footer-linkbox-list">
        
        <li class="devsite-footer-linkbox-item">
          
          <a href="//discuss.google.dev/c/google-cloud/14/" class="devsite-footer-linkbox-link gc-analytics-event">
            
          
            Community forums
          
          </a>
          
          
        </li>
        
        <li class="devsite-footer-linkbox-item">
          
          <a href="//cloud.google.com/support-hub/" class="devsite-footer-linkbox-link gc-analytics-event">
            
          
            Support
          
          </a>
          
          
        </li>
        
        <li class="devsite-footer-linkbox-item">
          
          <a href="//docs.cloud.google.com/release-notes" class="devsite-footer-linkbox-link gc-analytics-event">
            
          
            Release Notes
          
          </a>
          
          
        </li>
        
        <li class="devsite-footer-linkbox-item">
          
          <a href="//status.cloud.google.com" class="devsite-footer-linkbox-link gc-analytics-event">
            
              
              
            
          
            System status
          
          </a>
          
          
        </li>
        
      </ul>
    </li>
    
    <li class="devsite-footer-linkbox ">
    <h3 class="devsite-footer-linkbox-heading no-link">Resources</h3>
      <ul class="devsite-footer-linkbox-list">
        
        <li class="devsite-footer-linkbox-item">
          
          <a href="//github.com/googlecloudPlatform/" class="devsite-footer-linkbox-link gc-analytics-event">
            
          
            GitHub
          
          </a>
          
          
        </li>
        
        <li class="devsite-footer-linkbox-item">
          
          <a href="/docs/get-started/" class="devsite-footer-linkbox-link gc-analytics-event">
            
          
            Getting Started with Google Cloud
          
          </a>
          
          
        </li>
        
        <li class="devsite-footer-linkbox-item">
          
          <a href="/docs/samples" class="devsite-footer-linkbox-link gc-analytics-event">
            
          
            Code samples
          
          </a>
          
          
        </li>
        
        <li class="devsite-footer-linkbox-item">
          
          <a href="/architecture/" class="devsite-footer-linkbox-link gc-analytics-event">
            
          
            Cloud Architecture Center
          
          </a>
          
          
        </li>
        
        <li class="devsite-footer-linkbox-item">
          
          <a href="//cloud.google.com/learn/training/" class="devsite-footer-linkbox-link gc-analytics-event">
            
              
              
            
          
            Training and Certification
          
          </a>
          
          
        </li>
        
      </ul>
    </li>
    
    <li class="devsite-footer-linkbox ">
    <h3 class="devsite-footer-linkbox-heading no-link">Engage</h3>
      <ul class="devsite-footer-linkbox-list">
        
        <li class="devsite-footer-linkbox-item">
          
          <a href="//cloud.google.com/blog/" class="devsite-footer-linkbox-link gc-analytics-event">
            
          
            Blog
          
          </a>
          
          
        </li>
        
        <li class="devsite-footer-linkbox-item">
          
          <a href="//cloud.google.com/events/" class="devsite-footer-linkbox-link gc-analytics-event">
            
          
            Events
          
          </a>
          
          
        </li>
        
        <li class="devsite-footer-linkbox-item">
          
          <a href="//x.com/googlecloud" class="devsite-footer-linkbox-link gc-analytics-event">
            
          
            X (Twitter)
          
          </a>
          
          
        </li>
        
        <li class="devsite-footer-linkbox-item">
          
          <a href="//www.youtube.com/googlecloud" class="devsite-footer-linkbox-link gc-analytics-event">
            
          
            Google Cloud on YouTube
          
          </a>
          
          
        </li>
        
        <li class="devsite-footer-linkbox-item">
          
          <a href="//www.youtube.com/googlecloudplatform" class="devsite-footer-linkbox-link gc-analytics-event">
            
              
              
            
          
            Google Cloud Tech on YouTube
          
          </a>
          
          
        </li>
        
      </ul>
    </li>
    
  </ul>
  
</nav>
          
        </devsite-footer-linkboxes>
        <devsite-footer-utility class="devsite-footer">
          
            

<div class="devsite-footer-utility nocontent">
  

  
  <nav class="devsite-footer-utility-links">
    
    <ul class="devsite-footer-utility-list">
      
      <li class="devsite-footer-utility-item
                 ">
        
        
        <a class="devsite-footer-utility-link gc-analytics-event" href="//about.google/">
          About Google
        </a>
        
      </li>
      
      <li class="devsite-footer-utility-item
                 devsite-footer-privacy-link">
        
        
        <a class="devsite-footer-utility-link gc-analytics-event" href="//policies.google.com/privacy">
          Privacy
        </a>
        
      </li>
      
      <li class="devsite-footer-utility-item
                 ">
        
        
        <a class="devsite-footer-utility-link gc-analytics-event" href="//policies.google.com/terms?hl=en">
          Site terms
        </a>
        
      </li>
      
      <li class="devsite-footer-utility-item
                 ">
        
        
        <a class="devsite-footer-utility-link gc-analytics-event" href="//cloud.google.com/product-terms">
          Google Cloud terms
        </a>
        
      </li>
      
      <li class="devsite-footer-utility-item
                 glue-cookie-notification-bar-control">
        
        
        <a class="devsite-footer-utility-link gc-analytics-event" href="#">
          Manage cookies
        </a>
        
      </li>
      
      <li class="devsite-footer-utility-item
                 devsite-footer-carbon-button">
        
        
        <a class="devsite-footer-utility-link gc-analytics-event" href="//cloud.google.com/sustainability">
          Our third decade of climate action: join us
        </a>
        
      </li>
      
      <li class="devsite-footer-utility-item
                 devsite-footer-utility-button">
        
        <span class="devsite-footer-utility-description">Sign up for the Google Cloud newsletter</span>
        
        
        <a class="devsite-footer-utility-link gc-analytics-event" href="//cloud.google.com/newsletter/">
          Subscribe
        </a>
        
      </li>
      
    </ul>
    
    
<devsite-language-selector>
  <ul>
    
    
    <li>
      <a>English</a>
    </li>
    
    <li>
      <a>Deutsch</a>
    </li>
    
    <li>
      <a>Español</a>
    </li>
    
    <li>
      <a>Español – América Latina</a>
    </li>
    
    <li>
      <a>Français</a>
    </li>
    
    <li>
      <a>Indonesia</a>
    </li>
    
    <li>
      <a>Italiano</a>
    </li>
    
    <li>
      <a>Português</a>
    </li>
    
    <li>
      <a>Português – Brasil</a>
    </li>
    
    <li>
      <a>עברית</a>
    </li>
    
    <li>
      <a>中文 – 简体</a>
    </li>
    
    <li>
      <a>中文 – 繁體</a>
    </li>
    
    <li>
      <a>日本語</a>
    </li>
    
    <li>
      <a>한국어</a>
    </li>
    
  </ul>
</devsite-language-selector>

  </nav>
</div>
          
        </devsite-footer-utility>
        </section></section>
    </body>
</html>
