#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import subprocess
import argparse
import psutil
import torch
import gc
import traceback
from generate_subtitles import generate_subtitles, get_gpu_info, clear_gpu_memory
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Enable PyTorch CUDA logging with smaller memory block size
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:24"

def get_process_memory():
    """Get current process memory usage in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024  # Convert to MB

def benchmark_model(audio_path, model_size, language="en", iterations=1):
    """Benchmark a specific model size."""
    total_time = 0
    max_gpu_memory = 0
    max_cpu_memory = 0
    successful_runs = 0
    
    logger.info(f"===== Benchmarking {model_size} model with language={language} =====")
    logger.info(f"Initial CPU memory: {get_process_memory():.2f} MB")
    logger.info(f"Initial GPU status: {get_gpu_info()}")
    
    for i in range(iterations):
        logger.info(f"Iteration {i+1}/{iterations}")
        
        # Force garbage collection and clear GPU memory before test
        clear_gpu_memory()
        gc.collect()
        time.sleep(1)  # Give system a moment to release resources
        
        # Measure CPU memory before
        start_cpu_mem = get_process_memory()
        
        # Measure time
        start_time = time.time()
        
        # Generate subtitles
        output_path = f"test_output_{model_size}_{i+1}.srt"
        
        try:
            success = generate_subtitles(audio_path, output_path, model_size, language)
            if success:
                successful_runs += 1
                
            # Calculate time
            elapsed = time.time() - start_time
            total_time += elapsed
            
            # Measure GPU memory
            if torch.cuda.is_available():
                curr_gpu_allocated = torch.cuda.memory_allocated() / 1024 / 1024  # MB
                max_gpu_memory = max(max_gpu_memory, curr_gpu_allocated)
            
            # Measure CPU memory
            curr_cpu_mem = get_process_memory()
            max_cpu_memory = max(max_cpu_memory, curr_cpu_mem - start_cpu_mem)
            
            logger.info(f"Iteration {i+1} completed in {elapsed:.2f} seconds (Success: {success})")
            
        except Exception as e:
            logger.error(f"Error during benchmark iteration {i+1}: {str(e)}")
            logger.error(traceback.format_exc())
            
        logger.info(f"Current GPU status: {get_gpu_info()}")
        
        # Clean up output file
        if os.path.exists(output_path):
            os.remove(output_path)
            
        # Extra cleanup between iterations
        clear_gpu_memory()
        gc.collect()
        time.sleep(2)  # Give system time to release resources
    
    # Calculate average time only for successful runs
    avg_time = total_time / max(successful_runs, 1) if successful_runs > 0 else float('inf')
    
    logger.info(f"\n===== Results for {model_size} model =====")
    logger.info(f"Successful runs: {successful_runs}/{iterations}")
    logger.info(f"Average time (successful runs): {avg_time:.2f} seconds")
    logger.info(f"Max GPU memory used: {max_gpu_memory:.2f} MB")
    logger.info(f"Max additional CPU memory used: {max_cpu_memory:.2f} MB")
    
    return {
        "model": model_size,
        "success_rate": successful_runs / iterations if iterations > 0 else 0,
        "avg_time": avg_time,
        "max_gpu_memory": max_gpu_memory,
        "max_cpu_memory": max_cpu_memory
    }

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Benchmark Whisper models")
    parser.add_argument("audio_path", help="Path to input audio file (WAV)")
    parser.add_argument("--models", "-m", default="tiny,base,small", 
                        help="Comma-separated list of models to test (tiny, base, small)")
    parser.add_argument("--language", "-l", default="en", help="Language code (default: English)")
    parser.add_argument("--iterations", "-i", type=int, default=1, help="Number of iterations for each model")
    
    args = parser.parse_args()
    
    # Verify input audio exists
    if not os.path.exists(args.audio_path):
        logger.error(f"Input audio file does not exist: {args.audio_path}")
        exit(1)
    
    # Parse models
    models = [model.strip() for model in args.models.split(',')]
    
    # Run benchmarks
    results = []
    for model in models:
        # Extra cleanup before each model test
        clear_gpu_memory()
        gc.collect()
        time.sleep(3)  # Give system more time to release resources
        
        result = benchmark_model(args.audio_path, model, args.language, args.iterations)
        results.append(result)
    
    # Compare results
    logger.info("\n===== Comparison =====")
    logger.info(f"{'Model':<10} {'Success Rate':<15} {'Avg Time (s)':<15} {'Max GPU (MB)':<15} {'Max CPU (MB)':<15}")
    for result in results:
        logger.info(f"{result['model']:<10} {result['success_rate']*100:.1f}% {result['avg_time']:.2f} {result['max_gpu_memory']:.2f} {result['max_cpu_memory']:.2f}")
    
    # Recommend model based on performance, success rate and memory
    successful_results = [r for r in results if r['success_rate'] > 0]
    
    logger.info("\n===== Recommendations =====")
    if successful_results:
        fastest = min(successful_results, key=lambda x: x['avg_time'])
        lowest_memory = min(successful_results, key=lambda x: x['max_gpu_memory'] if x['max_gpu_memory'] > 0 else float('inf'))
        
        logger.info(f"Fastest model: {fastest['model']} ({fastest['avg_time']:.2f} seconds)")
        if lowest_memory['max_gpu_memory'] > 0:
            logger.info(f"Lowest memory usage: {lowest_memory['model']} ({lowest_memory['max_gpu_memory']:.2f} MB)")
        else:
            logger.info("CPU was used for all models, memory comparison not applicable")
            
        # Best balance of speed and accuracy
        best_model = fastest
        for model in successful_results:
            # Prefer larger models with good speed
            if model['model'] in ['base', 'small'] and model['avg_time'] < fastest['avg_time'] * 1.5:
                best_model = model
                break
                
        logger.info(f"Recommended model for your system: {best_model['model']} (Balance of accuracy and speed)")
    else:
        logger.warning("No models completed successfully. Try with the 'tiny' model only or check your CUDA setup.")
        
    logger.info("\nNote: If you're seeing CUDA memory errors, try these solutions:")
    logger.info("1. Close other applications that might be using GPU memory")
    logger.info("2. Set environment variable PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:16")
    logger.info("3. If only CPU runs succeed, your GPU may not have enough VRAM for larger models")

if __name__ == "__main__":
    main()