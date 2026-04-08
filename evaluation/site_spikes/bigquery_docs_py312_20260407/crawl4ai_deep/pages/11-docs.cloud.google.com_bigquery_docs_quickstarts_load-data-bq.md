---
title: https://docs.cloud.google.com/bigquery/docs/quickstarts/load-data-bq
url: https://docs.cloud.google.com/bigquery/docs/quickstarts/load-data-bq
fetch_mode: crawl4ai
status_code: null
blocked_reason: null
---

<html>
<head>
    <title>Use the bq tool  |  BigQuery  |  Google Cloud Documentation</title>


  </head>
  <body class="color-scheme--light viewport--desktop tenant--clouddocs">
  
    <a href="#main-content" class="skip-link button">
      
      Skip to main content
    </a>
    <section class="devsite-wrapper">
      <devsite-cookie-notification-bar><!----></devsite-cookie-notification-bar><devsite-header>
  
    





















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
        
      
    <tab class="devsite-overflow-tab"><!---->
          <button class="devsite-tabs-overflow-button devsite-icon devsite-icon-arrow-drop-down" id="tab-overflow-button-LViz"><!--?lit$970813483$-->More</button>
          </tab></nav>

  <!----></devsite-tabs>

            
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
      <a href="https://docs.cloud.google.com/bigquery/docs/quickstarts/load-data-bq">English</a>
    </li>
    
    <li>
      <a href="https://docs.cloud.google.com/bigquery/docs/quickstarts/load-data-bq?hl=de">Deutsch</a>
    </li>
    
    <li>
      <a href="https://docs.cloud.google.com/bigquery/docs/quickstarts/load-data-bq?hl=es">Español</a>
    </li>
    
    <li>
      <a href="https://docs.cloud.google.com/bigquery/docs/quickstarts/load-data-bq?hl=es-419">Español – América Latina</a>
    </li>
    
    <li>
      <a href="https://docs.cloud.google.com/bigquery/docs/quickstarts/load-data-bq?hl=fr">Français</a>
    </li>
    
    <li>
      <a href="https://docs.cloud.google.com/bigquery/docs/quickstarts/load-data-bq?hl=id">Indonesia</a>
    </li>
    
    <li>
      <a href="https://docs.cloud.google.com/bigquery/docs/quickstarts/load-data-bq?hl=it">Italiano</a>
    </li>
    
    <li>
      <a href="https://docs.cloud.google.com/bigquery/docs/quickstarts/load-data-bq?hl=pt">Português</a>
    </li>
    
    <li>
      <a href="https://docs.cloud.google.com/bigquery/docs/quickstarts/load-data-bq?hl=pt-br">Português – Brasil</a>
    </li>
    
    <li>
      <a href="https://docs.cloud.google.com/bigquery/docs/quickstarts/load-data-bq?hl=zh-cn">中文 – 简体</a>
    </li>
    
    <li>
      <a href="https://docs.cloud.google.com/bigquery/docs/quickstarts/load-data-bq?hl=zh-tw">中文 – 繁體</a>
    </li>
    
    <li>
      <a href="https://docs.cloud.google.com/bigquery/docs/quickstarts/load-data-bq?hl=ja">日本語</a>
    </li>
    
    <li>
      <a href="https://docs.cloud.google.com/bigquery/docs/quickstarts/load-data-bq?hl=ko">한국어</a>
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
        
      
    <tab class="devsite-overflow-tab"><!---->
          <button class="devsite-tabs-overflow-button devsite-icon devsite-icon-arrow-drop-down" id="tab-overflow-button-5PQy"><!--?lit$970813483$-->More</button>
          </tab></nav>

  <!----></devsite-tabs>

          
          
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
              
  
  <a href="/docs" class="devsite-nav-title gc-analytics-event">
  
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
                      
  
  <a href="/bigquery/docs/introduction" class="devsite-nav-title gc-analytics-event">
  
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

  <li class="devsite-nav-item"><a href="/bigquery/docs/quickstarts/load-data-bq" class="devsite-nav-title devsite-nav-active"><span class="devsite-nav-text">Use the bq CLI tool</span></a></li>

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
        
      </devsite-book-nav><section id="gc-wrapper">
        <main id="main-content" class="devsite-main-content">
          <div class="devsite-sidebar">
            <div class="devsite-sidebar-content">
                
                <devsite-toc class="devsite-nav devsite-toc"><ul class="devsite-nav-list">
