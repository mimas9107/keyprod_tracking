import pytest
from app.scraper import parse_option_text


def test_parse_option_text():
    text = "UMAX 32GB(雙q16GB*2) DDR5 4800/CL40 套裝, $9499 在庫"
    brand, capacity, speed, latency, price, status = parse_option_text(text)
    assert brand == "UMAX"
    assert capacity == "32GB"
    assert speed == "DDR5-4800"
    assert latency == "CL40"
    assert price == 9499
    assert status == "in_stock"


def test_parse_option_text_missing():
    text = "Some RAM without price or status"
    brand, capacity, speed, latency, price, status = parse_option_text(text)
    assert brand == "Some"
    assert capacity == "NaN"
    assert speed == "NaN"
    assert latency == "NaN"
    assert price == -99
    assert status == "in_stock"  # no "缺貨"


def test_parse_option_text_out_of_stock():
    text = "RAM $1000 缺貨"
    brand, capacity, speed, latency, price, status = parse_option_text(text)
    assert price == 1000
    assert status == "out_of_stock"
