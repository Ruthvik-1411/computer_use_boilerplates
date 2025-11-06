"""Module to add grid overlay over image for better spatial reasoning"""
import cv2
import numpy as np

def overlay_grid_on_image(image_bytes, num_x_lines=12, num_y_lines=9, alpha=0.6):
    """
    Overlay a semi-transparent coordinate grid on an image and return PNG bytes.

    Args:
        image_bytes (bytes or np.ndarray): Input image (bytes or cv2 image array).
        num_x_lines (int): Number of vertical grid lines.
        num_y_lines (int): Number of horizontal grid lines.
        alpha (float): Transparency of the grid overlay.

    Returns:
        bytes: PNG-encoded image bytes with grid overlay.
    """
    if isinstance(image_bytes, (bytes, bytearray)):
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    elif isinstance(image_bytes, np.ndarray):
        img = image_bytes.copy()
    else:
        raise TypeError("Input must be bytes or a numpy.ndarray")

    h, w = img.shape[:2]

    # black grid lines
    grid_color = (0, 0, 0)
    font = cv2.FONT_HERSHEY_SIMPLEX

    overlay = img.copy()

    # vertical lines + x labels
    for i in range(num_x_lines + 1):
        x = int(i * w / num_x_lines)
        cv2.line(overlay, (x, 0), (x, h), grid_color, 1)
        cv2.putText(overlay, f"x={x}", (x + 5, 20), font, 0.5, grid_color, 1, cv2.LINE_AA)

    # horizontal lines + y labels
    for j in range(num_y_lines + 1):
        y = int(j * h / num_y_lines)
        cv2.line(overlay, (0, y), (w, y), grid_color, 1)
        cv2.putText(overlay, f"y={y}", (5, y + 15), font, 0.5, grid_color, 1, cv2.LINE_AA)

    # blend overlay with image
    blended = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)

    # encode back to PNG bytes
    success, buf = cv2.imencode(".png", blended)
    if not success:
        raise RuntimeError("Failed to encode image as PNG")

    return buf.tobytes()
