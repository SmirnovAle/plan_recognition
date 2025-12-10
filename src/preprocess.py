import cv2
import numpy as np
from typing import Tuple, Optional
import matplotlib.pyplot as plt


class ImagePreprocessor:
    """Класс для предобработки изображений планов"""

    def __init__(self, config):
        self.config = config

    def load_image(self, image_path: str) -> np.ndarray:
        """Загрузка изображения"""
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(
                f"Не удалось загрузить изображение: {image_path}")
        return img

    def resize_image(self, img: np.ndarray, width: Optional[int] = None) -> np.ndarray:
        """Изменение размера изображения"""
        if width is None:
            width = self.config['resize_width']

        h, w = img.shape[:2]
        height = int(h * (width / w))
        return cv2.resize(img, (width, height))

    def convert_to_grayscale(self, img: np.ndarray) -> np.ndarray:
        """Конвертация в оттенки серого"""
        if len(img.shape) == 3:
            return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img

    def apply_binarization(self, gray: np.ndarray) -> np.ndarray:
        """Адаптивная бинаризация"""
        # Метод Отсу для автоматического подбора порога
        _, binary = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )
        return binary

    def remove_noise(self, binary: np.ndarray) -> np.ndarray:
        """Удаление шума морфологическими операциями"""
        kernel = np.ones((3, 3), np.uint8)

        # Закрытие для заполнения мелких разрывов
        closed = cv2.morphologyEx(
            binary, cv2.MORPH_CLOSE, kernel, iterations=1)

        # Открытие для удаления мелких объектов
        opened = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel, iterations=1)

        return opened

    def detect_edges(self, binary: np.ndarray) -> np.ndarray:
        """Детекция границ"""
        edges = cv2.Canny(
            binary,
            self.config['canny_low'],
            self.config['canny_high']
        )
        return edges

    def preprocess_pipeline(self, image_path: str, visualize: bool = False) -> dict:
        """
        Полный пайплайн предобработки

        Возвращает словарь с промежуточными результатами
        """
        # Загрузка
        original = self.load_image(image_path)
        resized = self.resize_image(original)

        # Конвертация в grayscale
        gray = self.convert_to_grayscale(resized)

        # Бинализация
        binary = self.apply_binarization(gray)

        # Удаление шума
        denoised = self.remove_noise(binary)

        # Детекция границ
        edges = self.detect_edges(denoised)

        if visualize:
            self._visualize_results(original, gray, binary, denoised, edges)

        return {
            'original': original,
            'resized': resized,
            'gray': gray,
            'binary': binary,
            'denoised': denoised,
            'edges': edges
        }

    def _visualize_results(self, original, gray, binary, denoised, edges):
        """Визуализация промежуточных результатов"""
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))

        images = [original, gray, binary, denoised, edges]
        titles = ['Original', 'Grayscale', 'Binary', 'Denoised', 'Edges']

        axes = axes.flatten()
        for i, (ax, img, title) in enumerate(zip(axes, images, titles)):
            if len(img.shape) == 2:
                ax.imshow(img, cmap='gray')
            else:
                ax.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            ax.set_title(title)
            ax.axis('off')

        axes[-1].axis('off')
        plt.tight_layout()
        plt.show()
