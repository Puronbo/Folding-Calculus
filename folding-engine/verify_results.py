"""Verify experiment output files are valid."""
import numpy as np
from PIL import Image
import json, os

results_dir = r'C:\Users\Me\Projects\Folding-Calculus\folding-engine\experiment_results'

for fname in sorted(os.listdir(results_dir)):
    fpath = os.path.join(results_dir, fname)
    if fname.endswith('.png'):
        try:
            img = Image.open(fpath)
            arr = np.array(img)
            print(f'PNG  {fname}: {img.size} valid (pixels {arr.min()}-{arr.max()})')
        except Exception as e:
            print(f'PNG  {fname}: ERROR {e}')
    elif fname.endswith('.json'):
        try:
            with open(fpath) as f:
                data = json.load(f)
            keys = list(data.keys())
            sizes = {k: len(v) if isinstance(v, (list, np.ndarray)) else type(v).__name__
                     for k, v in data.items()}
            print(f'JSON {fname}: keys={keys} sizes={sizes}')
        except Exception as e:
            print(f'JSON {fname}: ERROR {e}')
