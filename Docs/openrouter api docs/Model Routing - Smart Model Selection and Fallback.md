---
title: "Model Routing - Smart Model Selection and Fallback"
source: "https://openrouter.ai/docs/features/model-routing"
author:
  - "[[OpenRouter Documentation]]"
published:
created: 2025-05-08
description: "Dynamically route requests to models"
tags:
  - "clippings"
---
OpenRouter provides two options for model routing.

## Auto Router

The [Auto Router](https://openrouter.ai/openrouter/auto), a special model ID that you can use to choose between selected high-quality models based on your prompt, powered by [NotDiamond](https://www.notdiamond.ai/).

The resulting generation will have `model` set to the model that was used.

## The models parameter

The `models` parameter lets you automatically try other models if the primary model’s providers are down, rate-limited, or refuse to reply due to content moderation.

If the model you selected returns an error, OpenRouter will try to use the fallback model instead. If the fallback model is down or returns an error, OpenRouter will return that error.

By default, any error can trigger the use of a fallback model, including context length validation errors, moderation flags for filtered models, rate-limiting, and downtime.

Requests are priced using the model that was ultimately used, which will be returned in the `model` attribute of the response body.

## Using with OpenAI SDK

To use the `models` array with the OpenAI SDK, include it in the `extra_body` parameter. In the example below, gpt-4o will be tried first, and the `models` array will be tried in order as fallbacks.

x1.00

\>

<

\>>

<<

O

x1.00