<li class="devsite-nav-item devsite-nav-heading devsite-toc-toggle"><span class="devsite-nav-title"><span class="devsite-nav-text">On this page</span></span></li>
<li class="devsite-nav-item">
<a href="#before-you-begin" class="devsite-nav-title gc-analytics-event"><span class="devsite-nav-text">Before you begin</span></a><ul class="devsite-nav-list"><li class="devsite-nav-item"><a href="#required_roles" class="devsite-nav-title gc-analytics-event"><span class="devsite-nav-text">Required roles</span></a></li></ul>
</li>
<li class="devsite-nav-item"><a href="#download_the_file_that_contains_the_source_data" class="devsite-nav-title gc-analytics-event"><span class="devsite-nav-text">Download the file that contains the source data</span></a></li>
<li class="devsite-nav-item"><a href="#create_a_dataset" class="devsite-nav-title gc-analytics-event"><span class="devsite-nav-text">Create a dataset</span></a></li>
<li class="devsite-nav-item"><a href="#load_data_into_a_table" class="devsite-nav-title gc-analytics-event"><span class="devsite-nav-text">Load data into a table</span></a></li>
<li class="devsite-nav-item"><a href="#query_table_data" class="devsite-nav-title gc-analytics-event"><span class="devsite-nav-text">Query table data</span></a></li>
<li class="devsite-nav-item">
<a href="#clean-up" class="devsite-nav-title gc-analytics-event"><span class="devsite-nav-text">Clean up</span></a><ul class="devsite-nav-list">
<li class="devsite-nav-item"><a href="#delete_the_project" class="devsite-nav-title gc-analytics-event"><span class="devsite-nav-text">Delete the project</span></a></li>
<li class="devsite-nav-item"><a href="#delete_the_resources" class="devsite-nav-title gc-analytics-event"><span class="devsite-nav-text">Delete the resources</span></a></li>
</ul>
</li>
<li class="devsite-nav-item"><a href="#whats-next" class="devsite-nav-title gc-analytics-event"><span class="devsite-nav-text">What's next</span></a></li>
</ul></devsite-toc>
                </div>
          </div>
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
  
  
    
  

  <devsite-toc class="devsite-nav devsite-toc-embedded"><ul class="devsite-nav-list">
<li class="devsite-nav-item devsite-nav-heading devsite-toc-toggle"><span class="devsite-nav-title"><span class="devsite-nav-text">On this page</span></span></li>
<li class="devsite-nav-item">
<a href="#before-you-begin" class="devsite-nav-title gc-analytics-event"><span class="devsite-nav-text">Before you begin</span></a><ul class="devsite-nav-list"><li class="devsite-nav-item"><a href="#required_roles" class="devsite-nav-title gc-analytics-event"><span class="devsite-nav-text">Required roles</span></a></li></ul>
</li>
<li class="devsite-nav-item"><a href="#download_the_file_that_contains_the_source_data" class="devsite-nav-title gc-analytics-event"><span class="devsite-nav-text">Download the file that contains the source data</span></a></li>
<li class="devsite-nav-item"><a href="#create_a_dataset" class="devsite-nav-title gc-analytics-event"><span class="devsite-nav-text">Create a dataset</span></a></li>
<li class="devsite-nav-item"><a href="#load_data_into_a_table" class="devsite-nav-title gc-analytics-event"><span class="devsite-nav-text">Load data into a table</span></a></li>
<li class="devsite-nav-item"><a href="#query_table_data" class="devsite-nav-title gc-analytics-event"><span class="devsite-nav-text">Query table data</span></a></li>
<li class="devsite-nav-item">
<a href="#clean-up" class="devsite-nav-title gc-analytics-event"><span class="devsite-nav-text">Clean up</span></a><ul class="devsite-nav-list">
<li class="devsite-nav-item"><a href="#delete_the_project" class="devsite-nav-title gc-analytics-event"><span class="devsite-nav-text">Delete the project</span></a></li>
<li class="devsite-nav-item"><a href="#delete_the_resources" class="devsite-nav-title gc-analytics-event"><span class="devsite-nav-text">Delete the resources</span></a></li>
</ul>
</li>
<li class="devsite-nav-item"><a href="#whats-next" class="devsite-nav-title gc-analytics-event"><span class="devsite-nav-text">What's next</span></a></li>
</ul></devsite-toc>
  
    
  <div class="devsite-article-body clearfix
  devsite-no-page-title">

  
    
    
    
  <div class="quickstart">
    <h1 class="devsite-page-title" id="use-the-bq-tool">Use the bq tool<devsite-actions><devsite-feature-tooltip class="devsite-page-bookmark-tooltip nocontent" id="devsite-collections-dropdown">

    
    
      <span>
      
      Stay organized with collections
    </span>
    <span>
      
      Save and categorize content based on your preferences.
    </span>
  </devsite-feature-tooltip><!----></devsite-actions>
