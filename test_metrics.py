import pytest
from calculator import calculate_performance_metrics


def test_performance_metrics():
    m = calculate_performance_metrics(25000, 32000, 18500, 750, 5000)
    assert m["fcr"] == pytest.approx(1.6)
    assert m["energy_intensity_kwh_per_kg"] == pytest.approx(0.74)
    assert m["feed_intensity_kg_per_kg"] == pytest.approx(1.28)
    assert m["diesel_intensity_l_per_kg"] == pytest.approx(0.03)


def test_fcr_requires_valid_initial_biomass():
    m = calculate_performance_metrics(25000, 32000, 18500, 750)
    assert m["fcr"] is None
    with pytest.raises(ValueError):
        calculate_performance_metrics(25000, 32000, 18500, 750, 25000)
