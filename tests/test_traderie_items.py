import json
import os


def test_traderie_items_json_exists():
    assert os.path.exists(
        "traderie/traderie_items.json"
    ), "traderie_items.json 파일이 존재하지 않습니다"


def test_traderie_items_json_is_valid_json():
    with open("traderie/traderie_items.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list), "traderie_items.json은 리스트 형태여야 합니다"


def test_traderie_items_not_empty():
    with open("traderie/traderie_items.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) > 0, "traderie_items.json이 비어있습니다"


def test_traderie_items_are_strings():
    with open("traderie/traderie_items.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    for item in data:
        assert isinstance(item, str), f"모든 아이템은 문자열이어야 합니다: {item}"
