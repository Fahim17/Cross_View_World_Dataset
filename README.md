# World Dataset Research Toolkit

Utilities, dataset metadata, evaluation results, and visualizations for cross-view geolocation research using ground-level and satellite imagery. The repository includes tools for downloading imagery, preparing geographic dataset splits, plotting global coverage, and comparing image-retrieval models qualitatively.

## Repository contents

| Path | Description |
| --- | --- |
| `datasets/` | OSV5M/OSV500K metadata, dataset splits, and image-path references |
| `csv/` | Combined, country-wise, and experimental CSV splits |
| `evaluation/` | Retrieval outputs and Recall@1/5/10 metrics for GeoQueryNet, GeoDTR, and QDFL |
| `fig/` | Dataset statistics, geographic maps, and retrieval figures |
| `qualitative_figures/` | Generated side-by-side retrieval comparisons |
| `metadata/` | Supporting geographic and land-cover metadata |
| `main.py` | Download a Google Street View image for one coordinate |
| `main2.py` | Batch-download Google Static Maps satellite images from an OSV5M CSV |
| `worldmap_display.py` | Plot latitude/longitude samples on an interactive or static world map |
| `qualitative_fig.py` | Compare the top-five satellite retrievals from three models |
| `helper_func.py` | Experiment ID, logging, and runtime helpers |
| `*.ipynb` | Exploratory data cleaning and analysis notebooks |

## Dataset format

The primary paired CSV files use one row per location. A typical row contains:

- `id`, `latitude`, and `longitude`
- country, region, sub-region, and city metadata
- `gnd_image_path`: path to the ground-level image
- `sat_image_path`: path to the paired satellite image

Retrieval result files identify a query using `query_row_index` and store ranked satellite row indices in `retrieved_top5_sat_img_ids`, separated by `|`.

Image files are expected beneath the dataset root referenced by the CSV paths. Large image collections may need to be obtained separately and are not necessarily included in the Git repository.

## Setup

Python 3.9 or newer is recommended. Create a virtual environment and install the core dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install pandas matplotlib pillow requests tqdm plotly
```

Optional dependencies:

```bash
# Geographic map features for static plots
python -m pip install cartopy

# Plotly static image export
python -m pip install kaleido
```

Jupyter is also required to run the included notebooks.

## Usage

### Plot dataset coverage

Generate an interactive HTML map:

```bash
python worldmap_display.py \
  --input csv/all.csv \
  --category-column country \
  --output world_map.html \
  --no-show
```

Generate a static image:

```bash
python worldmap_display.py \
  --input csv/all.csv \
  --category-column country \
  --output world_map.png \
  --no-show
```

Custom coordinate column names can be supplied with `--latitude-column` and `--longitude-column`.

### Generate qualitative retrieval comparisons

Before running `qualitative_fig.py`, update its configuration section with:

- the local OSV500K dataset root and test CSV
- the GeoQueryNet, GeoDTR, and QDFL result CSV paths
- the desired output directory, sample count, and random seed

Then run:

```bash
python qualitative_fig.py
```

The script selects cases where GeoQueryNet retrieves the correct Top-1 match while GeoDTR and QDFL do not. It writes comparison images and the selected query indices to `qualitative_figures/`.

### Download map imagery

`main.py` downloads one Street View image, while `main2.py` downloads satellite images for a configured range of CSV rows. These scripts require a Google Maps Platform API key and enabled billing/APIs.

Before use:

1. Store the API key in an environment variable or another local secret store.
2. Update the coordinate, input CSV, output directory, and row-range settings as needed.
3. Confirm Google Maps Platform quotas and usage terms before starting a batch download.

Do not commit API keys, credentials, downloaded caches, or other secrets.

## Evaluation outputs

Each model directory under `evaluation/` contains retrieval metrics and query subsets such as:

- `retrieval_metrics.csv`
- `qualitative_retrieval_results.csv`
- `top1_correct_queries.csv`
- `top5_correct_but_not_top1.csv`
- `top10_correct_but_not_top5.csv`

These files support both aggregate recall analysis and inspection of individual successes and failures.

## Reproducibility notes

- Preserve CSV row order: the evaluation files use dataset row indices as retrieval identifiers.
- Relative image paths are resolved from the configured dataset root.
- The qualitative comparison script uses a fixed random seed by default.
- Generated logs are written to `logs/` by the batch downloader.

## License and citation

No license or citation information is currently included. Add the appropriate project license and citation details before distributing or reusing the dataset and generated imagery. Source datasets and imagery remain subject to their respective licenses and service terms.
