---
title: "Provider Routing - Smart Multi-Provider Request Management"
source: "https://openrouter.ai/docs/features/provider-routing"
author:
  - "[[OpenRouter Documentation]]"
published:
created: 2025-05-08
description: "Route requests to the best provider"
tags:
  - "clippings"
---
OpenRouter routes requests to the best available providers for your model. By default, [requests are load balanced](https://openrouter.ai/docs/features/provider-routing#load-balancing-default-strategy) across the top providers to maximize uptime.

You can customize how your requests are routed using the `provider` object in the request body for [Chat Completions](https://openrouter.ai/docs/api-reference/chat-completion) and [Completions](https://openrouter.ai/docs/api-reference/completion).

For a complete list of valid provider names to use in the API, see the [full provider schema](https://openrouter.ai/docs/features/provider-routing#json-schema-for-provider-preferences).

The `provider` object can contain the following fields:

## Price-Based Load Balancing (Default Strategy)

For each model in your request, OpenRouter’s default behavior is to load balance requests across providers, prioritizing price.

If you are more sensitive to throughput than price, you can use the `sort` field to explicitly prioritize throughput.

When you send a request with `tools` or `tool_choice`, OpenRouter will only route to providers that support tool use. Similarly, if you set a `max_tokens`, then OpenRouter will only route to providers that support a response of that length.

Here is OpenRouter’s default load balancing strategy:

1. Prioritize providers that have not seen significant outages in the last 30 seconds.
2. For the stable providers, look at the lowest-cost candidates and select one weighted by inverse square of the price (example below).
3. Use the remaining providers as fallbacks.

##### A Load Balancing Example

If Provider A costs $1 per million tokens, Provider B costs $2, and Provider C costs $3, and Provider B recently saw a few outages.

- Your request is routed to Provider A. Provider A is 9x more likely to be first routed to Provider A than Provider C because $(1 / 3^2 = 1/9)$ (inverse square of the price).
- If Provider A fails, then Provider C will be tried next.
- If Provider C also fails, Provider B will be tried last.

If you have `sort` or `order` set in your provider preferences, load balancing will be disabled.

## Provider Sorting

As described above, OpenRouter load balances based on price, while taking uptime into account.

If you instead want to *explicitly* prioritize a particular provider attribute, you can include the `sort` field in the `provider` preferences. Load balancing will be disabled, and the router will try providers in order.

The three sort options are:

- `"price"`: prioritize lowest price
- `"throughput"`: prioritize highest throughput
- `"latency"`: prioritize lowest latency

To *always* prioritize low prices, and not apply any load balancing, set `sort` to `"price"`.

To *always* prioritize low latency, and not apply any load balancing, set `sort` to `"latency"`.

## Nitro Shortcut

You can append `:nitro` to any model slug as a shortcut to sort by throughput. This is exactly equivalent to setting `provider.sort` to `"throughput"`.

## Floor Price Shortcut

You can append `:floor` to any model slug as a shortcut to sort by price. This is exactly equivalent to setting `provider.sort` to `"price"`.

## Ordering Specific Providers

You can set the providers that OpenRouter will prioritize for your request using the `order` field.

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `order` | string\[\] | \- | List of provider names to try in order (e.g. `["Anthropic", "OpenAI"]`). |

The router will prioritize providers in this list, and in this order, for the model you’re using. If you don’t set this field, the router will [load balance](https://openrouter.ai/docs/features/provider-routing#load-balancing-default-strategy) across the top providers to maximize uptime.

OpenRouter will try them one at a time and proceed to other providers if none are operational. If you don’t want to allow any other providers, you should [disable fallbacks](https://openrouter.ai/docs/features/provider-routing#disabling-fallbacks) as well.

### Example: Specifying providers with fallbacks

This example skips over OpenAI (which doesn’t host Mixtral), tries Together, and then falls back to the normal list of providers on OpenRouter:

### Example: Specifying providers with fallbacks disabled

Here’s an example with `allow_fallbacks` set to `false` that skips over OpenAI (which doesn’t host Mixtral), tries Together, and then fails if Together fails:

## Requiring Providers to Support All Parameters

You can restrict requests only to providers that support all parameters in your request using the `require_parameters` field.

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `require_parameters` | boolean | `false` | Only use providers that support all parameters in your request. |

With the default routing strategy, providers that don’t support all the [LLM parameters](https://openrouter.ai/docs/api-reference/parameters) specified in your request can still receive the request, but will ignore unknown parameters. When you set `require_parameters` to `true`, the request won’t even be routed to that provider.

### Example: Excluding providers that don’t support JSON formatting

For example, to only use providers that support JSON formatting:

## Requiring Providers to Comply with Data Policies

You can restrict requests only to providers that comply with your data policies using the `data_collection` field.

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `data_collection` | ”allow” \| “deny" | "allow” | Control whether to use providers that may store data. |

- `allow`: (default) allow providers which store user data non-transiently and may train on it
- `deny`: use only providers which do not collect user data

Some model providers may log prompts, so we display them with a **Data Policy** tag on model pages. This is not a definitive source of third party data policies, but represents our best knowledge.

### Example: Excluding providers that don’t comply with data policies

To exclude providers that don’t comply with your data policies, set `data_collection` to `deny`:

## Disabling Fallbacks

To guarantee that your request is only served by the top (lowest-cost) provider, you can disable fallbacks.

This is combined with the `order` field from [Ordering Specific Providers](https://openrouter.ai/docs/features/provider-routing#ordering-specific-providers) to restrict the providers that OpenRouter will prioritize to just your chosen list.

## Allowing Only Specific Providers

You can allow only specific providers for a request by setting the `only` field in the `provider` object.

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `only` | string\[\] | \- | List of provider names to allow for this request. |

Only allowing some providers may significantly reduce fallback options and limit request recovery.

##### Account-Wide Allowed Providers

You can allow providers for all account requests by configuring your [preferences](https://openrouter.ai/settings/preferences). This configuration applies to all API requests and chatroom messages.

Note that when you allow providers for a specific request, the list of allowed providers is merged with your account-wide allowed providers.

### Example: Allowing Azure for a request calling GPT-4 Omni

Here’s an example that will only use Azure for a request calling GPT-4 Omni:

## Ignoring Providers

You can ignore providers for a request by setting the `ignore` field in the `provider` object.

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `ignore` | string\[\] | \- | List of provider names to skip for this request. |

Ignoring multiple providers may significantly reduce fallback options and limit request recovery.

##### Account-Wide Ignored Providers

You can ignore providers for all account requests by configuring your [preferences](https://openrouter.ai/settings/preferences). This configuration applies to all API requests and chatroom messages.

Note that when you ignore providers for a specific request, the list of ignored providers is merged with your account-wide ignored providers.

### Example: Ignoring Azure for a request calling GPT-4 Omni

Here’s an example that will ignore Azure for a request calling GPT-4 Omni:

## Quantization

Quantization reduces model size and computational requirements while aiming to preserve performance. Most LLMs today use FP16 or BF16 for training and inference, cutting memory requirements in half compared to FP32. Some optimizations use FP8 or quantization to reduce size further (e.g., INT8, INT4).

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `quantizations` | string\[\] | \- | List of quantization levels to filter by (e.g. `["int4", "int8"]`). [Learn more](https://openrouter.ai/docs/features/provider-routing#quantization) |

Quantized models may exhibit degraded performance for certain prompts, depending on the method used.

Providers can support various quantization levels for open-weight models.

### Quantization Levels

By default, requests are load-balanced across all available providers, ordered by price. To filter providers by quantization level, specify the `quantizations` field in the `provider` parameter with the following values:

- `int4`: Integer (4 bit)
- `int8`: Integer (8 bit)
- `fp4`: Floating point (4 bit)
- `fp6`: Floating point (6 bit)
- `fp8`: Floating point (8 bit)
- `fp16`: Floating point (16 bit)
- `bf16`: Brain floating point (16 bit)
- `fp32`: Floating point (32 bit)
- `unknown`: Unknown

### Example: Requesting FP8 Quantization

Here’s an example that will only use providers that support FP8 quantization:

### Max Price

To filter providers by price, specify the `max_price` field in the `provider` parameter with a JSON object specifying the highest provider pricing you will accept.

For example, the value `{"prompt": 1, "completion": 2}` will route to any provider with a price of `<= $1/m` prompt tokens, and `<= $2/m` completion tokens or less.

Some providers support per request pricing, in which case you can use the `request` attribute of max\_price. Lastly, `image` is also available, which specifies the max price per image you will accept.

Practically, this field is often combined with a provider `sort` to express, for example, “Use the provider with the highest throughput, as long as it doesn’t cost more than `$x/m` tokens.”

## Terms of Service

You can view the terms of service for each provider below. You may not violate the terms of service or policies of third-party providers that power the models on OpenRouter.

- `AI21`: [https://www.ai21.com/terms-of-service/](https://www.ai21.com/terms-of-service/)
- `AionLabs`: [https://www.aionlabs.ai/terms/](https://www.aionlabs.ai/terms/)
- `Alibaba`: [https://www.alibabacloud.com/help/en/legal/latest/alibaba-cloud-international-website-product-terms-of-service-v-3-8-0](https://www.alibabacloud.com/help/en/legal/latest/alibaba-cloud-international-website-product-terms-of-service-v-3-8-0)
- `Amazon Bedrock`: [https://aws.amazon.com/service-terms/](https://aws.amazon.com/service-terms/)
- `Anthropic`: [https://www.anthropic.com/legal/commercial-terms](https://www.anthropic.com/legal/commercial-terms)
- `Atoma`: [https://atoma.network/terms\_of\_service](https://atoma.network/terms_of_service)
- `Avian.io`: [https://avian.io/terms](https://avian.io/terms)
- `Azure`: [https://www.microsoft.com/en-us/legal/terms-of-use?oneroute=true](https://www.microsoft.com/en-us/legal/terms-of-use?oneroute=true)
- `CentML`: [https://centml.ai/terms-of-service/](https://centml.ai/terms-of-service/)
- `Cerebras`: [https://www.cerebras.ai/terms-of-service](https://www.cerebras.ai/terms-of-service)
- `Chutes`: [https://chutes.ai/tos](https://chutes.ai/tos)
- `Cloudflare`: [https://www.cloudflare.com/service-specific-terms-developer-platform/#developer-platform-terms](https://www.cloudflare.com/service-specific-terms-developer-platform/#developer-platform-terms)
- `Cohere`: [https://cohere.com/terms-of-use](https://cohere.com/terms-of-use)
- `Crusoe`: [https://legal.crusoe.ai/open-router#managed-inference-tos-open-router](https://legal.crusoe.ai/open-router#managed-inference-tos-open-router)
- `DeepInfra`: [https://deepinfra.com/terms](https://deepinfra.com/terms)
- `DeepSeek`: [https://chat.deepseek.com/downloads/DeepSeek%20Terms%20of%20Use.html](https://chat.deepseek.com/downloads/DeepSeek%20Terms%20of%20Use.html)
- `Enfer`: [https://enfer.ai/privacy-policy](https://enfer.ai/privacy-policy)
- `Featherless`: [https://featherless.ai/terms](https://featherless.ai/terms)
- `Fireworks`: [https://fireworks.ai/terms-of-service](https://fireworks.ai/terms-of-service)
- `Friendli`: [https://friendli.ai/terms-of-service](https://friendli.ai/terms-of-service)
- `GMICloud`: [https://docs.gmicloud.ai/privacy](https://docs.gmicloud.ai/privacy)
- `Google Vertex`: [https://cloud.google.com/terms/](https://cloud.google.com/terms/)
- `Google AI Studio`: [https://cloud.google.com/terms/](https://cloud.google.com/terms/)
- `Groq`: [https://groq.com/terms-of-use/](https://groq.com/terms-of-use/)
- `Hyperbolic`: [https://hyperbolic.xyz/terms](https://hyperbolic.xyz/terms)
- `Inception`: [https://www.inceptionlabs.ai/terms](https://www.inceptionlabs.ai/terms)
- `inference.net`: [https://inference.net/terms-of-service](https://inference.net/terms-of-service)
- `Infermatic`: [https://infermatic.ai/terms-and-conditions/](https://infermatic.ai/terms-and-conditions/)
- `Inflection`: [https://developers.inflection.ai/tos](https://developers.inflection.ai/tos)
- `InoCloud`: [https://inocloud.com/terms](https://inocloud.com/terms)
- `kluster.ai`: [https://www.kluster.ai/terms-of-use](https://www.kluster.ai/terms-of-use)
- `Lambda`: [https://lambda.ai/legal/terms-of-service](https://lambda.ai/legal/terms-of-service)
- `Liquid`: [https://www.liquid.ai/terms-conditions](https://www.liquid.ai/terms-conditions)
- `Mancer`: [https://mancer.tech/terms](https://mancer.tech/terms)
- `Mancer (private)`: [https://mancer.tech/terms](https://mancer.tech/terms)
- `Minimax`: [https://www.minimax.io/platform/protocol/terms-of-service](https://www.minimax.io/platform/protocol/terms-of-service)
- `Mistral`: [https://mistral.ai/terms/#terms-of-use](https://mistral.ai/terms/#terms-of-use)
- `nCompass`: [https://ncompass.tech/terms](https://ncompass.tech/terms)
- `Nebius AI Studio`: [https://docs.nebius.com/legal/studio/terms-of-use/](https://docs.nebius.com/legal/studio/terms-of-use/)
- `NextBit`: [https://www.nextbit256.com/docs/terms-of-service](https://www.nextbit256.com/docs/terms-of-service)
- `Nineteen`: [https://nineteen.ai/tos](https://nineteen.ai/tos)
- `NovitaAI`: [https://novita.ai/legal/terms-of-service](https://novita.ai/legal/terms-of-service)
- `OpenAI`: [https://openai.com/policies/row-terms-of-use/](https://openai.com/policies/row-terms-of-use/)
- `OpenInference`: [https://www.openinference.xyz/terms](https://www.openinference.xyz/terms)
- `Parasail`: [https://www.parasail.io/legal/terms](https://www.parasail.io/legal/terms)
- `Perplexity`: [https://www.perplexity.ai/hub/legal/perplexity-api-terms-of-service](https://www.perplexity.ai/hub/legal/perplexity-api-terms-of-service)
- `Phala`: [https://red-pill.ai/terms](https://red-pill.ai/terms)
- `SambaNova`: [https://sambanova.ai/terms-and-conditions](https://sambanova.ai/terms-and-conditions)
- `Targon`: [https://targon.com/terms](https://targon.com/terms)
- `Together`: [https://www.together.ai/terms-of-service](https://www.together.ai/terms-of-service)
- `Ubicloud`: [https://www.ubicloud.com/docs/about/terms-of-service](https://www.ubicloud.com/docs/about/terms-of-service)
- `Venice`: [https://venice.ai/legal/tos](https://venice.ai/legal/tos)
- `xAI`: [https://x.ai/legal/terms-of-service](https://x.ai/legal/terms-of-service)

## JSON Schema for Provider Preferences

For a complete list of options, see this JSON schema:

```
1{
2    "$ref": "#/definitions/Provider Preferences Schema",
3    "definitions": {
4      "Provider Preferences Schema": {
5        "type": "object",
6        "properties": {
7          "allow_fallbacks": {
8            "type": [
9              "boolean",
10              "null"
11            ],
12            "description": "Whether to allow backup providers to serve requests\n- true: (default) when the primary provider (or your custom providers in \"order\") is unavailable, use the next best provider.\n- false: use only the primary/custom provider, and return the upstream error if it's unavailable.\n"
13          },
14          "require_parameters": {
15            "type": [
16              "boolean",
17              "null"
18            ],
19            "description": "Whether to filter providers to only those that support the parameters you've provided. If this setting is omitted or set to false, then providers will receive only the parameters they support, and ignore the rest."
20          },
21          "data_collection": {
22            "anyOf": [
23              {
24                "type": "string",
25                "enum": [
26                  "deny",
27                  "allow"
28                ]
29              },
30              {
31                "type": "null"
32              }
33            ],
34            "description": "Data collection setting. If no available model provider meets the requirement, your request will return an error.\n- allow: (default) allow providers which store user data non-transiently and may train on it\n- deny: use only providers which do not collect user data.\n"
35          },
36          "order": {
37            "anyOf": [
38              {
39                "type": "array",
40                "items": {
41                  "type": "string",
42                  "enum": [
43                    "AnyScale",
44                    "HuggingFace",
45                    "Hyperbolic 2",
46                    "Lepton",
47                    "Lynn 2",
48                    "Lynn",
49                    "Modal",
50                    "OctoAI",
51                    "Recursal",
52                    "Reflection",
53                    "Replicate",
54                    "SambaNova 2",
55                    "SF Compute",
56                    "Together 2",
57                    "01.AI",
58                    "AI21",
59                    "AionLabs",
60                    "Alibaba",
61                    "Amazon Bedrock",
62                    "Anthropic",
63                    "Atoma",
64                    "Avian",
65                    "Azure",
66                    "Cent-ML",
67                    "Cerebras",
68                    "Chutes",
69                    "Cloudflare",
70                    "Cohere",
71                    "Crusoe",
72                    "DeepInfra",
73                    "DeepSeek",
74                    "Enfer",
75                    "Featherless",
76                    "Fireworks",
77                    "Friendli",
78                    "GMICloud",
79                    "Google",
80                    "Google AI Studio",
81                    "Groq",
82                    "Hyperbolic",
83                    "Inception",
84                    "InferenceNet",
85                    "Infermatic",
86                    "Inflection",
87                    "InoCloud",
88                    "Kluster",
89                    "Lambda",
90                    "Liquid",
91                    "Mancer",
92                    "Mancer 2",
93                    "Minimax",
94                    "Mistral",
95                    "NCompass",
96                    "Nebius",
97                    "NextBit",
98                    "Nineteen",
99                    "Novita",
100                    "OpenAI",
101                    "OpenInference",
102                    "Parasail",
103                    "Perplexity",
104                    "Phala",
105                    "SambaNova",
106                    "Stealth",
107                    "Targon",
108                    "Together",
109                    "Ubicloud",
110                    "Venice",
111                    "xAI"
112                  ]
113                }
114              },
115              {
116                "type": "null"
117              }
118            ],
119            "description": "An ordered list of provider names. The router will attempt to use the first provider in the subset of this list that supports your requested model, and fall back to the next if it is unavailable. If no providers are available, the request will fail with an error message."
120          },
121          "only": {
122            "anyOf": [
123              {
124                "type": "array",
125                "items": {
126                  "type": "string",
127                  "enum": [
128                    "AnyScale",
129                    "HuggingFace",
130                    "Hyperbolic 2",
131                    "Lepton",
132                    "Lynn 2",
133                    "Lynn",
134                    "Modal",
135                    "OctoAI",
136                    "Recursal",
137                    "Reflection",
138                    "Replicate",
139                    "SambaNova 2",
140                    "SF Compute",
141                    "Together 2",
142                    "01.AI",
143                    "AI21",
144                    "AionLabs",
145                    "Alibaba",
146                    "Amazon Bedrock",
147                    "Anthropic",
148                    "Atoma",
149                    "Avian",
150                    "Azure",
151                    "Cent-ML",
152                    "Cerebras",
153                    "Chutes",
154                    "Cloudflare",
155                    "Cohere",
156                    "Crusoe",
157                    "DeepInfra",
158                    "DeepSeek",
159                    "Enfer",
160                    "Featherless",
161                    "Fireworks",
162                    "Friendli",
163                    "GMICloud",
164                    "Google",
165                    "Google AI Studio",
166                    "Groq",
167                    "Hyperbolic",
168                    "Inception",
169                    "InferenceNet",
170                    "Infermatic",
171                    "Inflection",
172                    "InoCloud",
173                    "Kluster",
174                    "Lambda",
175                    "Liquid",
176                    "Mancer",
177                    "Mancer 2",
178                    "Minimax",
179                    "Mistral",
180                    "NCompass",
181                    "Nebius",
182                    "NextBit",
183                    "Nineteen",
184                    "Novita",
185                    "OpenAI",
186                    "OpenInference",
187                    "Parasail",
188                    "Perplexity",
189                    "Phala",
190                    "SambaNova",
191                    "Stealth",
192                    "Targon",
193                    "Together",
194                    "Ubicloud",
195                    "Venice",
196                    "xAI"
197                  ]
198                }
199              },
200              {
201                "type": "null"
202              }
203            ],
204            "description": "List of provider names to allow. If provided, this list is merged with your account-wide allowed provider settings for this request."
205          },
206          "ignore": {
207            "anyOf": [
208              {
209                "type": "array",
210                "items": {
211                  "type": "string",
212                  "enum": [
213                    "AnyScale",
214                    "HuggingFace",
215                    "Hyperbolic 2",
216                    "Lepton",
217                    "Lynn 2",
218                    "Lynn",
219                    "Modal",
220                    "OctoAI",
221                    "Recursal",
222                    "Reflection",
223                    "Replicate",
224                    "SambaNova 2",
225                    "SF Compute",
226                    "Together 2",
227                    "01.AI",
228                    "AI21",
229                    "AionLabs",
230                    "Alibaba",
231                    "Amazon Bedrock",
232                    "Anthropic",
233                    "Atoma",
234                    "Avian",
235                    "Azure",
236                    "Cent-ML",
237                    "Cerebras",
238                    "Chutes",
239                    "Cloudflare",
240                    "Cohere",
241                    "Crusoe",
242                    "DeepInfra",
243                    "DeepSeek",
244                    "Enfer",
245                    "Featherless",
246                    "Fireworks",
247                    "Friendli",
248                    "GMICloud",
249                    "Google",
250                    "Google AI Studio",
251                    "Groq",
252                    "Hyperbolic",
253                    "Inception",
254                    "InferenceNet",
255                    "Infermatic",
256                    "Inflection",
257                    "InoCloud",
258                    "Kluster",
259                    "Lambda",
260                    "Liquid",
261                    "Mancer",
262                    "Mancer 2",
263                    "Minimax",
264                    "Mistral",
265                    "NCompass",
266                    "Nebius",
267                    "NextBit",
268                    "Nineteen",
269                    "Novita",
270                    "OpenAI",
271                    "OpenInference",
272                    "Parasail",
273                    "Perplexity",
274                    "Phala",
275                    "SambaNova",
276                    "Stealth",
277                    "Targon",
278                    "Together",
279                    "Ubicloud",
280                    "Venice",
281                    "xAI"
282                  ]
283                }
284              },
285              {
286                "type": "null"
287              }
288            ],
289            "description": "List of provider names to ignore. If provided, this list is merged with your account-wide ignored provider settings for this request."
290          },
291          "quantizations": {
292            "anyOf": [
293              {
294                "type": "array",
295                "items": {
296                  "type": "string",
297                  "enum": [
298                    "int4",
299                    "int8",
300                    "fp4",
301                    "fp6",
302                    "fp8",
303                    "fp16",
304                    "bf16",
305                    "fp32",
306                    "unknown"
307                  ]
308                }
309              },
310              {
311                "type": "null"
312              }
313            ],
314            "description": "A list of quantization levels to filter the provider by."
315          },
316          "sort": {
317            "anyOf": [
318              {
319                "type": "string",
320                "enum": [
321                  "price",
322                  "throughput",
323                  "latency"
324                ]
325              },
326              {
327                "type": "null"
328              }
329            ],
330            "description": "The sorting strategy to use for this request, if \"order\" is not specified. When set, no load balancing is performed."
331          },
332          "max_price": {
333            "type": "object",
334            "properties": {
335              "prompt": {
336                "anyOf": [
337                  {
338                    "type": "number"
339                  },
340                  {
341                    "type": "string"
342                  },
343                  {}
344                ]
345              },
346              "completion": {
347                "$ref": "#/definitions/Provider Preferences Schema/properties/max_price/properties/prompt"
348              },
349              "image": {
350                "$ref": "#/definitions/Provider Preferences Schema/properties/max_price/properties/prompt"
351              },
352              "request": {
353                "$ref": "#/definitions/Provider Preferences Schema/properties/max_price/properties/prompt"
354              }
355            },
356            "additionalProperties": false,
357            "description": "The object specifying the maximum price you want to pay for this request. USD price per million tokens, for prompt and completion."
358          }
359        },
360        "additionalProperties": false
361      }
362    },
363    "$schema": "http://json-schema.org/draft-07/schema#"
364  }
```

x1.00

\>

<

\>>

<<

O