# Semantic OKF Lifecycle Benchmark

- Work only inside `work/` and `deliverables/`.
- Treat `cases/`, `verification/`, and `bin/` as immutable benchmark inputs.
- Use the installed `build-semantic-okf` skill and its bundled scripts. Do not recreate the builder or refresher.
- Do not browse the web or install dependencies.
- Some safety checks intentionally return a nonzero exit code. Capture their JSON output and continue only when the task says that failure is expected.
- Finish by running the named deterministic verifier and returning the exact JSON response contract from the task.

