# PySpark Runtime

## Baseline

The authored baseline is Apache Spark/PySpark 4.1.2. Its official Python documentation requires Python 3.10 or later and Java 17 or later for local/classic PySpark. The skill pins PySpark and its Python dependencies, but it does not install or mutate a system JDK.

Primary documentation:

- PySpark overview: https://spark.apache.org/docs/latest/api/python/index.html
- Installation and Java/Python requirements: https://spark.apache.org/docs/latest/api/python/getting_started/install.html
- CSV/JSON/text readers: https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/io.html
- Whole-file text reader: https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrameReader.text.html
- Whole text files: https://spark.apache.org/docs/latest/api/python/reference/api/pyspark.SparkContext.wholeTextFiles.html
- PySpark testing: https://spark.apache.org/docs/latest/api/python/getting_started/testing_pyspark.html

## Local execution

Use `local[2]` for tests so multiple partitions execute without exhausting developer machines. Disable the Spark UI and reduce shuffle partitions in test sessions. Set `JAVA_HOME` to a Java 17+ installation and ensure its `bin` directory is available to the process.

Run the Pi smoke test before source processing. It uses `SparkSession.range`, partitioned arithmetic, and aggregation, so a successful result demonstrates driver/JVM startup and distributed DataFrame execution rather than merely importing `pyspark`.

On local Windows, Spark 4.1.2's simple Python-worker launcher waits only ten seconds for a new worker to connect. Endpoint scanning can make a first worker exceed that window even though the JVM-only Pi check passed. The builder therefore starts two small reusable Python workers immediately after session creation, before constructing a large source plan, and extends the separate authenticated result-socket timeout. A failure now happens during this explicit warm-up instead of after partial processing. Do not disable worker reuse for this pipeline.

## Source ingestion

- Read CSV with an explicit header/schema policy. Schema inference is a convenience, not a semantic contract.
- Read JSON Lines by default; use `multiLine=true` only for one JSON document per file.
- Read Markdown and RDF with `DataFrameReader.text(..., wholetext=True)` so each UTF-8 file remains one record.
- Parse RDF inside Spark worker transformations with pinned RDFLib. Return normalized scalar records to Spark rather than shipping mutable graph objects.
- Use `input_file_name()` for source lineage, then normalize local paths relative to the manifest directory before publishing.

Spark documents that whole-file ingestion loads each file fully in memory. Use it for ordinary documents and RDF files, not multi-gigabyte single files. Split oversized sources upstream.

## Determinism and scale

Never depend on Spark partition or row order. Sort by stable source ID, record ID, and source path before returning records to the driver. The bundled builder collects the normalized projection in one result transfer and then retains normalized records and RDFLib graphs in driver memory for atomic cross-artifact validation. This avoids the extra callback sockets used by `toLocalIterator()` on classic local Windows, without increasing the materializer's eventual memory requirement. Size the accepted bundle for driver memory or split it into independently versioned bundles.

Keep the semantic plan small enough for driver use. Broadcast it when worker parsing needs mappings. Store normalized record digests and source counts in the build report.

## Cluster deployment

The bundled builder intentionally accepts only manifest-relative local filesystem globs. A non-local Spark master can still execute transformations, but this implementation is not a Hadoop/object-store ingestion adapter. Local tests do not prove cluster filesystem visibility, dependency distribution, or executor memory sizing. Before cluster deployment:

- distribute the locked Python environment and RDFLib to every executor;
- implement and review a separate Hadoop-compatible URI resolver and provenance policy;
- pin Spark/JVM versions and record them in the build report;
- keep credentials outside the manifest;
- sandbox untrusted RDF and SHACL input;
- rerun all coherence and negative-fixture tests in the target deployment.
