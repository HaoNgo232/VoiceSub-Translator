---
title: "Quickstart - GroqDocs"
source: "https://console.groq.com/docs/quickstart"
author:
published:
created: 2025-05-08
description: "Get up and running with the Groq API in minutes: create an API key, set up your environment, and make your first request."
tags:
  - "clippings"
---
Get up and running with the Groq API in a few minutes.

Please visit [here](https://console.groq.com/keys) to create an API Key.

Configure your API key as an environment variable. This approach streamlines your API usage by eliminating the need to include your API key in each request. Moreover, it enhances security by minimizing the risk of inadvertently including your API key in your codebase.

```shell
export GROQ_API_KEY=<your-api-key-here>
```

```shell
pip install groq
```

```shell
1
import os
2

3
from groq import Groq
4

5
client = Groq(
6
    api_key=os.environ.get("GROQ_API_KEY"),
7
)
8

9
chat_completion = client.chat.completions.create(
10
    messages=[
11
        {
12
            "role": "user",
13
            "content": "Explain the importance of fast language models",
14
        }
15
    ],
16
    model="llama-3.3-70b-versatile",
17
)
18

19
print(chat_completion.choices[0].message.content)
```

Now that you have successfully received a chat completion, you can try out the other endpoints in the API.

- Check out the [Playground](https://console.groq.com/playground) to try out the Groq API in your browser
- Join our GroqCloud developer community on [Discord](https://discord.gg/groq)
- Add a how-to on your project to the [Groq API Cookbook](https://github.com/groq/groq-api-cookbook)

x1.00

\>

<

\>>

<<

O

x1.00