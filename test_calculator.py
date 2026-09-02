import pytest
from calculator import calculate


def test_known_inputs():
    r = calculate(
        production_kg=10000,
        electricity_kwh=1000,
        electricity_factor=0.716,
        diesel_litres=100,
        diesel_scope1_factor=2.71,
        diesel_upstream_factor=0.63,
        feed_kg=1000,
        feed_factor=1.5,
        transport_distance_km=100,
        transport_factor=0.1,
        feed_source="test",
        electricity_source="test",
        diesel_source="test",
        transport_source="test",
    )
    # 716 + 271 + 63 + 1500 + (1 t * 100 km * .1) = 2560 kgCO2e
    assert r["total_kg_co2e"] == pytest.approx(2560.0)
    assert r["carbon_intensity_kg_co2e_per_kg"] == pytest.approx(0.256)
    assert r["complete"] is True


def test_missing_feed_factor_marks_incomplete():
    r = calculate(
        production_kg=10000,
        electricity_kwh=1000,
        electricity_factor=0.716,
        diesel_litres=0,
        diesel_scope1_factor=2.71,
        diesel_upstream_factor=0.63,
        feed_kg=1000,
        feed_factor=None,
        transport_distance_km=100,
        transport_factor=0.1,
        feed_source="missing",
        electricity_source="test",
        diesel_source="test",
        transport_source="test",
    )
    assert r["complete"] is False
    assert r["total_kg_co2e"] == pytest.approx(716 + 10)


def test_zero_production_rejected():
    with pytest.raises(ValueError):
        calculate(0, 0, 0, 0, 0, 0, 0, 0, "x", 0, None, "x", "x", "x")
