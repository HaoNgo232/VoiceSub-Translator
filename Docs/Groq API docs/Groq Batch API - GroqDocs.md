---
title: "Groq Batch API - GroqDocs"
source: "https://console.groq.com/docs/batch"
author:
published:
created: 2025-05-08
description: "Learn how to process large-scale workloads asynchronously and cost-effectively with the Groq Batch API for chat, audio, and translation tasks."
tags:
  - "clippings"
---
Process large-scale workloads asynchronously with our Batch API.

Batch processing lets you run thousands of API requests at scale by submitting your workload as an asynchronous batch of requests to Groq with 25% lower cost (50% off from now until end of May 2025), no impact to your standard rate limits, and 24-hour to 7 day processing window.

While some of your use cases may require synchronous API requests, asynchronous batch processing is perfect for use cases that don't need immediate reponses or for processing a large number of queries that standard rate limits cannot handle, such as processing large datasets, generating content in bulk, and running evaluations.

Compared to using our synchronous API endpoints, our Batch API has:

- **Higher rate limits:** Process thousands of requests per batch with no impact on your standard API rate limits
- **Cost efficiency:** 25% cost discount compared to synchronous APIs (50% off now until end of May 2025)

The Batch API can currently be used to execute queries for chat completion (both text and vision), audio transcription, and audio translation inputs with the following models:

- `mistral-saba-24b`
- `llama-3.3-70b-versatile`
- `deepseek-r1-distill-llama-70b`
- `llama-3.1-8b-instant`
- `meta-llama/llama-4-scout-17b-16e-instruct`
- `meta-llama/llama-4-maverick-17b-128e-instruct`

