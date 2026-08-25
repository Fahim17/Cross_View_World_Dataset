import os
import random
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image, ImageOps


# ============================================================
# 1. Configuration
# ============================================================

DATASET_ROOT = "/home/fahimul/Documents/Research/Proj_worldDataset/datasets/osv500k"

DATASET_CSV = "/home/fahimul/Documents/Research/Proj_worldDataset/datasets/osv500k/test.csv"

GEOQUERYNET_RESULT_CSV = "evaluation/D10/qualitative_retrieval_results.csv"
GEODTR_RESULT_CSV = "evaluation/geodtr/qualitative_retrieval_results.csv"
QDFL_RESULT_CSV = "evaluation/qdfl/qualitative_retrieval_results.csv"

OUTPUT_DIR = "./qualitative_figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

NUM_SAMPLES_TO_PLOT = 5
RANDOM_SEED = 42

# Dataset CSV columns
ID_COL = "id"
GROUND_PATH_COL = "gnd_image_path"
SAT_PATH_COL = "sat_image_path"

# Result CSV columns
QUERY_ROW_COL = "query_row_index"
TOP5_COL = "retrieved_top5_sat_img_ids"


# DATASET_ROOT = "/home/fahimul/Documents/Research/Proj_worldDataset/datasets/osv500k"

# DATASET_CSV = "/home/fahimul/Documents/Research/Proj_worldDataset/datasets/osv500k/test.csv"

# GEOQUERYNET_RESULT_CSV = "evaluation/D10/qualitative_retrieval_results.csv"
# GEODTR_RESULT_CSV = "evaluation/geodtr/qualitative_retrieval_results.csv"
# QDFL_RESULT_CSV = "evaluation/qdfl/qualitative_retrieval_results.csv"

# OUTPUT_DIR = "./qualitative_figures"
# os.makedirs(OUTPUT_DIR, exist_ok=True)

# NUM_SAMPLES_TO_PLOT = 5
# RANDOM_SEED = 42

# # Dataset CSV columns
# ID_COL = "id"
# GROUND_PATH_COL = "gnd_image_path"
# SAT_PATH_COL = "sat_image_path"

# # Qualitative result CSV columns
# QUERY_ID_COL = "query_ground_img_id"
# TRUE_SAT_ID_COL = "true_sat_img_id"
# TOP1_COL = "retrieved_top1_sat_img_id"
# TOP5_COL = "retrieved_top5_sat_img_ids"


# ============================================================
# 2. Utility functions
# ============================================================

def normalize_row_index(x):
    """
    Converts row index values like '15', '15.0', 15 into int.
    """
    if pd.isna(x):
        return None

    x = str(x).strip()

    if x.endswith(".0"):
        x = x[:-2]

    return int(x)


def split_top5_row_indices(top5_string):
    """
    Top-5 IDs are saved as:
        index_row_id1|index_row_id2|index_row_id3|index_row_id4|index_row_id5
    """
    if pd.isna(top5_string):
        return []

    top5_string = str(top5_string).strip()

    if "|" in top5_string:
        parts = top5_string.split("|")
    elif "," in top5_string:
        parts = top5_string.split(",")
    else:
        parts = top5_string.split()

    row_indices = []

    for p in parts:
        p = p.strip()
        if p != "":
            row_indices.append(normalize_row_index(p))

    return row_indices


def resolve_path(root, image_path):
    """
    Supports both absolute and relative image paths.
    """
    image_path = str(image_path)

    if os.path.isabs(image_path):
        return image_path

    return os.path.join(root, image_path)


def load_image(image_path, image_size=224):
    """
    Load image and resize/crop for clean plotting.
    """
    try:
        img = Image.open(image_path).convert("RGB")
        img = ImageOps.fit(
            img,
            (image_size, image_size),
            method=Image.Resampling.LANCZOS
        )
        return img

    except Exception as e:
        print(f"Could not load image: {image_path}")
        print(e)
        return Image.new("RGB", (image_size, image_size), color=(240, 240, 240))


def get_ground_path_from_row(dataset_df, row_index):
    row = dataset_df.iloc[row_index]
    return resolve_path(DATASET_ROOT, row[GROUND_PATH_COL])


