# CoastalCarbon AI — V1 Accounting Methodology

## Purpose
CoastalCarbon AI estimates farm-level greenhouse-gas emissions for shrimp/aquaculture operations from documented activity data. The calculation is deterministic: activity data × documented emission factor.

## Current boundary
V1 is a farm-level operational footprint using the activity categories currently supported by the application:
- purchased electricity (Scope 2)
- on-farm diesel combustion (Scope 1)
- diesel upstream emissions (Scope 3, where the selected factor includes them)
- feed production/upstream emissions (Scope 3) using a supplier-specific/documented factor
- feed transport (Scope 3) using a documented tonne-km factor

Aeration and refrigeration are not added as separate emissions if their electricity consumption is already included in the electricity total. They may be tracked as sub-activities in a future version.

## Core equation
For each activity:

`emissions (kg CO2e) = activity data × emission factor`

Total footprint is the sum of included activities. Carbon intensity is total footprint divided by reported shrimp production in kg.

## Data hierarchy
1. Prefer primary records: utility bills, fuel invoices/logs, feed invoices and production records.
2. Prefer supplier-specific feed GHG profiles where available.
3. Any estimate or user-supplied factor must be clearly labelled and retained with its source/boundary.
4. Missing required factors are not treated as zero.

## Verification status
"Calculation complete" means required factors were supplied for the current V1 calculation. It does not mean the source documents, emission factors, boundaries or production records have been independently verified.

## Standards basis
The methodology is designed with reference to the GHG Protocol activity-data/emission-factor approach and current ASC Farm Standard requirements/guidance for aquaculture energy and feed-related GHG accounting. CoastalCarbon AI is not an ASC certification tool and this document does not make a certification claim.

## Important limitations
- V1 does not yet represent a full cradle-to-gate LCA of shrimp.
- Feed factors must be checked for their declared system boundary before external reporting.
- Transport currently models feed transport only.
- Current carbon intensity is on a reported production/live-weight basis; edible-weight conversion is not implemented in V1.
- Emission factors must be reviewed and versioned before external reporting.
- Intervention recommendations are management actions, not certification findings or guaranteed savings.
