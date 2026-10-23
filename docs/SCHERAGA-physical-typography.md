# Physical poster typography

Use `PrintedTypographyStyle` with `PrintedLegendStyle` when exporting physical posters. Values describe the final printed poster, rather than unscaled source images.

| Role | Final size | Weight |
|---|---:|---|
| A1–A5 and B1–B5 captions, including brief titles | 26 CSS px = 19.5 pt | Brief title bold; body normal |
| Named methods in A5 caption | Same 26 CSS px | Bold; connecting prose normal |
| Axis and colorbar titles | 15 pt | Normal |
| Axis and colorbar tick labels | 13.5 pt | Normal |
| Method names above stacked bars | 18 CSS px = 13.5 pt | Bold |
| All four AIS model filenames | 22 CSS px = 16.5 pt | Normal |
| Raised citations | 2/3 nominal caption size, +0.42-em rise | Inherit regular weight |
| Colorbars, chainbow strip, region markers | 10 pt thickness | Unchanged |

Use the supplied RPI Geist Regular/Bold font files. Convert a desired printed font size with `source_points = printed_points × source_figure_width_inches / placed_width_inches`. Native slide objects use CSS px at 96 DPI, with 1 CSS px = 0.75 pt. Keep a fixed plot canvas (no tight cropping); if cropped, recompute using the actual saved extent. Check measured ink bounds after rendering. Axis labels remain normal weight. No normalization, data, or scientific settings belong in this typography helper.

The machine-readable convention is [SCHERAGA-physical-typography.json](SCHERAGA-physical-typography.json); the reusable helper is [physical_poster_style.py](../src/analysis/physical_poster_style.py). Apply this convention in future physical exports, including whenever figure placement changes. For example, a 6.9-inch-wide source figure placed at 550/96 inches needs a 15-point printed axis title rendered at approximately 18.07 source points.

```python
from src.analysis.physical_poster_style import PrintedTypographyStyle

type_style = PrintedTypographyStyle()
source_font_pt = type_style.source_points(
    type_style.axis_title_points, 6.9, 550 / 96,
)
# Native slide caption: type_style.native_points(26) == 19.5 points.
```
