---
title: "Gọi hàm bằng Gemini API  |  Google AI for Developers"
source: "https://ai.google.dev/gemini-api/docs/function-calling?hl=vi&example=meeting"
author:
published:
created: 2025-05-08
description: "Bắt đầu sử dụng tính năng Gọi hàm bằng API Gemini"
tags:
  - "clippings"
---
Lệnh gọi hàm cho phép bạn kết nối các mô hình với các công cụ và API bên ngoài. Thay vì tạo câu trả lời văn bản, mô hình này hiểu được thời điểm gọi các hàm cụ thể và cung cấp các tham số cần thiết để thực thi các hành động trong thực tế. Điều này cho phép mô hình đóng vai trò là cầu nối giữa ngôn ngữ tự nhiên và các hành động cũng như dữ liệu trong thế giới thực. Lệnh gọi hàm có 3 trường hợp sử dụng chính:

- **Mở rộng kiến thức:** Truy cập thông tin từ các nguồn bên ngoài như cơ sở dữ liệu, API và cơ sở kiến thức.
- **Mở rộng chức năng:** Sử dụng các công cụ bên ngoài để thực hiện phép tính và mở rộng các giới hạn của mô hình, chẳng hạn như sử dụng máy tính hoặc tạo biểu đồ.
- **Thực hiện hành động:** Tương tác với các hệ thống bên ngoài bằng API, chẳng hạn như lên lịch hẹn, tạo hoá đơn, gửi email hoặc điều khiển các thiết bị nhà thông minh
```
from google import genai
 from google.genai import types

 # Define the function declaration for the model
 schedule_meeting_function = {
     "name": "schedule_meeting",
     "description": "Schedules a meeting with specified attendees at a given time and date.",
     "parameters": {
         "type": "object",
         "properties": {
             "attendees": {
                 "type": "array",
                 "items": {"type": "string"},
                 "description": "List of people attending the meeting.",
             },
             "date": {
                 "type": "string",
                 "description": "Date of the meeting (e.g., '2024-07-29')",
             },
             "time": {
                 "type": "string",
                 "description": "Time of the meeting (e.g., '15:00')",
             },
             "topic": {
                 "type": "string",
                 "description": "The subject or topic of the meeting.",
             },
         },
         "required": ["attendees", "date", "time", "topic"],
     },
 }

 # Configure the client and tools
 client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
 tools = types.Tool(function_declarations=[schedule_meeting_function])
 config = types.GenerateContentConfig(tools=[tools])

 # Send request with function declarations
 response = client.models.generate_content(
     model="gemini-2.0-flash",
     contents="Schedule a meeting with Bob and Alice for 03/14/2025 at 10:00 AM about the Q3 planning.",
     config=config,
 )

 # Check for a function call
 if response.candidates[0].content.parts[0].function_call:
     function_call = response.candidates[0].content.parts[0].function_call
     print(f"Function to call: {function_call.name}")
     print(f"Arguments: {function_call.args}")
     #  In a real app, you would call your function here:
     #  result = schedule_meeting(**function_call.args)
 else:
     print("No function call found in the response.")
     print(response.text)
```
```
import { GoogleGenAI, Type } from '@google/genai';

// Configure the client
const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

// Define the function declaration for the model
const scheduleMeetingFunctionDeclaration = {
  name: 'schedule_meeting',
  description: 'Schedules a meeting with specified attendees at a given time and date.',
  parameters: {
    type: Type.OBJECT,
    properties: {
      attendees: {
        type: Type.ARRAY,
        items: { type: Type.STRING },
        description: 'List of people attending the meeting.',
      },
      date: {
        type: Type.STRING,
        description: 'Date of the meeting (e.g., "2024-07-29")',
      },
      time: {
        type: Type.STRING,
        description: 'Time of the meeting (e.g., "15:00")',
      },
      topic: {
        type: Type.STRING,
        description: 'The subject or topic of the meeting.',
      },
    },
    required: ['attendees', 'date', 'time', 'topic'],
  },
};

// Send request with function declarations
const response = await ai.models.generateContent({
  model: 'gemini-2.0-flash',
  contents: 'Schedule a meeting with Bob and Alice for 03/27/2025 at 10:00 AM about the Q3 planning.',
  config: {
    tools: [{
      functionDeclarations: [scheduleMeetingFunctionDeclaration]
    }],
  },
});

// Check for function calls in the response
if (response.functionCalls && response.functionCalls.length > 0) {
  const functionCall = response.functionCalls[0]; // Assuming one function call
  console.log(\`Function to call: ${functionCall.name}\`);
  console.log(\`Arguments: ${JSON.stringify(functionCall.args)}\`);
  // In a real app, you would call your actual function here:
  // const result = await scheduleMeeting(functionCall.args);
} else {
  console.log("No function call found in the response.");
  console.log(response.text);
}
```
```
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=$GEMINI_API_KEY" \
  -H 'Content-Type: application/json' \
  -X POST \
  -d '{
    "contents": [
      {
        "role": "user",
        "parts": [
          {
            "text": "Schedule a meeting with Bob and Alice for 03/27/2025 at 10:00 AM about the Q3 planning."
          }
        ]
      }
    ],
    "tools": [
      {
        "functionDeclarations": [
          {
            "name": "schedule_meeting",
            "description": "Schedules a meeting with specified attendees at a given time and date.",
            "parameters": {
              "type": "object",
              "properties": {
                "attendees": {
                  "type": "array",
                  "items": {"type": "string"},
                  "description": "List of people attending the meeting."
                },
                "date": {
                  "type": "string",
                  "description": "Date of the meeting (e.g., '2024-07-29')"
                },
                "time": {
                  "type": "string",
                  "description": "Time of the meeting (e.g., '15:00')"
                },
                "topic": {
                  "type": "string",
                  "description": "The subject or topic of the meeting."
                }
              },
              "required": ["attendees", "date", "time", "topic"]
            }
          }
        ]
      }
    ]
  }'
```

