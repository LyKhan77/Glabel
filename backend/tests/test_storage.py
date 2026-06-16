from backend.core import storage


def test_read_missing_returns_default(monkeypatch, tmp_path):
    monkeypatch.setenv("GLABEL_DATA_DIR", str(tmp_path))
    assert storage.read_json("missing.json", [1, 2]) == [1, 2]


def test_write_then_read(monkeypatch, tmp_path):
    monkeypatch.setenv("GLABEL_DATA_DIR", str(tmp_path))
    storage.write_json("x.json", [{"a": 1}])
    assert storage.read_json("x.json", []) == [{"a": 1}]


def test_update_json_mutates_and_persists(monkeypatch, tmp_path):
    monkeypatch.setenv("GLABEL_DATA_DIR", str(tmp_path))

    def add_c(items):
        items.append("c")
        return len(items)

    count = storage.update_json("y.json", [], add_c)
    assert count == 1
    assert storage.read_json("y.json", []) == ["c"]


def test_update_json_returns_default_when_missing(monkeypatch, tmp_path):
    monkeypatch.setenv("GLABEL_DATA_DIR", str(tmp_path))

    def first(items):
        return items

    assert storage.update_json("z.json", ["seed"], first) == ["seed"]


def test_read_corrupt_returns_default(monkeypatch, tmp_path):
    monkeypatch.setenv("GLABEL_DATA_DIR", str(tmp_path))
    (tmp_path / "c.json").write_text("{not json", encoding="utf-8")
    assert storage.read_json("c.json", {"ok": True}) == {"ok": True}


def test_update_json_resets_corrupt_to_default(monkeypatch, tmp_path):
    monkeypatch.setenv("GLABEL_DATA_DIR", str(tmp_path))
    (tmp_path / "d.json").write_text("!!!broken", encoding="utf-8")

    def replace(items):
        items.append("fixed")
        return len(items)

    count = storage.update_json("d.json", [], replace)
    assert count == 1
    assert storage.read_json("d.json", []) == ["fixed"]
