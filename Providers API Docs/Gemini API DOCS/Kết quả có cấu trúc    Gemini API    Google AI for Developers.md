---
title: "Kết quả có cấu trúc  |  Gemini API  |  Google AI for Developers"
source: "https://ai.google.dev/gemini-api/docs/structured-output?hl=vi"
author:
published:
created: 2025-05-08
description: "Tìm hiểu cách tạo kết quả có cấu trúc bằng Gemini API"
tags:
  - "clippings"
---
Theo mặc định, Gemini tạo văn bản không có cấu trúc, nhưng bạn có thể ràng buộc mô hình để phản hồi bằng *đầu ra có cấu trúc* – JSON hoặc một giá trị từ enum. Tính năng đầu ra có cấu trúc này đặc biệt hữu ích khi bạn cần trích xuất thông tin từ dữ liệu không có cấu trúc, sau đó xử lý thông tin đó để ứng dụng sử dụng. Ví dụ: bạn có thể sử dụng tính năng này để trích xuất thông tin chuẩn hoá từ hồ sơ xin việc, sau đó tạo cơ sở dữ liệu từ thông tin đó. Hoặc bạn có thể trích xuất nguyên liệu từ công thức nấu ăn và hiển thị đường liên kết đến trang web bán thực phẩm tạp hoá cho từng nguyên liệu.

Hướng dẫn này sẽ hướng dẫn bạn cách tạo đầu ra có cấu trúc bằng API Gemini.

## Tạo JSON

Có hai cách để tạo JSON bằng API Gemini:

- Định cấu hình giản đồ trên mô hình
- Cung cấp giản đồ trong lời nhắc văn bản

Bạn nên định cấu hình giản đồ trên mô hình để tạo JSON, vì việc này sẽ ràng buộc mô hình để xuất JSON.

### Định cấu hình giản đồ

Để ràng buộc mô hình tạo JSON, hãy định cấu hình `responseSchema`. Sau đó, mô hình sẽ phản hồi mọi lời nhắc bằng đầu ra có định dạng JSON.

Kết quả có thể như sau:

```
[
  {
    "recipeName": "Chocolate Chip Cookies",
    "ingredients": [
      "1 cup (2 sticks) unsalted butter, softened",
      "3/4 cup granulated sugar",
      "3/4 cup packed brown sugar",
      "1 teaspoon vanilla extract",
      "2 large eggs",
      "2 1/4 cups all-purpose flour",
      "1 teaspoon baking soda",
      "1 teaspoon salt",
      "2 cups chocolate chips"
    ]
  },
  ...
]
```

### Cung cấp giản đồ trong lời nhắc văn bản

Thay vì định cấu hình giản đồ, bạn có thể cung cấp giản đồ dưới dạng ngôn ngữ tự nhiên hoặc mã giả trong lời nhắc văn bản. Bạn **không nên** sử dụng phương thức này vì phương thức này có thể tạo ra kết quả chất lượng thấp hơn và vì mô hình không bị ràng buộc phải tuân theo giản đồ.

Dưới đây là ví dụ chung về giản đồ được cung cấp trong câu lệnh dạng văn bản:

```
List a few popular cookie recipes, and include the amounts of ingredients.

Produce JSON matching this specification:

Recipe = { "recipeName": string, "ingredients": array<string> }
Return: array<Recipe>
```

Vì mô hình lấy giản đồ từ văn bản trong câu lệnh, nên bạn có thể linh hoạt trong cách biểu thị giản đồ. Tuy nhiên, khi bạn cung cấp giản đồ cùng dòng như thế này, mô hình thực sự không bị ràng buộc phải trả về JSON. Để có phản hồi chất lượng cao hơn và có tính quyết định hơn, hãy định cấu hình giản đồ trên mô hình và không sao chép giản đồ trong lời nhắc văn bản.

## Giản đồ JSON

