import os
from PIL import Image
import numpy as np

GRID_W, GRID_H = 40, 30

# -----------------------------
# Load images + labels
# -----------------------------
tiles = {}
edges = {}
labels = {}
label_flags = {}

def get_edges(img):
    arr = np.array(img)
    top = arr[0, :, :]
    bottom = arr[-1, :, :]
    left = arr[:, 0, :]
    right = arr[:, -1, :]
    return top, bottom, left, right

def edge_diff(e1, e2):
    return np.sum(np.abs(e1.astype(int) - e2.astype(int)))

print("Loading images...")

for filename in os.listdir("tiles"):
    if not filename.endswith(".png"):
        continue

    path = os.path.join("tiles", filename)
    img = Image.open(path).convert("RGB")

    base = filename.replace(".png", "")
    if "-" in base:
        id_str, label = base.split("-", 1)
    else:
        id_str = base
        label = ""
    label = label.strip()

    tile_id = int(id_str)

    tiles[tile_id] = img
    edges[tile_id] = get_edges(img)
    labels[tile_id] = label
    label_flags[tile_id] = frozenset(ch for ch in label if ch in {"t", "b", "l", "r"})

tile_w, tile_h = next(iter(tiles.values())).size

# -----------------------------
# Matching function
# -----------------------------
OPPOSITE_EDGE_INDEX = {
    "top": 0,
    "bottom": 1,
    "left": 2,
    "right": 3,
}


def find_best(target_edges=None, candidates=None, used=None):
    """
    Pick the candidate tile whose relevant edges best match already-placed neighbors.
    `target_edges` maps a candidate edge name ("top"/"bottom"/"left"/"right")
    to a numpy array that this edge should match.
    """
    target_edges = target_edges or {}
    best = None
    best_score = float('inf')

    for i in candidates:
        if i in used:
            continue

        score = 0

        for edge_name, target in target_edges.items():
            edge_idx = OPPOSITE_EDGE_INDEX[edge_name]
            score += edge_diff(target, edges[i][edge_idx])

    ranked.sort(key=lambda item: item[0])
    return ranked



def get_target_edges(row, col):
    """
    Build edge constraints for a tile at (row, col) using already-placed neighbors.
    """
    target_edges = {}

    if row > 0 and grid[row - 1][col] is not None:
        target_edges["top"] = edges[grid[row - 1][col]][1]

    if row < GRID_H - 1 and grid[row + 1][col] is not None:
        target_edges["bottom"] = edges[grid[row + 1][col]][0]

    if col > 0 and grid[row][col - 1] is not None:
        target_edges["left"] = edges[grid[row][col - 1]][3]

    if col < GRID_W - 1 and grid[row][col + 1] is not None:
        target_edges["right"] = edges[grid[row][col + 1]][2]

    return target_edges

def get_target_edges(row, col):
    """
    Build edge constraints for a tile at (row, col) using already-placed neighbors.
    """
    target_edges = {}

    if row > 0 and grid[row - 1][col] is not None:
        target_edges["top"] = edges[grid[row - 1][col]][1]

    if row < GRID_H - 1 and grid[row + 1][col] is not None:
        target_edges["bottom"] = edges[grid[row + 1][col]][0]

    if col > 0 and grid[row][col - 1] is not None:
        target_edges["left"] = edges[grid[row][col - 1]][3]

    if col < GRID_W - 1 and grid[row][col + 1] is not None:
        target_edges["right"] = edges[grid[row][col + 1]][2]

    return target_edges


def tile_matches_position(tile_id, row, col):
    """
    Enforce that border/corner labels are only used in valid positions.
    """
    flags = label_flags.get(tile_id, frozenset())

    on_top = row == 0
    on_bottom = row == GRID_H - 1
    on_left = col == 0
    on_right = col == GRID_W - 1

    if ("t" in flags) != on_top:
        return False
    if ("b" in flags) != on_bottom:
        return False
    if ("l" in flags) != on_left:
        return False
    if ("r" in flags) != on_right:
        return False

    return True


        target_edges = get_target_edges(top, col)
        best = find_best(target_edges=target_edges, candidates=candidates, used=used)

        if best is None:
            best = next(i for i in tiles if i not in used)

        grid[top][col] = best
        used.add(best)

def get_target_edges(row, col):
    """
    Build edge constraints for a tile at (row, col) using already-placed neighbors.
    """
    target_edges = {}

    if row > 0 and grid[row - 1][col] is not None:
        target_edges["top"] = edges[grid[row - 1][col]][1]

    if row < GRID_H - 1 and grid[row + 1][col] is not None:
        target_edges["bottom"] = edges[grid[row + 1][col]][0]

    if col > 0 and grid[row][col - 1] is not None:
        target_edges["left"] = edges[grid[row][col - 1]][3]

    if col < GRID_W - 1 and grid[row][col + 1] is not None:
        target_edges["right"] = edges[grid[row][col + 1]][2]

    return target_edges


        target_edges = get_target_edges(row, right)
        best = find_best(target_edges=target_edges, candidates=candidates, used=used)

    if ("t" in flags) != on_top:
        return False
    if ("b" in flags) != on_bottom:
        return False
    if ("l" in flags) != on_left:
        return False
    if ("r" in flags) != on_right:
        return False

    return True


