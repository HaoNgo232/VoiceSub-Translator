---
title: "Tool Use"
source: "https://inference-docs.cerebras.ai/capabilities/tool-use"
author:
  - "[[Cerebras Inference]]"
published:
created: 2025-05-08
description:
tags:
  - "clippings"
---
The Cerebras Inference SDK supports tool use, enabling programmatic execution of specific tasks by sending requests with clearly defined operations. This guide will walk you through a detailed example of how to use tool use with the Cerebras Inference SDK.

For a more detailed conceptual guide to tool use and function calling, please visit our AI Agent Bootcamp [section](https://inference-docs.cerebras.ai/agent-bootcamp/section-2) on the topic.

Tool calling is currently enabled via prompt engineering, but strict adherence to expected outputs is not yet guaranteed. The LLM autonomously determines whether to call a tool. An update is in progress to improve reliability in future versions.

In this case, the LLM determined that a tool call was appropriate to answer the users’ question of what the result of 15 multiplied by 7 is. See the output below.

## Conclusion

Tool use is an important feature that extends the capabilities of LLMs by allowing them to access pre-defined tools. Here are some more resources to continue learning about tool use with the Cerebras Inference SDK.

- [API Reference](https://inference-docs.cerebras.ai/api-reference/chat-completions)
- [AI Agent Bootcamp: Tool Use & Function Calling](https://inference-docs.cerebras.ai/agent-bootcamp/section-2)
- [Integration with Instructor for Structured Outputs](https://python.useinstructor.com/blog/2024/10/15/introducing-structured-outputs-with-cerebras-inference/)

x1.00

\>

<

\>>

<<

O

x1.00

Tool Use - Cerebras Inference