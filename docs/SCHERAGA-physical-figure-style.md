# Physical-poster figure style

Every legend strip on the physical poster has a **10-point printed thickness** (10/72 inch), matching the previous chainbow strip. This applies to the distance-variance chainbow strip and R1/R2 region markers, the distance-variance color bar, the TM-score color bar and the t-SNE confidence color bar. Horizontal region markers use the same thickness as vertical color bars. Categorical method-comparison plots use discrete swatches instead of an additional scalar color bar.

Use `PrintedLegendStyle` from `src.analysis.physical_poster_style` with the image's **final placement size in inches**. The current 36 × 48-inch poster uses 96 authoring pixels per inch. Conversion to source pixels is:

```python
from src.analysis.physical_poster_style import PHYSICAL_POSTER_LEGENDS as legends
source_strip_px = legends.source_pixels(
    source_extent_pixels=2400,
    placed_extent_inches=6,
)
```

For vertical strips the extent is image width; for horizontal strips it is image height. `figure_fraction`, `vertical_axes` and `horizontal_axes` size Matplotlib axes; `matplotlib_points` sizes a source-figure line at its eventual printed scale. Keep floating precision until rasterization. Each layout needs its own conversion when its image placement changes; equal source-pixel widths alone do not guarantee equal printed widths.

Matplotlib color bars can retain `box_aspect=20`, which changes their height when their width is adjusted. After drawing and freezing the figure layout, call `colorbar.ax.set_box_aspect(None)` and `colorbar.ax.set_aspect('auto')` before applying the final `vertical_axes` rectangle. Preserve the original bar height on a fixed canvas and verify the exported dimensions.

Export on a fixed canvas, or use the actual cropped output dimensions when `bbox_inches="tight"` is necessary. Verify the result using `source strip pixels × placed image inches ÷ source image pixels × 72`; it should equal 10 points within one source-pixel rounding error. Recalculate after resizing figures.

This convention changes display dimensions only. Scientific coordinates, model inclusion, normalization bounds and numerical values are independent settings. The current refold-pTM t-SNE color bars span each target's full observed range; TM similarity matrices span 0–1.
