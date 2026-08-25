#!/usr/bin/env python3
"""Display latitude/longitude points on a world map from a single combined CSV.

Usage:
    python worldmap_display.py --input csv/all.csv --output world_map.png
    python worldmap_display.py --input csv/all.csv --category-column Category --output world_map.pdf
"""

import argparse
import os
import sys

import pandas as pd
import matplotlib.pyplot as plt

try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    CARTOPY_AVAILABLE = True
except ImportError:
    CARTOPY_AVAILABLE = False


def build_dataframe(csv_path, category_col=None, lat_col="latitude", lon_col="longitude"):
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    df = pd.read_csv(csv_path)

    required_columns = {lat_col, lon_col}
    if not required_columns.issubset(df.columns):
        raise ValueError(
            f"CSV must contain columns {required_columns}. Found: {list(df.columns)}"
        )

    if df[[lat_col, lon_col]].isnull().any(axis=None):
        df = df.dropna(subset=[lat_col, lon_col])

    df = df.rename(columns={lat_col: "latitude", lon_col: "longitude"})

    if category_col:
        if category_col not in df.columns:
            raise ValueError(
                f"Category column '{category_col}' was not found in CSV."
            )
        df = df.rename(columns={category_col: "category"})
        df = df[~df["category"].isnull()]
        df["category"] = df["category"].astype(str)
    else:
        df["category"] = "All points"

    print(
        f"Loaded {len(df)} points from {csv_path}. "
        f"Latitude range: {df['latitude'].min():.4f} to {df['latitude'].max():.4f}, "
        f"Longitude range: {df['longitude'].min():.4f} to {df['longitude'].max():.4f}."
    )

    return df[["latitude", "longitude", "category"]]


def plot_with_plotly(df, output_path=None, show=True):
    fig = px.scatter_geo(
        df,
        lat="latitude",
        lon="longitude",
        color="category",
        title="World points by category",
        projection="natural earth",
        hover_name="category",
        opacity=0.8,
        height=600,
    )

    if output_path:
        if output_path.lower().endswith(('.html', '.htm')):
            fig.write_html(output_path)
            print(f"Saved interactive map to {output_path}")
        elif output_path.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf', '.svg')):
            try:
                fig.write_image(output_path, width=2400, height=1200, scale=2)
                print(f"Saved static map to {output_path}")
            except Exception as exc:
                print(
                    "Failed to save image with Plotly. Falling back to matplotlib for static output."
                )
                return False
        else:
            fig.write_html(output_path + ".html")
            print(f"Saved interactive map to {output_path}.html")

    if show:
        fig.show()


def plot_with_matplotlib(df, output_path=None, show=True):
    categories = df["category"].unique()
    colors = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple", "tab:brown"]
    color_map = {category: colors[i % len(colors)] for i, category in enumerate(categories)}

    if CARTOPY_AVAILABLE:
        fig = plt.figure(figsize=(12, 6))
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
        ax.add_feature(cfeature.LAND, facecolor="#f0f0f0")
        ax.add_feature(cfeature.OCEAN, facecolor="#dbe9f9")
        ax.add_feature(cfeature.COASTLINE, linewidth=0.6)
        ax.add_feature(cfeature.BORDERS, linestyle=":")
        ax.set_global()
    else:
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.set_facecolor("#dbe9f9")
        ax.set_xlim(-180, 180)
        ax.set_ylim(-90, 90)
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        ax.set_title("World points by category")
        ax.grid(True, linestyle="--", alpha=0.4)

    marker_size = 1 if len(df) > 100000 else 4
    for category in categories:
        subset = df[df["category"] == category]
        ax.scatter(
            subset["longitude"],
            subset["latitude"],
            s=marker_size,
            alpha=0.7,
            label=category,
            color=color_map.get(category, None),
            edgecolors="none",
            transform=ccrs.PlateCarree() if CARTOPY_AVAILABLE else None,
        )

    ax.legend(title="Category")
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        print(f"Saved map image to {output_path}")

    if show:
        plt.show()


def plot_world_map(df, output_path=None, show=True):
    if output_path and output_path.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf', '.svg')):
        print("Saving a high-quality static image with Matplotlib.")
        plot_with_matplotlib(df, output_path=output_path, show=show)
        return

    if PLOTLY_AVAILABLE:
        plot_with_plotly(df, output_path=output_path, show=show)
    else:
        print("Plotly is not installed, using matplotlib fallback.")
        plot_with_matplotlib(df, output_path=output_path, show=show)


def parse_args():
    parser = argparse.ArgumentParser(description="Plot world points from a single combined CSV file.")
    parser.add_argument("--input", required=True, help="CSV file containing all points")
    parser.add_argument("--category-column", default=None, help="Optional column name used for point categories")
    parser.add_argument("--latitude-column", default="latitude", help="Latitude column name")
    parser.add_argument("--longitude-column", default="longitude", help="Longitude column name")
    parser.add_argument("--output", default=None, help="Optional output path (HTML, PNG, JPG, PDF, SVG). If omitted, the plot is shown interactively.")
    parser.add_argument("--no-show", action="store_true", help="Do not show the plot interactively")
    return parser.parse_args()


def main():
    args = parse_args()
    df = build_dataframe(
        args.input,
        category_col=args.category_column,
        lat_col=args.latitude_column,
        lon_col=args.longitude_column,
    )

    if df.empty:
        print("No points available to plot.")
        sys.exit(1)

    plot_world_map(df, output_path=args.output, show=not args.no_show)


if __name__ == "__main__":
    main()