</h1>

  <section class="intro">
    


<p>In this tutorial, you learn how to use <code>bq</code>, the Python-based command-line
interface (CLI) tool for BigQuery to create a dataset, load sample
data, and query tables. After completing this tutorial, you'll be familiar with
<code>bq</code> and how to work with BigQuery by using a CLI.</p>

<p>For a complete reference of all <code>bq</code> commands and flags, see the
<a href="/bigquery/docs/reference/bq-cli-reference">bq command-line tool reference</a>.</p>



















<hr>
<p>To follow step-by-step guidance for this task directly in the
  Google Cloud console, click <b>Guide me</b>:
</p>


<p><a href="https://console.cloud.google.com/freetrial?redirectPath=/?walkthrough_id=bigquery--load-data-bq" class="button button-primary">Guide me</a>
</p>

<hr>





  </section>

  <section class="prereqs">
    <h2 id="before-you-begin">Before you begin</h2>
    

<ol>

























  
    <cloud-free-trial>
      <div class="eligible">
        
  












  



  
    
      
      <li>
      
        <p>Start by creating a Google Cloud account. With this account, you get $300 in free credits,
          plus free usage of over 20 products, up to monthly limits.</p>
        <p><a href="https://console.cloud.google.com/freetrial" class="button button-primary">Create an account</a></p>
      
      </li>
      
    
  

        
  

    
    
    

    
      
        






















  
  
    
    <li>
    
    
      <p>In the Google Cloud console, on the project selector page,
        select or create a Google Cloud project.</p>
      
<devsite-expandable id="expandable-1"><a class="exw-control"><p class="showalways"><b>Roles required to select or create a project</b></p></a>
  
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

      
      <p><a href="https://console.cloud.google.com/projectselector2/home/dashboard" class="button button-primary">Go to project selector</a></p>
    
    
    </li>
    
  




      
      
        
          <li>
          <p>
            If you're using an existing project for this guide,
            <a href="#required_roles">verify that you have
            the permissions required to complete this guide</a>. If you created a new
            project, then you already have the required permissions.
          </p>
          </li>
        
      
      
      
      
    

    
  

      </div>
      <div class="ineligible">
        
        
  

    
    
    

    
      
        






















  
  
    
    <li>
    
    
      <p>In the Google Cloud console, on the project selector page,
        select or create a Google Cloud project.</p>
      
<devsite-expandable id="expandable-2"><a class="exw-control"><p class="showalways"><b>Roles required to select or create a project</b></p></a>
  
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

      
      <p><a href="https://console.cloud.google.com/projectselector2/home/dashboard" class="button button-primary">Go to project selector</a></p>
    
    
    </li>
    
  




      
      
        
          <li>
          <p>
            If you're using an existing project for this guide,
            <a href="#required_roles">verify that you have
            the permissions required to complete this guide</a>. If you created a new
            project, then you already have the required permissions.
          </p>
          </li>
        
      
      
      
      
    

    
  

      </div>
    </cloud-free-trial>
   
  
  









<li>







<p>
        
          
            
              Enable the BigQuery API.
            
          
        
      </p>
