---
title: "Rate limits"
source: "https://novita.ai/docs/guides/llm-rate-limits"
author:
  - "[[Documentation]]"
published:
created: 2025-05-08
description:
tags:
  - "clippings"
---
Rate limits control how frequently users can make requests to our LLM API within specific time periods. Understanding and working within these limits is essential for optimal API usage.

## 1\. Understanding Rate Limits

### What are Rate Limits?

Rate limits restrict the number of API requests that can be made within defined time periods. They help:

- Prevent API abuse and misuse;
- Ensure fair resource distribution among users;
- Maintain consistent API performance and reliability;
- Protect the stability of our services.

### Default Rate Limits

Each account has a default rate limit for model calls, measured in RPM (requests per model per minute) and TPM (tokens per model per minute). Rate limits vary by account tier, as outlined in the tables below.

| Tier | How to reach |
| --- | --- |
| T1 | Monthly top-ups did not exceed $50 in any of the last 3 calendar months. |
| T2 | Monthly top-ups were at least $50 but did not exceed $500 in any of the last 3 calendar months. |
| T3 | Monthly top-ups were at least $500 but did not exceed $3,000 in any of the last 3 calendar months. |
| T4 | Monthly top-ups were at least $3,000 but did not exceed $10,000 in any of the last 3 calendar months. |
| T5 | Monthly top-ups were at least $10,000 in at least one of the last 3 calendar months. |

The last 3 calendar months refers to the current month and the two months before it.

Default Rate Limit by Tier (RPM / TPM):

