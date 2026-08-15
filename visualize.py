"""
visualize.py -- Chart-building functions for the HCES 2022-23 project

Uses matplotlib only (no seaborn dependency). Each function returns the
matplotlib Figure so you can further customize, save, or display it in
Jupyter.

Usage:
    from visualize import plot_category_share_by_quintile, plot_mpce_by_quintile, plot_mpce_distribution

    fig1 = plot_category_share_by_quintile(table, sector=1)  # rural
    fig1.savefig("category_share_rural.png", dpi=150, bbox_inches="tight")

    fig2 = plot_mpce_by_quintile(household_master)
    fig3 = plot_mpce_distribution(household_master)
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SECTOR_LABELS = {1: "Rural", 2: "Urban"}


def plot_category_share_by_quintile(category_share_df: pd.DataFrame, sector: int = None) -> plt.Figure:
    """
    Stacked bar chart of category % share, one bar per quintile.

    category_share_df: output of category_analysis.category_share_table(),
    with a MultiIndex of (sector, mpce_quintile) and one column per category.

    sector: if given (1=rural, 2=urban), plots only that sector. If None,
    plots both sectors side by side as two subplots.
    """
    df = category_share_df.copy()

    if sector is not None:
        subset = df.xs(sector, level="sector")
        fig, ax = plt.subplots(figsize=(9, 6))
        _stacked_bar(ax, subset, title=f"Category Spend Share by MPCE Quintile ({SECTOR_LABELS.get(sector, sector)})")
        fig.tight_layout()
        return fig

    sectors = df.index.get_level_values("sector").unique()
    fig, axes = plt.subplots(1, len(sectors), figsize=(9 * len(sectors), 6), sharey=True)
    if len(sectors) == 1:
        axes = [axes]
    for ax, s in zip(axes, sectors):
        subset = df.xs(s, level="sector")
        _stacked_bar(ax, subset, title=SECTOR_LABELS.get(s, s))
    fig.suptitle("Category Spend Share by MPCE Quintile", fontsize=14, y=1.02)
    fig.tight_layout()
    return fig


def _stacked_bar(ax, subset_df, title):
    categories = subset_df.columns.tolist()
    quintiles = subset_df.index.tolist()
    bottom = np.zeros(len(quintiles))

    cmap = plt.get_cmap("tab10")
    for i, cat in enumerate(categories):
        values = subset_df[cat].values
        ax.bar([f"Q{q}" for q in quintiles], values, bottom=bottom, label=cat, color=cmap(i % 10))
        bottom += values

    ax.set_title(title)
    ax.set_xlabel("MPCE Quintile (1=poorest, 5=richest)")
    ax.set_ylabel("% Share of Spend")
    ax.set_ylim(0, 100)
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)


def plot_mpce_by_quintile(household_master: pd.DataFrame) -> plt.Figure:
    """
    Grouped bar chart: average (weighted) MPCE per quintile, rural vs urban
    side by side.
    """
    df = household_master.copy()

    def weighted_mean(g):
        return np.average(g["mpce"], weights=g["final_weight"])

    summary = df.groupby(["sector", "mpce_quintile"]).apply(weighted_mean, include_groups=False).unstack("sector")
    summary.columns = [SECTOR_LABELS.get(c, c) for c in summary.columns]

    fig, ax = plt.subplots(figsize=(8, 5))
    summary.plot(kind="bar", ax=ax, color=["#4C72B0", "#DD8452"])
    ax.set_title("Average MPCE by Quintile")
    ax.set_xlabel("MPCE Quintile (1=poorest, 5=richest)")
    ax.set_ylabel("Weighted Avg MPCE (Rs)")
    ax.legend(title="Sector")
    ax.set_xticklabels([f"Q{i}" for i in summary.index], rotation=0)
    fig.tight_layout()
    return fig


def plot_mpce_distribution(household_master: pd.DataFrame) -> plt.Figure:
    """
    Side-by-side histograms of MPCE distribution, rural vs urban. Uses the
    (already winsorized, if applied) mpce column, so extreme outliers won't
    distort the x-axis.
    """
    df = household_master.copy()
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)

    for ax, sector in zip(axes, [1, 2]):
        subset = df[df["sector"] == sector]
        ax.hist(subset["mpce"], bins=50, color="#4C72B0" if sector == 1 else "#DD8452", edgecolor="white")
        ax.set_title(SECTOR_LABELS.get(sector, sector))
        ax.set_xlabel("MPCE (Rs)")
        ax.axvline(np.average(subset["mpce"], weights=subset["final_weight"]), color="black", linestyle="--", label="Weighted Mean")
        ax.axvline(subset["mpce"].median(), color="gray", linestyle=":", label="Median")
        ax.legend(fontsize=8)

    axes[0].set_ylabel("Number of Households")
    fig.suptitle("MPCE Distribution by Sector")
    fig.tight_layout()
    return fig


if __name__ == "__main__":
    print("This module is meant to be imported, e.g.:")
    print("  from visualize import plot_category_share_by_quintile, plot_mpce_by_quintile, plot_mpce_distribution")