Pricing is at a 25% cost discount compared to [synchronous API pricing (50% off now until end of May 2025).](https://groq.com/pricing)

Our Batch API endpoints allow you to collect a group of requests into a single file, kick off a batch processing job to execute the requests within your file, query for the status of your batch, and eventually retrieve the results when your batch is complete.

Multiple batch jobs can be submitted at once.

Each batch has a processing window, during which we'll process as many requests as our capacity allows while maintaining service quality for all users. We allow for setting a batch window from 24 hours to 7 days and recommend setting a longer batch window allow us more time to complete your batch jobs instead of expiring them.

A batch is composed of a list of API requests and every batch job starts with a JSON Lines (JSONL) file that contains the requests you want processed. Each line in this file represents a single API call.

The Groq Batch API currently supports:

- Chat completion requests through [`/v1/chat/completions`](https://console.groq.com/docs/text-chat)
- Audio transcription requests through [`/v1/audio/transcriptions`](https://console.groq.com/docs/speech-to-text)
- Audio translation requests through [`/v1/audio/translations`](https://console.groq.com/docs/speech-to-text)

The structure for each line must include:

- `custom_id`: Your unique identifier for tracking the batch request
- `method`: The HTTP method (currently `POST` only)
- `url`: The API endpoint to call (one of: `/v1/chat/completions`, `/v1/audio/transcriptions`, or `/v1/audio/translations`)
- `body`: The parameters of your request matching our synchronous API format. See our API Reference [here.](https://console.groq.com/docs/api-reference#chat-create)

The following is an example of a JSONL batch file with different types of requests:

```json
{"custom_id": "request-1", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "llama-3.1-8b-instant", "messages": [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "What is 2+2?"}]}}
{"custom_id": "request-2", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "llama-3.1-8b-instant", "messages": [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "What is 2+3?"}]}}
{"custom_id": "request-3", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "llama-3.1-8b-instant", "messages": [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "count up to 1000000. starting with 1, 2, 3. print all the numbers, do not stop until you get to 1000000."}]}}
```

If you're familiar with making synchronous API calls, converting them to batch format is straightforward. Here's how a regular API call transforms into a batch request:

```json
# Your typical synchronous API call in Python:
response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "user", "content": "What is quantum computing?"}
    ]
)

# The same call in batch format (must be on a single line as JSONL):
{"custom_id": "quantum-1", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": "What is quantum computing?"}]}}
```

Upload your `.jsonl` batch file using the Files API endpoint for when kicking off your batch job:

**Note:** The Files API currently only supports `.jsonl` files 50,000 lines or less and up to maximum of 200MB in size. There is no limit for the number of batch jobs you can submit. We recommend submitting multiple shorter batch files for a better chance of completion.

```
1
import os
2
from groq import Groq
3

4
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
5

6
file_path = "batch_file.jsonl"
7
response = client.files.create(file=open(file_path, "rb"), purpose="batch")
8

9
print(response)
```

You will receive a JSON response that contains the ID (`id`) for your file object that you will then use to create your batch job:

```json
{
    "id":"file_01jh6x76wtemjr74t1fh0faj5t",
    "object":"file",
    "bytes":966,
    "created_at":1736472501,
    "filename":"input_file.jsonl",
    "purpose":"batch"
}
```

Once you've uploaded your `.jsonl` file, you can use the file object ID (in this case, `file_01jh6x76wtemjr74t1fh0faj5t` as shown in Step 2) to create a batch:

**Note:** The completion window for batch jobs can be set from to 24 hours (`24h`) to 7 days (`7d`). We recommend setting a longer batch window to have a better chance for completed batch jobs rather than expirations for when we are under heavy load.

```
1
import os
2
from groq import Groq
3

4
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
5

6
response = client.batches.create(
7
    completion_window="24h",
8
    endpoint="/v1/chat/completions",
9
    input_file_id="file_01jh6x76wtemjr74t1fh0faj5t",
10
)
11
print(response.to_json())
```

This request will return a Batch object with metadata about your batch, including the batch `id` that you can use to check the status of your batch:

```json
{
    "id":"batch_01jh6xa7reempvjyh6n3yst2zw",
    "object":"batch",
    "endpoint":"/v1/chat/completions",
    "errors":null,
    "input_file_id":"file_01jh6x76wtemjr74t1fh0faj5t",
    "completion_window":"24h",
    "status":"validating",
    "output_file_id":null,
    "error_file_id":null,
    "finalizing_at":null,
    "failed_at":null,
    "expired_at":null,
    "cancelled_at":null,
    "request_counts":{
        "total":0,
        "completed":0,
        "failed":0
    },
    "metadata":null,
    "created_at":1736472600,
    "expires_at":1736559000,
    "cancelling_at":null,
    "completed_at":null,
    "in_progress_at":null
}
```

You can check the status of a batch any time your heart desires with the batch `id` (in this case, `batch_01jh6xa7reempvjyh6n3yst2zw` from the above Batch response object), which will also return a Batch object:

```
1
import os
2
from groq import Groq
3

4
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
5

6
response = client.batches.retrieve("batch_01jh6xa7reempvjyh6n3yst2zw")
7

8
print(response.to_json())
```

The status of a given batch job can return any of the following status codes:

| Status | Description |
| --- | --- |
| `validating` | batch file is being validated before the batch processing begins |
| `failed` | batch file has failed the validation process |
| `in_progress` | batch file was successfully validated and the batch is currently being run |
| `finalizing` | batch has completed and the results are being prepared |
| `completed` | batch has been completed and the results are ready |
| `expired` | batch was not able to be completed within the processing window |
| `cancelling` | batch is being cancelled (may take up to 10 minutes) |
| `cancelled` | batch was cancelled |

When your batch job is complete, the Batch object will return an `output_file_id` and/or an `error_file_id` that you can then use to retrieve your results (as shown below in Step 5). Here's an example:

```json
{
    "id":"batch_01jh6xa7reempvjyh6n3yst2zw",
    "object":"batch",
    "endpoint":"/v1/chat/completions",
    "errors":[
        {
            "code":"invalid_method",
            "message":"Invalid value: 'GET'. Supported values are: 'POST'","param":"method",
            "line":4
        }
    ],
    "input_file_id":"file_01jh6x76wtemjr74t1fh0faj5t",
    "completion_window":"24h",
    "status":"completed",
    "output_file_id":"file_01jh6xa97be52b7pg88czwrrwb",
    "error_file_id":"file_01jh6xa9cte52a5xjnmnt5y0je",
    "finalizing_at":null,
    "failed_at":null,
    "expired_at":null,
    "cancelled_at":null,
    "request_counts":
    {
        "total":3,
        "completed":2,
        "failed":1
    },
    "metadata":null,
    "created_at":1736472600,
    "expires_at":1736559000,
    "cancelling_at":null,
    "completed_at":1736472607,
    "in_progress_at":1736472601
}
```

Now for the fun. Once the batch is complete, you can retrieve the results using the `output_file_id` from your Batch object (in this case, `file_01jh6xa97be52b7pg88czwrrwb` from the above Batch response object) and write it to a file on your machine (`batch_output.jsonl` in this case) to view them:

```
1
import os
2
from groq import Groq
3

4
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
5

6
response = client.files.content("file_01jh6xa97be52b7pg88czwrrwb")
7
response.write_to_file("batch_results.jsonl")
8
print("Batch file saved to batch_results.jsonl")
```

The output `.jsonl` file will have one response line per successful request line of your batch file. Each line includes the original `custom_id` for mapping results, a unique batch request ID, and the response:

```json
{"id": "batch_req_123", "custom_id": "my-request-1", "response": {"status_code": 200, "request_id": "req_abc", "body": {"id": "completion_xyz", "model": "llama-3.1-8b-instant", "choices": [{"index": 0, "message": {"role": "assistant", "content": "Hello!"}}], "usage": {"prompt_tokens": 20, "completion_tokens": 5, "total_tokens": 25}}}, "error": null}
```

Any failed or expired requests in the batch will have their error information written to an error file that can be accessed via the batch's `error_file_id`.

**Note:** Results may not appears in the same order as your batch request submissions. Always use the `custom_id` field to match results with your original request.

You can view all your batch jobs by making a call to `https://api.groq.com/openai/v1/batches`:

```
1
import os
2
from groq import Groq
3

4
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
5

6
response = client.batches.list()
7
print(response.to_json())
```

The Files API supports JSONL files up to 50,000 lines and 200MB in size. Multiple batch jobs can be submitted at once.

**Note:** Consider splitting very large workloads into multiple smaller batches (e.g. 1000 requests per batch) for a better chance at completion rather than expiration for when we are under heavy load.

Each batch has a processing window (24 hours to 7 days) during which we'll process as many requests as our capacity allows while maintaining service quality for all users.

We recommend setting a longer batch window for a better chance of completing your batch job rather than returning expired jobs when we are under heavy load.

Batch jobs that do not complete within their processing window will have a status of `expired`.

In cases where your batch job expires:

- You are only charged for successfully completed requests
- You can access all completed results and see which request IDs were not processed
- You can resubmit any uncompleted requests in a new batch

Input, intermediate files, and results from processed batches will be stored securely for up to 30 days in Groq's systems. You may also immediately delete once a processed batch is retrieved.

The Batch API rate limits are separate than existing per-model rate limits for synchronous requests. Using the Batch API will not consume tokens from your standard per-model limits, which means you can conveniently leverage batch processing to increase the number of tokens you process with us.

See your limits [here.](https://console.groq.com/settings/limits)

x1.00

\>

<

\>>

<<

O