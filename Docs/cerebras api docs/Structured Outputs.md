---
title: "Structured Outputs"
source: "https://inference-docs.cerebras.ai/capabilities/structured-outputs"
author:
  - "[[Cerebras Inference]]"
published:
created: 2025-05-08
description: "Generate structured data with the Cerebras Inference API"
tags:
  - "clippings"
---
Structured outputs with strict adherence is currently in beta, released in version 1.23 of the Cerebras Inference Cloud SDK. Improvements for speed and expanded support will be released in coming weeks, with documentation updated accordingly.

Structured outputs is a feature that can enforce consistent JSON outputs for models in the Cerebras Inference API. This is particularly useful when building applications that need to process AI-generated data programmatically. Some of the key benefits of using structured outputs are:

- **Reduced Variability**: Ensures consistent outputs by adhering to predefined fields.
- **Type Safety**: Enforces correct data types, preventing mismatches.
- **Easier Parsing & Integration**: Enables direct use in applications without extra processing.

## Tutorial: Structured Outputs using Cerebras Inference

In this tutorial, we’ll explore how to use structured outputs with the Cerebras Cloud SDK. We’ll build a simple application that generates movie recommendations and uses structured outputs to ensure the response is in a consistent JSON format.

## Advanced Schema Features

Your schema can include various JSON Schema features:

- **Types**: String, Number, Boolean, Integer, Object, Array, Enum, anyOf (max of 5), null
- **Nested structures**: Define complex objects with nested properties, with support for up to 5 layers of nesting. You can also use definitions to reference reusable schema components.
- **Required fields**: Specify which fields must be present.
- **Additional properties**: Control whether extra fields are allowed. Note: the only accepted value is `false`.
- **Enums (value constraints)**: Use the `enum` keyword to whitelist the exact literals a field may take. See `rating` in the example below.

For example, a more complex schema might look like:

When used with the API, you might get a response like:

## Working with Pydantic and Zod

Besides defining a JSON schema manually, you can use Pydantic (Python) or Zod (JavaScript) to create your schema and convert it to JSON. Pydantic’s `model_json_schema` and Zod’s `zodToJsonSchema` methods generate the JSON schema, which can then be used in the API call, as demonstrated in the workflow above.

## JSON Mode

In addition to structured outputs, you can also use JSON mode to generate JSON responses from the model. This approach tells the model to return data in JSON format but doesn’t enforce a specific structure. The model decides what fields to include based on the context of your prompt. Note: we recommend using structured outputs (with strict set to true) whenever possible, as it provides more predictable and reliable results.

To use JSON mode, simply set the `response_format` parameter to `json_object`:

### Structured Outputs vs JSON Mode

The table below summarizes the key differences between Structured Outputs and JSON Mode:

| Feature | Structured Output | JSON Mode |
| --- | --- | --- |
| Outputs valid JSON | Yes | Yes |
| Adheres to schema | Yes (enforced) | No (flexible) |
| Compatible models | `llama-3.1-8b`, `llama-3.3-70b` and `llama-4-scout-17b-16e-instruct` | `llama-3.1-8b`, `llama-3.3-70b` and `llama-4-scout-17b-16e-instruct` |
| Enabling | `response_format: { type: "json_schema", json_schema: {"strict": true, "schema": ...} }` | `response_format: { type: "json_object" }` |

## Variation from OpenAI’s Structured Output Capabilities

While our structured output capabilities closely match OpenAI’s implementation, there are a few key differences to note.

These limitations only apply if `strict` is set to `true` in the JSON schema.

Structured outputs do not work with function calling yet. This feature will be supported in a future release.

## Conclusion

Structured outputs with JSON schema enforcement ensures your AI-generated responses follow a consistent, predictable format. This makes it easier to build reliable applications that can process AI outputs programmatically without worrying about unexpected data structures or missing fields.

Check out some of our other tutorials to learn more about other features of the Cerebras Inference SDK:

- [CePO](https://inference-docs.cerebras.ai/capabilities/cepo): a reasoning framework for improving Llama’s reasoning abilities with test-time compute
- [Tool Use](https://inference-docs.cerebras.ai/capabilities/tool-use): extending models’ capabilities to access tools to answer questions and perform actions
- [Streaming](https://inference-docs.cerebras.ai/capabilities/streaming): a feature for streaming responses from the model

x1.00

\>

<

\>>

<<

O