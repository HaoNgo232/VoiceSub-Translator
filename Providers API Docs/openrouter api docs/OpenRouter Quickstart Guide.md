---
title: "OpenRouter Quickstart Guide"
source: "https://openrouter.ai/docs/quickstart"
author:
  - "[[OpenRouter Documentation]]"
published:
created: 2025-05-08
description: "Get started with OpenRouter"
tags:
  - "clippings"
---
OpenRouter provides a unified API that gives you access to hundreds of AI models through a single endpoint, while automatically handling fallbacks and selecting the most cost-effective options. Get started with just a few lines of code using your preferred SDK or framework.

Want to chat with our docs? Download an LLM-friendly text file of our [full documentation](https://openrouter.ai/docs/llms-full.txt) and include it in your system prompt.

In the examples below, the OpenRouter-specific headers are optional. Setting them allows your app to appear on the OpenRouter leaderboards.

## Using the OpenAI SDK

## Using the OpenRouter API directly

```
$curl https://openrouter.ai/api/v1/chat/completions \
>  -H "Content-Type: application/json" \
>  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
>  -d '{
>  "model": "openai/gpt-4o",
>  "messages": [
>    {
>      "role": "user",
>      "content": "What is the meaning of life?"
>    }
>  ]
>}'
```

The API also supports [streaming](https://openrouter.ai/docs/api-reference/streaming).

## Using third-party SDKs

For information about using third-party SDKs and frameworks with OpenRouter, please [see our frameworks documentation.](https://openrouter.ai/docs/community/frameworks)

x1.00

\>

<

\>>

<<

O

x1.00