---
title: "Structured Outputs - Type-Safe JSON Responses from AI Models"
source: "https://openrouter.ai/docs/features/structured-outputs"
author:
  - "[[OpenRouter Documentation]]"
published:
created: 2025-05-08
description: "Return structured data from your models"
tags:
  - "clippings"
---
OpenRouter supports structured outputs for compatible models, ensuring responses follow a specific JSON Schema format. This feature is particularly useful when you need consistent, well-formatted responses that can be reliably parsed by your application.

## Overview

Structured outputs allow you to:

- Enforce specific JSON Schema validation on model responses
- Get consistent, type-safe outputs
- Avoid parsing errors and hallucinated fields
- Simplify response handling in your application

## Using Structured Outputs

To use structured outputs, include a `response_format` parameter in your request, with `type` set to `json_schema` and the `json_schema` object containing your schema:

The model will respond with a JSON object that strictly follows your schema:

## Model Support

Structured outputs are supported by select models.

You can find a list of models that support structured outputs on the [models page](https://openrouter.ai/models?order=newest&supported_parameters=structured_outputs).

- OpenAI models (GPT-4o and later versions) [Docs](https://platform.openai.com/docs/guides/structured-outputs)
- All Fireworks provided models [Docs](https://docs.fireworks.ai/structured-responses/structured-response-formatting#structured-response-modes)

To ensure your chosen model supports structured outputs:

1. Check the model’s supported parameters on the [models page](https://openrouter.ai/models)
2. Set `require_parameters: true` in your provider preferences (see [Provider Routing](https://openrouter.ai/docs/features/provider-routing))
3. Include `response_format` and set `type: json_schema` in the required parameters

## Best Practices

1. **Include descriptions**: Add clear descriptions to your schema properties to guide the model
2. **Use strict mode**: Always set `strict: true` to ensure the model follows your schema exactly

## Example Implementation

Here’s a complete example using the Fetch API:

## Streaming with Structured Outputs

Structured outputs are also supported with streaming responses. The model will stream valid partial JSON that, when complete, forms a valid response matching your schema.

To enable streaming with structured outputs, simply add `stream: true` to your request:

When using structured outputs, you may encounter these scenarios:

1. **Model doesn’t support structured outputs**: The request will fail with an error indicating lack of support
2. **Invalid schema**: The model will return an error if your JSON Schema is invalid

x1.00

\>

<

\>>

<<

O