---
title: "Chat Completions"
source: "https://inference-docs.cerebras.ai/api-reference/chat-completions"
author:
  - "[[Cerebras Inference]]"
published:
created: 2025-05-08
description:
tags:
  - "clippings"
---
messages

object\[\]

required

A list of messages comprising the conversation so far.

**Note**: System prompts must be passed to the `messages` parameter as a string. Support for other object types will be added in future releases.model

string

required

Available options:

- `llama-4-scout-17b-16e-instruct`
- `llama3.1-8b`
- `llama-3.3-70b`
- `deepseek-r1-distill-llama-70b` (private preview)

`deepseek-r1-distill-llama-70b` are available in private preview. Please [contact us](https://cerebras.ai/contact) to request access.max\_completion\_tokens

integer | null

The maximum number of **tokens** that can be generated in the completion. The total length of input tokens and generated tokens is limited by the model’s context length.response\_format

object | null

Controls the format of the model response. The primary option is structured outputs with schema enforcement, which ensures the model returns valid JSON adhering to your defined schema structure.

Setting to `{ "type": "json_schema", "json_schema": { "name": "schema_name", "strict": true, "schema": {...} } }` enforces schema compliance. The schema must follow standard JSON Schema format with the following properties:

Note: Structured outputs with JSON schema is currently in beta. Visit our page on [Structured Outputs](https://inference-docs.cerebras.ai/capabilities/structured-outputs) for more information.seed

integer | null

If specified, our system will make a best effort to sample deterministically, such that repeated requests with the same `seed` and parameters should return the same result. Determinism is not guaranteed.stop

string | null

Up to 4 sequences where the API will stop generating further tokens. The returned text will not contain the stop sequence.stream

boolean | null

If set, partial message deltas will be sent.temperature

number | null

What sampling temperature to use, between 0 and 1.5. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. We generally recommend altering this or top\_p but not both.top\_p

number | null

An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top\_p probability mass. So, 0.1 means only the tokens comprising the top 10% probability mass are considered. We generally recommend altering this or temperature but not both.tool\_choice

string | object

Controls which (if any) tool is called by the model. `none` means the model will not call any tool and instead generates a message. `auto` means the model can pick between generating a message or calling one or more tools. required means the model must call one or more tools. Specifying a particular tool via `{"type": "function", "function": {"name": "my_function"}}` forces the model to call that tool.

`none` is the default when no tools are present. `auto` is the default if tools are present.tools

object | null

A list of tools the model may call. Currently, only functions are supported as a tool. Use this to provide a list of functions the model may generate JSON inputs for.

Specifying tools consumes prompt tokens in the context. If too many are given, the model may perform poorly or you may hit context length limitationsuser

string | null

A unique identifier representing your end-user, which can help to monitor and detect abuse.logprobs

bool

Whether to return log probabilities of the output tokens or not.

Default: `False`top\_logprobs

integer | null

An integer between 0 and 20 specifying the number of most likely tokens to return at each token position, each with an associated log probability.`logprobs` must be set to true if this parameter is used.

x1.00

\>

<

\>>

<<

O