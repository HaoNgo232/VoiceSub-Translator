---
title: "Rate Limits - GroqDocs"
source: "https://console.groq.com/docs/rate-limits"
author:
published:
created: 2025-05-08
description: "Understand Groq API rate limits, headers, and best practices for managing request and token quotas in your applications."
tags:
  - "clippings"
---
Rate limits act as control measures to regulate how frequently users and applications can access our API within specified timeframes. These limits help ensure service stability, fair access, and protection against misuse so that we can serve reliable and fast inference for all.

Rate limits are measured in:

- **RPM:** Requests per minute
- **RPD:** Requests per day
- **TPM:** Tokens per minute
- **TPD:** Tokens per day
- **ASH:** Audio seconds per hour
- **ASD:** Audio seconds per day

Rate limits apply at the organization level, not individual users. You can hit any limit type depending on which threshold you reach first.

**Example:** Let's say your RPM = 50 and your TPM = 200K. If you were to send 50 requests with only 100 tokens within a minute, you would reach your limit even though you did not send 200K tokens within those 50 requests.

The following is a high level summary and there may be exceptions to these limits. You can view the current, exact rate limits for your organization on the [limits page](https://console.groq.com/settings/limits) in your account settings.

| MODEL ID | RPM | RPD | TPM | TPD | ASH | ASD |
| --- | --- | --- | --- | --- | --- | --- |
| allam-2-7b | 30 | 7000 | 6000 | \- | \- | \- |
| compound-beta | 15 | 200 | 70000 | \- | \- | \- |
| compound-beta-mini | 15 | 200 | 70000 | \- | \- | \- |
| deepseek-r1-distill-llama-70b | 30 | 1000 | 6000 | \- | \- | \- |
| distil-whisper-large-v3-en | 20 | 2000 | \- | \- | 7200 | 28800 |
| gemma2-9b-it | 30 | 14400 | 15000 | 500000 | \- | \- |
| llama-3.1-8b-instant | 30 | 14400 | 6000 | 500000 | \- | \- |
| llama-3.3-70b-versatile | 30 | 1000 | 12000 | 100000 | \- | \- |
| llama-guard-3-8b | 30 | 14400 | 15000 | 500000 | \- | \- |
| llama3-70b-8192 | 30 | 14400 | 6000 | 500000 | \- | \- |
| llama3-8b-8192 | 30 | 14400 | 6000 | 500000 | \- | \- |
| meta-llama/llama-4-maverick-17b-128e-instruct | 30 | 1000 | 6000 | \- | \- | \- |
| meta-llama/llama-4-scout-17b-16e-instruct | 30 | 1000 | 30000 | \- | \- | \- |
| mistral-saba-24b | 30 | 1000 | 6000 | 500000 | \- | \- |
| playai-tts | 10 | 100 | 1200 | 3600 | \- | \- |
| playai-tts-arabic | 10 | 100 | 1200 | 3600 | \- | \- |
| qwen-qwq-32b | 30 | 1000 | 6000 | \- | \- | \- |
| whisper-large-v3 | 20 | 2000 | \- | \- | 7200 | 28800 |
| whisper-large-v3-turbo | 20 | 2000 | \- | \- | 7200 | 28800 |

In addition to viewing your limits on your account's [limits](https://console.groq.com/settings/limits) page, you can also view rate limit information such as remaining requests and tokens in HTTP response headers as follows:

The following headers are set (values are illustrative):

When you exceed rate limits, our API returns a `429 Too Many Requests` HTTP status code.

**Note**: `retry-after` is only set if you hit the rate limit and status code 429 is returned. The other headers are always included.

x1.00

\>

<

\>>

<<

O