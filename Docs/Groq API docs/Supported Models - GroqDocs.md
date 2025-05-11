---
title: "Supported Models - GroqDocs"
source: "https://console.groq.com/docs/models"
author:
published:
created: 2025-05-08
description: "See all AI models available on Groq."
tags:
  - "clippings"
---
GroqCloud currently supports the following models:

  

**Note:** Production models are intended for use in your production environments. They meet or exceed our high standards for speed, quality, and reliability. Read more [here](https://console.groq.com/docs/deprecations).

| MODEL ID | DEVELOPER | CONTEXT WINDOW (TOKENS) | MAX COMPLETION TOKENS | MAX FILE SIZE | DETAILS |
| --- | --- | --- | --- | --- | --- |
| gemma2-9b-it | Google | 8,192 | \- | \- | [Details](https://huggingface.co/google/gemma-2-9b-it) |
| llama-3.3-70b-versatile | Meta | 128K | 32,768 | \- | [Details](https://console.groq.com/docs/model/llama-3.3-70b-versatile) |
| llama-3.1-8b-instant | Meta | 128K | 8,192 | \- | [Details](https://console.groq.com/docs/model/llama-3.1-8b-instant) |
| llama-guard-3-8b | Meta | 8,192 | \- | \- | [Details](https://console.groq.com/docs/model/llama-guard-3-8b) |
| llama3-70b-8192 | Meta | 8,192 | \- | \- | [Details](https://console.groq.com/docs/model/llama3-70b-8192) |
| llama3-8b-8192 | Meta | 8,192 | \- | \- | [Details](https://console.groq.com/docs/model/llama3-8b-8192) |
| whisper-large-v3 | OpenAI | \- | \- | 25 MB | [Details](https://huggingface.co/openai/whisper-large-v3) |
| whisper-large-v3-turbo | OpenAI | \- | \- | 25 MB | [Details](https://huggingface.co/openai/whisper-large-v3-turbo) |
| distil-whisper-large-v3-en | HuggingFace | \- | \- | 25 MB | [Details](https://huggingface.co/distil-whisper/distil-large-v3) |

  

**Note:** Preview models are intended for evaluation purposes only and should not be used in production environments as they may be discontinued at short notice. Read more about deprecations [here](https://console.groq.com/docs/deprecations).

| MODEL ID | DEVELOPER | CONTEXT WINDOW (TOKENS) | MAX COMPLETION TOKENS | MAX FILE SIZE | DETAILS |
| --- | --- | --- | --- | --- | --- |
| allam-2-7b | Saudi Data and AI Authority (SDAIA) | 4,096 | \- | \- | [Details](https://ai.azure.com/explore/models/ALLaM-2-7b-instruct/version/2/registry/azureml) |
| deepseek-r1-distill-llama-70b | DeepSeek | 128K | \- | \- | [Details](https://console.groq.com/docs/model/deepseek-r1-distill-llama-70b) |
| meta-llama/llama-4-maverick-17b-128e-instruct | Meta | 131,072 | 8192 | \- | [Details](https://console.groq.com/docs/model/llama-4-maverick-17b-128e-instruct) |
| meta-llama/llama-4-scout-17b-16e-instruct | Meta | 131,072 | 8192 | \- | [Details](https://console.groq.com/docs/model/llama-4-scout-17b-16e-instruct) |
| mistral-saba-24b | Mistral | 32K | \- | \- | [Details](https://console.groq.com/docs/model/mistral-saba-24b) |
| playai-tts | Playht, Inc | 10K |  | \- | [Details](https://console.groq.com/docs/model/playai-tts) |
| playai-tts-arabic | Playht, Inc | 10K | \- | \- | [Details](https://console.groq.com/docs/model/playai-tts) |
| qwen-qwq-32b | Alibaba Cloud | 128K | \- | \- | [Details](https://console.groq.com/docs/model/qwen-qwq-32b) |

  

Systems are a collection of models and tools that work together to answer a user query.

**Note:** Preview systems are intended for evaluation purposes only and should not be used in production environments as they may be discontinued at short notice. Read more about deprecations [here](https://console.groq.com/docs/deprecations).

| MODEL ID | DEVELOPER | CONTEXT WINDOW (TOKENS) | MAX COMPLETION TOKENS | MAX FILE SIZE | DETAILS |
| --- | --- | --- | --- | --- | --- |
| compound-beta | Groq | 128K | 8192 | \- | [Details](https://console.groq.com/docs/agentic-tooling/compound-beta) |
| compound-beta-mini | Groq | 128K | 8192 | \- | [Details](https://console.groq.com/docs/agentic-tooling/compound-beta-mini) |

  
[

Learn More About Agentic Tooling

Discover how to build powerful applications with real-time web search and code execution

](https://console.groq.com/docs/agentic-tooling)  

Deprecated models are models that are no longer supported or will no longer be supported in the future. See our deprecation guidelines and deprecated models [here](https://console.groq.com/docs/deprecations).

  

Hosted models are directly accessible through the GroqCloud Models API endpoint using the model IDs mentioned above. You can use the `https://api.groq.com/openai/v1/models` endpoint to return a JSON list of all active models:

x1.00

\>

<

\>>

<<

O