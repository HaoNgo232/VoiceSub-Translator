from setuptools import setup, find_packages

setup(
    name="subtitle_processor",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "google-genai",
        "openai-whisper",
        "torch"
    ],
    entry_points={
        "console_scripts": [
            "subtitle-processor=main:main",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="Công cụ xử lý video và dịch phụ đề",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/subtitle-processor",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
) 