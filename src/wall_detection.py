import cv2
import numpy as np
from typing import List, Tuple, Dict
import math


class WallDetector:
    """Класс для детекции стен на плане"""

    def __init__(self, config):
        self.config = config
        self.wall_settings = config.get('WALL_SETTINGS', {})

    def detect_lines(self, edges: np.ndarray) -> List[Tuple]:
        """Детекция линий методом Хафа"""
        lines = cv2.HoughLinesP(
            edges,
            rho=self.config['hough_rho'],
            theta=self.config['hough_theta'],
            threshold=self.config['hough_threshold'],
            minLineLength=self.config['min_line_length'],
            maxLineGap=self.config['max_line_gap']
        )

        if lines is None:
            return []

        # Преобразование в удобный формат
        detected_lines = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            angle = math.degrees(math.atan2(y2 - y1, x2 - x1)) % 180

            detected_lines.append({
                'points': [(x1, y1), (x2, y2)],
                'length': length,
                'angle': angle,
                'original': line[0]
            })

        return detected_lines

    def filter_by_angle(self, lines: List[Dict], target_angles: List[float] = None) -> List[Dict]:
        """Фильтрация линий по углу"""
        if target_angles is None:
            target_angles = [0, 90]  # Горизонтальные и вертикальные

        filtered_lines = []
        tolerance = self.wall_settings.get('angle_tolerance', 10)

        for line in lines:
            angle = line['angle']

            # Находим ближайший целевой угол
            closest_angle = min(target_angles, key=lambda x: abs(x - angle))

            # Проверяем, попадает ли в допуск
            if abs(closest_angle - angle) <= tolerance:
                # Корректируем угол
                corrected_line = self._snap_line_to_angle(line, closest_angle)
                filtered_lines.append(corrected_line)

        return filtered_lines

    def _snap_line_to_angle(self, line: Dict, target_angle: float) -> Dict:
        """Корректировка линии к заданному углу"""
        x1, y1 = line['points'][0]
        x2, y2 = line['points'][1]

        # Для горизонтальных линий
        if abs(target_angle - 0) < 1 or abs(target_angle - 180) < 1:
            y2 = y1
        # Для вертикальных линий
        elif abs(target_angle - 90) < 1:
            x2 = x1

        # Пересчитываем длину и угол
        length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        angle = math.degrees(math.atan2(y2 - y1, x2 - x1)) % 180

        return {
            'points': [(x1, y1), (x2, y2)],
            'length': length,
            'angle': angle,
            'original': [x1, y1, x2, y2]
        }

    def merge_similar_lines(self, lines: List[Dict]) -> List[Dict]:
        """Объединение близких линий"""
        if not lines:
            return []

        merge_distance = self.wall_settings.get('merge_distance', 20)
        merged = []
        used = [False] * len(lines)

        for i, line1 in enumerate(lines):
            if used[i]:
                continue

            # Начинаем с текущей линии
            current_points = list(line1['points'])
            used[i] = True

            # Ищем линии для объединения
            for j, line2 in enumerate(lines[i+1:], i+1):
                if used[j]:
                    continue

                # Проверяем, можно ли объединить
                if self._can_merge_lines(line1, line2, merge_distance):
                    # Объединяем точки
                    current_points.extend(line2['points'])
                    used[j] = True

            # Создаем объединенную линию
            merged_line = self._create_line_from_points(current_points)
            if merged_line['length'] >= self.wall_settings.get('min_wall_length', 50):
                merged.append(merged_line)

        return merged

    def _can_merge_lines(self, line1: Dict, line2: Dict, max_distance: float) -> bool:
        """Проверка возможности объединения двух линий"""
        # Проверяем углы
        angle_diff = abs(line1['angle'] - line2['angle'])
        if angle_diff > 5:  # Только линии с близкими углами
            return False

        # Проверяем расстояние между концами
        points1 = line1['points']
        points2 = line2['points']

        for p1 in points1:
            for p2 in points2:
                distance = math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
                if distance <= max_distance:
                    return True

        return False

    def _create_line_from_points(self, points: List[Tuple]) -> Dict:
        """Создание линии из набора точек"""
        if not points:
            return None

        # Находим крайние точки
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]

        x1, x2 = min(x_coords), max(x_coords)
        y1, y2 = min(y_coords), max(y_coords)

        # Для горизонтальных/вертикальных линий
        if abs(x2 - x1) > abs(y2 - y1):  # Горизонтальная
            y1 = y2 = np.mean(y_coords)
        else:  # Вертикальная
            x1 = x2 = np.mean(x_coords)

        length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        angle = math.degrees(math.atan2(y2 - y1, x2 - x1)) % 180

        return {
            'points': [(int(x1), int(y1)), (int(x2), int(y2))],
            'length': length,
            'angle': angle,
            'original': [int(x1), int(y1), int(x2), int(y2)]
        }

    def detect_walls(self, edges: np.ndarray) -> List[Dict]:
        """Полный пайплайн детекции стен"""
        # Детекция линий
        lines = self.detect_lines(edges)

        # Фильтрация по углу (только горизонтальные и вертикальные)
        filtered_lines = self.filter_by_angle(lines, target_angles=[0, 90])

        # Объединение близких линий
        merged_lines = self.merge_similar_lines(filtered_lines)

        # Присваиваем ID
        for i, wall in enumerate(merged_lines, 1):
            wall['id'] = f'w{i}'

        return merged_lines

    def visualize_detection(self, image: np.ndarray, walls: List[Dict]):
        """Визуализация найденных стен"""
        result = image.copy()

        for wall in walls:
            points = wall['points']
            cv2.line(result, points[0], points[1], (0, 255, 0), 2)

            # Подпись ID
            mid_x = (points[0][0] + points[1][0]) // 2
            mid_y = (points[0][1] + points[1][1]) // 2
            cv2.putText(result, wall['id'], (mid_x, mid_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        return result
