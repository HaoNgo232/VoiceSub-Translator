---
title: "Bắt đầu nhanh API Gemini  |  Gemini API  |  Google AI for Developers"
source: "https://ai.google.dev/gemini-api/docs/quickstart?hl=vi&lang=python"
author:
published:
created: 2025-05-08
description: "Làm quen với Gemini API dành cho nhà phát triển"
tags:
  - "clippings"
---
Hướng dẫn bắt đầu nhanh này sẽ hướng dẫn bạn cách cài đặt SDK mà bạn chọn trong **[SDK AI tạo sinh của Google](https://ai.google.dev/gemini-api/docs/libraries?hl=vi)** (mới), sau đó đưa ra yêu cầu Gemini API đầu tiên.

## Cài đặt thư viện Gemini API

Sử dụng [Python 3.9 trở lên](https://www.python.org/downloads/), hãy cài đặt [gói `google-genai`](https://pypi.org/project/google-genai/) bằng [lệnh pip](https://packaging.python.org/en/latest/tutorials/installing-packages/) sau:

```
pip install -q -U google-genai
```

## Đưa ra yêu cầu đầu tiên

[Lấy khoá Gemini API trong Google AI Studio](https://aistudio.google.com/app/apikey?hl=vi)

Sử dụng phương thức [`generateContent`](https://ai.google.dev/api/generate-content?hl=vi#method:-models.generatecontent) để gửi yêu cầu đến Gemini API.

```
from google import genai

client = genai.Client(api_key="YOUR_API_KEY")

response = client.models.generate_content(
    model="gemini-2.0-flash", contents="Explain how AI works in a few words"
)
print(response.text)
```

## Bước tiếp theo

Giờ đây, khi đã tạo yêu cầu API đầu tiên, bạn nên khám phá các hướng dẫn sau đây về cách Gemini hoạt động:

- [Tạo văn bản](https://ai.google.dev/gemini-api/docs/text-generation?hl=vi)
- [Vision](https://ai.google.dev/gemini-api/docs/vision?hl=vi)
- [Ngữ cảnh dài](https://ai.google.dev/gemini-api/docs/long-context?hl=vi)

Trừ phi có lưu ý khác, nội dung của trang này được cấp phép theo [Giấy phép ghi nhận tác giả 4.0 của Creative Commons](https://creativecommons.org/licenses/by/4.0/) và các mẫu mã lập trình được cấp phép theo [Giấy phép Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0). Để biết thông tin chi tiết, vui lòng tham khảo [Chính sách trang web của Google Developers](https://developers.google.com/site-policies?hl=vi). Java là nhãn hiệu đã đăng ký của Oracle và/hoặc các đơn vị liên kết với Oracle.

Cập nhật lần gần đây nhất: 2025-04-28 UTC.

Đã tải xong trang mới..

x1.00

\>

<

\>>

<<

O