---
title: "Mô hình Gemini  |  Gemini API  |  Google AI for Developers"
source: "https://ai.google.dev/gemini-api/docs/models?hl=vi"
author:
published:
created: 2025-05-08
description: "Tìm hiểu về các mô hình AI tiên tiến nhất của Google, bao gồm cả Gemini 2.5 Pro"
tags:
  - "clippings"
---
## Biến thể mô hình

Gemini API cung cấp nhiều mô hình được tối ưu hoá cho các trường hợp sử dụng cụ thể. Dưới đây là thông tin tổng quan ngắn gọn về các biến thể Gemini hiện có:

| Biến thể mô hình | (Các) giá trị đầu vào | Đầu ra | Được tối ưu hoá cho |
| --- | --- | --- | --- |
| [Gemini 2.5 Bản dùng thử Flash 04-17](https://ai.google.dev/gemini-api/docs/?hl=vi#gemini-2.5-flash-preview)   `gemini-2.5-flash-preview-04-17` | Âm thanh, hình ảnh, video và văn bản | Văn bản | Tư duy thích ứng, hiệu quả chi phí |
| [Bản xem trước Gemini 2.5 Pro](https://ai.google.dev/gemini-api/docs/?hl=vi#gemini-2.5-pro-preview-05-06)   `gemini-2.5-pro-preview-05-06` | Âm thanh, hình ảnh, video và văn bản | Văn bản | Nâng cao khả năng tư duy và suy luận, hiểu biết đa phương thức, lập trình nâng cao và nhiều tính năng khác |
| [Gemini 2.0 Flash](https://ai.google.dev/gemini-api/docs/?hl=vi#gemini-2.0-flash)   `gemini-2.0-flash` | Âm thanh, hình ảnh, video và văn bản | Văn bản | Các tính năng thế hệ mới, tốc độ, khả năng suy nghĩ và truyền trực tuyến theo thời gian thực. |
| [Tạo hình ảnh xem trước Flash Gemini 2.0](https://ai.google.dev/gemini-api/docs/?hl=vi#gemini-2.0-flash-preview-image-generation)   `gemini-2.0-flash-preview-image-generation` | Âm thanh, hình ảnh, video và văn bản | Văn bản, hình ảnh | Tạo và chỉnh sửa hình ảnh trò chuyện |
| [Gemini 2.0 Flash-Lite](https://ai.google.dev/gemini-api/docs/?hl=vi#gemini-2.0-flash-lite)   `gemini-2.0-flash-lite` | Âm thanh, hình ảnh, video và văn bản | Văn bản | Chi phí hiệu quả và độ trễ thấp |
| [Gemini 1.5 Flash](https://ai.google.dev/gemini-api/docs/?hl=vi#gemini-1.5-flash)   `gemini-1.5-flash` | Âm thanh, hình ảnh, video và văn bản | Văn bản | Hiệu suất nhanh và linh hoạt trên nhiều tác vụ |
| [Gemini 1.5 Flash-8B](https://ai.google.dev/gemini-api/docs/?hl=vi#gemini-1.5-flash-8b)   `gemini-1.5-flash-8b` | Âm thanh, hình ảnh, video và văn bản | Văn bản | Số lượng lớn và các tác vụ có mức độ thông minh thấp hơn |
| [Gemini 1.5 Pro](https://ai.google.dev/gemini-api/docs/?hl=vi#gemini-1.5-pro)   `gemini-1.5-pro` | Âm thanh, hình ảnh, video và văn bản | Văn bản | Các nhiệm vụ suy luận phức tạp đòi hỏi nhiều trí tuệ hơn |
| [Nhúng Gemini](https://ai.google.dev/gemini-api/docs/?hl=vi#gemini-embedding)   `gemini-embedding-exp` | Văn bản | Nhúng văn bản | Đo lường mức độ liên quan của các chuỗi văn bản |
| [Imagen 3](https://ai.google.dev/gemini-api/docs/?hl=vi#imagen-3)   `imagen-3.0-generate-002` | Văn bản | Hình ảnh | Mô hình tạo ảnh tiên tiến nhất của chúng tôi |
| [Veo 2](https://ai.google.dev/gemini-api/docs/?hl=vi#veo-2)   `veo-2.0-generate-001` | Văn bản, hình ảnh | Video | Tạo video chất lượng cao |
| [Gemini 2.0 Flash Live](https://ai.google.dev/gemini-api/docs/?hl=vi#live-api)   `gemini-2.0-flash-live-001` | Âm thanh, video và văn bản | Văn bản, âm thanh | Tương tác hai chiều bằng giọng nói và video có độ trễ thấp |

Bạn có thể xem hạn mức tốc độ cho từng mô hình trên [trang hạn mức tốc độ](https://ai.google.dev/gemini-api/docs/rate-limits?hl=vi).

### Bản xem trước Gemini 2.5 Flash 04-17

Mô hình tốt nhất của chúng tôi về hiệu suất theo giá, cung cấp nhiều tính năng. Giới hạn tốc độ của Gemini 2.5 Flash bị hạn chế hơn vì đây là mô hình thử nghiệm / xem trước.

[Dùng thử trong Google AI Studio](https://aistudio.google.com/?model=gemini-2.5-flash-preview-04-17&hl=vi)

#### Chi tiết mô hình

| Thuộc tính | Mô tả |
| --- | --- |
| Mã mô hình | `models/gemini-2.5-flash-preview-04-17` |
| Các loại dữ liệu được hỗ trợ | **Thông tin đầu vào**  Văn bản, hình ảnh, video, âm thanh  **Kết quả**  Văn bản |
| Giới hạn mã thông báo <sup><a href="https://ai.google.dev/gemini-api/docs/?hl=vi#token-size">[*]</a></sup> | **Giới hạn mã thông báo đầu vào**  1.048.576  **Giới hạn mã thông báo đầu ra**  65.536 |
| Khả năng của | **Tạo âm thanh**  Không được hỗ trợ  **Lưu vào bộ nhớ đệm**  Không được hỗ trợ  **Thực thi mã**  Được hỗ trợ  **Gọi hàm**  Được hỗ trợ  **Tạo hình ảnh**  Không được hỗ trợ  **Tìm hiểu về việc liên kết với Google Tìm kiếm**  Được hỗ trợ  **Kết quả có cấu trúc**  Được hỗ trợ  **Tư duy**  Được hỗ trợ  **Điều chỉnh**  Không được hỗ trợ |
| Phiên bản | Đọc [các mẫu phiên bản mô hình](https://ai.google.dev/gemini-api/docs/models/gemini?hl=vi#model-versions) để biết thêm chi tiết. - Xem trước: `gemini-2.5-flash-preview-04-17` |
| Thông tin cập nhật mới nhất | Tháng 4 năm 2025 |
| Điểm cắt kiến thức | Tháng 1 năm 2025 |

### Bản xem trước Gemini 2.5 Pro

Gemini 2.5 Pro là mô hình tư duy hiện đại nhất của chúng tôi, có khả năng suy luận về các vấn đề phức tạp trong mã, toán học và STEM, cũng như phân tích các tập dữ liệu lớn, cơ sở mã và tài liệu bằng ngữ cảnh dài. Giới hạn tốc độ của Gemini 2.5 Pro bị hạn chế hơn vì đây là mô hình thử nghiệm / xem trước.

[Dùng thử trong Google AI Studio](https://aistudio.google.com/?model=gemini-2.5-pro-preview-05-06&hl=vi)

#### Chi tiết mô hình

| Thuộc tính | Mô tả |
| --- | --- |
| Mã mô hình | Trả phí: `gemini-2.5-pro-preview-05-06`, Thử nghiệm: `gemini-2.5-pro-exp-03-25` |
| Các loại dữ liệu được hỗ trợ | **Thông tin đầu vào**  Âm thanh, hình ảnh, video và văn bản  **Kết quả**  Văn bản |
| Giới hạn mã thông báo <sup><a href="https://ai.google.dev/gemini-api/docs/?hl=vi#token-size">[*]</a></sup> | **Giới hạn mã thông báo đầu vào**  1.048.576  **Giới hạn mã thông báo đầu ra**  65.536 |
| Khả năng của | **Kết quả có cấu trúc**  Được hỗ trợ  **Lưu vào bộ nhớ đệm**  Được hỗ trợ  **Điều chỉnh**  Không được hỗ trợ  **Gọi hàm**  Được hỗ trợ  **Thực thi mã**  Được hỗ trợ  **Tìm hiểu về việc liên kết với Google Tìm kiếm**  Được hỗ trợ  **Tạo hình ảnh**  Không được hỗ trợ  **Tạo âm thanh**  Không được hỗ trợ  **Live API**  Không được hỗ trợ  **Tư duy**  Được hỗ trợ |
| Phiên bản | Đọc [các mẫu phiên bản mô hình](https://ai.google.dev/gemini-api/docs/models/gemini?hl=vi#model-versions) để biết thêm chi tiết. - Xem trước: `gemini-2.5-pro-preview-05-06` - Thử nghiệm: `gemini-2.5-pro-exp-03-25` |
| Thông tin cập nhật mới nhất | Tháng 5/2025 |
| Điểm cắt kiến thức | Tháng 1 năm 2025 |

### Gemini 2.0 Flash

Gemini 2.0 Flash cung cấp các tính năng thế hệ mới và khả năng cải tiến, bao gồm tốc độ vượt trội, sử dụng công cụ gốc và cửa sổ ngữ cảnh 1 triệu mã thông báo.

[Dùng thử trong Google AI Studio](https://aistudio.google.com/?model=gemini-2.0-flash-001&hl=vi)

#### Chi tiết mô hình

| Thuộc tính | Mô tả |
| --- | --- |
| Mã mô hình | `models/gemini-2.0-flash` |
| Các loại dữ liệu được hỗ trợ | **Thông tin đầu vào**  Âm thanh, hình ảnh, video và văn bản  **Kết quả**  Văn bản |
| Giới hạn mã thông báo <sup><a href="https://ai.google.dev/gemini-api/docs/?hl=vi#token-size">[*]</a></sup> | **Giới hạn mã thông báo đầu vào**  1.048.576  **Giới hạn mã thông báo đầu ra**  8.192 |
| Khả năng của | **Kết quả có cấu trúc**  Được hỗ trợ  **Lưu vào bộ nhớ đệm**  Được hỗ trợ  **Điều chỉnh**  Không được hỗ trợ  **Gọi hàm**  Được hỗ trợ  **Thực thi mã**  Được hỗ trợ  **Tìm kiếm**  Được hỗ trợ  **Tạo hình ảnh**  Không được hỗ trợ  **Tạo âm thanh**  Không được hỗ trợ  **Live API**  Được hỗ trợ  **Tư duy**  Thử nghiệm |
| Phiên bản | Đọc [các mẫu phiên bản mô hình](https://ai.google.dev/gemini-api/docs/models/gemini?hl=vi#model-versions) để biết thêm chi tiết. - Mới nhất: `gemini-2.0-flash` - Ổn định: `gemini-2.0-flash-001` - Thử nghiệm: `gemini-2.0-flash-exp*` và `gemini-2.0-flash-exp-image-generation*` trỏ đến cùng một mô hình cơ bản  gemini-2.0-flash-exp-image-generation hiện không được hỗ trợ ở một số quốc gia ở Châu Âu, Trung Đông và Châu Phi |
| Thông tin cập nhật mới nhất | Tháng 2 năm 2025 |
| Điểm cắt kiến thức | Tháng 8 năm 2024 |

### Tạo hình ảnh xem trước Flash Gemini 2.0

Tính năng Tạo hình ảnh xem trước Gemini 2.0 Flash mang đến các tính năng tạo hình ảnh cải tiến, bao gồm cả việc tạo và chỉnh sửa hình ảnh theo kiểu trò chuyện.

[Dùng thử trong Google AI Studio](https://aistudio.google.com/?model=gemini-2.0-flash-preview-image-generation&hl=vi)

#### Chi tiết mô hình

| Thuộc tính | Mô tả |
| --- | --- |
| Mã mô hình | `models/gemini-2.0-flash-preview-image-generation` |
| Các loại dữ liệu được hỗ trợ | **Thông tin đầu vào**  Âm thanh, hình ảnh, video và văn bản  **Kết quả**  Văn bản và hình ảnh |
| Giới hạn mã thông báo <sup><a href="https://ai.google.dev/gemini-api/docs/?hl=vi#token-size">[*]</a></sup> | **Giới hạn mã thông báo đầu vào**  32.000  **Giới hạn mã thông báo đầu ra**  8.192 |
| Khả năng của | **Kết quả có cấu trúc**  Được hỗ trợ  **Lưu vào bộ nhớ đệm**  Được hỗ trợ  **Điều chỉnh**  Không được hỗ trợ  **Gọi hàm**  Không được hỗ trợ  **Thực thi mã**  Không được hỗ trợ  **Tìm kiếm**  Không được hỗ trợ  **Tạo hình ảnh**  Được hỗ trợ  **Tạo âm thanh**  Không được hỗ trợ  **Live API**  Không được hỗ trợ  **Tư duy**  Không được hỗ trợ |
| Phiên bản | Đọc [các mẫu phiên bản mô hình](https://ai.google.dev/gemini-api/docs/models/gemini?hl=vi#model-versions) để biết thêm chi tiết. - Xem trước: `gemini-2.0-flash-preview-image-generation` - Thử nghiệm: `gemini-2.0-flash-exp-image-generation`  Các mô hình tạo hình ảnh gemini-2.0-flash-\*-hiện không được hỗ trợ ở một số quốc gia ở Châu Âu, Trung Đông và Châu Phi |
| Thông tin cập nhật mới nhất | Tháng 5/2025 |
| Điểm cắt kiến thức | Tháng 8 năm 2024 |

### Gemini 2.0 Flash-Lite

Mô hình Gemini 2.0 Flash được tối ưu hoá để tiết kiệm chi phí và có độ trễ thấp.

[Dùng thử trong Google AI Studio](https://aistudio.google.com/?model=gemini-2.0-flash-lite&hl=vi)

#### Chi tiết mô hình

| Thuộc tính | Mô tả |
| --- | --- |
| Mã mô hình | `models/gemini-2.0-flash-lite` |
| Các loại dữ liệu được hỗ trợ | **Thông tin đầu vào**  Âm thanh, hình ảnh, video và văn bản  **Kết quả**  Văn bản |
| Giới hạn mã thông báo <sup><a href="https://ai.google.dev/gemini-api/docs/?hl=vi#token-size">[*]</a></sup> | **Giới hạn mã thông báo đầu vào**  1.048.576  **Giới hạn mã thông báo đầu ra**  8.192 |
| Khả năng của | **Kết quả có cấu trúc**  Được hỗ trợ  **Lưu vào bộ nhớ đệm**  Được hỗ trợ  **Điều chỉnh**  Không được hỗ trợ  **Gọi hàm**  Được hỗ trợ  **Thực thi mã**  Không được hỗ trợ  **Tìm kiếm**  Không được hỗ trợ  **Tạo hình ảnh**  Không được hỗ trợ  **Tạo âm thanh**  Không được hỗ trợ  **Live API**  Không được hỗ trợ |
| Phiên bản | Đọc [các mẫu phiên bản mô hình](https://ai.google.dev/gemini-api/docs/models/gemini?hl=vi#model-versions) để biết thêm chi tiết. - Mới nhất: `gemini-2.0-flash-lite` - Ổn định: `gemini-2.0-flash-lite-001` |
| Thông tin cập nhật mới nhất | Tháng 2 năm 2025 |
| Điểm cắt kiến thức | Tháng 8 năm 2024 |

### Gemini 1.5 Flash

Gemini 1.5 Flash là một mô hình đa phương thức nhanh chóng và linh hoạt để mở rộng quy mô trên nhiều nhiệm vụ.

[Dùng thử trong Google AI Studio](https://aistudio.google.com/?model=gemini-1.5-flash&hl=vi)

#### Chi tiết mô hình

| Thuộc tính | Mô tả |
| --- | --- |
| Mã mô hình | `models/gemini-1.5-flash` |
| Các loại dữ liệu được hỗ trợ | **Thông tin đầu vào**  Âm thanh, hình ảnh, video và văn bản  **Kết quả**  Văn bản |
| Giới hạn mã thông báo <sup><a href="https://ai.google.dev/gemini-api/docs/?hl=vi#token-size">[*]</a></sup> | **Giới hạn mã thông báo đầu vào**  1.048.576  **Giới hạn mã thông báo đầu ra**  8.192 |
| Quy cách âm thanh/hình ảnh | **Số lượng hình ảnh tối đa cho mỗi câu lệnh**  3.600  **Thời lượng video tối đa**  1 giờ  **Thời lượng âm thanh tối đa**  Khoảng 9,5 giờ |
| Khả năng của | **Hướng dẫn về hệ thống**  Được hỗ trợ  **Chế độ JSON**  Được hỗ trợ  **Giản đồ JSON**  Được hỗ trợ  **Chế độ cài đặt an toàn có thể điều chỉnh**  Được hỗ trợ  **Lưu vào bộ nhớ đệm**  Được hỗ trợ  **Điều chỉnh**  Được hỗ trợ  **Gọi hàm**  Được hỗ trợ  **Thực thi mã**  Được hỗ trợ  **Live API**  Không được hỗ trợ |
| Phiên bản | Đọc [các mẫu phiên bản mô hình](https://ai.google.dev/gemini-api/docs/models/gemini?hl=vi#model-versions) để biết thêm chi tiết. - Mới nhất: `gemini-1.5-flash-latest` - Bản ổn định mới nhất: `gemini-1.5-flash` - Ổn định: - `gemini-1.5-flash-001` 	- `gemini-1.5-flash-002` |
| Thông tin cập nhật mới nhất | Tháng 9 năm 2024 |

### Gemini 1.5 Flash-8B

Gemini 1.5 Flash-8B là một mô hình nhỏ được thiết kế cho các tác vụ có mức độ thông minh thấp hơn.

[Dùng thử trong Google AI Studio](https://aistudio.google.com/?model=gemini-1.5-flash&hl=vi)

#### Chi tiết mô hình

| Thuộc tính | Mô tả |
| --- | --- |
| Mã mô hình | `models/gemini-1.5-flash-8b` |
| Các loại dữ liệu được hỗ trợ | **Thông tin đầu vào**  Âm thanh, hình ảnh, video và văn bản  **Kết quả**  Văn bản |
| Giới hạn mã thông báo <sup><a href="https://ai.google.dev/gemini-api/docs/?hl=vi#token-size">[*]</a></sup> | **Giới hạn mã thông báo đầu vào**  1.048.576  **Giới hạn mã thông báo đầu ra**  8.192 |
| Quy cách âm thanh/hình ảnh | **Số lượng hình ảnh tối đa cho mỗi câu lệnh**  3.600  **Thời lượng video tối đa**  1 giờ  **Thời lượng âm thanh tối đa**  Khoảng 9,5 giờ |
| Khả năng của | **Hướng dẫn về hệ thống**  Được hỗ trợ  **Chế độ JSON**  Được hỗ trợ  **Giản đồ JSON**  Được hỗ trợ  **Chế độ cài đặt an toàn có thể điều chỉnh**  Được hỗ trợ  **Lưu vào bộ nhớ đệm**  Được hỗ trợ  **Điều chỉnh**  Được hỗ trợ  **Gọi hàm**  Được hỗ trợ  **Thực thi mã**  Được hỗ trợ  **Live API**  Không được hỗ trợ |
| Phiên bản | Đọc [các mẫu phiên bản mô hình](https://ai.google.dev/gemini-api/docs/models/gemini?hl=vi#model-versions) để biết thêm chi tiết. - Mới nhất: `gemini-1.5-flash-8b-latest` - Bản ổn định mới nhất: `gemini-1.5-flash-8b` - Ổn định: - `gemini-1.5-flash-8b-001` |
| Thông tin cập nhật mới nhất | Tháng 10 năm 2024 |

### Gemini 1.5 Pro

Dùng thử [Gemini 2.5 Pro Bản dùng thử](https://ai.google.dev/gemini-api/docs/models/experimental-models?hl=vi#available-models), mô hình Gemini tiên tiến nhất của chúng tôi cho đến nay.

Gemini 1.5 Pro là một mô hình đa phương thức cỡ trung được tối ưu hoá cho nhiều nhiệm vụ suy luận. 1.5 Pro có thể xử lý lượng lớn dữ liệu cùng một lúc, bao gồm 2 giờ video, 19 giờ âm thanh, cơ sở mã có 60.000 dòng mã hoặc 2.000 trang văn bản.

[Dùng thử trong Google AI Studio](https://aistudio.google.com/?model=gemini-1.5-pro&hl=vi)

#### Chi tiết mô hình

| Thuộc tính | Mô tả |
| --- | --- |
| Mã mô hình | `models/gemini-1.5-pro` |
| Các loại dữ liệu được hỗ trợ | **Thông tin đầu vào**  Âm thanh, hình ảnh, video và văn bản  **Kết quả**  Văn bản |
| Giới hạn mã thông báo <sup><a href="https://ai.google.dev/gemini-api/docs/?hl=vi#token-size">[*]</a></sup> | **Giới hạn mã thông báo đầu vào**  2.097.152  **Giới hạn mã thông báo đầu ra**  8.192 |
| Quy cách âm thanh/hình ảnh | **Số lượng hình ảnh tối đa cho mỗi câu lệnh**  7.200  **Thời lượng video tối đa**  2 giờ  **Thời lượng âm thanh tối đa**  Khoảng 19 giờ |
| Khả năng của | **Hướng dẫn về hệ thống**  Được hỗ trợ  **Chế độ JSON**  Được hỗ trợ  **Giản đồ JSON**  Được hỗ trợ  **Chế độ cài đặt an toàn có thể điều chỉnh**  Được hỗ trợ  **Lưu vào bộ nhớ đệm**  Được hỗ trợ  **Điều chỉnh**  Không được hỗ trợ  **Gọi hàm**  Được hỗ trợ  **Thực thi mã**  Được hỗ trợ  **Live API**  Không được hỗ trợ |
| Phiên bản | Đọc [các mẫu phiên bản mô hình](https://ai.google.dev/gemini-api/docs/models/gemini?hl=vi#model-versions) để biết thêm chi tiết. - Mới nhất: `gemini-1.5-pro-latest` - Bản ổn định mới nhất: `gemini-1.5-pro` - Ổn định: - `gemini-1.5-pro-001` 	- `gemini-1.5-pro-002` |
| Thông tin cập nhật mới nhất | Tháng 9 năm 2024 |

### Imagen 3

Imagen 3 là mô hình chuyển văn bản thành hình ảnh có chất lượng cao nhất của chúng tôi, có khả năng tạo hình ảnh có độ chi tiết cao hơn, ánh sáng chân thực hơn và ít hiện tượng gây mất tập trung hơn so với các mô hình trước đây.

##### Chi tiết mô hình

| Thuộc tính | Mô tả |
| --- | --- |
| Mã mô hình | **Gemini API**  `imagen-3.0-generate-002` |
| Các loại dữ liệu được hỗ trợ | **Input**  Văn bản  **Kết quả**  Hình ảnh |
| Giới hạn mã thông báo <sup><a href="https://ai.google.dev/gemini-api/docs/?hl=vi#token-size">[*]</a></sup> | **Giới hạn mã thông báo đầu vào**  Không áp dụng  **Hình ảnh đầu ra**  Lên đến 4 |
| Thông tin cập nhật mới nhất | Tháng 2 năm 2025 |

### Veo 2

Veo 2 là mô hình tạo video từ văn bản và hình ảnh chất lượng cao, có khả năng tạo video chi tiết, nắm bắt được sắc thái nghệ thuật trong câu lệnh của bạn.

##### Chi tiết mô hình

| Thuộc tính | Mô tả |
| --- | --- |
| Mã mô hình | **Gemini API**  `veo-2.0-generate-001` |
| Các loại dữ liệu được hỗ trợ | **Input**  Văn bản, hình ảnh  **Kết quả**  Video |
| Giới hạn | **Nhập văn bản**  Không áp dụng  **Dữ liệu đầu vào hình ảnh**  Độ phân giải và tỷ lệ khung hình hình ảnh bất kỳ, kích thước tệp tối đa là 20 MB  **Đầu ra video**  Tối đa 2 |
| Thông tin cập nhật mới nhất | Tháng 4 năm 2025 |

### Gemini 2.0 Flash Live

Mô hình Gemini 2.0 Flash Live hoạt động với Live API để cho phép tương tác hai chiều bằng giọng nói và video với độ trễ thấp với Gemini. Mô hình này có thể xử lý dữ liệu đầu vào là văn bản, âm thanh và video, đồng thời có thể cung cấp dữ liệu đầu ra là văn bản và âm thanh.

[Dùng thử trong Google AI Studio](https://aistudio.google.com/?model=gemini-2.0-flash-live-001&hl=vi)

#### Chi tiết mô hình

| Thuộc tính | Mô tả |
| --- | --- |
| Mã mô hình | `models/gemini-2.0-flash-live-001` |
| Các loại dữ liệu được hỗ trợ | **Thông tin đầu vào**  Âm thanh, video và văn bản  **Kết quả**  Văn bản và âm thanh |
| Giới hạn mã thông báo <sup><a href="https://ai.google.dev/gemini-api/docs/?hl=vi#token-size">[*]</a></sup> | **Giới hạn mã thông báo đầu vào**  1.048.576  **Giới hạn mã thông báo đầu ra**  8.192 |
| Khả năng của | **Kết quả có cấu trúc**  Được hỗ trợ  **Điều chỉnh**  Không được hỗ trợ  **Gọi hàm**  Được hỗ trợ  **Thực thi mã**  Được hỗ trợ  **Tìm kiếm**  Được hỗ trợ  **Tạo hình ảnh**  Không được hỗ trợ  **Tạo âm thanh**  Được hỗ trợ  **Tư duy**  Không được hỗ trợ |
| Phiên bản | Đọc [các mẫu phiên bản mô hình](https://ai.google.dev/gemini-api/docs/models/gemini?hl=vi#model-versions) để biết thêm chi tiết. - Xem trước: `gemini-2.0-flash-live-001` |
| Thông tin cập nhật mới nhất | Tháng 4 năm 2025 |
| Điểm cắt kiến thức | Tháng 8 năm 2024 |

### Thử nghiệm nhúng Gemini

`Gemini embedding` đạt được [hiệu suất SOTA](https://deepmind.google/research/publications/157741/?hl=vi) trên nhiều phương diện chính, bao gồm cả mã, đa ngôn ngữ và truy xuất. Giới hạn tốc độ nhúng Gemini bị hạn chế hơn vì đây là mô hình thử nghiệm.

##### Chi tiết mô hình

| Thuộc tính | Mô tả |
| --- | --- |
| Mã mô hình | **Gemini API**  `gemini-embedding-exp-03-07` |
| Các loại dữ liệu được hỗ trợ | **Input**  Văn bản  **Kết quả**  Nhúng văn bản |
| Giới hạn mã thông báo <sup><a href="https://ai.google.dev/gemini-api/docs/?hl=vi#token-size">[*]</a></sup> | **Giới hạn mã thông báo đầu vào**  8.192  **Kích thước phương diện đầu ra**  Co giãn, hỗ trợ: 3072, 1536 hoặc 768 |
| Thông tin cập nhật mới nhất | Tháng 3 năm 2025 |

### Nhúng văn bản và nhúng

#### Nhúng văn bản

Dùng thử [mô hình nhúng Gemini thử nghiệm](https://developers.googleblog.com/en/gemini-embedding-text-model-now-available-gemini-api/) mới của chúng tôi, giúp đạt được hiệu suất tiên tiến nhất.

[Nội dung nhúng văn bản](https://ai.google.dev/gemini-api/docs/embeddings?hl=vi) được dùng để đo lường mức độ liên quan của các chuỗi và được sử dụng rộng rãi trong nhiều ứng dụng AI.

`text-embedding-004` đạt được [hiệu suất truy xuất mạnh mẽ hơn và vượt trội so với các mô hình hiện có](https://arxiv.org/pdf/2403.20327) với các phương diện tương đương, dựa trên điểm chuẩn nhúng MTEB tiêu chuẩn.

##### Chi tiết mô hình

| Thuộc tính | Mô tả |
| --- | --- |
| Mã mô hình | **Gemini API**  `models/text-embedding-004` |
| Các loại dữ liệu được hỗ trợ | **Input**  Văn bản  **Kết quả**  Nhúng văn bản |
| Giới hạn mã thông báo <sup><a href="https://ai.google.dev/gemini-api/docs/?hl=vi#token-size">[*]</a></sup> | **Giới hạn mã thông báo đầu vào**  2.048  **Kích thước phương diện đầu ra**  768 |
| Giới hạn tốc độ <sup><a href="https://ai.google.dev/gemini-api/docs/?hl=vi#rate-limits">[**]</a></sup> | 1.500 yêu cầu mỗi phút |
| Chế độ cài đặt an toàn có thể điều chỉnh | Không được hỗ trợ |
| Thông tin cập nhật mới nhất | Tháng 4 năm 2024 |

#### Nhúng

Bạn có thể sử dụng mô hình Nhúng để tạo [nội dung nhúng văn bản](https://ai.google.dev/gemini-api/docs/embeddings?hl=vi) cho văn bản đầu vào.

Mô hình nhúng được tối ưu hoá để tạo các mục nhúng có 768 phương diện cho văn bản có tối đa 2.048 mã thông báo.

##### Nhúng thông tin chi tiết về mô hình

| Thuộc tính | Mô tả |
| --- | --- |
| Mã mô hình | `models/embedding-001` |
| Các loại dữ liệu được hỗ trợ | **Input**  Văn bản  **Kết quả**  Nhúng văn bản |
| Giới hạn mã thông báo <sup><a href="https://ai.google.dev/gemini-api/docs/?hl=vi#token-size">[*]</a></sup> | **Giới hạn mã thông báo đầu vào**  2.048  **Kích thước phương diện đầu ra**  768 |
| Giới hạn tốc độ <sup><a href="https://ai.google.dev/gemini-api/docs/?hl=vi#rate-limits">[**]</a></sup> | 1.500 yêu cầu mỗi phút |
| Chế độ cài đặt an toàn có thể điều chỉnh | Không được hỗ trợ |
| Thông tin cập nhật mới nhất | Tháng 12 năm 2023 |

### AQA

Bạn có thể sử dụng mô hình AQA để thực hiện các nhiệm vụ liên quan đến tính năng [Trả lời câu hỏi được phân bổ](https://ai.google.dev/gemini-api/docs/semantic_retrieval?hl=vi) (AQA) trên một tài liệu, tập hợp văn bản hoặc một tập hợp các đoạn văn. Mô hình AQA trả về câu trả lời cho các câu hỏi dựa trên các nguồn được cung cấp, cùng với việc ước tính xác suất có thể trả lời.

#### Chi tiết mô hình

| Thuộc tính | Mô tả |
| --- | --- |
| Mã mô hình | `models/aqa` |
| Các loại dữ liệu được hỗ trợ | **Input**  Văn bản  **Kết quả**  Văn bản |
| Ngôn ngữ được hỗ trợ | Tiếng Anh |
| Giới hạn mã thông báo <sup><a href="https://ai.google.dev/gemini-api/docs/?hl=vi#token-size">[*]</a></sup> | **Giới hạn mã thông báo đầu vào**  7.168  **Giới hạn mã thông báo đầu ra**  1.024 |
| Giới hạn tốc độ <sup><a href="https://ai.google.dev/gemini-api/docs/?hl=vi#rate-limits">[**]</a></sup> | 1.500 yêu cầu mỗi phút |
| Chế độ cài đặt an toàn có thể điều chỉnh | Được hỗ trợ |
| Thông tin cập nhật mới nhất | Tháng 12 năm 2023 |

Hãy xem [các ví dụ](https://ai.google.dev/examples?hl=vi) để khám phá khả năng của các biến thể mô hình này.

\[\*\] Một mã thông báo tương đương với khoảng 4 ký tự đối với các mô hình Gemini. 100 mã thông báo tương đương với khoảng 60-80 từ tiếng Anh.

## Mẫu tên phiên bản mô hình

Các mô hình Gemini có sẵn ở phiên bản *ổn định*, *xem trước* hoặc *thử nghiệm*. Trong mã, bạn có thể sử dụng một trong các định dạng tên mô hình sau đây để chỉ định mô hình và phiên bản mà bạn muốn sử dụng.

### Bản phát hành ổn định mới nhất

Chỉ đến phiên bản ổn định mới nhất được phát hành cho phiên bản và biến thể mô hình đã chỉ định.

Để chỉ định phiên bản ổn định mới nhất, hãy sử dụng mẫu sau:`<model>-<generation>-<variation>`. Ví dụ: `gemini-2.0-flash`.

### Ổn định

Chỉ đến một mô hình ổn định cụ thể. Các mô hình ổn định thường không thay đổi. Hầu hết các ứng dụng phát hành công khai đều nên sử dụng một mô hình ổn định cụ thể.

Để chỉ định một phiên bản ổn định, hãy sử dụng mẫu sau: `<model>-<generation>-<variation>-<version>`. Ví dụ: `gemini-2.0-flash-001`.

### Xem trước

Chỉ đến một mô hình xem trước có thể không phù hợp để sử dụng trong môi trường thực tế, có giới hạn tốc độ nghiêm ngặt hơn nhưng có thể đã bật tính năng thanh toán.

Để chỉ định phiên bản xem trước, hãy sử dụng mẫu sau:`<model>-<generation>-<variation>-<version>`. Ví dụ: `gemini-2.5-pro-preview-05-06`.

### Thử nghiệm

Chỉ đến một mô hình thử nghiệm có thể không phù hợp để sử dụng trong sản xuất và có các giới hạn tốc độ nghiêm ngặt hơn. Chúng tôi phát hành các mô hình thử nghiệm để thu thập phản hồi và nhanh chóng cung cấp các bản cập nhật mới nhất cho nhà phát triển.

Để chỉ định một phiên bản thử nghiệm, hãy sử dụng mẫu sau:`<model>-<generation>-<variation>-<version>`. Ví dụ: `gemini-2.0-pro-exp-02-05`.

## Mô hình thử nghiệm

Ngoài các mô hình ổn định, Gemini API còn cung cấp các mô hình thử nghiệm có thể không phù hợp để sử dụng trong sản xuất và có giới hạn tốc độ nghiêm ngặt hơn.

Chúng tôi phát hành các mô hình thử nghiệm để thu thập ý kiến phản hồi, nhanh chóng cung cấp các bản cập nhật mới nhất cho nhà phát triển và nêu bật tốc độ đổi mới đang diễn ra tại Google. Những gì chúng tôi học được từ các bản phát hành thử nghiệm sẽ giúp chúng tôi có thêm kinh nghiệm để phát hành các mô hình trên phạm vi rộng hơn. Chúng tôi có thể hoán đổi một mô hình thử nghiệm cho một mô hình khác mà không cần thông báo trước. Chúng tôi không đảm bảo rằng mô hình thử nghiệm sẽ trở thành mô hình ổn định trong tương lai.

### Các mô hình thử nghiệm trước

Khi các phiên bản mới hoặc bản phát hành ổn định ra mắt, chúng tôi sẽ xoá và thay thế các mô hình thử nghiệm. Bạn có thể tìm thấy các mô hình thử nghiệm trước đây mà chúng tôi đã phát hành trong phần sau cùng với phiên bản thay thế:

| Mã mô hình | Mô hình cơ sở | Phiên bản thay thế |
| --- | --- | --- |
| `gemini-2.5-pro-preview-03-25` | Bản xem trước Gemini 2.5 Pro | `gemini-2.5-pro-preview-05-06` |
| `gemini-2.0-flash-thinking-exp-01-21` | Gemini 2.5 Flash | `gemini-2.5-flash-preview-04-17` |
| `gemini-2.0-pro-exp-02-05` | Gemini 2.0 Pro Experimental | `gemini-2.5-pro-preview-03-25` |
| `gemini-2.0-flash-exp` | Gemini 2.0 Flash | `gemini-2.0-flash` |
| `gemini-exp-1206` | Gemini 2.0 Pro | `gemini-2.0-pro-exp-02-05` |
| `gemini-2.0-flash-thinking-exp-1219` | Gemini 2.0 Flash Thinking | `gemini-2.0-flash-thinking-exp-01-21` |
| `gemini-exp-1121` | Gemini | `gemini-exp-1206` |
| `gemini-exp-1114` | Gemini | `gemini-exp-1206` |
| `gemini-1.5-pro-exp-0827` | Gemini 1.5 Pro | `gemini-exp-1206` |
| `gemini-1.5-pro-exp-0801` | Gemini 1.5 Pro | `gemini-exp-1206` |
| `gemini-1.5-flash-8b-exp-0924` | Gemini 1.5 Flash-8B | `gemini-1.5-flash-8b` |
| `gemini-1.5-flash-8b-exp-0827` | Gemini 1.5 Flash-8B | `gemini-1.5-flash-8b` |

## Ngôn ngữ được hỗ trợ

Các mô hình Gemini được huấn luyện để hoạt động với các ngôn ngữ sau:

- Tiếng Ả Rập (`ar`)
- Tiếng Bengal (`bn`)
- Tiếng Bulgaria (`bg`)
- Tiếng Trung giản thể và phồn thể (`zh`)
- Tiếng Croatia (`hr`)
- Tiếng Séc (`cs`)
- Tiếng Đan Mạch (`da`)
- Tiếng Hà Lan (`nl`)
- Tiếng Anh (`en`)
- Tiếng Estonia (`et`)
- Tiếng Phần Lan (`fi`)
- Tiếng Pháp (`fr`)
- Tiếng Đức (`de`)
- Tiếng Hy Lạp (`el`)
- Tiếng Do Thái (`iw`)
- Tiếng Hindi (`hi`)
- Tiếng Hungary (`hu`)
- Tiếng Indonesia (`id`)
- Tiếng Ý (`it`)
- Tiếng Nhật (`ja`)
- Tiếng Hàn (`ko`)
- Tiếng Latvia (`lv`)
- Tiếng Lithuania (`lt`)
- Tiếng Na Uy (`no`)
- Tiếng Ba Lan (`pl`)
- Tiếng Bồ Đào Nha (`pt`)
- Tiếng Romania (`ro`)
- Tiếng Nga (`ru`)
- Tiếng Serbia (`sr`)
- Tiếng Slovak (`sk`)
- Tiếng Slovenia (`sl`)
- Tiếng Tây Ban Nha (`es`)
- Tiếng Swahili (`sw`)
- Tiếng Thuỵ Điển (`sv`)
- Tiếng Thái (`th`)
- Tiếng Thổ Nhĩ Kỳ (`tr`)
- Tiếng Ukraina (`uk`)
- Tiếng Việt (`vi`)

Trừ phi có lưu ý khác, nội dung của trang này được cấp phép theo [Giấy phép ghi nhận tác giả 4.0 của Creative Commons](https://creativecommons.org/licenses/by/4.0/) và các mẫu mã lập trình được cấp phép theo [Giấy phép Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0). Để biết thông tin chi tiết, vui lòng tham khảo [Chính sách trang web của Google Developers](https://developers.google.com/site-policies?hl=vi). Java là nhãn hiệu đã đăng ký của Oracle và/hoặc các đơn vị liên kết với Oracle.

Cập nhật lần gần đây nhất: 2025-05-07 UTC.

Đã tải xong trang mới..

x1.00

\>

<

\>>

<<

O