<table><thead><tr><th>Model</th><th></th><th>T1</th><th>T2</th><th>T3</th><th>T4</th><th>T5</th></tr></thead><tbody><tr><td rowspan="2">deepseek/deepseek-prover-v2-671b</td><td>RPM</td><td>10</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">qwen/qwen3-235b-a22b-fp8</td><td>RPM</td><td>10</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">qwen/qwen3-30b-a3b-fp8</td><td>RPM</td><td>20</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">qwen/qwen3-32b-fp8</td><td>RPM</td><td>20</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">deepseek/deepseek-v3-0324</td><td>RPM</td><td>10</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">qwen/qwen2.5-vl-72b-instruct</td><td>RPM</td><td>20</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">deepseek/deepseek-v3-turbo</td><td>RPM</td><td>10</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">deepseek/deepseek-r1-turbo</td><td>RPM</td><td>10</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">meta-llama/llama-4-maverick-17b-128e-instruct-fp8</td><td>RPM</td><td>10</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">google/gemma-3-27b-it</td><td>RPM</td><td>20</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">qwen/qwq-32b</td><td>RPM</td><td>20</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">Sao10K/L3-8B-Stheno-v3.2</td><td>RPM</td><td>50</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">gryphe/mythomax-l2-13b</td><td>RPM</td><td>50</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">meta-llama/llama-4-scout-17b-16e-instruct</td><td>RPM</td><td>50</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">deepseek/deepseek-r1-distill-llama-8b</td><td>RPM</td><td>50</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">deepseek/deepseek_v3</td><td>RPM</td><td>10</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">meta-llama/llama-3.1-8b-instruct</td><td>RPM</td><td>50</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">deepseek/deepseek-r1-distill-qwen-14b</td><td>RPM</td><td>50</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">meta-llama/llama-3.3-70b-instruct</td><td>RPM</td><td>20</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">qwen/qwen-2.5-72b-instruct</td><td>RPM</td><td>20</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">mistralai/mistral-nemo</td><td>RPM</td><td>50</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">deepseek/deepseek-r1-distill-qwen-32b</td><td>RPM</td><td>20</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">meta-llama/llama-3-8b-instruct</td><td>RPM</td><td>50</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">microsoft/wizardlm-2-8x22b</td><td>RPM</td><td>20</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">deepseek/deepseek-r1-distill-llama-70b</td><td>RPM</td><td>20</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">meta-llama/llama-3.1-70b-instruct</td><td>RPM</td><td>20</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">google/gemma-2-9b-it</td><td>RPM</td><td>50</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">mistralai/mistral-7b-instruct</td><td>RPM</td><td>50</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">meta-llama/llama-3-70b-instruct</td><td>RPM</td><td>20</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">deepseek/deepseek-r1</td><td>RPM</td><td>10</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">nousresearch/hermes-2-pro-llama-3-8b</td><td>RPM</td><td>50</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">sao10k/l3-70b-euryale-v2.1</td><td>RPM</td><td>20</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">cognitivecomputations/dolphin-mixtral-8x22b</td><td>RPM</td><td>10</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">jondurbin/airoboros-l2-70b</td><td>RPM</td><td>20</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">sophosympatheia/midnight-rose-70b</td><td>RPM</td><td>20</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">sao10k/l3-8b-lunaris</td><td>RPM</td><td>50</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">qwen/qwen3-0.6b-fp8</td><td>RPM</td><td>1,000</td><td>1,000</td><td>1,000</td><td>1,000</td><td>1,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">qwen/qwen3-1.7b-fp8</td><td>RPM</td><td>1,000</td><td>1,000</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">qwen/qwen3-8b-fp8</td><td>RPM</td><td>50</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">qwen/qwen3-4b-fp8</td><td>RPM</td><td>1,000</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">qwen/qwen3-14b-fp8</td><td>RPM</td><td>50</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">thudm/glm-4-9b-0414</td><td>RPM</td><td>1,000</td><td>1,000</td><td>1,000</td><td>1,000</td><td>1,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">thudm/glm-z1-9b-0414</td><td>RPM</td><td>1,000</td><td>1,000</td><td>1,000</td><td>1,000</td><td>1,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">thudm/glm-z1-32b-0414</td><td>RPM</td><td>20</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">thudm/glm-4-32b-0414</td><td>RPM</td><td>20</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">thudm/glm-z1-rumination-32b-0414</td><td>RPM</td><td>20</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">qwen/qwen2.5-7b-instruct</td><td>RPM</td><td>1,000</td><td>1,000</td><td>1,000</td><td>1,000</td><td>1,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">meta-llama/llama-3.2-1b-instruct</td><td>RPM</td><td>1,000</td><td>1,000</td><td>1,000</td><td>1,000</td><td>1,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">meta-llama/llama-3.2-11b-vision-instruct</td><td>RPM</td><td>50</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">meta-llama/llama-3.2-3b-instruct</td><td>RPM</td><td>50</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">meta-llama/llama-3.1-8b-instruct-bf16</td><td>RPM</td><td>50</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr><tr><td rowspan="2">sao10k/l31-70b-euryale-v2.2</td><td>RPM</td><td>20</td><td>100</td><td>1,000</td><td>3,000</td><td>6,000</td></tr><tr><td>TPM</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td><td>50,000,000</td></tr></tbody></table>

## 2\. Handling Rate Limits

### How to Monitor Rate Limits?

When you exceed the rate limit, the API will return:

- HTTP Status Code: 429 (Too Many Requests);
- A rate limit exceeded message in the response body.

### Best Practices

To avoid hitting rate limits:

1. Implement request throttling in your application;
2. Add exponential backoff for retries;
3. Monitor your API usage patterns.

### When You Hit Rate Limits

If you receive a 429 error, you can:

1. **Retry Later**: Wait a short period before retrying your request;
2. **Optimize Requests**: Reduce request frequency;
3. **Rate Limits Increase**: For higher rate limits, you can:
	- [Contact us through Discord](https://discord.gg/YyPRAzwp7P)
	- or [Book a call with our sales team](https://meet.brevo.com/novita-ai/contact-sales)

---

**If you have any questions, [please reach out to us on Discord](https://discord.gg/YyPRAzwp7P).**

x1.00

\>

<

\>>

<<

O