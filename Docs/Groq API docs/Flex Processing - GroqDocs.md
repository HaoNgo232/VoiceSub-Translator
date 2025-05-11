---
title: "Flex Processing - GroqDocs"
source: "https://console.groq.com/docs/flex-processing"
author:
published:
created: 2025-05-08
description: "Learn about Groq's Flex Processing service tier, optimized for high-throughput workloads with fast inference and higher rate limits."
tags:
  - "clippings"
---
Flex Processing is a service tier optimized for high-throughput workloads that prioritizes fast inference and can handle occasional request failures. This tier offers significantly higher rate limits while maintaining the same pricing as on-demand processing during beta.

Flex processing is available for all [models](https://console.groq.com/docs/models) to paid customers only with 10x higher rate limits compared to on-demand processing. While in beta, pricing will remain the same as our on-demand tier.

- **On-demand (`"service_tier":"on_demand"`):** The on-demand tier is the default tier and the one you are used to. We have kept rate limits low in order to ensure fairness and a consistent experience.
- **Flex (`"service_tier":"flex"`):** The flex tier offers on-demand processing when capacity is available, with rapid timeouts if resources are constrained. This tier is perfect for workloads that prioritize fast inference and can gracefully handle occasional request failures. It provides an optimal balance between performance and reliability for workloads that don't require guaranteed processing.
- **Auto (`"service_tier":"auto"`):** The auto tier uses on-demand rate limits, then falls back to flex tier if those limits are exceeded.

The `service_tier` parameter is an additional, optional parameter that you can include in your chat completion request to specify the service tier you'd like to use. The possible values are:

| Option | Description |
| --- | --- |
| `flex` | Only uses flex tier limits |
| `on_demand` (default) | Only uses on\_demand rate limits |
| `auto` | First uses on\_demand rate limits, then falls back to flex tier if exceeded |

x1.00

\>

<

\>>

<<

O