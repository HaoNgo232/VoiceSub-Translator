---
title: "Giới hạn số lượng yêu cầu  |  Gemini API  |  Google AI for Developers"
source: "https://ai.google.dev/gemini-api/docs/rate-limits?hl=vi"
author:
published:
created: 2025-05-08
description:
tags:
  - "clippings"
---
Giới hạn tốc độ điều chỉnh số lượng yêu cầu mà bạn có thể gửi tới API Gemini trong một khung thời gian nhất định. Các giới hạn này giúp đảm bảo việc sử dụng công bằng, ngăn chặn hành vi sai trái và giúp duy trì hiệu suất hệ thống cho tất cả người dùng.

## Cách hoạt động của giới hạn tốc độ

Giới hạn tốc độ được đo lường theo 4 phương diện:

- Số yêu cầu mỗi phút (**RPM**)
- Số yêu cầu mỗi ngày (**RPD**)
- Số mã thông báo mỗi phút (**TPM**)
- Số mã thông báo mỗi ngày (**TPD**)

Mức sử dụng của bạn được đánh giá theo từng giới hạn và việc vượt quá bất kỳ giới hạn nào sẽ kích hoạt lỗi giới hạn tốc độ. Ví dụ: nếu giới hạn RPM là 20, thì việc tạo 21 yêu cầu trong vòng một phút sẽ dẫn đến lỗi, ngay cả khi bạn chưa vượt quá TPM hoặc các giới hạn khác.

Hạn mức tốc độ được áp dụng cho mỗi dự án, chứ không phải cho mỗi khoá API.

Các giới hạn sẽ khác nhau tuỳ thuộc vào mô hình cụ thể đang được sử dụng và một số giới hạn chỉ áp dụng cho các mô hình cụ thể. Ví dụ: Số hình ảnh/phút (IPM) chỉ được tính cho các mô hình có thể tạo hình ảnh (Imagen 3), nhưng về mặt khái niệm thì tương tự như TPM.

Giới hạn tốc độ sẽ bị hạn chế hơn đối với các mô hình thử nghiệm và dùng thử.

## Cấp sử dụng

Giới hạn tốc độ được liên kết với cấp sử dụng của dự án. Khi mức sử dụng và mức chi tiêu API tăng lên, bạn có thể nâng cấp lên cấp cao hơn với các giới hạn tốc độ cao hơn.