<devsite-expandable id="expandable-3"><a class="exw-control"><p class="showalways"><b>Roles required to enable APIs</b></p></a><p>
          To enable APIs, you need the Service Usage Admin IAM
          role (<code>roles/serviceusage.serviceUsageAdmin</code>), which
          contains the <code>serviceusage.services.enable</code> permission. <a href="/iam/docs/granting-changing-revoking-access">Learn how to grant
          roles</a>.
        </p></devsite-expandable><p><a href="https://console.cloud.google.com/flows/enableapi?apiid=bigquery" class="button button-primary">Enable the API</a></p>
<p>For new projects, the BigQuery API is
  automatically enabled.</p>
</li>
<li>Optional:
  <a href="/billing/docs/how-to/modify-project">Enable
    billing</a> for the project. If you don't want to enable billing or provide
  a credit card, the steps in this document still work. BigQuery
  provides you a sandbox to perform the steps. For more information, see
  <a href="/bigquery/docs/sandbox#setup">Enable the BigQuery sandbox</a>.

  <aside class="note">
  <b>Note:</b> If your project has a billing account and you want to use the
    BigQuery sandbox, then
    <a href="/billing/docs/how-to/modify-project#disable_billing_for_a_project">disable billing for your project</a>.
</aside>
</li>



















  





  
    
  
    
    <p>In one of the following development environments, set up the gcloud CLI:</p>
    <ul>
      <li>
        <p><b>Cloud Shell</b>: to use an online terminal with the gcloud CLI
          already set up, activate Cloud Shell.</p>
          <p><cloud-shell-button><button class="button-primary gc-analytics-event"><span>Activate Cloud Shell on this page</span></button></cloud-shell-button></p>
          
          <p>At the bottom of this page, a Cloud Shell session starts and displays a
            command-line prompt. It can take a few seconds for the session to initialize.</p>
          
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
    
  

  










</ol>
<h3 id="required_roles">Required roles</h3>














  
  
  
































  
  

  
  
    
    
    
    
    
    
      
      
        
        
      
      
    
    
    
    
    
  

  
  
    
    
    
    
    
    
      
      
        
        
      
      
    
    
    
    
    
  




















  <p>
    
      To get the permissions that
      you need to create a dataset, create a table, load data, and query data,
    
      ask your administrator to grant you the
    following IAM roles on the project:
  
    </p>
  

  

  
    <ul>
      
          <li>
            Run load jobs and query jobs:
              
  
  
    
      <a href="/iam/docs/roles-permissions/bigquery#bigquery.jobUser">BigQuery Job User </a> (<code>roles/bigquery.jobUser</code>)
    
            
          </li>
        
      
          <li>
            Create a dataset, create a table, load data into a table, and query a table:
              
  
  
    
      <a href="/iam/docs/roles-permissions/bigquery#bigquery.dataEditor">BigQuery Data Editor </a> (<code>roles/bigquery.dataEditor</code>)
    
            
          </li>
        
      
    </ul>

    <p>
  
  
  For more information about granting roles, see <a href="/iam/docs/granting-changing-revoking-access">Manage access to projects, folders, and organizations</a>.
  
  </p>

  
  
      
      
      <p>
        You might also be able to get
        the required permissions through <a href="/iam/docs/creating-custom-roles">custom
        roles</a> or other <a href="/iam/docs/roles-overview#predefined">predefined
        roles</a>.
      </p>
    
  

  

 

























  </section>

  <section class="steps">
    

<h2 id="download_the_file_that_contains_the_source_data">Download the file that contains the source data</h2>

<p>The file that you're downloading contains approximately 7 MB of data about
popular baby names. It's provided by the US Social Security Administration.</p>

<p>For more information about the data, see the Social Security Administration's
<a href="http://www.ssa.gov/OACT/babynames/background.html">Background information for popular names</a>.</p>

<ol>
<li>
<p>Download the US Social Security Administration's data by opening the
following URL in a new browser tab:</p>
<devsite-code><pre class=""><code>https://www.ssa.gov/OACT/babynames/names.zip
</code></pre></devsite-code>
</li>
<li>
<p>Extract the file.</p>

<p>For more information about the dataset schema, see the
<code>NationalReadMe.pdf</code> file you extracted.</p>
</li>
<li><p>To see what the data looks like, open the <code>yob2024.txt</code> file. This file
contains comma-separated values for name, assigned sex at birth, and number
of children with that name. The file has no header row.</p></li>
<li>
<p>Move the file to your working directory.</p>

