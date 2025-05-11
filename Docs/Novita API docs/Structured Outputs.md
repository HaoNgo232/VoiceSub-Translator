---
title: "Structured Outputs"
source: "https://novita.ai/docs/guides/llm-structured-outputs"
author:
  - "[[Documentation]]"
published:
created: 2025-05-08
description:
tags:
  - "clippings"
---
`Structured Outputs` enables the model to generate responses that adhere to your supplied [JSON Schema](https://json-schema.org/specification).

## Supported Models

The following models support `Structured Outputs`:

- qwen/qwen2.5-vl-72b-instruct
- google/gemma-3-27b-it
- deepseek/deepseek-r1-distill-llama-8b

## Quick Start Guide

This guide demonstrates how to use `Structured Outputs` ability to generate the JSON response via `json_schema` response format. We will walk through a complete Python code example.

### 1\. Initialize the Client

First, you need to initialize the client with your Novita API key.

### 2\. Define the JSON schema

This example creates a schema for extracting expense information from the user’s input.

```python
# Define system prompt for expense tracking.
system_prompt = """You are an expense tracking assistant. 
Extract expense information from the user's input and format it according to the provided schema."""

# Define JSON schema for structured response.
response_format = {
    "type": "json_schema",
    "json_schema": {
        "name": "expense_tracking_schema",
        "schema": {
            "type": "object",
            "properties": {
                "expenses": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "description": {
                                "type": "string",
                                "description": "Description of the expense"
                            },
                            "amount": {
                                "type": "number",
                                "description": "Amount spent in dollars"
                            },
                            "date": {
                                "type": "string",
                                "description": "When the expense occurred"
                            },
                            "category": {
                                "type": "string",
                                "description": "Category of expense (e.g., food, office, travel)"
                            }
                        },
                        "required": [
                            "description",
                            "amount"
                        ]
                    }
                },
                "total": {
                    "type": "number",
                    "description": "Total amount of all expenses"
                }
            },
            "required": [
                "expenses",
                "total"
            ],
        },
    },
}
```

### 3\. Request chat completion API

Now, make the chat completion request to the Novita endpoint.

This request includes the `response_format` parameter, defining the JSON schema we defined in the previous step.

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

# Go to the [Models](https://novita.ai/models) page to see the models that support \`Structured Outputs\`.
model = "mistralai/mistral-7b-instruct"

# Example of using JSON Schema for structured output
# This example creates a schema for extracting expense information

# Define system prompt for expense tracking
system_prompt = """You are an expense tracking assistant. 
Extract expense information from the user's input and format it according to the provided schema."""

# Define JSON schema for structured response
response_format = {
    "type": "json_schema",
    "json_schema": {
        "name": "expense_tracking_schema",
        "schema": {
            "type": "object",
            "properties": {
                "expenses": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "description": {
                                "type": "string",
                                "description": "Description of the expense"
                            },
                            "amount": {
                                "type": "number",
                                "description": "Amount spent in dollars"
                            },
                            "date": {
                                "type": "string",
                                "description": "When the expense occurred"
                            },
                            "category": {
                                "type": "string",
                                "description": "Category of expense (e.g., food, office, travel)"
                            }
                        },
                        "required": [
                            "description",
                            "amount"
                        ]
                    }
                },
                "total": {
                    "type": "number",
                    "description": "Total amount of all expenses"
                }
            },
            "required": [
                "expenses",
                "total"
            ],
        },
    },
}

chat_completion = client.chat.completions.create(
    model=model,
    messages=[
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": """I spent $120 on dinner at an Italian restaurant last Friday with my colleagues.
Also bought office supplies for $45 on Monday.""",
        },
    ],
    max_tokens=1024,
    temperature=0.8,
    stream=False,
    response_format=response_format,
)

response_content = chat_completion.choices[0].message.content

# Parse and prettify the JSON
try:
    json_response = json.loads(response_content)
    prettified_json = json.dumps(json_response, indent=2)
    print(prettified_json)
except json.JSONDecodeError:
    print("Could not parse response as JSON. Raw response:")
    print(response_content)
```

x1.00

\>

<

\>>

<<

O