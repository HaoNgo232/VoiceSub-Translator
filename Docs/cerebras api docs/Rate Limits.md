---
title: "Rate Limits"
source: "https://inference-docs.cerebras.ai/support/rate-limits"
author:
  - "[[Cerebras Inference]]"
published:
created: 2025-05-08
description:
tags:
  - "clippings"
---
We enforce rate limits to ensure fair usage and system stability. These limits apply per API key and reset periodically based on the type of limit (daily or per-minute).

To help you monitor your usage in real time, we inject several custom headers into every API response. These headers provide insight into your current usage and when your limits will reset.

## Rate Limit Headers

You’ll find the following headers in the response:

| Header | Description |
| --- | --- |
| `x-ratelimit-limit-requests-day` | Maximum number of requests allowed per day. |
| `x-ratelimit-limit-tokens-minute` | Maximum number of tokens allowed per minute. |
| `x-ratelimit-remaining-requests-day` | Number of requests remaining for the current day. |
| `x-ratelimit-remaining-tokens-minute` | Number of tokens remaining for the current minute. |
| `x-ratelimit-reset-requests-day` | Time (in seconds) until your daily request limit resets. |
| `x-ratelimit-reset-tokens-minute` | Time (in seconds) until your per-minute token limit resets. |

These values update with each API call, giving you immediate visibility into your current usage.

## Example

You can view these headers by adding the —verbose flag to a cURL request. Here’s an example:

In the response, look for headers like these:

## Notes

- The `reset` headers are measured in seconds.
- If you exceed your rate limits, you will receive a [429 Too Many Requests error](https://inference-docs.cerebras.ai/support/error).

If you have questions about your usage or need higher rate limits, [contact us](https://www.cerebras.ai/contact) via our website, or reach out to your account representative.

x1.00

\>

<

\>>

<<

O