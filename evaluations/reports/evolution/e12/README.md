# EnterpriseRAG E12: controller stopped before native allocation

The original E12 development invocation failed before any native job was
allocated. Its four stages are now **stopped**, and the native organizer's
final verification passed. The [terminal report](preallocation-failure-001/README.md)
records the independently checked cause, preserved opportunity counts and
unchanged internal comparison.

A separate source correction passed **nine integration tests using the actual
pinned Harbor configuration API**. That is software evidence. No E12 retrieval
score, candidate selection, all-500 comparison or promotion resulted.

- [Eight-family status and terminal evidence](preallocation-failure-001/README.md)
- [Cost, time and quality scope](preallocation-failure-001/cta.md)
- [Application, category and dataset availability](preallocation-failure-001/groups.md)
- [Machine-readable aggregate](preallocation-failure-001/aggregate.json)
- [Decision: preserve native template types](../../../../.specs/adr/0151-load-enterprise-native-job-templates-through-owner-api.md)

The all-eight evolution and final-report objective remains incomplete.
Five family searches retain their existing opportunities. The next native
execution requires a separately versioned controller and the existing design
and custody gates; the consumed E12 invocation cannot be restarted.

[Family report index](../../../../docs/enterprise-family-report-index.md)
· [Evolution studies](../README.md)
