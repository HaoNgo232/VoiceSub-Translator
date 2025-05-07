#!/bin/bash
echo "=== Bắt đầu cài đặt CUDA và cuDNN ==="
sudo apt update
sudo apt install -y build-essential wget
echo "Đang tải CUDA Toolkit 11.8..."
wget https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda_11.8.0_520.61.05_linux.run
echo "Đang cài đặt CUDA Toolkit..."
sudo sh cuda_11.8.0_520.61.05_linux.run --toolkit --silent --override
echo "Thiết lập biến môi trường..."
echo 'export PATH=/usr/local/cuda-11.8/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-11.8/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
echo "Đang cài đặt cuDNN..."
sudo apt install -y libcudnn9=9.1.0.70-1+cuda11.8
sudo apt install -y libcudnn9-dev=9.1.0.70-1+cuda11.8
echo "Kiểm tra cài đặt..."
if [ -f "/usr/local/cuda-11.8/lib64/libcudnn.so.9.1.0" ]; then
echo "✅ Cài đặt cuDNN thành công!"
else
echo "❌ Cài đặt cuDNN thất bại!"
fi

if [ -f "/usr/local/cuda-11.8/bin/nvcc" ]; then
echo "✅ Cài đặt CUDA thành công!"
else
echo "❌ Cài đặt CUDA thất bại!"
fi

echo "=== Hoàn tất quá trình cài đặt ==="
echo "Vui lòng khởi động lại máy tính để áp dụng các thay đổi."
