---
title: "Error Codes"
source: "https://inference-docs.cerebras.ai/support/error"
author:
  - "[[Cerebras Inference]]"
published:
created: 2025-05-08
description:
tags:
  - "clippings"
---
The Cerebras Inference API uses standard HTTP response status codes to indicate the success or failure of an API request. In cases of errors, the SDK throws specific exceptions that inherit from `cerebras.cloud.sdk.APIError`. This documentation outlines the error types, how to handle them, and provides examples for effective error management.

## Error Types

All errors in the Cerebras Inference API inherit from `cerebras.cloud.sdk.APIError`. The main categories of errors are:

1. `cerebras.cloud.sdk.APIConnectionError`: Raised when the library is unable to connect to the API.
2. `cerebras.cloud.sdk.APIStatusError`: Raised when the API returns a non-success status code (4xx or 5xx).

## Error Codes and Corresponding Exceptions

| Status Code | Error Type |
| --- | --- |
| 400 | BadRequestError |
| 401 | AuthenticationError |
| 403 | PermissionDeniedError |
| 404 | NotFoundError |
| 422 | UnprocessableEntityError |
| 429 | RateLimitError |
| \>=500 | InternalServerError |
| N/A | APIConnectionError |

## Handling Errors

Here’s an example of how to handle different types of errors:

## Retries

By default, certain errors are automatically retried 2 times with a short exponential backoff. These include:

- Connection errors
- 408 Request Timeout
- 409 Conflict
- 429 Rate Limit
- \>= 500 Internal errors

You can configure or disable retry settings using the `max_retries` option:

## Timeouts

Requests time out after 1 minute by default. You can configure this with a `timeout` option:

On timeout, an `APITimeoutError` is thrown. Note that requests that time out are retried twice by default.

x1.00

\>

<

\>>

<<

O

x1.00

Error Codes - Cerebras Inference