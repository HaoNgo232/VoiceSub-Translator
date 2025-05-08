---
title: "Prompt Caching - Optimize AI Model Costs with Smart Caching"
source: "https://openrouter.ai/docs/features/prompt-caching"
author:
  - "[[OpenRouter Documentation]]"
published:
created: 2025-05-08
description: "Cache prompt messages"
tags:
  - "clippings"
---
To save on inference costs, you can enable prompt caching on supported providers and models.

Most providers automatically enable prompt caching, but note that some (see Anthropic below) require you to enable it on a per-message basis.

When using caching (whether automatically in supported models, or via the `cache_control` header), OpenRouter will make a best-effort to continue routing to the same provider to make use of the warm cache. In the event that the provider with your cached prompt is not available, OpenRouter will try the next-best provider.

## Inspecting cache usage

To see how much caching saved on each generation, you can:

1. Click the detail button on the [Activity](https://openrouter.ai/activity) page
2. Use the `/api/v1/generation` API, [documented here](https://openrouter.ai/docs/api-reference/overview#querying-cost-and-stats)
3. Use `usage: {include: true}` in your request to get the cache tokens at the end of the response (see [Usage Accounting](https://openrouter.ai/docs/use-cases/usage-accounting) for details)

The `cache_discount` field in the response body will tell you how much the response saved on cache usage. Some providers, like Anthropic, will have a negative discount on cache writes, but a positive discount (which reduces total cost) on cache reads.

## OpenAI

Caching price changes:

- **Cache writes**: no cost
- **Cache reads**: charged at 0.5x the price of the original input pricing

Prompt caching with OpenAI is automated and does not require any additional configuration. There is a minimum prompt size of 1024 tokens.

[Click here to read more about OpenAI prompt caching and its limitation.](https://openai.com/index/api-prompt-caching/)

## Anthropic Claude

Caching price changes:

- **Cache writes**: charged at 1.25x the price of the original input pricing
- **Cache reads**: charged at 0.1x the price of the original input pricing

Prompt caching with Anthropic requires the use of `cache_control` breakpoints. There is a limit of four breakpoints, and the cache will expire within five minutes. Therefore, it is recommended to reserve the cache breakpoints for large bodies of text, such as character cards, CSV data, RAG data, book chapters, etc.

[Click here to read more about Anthropic prompt caching and its limitation.](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)

The `cache_control` breakpoint can only be inserted into the text part of a multipart message.

System message caching example:

User message caching example:

## DeepSeek

Caching price changes:

- **Cache writes**: charged at the same price as the original input pricing
- **Cache reads**: charged at 0.1x the price of the original input pricing

Prompt caching with DeepSeek is automated and does not require any additional configuration.

## Google Gemini

### Pricing Changes for Cached Requests:

- **Cache Writes:** Charged at the input token cost plus 5 minutes of cache storage, calculated as follows:
- **Cache Reads:** Charged at 0.25× the original input token cost.

### Supported Models and Limitations:

Only certain Gemini models support caching. Please consult Google’s [Gemini API Pricing Documentation](https://ai.google.dev/gemini-api/docs/pricing) for the most current details.

Cache Writes have a 5 minute Time-to-Live (TTL) that does not update. After 5 minutes, the cache expires and a new cache must be written.

Gemini models have a 4,096 token minimum for cache write to occur. Cached tokens count towards the model’s maximum token usage.

### How Gemini Prompt Caching works on OpenRouter:

OpenRouter simplifies Gemini cache management, abstracting away complexities:

- You **do not** need to manually create, update, or delete caches.
- You **do not** need to manage cache names or TTL explicitly.

### How to Enable Gemini Prompt Caching:

Gemini caching in OpenRouter requires you to insert `cache_control` breakpoints explicitly within message content, similar to Anthropic. We recommend using caching primarily for large content pieces (such as CSV files, lengthy character cards, retrieval augmented generation (RAG) data, or extensive textual sources).

There is not a limit on the number of `cache_control` breakpoints you can include in your request. OpenRouter will use only the last breakpoint for Gemini caching. Including multiple breakpoints is safe and can help maintain compatibility with Anthropic, but only the final one will be used for Gemini.

### Examples:

#### System Message Caching Example

#### User Message Caching Example

x1.00

\>

<

\>>

<<

O