| Bậc | Điều kiện |
| --- | --- |
| Miễn phí | Người dùng ở [các quốc gia đủ điều kiện](https://ai.google.dev/gemini-api/docs/available-regions?hl=vi) |
| Cấp 1 | Tài khoản thanh toán [đã liên kết với dự án](https://ai.google.dev/gemini-api/docs/billing?hl=vi#enable-cloud-billing) |
| Cấp 2 | Tổng mức chi tiêu: 250 đô la + ít nhất 30 ngày kể từ khi thanh toán thành công |
| Cấp 3 | Tổng mức chi tiêu: 1.000 đô la trở lên và ít nhất 30 ngày kể từ khi thanh toán thành công |

Khi bạn yêu cầu nâng cấp, hệ thống tự động chống hành vi sai trái của chúng tôi sẽ thực hiện thêm các bước kiểm tra. Mặc dù việc đáp ứng các tiêu chí nêu trên thường là đủ để được phê duyệt, nhưng trong một số ít trường hợp, yêu cầu nâng cấp có thể bị từ chối dựa trên các yếu tố khác được xác định trong quá trình xem xét.

Hệ thống này giúp đảm bảo tính bảo mật và tính toàn vẹn của nền tảng API Gemini cho tất cả người dùng.

## Giới hạn số lượng yêu cầu hiện tại

| Mô hình | RPM | TPM | RPD |
| --- | --- | --- | --- |
| Bản xem trước Gemini 2.5 Flash 04-17 | 10 | 250.000 | 500 |
| Gemini 2.5 Pro Experimental 03-25 | 5 | 250.000 TPM   1.000.000 TPD | 25 |
| Bản dùng thử Gemini 2.5 Pro 05-06 | \-- | \-- | \-- |
| Gemini 2.0 Flash | 15 | 1.000.000 | Tăng 1.500 |
| Tạo hình ảnh xem trước Flash Gemini 2.0 | 10 | 200.000 | 100 |
| Gemini 2.0 Flash Experimental | 10 | 1.000.000 | 1.000 |
| Gemini 2.0 Flash-Lite | 30 | 1.000.000 | Tăng 1.500 |
| Gemini 1.5 Flash | 15 | 250.000 | 500 |
| Gemini 1.5 Flash-8B | 15 | 250.000 | 500 |
| Gemini 1.5 Pro | \-- | \-- | \-- |
| Veo 2 | \-- | \-- | \-- |
| Imagen 3 | \-- | \-- | \-- |
| Gemma 3 | 30 | 15.000 | 14.400 |
| Gemini Embedding Experimental 03-07 | 5 | \-- | 100 |

| Mô hình | RPM | TPM | RPD |
| --- | --- | --- | --- |
| Bản xem trước Gemini 2.5 Flash 04-17 | 1.000 | 1.000.000 | 10.000 |
| Bản dùng thử Gemini 2.5 Pro 05-06 | 150 | 2.000.000 | 1.000 |
| Gemini 2.5 Pro Experimental 03-25 | \-- | \-- | \-- |
| Gemini 2.0 Flash | 2.000 | 4.000.000 | \-- |
| Tạo hình ảnh xem trước Flash Gemini 2.0 | 1.000 | 1.000.000 | 10.000 |
| Gemini 2.0 Flash Experimental | 10 | 4.000.000 | \-- |
| Gemini 2.0 Flash-Lite | 4.000 | 4.000.000 | \-- |
| Gemini 1.5 Flash | 2.000 | 4.000.000 | \-- |
| Gemini 1.5 Flash-8B | 4.000 | 4.000.000 | \-- |
| Gemini 1.5 Pro | 1.000 | 4.000.000 | \-- |
| Imagen 3 | \-- | 20 hình ảnh mỗi phút (IPM) | \-- |
| Veo 2 | 2 video/phút (VPM) | \-- | 50 video mỗi ngày (VPD) |
| Gemma 3 | 30 | 15.000 | 14.400 |
| Gemini Embedding Experimental 03-07 | 10 | \-- | 1.000 |

| Mô hình | RPM | TPM | RPD |
| --- | --- | --- | --- |
| Bản xem trước Gemini 2.5 Flash 04-17 | 2.000 | 3.000.000 | 100.000 |
| Gemini 2.5 Pro Experimental 03-25 | \-- | \-- | \-- |
| Bản dùng thử Gemini 2.5 Pro 05-06 | 1.000 | 5.000.000 | 50.000 |
| Gemini 2.0 Flash | 10.000 | 10.000.000 | \-- |
| Tạo hình ảnh xem trước Flash Gemini 2.0 | 2.000 | 3.000.000 | 100.000 |
| Gemini 2.0 Flash Experimental | 10 | 4.000.000 | \-- |
| Gemini 2.0 Flash-Lite | 20.000 | 10.000.000 | \-- |
| Gemini 1.5 Flash | 2.000 | 4.000.000 | \-- |
| Gemini 1.5 Flash-8B | 4.000 | 4.000.000 | \-- |
| Gemini 1.5 Pro | 1.000 | 4.000.000 | \-- |
| Imagen 3 | \-- | 20 hình ảnh mỗi phút (IPM) | \-- |
| Veo 2 | \-- | \-- | \-- |
| Gemma 3 | 30 | 15.000 | 14.400 |
| Gemini Embedding Experimental 03-07 | 10 | \-- | 1.000 |

| Mô hình | RPM | TPM | RPD |
| --- | --- | --- | --- |
| Bản xem trước Gemini 2.5 Flash 04-17 | 10.000 | 8.000.000 | \-- |
| Bản dùng thử Gemini 2.5 Pro 05-06 | 2.000 | 8.000.000 | \-- |
| Gemini 2.0 Flash | 30.000 | 30.000.000 | \-- |
| Tạo hình ảnh xem trước Flash Gemini 2.0 | 5.000 | 5.000.000 | \-- |
| Gemini 2.0 Flash-Lite | 30.000 | 30.000.000 | \-- |

Chúng tôi không đảm bảo các giới hạn tốc độ đã chỉ định và dung lượng thực tế có thể thay đổi.

### Giới hạn tốc độ API trực tiếp

| Số phiên đồng thời | TPM |
| --- | --- |
| 3 | 1.000.000 |

| Số phiên đồng thời | TPM |
| --- | --- |
| 50 | 4.000.000 |

| Số phiên đồng thời | TPM |
| --- | --- |
| 1000 | 10.000.000 |

| Số phiên đồng thời | TPM |
| --- | --- |
| Chưa khả dụng | Chưa khả dụng |

Chúng tôi không đảm bảo các giới hạn tốc độ đã chỉ định và dung lượng thực tế có thể thay đổi.

Gemini API sử dụng Cloud Billing cho tất cả dịch vụ thanh toán. Để chuyển từ cấp Miễn phí sang cấp có tính phí, trước tiên, bạn phải bật tính năng Thanh toán trên đám mây cho dự án Google Cloud của mình.

Sau khi đáp ứng các tiêu chí đã chỉ định, dự án của bạn sẽ đủ điều kiện để nâng cấp lên cấp tiếp theo. Để yêu cầu nâng cấp, hãy làm theo các bước sau:

- Chuyển đến [trang Khoá API](https://aistudio.google.com/app/apikey?hl=vi) trong AI Studio.
- Tìm dự án mà bạn muốn nâng cấp rồi nhấp vào "Nâng cấp". Lựa chọn "Nâng cấp" chỉ xuất hiện đối với những dự án đáp ứng [các tiêu chí của cấp tiếp theo](https://ai.google.dev/gemini-api/docs/rate-limits?hl=vi#usage-tiers).

Sau khi xác thực nhanh, dự án sẽ được nâng cấp lên cấp tiếp theo.

## Yêu cầu tăng giới hạn tốc độ yêu cầu

Mỗi biến thể mô hình đều có giới hạn tốc độ liên quan (yêu cầu mỗi phút, RPM). Để biết thông tin chi tiết về các giới hạn tốc độ đó, hãy xem phần [Mô hình Gemini](https://ai.google.dev/models/gemini?hl=vi).

[Yêu cầu tăng giới hạn tốc độ của cấp có tính phí](https://forms.gle/ETzX94k8jf7iSotH9)

Chúng tôi không đảm bảo về việc tăng hạn mức tốc độ, nhưng chúng tôi sẽ cố gắng hết sức để xem xét yêu cầu của bạn và liên hệ với bạn nếu có thể đáp ứng nhu cầu về dung lượng của bạn.

Trừ phi có lưu ý khác, nội dung của trang này được cấp phép theo [Giấy phép ghi nhận tác giả 4.0 của Creative Commons](https://creativecommons.org/licenses/by/4.0/) và các mẫu mã lập trình được cấp phép theo [Giấy phép Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0). Để biết thông tin chi tiết, vui lòng tham khảo [Chính sách trang web của Google Developers](https://developers.google.com/site-policies?hl=vi). Java là nhãn hiệu đã đăng ký của Oracle và/hoặc các đơn vị liên kết với Oracle.

Cập nhật lần gần đây nhất: 2025-05-07 UTC.

Đã tải xong trang mới..

x1.00

\>

<

\>>

<<

O