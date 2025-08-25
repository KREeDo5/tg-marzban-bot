import json
import time
import os
from pathlib import Path
from datetime import datetime

class FileBroadcast:
    def __init__(self):
        self.broadcast_dir = Path('broadcasts')
        self.broadcast_dir.mkdir(exist_ok=True)

    def create_broadcast(self, message, admin_id):
        """Создание файла рассылки"""
        timestamp = int(time.time())
        filename = self.broadcast_dir / f"broadcast_{timestamp}_{admin_id}.json"

        broadcast_data = {
            'message': message,
            'created_at': timestamp,
            'admin_id': admin_id,
            'processed': False,
            'processed_at': None
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(broadcast_data, f, ensure_ascii=False, indent=2)

        print(f"📨 Создан файл рассылки: {filename.name}")
        return filename

    def get_pending_broadcasts(self):
        """Получение всех непрочитанных рассылок"""
        broadcasts = []
        for file in self.broadcast_dir.glob('broadcast_*.json'):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if not data.get('processed', False):
                        broadcasts.append((file, data))
            except Exception as e:
                print(f"❌ Ошибка чтения файла {file}: {e}")
                continue

        print(f"📋 Найдено {len(broadcasts)} непрочитанных рассылок")
        return broadcasts

    def mark_as_processed(self, file_path):
        """Пометить рассылку как обработанную"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            data['processed'] = True
            data['processed_at'] = time.time()

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"✅ Помечен как обработанный: {file_path.name}")

        except Exception as e:
            print(f"❌ Ошибка пометки файла {file_path}: {e}")

    def cleanup_old_broadcasts(self, days=1):
        """Очистка старых рассылок"""
        try:
            cutoff_time = time.time() - (days * 24 * 3600)
            removed_count = 0

            for file in self.broadcast_dir.glob('broadcast_*.json'):
                if file.stat().st_mtime < cutoff_time:
                    file.unlink()
                    removed_count += 1

            print(f"🧹 Очищено {removed_count} старых рассылок")

        except Exception as e:
            print(f"❌ Ошибка очистки старых рассылок: {e}")

# Глобальный экземпляр
broadcast_manager = FileBroadcast()