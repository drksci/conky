---
kind: research
title: "Observability standards for an agent runtime"
status: current
date: 2026-11-20
source: "OpenTelemetry GenAI semantic conventions (semantic-conventions-genai repository), OTLP specification, OTel file exporter, OpenInference, OpenLLMetry, W3C Trace Context"
---

# Observability standards for an agent runtime

Question: which open standard should record what an agent runtime does (model calls, tool calls, agent steps, tokens, time, errors), so ordinary observability tools can read the record.

## What was read

| Source | Address | Fetched | How far |
|---|---|---|---|
| OTel GenAI conventions, old site | https://opentelemetry.io/docs/specs/semconv/gen-ai/ | 2026-11-20 | Notice only: pages moved to the repository below |
| OTel GenAI conventions repository | https://github.com/open-telemetry/semantic-conventions-genai | 2026-11-20 | README and directory listing |
| Agent, inference, tool and metrics pages | `docs/gen-ai/gen-ai-agent-spans.md`, `client-inference.md`, `execute-tool.md`, `gen-ai-metrics.md` in that repository | 2026-11-20 | Attribute tables; `client-inference.md` read to 100000 of 133398 characters |
| OTLP specification | https://opentelemetry.io/docs/specs/otlp/ | 2026-11-20 | Status and JSON encoding rules |
| OTel file exporter | https://opentelemetry.io/docs/specs/otel/protocol/file-exporter/ | 2026-11-20 | Whole page |
| OpenInference | https://github.com/Arize-ai/openinference and https://openinf.dev/spec/ | 2026-11-20 | README and spec index; attribute definitions not read |
| OpenLLMetry | https://github.com/traceloop/openllmetry and https://www.traceloop.com/docs/openllmetry/introduction | 2026-11-20 | README and introduction |
| W3C Trace Context | https://www.w3.org/TR/trace-context/ | 2026-11-20 | Status and header format |

## What each defines

**OpenTelemetry GenAI conventions.** Spans for inference (`gen_ai.operation.name` such as `chat`), agent creation and invocation (`create_agent`, `invoke_agent`, `invoke_workflow`, `plan`) and tool execution (`execute_tool`), plus metrics and events. Attributes sit in the `gen_ai.*` family. The conventions moved from the main semantic-conventions repository to a separate one. The repository README does not state a stability status or a schema URL (it reads "TODO"), so the status below comes from the individual pages.

**OpenInference.** A specification from Arize for recording AI applications as OpenTelemetry traces. It sets span kinds (`LLM`, `AGENT`, `TOOL`, `RETRIEVER`) in `openinference.span.kind` and attributes such as `llm.token_count.prompt`. It says it builds on OpenTelemetry, and its spec index lists an experimental export to the GenAI conventions.

**OpenLLMetry.** Instrumentation libraries from Traceloop, Apache-2.0, "built on top of OpenTelemetry". Its README says its semantic conventions are now part of OpenTelemetry. It is software that emits traces, not a separate record format. The sources fetched do not say whether it needs a collector.

**OTLP and its file form.** OTLP is stable for traces, metrics and logs. The file exporter page defines JSON lines (UTF-8, one JSON value per line, preferred extension `jsonl`) holding `TracesData`, `MetricsData` or `LogsData`, one type per file. Its status is Development. No collector is needed to write it.

**W3C Trace Context.** A Recommendation (23 November 2021) for the `traceparent` header: version, 32-hex trace id, 16-hex parent id, flags. It links spans across processes.

## Comparison

| | OTel GenAI | OpenInference | OpenLLMetry | OTLP file | W3C Trace Context |
|---|---|---|---|---|---|
| Open standard or single vendor | Open standard, OpenTelemetry project | Open spec, led by Arize | Open source, single vendor (Traceloop) | Open standard | Open standard |
| Model calls, tools, agents | All three | LLM, tool, agent, retriever kinds | Via instrumentation | Carrier only | Carrier only |
| Stability today | Development, except `error.type` (Stable) | No version stated; two parts experimental | Not stated | Development | Recommendation |
| Works with no collector | Yes, as OTLP JSON lines | Yes, as OTLP | Not verified | Yes | Not applicable |
| Support | OpenTelemetry project; OpenAI, Anthropic, Bedrock and MCP pages exist | Arize Phoenix and AX | Traceloop | OpenTelemetry project | W3C |

## Recommendation

Use the OpenTelemetry GenAI conventions for names, written as OTLP JSON lines files, with `Cause` supplying the parent link. It is the only candidate that is both vendor-neutral and the one the others are converging on, and it has named spans for all three activities. It is not stable yet: every `gen_ai.*` attribute read is marked Development, so names may change and the vocabulary should pin the version it was read against. OpenInference and OpenLLMetry add nothing to the record that these names lack, and both defer to OpenTelemetry. W3C Trace Context is needed only if a trace must cross a process boundary.

## Mapping from Conky trailers

| Trailer | OpenTelemetry name | Note |
|---|---|---|
| `Kind` | `gen_ai.operation.name` for model calls (`chat`), tools (`execute_tool`) and agent steps (`invoke_agent`) | Other kinds (write, refusal) have no operation value: `conky.kind` |
| `Page` | `gen_ai.agent.name` | Low cardinality required; a page is an agent |
| `Cause` | Span parent id | Not an attribute. The commit id of the cause becomes `parentSpanId` |
| `Reason` | `error.type` (Stable) | Short class only; the sentence goes under `conky.reason` |
| `Model` | `gen_ai.provider.name` | Provider page, to be confirmed against the meaning of the trailer |
| `Model-Name` | `gen_ai.request.model` | `gen_ai.response.model` if the answer reports one |
| `Tokens-In` | `gen_ai.usage.input_tokens` | Includes cached tokens |
| `Tokens-Out` | `gen_ai.usage.output_tokens` | Includes reasoning tokens |
| `Cache` (hit) | `gen_ai.usage.cache_read.input_tokens` is a token count, not a flag | Hit flag: `conky.cache.hit` |
| `From` | none | `conky.from` |
| `Read` | none | `conky.read` |

A trace can be derived from the history: each commit is a span, its id gives the span id, `Cause` gives the parent, and a root commit starts a trace. Nothing is added to the vault; the export is derived data.

Missing today: the duration of a model call is not recorded in any trailer, so `gen_ai.client.operation.duration` and span end time cannot be filled. The commit time gives a start only. Tool name and tool call id are also absent from the trailers listed. Trace and span ids would be derived from commit ids, a choice not found in any source read.

## Not verified

The stability status of the repository as a whole, the OpenInference attribute definitions, whether OpenLLMetry needs a collector, and the final 33398 characters of `client-inference.md`.
