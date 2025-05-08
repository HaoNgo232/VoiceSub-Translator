#!/usr/bin/env python3
import os
import subprocess
import logging
import argparse
from pathlib import Path
from src.api.handler import APIHandler
from src.translator.subtitle import SubtitleTranslator
from src.utils.subtitle_generator import generate_subtitles

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('course_processing.log'),
        logging.StreamHandler()
    ]
)

def process_video(input_video, translate=False):
    """Xử lý một video và tạo phụ đề SRT tại vị trí video gốc"""
    try:
        # Tạo tên file output SRT cùng vị trí với video
        video_path = Path(input_video)
        output_srt = video_path.with_suffix('.srt')
        
        # Kiểm tra nếu file phụ đề đã tồn tại
        if output_srt.exists():
            logging.info(f"Video {video_path.name} đã có phụ đề SRT, bỏ qua")
            return True
        
        logging.info(f"Đang xử lý video: {video_path.name}")
        
        # Tạo phụ đề SRT
        generate_subtitles(str(video_path), str(output_srt), model_name="small.en")
        logging.info(f"Đã tạo phụ đề SRT cho video {video_path.name}")

        # Dịch phụ đề nếu được yêu cầu
        if translate:
            logging.info(f"Bắt đầu dịch phụ đề cho video {video_path.name}")
            api_handler = APIHandler()
            translator = SubtitleTranslator(api_handler)
            result = translator.process_subtitle_file(str(output_srt), str(output_srt.with_stem(f"{output_srt.stem}_vi")))
            if result:
                logging.info(f"Đã dịch phụ đề cho video {video_path.name}")
            else:
                logging.warning(f"Không thể dịch phụ đề cho video {video_path.name}")
        
        return True

    except Exception as e:
        logging.error(f"Lỗi khi xử lý video {input_video}: {str(e)}")
        return False

def main():
    # Thiết lập argument parser
    parser = argparse.ArgumentParser(description='Tạo và dịch phụ đề cho video')
    parser.add_argument('--translate', action='store_true', help='Dịch phụ đề sang tiếng Việt')
    args = parser.parse_args()

    # Lấy danh sách video trong thư mục Khoa_hoc_mau
    video_dir = "Khoa_hoc_mau"
    video_files = sorted([f for f in os.listdir(video_dir) if f.endswith(('.mp4', '.MP4'))])
    
    total_videos = len(video_files)
    logging.info(f"Tìm thấy {total_videos} video để xử lý")
    if args.translate:
        logging.info("Chế độ dịch phụ đề đã được bật")
    
    # Xử lý từng video
    success_count = 0
    skipped_count = 0
    
    for video_file in video_files:
        input_path = os.path.join(video_dir, video_file)
        
        # Kiểm tra nếu đã có file SRT
        if os.path.exists(input_path.replace('.mp4', '.srt')):
            if args.translate:
                # Nếu bật chế độ dịch, kiểm tra file dịch
                vi_file = input_path.replace('.mp4', '_vi.srt')
                if os.path.exists(vi_file):
                    logging.info(f"Bỏ qua video {video_file} (đã có phụ đề và bản dịch)")
                    skipped_count += 1
                    continue
            else:
                logging.info(f"Bỏ qua video {video_file} (đã có phụ đề)")
                skipped_count += 1
                continue
            
        if process_video(input_path, args.translate):
            success_count += 1
    
    # Tổng kết
    logging.info("Hoàn thành xử lý:")
    logging.info(f"- Số video đã có phụ đề trước đó: {skipped_count}")
    logging.info(f"- Số video tạo phụ đề thành công: {success_count}")
    logging.info(f"- Tổng số video: {total_videos}")

if __name__ == "__main__":
    main() 