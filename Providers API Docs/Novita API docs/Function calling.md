---
title: "Function calling"
source: "https://novita.ai/docs/guides/llm-function-calling"
author:
  - "[[Documentation]]"
published:
created: 2025-05-08
description:
tags:
  - "clippings"
---
`Function Calling` empowers AI models to interact with external tools and APIs, enabling them to perform specific actions and access real-time information. This capability extends the functionality of AI models beyond simple text generation, allowing for more dynamic and practical applications.

## Supported Models

The following models support `Function Calling`:

- deepseek/deepseek-v3-0324
- deepseek/deepseek-v3-turbo
- deepseek/deepseek-r1-turbo

## Quick Start Guide

This guide demonstrates how to use Function Calling to retrieve current weather information for a user’s specified location. We will walk through a complete Python code example.

For the specific API format of Function Calling, please refer to the API reference [Create Chat Completion](https://novita.ai/docs/api-reference/model-apis-llm-create-chat-completion).

### 1\. Initialize the Client

First, you need to initialize the client with your Novita API key.

### 2\. Define the Function to Be Called

Next, define the Python function that the model can call. In this example, it’s a function to get weather information.

### 3\. Construct the API Request with Tools and User Message

Now, create the API request to the Novita endpoint. This request includes the `tools` parameter, defining the functions the model can use, and the user’s message.

**Output:**

### 4\. Respond with the Function Call Result and Get the Final Answer

The next step is to process the function call, execute the `get_weather` function, and send the result back to the model to generate the final response to the user.

**Output:**

### The Complete Code

```python
from openai import OpenAI
import json

client = OpenAI(
    base_url="https://api.novita.ai/v3/openai",
    # Get the Novita AI API Key from: https://novita.ai/settings/key-management.
    api_key="<YOUR Novita AI API Key>",
)

model = "deepseek/deepseek_v3"

# Example function to simulate fetching weather data.
def get_weather(location):
    """Retrieves the current weather for a given location."""
    print("Calling get_weather function with location: ", location)
    # In a real application, you would call an external weather API here.
    # This is a simplified example returning hardcoded data.
    return json.dumps({"location": location, "temperature": "60 degrees Fahrenheit"})

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather of an location, the user shoud supply a location first",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    }
                },
                "required": ["location"]
            },
        }
    },
]

messages = [
    {
        "role": "user",
        "content": "What is the weather in San Francisco?"
    }
]

# Let's send the request and print the response.
response = client.chat.completions.create(
    model=model,
    messages=messages,
    tools=tools,
)

# Please check if the response contains tool calls if in production.
tool_call = response.choices[0].message.tool_calls[0]
print(tool_call.model_dump())

# Ensure tool_call is defined from the previous step
if tool_call:
    # Extend conversation history with the assistant's tool call message
    messages.append(response.choices[0].message)

    function_name = tool_call.function.name
    if function_name == "get_weather":
        function_args = json.loads(tool_call.function.arguments)
        # Execute the function and get the response
        function_response = get_weather(
            location=function_args.get("location"))
        # Append the function response to the messages
        messages.append(
            {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "content": function_response,
            }
        )

    # Get the final response from the model, now with the function result
    answer_response = client.chat.completions.create(
        model=model,
        messages=messages,
        # Note: Do not include tools parameter here
    )
    print(answer_response.choices[0].message)
```

x1.00

\>

<

\>>

<<

O