<ul>
<li><p>If you're working in Cloud Shell, click
<walkthrough-spotlight-pointer title="Show me where">
<span class="material-icons">more_vert</span>
<strong>More</strong>
</walkthrough-spotlight-pointer>
<strong>Upload</strong>, click <strong>Choose Files</strong>, choose the
<code>yob2024.txt</code> file, and then click <strong>Upload</strong>.</p></li>
<li><p>If you're working in a local shell, copy or move the file <code>yob2024.txt</code>
into the directory where you're running the bq tool.</p></li>
</ul>
</li>
</ol>



<h2 id="create_a_dataset">Create a dataset</h2>



<ol>
<li>
<p>If you launched Cloud Shell from the documentation, enter the
following command to set your project ID. This prevents you from having to
specify the project ID in each CLI command.</p>
<devsite-code><pre class=""><code>gcloud<span class="devsite-syntax-w"> </span>config<span class="devsite-syntax-w"> </span><span class="devsite-syntax-nb">set</span><span class="devsite-syntax-w"> </span>project<span class="devsite-syntax-w"> </span><devsite-var><var>PROJECT_ID</var></devsite-var>
</code></pre></devsite-code>
<p>Replace <var>PROJECT_ID</var> with your project ID.</p>
</li>
</ol>



<ol>
<li>
<p>Enter the following command to create a dataset named <code>babynames</code>:</p>
<devsite-code><pre class=""><code>bq<span class="devsite-syntax-w"> </span>mk<span class="devsite-syntax-w"> </span>--dataset<span class="devsite-syntax-w"> </span>babynames
</code></pre></devsite-code>
<p>The output is similar to the following:</p>


<devsite-code><pre class=""><code>Dataset 'babynames' successfully created.
</code></pre></devsite-code>
</li>
<li>
<p>Confirm that the dataset <code>babynames</code> now appears in your project:</p>
<devsite-code><pre class=""><code>bq<span class="devsite-syntax-w"> </span>ls<span class="devsite-syntax-w"> </span>--datasets<span class="devsite-syntax-o">=</span><span class="devsite-syntax-nb">true</span>
</code></pre></devsite-code>
<p>The output is similar to the following:</p>


<devsite-code><pre class=""><code>  datasetId
-------------
  babynames
</code></pre></devsite-code>
</li>
</ol>



<h2 id="load_data_into_a_table">Load data into a table</h2>

<ol>
<li>
<p>In the <code>babynames</code> dataset, load the source file <code>yob2024.txt</code> into a
new table named <code>names2024</code>:</p>
<devsite-code><pre class=""><code>bq<span class="devsite-syntax-w"> </span>load<span class="devsite-syntax-w"> </span>babynames.names2024<span class="devsite-syntax-w"> </span>yob2024.txt<span class="devsite-syntax-w"> </span>name:string,assigned_sex_at_birth:string,count:integer
</code></pre></devsite-code>
<p>The output is similar to the following:</p>


<devsite-code><pre class=""><code>Upload complete.
Waiting on bqjob_r3c045d7cbe5ca6d2_0000018292f0815f_1 ... (1s) Current status: DONE
</code></pre></devsite-code>
</li>
<li>
<p>Confirm that the table <code>names2024</code> now appears in the <code>babynames</code> dataset:</p>
<devsite-code><pre class=""><code>bq<span class="devsite-syntax-w"> </span>ls<span class="devsite-syntax-w"> </span>--format<span class="devsite-syntax-o">=</span>pretty<span class="devsite-syntax-w"> </span>babynames
</code></pre></devsite-code>
<p>The output is similar to the following. Some columns are omitted to simplify
the output.</p>


<devsite-code><pre class=""><code>+-----------+-------+
|  tableId  | Type  |
+-----------+-------+
| names2024 | TABLE |
+-----------+-------+
</code></pre></devsite-code>
</li>
<li>
<p>Confirm that the table schema of your new <code>names2024</code> table is
<code>name: string</code>, <code>assigned_sex_at_birth: string</code>, and <code>count: integer</code>:</p>
<devsite-code><pre class=""><code>bq<span class="devsite-syntax-w"> </span>show<span class="devsite-syntax-w"> </span>babynames.names2024
</code></pre></devsite-code>
<p>The output is similar to the following. Some columns are omitted to simplify
the output.</p>


