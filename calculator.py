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
    return Activity("Electricity", "Scope 2", kwh * factor_kgco2_per_kwh, factor_kgco2_per_kwh, "kgCO2/kWh", source)


def diesel_emissions(litres: float, scope1_factor: float, upstream_factor: float, source: str) -> tuple[Activity, Activity]:
    if litres < 0 or scope1_factor < 0 or upstream_factor < 0:
        raise ValueError("Diesel and emission factors must be non-negative")
    return (
        Activity("Diesel combustion", "Scope 1", litres * scope1_factor, scope1_factor, "kgCO2e/L", source),
        Activity("Diesel upstream", "Scope 3", litres * upstream_factor, upstream_factor, "kgCO2e/L", source),
    )


def feed_emissions(kg_feed: float, factor_kgco2e_per_kg: Optional[float], source: str) -> Optional[Activity]:
    if kg_feed < 0:
        raise ValueError("Feed quantity must be non-negative")
    if factor_kgco2e_per_kg is None:
        return None
    if factor_kgco2e_per_kg < 0:
        raise ValueError("Feed emission factor must be non-negative")
    return Activity("Feed", "Scope 3", kg_feed * factor_kgco2e_per_kg, factor_kgco2e_per_kg, "kgCO2e/kg feed", source)


def transport_emissions(feed_tonnes: float, distance_km: float, factor_kgco2e_per_tonne_km: Optional[float], source: str) -> Optional[Activity]:
    if feed_tonnes < 0 or distance_km < 0:
        raise ValueError("Transport quantity and distance must be non-negative")
    if factor_kgco2e_per_tonne_km is None:
        return None
    if factor_kgco2e_per_tonne_km < 0:
        raise ValueError("Transport emission factor must be non-negative")
    return Activity("Feed transport", "Scope 3", feed_tonnes * distance_km * factor_kgco2e_per_tonne_km, factor_kgco2e_per_tonne_km, "kgCO2e/t-km", source)


def calculate_performance_metrics(production_kg: float, feed_kg: float, electricity_kwh: float, diesel_litres: float, initial_biomass_kg: Optional[float] = None) -> dict:
    if production_kg <= 0:
        raise ValueError("Production must be greater than zero")
    if any(x < 0 for x in (feed_kg, electricity_kwh, diesel_litres)):
        raise ValueError("Activity quantities must be non-negative")

    metrics = {
        "energy_intensity_kwh_per_kg": electricity_kwh / production_kg,
        "feed_intensity_kg_per_kg": feed_kg / production_kg,
        "diesel_intensity_l_per_kg": diesel_litres / production_kg,
        "fcr": None,
    }
    if initial_biomass_kg is not None:
        if initial_biomass_kg < 0 or initial_biomass_kg >= production_kg:
            raise ValueError("Initial biomass must be non-negative and lower than harvested production")
        biomass_gain = production_kg - initial_biomass_kg
        metrics["fcr"] = feed_kg / biomass_gain if biomass_gain > 0 else None
    return metrics


