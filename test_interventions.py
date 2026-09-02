from calculator import Activity, generate_interventions


def test_feed_hotspot_is_priority_one():
    activities = [
        Activity("Electricity", "Scope 2", 13246, 0.716, "kgCO2/kWh", "test"),
        Activity("Diesel combustion", "Scope 1", 2032.5, 2.71, "kgCO2e/L", "test"),
        Activity("Diesel upstream", "Scope 3", 472.5, 0.63, "kgCO2e/L", "test"),
        Activity("Feed", "Scope 3", 40000, 1.25, "kgCO2e/kg feed", "test"),
        Activity("Feed transport", "Scope 3", 489.6, 0.085, "kgCO2e/t-km", "test"),
    ]
    result = generate_interventions(activities, 25000, 32000, 18500, 750, 1.25)
    assert result[0]["area"] == "Feed efficiency & feed footprint"
    assert round(result[0]["hotspot_share"] * 100, 1) == 71.1


def test_low_transport_share_does_not_get_transport_priority():
    activities = [
        Activity("Electricity", "Scope 2", 900, 0.716, "kgCO2/kWh", "test"),
        Activity("Diesel combustion", "Scope 1", 100, 2.71, "kgCO2e/L", "test"),
        Activity("Diesel upstream", "Scope 3", 20, 0.63, "kgCO2e/L", "test"),
        Activity("Feed", "Scope 3", 1000, 1.25, "kgCO2e/kg feed", "test"),
        Activity("Feed transport", "Scope 3", 10, 0.085, "kgCO2e/t-km", "test"),
    ]
    result = generate_interventions(activities, 10000, 800, 1257, 37, 1.25)
    assert not any(x["area"] == "Feed transport" for x in result)