<devsite-code><pre class=""><code>  Last modified        Schema                      Total Rows   Total Bytes
----------------- ------------------------------- ------------ ------------
14 Mar 17:16:45   |- name: string                    31904       607494
                  |- assigned_sex_at_birth: string
                  |- count: integer
</code></pre></devsite-code>
</li>
</ol>



<h2 id="query_table_data">Query table data</h2>

<ol>
<li>
<p>Determine the most popular girls' names in the data:</p>
<devsite-code><pre class=""><code><span class="devsite-syntax-n">bq</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-n">query</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-err">\</span>
<span class="devsite-syntax-w">    </span><span class="devsite-syntax-s1">'SELECT</span>
<span class="devsite-syntax-s1">      name,</span>
<span class="devsite-syntax-s1">      count</span>
<span class="devsite-syntax-s1">    FROM</span>
<span class="devsite-syntax-s1">      babynames.names2024</span>
<span class="devsite-syntax-s1">    WHERE</span>
<span class="devsite-syntax-s1">      assigned_sex_at_birth = "F"</span>
<span class="devsite-syntax-s1">    ORDER BY</span>
<span class="devsite-syntax-s1">      count DESC</span>
<span class="devsite-syntax-s1">    LIMIT 5'</span>
</code></pre></devsite-code>
<p>The output is similar to the following:</p>


<devsite-code><pre class=""><code>+-----------+-------+
|   name    | count |
+-----------+-------+
| Olivia    | 14718 |
| Emma      | 13485 |
| Amelia    | 12740 |
| Charlotte | 12552 |
| Mia       | 12113 |
+-----------+-------+
</code></pre></devsite-code>
</li>
<li>
<p>Determine the least popular boys' names in the data:</p>
<devsite-code><pre class=""><code><span class="devsite-syntax-n">bq</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-n">query</span><span class="devsite-syntax-w"> </span><span class="devsite-syntax-err">\</span>
<span class="devsite-syntax-w">    </span><span class="devsite-syntax-s1">'SELECT</span>
<span class="devsite-syntax-s1">      name,</span>
<span class="devsite-syntax-s1">      count</span>
<span class="devsite-syntax-s1">    FROM</span>
<span class="devsite-syntax-s1">      babynames.names2024</span>
<span class="devsite-syntax-s1">    WHERE</span>
<span class="devsite-syntax-s1">      assigned_sex_at_birth = "M"</span>
<span class="devsite-syntax-s1">    ORDER BY</span>
<span class="devsite-syntax-s1">      count ASC</span>
<span class="devsite-syntax-s1">    LIMIT 5'</span>
</code></pre></devsite-code>
<p>The output is similar to the following:</p>


<devsite-code><pre class=""><code>+---------+-------+
|  name   | count |
+---------+-------+
| Aaran   |     5 |
| Aadiv   |     5 |
| Aadarsh |     5 |
| Aarash  |     5 |
| Aadrik  |     5 |
+---------+-------+
</code></pre></devsite-code>


<p>The minimum count is 5 because the source data omits names with fewer than
5 occurrences.</p>
</li>
</ol>




  </section>

  
  <section class="cleanup">
    <h2 id="clean-up">Clean up</h2>
    
      
        <p>
          To avoid incurring charges to your Google Cloud account for
          the resources used on this page, delete the Google Cloud project with the
          resources.
        </p>
      
    
    

<h3 id="delete_the_project">Delete the project</h3>


If you used the <a href="/bigquery/docs/sandbox">BigQuery sandbox</a> to query
the public dataset, then billing is not enabled for your project, and you don't
need to delete the project.<p>
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

<ol>
<li>
<p>Delete the <code>babynames</code> dataset:</p>
<devsite-code><pre class=""><code>bq<span class="devsite-syntax-w"> </span>rm<span class="devsite-syntax-w"> </span>--recursive<span class="devsite-syntax-o">=</span><span class="devsite-syntax-nb">true</span><span class="devsite-syntax-w"> </span>babynames
</code></pre></devsite-code>
<p>The <code>--recursive</code> flag deletes all tables in the dataset, including the
<code>names2024</code> table.</p>

<p>The output is similar to the following:</p>


