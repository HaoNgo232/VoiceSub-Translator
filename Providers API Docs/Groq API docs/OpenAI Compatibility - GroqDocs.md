---
title: "OpenAI Compatibility - GroqDocs"
source: "https://console.groq.com/docs/openai"
author:
published:
created: 2025-05-08
description: "Learn how to use OpenAI's client libraries with Groq API, including configuration, supported features, and limitations."
tags:
  - "clippings"
---
We designed Groq API to be mostly compatible with OpenAI's client libraries, making it easy to configure your existing applications to run on Groq and try our inference speed.

We also have our own [Groq Python and Groq TypeScript libraries](https://console.groq.com/docs/libraries) that we encourage you to use.

To start using Groq with OpenAI's client libraries, pass your Groq API key to the `api_key` parameter and change the `base_url` to `https://api.groq.com/openai/v1`:

```python
import os
import openai

client = openai.OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ.get("GROQ_API_KEY")
)
```

  

You can find your API key [here](https://console.groq.com/keys).

Note that although Groq API is mostly OpenAI compatible, there are a few features we don't support just yet:

The following fields are currently not supported and will result in a 400 error (yikes) if they are supplied:

- `logprobs`
- `logit_bias`
- `top_logprobs`
- `messages[].name`
- If `N` is supplied, it must be equal to 1.

If you set a `temperature` value of 0, it will be converted to `1e-8`. If you run into any issues, please try setting the value to a float32 `> 0` and `<= 2`.

The following values are not supported:

- `vtt`
- `srt`

If you'd like to see support for such features as the above on Groq API, please reach out to us and let us know by submitting a "Feature Request" via "Chat with us" located on the left. We really value your feedback and would love to hear from you! 🤩

x1.00

\>

<

\>>

<<

O