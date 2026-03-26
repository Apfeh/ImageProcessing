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

    tile_id = int(id_str)

    tiles[tile_id] = img
    edges[tile_id] = get_edges(img)
    labels[tile_id] = label

tile_w, tile_h = next(iter(tiles.values())).size

# -----------------------------
# Matching function
# -----------------------------
def find_best(target_top=None, target_left=None, candidates=None, used=None):
    best = None
    best_score = float('inf')

    for i in candidates:
        if i in used:
            continue

        score = 0

        if target_top is not None:
            score += edge_diff(target_top, edges[i][0])

        if target_left is not None:
            score += edge_diff(target_left, edges[i][2])

        if score < best_score:
            best_score = score
            best = i

    return best

# -----------------------------
# Prepare grid
# -----------------------------
grid = [[None for _ in range(GRID_W)] for _ in range(GRID_H)]
used = set()

# -----------------------------
# Find top-left corner
# -----------------------------
top_left = None
for i, label in labels.items():
    if 't' in label and 'l' in label:
        top_left = i
        break

if top_left is None:
    top_left = next(iter(tiles.keys()))

grid[0][0] = top_left
used.add(top_left)

print("Top-left tile:", top_left)

# -----------------------------
# Spiral solving
# -----------------------------
top, bottom = 0, GRID_H - 1
left, right = 0, GRID_W - 1

while top <= bottom and left <= right:

    # --- TOP ROW ---
    for col in range(left, right + 1):

        if grid[top][col] is not None:
            continue

        candidates = []
        for i in tiles:
            if i in used:
                continue

            label = labels.get(i, "")

            if top == 0 and 't' not in label:
                continue
            if col == 0 and left == 0 and 'l' not in label:
                continue
            if col == GRID_W - 1 and right == GRID_W - 1 and 'r' not in label:
                continue

            candidates.append(i)

        target_left = None
        if col > left:
            target_left = edges[grid[top][col - 1]][3]

        best = find_best(target_left=target_left, candidates=candidates, used=used)

        if best is None:
            best = next(i for i in tiles if i not in used)

        grid[top][col] = best
        used.add(best)

    top += 1

    # --- RIGHT COLUMN ---
    for row in range(top, bottom + 1):

        if grid[row][right] is not None:
            continue

        candidates = []
        for i in tiles:
            if i in used:
                continue

            label = labels.get(i, "")

            if right == GRID_W - 1 and 'r' not in label:
                continue
            if row == GRID_H - 1 and bottom == GRID_H - 1 and 'b' not in label:
                continue

            candidates.append(i)

        target_top = edges[grid[row - 1][right]][1]

        best = find_best(target_top=target_top, candidates=candidates, used=used)

        if best is None:
            best = next(i for i in tiles if i not in used)

        grid[row][right] = best
        used.add(best)

    right -= 1

    # --- BOTTOM ROW ---
    for col in range(right, left - 1, -1):

        if grid[bottom][col] is not None:
            continue

        candidates = []
        for i in tiles:
            if i in used:
                continue

            label = labels.get(i, "")

            if bottom == GRID_H - 1 and 'b' not in label:
                continue
            if col == 0 and left == 0 and 'l' not in label:
                continue
            if col == GRID_W - 1 and right == GRID_W - 1 and 'r' not in label:
                continue

            candidates.append(i)

        target_left = None
        if col < right:
            target_left = edges[grid[bottom][col + 1]][2]

        best = find_best(target_left=target_left, candidates=candidates, used=used)

        if best is None:
            best = next(i for i in tiles if i not in used)

        grid[bottom][col] = best
        used.add(best)

    bottom -= 1

    # --- LEFT COLUMN ---
    for row in range(bottom, top - 1, -1):

        if grid[row][left] is not None:
            continue

        candidates = []
        for i in tiles:
            if i in used:
                continue

            label = labels.get(i, "")

            if left == 0 and 'l' not in label:
                continue
            if row == 0 and top == 0 and 't' not in label:
                continue

            candidates.append(i)

        target_top = edges[grid[row + 1][left]][0]

        best = find_best(target_top=target_top, candidates=candidates, used=used)

        if best is None:
            best = next(i for i in tiles if i not in used)

        grid[row][left] = best
        used.add(best)

    left += 1

    print(f"Layer completed. Used tiles: {len(used)}")

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