Khi định cấu hình mô hình để trả về phản hồi JSON, bạn sẽ sử dụng đối tượng `Schema` để xác định hình dạng của dữ liệu JSON. `Schema` đại diện cho một tập hợp con chọn lọc của [đối tượng giản đồ OpenAPI 3.0](https://spec.openapis.org/oas/v3.0.3#schema-object), đồng thời thêm trường `propertyOrdering`.

Dưới đây là nội dung đại diện JSON giả lập của tất cả các trường `Schema`:

```
{
  "type": enum (Type),
  "format": string,
  "description": string,
  "nullable": boolean,
  "enum": [
    string
  ],
  "maxItems": integer,
  "minItems": integer,
  "properties": {
    string: {
      object (Schema)
    },
    ...
  },
  "required": [
    string
  ],
  "propertyOrdering": [
    string
  ],
  "items": {
    object (Schema)
  }
}
```

`Type` của giản đồ phải là một trong các [Loại dữ liệu](https://spec.openapis.org/oas/v3.0.3#data-types) của OpenAPI hoặc một tổ hợp các loại đó (sử dụng `anyOf`). Chỉ một tập hợp con các trường mới hợp lệ cho mỗi `Type`. Danh sách sau đây liên kết từng `Type` với một tập hợp con các trường hợp hợp lệ cho loại đó:

- `string` -> `enum`, `format`, `nullable`
- `integer` -> `format`, `minimum`, `maximum`, `enum`, `nullable`
- `number` -> `format`, `minimum`, `maximum`, `enum`, `nullable`
- `boolean` -> `nullable`
- `array` -> `minItems`, `maxItems`, `items`, `nullable`
- `object` -> `properties`, `required`, `propertyOrdering`, `nullable`

Dưới đây là một số giản đồ mẫu cho thấy các tổ hợp loại và trường hợp hợp lệ:

```
{ "type": "string", "enum": ["a", "b", "c"] }

{ "type": "string", "format": "date-time" }

{ "type": "integer", "format": "int64" }

{ "type": "number", "format": "double" }

{ "type": "boolean" }

{ "type": "array", "minItems": 3, "maxItems": 3, "items": { "type": ... } }

{ "type": "object",
  "properties": {
    "a": { "type": ... },
    "b": { "type": ... },
    "c": { "type": ... }
  },
  "nullable": true,
  "required": ["c"],
  "propertyOrdering": ["c", "b", "a"]
}
```

Để xem tài liệu đầy đủ về các trường Giản đồ khi được sử dụng trong API Gemini, hãy xem [Tài liệu tham khảo về Giản đồ](https://ai.google.dev/api/caching?hl=vi#Schema).

### Đặt hàng tài sản

Khi bạn làm việc với giản đồ JSON trong API Gemini, thứ tự của các thuộc tính rất quan trọng. Theo mặc định, API sắp xếp các thuộc tính theo thứ tự bảng chữ cái và không giữ nguyên thứ tự xác định các thuộc tính (mặc dù [SDK AI tạo sinh của Google](https://ai.google.dev/gemini-api/docs/sdks?hl=vi) có thể giữ nguyên thứ tự này). Nếu bạn đang cung cấp ví dụ cho mô hình đã định cấu hình giản đồ và thứ tự thuộc tính của các ví dụ không nhất quán với thứ tự thuộc tính của giản đồ, thì kết quả có thể là lộn xộn hoặc không mong muốn.

Để đảm bảo thứ tự các thuộc tính nhất quán và dễ dự đoán, bạn có thể sử dụng trường `propertyOrdering[]` không bắt buộc.

```
"propertyOrdering": ["recipeName", "ingredients"]
```

`propertyOrdering[]` – không phải là trường tiêu chuẩn trong quy cách OpenAPI – là một mảng các chuỗi dùng để xác định thứ tự của các thuộc tính trong phản hồi. Bằng cách chỉ định thứ tự của các thuộc tính, sau đó cung cấp ví dụ với các thuộc tính theo thứ tự đó, bạn có thể cải thiện chất lượng của kết quả. `propertyOrdering` chỉ được hỗ trợ khi bạn tạo `types.Schema` theo cách thủ công.

### Giản đồ trong Python

Phần này cung cấp hướng dẫn bổ sung về cách xử lý giản đồ JSON bằng thư viện Python.

Khi bạn đang sử dụng thư viện Python, giá trị của `response_schema` phải là một trong các giá trị sau:

- Một loại, như bạn sẽ sử dụng trong chú giải loại (xem [mô-đun `typing`](https://docs.python.org/3/library/typing.html) của Python)
- Một thực thể của [`genai.types.Schema`](https://googleapis.github.io/python-genai/genai.html#genai.types.Schema)
- `dict` tương đương với `genai.types.Schema`

Cách dễ nhất để xác định một giản đồ là sử dụng loại Pydantic (như trong ví dụ trước):

```
config={'response_mime_type': 'application/json',
        'response_schema': list[Recipe]}
```

Khi bạn sử dụng loại Pydantic, thư viện Python sẽ tạo một giản đồ JSON cho bạn và gửi giản đồ đó đến API. Để biết thêm ví dụ, hãy xem [tài liệu về thư viện Python](https://googleapis.github.io/python-genai/index.html#json-response-schema).

Thư viện Python hỗ trợ các giản đồ được xác định bằng các loại sau (trong đó `AllowedType` là bất kỳ loại nào được cho phép):

- `int`
- `float`
- `bool`
- `str`
- `list[AllowedType]`
- `AllowedType|AllowedType|...`
- Đối với các loại có cấu trúc:
	- `dict[str, AllowedType]`. Chú thích này khai báo tất cả giá trị của từ điển là cùng một loại, nhưng không chỉ định những khoá cần đưa vào.
	- [Mô hình Pydantic](https://docs.pydantic.dev/latest/concepts/models/) do người dùng xác định. Phương pháp này cho phép bạn chỉ định tên khoá và xác định các loại khác nhau cho các giá trị liên kết với từng khoá, bao gồm cả cấu trúc lồng nhau.

## Tạo giá trị enum

Trong một số trường hợp, bạn có thể muốn mô hình chọn một tuỳ chọn trong danh sách tuỳ chọn. Để triển khai hành vi này, bạn có thể truyền một *enum* trong giản đồ. Bạn có thể sử dụng tuỳ chọn enum ở bất cứ nơi nào bạn có thể sử dụng `string` trong `responseSchema`, vì enum là một mảng chuỗi. Giống như giản đồ JSON, enum cho phép bạn ràng buộc đầu ra của mô hình để đáp ứng các yêu cầu của ứng dụng.

Ví dụ: giả sử bạn đang phát triển một ứng dụng để phân loại các nhạc cụ thành một trong năm danh mục: `"Percussion"`, `"String"`, `"Woodwind"`, `"Brass"` hoặc " `"Keyboard"` ". Bạn có thể tạo một enum để giúp thực hiện nhiệm vụ này.

Trong ví dụ sau, bạn truyền một enum dưới dạng `responseSchema`, ràng buộc mô hình để chọn tuỳ chọn phù hợp nhất.

```
from google import genai
import enum

class Instrument(enum.Enum):
  PERCUSSION = "Percussion"
  STRING = "String"
  WOODWIND = "Woodwind"
  BRASS = "Brass"
  KEYBOARD = "Keyboard"

client = genai.Client(api_key="GEMINI_API_KEY")
response = client.models.generate_content(
    model='gemini-2.0-flash',
    contents='What type of instrument is an oboe?',
    config={
        'response_mime_type': 'text/x.enum',
        'response_schema': Instrument,
    },
)

print(response.text)
# Woodwind
```

Thư viện Python sẽ dịch các nội dung khai báo loại cho API. Tuy nhiên, API chấp nhận một tập hợp con của giản đồ OpenAPI 3.0 ([Giản đồ](https://ai.google.dev/api/caching?hl=vi#schema)).

Có hai cách khác để chỉ định một enum. Bạn có thể sử dụng [`Literal`](https://docs.pydantic.dev/1.10/usage/types/#literal-type):

```
Literal["Percussion", "String", "Woodwind", "Brass", "Keyboard"]
```

Bạn cũng có thể truyền giản đồ dưới dạng JSON:

```
from google import genai

client = genai.Client(api_key="GEMINI_API_KEY")
response = client.models.generate_content(
    model='gemini-2.0-flash',
    contents='What type of instrument is an oboe?',
    config={
        'response_mime_type': 'text/x.enum',
        'response_schema': {
            "type": "STRING",
            "enum": ["Percussion", "String", "Woodwind", "Brass", "Keyboard"],
        },
    },
)

print(response.text)
# Woodwind
```

Ngoài các bài tập trắc nghiệm cơ bản, bạn có thể sử dụng enum ở bất kỳ đâu trong giản đồ JSON. Ví dụ: bạn có thể yêu cầu mô hình cung cấp danh sách các tiêu đề công thức nấu ăn và sử dụng enum `Grade` để xếp hạng mức độ phổ biến cho từng tiêu đề:

Phản hồi có thể có dạng như sau:

```
[
  {
    "recipe_name": "Chocolate Chip Cookies",
    "rating": "a+"
  },
  {
    "recipe_name": "Peanut Butter Cookies",
    "rating": "a"
  },
  {
    "recipe_name": "Oatmeal Raisin Cookies",
    "rating": "b"
  },
  ...
]
```

## Những yếu tố nên cân nhắc

Hãy lưu ý những điểm cần cân nhắc và phương pháp hay nhất sau đây khi bạn sử dụng giản đồ phản hồi:

- Kích thước của giản đồ phản hồi được tính vào giới hạn mã thông báo đầu vào.
- Theo mặc định, các trường là không bắt buộc, nghĩa là mô hình có thể điền sẵn các trường hoặc bỏ qua các trường đó. Bạn có thể đặt các trường theo yêu cầu để buộc mô hình cung cấp một giá trị. Nếu không có đủ ngữ cảnh trong câu lệnh đầu vào được liên kết, mô hình sẽ tạo câu trả lời chủ yếu dựa trên dữ liệu mà mô hình được huấn luyện.
- Một giản đồ phức tạp có thể dẫn đến lỗi `InvalidArgument: 400`. Mức độ phức tạp có thể đến từ tên thuộc tính dài, giới hạn độ dài mảng dài, enum có nhiều giá trị, đối tượng có nhiều thuộc tính không bắt buộc hoặc sự kết hợp của các yếu tố này.
	Nếu bạn gặp lỗi này với một giản đồ hợp lệ, hãy thực hiện một hoặc nhiều thay đổi sau đây để giải quyết lỗi:
	- Rút ngắn tên thuộc tính hoặc tên enum.
	- Làm phẳng các mảng lồng nhau.
	- Giảm số lượng thuộc tính có quy tắc ràng buộc, chẳng hạn như số có giới hạn tối thiểu và tối đa.
	- Giảm số lượng thuộc tính có các quy tắc ràng buộc phức tạp, chẳng hạn như các thuộc tính có định dạng phức tạp như `date-time`.
	- Giảm số lượng thuộc tính không bắt buộc.
	- Giảm số lượng giá trị hợp lệ cho enum.
- Nếu bạn không thấy kết quả như mong đợi, hãy thêm ngữ cảnh vào lời nhắc nhập hoặc sửa đổi giản đồ phản hồi. Ví dụ: xem xét phản hồi của mô hình mà không có đầu ra có cấu trúc để xem mô hình phản hồi như thế nào. Sau đó, bạn có thể cập nhật giản đồ phản hồi để phù hợp hơn với đầu ra của mô hình.

## Bước tiếp theo

Giờ đây, khi đã tìm hiểu cách tạo đầu ra có cấu trúc, bạn có thể thử sử dụng các công cụ Gemini API:

- [Gọi hàm](https://ai.google.dev/gemini-api/docs/function-calling?hl=vi)
- [Thực thi mã](https://ai.google.dev/gemini-api/docs/code-execution?hl=vi)
- [Làm quen với Google Tìm kiếm](https://ai.google.dev/gemini-api/docs/grounding?hl=vi)

Trừ phi có lưu ý khác, nội dung của trang này được cấp phép theo [Giấy phép ghi nhận tác giả 4.0 của Creative Commons](https://creativecommons.org/licenses/by/4.0/) và các mẫu mã lập trình được cấp phép theo [Giấy phép Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0). Để biết thông tin chi tiết, vui lòng tham khảo [Chính sách trang web của Google Developers](https://developers.google.com/site-policies?hl=vi). Java là nhãn hiệu đã đăng ký của Oracle và/hoặc các đơn vị liên kết với Oracle.

Cập nhật lần gần đây nhất: 2025-05-07 UTC.

Đã tải xong trang mới.

x1.00

\>

<

\>>

<<

O