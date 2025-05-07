import os
import re
import logging
from typing import List, Optional
# Đảm bảo import đúng class từ api_handler
from api_handler import GroqAPIHandler

# Logging sẽ được cấu hình ở main.py
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SubtitleProcessor:
    # Markers cho việc đánh dấu block
    BLOCK_START = "---BLOCK"
    BLOCK_END = "---END BLOCK"
    MAX_BLOCKS_PER_REQUEST = 10  # Giới hạn số block mỗi request
    
    def __init__(self, api_handler: GroqAPIHandler): # Nhận instance của GroqAPIHandler
        self.api_handler = api_handler
        # Pattern để kiểm tra ký tự tiếng Việt (có thể cần tinh chỉnh)
        self.vietnamese_pattern = re.compile(r'[\u00C0-\u1EF9]')
        # Pattern để tách các khối phụ đề SRT
        self.srt_block_pattern = re.compile(r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n([\s\S]*?)(?=\n\n|\Z)', re.MULTILINE)

    def scan_directory(self, directory: str) -> List[str]:
        """Quét thư mục và các thư mục con để tìm file .srt."""
        srt_files = []
        logging.info(f"Bắt đầu quét thư mục: {directory}")
        for root, _, files in os.walk(directory):
            for file in files:
                if not file.lower().endswith('.srt'):
                    continue
                
                file_path = os.path.join(root, file)
                base_name = os.path.splitext(file)[0]
                
                # Kiểm tra xem file có phải là file đã dịch (_vi.srt)
                if base_name.endswith('_vi'):
                    srt_files.append(file_path)
                    continue
                
                # Kiểm tra xem đã có file dịch chưa
                vi_file = os.path.join(root, f"{base_name}_vi.srt")
                if os.path.exists(vi_file):
                    # Kiểm tra nội dung file dịch
                    try:
                        with open(vi_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Nếu không có marker lỗi, coi như file đã dịch hoàn chỉnh
                            if '[DỊCH LỖI]' not in content and '[DỊCH LỖI - KHÔNG KHỚP BLOCK]' not in content:
                                continue  # Bỏ qua file gốc nếu file dịch đã hoàn chỉnh
                    except Exception as e:
                        logging.warning(f"Không thể đọc file dịch {vi_file}: {e}")
                
                # Thêm file gốc vào danh sách nếu chưa có file dịch hoặc file dịch có lỗi
                srt_files.append(file_path)
        
        logging.info(f"Tìm thấy {len(srt_files)} file .srt cần xử lý.")
        return srt_files

    def process_directory(self, directory: str) -> str:
        """Xử lý tất cả các file .srt trong thư mục đã cho."""
        srt_files = self.scan_directory(directory)
        processed_files = 0
        translated_segments = 0
        errors = 0

        for file_path in srt_files:
            logging.info(f"Đang xử lý file: {file_path}")
            try:
                count = self.process_subtitle_file(file_path)
                if count > 0:
                    translated_segments += count
                    processed_files += 1
                elif count == 0: # File đã được dịch hoàn toàn hoặc không có gì để dịch
                     processed_files += 1
                else: # count == -1 -> Lỗi xử lý file
                    errors += 1
            except Exception as e:
                logging.error(f"Lỗi khi xử lý file {file_path}: {e}")
                errors += 1

        return f"Đã xử lý {processed_files}/{len(srt_files)} file. Dịch {translated_segments} đoạn. Gặp {errors} lỗi."

    def process_subtitle_file(self, file_path: str) -> int:
        """Đọc, xử lý và lưu file phụ đề."""
        try:
            # Thử đọc với utf-8-sig trước (phổ biến cho file SRT từ Windows)
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
        except FileNotFoundError:
            logging.error(f"Lỗi: Không tìm thấy file {file_path}")
            return -1
        except UnicodeDecodeError:
            logging.warning(f"Lỗi giải mã UTF-8 cho file {file_path}. Thử lại với encoding 'latin-1'.")
            try:
                # Thử encoding khác nếu utf-8 thất bại
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
            except Exception as e_inner:
                logging.error(f"Không thể đọc file {file_path} với cả UTF-8 và latin-1: {e_inner}")
                return -1
        except IOError as e:
            logging.error(f"Lỗi IO khi đọc file {file_path}: {e}")
            return -1
        except Exception as e: # Bắt các lỗi không mong muốn khác
            logging.error(f"Lỗi không xác định khi đọc file {file_path}: {e}")
            return -1

        # Kiểm tra file đã dịch trước đó
        existing_translated_file = os.path.join(os.path.dirname(file_path), f"{os.path.splitext(os.path.basename(file_path))[0]}_vi.srt")
        existing_blocks = {}
        if os.path.exists(existing_translated_file):
            try:
                with open(existing_translated_file, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
                existing_parsed = self.parse_srt_content(existing_content)
                for idx, _, _, text in existing_parsed:
                    if '[DỊCH THÀNH CÔNG]' in text:
                        # Lưu text đã được dịch thành công (bỏ prefix)
                        existing_blocks[idx] = text.replace('[DỊCH THÀNH CÔNG] ', '')
                    elif '[DỊCH LỖI]' in text or '[DỊCH LỖI - KHÔNG KHỚP BLOCK]' in text:
                        # Đánh dấu block cần dịch lại
                        existing_blocks[idx] = None
            except Exception as e:
                logging.warning(f"Không thể đọc file đã dịch trước đó: {e}")

        blocks = self.parse_srt_content(content)
        if not blocks:
            logging.warning(f"Không tìm thấy khối phụ đề hợp lệ nào trong file: {file_path}")
            return 0 # Không có gì để xử lý

        translated_blocks_content = []
        segments_to_translate = 0
        translated_count = 0
        failed_count = 0
        skipped_count = 0
        current_batch = []
        batch_count = 0

        # Thu thập và xử lý các block theo batch
        for index, start_time, end_time, text in blocks:
            # Nếu block đã dịch thành công trước đó, sử dụng lại
            if index in existing_blocks and existing_blocks[index] is not None:
                translated_blocks_content.append(f"{index}\n{start_time} --> {end_time}\n{existing_blocks[index]}")
                skipped_count += 1
                continue

            original_block_text = f"{index}\n{start_time} --> {end_time}\n{text}"
            
            # Dịch lại nếu block chưa được dịch hoặc bị lỗi trước đó
            if not self.is_translated(text) or index in existing_blocks:
                segments_to_translate += 1
                
                # Nếu batch đạt giới hạn, xử lý batch hiện tại
                if len(current_batch) >= self.MAX_BLOCKS_PER_REQUEST:
                    batch_result = self._translate_batch(current_batch, batch_count)
                    translated_count += batch_result['translated']
                    failed_count += batch_result['failed']
                    translated_blocks_content.extend(batch_result['blocks'])
                    current_batch = []
                    batch_count += 1
                
                block_text = f"{self.BLOCK_START} {len(current_batch) + 1}---\n{text}\n{self.BLOCK_END} {len(current_batch) + 1}---"
                current_batch.append({
                    'index': index,
                    'start_time': start_time,
                    'end_time': end_time,
                    'text': block_text,
                    'original': text
                })
            else:
                skipped_count += 1
                translated_blocks_content.append(original_block_text)

        # Xử lý batch cuối cùng nếu có
        if current_batch:
            batch_result = self._translate_batch(current_batch, batch_count)
            translated_count += batch_result['translated']
            failed_count += batch_result['failed']
            translated_blocks_content.extend(batch_result['blocks'])

        # Ghi log tổng kết và lưu file
        total_blocks = len(blocks)
        file_basename = os.path.basename(file_path)
        log_message = (
            f"File '{file_basename}': "
            f"Tổng cộng {total_blocks} khối. "
            f"Cần dịch: {segments_to_translate}. "
            f"Đã dịch: {translated_count}. "
            f"Lỗi dịch: {failed_count}. "
            f"Bỏ qua (đã dịch/không cần): {skipped_count}."
        )

        if translated_count > 0 or failed_count > 0:
            logging.info(log_message)
            self.save_translated_file(file_path, translated_blocks_content)
            return translated_count
        elif segments_to_translate == 0:
            logging.info(f"File '{file_basename}' không có đoạn nào cần dịch (Tổng cộng {total_blocks} khối).")
            return 0
        else:
            logging.warning(f"File '{file_basename}': Không dịch được đoạn nào trong số {segments_to_translate} đoạn cần dịch (Lỗi: {failed_count}).")
            if failed_count > 0:
                self.save_translated_file(file_path, translated_blocks_content)
            return 0

    def _translate_batch(self, batch, batch_number):
        """Xử lý một batch các block cần dịch."""
        result = {
            'translated': 0,
            'failed': 0,
            'blocks': []
        }

        # Gộp các block trong batch
        combined_text = "\n".join(block['text'] for block in batch)
        logging.info(f"Xử lý batch #{batch_number + 1} với {len(batch)} block")

        # Gửi request dịch
        translated_combined = self.api_handler.translate_text(combined_text)
        
        if translated_combined:
            # Tách kết quả dịch thành các block riêng biệt
            translated_blocks = self._split_translated_blocks(translated_combined)
            
            if len(translated_blocks) == len(batch):
                # Map kết quả dịch về các block gốc
                for i, translated_text in enumerate(translated_blocks):
                    block = batch[i]
                    translated_block = f"{block['index']}\n{block['start_time']} --> {block['end_time']}\n[DỊCH THÀNH CÔNG] {translated_text.strip()}"
                    result['blocks'].append(translated_block)
                    result['translated'] += 1
                    logging.info(f"Batch #{batch_number + 1} - Block #{block['index']}: Dịch thành công")
            else:
                # Xử lý lỗi không khớp số block
                logging.error(f"Batch #{batch_number + 1}: Số block sau khi dịch ({len(translated_blocks)}) không khớp với số block gốc ({len(batch)})")
                for block in batch:
                    error_block = f"{block['index']}\n{block['start_time']} --> {block['end_time']}\n[DỊCH LỖI - KHÔNG KHỚP BLOCK] {block['original']}"
                    result['blocks'].append(error_block)
                    result['failed'] += 1
        else:
            # Xử lý lỗi dịch toàn bộ batch
            logging.error(f"Lỗi dịch batch #{batch_number + 1}")
            for block in batch:
                error_block = f"{block['index']}\n{block['start_time']} --> {block['end_time']}\n[DỊCH LỖI] {block['original']}"
                result['blocks'].append(error_block)
                result['failed'] += 1

        # Log kết quả của batch
        logging.info(f"Kết quả batch #{batch_number + 1}: "
                    f"Thành công: {result['translated']}, "
                    f"Lỗi: {result['failed']}")
        return result

    def _split_translated_blocks(self, translated_text):
        """Tách văn bản đã dịch thành các block riêng biệt."""
        blocks = []
        pattern = f"{self.BLOCK_START} (\\d+)---\\n(.*?)\\n{self.BLOCK_END} \\1---"
        matches = re.finditer(pattern, translated_text, re.DOTALL)
        
        return [match.group(2).strip() for match in matches]

        # Ghi log tổng kết cho file
        total_blocks = len(blocks)
        file_basename = os.path.basename(file_path)
        log_message = (
            f"File '{file_basename}': "
            f"Tổng cộng {total_blocks} khối. "
            f"Cần dịch: {segments_to_translate}. "
            f"Đã dịch: {translated_count}. "
            f"Lỗi dịch: {failed_count}. "
            f"Bỏ qua (đã dịch/không cần): {skipped_count}."
        )

        # Chỉ lưu file nếu có thay đổi (dịch thành công hoặc có lỗi được đánh dấu)
        if translated_count > 0 or failed_count > 0:
            logging.info(log_message)
            self.save_translated_file(file_path, translated_blocks_content)
            return translated_count # Trả về số lượng dịch thành công
        elif segments_to_translate == 0:
             logging.info(f"File '{file_basename}' không có đoạn nào cần dịch (Tổng cộng {total_blocks} khối).")
             return 0 # Không có gì được dịch
        else: # segments_to_translate > 0 nhưng translated_count == 0 và failed_count == 0 (trường hợp này không nên xảy ra với logic hiện tại, nhưng để phòng ngừa)
             logging.warning(f"File '{file_basename}': Không dịch được đoạn nào trong số {segments_to_translate} đoạn cần dịch (Lỗi: {failed_count}).")
             # Vẫn lưu file nếu có lỗi được đánh dấu
             if failed_count > 0:
                 self.save_translated_file(file_path, translated_blocks_content)
             return 0 # Không có gì được dịch thành công


    def parse_srt_content(self, content: str) -> List[tuple]:
        """Phân tích nội dung SRT thành các khối (index, start, end, text)."""
        blocks = []
        for match in self.srt_block_pattern.finditer(content):
            index = match.group(1)
            start_time = match.group(2)
            end_time = match.group(3)
            text = match.group(4).strip()
            blocks.append((index, start_time, end_time, text))
        return blocks

    def is_translated(self, text: str) -> bool:
        """Kiểm tra xem văn bản có chứa ký tự tiếng Việt không."""
        # Có thể thêm logic kiểm tra phức tạp hơn nếu cần
        # Ví dụ: kiểm tra tỷ lệ ký tự tiếng Việt, hoặc bỏ qua các dòng chỉ chứa số/ký tự đặc biệt
        lines = text.split('\n')
        # Chỉ kiểm tra các dòng chứa chữ cái
        text_lines = [line for line in lines if re.search(r'[a-zA-Z]', line)]
        if not text_lines:
            return False # Bỏ qua nếu không có dòng chữ nào
        # Kiểm tra sự hiện diện của tiếng Việt trong các dòng chữ
        return any(self.vietnamese_pattern.search(line) for line in text_lines)

    # Hàm translate_block và apply_translation không còn cần thiết vì logic đã tích hợp vào process_subtitle_file

    def save_translated_file(self, original_file_path: str, translated_blocks: List[str]):
        """Lưu các khối đã dịch vào file mới."""
        dir_name = os.path.dirname(original_file_path)
        base_name = os.path.basename(original_file_path)
        name, ext = os.path.splitext(base_name)
        new_file_name = f"{name}_vi{ext}"
        new_file_path = os.path.join(dir_name, new_file_name)

        # Kiểm tra nếu tất cả các block đã dịch thành công
        all_successful = all('[DỊCH THÀNH CÔNG]' in block for block in translated_blocks)
        if all_successful:
            # Nếu tất cả đã thành công, xóa prefix
            cleaned_blocks = []
            for block in translated_blocks:
                lines = block.split('\n')
                if len(lines) >= 3:  # Đảm bảo block có đủ 3 dòng
                    text_line = lines[2].replace('[DỊCH THÀNH CÔNG] ', '')
                    cleaned_block = f"{lines[0]}\n{lines[1]}\n{text_line}"
                    cleaned_blocks.append(cleaned_block)
                else:
                    cleaned_blocks.append(block)  # Giữ nguyên nếu block không đủ dòng
            translated_blocks = cleaned_blocks

        try:
            with open(new_file_path, 'w', encoding='utf-8') as f:
                f.write('\n\n'.join(translated_blocks))
            logging.info(f"Đã lưu file đã dịch vào: {new_file_path}")
            if all_successful:
                logging.info(f"Tất cả các block đã dịch thành công và đã xóa prefix trạng thái")
        except IOError as e:
            logging.error(f"Lỗi IO khi lưu file {new_file_path}: {e}")
        except Exception as e:
            logging.error(f"Lỗi không xác định khi lưu file {new_file_path}: {e}")
