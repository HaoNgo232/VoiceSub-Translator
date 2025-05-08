---
title: "Thư viện Gemini API  |  Google AI for Developers"
source: "https://ai.google.dev/gemini-api/docs/libraries?hl=vi"
author:
published:
created: 2025-05-08
description: "Tải xuống và bắt đầu sử dụng SDK Thư viện API Gemini"
tags:
  - "clippings"
---
Trang này cung cấp thông tin về cách tải xuống và cài đặt các thư viện mới nhất cho API Gemini. Nếu bạn mới sử dụng Gemini API, hãy bắt đầu bằng [hướng dẫn nhanh về API](https://ai.google.dev/gemini-api/docs/quickstart?hl=vi).

## Lưu ý quan trọng về các thư viện mới của chúng tôi

Gần đây, chúng tôi đã ra mắt một bộ thư viện mới để mang đến trải nghiệm nhất quán và đơn giản hơn khi truy cập vào các mô hình AI tạo sinh của Google trên nhiều dịch vụ của Google.

**Nội dung cập nhật về Thư viện khoá**

| Ngôn ngữ | Thư viện cũ | Thư viện mới (Nên dùng) |
| --- | --- | --- |
| [**Python**](https://ai.google.dev/gemini-api/docs/libraries?hl=vi#python) | `google-generativeai` | `google-genai` |
| [**JavaScript   và TypeScript**](https://ai.google.dev/gemini-api/docs/libraries?hl=vi#javascript) | `@google/generative-ai` | `@google/genai`   Đang ở giai đoạn [Xem trước](https://ai.google.dev/gemini-api/docs/libraries?hl=vi#javascript) |
| [**Go**](https://ai.google.dev/gemini-api/docs/libraries?hl=vi#go) | `google.golang.org/generative-ai` | `google.golang.org/genai` |

Tất cả người dùng các thư viện trước đó nên chuyển sang thư viện mới. Mặc dù thư viện JavaScript/TypeScript đang ở giai đoạn Xem trước, nhưng bạn vẫn nên bắt đầu di chuyển, miễn là bạn cảm thấy thoải mái với các lưu ý được liệt kê trong phần [JavaScript/TypeScript](https://ai.google.dev/gemini-api/docs/libraries?hl=vi#javascript).

## Python

Bạn có thể cài đặt [thư viện Python](https://pypi.org/project/google-genai) bằng cách chạy:

```
pip install google-genai
```

## JavaScript và TypeScript

Bạn có thể cài đặt [thư viện JavaScript và TypeScript](https://www.npmjs.com/package/@google/genai) bằng cách chạy:

```
npm install @google/genai
```

Thư viện JavaScript/TypeScript [mới](https://ai.google.dev/gemini-api/docs/libraries?hl=vi) hiện đang ở dạng [*xem trước*](https://cloud.google.com/products?hl=vi#product-launch-stages), nghĩa là thư viện này có thể chưa hoàn thiện về tính năng và chúng tôi có thể cần phải giới thiệu các thay đổi có thể gây lỗi.

Tuy nhiên, bạn *nên* bắt đầu sử dụng [SDK mới](https://www.npmjs.com/package/@google/genai) thay vì phiên bản [trước đó](https://ai.google.dev/gemini-api/docs/?hl=vi#previous-sdks) không dùng nữa, miễn là bạn cảm thấy thoải mái với những lưu ý này. Chúng tôi đang tích cực triển khai để phát hành bản GA (Bản phát hành công khai) cho thư viện này.

### Khoá API trong các ứng dụng phía máy khách

**CẢNH BÁO**: Bất kể bạn đang sử dụng thư viện nào, việc chèn khoá API vào mã JavaScript hoặc TypeScript phía máy khách đều [không an toàn](https://ai.google.dev/gemini-api/docs/api-key?hl=vi#security). Sử dụng các bản triển khai phía máy chủ để truy cập vào Gemini API trong môi trường sản xuất.

## Go

Bạn có thể cài đặt [thư viện Go](https://pkg.go.dev/google.golang.org/genai) bằng cách chạy:

```
go get google.golang.org/genai
```

## Thư viện và SDK trước đó

Sau đây là một tập hợp các SDK trước đây của chúng tôi không còn được phát triển tích cực. Bạn có thể chuyển sang SDK AI tạo sinh của Google đã cập nhật bằng cách sử dụng [hướng dẫn di chuyển](https://ai.google.dev/gemini-api/docs/migrate?hl=vi) của chúng tôi:

- [Thư viện Python trước đó](https://github.com/google-gemini/deprecated-generative-ai-python)
- [Thư viện Node.js trước đó](https://github.com/google-gemini/generative-ai-js)
- [Thư viện Go trước](https://github.com/google/generative-ai-go)
- [Thư viện Dart và Flutter trước đây](https://pub.dev/packages/google_generative_ai/install)
- [Thư viện Swift trước đó](https://github.com/google/generative-ai-swift)
- [Thư viện Android trước đó](https://github.com/google-gemini/generative-ai-android)

Trừ phi có lưu ý khác, nội dung của trang này được cấp phép theo [Giấy phép ghi nhận tác giả 4.0 của Creative Commons](https://creativecommons.org/licenses/by/4.0/) và các mẫu mã lập trình được cấp phép theo [Giấy phép Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0). Để biết thông tin chi tiết, vui lòng tham khảo [Chính sách trang web của Google Developers](https://developers.google.com/site-policies?hl=vi). Java là nhãn hiệu đã đăng ký của Oracle và/hoặc các đơn vị liên kết với Oracle.

Cập nhật lần gần đây nhất: 2025-04-29 UTC.

Đã tải xong trang mới..

x1.00

\>

<

\>>

<<

O