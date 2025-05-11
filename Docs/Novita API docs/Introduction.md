---
title: "Introduction"
source: "https://novita.ai/docs/guides/llm-api"
author:
  - "[[Documentation]]"
published:
created: 2025-05-08
description:
tags:
  - "clippings"
---
We provide compatibility with the OpenAI API standard, allowing for easier integration into existing applications.

## Base URL

```
https://api.novita.ai/v3/openai
```

## The APIs we support are:

- [Chat Completion](https://novita.ai/docs/api-reference/model-apis-llm-create-chat-completion), both streaming and regular.
- [Completion](https://novita.ai/docs/api-reference/model-apis-llm-create-completion), both streaming and regular.

## The Models we support are:

You can find all the models we support here: [https://novita.ai/llm-api](https://novita.ai/llm-api) or request the [List Models API](https://novita.ai/docs/api-reference/model-apis-llm-list-models) to get all available models.

## Example with Python Client

- **Chat Completions API**
- **Completions API**

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.novita.ai/v3/openai",
    # Get the Novita AI API Key from: https://novita.ai/settings/key-management.
    api_key="<YOUR Novita AI API Key>",
)

model = "meta-llama/llama-3.1-8b-instruct"
stream = True  # or False
max_tokens = 512

completion_res = client.completions.create(
    model=model,
    prompt="A chat between a curious user and an artificial intelligence assistant.\nYou are a cooking assistant.\nBe edgy in your cooking ideas.\nUSER: How do I make pasta?\nASSISTANT: First, boil water. Then, add pasta to the boiling water. Cook for 8-10 minutes or until al dente. Drain and serve!\nUSER: How do I make it better?\nASSISTANT:",
    stream=stream,
    max_tokens=max_tokens,
)

if stream:
    for chunk in completion_res:
        print(chunk.choices[0].text or "", end="")
else:
    print(completion_res.choices[0].text)
```

## Example with Curl Client

- **Chat Completions API**
- **Completions API**

If you’re already using OpenAI’s chat completion endpoint, you can simply set the base URL to `https://api.novita.ai/v3/openai`, obtain and set your API Key (detailed instructions are available at [https://novita.ai/guides/quickstart#\_2-manage-api-key](https://novita.ai/guides/quickstart#_2-manage-api-key)), and update the model name according to your needs. With these steps, you’re good to go.

If the response status code is not 200, we will return the error code and message in JSON format in the response body. The format is as follows:

| Code | Reason | Description |
| --- | --- | --- |
| 401 | INVALID\_API\_KEY | The API key is invalid. You can check your API key here: [Manage API Key](https://novita.ai/docs/guides/quickstart#2-manage-api-key) |
| 403 | NOT\_ENOUGH\_BALANCE | Your credit is not enough. You can top up more credit here: [Top Up Credit](https://novita.ai/docs/guides/quickstart#3-maintain-sufficient-credit-balance-in-your-account) |
| 404 | MODEL\_NOT\_FOUND | The requested model is not found. You can find all the models we support here: [https://novita.ai/llm-api](https://novita.ai/llm-api) or request the [List models API](https://novita.ai/docs/api-reference/model-apis-llm-list-models) to get all available models. |
| 429 | RATE\_LIMIT\_EXCEEDED | You have exceeded the rate limit. Please refer to [Rate limits](https://novita.ai/docs/guides/llm-rate-limits) for more information. |
| 500 | MODEL\_NOT\_AVAILABLE | The requested model is not available now. This is usually due to the model being under maintenance. You can contact us on [Discord](https://discord.gg/YyPRAzwp7P) for more information. |

x1.00

\>

<

\>>

<<

O