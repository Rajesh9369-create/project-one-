# CoastalCarbon AI — Aqua Carbon Tracker V1

A transparent, auditable carbon-footprint calculator for aquaculture MSMEs. V1 focuses on calculation accuracy before AI document extraction.

## Methodology

The engine follows the current ASC Farm Standard approach for aquaculture GHG accounting: farm energy includes on-site fuels and production electricity; feed and feed transport are Scope 3; electricity uses a documented regional/national grid factor; results are reported relative to production. ASC explicitly recommends its own GHG calculator and requires the emission-factor source to be documented. See the methodology references below.

**Important:** this application does not invent a generic feed emission factor. Feed emissions must be supplied from the feed supplier's GHG profile or another documented factor with a compatible system boundary. If no factor is available, the application marks the result as incomplete instead of silently producing a misleading number.

## V1 inputs

- Production: kg live-weight shrimp harvested/net production
- Grid electricity: kWh + documented grid emission factor
- Diesel: litres
- Diesel Scope 1 and upstream Scope 3 factors
- Feed: kg + supplier-specific kg CO2e/kg feed factor
- Feed transport: tonnes + km + kg CO2e/tonne-km factor
- Optional other inputs: quantity + emission factor

## Run locally

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Test

```bash
pytest -q
```

## Current factor sources

- ASC Farm Standard v1.0.1A2: diesel Scope 1 = 2.71 kg CO2e/L and Scope 3 = 0.63 kg CO2e/L; electricity requires a documented national/regional grid factor; feed requires feed-supplier GHG data. https://programme-centre.asc-aqua.org/farm-v1/farm-standard/
- Central Electricity Authority (CEA) CO2 Baseline Database: the CEA publishes versioned Indian grid emission factors. The repository deliberately stores the selected factor with its source/version so it can be updated without changing the calculation engine. https://cea.nic.in/cdm-co2-baseline-database/

The included example uses CEA's published FY2022-23 weighted-average grid factor of **0.716 tCO2/MWh = 0.716 kgCO2/kWh** from the CEA Version 19 user guide. This is an example factor, not a claim that it is the latest available factor; update `factors.json` when using a newer CEA version. The UI displays the factor source and version.

## Scope and boundary

V1 calculates farm-gate attributional emissions from:

1. electricity used for production (Scope 2),
2. on-site diesel combustion and diesel upstream emissions (Scopes 1 + 3),
3. feed production emissions supplied by the feed producer (Scope 3),
4. transport of feed from mill to farm (Scope 3), and
5. optional documented inputs.

Aeration and refrigeration are **activities under electricity**, not additional emissions categories, to prevent double counting. Later versions can allocate electricity to aeration/refrigeration if the user supplies sub-meter or equipment-level energy data.

V1 reports **kg CO2e per kg net live-weight production**. It does not claim edible-product intensity unless an explicit, documented conversion/yield factor is supplied.
