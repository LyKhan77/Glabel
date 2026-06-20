import cv2
import numpy as np
import random

def apply_augmentation(image: np.ndarray, key: str, params: dict) -> np.ndarray:
    handlers = {
        "flip_horizontal": _flip_horizontal,
        "flip_vertical": _flip_vertical,
        "rotation": _rotation,
        "brightness": _brightness,
        "blur": _blur,
        "noise": _noise,
        "cutout": _cutout,
        "hsv_shift": _hsv_shift,
    }
    handler = handlers.get(key)
    if handler is None:
        raise ValueError(f"Unknown augmentation: {key}")
    return handler(image, params)

def _flip_horizontal(image: np.ndarray, params: dict) -> np.ndarray:
    return cv2.flip(image, 1)

def _flip_vertical(image: np.ndarray, params: dict) -> np.ndarray:
    return cv2.flip(image, 0)

def _rotation(image: np.ndarray, params: dict) -> np.ndarray:
    degrees = params.get("degrees", 15)
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, degrees, 1.0)
    return cv2.warpAffine(image, M, (w, h))

def _brightness(image: np.ndarray, params: dict) -> np.ndarray:
    factor = params.get("factor", 1.2)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hsv = np.array(hsv, dtype=np.float64)
    hsv[:, :, 2] = hsv[:, :, 2] * factor
    hsv[:, :, 2][hsv[:, :, 2] > 255] = 255
    hsv = np.array(hsv, dtype=np.uint8)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

def _blur(image: np.ndarray, params: dict) -> np.ndarray:
    ksize = params.get("ksize", 5)
    if ksize % 2 == 0:
        ksize += 1
    return cv2.GaussianBlur(image, (ksize, ksize), 0)

def _noise(image: np.ndarray, params: dict) -> np.ndarray:
    amount = params.get("amount", 0.05)
    noisy = image.copy()
    h, w, c = noisy.shape
    num_salt = np.ceil(amount * h * w * 0.5)
    coords = [np.random.randint(0, i - 1, int(num_salt)) for i in (h, w)]
    noisy[tuple(coords)] = 255
    num_pepper = np.ceil(amount * h * w * 0.5)
    coords = [np.random.randint(0, i - 1, int(num_pepper)) for i in (h, w)]
    noisy[tuple(coords)] = 0
    return noisy

def _cutout(image: np.ndarray, params: dict) -> np.ndarray:
    count = params.get("count", 1)
    size = params.get("size", 20)
    h, w, c = image.shape
    out = image.copy()
    for _ in range(count):
        y = random.randint(0, max(0, h - size))
        x = random.randint(0, max(0, w - size))
        out[y:y+size, x:x+size] = 0
    return out

def _hsv_shift(image: np.ndarray, params: dict) -> np.ndarray:
    h_shift = params.get("h_shift", 10)
    s_shift = params.get("s_shift", 10)
    v_shift = params.get("v_shift", 10)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hsv = np.array(hsv, dtype=np.float64)
    hsv[:, :, 0] = (hsv[:, :, 0] + h_shift) % 180
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] + s_shift, 0, 255)
    hsv[:, :, 2] = np.clip(hsv[:, :, 2] + v_shift, 0, 255)
    hsv = np.array(hsv, dtype=np.uint8)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
