import json
import os
from typing import List, Dict
from datetime import datetime


class JSONExporter:
    """Класс для экспорта результатов в JSON"""

    def __init__(self, config):
        self.config = config

    def format_walls(self, walls: List[Dict]) -> List[Dict]:
        """Форматирование информации о стенах для JSON"""
        formatted_walls = []

        for wall in walls:
            formatted_wall = {
                'id': wall.get('id', 'unknown'),
                'points': wall['points'],
                'length': wall.get('length', 0),
                'angle': wall.get('angle', 0)
            }
            formatted_walls.append(formatted_wall)

        return formatted_walls

    def create_json_structure(self, source_image: str, walls: List[Dict]) -> Dict:
        """Создание структуры JSON"""
        # Мета-информация
        meta = {
            'source': os.path.basename(source_image),
            'processed_date': datetime.now().isoformat(),
            'total_walls': len(walls),
            'image_width': 0,
            'image_height': 0
        }

        # Форматируем стены
        formatted_walls = self.format_walls(walls)

        # Базовая структура
        result = {
            'meta': meta,
            'walls': formatted_walls
        }

        return result

    def export_to_json(self, data: Dict, output_path: str):
        """Экспорт данных в JSON файл"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=self.config.get('indent', 2),
                      ensure_ascii=self.config.get('ensure_ascii', False))

        print(f"JSON успешно экспортирован: {output_path}")

    def export_walls_to_minimal_json(self, source_image: str, walls: List[Dict],
                                     output_path: str):
        """Экспорт в минимальный требуемый формат JSON"""
        formatted_walls = []

        for wall in walls:
            formatted_wall = {
                'id': wall.get('id', 'unknown'),
                'points': wall['points']
            }
            formatted_walls.append(formatted_wall)

        result = {
            'meta': {
                'source': os.path.basename(source_image)
            },
            'walls': formatted_walls
        }

        self.export_to_json(result, output_path)
