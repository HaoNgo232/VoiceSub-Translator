---
title: "OpenAI Compatibility"
source: "https://inference-docs.cerebras.ai/resources/openai"
author:
  - "[[Cerebras Inference]]"
published:
created: 2025-05-08
description: "Use the OpenAI Client Libraries with Cerebras Inference"
tags:
  - "clippings"
---
We designed the Cerebras API to be mostly compatible with OpenAI’s client libraries, making it simple to configure your existing applications to run on Cerebras and take advantage of our inference capabilities.

We also offer dedicated Cerebras Python and Cerebras TypeScript SDKs.

## Configuring OpenAI to Use Cerebras API

To start using Cerebras with OpenAI’s client libraries, simply pass your Cerebras API key to the `apiKey` parameter and change the `baseURL` to [https://api.cerebras.ai/v1](https://api.cerebras.ai/v1):

## Currently Unsupported OpenAI Features

Note that although Cerebras API is mostly OpenAI compatible, there are a few features we don’t support just yet:

**Text Completions**  
The following fields are currently not supported and will result in a 400 error if they are supplied:

- `frequency_penalty`
- `logit_bias`
- `presence_penalty`
- `parallel_tool_calls`
- `service_tier`

**Streaming with JSON Mode**  
While Cerebras supports a `stream` parameter, note that JSON mode is not compatible with streaming.

x1.00

\>

<

\>>

<<

O

x1.00

OpenAI Compatibility - Cerebras Inference