def get_sat_path_from_row(dataset_df, row_index):
    row = dataset_df.iloc[row_index]
    return resolve_path(DATASET_ROOT, row[SAT_PATH_COL])


def get_display_id_from_row(dataset_df, row_index):
    """
    This is only for writing titles.
    The retrieval matching itself uses row index.
    """
    if ID_COL in dataset_df.columns:
        return str(dataset_df.iloc[row_index][ID_COL])
    return str(row_index)


def show_image(ax, img, title=None, border_color=None, linewidth=4):
    ax.imshow(img)
    ax.set_xticks([])
    ax.set_yticks([])

    if title is not None:
        ax.set_title(title, fontsize=8)

    if border_color is not None:
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_edgecolor(border_color)
            spine.set_linewidth(linewidth)
    else:
        for spine in ax.spines.values():
            spine.set_visible(False)


# ============================================================
# 3. Load dataset CSV
# ============================================================

dataset_df = pd.read_csv(DATASET_CSV)

# Very important:
# keep the row order exactly the same as evaluation.
dataset_df = dataset_df.reset_index(drop=True)

print(f"Loaded dataset CSV with {len(dataset_df)} rows")


# ============================================================
# 4. Load result CSVs
# ============================================================

def load_result_csv(csv_path, model_name):
    df = pd.read_csv(csv_path)

    df[QUERY_ROW_COL] = df[QUERY_ROW_COL].apply(normalize_row_index)

    df["top5_row_indices"] = df[TOP5_COL].apply(split_top5_row_indices)

    df["retrieved_top1_row_index"] = df["top5_row_indices"].apply(
        lambda x: x[0] if len(x) > 0 else None
    )

    # Because ground and satellite positive pair are from the same row
    df["true_sat_row_index"] = df[QUERY_ROW_COL]

    df["top1_correct_computed"] = (
        df["retrieved_top1_row_index"] == df["true_sat_row_index"]
    )

    df["model"] = model_name

    return df


geoquerynet_df = load_result_csv(
    GEOQUERYNET_RESULT_CSV,
    "GeoQueryNet"
)

geodtr_df = load_result_csv(
    GEODTR_RESULT_CSV,
    "GeoDTR"
)

qdfl_df = load_result_csv(
    QDFL_RESULT_CSV,
    "QDFL"
)


# ============================================================
# 5. Find valid samples
#    Condition:
#    GeoQueryNet Top-1 correct
#    GeoDTR Top-1 incorrect
#    QDFL Top-1 incorrect
# ============================================================

geoquerynet_good_rows = set(
    geoquerynet_df.loc[
        geoquerynet_df["top1_correct_computed"] == True,
        QUERY_ROW_COL
    ]
)

geodtr_bad_rows = set(
    geodtr_df.loc[
        geodtr_df["top1_correct_computed"] == False,
        QUERY_ROW_COL
    ]
)

qdfl_bad_rows = set(
    qdfl_df.loc[
        qdfl_df["top1_correct_computed"] == False,
        QUERY_ROW_COL
    ]
)

candidate_rows = sorted(
    geoquerynet_good_rows
    & geodtr_bad_rows
    & qdfl_bad_rows
)

print(f"Number of candidate samples found: {len(candidate_rows)}")

if len(candidate_rows) == 0:
    raise ValueError(
        "No sample found where GeoQueryNet is Top-1 correct "
        "and both GeoDTR and QDFL are Top-1 incorrect."
    )

random.seed(RANDOM_SEED)

selected_rows = random.sample(
    candidate_rows,
    k=min(NUM_SAMPLES_TO_PLOT, len(candidate_rows))
)

print("Selected dataset row indices:", selected_rows)

pd.DataFrame({"selected_row_index": selected_rows}).to_csv(
    os.path.join(OUTPUT_DIR, "selected_qualitative_row_indices.csv"),
    index=False
)


# ============================================================
# 6. Convert each result dataframe into dictionary
# ============================================================

def df_to_row_dict(df):
    return {
        int(row[QUERY_ROW_COL]): row
        for _, row in df.iterrows()
    }


geoquerynet_dict = df_to_row_dict(geoquerynet_df)
geodtr_dict = df_to_row_dict(geodtr_df)
qdfl_dict = df_to_row_dict(qdfl_df)