## Cách hoạt động của lệnh gọi hàm

![tổng quan về lệnh gọi hàm](https://ai.google.dev/static/gemini-api/docs/images/function-calling-overview.png?hl=vi)

Lệnh gọi hàm liên quan đến hoạt động tương tác có cấu trúc giữa ứng dụng, mô hình và các hàm bên ngoài. Dưới đây là thông tin chi tiết về quy trình này:

1. **Xác định phần khai báo hàm:** Xác định phần khai báo hàm trong mã ứng dụng. Phần Khai báo hàm mô tả tên, tham số và mục đích của hàm đối với mô hình.
2. **Gọi LLM bằng nội dung khai báo hàm:** Gửi lời nhắc người dùng cùng với(các) nội dung khai báo hàm đến mô hình. Phương thức này phân tích yêu cầu và xác định xem lệnh gọi hàm có hữu ích hay không. Nếu có, hàm này sẽ phản hồi bằng một đối tượng JSON có cấu trúc.
3. **Thực thi mã hàm (Trách nhiệm của bạn):** Mô hình *không* thực thi chính hàm đó. Ứng dụng của bạn có trách nhiệm xử lý phản hồi và kiểm tra Lệnh gọi hàm, nếu
	- **Có**: Trích xuất tên và args của hàm rồi thực thi hàm tương ứng trong ứng dụng.
	- **Không:** Mô hình đã cung cấp phản hồi văn bản trực tiếp cho câu lệnh (luồng này ít được nhấn mạnh trong ví dụ nhưng là một kết quả có thể xảy ra).
4. **Tạo phản hồi thân thiện với người dùng:** Nếu một hàm đã được thực thi, hãy ghi lại kết quả và gửi lại cho mô hình trong lượt trò chuyện tiếp theo. Hàm này sẽ sử dụng kết quả để tạo một phản hồi cuối cùng, thân thiện với người dùng, kết hợp thông tin từ lệnh gọi hàm.

Bạn có thể lặp lại quy trình này nhiều lần, cho phép các lượt tương tác và quy trình làm việc phức tạp. Mô hình này cũng hỗ trợ việc gọi nhiều hàm trong một lượt ([gọi hàm song song](https://ai.google.dev/gemini-api/docs/function-calling?hl=vi#parallel_function_calling)) và theo trình tự ([gọi hàm tổng hợp](https://ai.google.dev/gemini-api/docs/function-calling?hl=vi#compositional_function_calling)).

### Bước 1: Xác định phần khai báo hàm

Xác định một hàm và phần khai báo hàm đó trong mã ứng dụng cho phép người dùng đặt giá trị ánh sáng và tạo yêu cầu API. Hàm này có thể gọi các dịch vụ hoặc API bên ngoài.

```
from google.genai import types

# Define a function that the model can call to control smart lights
set_light_values_declaration = {
    "name": "set_light_values",
    "description": "Sets the brightness and color temperature of a light.",
    "parameters": {
        "type": "object",
        "properties": {
            "brightness": {
                "type": "integer",
                "description": "Light level from 0 to 100. Zero is off and 100 is full brightness",
            },
            "color_temp": {
                "type": "string",
                "enum": ["daylight", "cool", "warm"],
                "description": "Color temperature of the light fixture, which can be \`daylight\`, \`cool\` or \`warm\`.",
            },
        },
        "required": ["brightness", "color_temp"],
    },
}

# This is the actual function that would be called based on the model's suggestion
def set_light_values(brightness: int, color_temp: str) -> dict[str, int | str]:
    """Set the brightness and color temperature of a room light. (mock API).

    Args:
        brightness: Light level from 0 to 100. Zero is off and 100 is full brightness
        color_temp: Color temperature of the light fixture, which can be \`daylight\`, \`cool\` or \`warm\`.

    Returns:
        A dictionary containing the set brightness and color temperature.
    """
    return {"brightness": brightness, "colorTemperature": color_temp}
```
```
import { Type } from '@google/genai';

// Define a function that the model can call to control smart lights
const setLightValuesFunctionDeclaration = {
  name: 'set_light_values',
  description: 'Sets the brightness and color temperature of a light.',
  parameters: {
    type: Type.OBJECT,
    properties: {
      brightness: {
        type: Type.NUMBER,
        description: 'Light level from 0 to 100. Zero is off and 100 is full brightness',
      },
      color_temp: {
        type: Type.STRING,
        enum: ['daylight', 'cool', 'warm'],
        description: 'Color temperature of the light fixture, which can be \`daylight\`, \`cool\` or \`warm\`.',
      },
    },
    required: ['brightness', 'color_temp'],
  },
};

/**
* Set the brightness and color temperature of a room light. (mock API)
* @param {number} brightness - Light level from 0 to 100. Zero is off and 100 is full brightness
* @param {string} color_temp - Color temperature of the light fixture, which can be \`daylight\`, \`cool\` or \`warm\`.
* @return {Object} A dictionary containing the set brightness and color temperature.
*/
function setLightValues(brightness, color_temp) {
  return {
    brightness: brightness,
    colorTemperature: color_temp
  };
}
```

### Bước 2: Gọi mô hình bằng các khai báo hàm

Sau khi xác định các phần khai báo hàm, bạn có thể nhắc mô hình sử dụng hàm. Phương thức này phân tích lời nhắc và nội dung khai báo hàm, sau đó quyết định phản hồi trực tiếp hoặc gọi một hàm. Nếu một hàm được gọi, đối tượng phản hồi sẽ chứa một đề xuất gọi hàm.

```
from google import genai

# Generation Config with Function Declaration
tools = types.Tool(function_declarations=[set_light_values_declaration])
config = types.GenerateContentConfig(tools=[tools])

# Configure the client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Define user prompt
contents = [
    types.Content(
        role="user", parts=[types.Part(text="Turn the lights down to a romantic level")]
    )
]

# Send request with function declarations
response = client.models.generate_content(
    model="gemini-2.0-flash", config=config, contents=contents
)

print(response.candidates[0].content.parts[0].function_call)
```
```
import { GoogleGenAI } from '@google/genai';

// Generation Config with Function Declaration
const config = {
  tools: [{
    functionDeclarations: [setLightValuesFunctionDeclaration]
  }]
};

// Configure the client
const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

// Define user prompt
const contents = [
  {
    role: 'user',
    parts: [{ text: 'Turn the lights down to a romantic level' }]
  }
];

// Send request with function declarations
const response = await ai.models.generateContent({
  model: 'gemini-2.0-flash',
  contents: contents,
  config: config
});

console.log(response.functionCalls[0]);
```

Sau đó, mô hình sẽ trả về một đối tượng `functionCall` trong giản đồ tương thích với OpenAPI, chỉ định cách gọi một hoặc nhiều hàm đã khai báo để phản hồi câu hỏi của người dùng.

```
id=None args={'color_temp': 'warm', 'brightness': 25} name='set_light_values'
```
```
{
  name: 'set_light_values',
  args: { brightness: 25, color_temp: 'warm' }
}
```

### Bước 3: Thực thi mã hàm set\_light\_values

Trích xuất thông tin chi tiết về lệnh gọi hàm từ phản hồi của mô hình, phân tích cú pháp các đối số và thực thi hàm `set_light_values` trong mã của chúng ta.

```
# Extract tool call details
tool_call = response.candidates[0].content.parts[0].function_call

if tool_call.name == "set_light_values":
    result = set_light_values(**tool_call.args)
    print(f"Function execution result: {result}")
```
```
// Extract tool call details
const tool_call = response.functionCalls[0]

let result;
if (tool_call.name === 'set_light_values') {
  result = setLightValues(tool_call.args.brightness, tool_call.args.color_temp);
  console.log(\`Function execution result: ${JSON.stringify(result)}\`);
}
```

### Bước 4: Tạo phản hồi thân thiện với người dùng bằng kết quả hàm và gọi lại mô hình

Cuối cùng, hãy gửi kết quả thực thi hàm trở lại mô hình để mô hình có thể kết hợp thông tin này vào phản hồi cuối cùng cho người dùng.

```
# Create a function response part
function_response_part = types.Part.from_function_response(
    name=tool_call.name,
    response={"result": result},
)

# Append function call and result of the function execution to contents
contents.append(types.Content(role="model", parts=[types.Part(function_call=tool_call)])) # Append the model's function call message
contents.append(types.Content(role="user", parts=[function_response_part])) # Append the function response

final_response = client.models.generate_content(
    model="gemini-2.0-flash",
    config=config,
    contents=contents,
)

print(final_response.text)
```
```
// Create a function response part
const function_response_part = {
  name: tool_call.name,
  response: { result }
}

// Append function call and result of the function execution to contents
contents.push({ role: 'model', parts: [{ functionCall: tool_call }] });
contents.push({ role: 'user', parts: [{ functionResponse: function_response_part }] });

// Get the final response from the model
const final_response = await ai.models.generateContent({
  model: 'gemini-2.0-flash',
  contents: contents,
  config: config
});

console.log(final_response.text);
```

Thao tác này sẽ hoàn tất quy trình gọi hàm. Mô hình đã sử dụng thành công hàm `set_light_values` để thực hiện hành động yêu cầu của người dùng.

## Khai báo hàm

Khi triển khai lệnh gọi hàm trong lời nhắc, bạn sẽ tạo một đối tượng `tools` chứa một hoặc nhiều *`function declarations`*. Bạn xác định các hàm bằng JSON, cụ thể là bằng một [tập hợp con chọn lọc](https://ai.google.dev/api/caching?hl=vi#Schema) của định dạng [giản đồ OpenAPI](https://spec.openapis.org/oas/v3.0.3#schemawr). Một phần khai báo hàm có thể bao gồm các tham số sau:

- `name` (chuỗi): Tên duy nhất cho hàm (`get_weather_forecast`, `send_email`). Sử dụng tên mô tả không có dấu cách hoặc ký tự đặc biệt (sử dụng dấu gạch dưới hoặc viết hoa chữ cái đầu tiên).
- `description` (chuỗi): Nội dung giải thích rõ ràng và chi tiết về mục đích và chức năng của hàm. Điều này rất quan trọng để mô hình hiểu được thời điểm sử dụng hàm. Hãy nêu rõ và đưa ra ví dụ nếu hữu ích ("Tìm rạp chiếu phim dựa trên vị trí và tên phim (không bắt buộc) đang chiếu tại rạp").
- `parameters` (đối tượng): Xác định các tham số đầu vào mà hàm dự kiến.
	- `type` (chuỗi): Chỉ định loại dữ liệu tổng thể, chẳng hạn như `object`.
	- `properties` (đối tượng): Liệt kê các tham số riêng lẻ, mỗi tham số có:
		- `type` (chuỗi): Loại dữ liệu của tham số, chẳng hạn như `string`, `integer`, `boolean, array`.
		- `description` (chuỗi): Nội dung mô tả mục đích và định dạng của thông số. Cung cấp ví dụ và quy tắc ràng buộc ("Thành phố và tiểu bang, ví dụ: "San Francisco, CA" hoặc mã zip, ví dụ: '95616'.").
		- `enum` (mảng, không bắt buộc): Nếu các giá trị tham số thuộc một tập hợp cố định, hãy sử dụng "enum" để liệt kê các giá trị được phép thay vì chỉ mô tả các giá trị đó trong phần mô tả. Điều này giúp cải thiện độ chính xác ("enum": \["daylight", "cool", "warm"\]).
	- `required` (mảng): Một mảng chuỗi liệt kê các tên tham số bắt buộc để hàm hoạt động.

## Gọi hàm song song

Ngoài việc gọi hàm một lượt, bạn cũng có thể gọi nhiều hàm cùng một lúc. Lệnh gọi hàm song song cho phép bạn thực thi nhiều hàm cùng một lúc và được dùng khi các hàm không phụ thuộc lẫn nhau. Điều này hữu ích trong các trường hợp như thu thập dữ liệu từ nhiều nguồn độc lập, chẳng hạn như truy xuất thông tin chi tiết về khách hàng từ nhiều cơ sở dữ liệu hoặc kiểm tra mức tồn kho trên nhiều kho hàng hoặc thực hiện nhiều thao tác như chuyển đổi căn hộ của bạn thành một vũ trường.

```
power_disco_ball = {
    "name": "power_disco_ball",
    "description": "Powers the spinning disco ball.",
    "parameters": {
        "type": "object",
        "properties": {
            "power": {
                "type": "boolean",
                "description": "Whether to turn the disco ball on or off.",
            }
        },
        "required": ["power"],
    },
}

start_music = {
    "name": "start_music",
    "description": "Play some music matching the specified parameters.",
    "parameters": {
        "type": "object",
        "properties": {
            "energetic": {
                "type": "boolean",
                "description": "Whether the music is energetic or not.",
            },
            "loud": {
                "type": "boolean",
                "description": "Whether the music is loud or not.",
            },
        },
        "required": ["energetic", "loud"],
    },
}

dim_lights = {
    "name": "dim_lights",
    "description": "Dim the lights.",
    "parameters": {
        "type": "object",
        "properties": {
            "brightness": {
                "type": "number",
                "description": "The brightness of the lights, 0.0 is off, 1.0 is full.",
            }
        },
        "required": ["brightness"],
    },
}
```
```
import { Type } from '@google/genai';

const powerDiscoBall = {
  name: 'power_disco_ball',
  description: 'Powers the spinning disco ball.',
  parameters: {
    type: Type.OBJECT,
    properties: {
      power: {
        type: Type.BOOLEAN,
        description: 'Whether to turn the disco ball on or off.'
      }
    },
    required: ['power']
  }
};

const startMusic = {
  name: 'start_music',
  description: 'Play some music matching the specified parameters.',
  parameters: {
    type: Type.OBJECT,
    properties: {
      energetic: {
        type: Type.BOOLEAN,
        description: 'Whether the music is energetic or not.'
      },
      loud: {
        type: Type.BOOLEAN,
        description: 'Whether the music is loud or not.'
      }
    },
    required: ['energetic', 'loud']
  }
};

const dimLights = {
  name: 'dim_lights',
  description: 'Dim the lights.',
  parameters: {
    type: Type.OBJECT,
    properties: {
      brightness: {
        type: Type.NUMBER,
        description: 'The brightness of the lights, 0.0 is off, 1.0 is full.'
      }
    },
    required: ['brightness']
  }
};
```

Gọi mô hình bằng một hướng dẫn có thể sử dụng tất cả các công cụ được chỉ định. Ví dụ này sử dụng `tool_config`. Để tìm hiểu thêm, bạn có thể đọc bài viết về [cách định cấu hình lệnh gọi hàm](https://ai.google.dev/gemini-api/docs/function-calling?hl=vi#function_calling_modes).

```
from google import genai
from google.genai import types

# Set up function declarations
house_tools = [
    types.Tool(function_declarations=[power_disco_ball, start_music, dim_lights])
]

config = {
    "tools": house_tools,
    "automatic_function_calling": {"disable": True},
    # Force the model to call 'any' function, instead of chatting.
    "tool_config": {"function_calling_config": {"mode": "any"}},
}

# Configure the client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

chat = client.chats.create(model="gemini-2.0-flash", config=config)
response = chat.send_message("Turn this place into a party!")

# Print out each of the function calls requested from this single call
print("Example 1: Forced function calling")
for fn in response.function_calls:
    args = ", ".join(f"{key}={val}" for key, val in fn.args.items())
    print(f"{fn.name}({args})")
```
```
import { GoogleGenAI } from '@google/genai';

// Set up function declarations
const houseFns = [powerDiscoBall, startMusic, dimLights];

const config = {
    tools: [{
        functionDeclarations: houseFns
    }],
    // Force the model to call 'any' function, instead of chatting.
    toolConfig: {
        functionCallingConfig: {
        mode: 'any'
        }
    }
};

// Configure the client
const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

// Create a chat session
const chat = ai.chats.create({
    model: 'gemini-2.0-flash',
    config: config
});
const response = await chat.sendMessage({message: 'Turn this place into a party!'});

// Print out each of the function calls requested from this single call
console.log("Example 1: Forced function calling");
for (const fn of response.functionCalls) {
    const args = Object.entries(fn.args)
        .map(([key, val]) => \`${key}=${val}\`)
        .join(', ');
    console.log(\`${fn.name}(${args})\`);
}
```

Mỗi kết quả in phản ánh một lệnh gọi hàm mà mô hình đã yêu cầu. Để gửi lại kết quả, hãy đưa các phản hồi theo thứ tự đã yêu cầu.

SDK Python hỗ trợ một tính năng có tên là [tự động gọi hàm](https://ai.google.dev/gemini-api/docs/function-calling?hl=vi#automatic_function_calling_python_only). Tính năng này chuyển đổi hàm Python thành phần khai báo, xử lý quá trình thực thi lệnh gọi hàm và chu kỳ phản hồi cho bạn. Sau đây là ví dụ về trường hợp sử dụng disco.

```
from google import genai
from google.genai import types

# Actual implementation functions
def power_disco_ball_impl(power: bool) -> dict:
    """Powers the spinning disco ball.

    Args:
        power: Whether to turn the disco ball on or off.

    Returns:
        A status dictionary indicating the current state.
    """
    return {"status": f"Disco ball powered {'on' if power else 'off'}"}

def start_music_impl(energetic: bool, loud: bool) -> dict:
    """Play some music matching the specified parameters.

    Args:
        energetic: Whether the music is energetic or not.
        loud: Whether the music is loud or not.

    Returns:
        A dictionary containing the music settings.
    """
    music_type = "energetic" if energetic else "chill"
    volume = "loud" if loud else "quiet"
    return {"music_type": music_type, "volume": volume}

def dim_lights_impl(brightness: float) -> dict:
    """Dim the lights.

    Args:
        brightness: The brightness of the lights, 0.0 is off, 1.0 is full.

    Returns:
        A dictionary containing the new brightness setting.
    """
    return {"brightness": brightness}

config = {
    "tools": [power_disco_ball_impl, start_music_impl, dim_lights_impl],
}

chat = client.chats.create(model="gemini-2.0-flash", config=config)
response = chat.send_message("Do everything you need to this place into party!")

print("\nExample 2: Automatic function calling")
print(response.text)
# I've turned on the disco ball, started playing loud and energetic music, and dimmed the lights to 50% brightness. Let's get this party started!
```

## Gọi hàm có khả năng kết hợp

Gemini 2.0 hỗ trợ tính năng gọi hàm có khả năng kết hợp, nghĩa là mô hình có thể liên kết nhiều lệnh gọi hàm với nhau. Ví dụ: để trả lời câu lệnh "Tìm nhiệt độ ở vị trí hiện tại của tôi", API Gemini có thể gọi cả hàm `get_current_location()` và hàm `get_weather()`, trong đó vị trí là tham số.

```
# Light control schemas
turn_on_the_lights_schema = {'name': 'turn_on_the_lights'}
turn_off_the_lights_schema = {'name': 'turn_off_the_lights'}

prompt = """
  Hey, can you write run some python code to turn on the lights, wait 10s and then turn off the lights?
  """

tools = [
    {'code_execution': {}},
    {'function_declarations': [turn_on_the_lights_schema, turn_off_the_lights_schema]}
]

await run(prompt, tools=tools, modality="AUDIO")
```
```
// Light control schemas
const turnOnTheLightsSchema = { name: 'turn_on_the_lights' };
const turnOffTheLightsSchema = { name: 'turn_off_the_lights' };

const prompt = \`
  Hey, can you write run some python code to turn on the lights, wait 10s and then turn off the lights?
\`;

const tools = [
  { codeExecution: {} },
  { functionDeclarations: [turnOnTheLightsSchema, turnOffTheLightsSchema] }
];

await run(prompt, tools=tools, modality="AUDIO")
```

## Chế độ gọi hàm

API Gemini cho phép bạn kiểm soát cách mô hình sử dụng các công cụ được cung cấp (tuyên bố hàm). Cụ thể, bạn có thể đặt chế độ trong `function_calling_config`.

- `AUTO (Default)`: Mô hình quyết định việc tạo câu trả lời bằng ngôn ngữ tự nhiên hay đề xuất lệnh gọi hàm dựa trên câu lệnh và ngữ cảnh. Đây là chế độ linh hoạt nhất và được đề xuất cho hầu hết các trường hợp.
- `ANY`: Mô hình bị ràng buộc để luôn dự đoán lệnh gọi hàm và đảm bảo tuân thủ giản đồ hàm. Nếu không chỉ định `allowed_function_names`, mô hình có thể chọn trong số bất kỳ nội dung khai báo hàm nào được cung cấp. Nếu `allowed_function_names` được cung cấp dưới dạng danh sách, thì mô hình chỉ có thể chọn trong số các hàm trong danh sách đó. Sử dụng chế độ này khi bạn yêu cầu một lệnh gọi hàm để phản hồi mọi lời nhắc (nếu có).
- `NONE`: Mô hình *bị cấm* thực hiện lệnh gọi hàm. Điều này tương đương với việc gửi một yêu cầu mà không có bất kỳ nội dung khai báo hàm nào. Sử dụng tính năng này để tạm thời tắt tính năng gọi hàm mà không xoá các định nghĩa công cụ.
```
from google.genai import types

# Configure function calling mode
tool_config = types.ToolConfig(
    function_calling_config=types.FunctionCallingConfig(
        mode="ANY", allowed_function_names=["get_current_temperature"]
    )
)

# Create the generation config
config = types.GenerateContentConfig(
    temperature=0,
    tools=[tools],  # not defined here.
    tool_config=tool_config,
)
```
```
import { FunctionCallingConfigMode } from '@google/genai';

// Configure function calling mode
const toolConfig = {
  functionCallingConfig: {
    mode: FunctionCallingConfigMode.ANY,
    allowedFunctionNames: ['get_current_temperature']
  }
};

// Create the generation config
const config = {
  temperature: 0,
  tools: tools, // not defined here.
  toolConfig: toolConfig,
};
```

## Gọi hàm tự động (chỉ dành cho Python)

Khi sử dụng SDK Python, bạn có thể trực tiếp cung cấp các hàm Python dưới dạng công cụ. SDK sẽ tự động chuyển đổi hàm Python thành các nội dung khai báo, xử lý chu kỳ thực thi lệnh gọi hàm và phản hồi cho bạn. Sau đó, SDK Python sẽ tự động:

1. Phát hiện phản hồi lệnh gọi hàm từ mô hình.
2. Gọi hàm Python tương ứng trong mã.
3. Gửi phản hồi hàm trở lại mô hình.
4. Trả về phản hồi văn bản cuối cùng của mô hình.

Để sử dụng tính năng này, hãy xác định hàm bằng gợi ý kiểu và docstring, sau đó truyền chính hàm đó (không phải nội dung khai báo JSON) dưới dạng một công cụ:

```
from google import genai
from google.genai import types

# Define the function with type hints and docstring
def get_current_temperature(location: str) -> dict:
    """Gets the current temperature for a given location.

    Args:
        location: The city and state, e.g. San Francisco, CA

    Returns:
        A dictionary containing the temperature and unit.
    """
    # ... (implementation) ...
    return {"temperature": 25, "unit": "Celsius"}

# Configure the client and model
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))  # Replace with your actual API key setup
config = types.GenerateContentConfig(
    tools=[get_current_temperature]
)  # Pass the function itself

# Make the request
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="What's the temperature in Boston?",
    config=config,
)

print(response.text)  # The SDK handles the function call and returns the final text
```

Bạn có thể tắt tính năng gọi hàm tự động bằng:

```
# To disable automatic function calling:
config = types.GenerateContentConfig(
    tools=[get_current_temperature],
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
)
```

### Khai báo giản đồ Hàm tự động

Tính năng tự động trích xuất giản đồ từ các hàm Python không hoạt động trong mọi trường hợp. Ví dụ: trình tạo không xử lý các trường hợp bạn mô tả các trường của đối tượng từ điển lồng nhau. API có thể mô tả bất kỳ loại nào sau đây:

```
AllowedType = (int | float | bool | str | list['AllowedType'] | dict[str, AllowedType])
```

Để xem giản đồ suy luận, bạn có thể chuyển đổi giản đồ đó bằng [`from_callable`](https://googleapis.github.io/python-genai/genai.html#genai.types.FunctionDeclaration.from_callable):

```
def multiply(a: float, b: float):
    """Returns a * b."""
    return a * b

fn_decl = types.FunctionDeclaration.from_callable(callable=multiply, client=client)

# to_json_dict() provides a clean JSON representation.
print(fn_decl.to_json_dict())
```

## Sử dụng nhiều công cụ: Kết hợp Công cụ gốc với Lệnh gọi hàm

Với Gemini 2.0, bạn có thể bật nhiều công cụ kết hợp các công cụ gốc với lệnh gọi hàm cùng một lúc. Sau đây là ví dụ về việc bật hai công cụ, [Tìm thông tin cơ bản bằng Google Tìm kiếm](https://ai.google.dev/gemini-api/docs/grounding?hl=vi) và [thực thi mã](https://ai.google.dev/gemini-api/docs/code-execution?hl=vi), trong một yêu cầu sử dụng [API Trực tiếp](https://ai.google.dev/gemini-api/docs/live?hl=vi).

```
# Multiple tasks example - combining lights, code execution, and search
prompt = """
  Hey, I need you to do three things for me.

    1.  Turn on the lights.
    2.  Then compute the largest prime palindrome under 100000.
    3.  Then use Google Search to look up information about the largest earthquake in California the week of Dec 5 2024.

  Thanks!
  """

tools = [
    {'google_search': {}},
    {'code_execution': {}},
    {'function_declarations': [turn_on_the_lights_schema, turn_off_the_lights_schema]} # not defined here.
]

# Execute the prompt with specified tools in audio modality
await run(prompt, tools=tools, modality="AUDIO")
```
```
// Multiple tasks example - combining lights, code execution, and search
const prompt = \`
  Hey, I need you to do three things for me.

    1.  Turn on the lights.
    2.  Then compute the largest prime palindrome under 100000.
    3.  Then use Google Search to look up information about the largest earthquake in California the week of Dec 5 2024.

  Thanks!
\`;

const tools = [
  { googleSearch: {} },
  { codeExecution: {} },
  { functionDeclarations: [turnOnTheLightsSchema, turnOffTheLightsSchema] } // not defined here.
];

// Execute the prompt with specified tools in audio modality
await run(prompt, {tools: tools, modality: "AUDIO"});
```

Nhà phát triển Python có thể thử tính năng này trong [sổ tay Sử dụng công cụ API trực tiếp](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Get_started_LiveAPI_tools.ipynb).

## Sử dụng Giao thức ngữ cảnh mô hình (MCP)

[Giao thức ngữ cảnh mô hình (MCP)](https://modelcontextprotocol.io/introduction) là một tiêu chuẩn mở để kết nối các ứng dụng AI với các công cụ, nguồn dữ liệu và hệ thống bên ngoài. MCP cung cấp một giao thức chung để các mô hình truy cập vào ngữ cảnh, chẳng hạn như các hàm (công cụ), nguồn dữ liệu (tài nguyên) hoặc lời nhắc được xác định trước. Bạn có thể sử dụng các mô hình với máy chủ MCP bằng cách sử dụng chức năng gọi công cụ của các mô hình đó.

Máy chủ MCP hiển thị các công cụ dưới dạng định nghĩa giản đồ JSON. Bạn có thể sử dụng các công cụ này với các nội dung khai báo hàm tương thích với Gemini. Điều này cho phép bạn sử dụng trực tiếp máy chủ MCP với các mô hình Gemini. Tại đây, bạn có thể tìm thấy ví dụ về cách sử dụng máy chủ MCP cục bộ bằng SDK Gemini và SDK `mcp`.

```
import asyncio
import os
from datetime import datetime
from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Create server parameters for stdio connection
server_params = StdioServerParameters(
    command="npx",  # Executable
    args=["-y", "@philschmid/weather-mcp"],  # Weather MCP Server
    env=None,  # Optional environment variables
)

async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Prompt to get the weather for the current day in London.
            prompt = f"What is the weather in London in {datetime.now().strftime('%Y-%m-%d')}?"
            # Initialize the connection between client and server
            await session.initialize()

            # Get tools from MCP session and convert to Gemini Tool objects
            mcp_tools = await session.list_tools()
            tools = [
                types.Tool(
                    function_declarations=[
                        {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": {
                                k: v
                                for k, v in tool.inputSchema.items()
                                if k not in ["additionalProperties", "$schema"]
                            },
                        }
                    ]
                )
                for tool in mcp_tools.tools
            ]

            # Send request to the model with MCP function declarations
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0,
                    tools=tools,
                ),
            )

            # Check for a function call
            if response.candidates[0].content.parts[0].function_call:
                function_call = response.candidates[0].content.parts[0].function_call
                print(function_call)
                # Call the MCP server with the predicted tool
                result = await session.call_tool(
                    function_call.name, arguments=function_call.args
                )
                print(result.content[0].text)
                # Continue as shown in step 4 of "How Function Calling Works"
                # and create a user friendly response
            else:
                print("No function call found in the response.")
                print(response.text)

# Start the asyncio event loop and run the main function
asyncio.run(run())
```
```
import { GoogleGenAI } from '@google/genai';
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

// Create server parameters for stdio connection
const serverParams = new StdioClientTransport({
  command: "npx",
  args: ["-y", "@philschmid/weather-mcp"]
});

const client = new Client(
  {
    name: "example-client",
    version: "1.0.0"
  }
);

// Configure the client
const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

// Initialize the connection between client and server
await client.connect(serverParams);

// Get tools from MCP session and convert to Gemini Tool objects
const mcpTools = await client.listTools();
const tools = mcpTools.tools.map((tool) => {
  // Filter the parameters to exclude not supported keys
  const parameters = Object.fromEntries(
    Object.entries(tool.inputSchema).filter(([key]) => !["additionalProperties", "$schema"].includes(key))
  );
  return {
    name: tool.name,
    description: tool.description,
    parameters: parameters
  };
});

// Send request to the model with MCP function declarations
const response = await ai.models.generateContent({
  model: "gemini-2.0-flash",
  contents: "What is the weather in London in the UK on 2024-04-04?",
  config: {
    tools: [{
      functionDeclarations: tools
    }],
  },
});

// Check for function calls in the response
if (response.functionCalls && response.functionCalls.length > 0) {
  const functionCall = response.functionCalls[0]; // Assuming one function call
  console.log(\`Function to call: ${functionCall.name}\`);
  console.log(\`Arguments: ${JSON.stringify(functionCall.args)}\`);
  // Call the MCP server with the predicted tool
  const result = await client.callTool({name: functionCall.name, arguments: functionCall.args});
  console.log(result.content[0].text);
  // Continue as shown in step 4 of "How Function Calling Works"
  // and create a user friendly response
} else {
  console.log("No function call found in the response.");
  console.log(response.text);
}

// Close the connection
await client.close();
```

## Mô hình được hỗ trợ

Không bao gồm mô hình thử nghiệm. Bạn có thể tìm thấy các chức năng của chúng trên trang [tổng quan về mô hình](https://ai.google.dev/gemini-api/docs/models?hl=vi).

| Mô hình | Gọi hàm | Gọi hàm song song | Gọi hàm có khả năng kết hợp   (chỉ dành cho API trực tiếp) |
| --- | --- | --- | --- |
| Gemini 2.0 Flash | ✔️ | ✔️ | ✔️ |
| Gemini 2.0 Flash-Lite | X | X | X |
| Gemini 1.5 Flash | ✔️ | ✔️ | ✔️ |
| Gemini 1.5 Pro | ✔️ | ✔️ | ✔️ |

## Các phương pháp hay nhất

- **Mô tả hàm và tham số:** Hãy mô tả một cách rõ ràng và cụ thể. Mô hình này dựa vào các thông tin này để chọn hàm chính xác và cung cấp các đối số phù hợp.
- **Đặt tên:** Sử dụng tên hàm mô tả (không có dấu cách, dấu chấm hoặc dấu gạch ngang).
- **Kiểu mạnh:** Sử dụng các loại cụ thể (số nguyên, chuỗi, enum) cho các tham số để giảm lỗi. Nếu một tham số có một tập hợp giá trị hợp lệ bị giới hạn, hãy sử dụng enum.
- **Chọn công cụ:** Mặc dù mô hình có thể sử dụng số lượng công cụ tuỳ ý, nhưng việc cung cấp quá nhiều công cụ có thể làm tăng nguy cơ chọn công cụ không chính xác hoặc không tối ưu. Để đạt được kết quả tốt nhất, hãy cố gắng chỉ cung cấp các công cụ phù hợp với ngữ cảnh hoặc tác vụ, tốt nhất là giữ cho bộ công cụ đang hoạt động ở mức tối đa là 10-20. Hãy cân nhắc việc chọn công cụ động dựa trên ngữ cảnh cuộc trò chuyện nếu bạn có tổng số công cụ lớn.
- **Thiết kế câu lệnh:**
	- Cung cấp ngữ cảnh: Cho mô hình biết vai trò của mô hình đó (ví dụ: "Bạn là một trợ lý thời tiết hữu ích").
	- Hướng dẫn: Chỉ định cách và thời điểm sử dụng hàm (ví dụ: "Đừng đoán ngày; hãy luôn sử dụng ngày trong tương lai cho thông tin dự báo").
	- Khuyến khích làm rõ: Hướng dẫn mô hình đặt câu hỏi làm rõ nếu cần.
- **Nhiệt độ:** Sử dụng nhiệt độ thấp (ví dụ: 0) để có các lệnh gọi hàm có tính quyết định và đáng tin cậy hơn.
- **Xác thực:** Nếu lệnh gọi hàm có hậu quả đáng kể (ví dụ: đặt hàng), hãy xác thực lệnh gọi với người dùng trước khi thực thi.
- **Xử lý lỗi**: Triển khai tính năng xử lý lỗi mạnh mẽ trong các hàm để xử lý linh hoạt các lỗi API hoặc dữ liệu đầu vào không mong muốn. Trả về thông báo lỗi đầy đủ thông tin mà mô hình có thể sử dụng để tạo câu trả lời hữu ích cho người dùng.
- **Bảo mật:** Hãy chú ý đến vấn đề bảo mật khi gọi các API bên ngoài. Sử dụng các cơ chế xác thực và uỷ quyền thích hợp. Tránh tiết lộ dữ liệu nhạy cảm trong các lệnh gọi hàm.
- **Giới hạn mã thông báo:** Nội dung mô tả hàm và tham số được tính vào giới hạn mã thông báo đầu vào. Nếu bạn sắp đạt đến giới hạn mã thông báo, hãy cân nhắc giới hạn số lượng hàm hoặc độ dài của nội dung mô tả, chia nhỏ các tác vụ phức tạp thành các nhóm hàm nhỏ hơn, tập trung hơn.

## Lưu ý và giới hạn

- Chỉ hỗ trợ [một tập hợp con của giản đồ OpenAPI](https://ai.google.dev/api/caching?hl=vi#FunctionDeclaration).
- Các loại tham số được hỗ trợ trong Python bị hạn chế.
- Tính năng gọi hàm tự động chỉ dành cho SDK Python.

Trừ phi có lưu ý khác, nội dung của trang này được cấp phép theo [Giấy phép ghi nhận tác giả 4.0 của Creative Commons](https://creativecommons.org/licenses/by/4.0/) và các mẫu mã lập trình được cấp phép theo [Giấy phép Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0). Để biết thông tin chi tiết, vui lòng tham khảo [Chính sách trang web của Google Developers](https://developers.google.com/site-policies?hl=vi). Java là nhãn hiệu đã đăng ký của Oracle và/hoặc các đơn vị liên kết với Oracle.

Cập nhật lần gần đây nhất: 2025-04-14 UTC.

Đã tải xong trang mới.

x1.00

\>

<

\>>

<<

O