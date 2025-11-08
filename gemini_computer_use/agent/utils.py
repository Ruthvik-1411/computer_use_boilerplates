"""Utils file for common functions"""
import time
import functools
import asyncio

from .config import SAFETY_AUTO_PROCEED
from .logger import get_logger

logger = get_logger(__name__)

def denormalize_x(x: int, width: int = 1440) -> int:
    """Denormalize normalized x coordinates wrt page width"""
    # Gemini gives 0-1000 normalized pixels
    return int(x / 1000 * width)

def denormalize_y(y: int, height: int = 900) -> int:
    """Denormalize normalized y coordinates wrt page height"""
    return int(y / 1000 * height)

def get_safety_confirmation(safety_decision: dict):
    """Prompt user for confirmation when safety check is triggered."""
    # NOTE: This might not be needed, but docs says we might have to implement one
    # FIXME: Ideally for full automation, we should skip this or OK everything
    logger.info("Safety service requires explicit confirmation!")
    logger.info(f"Explanation: {safety_decision['explanation']}")

    # For server setup, auto proceed
    if SAFETY_AUTO_PROCEED:
        logger.warning("Auto-proceeding due to server configuration.")
        return "CONTINUE"

    # For CLI usage, it's optional
    decision = ""
    while decision.lower() not in ("y", "n", "ye", "yes", "no"):
        decision = input("Do you wish to proceed? [Y]es/[N]o\n")

    if decision.lower() in ("n", "no"):
        return "TERMINATE"
    return "CONTINUE"

def time_logger(func):
    """
    Decorator to log execution time for a function,
    usually for the function tools
    """
    if asyncio.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.time()
            try:
                return await func(*args, **kwargs)
            finally:
                duration = time.time() - start
                logger.info(f"[TIME] {func.__qualname__} executed in {duration:.4f} seconds.")
        return async_wrapper
    else:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.time()
            try:
                return func(*args, **kwargs)
            finally:
                duration = time.time() - start
                logger.info(f"[TIME] {func.__qualname__} executed in {duration:.4f} seconds.")
        return sync_wrapper
