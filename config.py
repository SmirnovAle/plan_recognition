import os

# Пути
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
INPUT_DIR = os.path.join(DATA_DIR, 'input')
OUTPUT_DIR = os.path.join(DATA_DIR, 'output')
MODELS_DIR = os.path.join(BASE_DIR, 'models')

# Создание директорий
for dir_path in [INPUT_DIR, OUTPUT_DIR, MODELS_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# Параметры обработки изображений
IMAGE_SETTINGS = {
    'resize_width': 1024,  # Ширина для ресайза
    'binary_threshold': 128,  # Порог бинаризации
    'canny_low': 50,  # Нижний порог для Canny
    'canny_high': 150,  # Верхний порог для Canny
    'hough_rho': 1,  # Разрешение по ρ в пикселях
    'hough_theta': 3.1415926 / 180,  # Разрешение по θ в радианах
    'hough_threshold': 80,  # Порог для детекции линий
    'min_line_length': 50,  # Минимальная длина линии
    'max_line_gap': 20,  # Максимальный разрыв между линиями
    'angle_tolerance': 10,  # Допуск угла для фильтрации (градусы)
}

# Параметры стен
WALL_SETTINGS = {
    'min_wall_length': 100,  # Минимальная длина стены (пиксели)
    'merge_distance': 20,  # Расстояние для объединения линий
    'snap_angles': [0, 45, 90, 135],  # Углы для "привязки"
}

# Настройки JSON
JSON_SETTINGS = {
    'indent': 2,
    'ensure_ascii': False,
}
