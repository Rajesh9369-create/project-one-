from dataclasses import dataclass
from typing import Optional

@dataclass
class Activity:
    name: str
    scope: str
    kg_co2e: float
    factor: float
    factor_unit: str
    source: str


def electricity_emissions(kwh: float, factor_kgco2_per_kwh: float, source: str) -> Activity:
    if kwh < 0 or factor_kgco2_per_kwh < 0:
        raise ValueError("Electricity and emission factor must be non-negative")
    return Activity("Electricity", "Scope 2", kwh * factor_kgco2_per_kwh,
                    factor_kgco2_per_kwh, "kgCO2/kWh", source)


def diesel_emissions(litres: float, scope1_factor: float, upstream_factor: float,
                     source: str) -> tuple[Activity, Activity]:
    if litres < 0 or scope1_factor < 0 or upstream_factor < 0:
        raise ValueError("Diesel and emission factors must be non-negative")
    return (
        Activity("Diesel combustion", "Scope 1", litres * scope1_factor,
                 scope1_factor, "kgCO2e/L", source),
        Activity("Diesel upstream", "Scope 3", litres * upstream_factor,
                 upstream_factor, "kgCO2e/L", source),
    )


def feed_emissions(kg_feed: float, factor_kgco2e_per_kg: Optional[float], source: str) -> Optional[Activity]:
    if kg_feed < 0:
        raise ValueError("Feed quantity must be non-negative")
    if factor_kgco2e_per_kg is None:
        return None
    if factor_kgco2e_per_kg < 0:
        raise ValueError("Feed emission factor must be non-negative")
    return Activity("Feed", "Scope 3", kg_feed * factor_kgco2e_per_kg,
                    factor_kgco2e_per_kg, "kgCO2e/kg feed", source)


def transport_emissions(feed_tonnes: float, distance_km: float,
                        factor_kgco2e_per_tonne_km: Optional[float], source: str) -> Optional[Activity]:
    if feed_tonnes < 0 or distance_km < 0:
        raise ValueError("Transport quantity and distance must be non-negative")
    if factor_kgco2e_per_tonne_km is None:
        return None
    if factor_kgco2e_per_tonne_km < 0:
        raise ValueError("Transport emission factor must be non-negative")
    emissions = feed_tonnes * distance_km * factor_kgco2e_per_tonne_km
    return Activity("Feed transport", "Scope 3", emissions,
                    factor_kgco2e_per_tonne_km, "kgCO2e/t-km", source)


def calculate(production_kg: float, electricity_kwh: float, electricity_factor: float,
              diesel_litres: float, diesel_scope1_factor: float, diesel_upstream_factor: float,
              feed_kg: float, feed_factor: Optional[float], feed_source: str,
              transport_distance_km: float, transport_factor: Optional[float],
              electricity_source: str, diesel_source: str, transport_source: str) -> dict:
    if production_kg <= 0:
        raise ValueError("Production must be greater than zero")

    activities = [electricity_emissions(electricity_kwh, electricity_factor, electricity_source)]
    activities.extend(diesel_emissions(diesel_litres, diesel_scope1_factor,
                                       diesel_upstream_factor, diesel_source))
    feed = feed_emissions(feed_kg, feed_factor, feed_source)
    if feed:
        activities.append(feed)
    transport = transport_emissions(feed_kg / 1000.0, transport_distance_km,
                                    transport_factor, transport_source)
    if transport:
        activities.append(transport)

    total = sum(a.kg_co2e for a in activities)
    return {
        "production_kg": production_kg,
        "total_kg_co2e": total,
        "carbon_intensity_kg_co2e_per_kg": total / production_kg,
        "activities": activities,
        "complete": feed is not None and transport is not None,
    }