model_results = {
    "GeoQueryNet": geoquerynet_dict,
    "GeoDTR": geodtr_dict,
    "QDFL": qdfl_dict,
}


# ============================================================
# 7. Plot qualitative comparison
# ============================================================

def plot_qualitative_sample(query_row_index, save_path):
    model_names = ["GeoQueryNet", "GeoDTR", "QDFL"]

    column_titles = [
        "Model",
        "Ground",
        "GT Satellite",
        "Top-1",
        "Top-2",
        "Top-3",
        "Top-4",
        "Top-5",
    ]

    fig, axes = plt.subplots(
        nrows=3,
        ncols=8,
        figsize=(24, 9),
        dpi=300
    )

    query_display_id = get_display_id_from_row(dataset_df, query_row_index)

    # Remove figure title and column headers for a tighter layout
    # and cleaner academic display.

    # Since anchor and positive are paired in the same dataset row
    true_sat_row_index = query_row_index

    ground_path = get_ground_path_from_row(dataset_df, query_row_index)
    gt_sat_path = get_sat_path_from_row(dataset_df, true_sat_row_index)

    ground_img = load_image(ground_path)
    gt_sat_img = load_image(gt_sat_path)

    for row_idx, model_name in enumerate(model_names):
        result_row = model_results[model_name][query_row_index]

        top5_row_indices = result_row["top5_row_indices"]

        top5_row_indices = top5_row_indices[:5]
        while len(top5_row_indices) < 5:
            top5_row_indices.append(None)

        top1_row_index = top5_row_indices[0]
        top1_correct = top1_row_index == true_sat_row_index

        # ----------------------------------------------------
        # Column 0: Model name
        # ----------------------------------------------------
        ax = axes[row_idx, 0]
        ax.set_xticks([])
        ax.set_yticks([])

        for spine in ax.spines.values():
            spine.set_visible(False)

        if top1_correct:
            status = "Top-1 Correct"
            status_color = "green"
        else:
            status = "Top-1 Incorrect"
            status_color = "red"

        ax.text(
            0.5,
            0.58,
            model_name,
            ha="center",
            va="center",
            fontsize=15,
            fontweight="bold"
        )

        ax.text(
            0.5,
            0.38,
            status,
            ha="center",
            va="center",
            fontsize=11,
            color=status_color,
            fontweight="bold"
        )

        # ----------------------------------------------------
        # Column 1: Ground image
        # ----------------------------------------------------
        show_image(
            axes[row_idx, 1],
            ground_img,
            title=None,
            border_color=None
        )

        # ----------------------------------------------------
        # Column 2: Ground-truth satellite image
        # ----------------------------------------------------
        show_image(
            axes[row_idx, 2],
            gt_sat_img,
            title=None,
            border_color="green"
        )

        # ----------------------------------------------------
        # Columns 3-7: Top-5 retrieved satellite images
        # ----------------------------------------------------
        for k in range(5):
            retrieved_row_index = top5_row_indices[k]
            ax = axes[row_idx, k + 3]

            if retrieved_row_index is None:
                blank = Image.new("RGB", (224, 224), color=(240, 240, 240))
                show_image(ax, blank, title="Missing", border_color=None)
                continue

            retrieved_sat_path = get_sat_path_from_row(
                dataset_df,
                retrieved_row_index
            )

            retrieved_img = load_image(retrieved_sat_path)

            retrieved_display_id = get_display_id_from_row(
                dataset_df,
                retrieved_row_index
            )

            if retrieved_row_index == true_sat_row_index:
                border_color = "green"
                title = "Correct"
            else:
                border_color = "red"
                title = None

            show_image(
                ax,
                retrieved_img,
                title=title,
                border_color=border_color
            )

    plt.tight_layout()
    fig.subplots_adjust(wspace=0.02, hspace=0.02)
    plt.savefig(save_path, bbox_inches="tight", dpi=300)
    plt.close()

    print(f"Saved figure: {save_path}")


# ============================================================
# 8. Generate figures
# ============================================================

for query_row_index in selected_rows:
    save_path = os.path.join(
        OUTPUT_DIR,
        f"qualitative_comparison_row_{query_row_index}.png"
    )

    plot_qualitative_sample(
        query_row_index=query_row_index,
        save_path=save_path
    )