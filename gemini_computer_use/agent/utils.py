"""Utils file for common functions"""

from .logger import get_logger

logger = get_logger(__name__)

def denormalize_x(x: int, width: int = 1440) -> int:
    # Gemini gives 0-1000 normalized pixels
    return int(x / 1000 * width)

def denormalize_y(y: int, height: int = 900) -> int:
    return int(y / 1000 * height)

def get_safety_confirmation(safety_decision: dict):
    """Prompt user for confirmation when safety check is triggered."""
    # This might not be needed, but docs says we might have to implement one
    # Ideally for full automation, we should skip this or atleady OK everything
    logger.info("Safety service requires explicit confirmation!")
    logger.info(f"Explanation: {safety_decision['explanation']}")

    decision = ""
    while decision.lower() not in ("y", "n", "ye", "yes", "no"):
        decision = input("Do you wish to proceed? [Y]es/[N]o\n")

    if decision.lower() in ("n", "no"):
        return "TERMINATE"
    return "CONTINUE"
