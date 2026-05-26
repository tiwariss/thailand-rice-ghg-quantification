"""
GHG Quantification — CH4 Emissions from Rice Cultivation in Thailand
IPCC 2006 Guidelines, Volume 4 (Agriculture), Chapter 5 — Tier 1 Bottom-Up Approach

Source: FAOSTAT QCL — Crops and livestock products, Thailand, Rice (1961–2024)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os

# ─────────────────────────────────────────────────────────────
# 1. IPCC 2006 TIER 1 EMISSION FACTORS (Vol.4, Ch.5, Table 5.11)
# ─────────────────────────────────────────────────────────────
EF_c        = 1.30      # kg CH4 / ha / day  — baseline EF, continuously flooded
SF_w        = 1.0       # scaling factor for water regime (continuously flooded during season)
SF_p        = 1.0       # scaling factor for pre-season water regime (≤ 30 days flooding before planting)
SF_o        = 1.0       # scaling factor for organic amendments (none applied — Tier 1 default)
t_p         = 118       # days — wet/main season cultivation period, Thailand (Buddhaboon et al., 2011, Field Crops Res. 124:270-277)

# Adjusted seasonal EF (kg CH4 / ha / season)
# IPCC Eq. 5.1: EF_i = EF_c × SF_w × SF_p × SF_o × t_p
EF_season   = EF_c * SF_w * SF_p * SF_o * t_p   # = 130 kg CH4/ha/season

# Global Warming Potential (100-year, IPCC AR5 / IPCC 2021)
GWP_CH4     = 28        # dimensionless (AR5; use 25 for AR4)

# ─────────────────────────────────────────────────────────────
# 2. LOAD & PARSE FAOSTAT CSV
# ─────────────────────────────────────────────────────────────
CSV_PATH = r"../resources/FAOSTAT_data_en_5-17-2026.csv"
raw = pd.read_csv(CSV_PATH)

# Keep only "Area harvested" rows (Element Code 5312)
area_df = (
    raw[raw["Element"] == "Area harvested"]
    .rename(columns={"Year": "year", "Value": "area_ha"})
    [["year", "area_ha"]]
    .dropna(subset=["area_ha"])
    .sort_values("year")
    .reset_index(drop=True)
)
area_df["year"]    = area_df["year"].astype(int)
area_df["area_ha"] = area_df["area_ha"].astype(float)

# ─────────────────────────────────────────────────────────────
# 3. BOTTOM-UP CH4 EMISSION CALCULATION
# ─────────────────────────────────────────────────────────────
# IPCC 2006 Eq. 5.1 (rearranged for annual inventory):
#   Emissions (Gg CH4/yr) = Area (ha) × EF_season (kg CH4/ha) × 1e-6
#
# Note: FAOSTAT "area harvested" counts each crop season separately,
# so it correctly represents total flooded area-season units per year.

df = area_df.copy()
df["CH4_Gg"]     = df["area_ha"] * EF_season * 1e-6          # Gg CH4 / year
df["CH4_kt"]     = df["CH4_Gg"] * 1e3                        # kt CH4 / year (same as Gg × 1000 / 1000 — for display)
df["CO2e_Gg"]    = df["CH4_Gg"] * GWP_CH4                    # Gg CO2-eq / year
df["CO2e_Mt"]    = df["CO2e_Gg"] / 1e3                       # Mt CO2-eq / year

# ─────────────────────────────────────────────────────────────
# 4. SUMMARY STATISTICS
# ─────────────────────────────────────────────────────────────
print("=" * 65)
print("  GHG QUANTIFICATION — THAILAND RICE (IPCC 2006 Tier 1)")
print("=" * 65)
print(f"\n  Emission Factor Parameters:")
print(f"    EF_c (baseline)          = {EF_c:.2f} kg CH4/ha/day")
print(f"    SF_w (water regime)      = {SF_w:.2f}")
print(f"    SF_p (pre-season water)  = {SF_p:.2f}")
print(f"    SF_o (organic amendment) = {SF_o:.2f}")
print(f"    t_p  (season length)     = {t_p} days")
print(f"    EF_season                = {EF_season:.1f} kg CH4/ha/season")
print(f"    GWP_CH4 (AR5, 100-yr)   = {GWP_CH4}")

print(f"\n  Period: {df['year'].min()} – {df['year'].max()}")
print(f"  Years:  {len(df)}")

print("\n  Key Results:")
print(f"    Mean area harvested  : {df['area_ha'].mean()/1e6:.2f}  M ha/yr")
print(f"    Mean CH4 emissions   : {df['CH4_Gg'].mean():.1f} Gg CH4/yr")
print(f"    Mean CO2e emissions  : {df['CO2e_Gg'].mean():.1f} Gg CO2e/yr  ({df['CO2e_Mt'].mean():.2f} Mt CO2e/yr)")
print(f"    Peak CH4 year        : {df.loc[df['CH4_Gg'].idxmax(), 'year']}  ({df['CH4_Gg'].max():.1f} Gg CH4)")
print(f"    Min  CH4 year        : {df.loc[df['CH4_Gg'].idxmin(), 'year']}  ({df['CH4_Gg'].min():.1f} Gg CH4)")

# Recent decade
recent = df[df["year"] >= 2015]
print(f"\n  Recent period (2015–{df['year'].max()}):")
print(f"    Mean CH4             : {recent['CH4_Gg'].mean():.1f} Gg CH4/yr")
print(f"    Mean CO2e            : {recent['CO2e_Mt'].mean():.2f} Mt CO2e/yr")
print(f"    Latest ({df['year'].max()})        : {df.iloc[-1]['CH4_Gg']:.1f} Gg CH4  |  {df.iloc[-1]['CO2e_Mt']:.2f} Mt CO2e")

# ─────────────────────────────────────────────────────────────
# 5. EXPORT RESULTS
# ─────────────────────────────────────────────────────────────
out_cols = {
    "year":     "Year",
    "area_ha":  "Area_Harvested_ha",
    "CH4_Gg":   "CH4_Emissions_Gg",
    "CO2e_Gg":  "CO2e_Emissions_Gg",
    "CO2e_Mt":  "CO2e_Emissions_Mt",
}
result_df = df[list(out_cols.keys())].rename(columns=out_cols)
result_df.to_csv("thailand_rice_ghg_results.csv", index=False, float_format="%.4f")
print("\n  Results saved → thailand_rice_ghg_results.csv")

# ─────────────────────────────────────────────────────────────
# 6. PLOTS
# ─────────────────────────────────────────────────────────────
fig, axes = plt.subplots(3, 1, figsize=(12, 14), sharex=True)
fig.suptitle(
    "Thailand Rice — GHG Quantification (IPCC 2006 Tier 1)\n"
    "CH₄ from Flooded Rice Paddies, 1961–2024",
    fontsize=14, fontweight="bold", y=0.98
)

years = df["year"]

# --- Panel 1: Area harvested ---
ax1 = axes[0]
ax1.fill_between(years, df["area_ha"] / 1e6, alpha=0.25, color="steelblue")
ax1.plot(years, df["area_ha"] / 1e6, color="steelblue", linewidth=1.5)
ax1.set_ylabel("Area Harvested (M ha)", fontsize=11)
ax1.set_title("Activity Data — Area Harvested", fontsize=11)
ax1.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f"))
ax1.grid(True, alpha=0.3)
ax1.annotate(
    f'Peak: {df.loc[df["area_ha"].idxmax(), "year"]}\n{df["area_ha"].max()/1e6:.2f} M ha',
    xy=(df.loc[df["area_ha"].idxmax(), "year"], df["area_ha"].max() / 1e6),
    xytext=(10, -20), textcoords="offset points",
    arrowprops=dict(arrowstyle="->", color="steelblue"),
    fontsize=9, color="steelblue"
)

# --- Panel 2: CH4 emissions ---
ax2 = axes[1]
ax2.fill_between(years, df["CH4_Gg"], alpha=0.25, color="darkorange")
ax2.plot(years, df["CH4_Gg"], color="darkorange", linewidth=1.5)
ax2.set_ylabel("CH₄ Emissions (Gg CH₄/yr)", fontsize=11)
ax2.set_title(
    f"CH₄ Emissions — IPCC Eq. 5.1  |  EF = {EF_c} kg/ha/day × {t_p} days = {EF_season} kg CH₄/ha/season",
    fontsize=11
)
ax2.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f"))
ax2.grid(True, alpha=0.3)
ax2.axhline(df["CH4_Gg"].mean(), color="darkorange", linestyle="--", linewidth=1, alpha=0.7,
            label=f'Mean = {df["CH4_Gg"].mean():.0f} Gg/yr')
ax2.legend(fontsize=9)

# --- Panel 3: CO2-equivalent ---
ax3 = axes[2]
ax3.fill_between(years, df["CO2e_Mt"], alpha=0.25, color="firebrick")
ax3.plot(years, df["CO2e_Mt"], color="firebrick", linewidth=1.5)
ax3.set_ylabel("CO₂-equivalent (Mt CO₂e/yr)", fontsize=11)
ax3.set_title(f"CO₂-equivalent Emissions  |  GWP_CH₄ = {GWP_CH4} (IPCC AR5, 100-yr)", fontsize=11)
ax3.set_xlabel("Year", fontsize=11)
ax3.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f"))
ax3.grid(True, alpha=0.3)
ax3.axhline(df["CO2e_Mt"].mean(), color="firebrick", linestyle="--", linewidth=1, alpha=0.7,
            label=f'Mean = {df["CO2e_Mt"].mean():.1f} Mt CO₂e/yr')
ax3.legend(fontsize=9)

plt.tight_layout()
plt.savefig("../figures/thailand_rice_ghg.png", dpi=150, bbox_inches="tight")
plt.show()
print("  Plot saved → figures/thailand_rice_ghg.png")
print("=" * 65)
