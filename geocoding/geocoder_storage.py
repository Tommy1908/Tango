from schemas import operation_dict, count_dict
import json
import os

class Geocoder_storage:
    def __init__(self, automatic_path=None, manual_path=None):
        self.auto_path = automatic_path # Path geocoder will save automatically
        self.manual_path = manual_path  # Path to overwrite wrong addresses

    def _load_from_file(self, path):
        if path is None or not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
      
    def _save_coords(self, new_data, path):
        data = []
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []

        processed_new_data = []
        for item in new_data:
            save_item = item.copy()
            save_item.pop('count', None) 
            processed_new_data.append(save_item)

        existing_names = {item['name'] for item in data}

        for item in processed_new_data:
            if item['name'] not in existing_names:
                data.append(item)
                existing_names.add(item['name'])

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def get_saved_coords(self) -> dict[str, tuple[float, float]]:
        auto_data = self._load_from_file(self.auto_path)
        manual_data = self._load_from_file(self.manual_path)

        data_dict = {item['name']: item for item in auto_data}
        for item in manual_data:
            data_dict[item['name']] = item

        return {
            item['name']: tuple(item['coordinates'])
            for item in data_dict.values()
            if item.get('coordinates') is not None
        }

    def save(self, result: list[operation_dict]) -> None:
        self._save_coords(result, self.auto_path)

    def geocode_and_save(self, count: list[count_dict], geocoder) -> list[operation_dict]:
        saved = self.get_saved_coords()
        result = geocoder.geocode_count(count, saved)
        self.save(result)
        return result