def find_exact_label(required_flags):
    for tile_id, flags in label_flags.items():
        if flags == required_flags:
            return tile_id
    return None

# -----------------------------
# Prepare grid
# -----------------------------
grid = [[None for _ in range(GRID_W)] for _ in range(GRID_H)]
used = set()

# -----------------------------
# Fix corners first
# -----------------------------
corner_targets = [
    ((0, 0), frozenset({"t", "l"}), "top-left"),
    ((0, GRID_W - 1), frozenset({"t", "r"}), "top-right"),
    ((GRID_H - 1, 0), frozenset({"b", "l"}), "bottom-left"),
    ((GRID_H - 1, GRID_W - 1), frozenset({"b", "r"}), "bottom-right"),
]

for (row, col), flags, corner_name in corner_targets:
    corner_tile = find_exact_label(flags)
    if corner_tile is None:
        raise ValueError(f"Missing required {corner_name} corner tile with label {''.join(sorted(flags))}")
    grid[row][col] = corner_tile
    used.add(corner_tile)
    print(f"{corner_name} tile fixed:", corner_tile)

# -----------------------------
# Wavefront solving from all corners toward center
# -----------------------------
total_cells = GRID_W * GRID_H
while len(used) < total_cells:
    frontier = []

    for row in range(GRID_H):
        for col in range(GRID_W):
            if grid[row][col] is not None:
                continue

            candidates.append(i)

        target_edges = get_target_edges(bottom, col)
        best = find_best(target_edges=target_edges, candidates=candidates, used=used)

    best_choice = None
    for neighbor_count in sorted({item[0] for item in frontier}, reverse=True):
        constrained_cells = [item for item in frontier if item[0] == neighbor_count]

        for _, row, col, target_edges in constrained_cells:
            candidates = [
                tile_id for tile_id in tiles
                if tile_id not in used and tile_matches_position(tile_id, row, col)
            ]
            if not candidates:
                continue

            neighbor_count = len(target_edges)
            frontier.append((neighbor_count, row, col, target_edges))

    if not frontier:
        raise RuntimeError("No frontier cells available; puzzle cannot progress with current constraints.")

        target_edges = get_target_edges(row, left)
        best = find_best(target_edges=target_edges, candidates=candidates, used=used)

    if not candidates:
        raise RuntimeError(f"No candidate tiles fit position ({row}, {col}) with border/corner constraints.")

    best = find_best(target_edges=target_edges, candidates=candidates, used=used)
    if best is None:
        raise RuntimeError(f"Unable to score candidates for position ({row}, {col}).")

    grid[row][col] = best
    used.add(best)

    if len(used) % 100 == 0 or len(used) == total_cells:
        print(f"Placed tiles: {len(used)}/{total_cells}")


# -----------------------------
# DEBUG OUTPUT
# -----------------------------
print("\n--- GRID DEBUG (ROW BY ROW) ---")

for row in range(GRID_H):
    row_data = []
    for col in range(GRID_W):
        tile_id = grid[row][col]
        label = labels.get(tile_id, "")
        row_data.append(f"{tile_id}-{label}".ljust(8))
    print(f"Row {row:02d}: {' '.join(row_data)}")

# -----------------------------
# BORDER VALIDATION
# -----------------------------
print("\n--- BORDER VALIDATION ---")

for col in range(GRID_W):
    if 't' not in labels.get(grid[0][col], ''):
        print(f"Top border error at (0,{col})")

for col in range(GRID_W):
    if 'b' not in labels.get(grid[GRID_H-1][col], ''):
        print(f"Bottom border error at ({GRID_H-1},{col})")

for row in range(GRID_H):
    if 'l' not in labels.get(grid[row][0], ''):
        print(f"Left border error at ({row},0)")

for row in range(GRID_H):
    if 'r' not in labels.get(grid[row][GRID_W-1], ''):
        print(f"Right border error at ({row},{GRID_W-1})")

# -----------------------------
# SAVE DEBUG FILE
# -----------------------------
with open("grid_debug.txt", "w") as f:
    for row in range(GRID_H):
        row_data = []
        for col in range(GRID_W):
            tile_id = grid[row][col]
            label = labels.get(tile_id, "")
            row_data.append(f"{tile_id}-{label}")
        f.write(" ".join(row_data) + "\n")

print("Saved grid_debug.txt")

# -----------------------------
# BUILD FINAL IMAGE
# -----------------------------
print("Constructing final image...")

final = Image.new("RGB", (tile_w * GRID_W, tile_h * GRID_H))

for row in range(GRID_H):
    for col in range(GRID_W):
        tile_id = grid[row][col]
        final.paste(tiles[tile_id], (col * tile_w, row * tile_h))

final.save("result_spiral.png")

print("Saved as result_spiral.png")
