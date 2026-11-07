# Scope of the first broker endpoint

The model-authored manifest's `model_calls: 0` refers to its synthetic worker tests. Terra's construction session made real paid model calls, recorded separately in `invocation.json`. No real Gemma worker was invoked by this prototype.

Gemma's fresh review is an acceptable **limited synthetic draft** assessment. Neither that report nor file mode 0600 proves actor isolation for processes sharing a UID: actual mount/identity restrictions and controller container-wide cleanup/snapshot checks remain unqualified. Registered mode stays disabled. Full OpenCode/Gemma routing, all-model accounting, global stopping and actual physical-boundary race tests are still required.
