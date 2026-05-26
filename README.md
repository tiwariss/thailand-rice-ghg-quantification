# Price Policy as a Driver of Agricultural Methane: Evidence from Thailand's Rice Sector, 1961–2024

**Sirawit Tangchitwatthanakon**  
The Hong Kong University of Science and Technology (Guangzhou)  
IPEN6100F Final Project

---

## Abstract

This study applies IPCC 2006 Tier 1 at two scales — a national time series (1961–2024) and a 77-province spatial analysis (2022–2024) — to quantify rice CH₄ emissions from Thailand's paddy sector and examine how the structural design of price-support programmes determines their emission impact.

**Key findings:**
- National emissions averaged **1,420 Gg CH₄ yr⁻¹** (39.8 Mt CO₂e), peaking at 1,884 Gg in 2012 and falling to 1,726 Gg by 2024
- The 2011–2014 Rice Pledging Scheme (unlimited price guarantee, 40–50% above market) added ~988,000 ha beyond the price effect alone (*p* < 0.001), driving the 64-year emission peak
- A counterfactual area cap (40 rai/household) from 2011 would have avoided **606 Gg CH₄** (17.0 Mt CO₂e) over four years
- Emission intensity fell 44% (92.5 → 51.4 kg CH₄ t⁻¹) as yields improved, yet absolute emissions rose 84% — a rebound effect
- AWD adoption in dry-season irrigated provinces saves 57–96 Gg yr⁻¹ (30–50% EF reduction scenarios)

**→ Thailand's NDC agriculture targets are more sensitive to the *design* of price-support programmes than to yield improvement or field-level mitigation alone.**

---

## Repository Structure

```
├── resources/
│   ├── data/                                     # Raw source files
│   │   ├── faostat_thailand_rice_1961_2024.csv   # FAOSTAT national harvested area & production
│   │   ├── OAE (20XX) *.pdf                      # OAE seasonal source reports
│   │   └── gadm_THA/                             # GADM shapefiles (not in repo — download separately)
│   └── clean/                                    # Processed / extracted data
│       ├── oae_provincial_rice_2022_2024.csv     # Provincial rice data extracted from OAE PDFs (77 provinces)
│       ├── thailand_rice_price.csv               # Farm-gate paddy price (extracted from OAE PDF)
│       ├── oni_growing_season.csv                # NOAA ONI climate index (growing season)
│       ├── thailand_rice_ghg_results.csv         # National CH4 inventory output
│       ├── thailand_rice_provincial_ghg.csv      # Provincial CH4 inventory output
│       ├── oae_raw_data.csv                      # OAE intermediate extraction output
│       └── oae_rice_price_variety.xlsx           # OAE rice variety price table
├── output/
│   └── figures/                                  # All output plots (PNG)
├── code/
│   ├── ghg_spatial_analysis.ipynb               # Full analysis: national inventory + provincial spatial + Monte Carlo
│   └── parse_rice_pdfs.py                        # PDF parser for OAE seasonal reports
└── paper.pdf                                     # Full paper (22 pp.)
```

---

## Methods

**Emission model:** IPCC 2006 Guidelines Vol. 4 Ch. 5, Tier 1

```
CH₄ = EFc × SFw × SFp × SFo × tp × Area × 10⁻⁶
```

| Parameter | Value | Source |
|-----------|-------|--------|
| EFc | 1.30 kg CH₄ ha⁻¹ day⁻¹ | IPCC Table 5.11 |
| SFw (national) | 1.00 | IPCC Table 5.12 |
| SFw (provincial) | 0.52 NE/South · 1.0 Central/North | IPCC Table 5.12; Arunrat & Pumijumnong (2017) |
| tp (main season) | 118 days | Buddhaboon et al. (2011) |
| tp (dry season) | 111 days | Buddhaboon et al. (2011) |
| GWP₁₀₀ (CH₄) | 28 | IPCC AR5 |

**Uncertainty:** Monte Carlo analysis (*N* = 10,000) varying SFw rainfed [0.27–0.71], SFw irrigated [0.61–1.00], and season lengths (σ = 5/6 days). Provincial total 90% CI: 803–1,315 Gg, CV = 14.7%.

**Econometrics:** OLS regression of harvested area on farm-gate price + policy dummy (2011–2014 Pledging Scheme), with Newey–West HAC standard errors.

---

## Data Sources

| Dataset | Source | Coverage |
|---------|--------|----------|
| National harvested area & production | [FAOSTAT](https://www.fao.org/faostat/) (element code 5312) | 1961–2024 |
| Provincial harvested area & production | Office of Agricultural Economics (OAE), Thailand | 2022–2024 |
| Farm-gate paddy price | OAE, Thailand | 2007–2024 |
| Province boundaries | [GADM 4.1](https://gadm.org/) Level 1 | — |
| ONI climate index | NOAA Climate Prediction Center | — |

> **Large files not in repo** (download separately):
> - GADM shapefiles: [gadm.org](https://gadm.org/download_country.html) → Thailand Level 1
> - USDA PSD data: [apps.fas.usda.gov/psdonline](https://apps.fas.usda.gov/psdonline/app/index.html#/app/downloads)

---

## How to Run

**Requirements:**
```
pandas numpy matplotlib geopandas scipy statsmodels pdfplumber jupyter
```

**1. Parse OAE PDFs → extracted CSVs:**
```bash
python code/parse_rice_pdfs.py
```

**2. Run full analysis (national + provincial):**
```bash
jupyter notebook code/ghg_spatial_analysis.ipynb
```

---

## Keywords

methane emissions · paddy rice cultivation · greenhouse gas inventory · IPCC Tier 1 · Thailand · subnational spatial analysis · agricultural price support · NDC · alternate wetting and drying