<devsite-code><pre class=""><code>rm: remove dataset 'myproject:babynames'? (y/N)
</code></pre></devsite-code>
</li>
<li><p>To confirm the delete command, enter <code>y</code>.</p></li>
</ol>


  </section>
  

  <section class="whatsnext">
    <h2 id="whats-next">What's next</h2>
    

<ul>
<li>Learn more about <a href="/bigquery/bq-command-line-tool">using the bq tool</a>.</li>
<li>Learn about the <a href="/bigquery/docs/sandbox">BigQuery sandbox</a>.</li>
<li>Learn more about
<a href="/bigquery/docs/loading-data">loading data into BigQuery</a>.</li>
<li>Learn more about
<a href="/bigquery/docs/query-overview">querying data in BigQuery</a>.</li>
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
      <a href="https://docs.cloud.google.com/bigquery/docs/quickstarts/load-data-bq">English</a>
    </li>
    
    <li>
      <a href="https://docs.cloud.google.com/bigquery/docs/quickstarts/load-data-bq?hl=de">Deutsch</a>
    </li>
    
    <li>
      <a href="https://docs.cloud.google.com/bigquery/docs/quickstarts/load-data-bq?hl=es">Español</a>
    </li>
    
    <li>
      <a href="https://docs.cloud.google.com/bigquery/docs/quickstarts/load-data-bq?hl=es-419">Español – América Latina</a>
    </li>
    
    <li>
      <a href="https://docs.cloud.google.com/bigquery/docs/quickstarts/load-data-bq?hl=fr">Français</a>
    </li>
    
    <li>
      <a href="https://docs.cloud.google.com/bigquery/docs/quickstarts/load-data-bq?hl=id">Indonesia</a>
    </li>
    
    <li>
      <a href="https://docs.cloud.google.com/bigquery/docs/quickstarts/load-data-bq?hl=it">Italiano</a>
    </li>
    
    <li>
      <a href="https://docs.cloud.google.com/bigquery/docs/quickstarts/load-data-bq?hl=pt">Português</a>
    </li>
    
    <li>
      <a href="https://docs.cloud.google.com/bigquery/docs/quickstarts/load-data-bq?hl=pt-br">Português – Brasil</a>
    </li>
    
    <li>
      <a href="https://docs.cloud.google.com/bigquery/docs/quickstarts/load-data-bq?hl=zh-cn">中文 – 简体</a>
    </li>
    
    <li>
      <a href="https://docs.cloud.google.com/bigquery/docs/quickstarts/load-data-bq?hl=zh-tw">中文 – 繁體</a>
    </li>
    
    <li>
      <a href="https://docs.cloud.google.com/bigquery/docs/quickstarts/load-data-bq?hl=ja">日本語</a>
    </li>
    
    <li>
      <a href="https://docs.cloud.google.com/bigquery/docs/quickstarts/load-data-bq?hl=ko">한국어</a>
    </li>
    
  </ul>
</devsite-language-selector>

  </nav>
</div>
          
        </devsite-footer-utility>
        <devsite-panel>
          
<cloud-shell-pane>
<!---->
    <!--?lit$970813483$--> <div class="free-trial-banner">
    <a class="close-btn button-white material-icons">close</a>
    <div class="banner-text">
      <h3>
<!--?lit$970813483$-->Welcome to Cloud Shell</h3>
      <p><!--?lit$970813483$-->Cloud Shell is a development environment that you can use in the browser:</p>
      <ul>
        <li>
<!--?lit$970813483$-->Activate Cloud Shell to explore Google Cloud with a terminal and an editor</li>
        <li>
<!--?lit$970813483$-->Start a free trial to get $300 in free credits</li>
      </ul>
      <div class="row">
        <button class="button-blue"><!--?lit$970813483$-->Activate Cloud Shell
        </button>
        <button>
          <!--?lit$970813483$-->Start a free trial</button>
      </div>
    </div>
    <!--?lit$970813483$--><img src="https://www.gstatic.com/devrel-devsite/prod/v369eac9380f92e8fedc492e2689927bb3475d758266c381eee326d0b49a77481/images/cloud-shell-cta-art.png">
  </div>
  </cloud-shell-pane>

        </devsite-panel>
        
      </section></section>
    </body>
</html>
