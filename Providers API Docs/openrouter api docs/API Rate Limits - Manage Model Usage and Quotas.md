---
title: "API Rate Limits - Manage Model Usage and Quotas"
source: "https://openrouter.ai/docs/api-reference/limits"
author:
  - "[[OpenRouter Documentation]]"
published:
created: 2025-05-08
description: "Rate Limits"
tags:
  - "clippings"
---
If you need a lot of inference, making additional accounts or API keys *makes no difference*. We manage the rate limit globally. We do however have different rate limits for different models, so you can share the load that way if you do run into issues. If you start getting rate limited — [tell us](https://discord.gg/fVyRaUDgxW)! We are here to help. If you are able, don’t specify providers; that will let us load balance it better.

## Rate Limits and Credits Remaining

To check the rate limit or credits left on an API key, make a GET request to `https://openrouter.ai/api/v1/auth/key`.

If you submit a valid API key, you should get a response of the form:

There are a few rate limits that apply to certain types of requests, regardless of account status:

1. Free usage limits: If you’re using a free model variant (with an ID ending in `:free`), you can make up to 20 requests per minute. The following per-day limits apply:
- If you have purchased less than 10 credits, you’re limited to 50`:free` model requests per day.
- If you purchase at least 10 credits, your daily limit is increased to 1000`:free` model requests per day.
1. **DDoS protection**: Cloudflare’s DDoS protection will block requests that dramatically exceed reasonable usage.

For all other requests, rate limits are a function of the number of credits remaining on the key or account. Partial credits round up in your favor. For the credits available on your API key, you can make **1 request per credit per second** up to the surge limit (typically 500 requests per second, but you can go higher).

For example:

- 0.5 credits → 1 req/s (minimum)
- 5 credits → 5 req/s
- 10 credits → 10 req/s
- 500 credits → 500 req/s
- 1000 credits → Contact us if you see ratelimiting from OpenRouter

If your account has a negative credit balance, you may see `402` errors, including for free models. Adding credits to put your balance above zero allows you to use those models again.

x1.00

\>

<

\>>

<<

O