def generate_interventions(activities: list[Activity], production_kg: float, feed_kg: float, electricity_kwh: float, diesel_litres: float, feed_factor: Optional[float]) -> list[dict]:
    total = sum(a.kg_co2e for a in activities)
    if total <= 0 or production_kg <= 0:
        return []
    by_name = {a.name: a.kg_co2e for a in activities}
    interventions = []
    feed_em = by_name.get("Feed", 0.0)
    electricity_em = by_name.get("Electricity", 0.0)
    diesel_em = by_name.get("Diesel combustion", 0.0) + by_name.get("Diesel upstream", 0.0)
    transport_em = by_name.get("Feed transport", 0.0)

    if feed_em / total >= 0.50:
        interventions.append({"priority": 1, "area": "Feed efficiency & feed footprint", "hotspot_share": feed_em / total, "action": "Verify the feed supplier GHG profile and investigate feed conversion ratio (FCR), feed wastage and mortality before changing feed quantity.", "why": "Feed is the dominant measured emissions source.", "standard_basis": "ASC Farm Standard v1.0.1A2, §2.10 / Appendix 9; ASC Farm Interpretation Manual v1.0.1"})
    elif feed_em > 0:
        interventions.append({"priority": 2, "area": "Feed data quality", "hotspot_share": feed_em / total, "action": "Obtain and retain the current supplier GHG profile and confirm feed quantity by supplier for the reporting period.", "why": "Feed emissions are upstream Scope 3 and depend on documented supplier data.", "standard_basis": "ASC Farm Standard v1.0.1A2, feed GHG calculation method"})
    if electricity_em / total >= 0.15:
        interventions.append({"priority": 2, "area": "Energy efficiency", "hotspot_share": electricity_em / total, "action": "Measure electricity use by major load where practical, track kWh/kg shrimp, and investigate avoidable runtime or inefficient equipment.", "why": "Electricity is a material measured source.", "standard_basis": "ASC Farm Standard v1.0.1A2, §2.10; ASC Farm Interpretation Manual v1.0.1"})
    if diesel_em / total >= 0.05:
        interventions.append({"priority": 3, "area": "Diesel / fossil-fuel reduction", "hotspot_share": diesel_em / total, "action": "Track diesel litres per kg shrimp and identify generator/pump operating hours that can be reduced or replaced with more efficient or non-fossil energy where technically feasible.", "why": "Diesel creates direct and upstream emissions and is an energy-efficiency opportunity.", "standard_basis": "ASC Farm Standard v1.0.1A2, §2.10; ASC Farm Interpretation Manual v1.0.1"})
    if transport_em / total >= 0.10:
        interventions.append({"priority": 4, "area": "Feed transport", "hotspot_share": transport_em / total, "action": "Verify transport distance, mode and factor; then assess consolidation, sourcing logistics or lower-emission transport options where feasible.", "why": "Transport becomes a management priority when it is a material part of the measured footprint.", "standard_basis": "ASC Farm Interpretation Manual v1.0.1"})
    interventions.append({"priority": 5, "area": "GHG management plan & verification", "hotspot_share": 1.0, "action": "Set a baseline, choose measurable reduction actions, assign an owner and review the same metrics each production cycle/year.", "why": "A footprint is useful only when actions are implemented and their effectiveness is tracked.", "standard_basis": "ASC Farm Interpretation Manual v1.0.1; ASC Farm Standard v1.0.1A2"})
    return sorted(interventions, key=lambda x: x["priority"])


def calculate(production_kg: float, electricity_kwh: float, electricity_factor: float, diesel_litres: float, diesel_scope1_factor: float, diesel_upstream_factor: float, feed_kg: float, feed_factor: Optional[float], feed_source: str, transport_distance_km: float, transport_factor: Optional[float], electricity_source: str, diesel_source: str, transport_source: str, initial_biomass_kg: Optional[float] = None) -> dict:
    if production_kg <= 0:
        raise ValueError("Production must be greater than zero")
    activities = [electricity_emissions(electricity_kwh, electricity_factor, electricity_source)]
    activities.extend(diesel_emissions(diesel_litres, diesel_scope1_factor, diesel_upstream_factor, diesel_source))
    feed = feed_emissions(feed_kg, feed_factor, feed_source)
    if feed:
        activities.append(feed)
    transport = transport_emissions(feed_kg / 1000.0, transport_distance_km, transport_factor, transport_source)
    if transport:
        activities.append(transport)
    total = sum(a.kg_co2e for a in activities)
    return {
        "production_kg": production_kg,
        "total_kg_co2e": total,
        "carbon_intensity_kg_co2e_per_kg": total / production_kg,
        "activities": activities,
        "complete": feed is not None and transport is not None,
        "interventions": generate_interventions(activities, production_kg, feed_kg, electricity_kwh, diesel_litres, feed_factor),
        "metrics": calculate_performance_metrics(production_kg, feed_kg, electricity_kwh, diesel_litres, initial_biomass_kg),
    }
