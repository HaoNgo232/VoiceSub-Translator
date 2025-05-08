import torch
import gc
import logging

logger = logging.getLogger(__name__)

def get_gpu_info():
    """Get GPU memory information."""
    if torch.cuda.is_available():
        try:
            t = torch.cuda.get_device_properties(0).total_memory
            r = torch.cuda.memory_reserved(0)
            a = torch.cuda.memory_allocated(0)
            f = r - a  # Free memory within the reserved block
            return f"Total: {t/1e9:.1f}GB, Reserved: {r/1e9:.1f}GB, Allocated: {a/1e9:.1f}GB, Free in Reserved: {f/1e9:.1f}GB"
        except Exception as e:
            logger.error(f"Could not get GPU info: {e}")
            return "Error getting GPU info"
    return "CUDA not available"

def clear_gpu_memory():
    """Clear GPU memory cache."""
    logger.info("Attempting to clear GPU memory...")
    gc.collect()
    if torch.cuda.is_available():
        try:
            torch.cuda.empty_cache()
            logger.info("torch.cuda.empty_cache() called.")
        except Exception as e:
            logger.error(f"Error calling torch.cuda.empty_cache(): {e}")
    else:
        logger.info("CUDA not available, skipping torch.cuda.empty_cache().") 