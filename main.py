from src.json_export import JSONExporter
from src.wall_detection import WallDetector
from src.preprocess import ImagePreprocessor
from config import IMAGE_SETTINGS, WALL_SETTINGS, JSON_SETTINGS, INPUT_DIR, OUTPUT_DIR
import os
import sys
import cv2
from pathlib import Path

# Добавляем путь к src
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))


def process_single_image(image_path: str, output_dir: str = OUTPUT_DIR):
    """Обработка одного изображения"""
    print(f"\nОбработка: {image_path}")

    # Инициализация компонентов
    config = {**IMAGE_SETTINGS, **WALL_SETTINGS, **JSON_SETTINGS}
    preprocessor = ImagePreprocessor(config)
    detector = WallDetector(config)
    exporter = JSONExporter(config)

    # 1. Предобработка
    print("  Шаг 1: Предобработка изображения...")
    processed = preprocessor.preprocess_pipeline(image_path, visualize=False)

    # 2. Детекция стен
    print("  Шаг 2: Детекция стен...")
    walls = detector.detect_walls(processed['edges'])
    print(f"  Найдено стен: {len(walls)}")

    # 3. Визуализация
    print("  Шаг 3: Визуализация результатов...")
    visualization = detector.visualize_detection(processed['resized'], walls)

    # 4. Экспорт в JSON
    print("  Шаг 4: Экспорт в JSON...")
    image_name = Path(image_path).stem
    json_path = os.path.join(output_dir, f"{image_name}_walls.json")
    exporter.export_walls_to_minimal_json(image_path, walls, json_path)

    # 5. Сохранение визуализации
    vis_path = os.path.join(output_dir, f"{image_name}_detection.jpg")
    cv2.imwrite(vis_path, visualization)

    print(f"  Результаты сохранены в: {output_dir}")

    return walls, visualization, json_path


def main():
    """Главная функция"""
    print("=== Распознавание плана квартиры ===")
    print(f"Входная директория: {INPUT_DIR}")
    print(f"Выходная директория: {OUTPUT_DIR}")

    # Получаем список изображений
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    image_files = []

    for ext in image_extensions:
        image_files.extend(Path(INPUT_DIR).glob(f'*{ext}'))
        image_files.extend(Path(INPUT_DIR).glob(f'*{ext.upper()}'))

    if not image_files:
        print(f"\nОшибка: Не найдено изображений в {INPUT_DIR}")
        print("Пожалуйста, добавьте изображения в папку data/input/")
        return

    print(f"\nНайдено изображений: {len(image_files)}")

    # Обрабатываем каждое изображение
    results = {}
    for i, image_path in enumerate(image_files, 1):
        print(f"\n[{i}/{len(image_files)}] ", end="")
        try:
            walls, visualization, json_path = process_single_image(
                str(image_path))
            results[str(image_path)] = {
                'walls': walls,
                'json_path': json_path
            }
        except Exception as e:
            print(f"Ошибка при обработке {image_path}: {e}")

    print("\n=== Обработка завершена ===")
    print(f"Результаты сохранены в: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
