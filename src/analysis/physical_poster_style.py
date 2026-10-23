"""Physical-poster legend dimensions, independent of raster DPI or placement size.

Use the final image placement in inches, not its intrinsic Matplotlib size.
All region strips and scalar color bars share one printed thickness. These
helpers only size graphics; they never normalize or alter scientific values.
"""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class PrintedLegendStyle:
    """One thickness in the final printed poster, defaulting to 10 printed points."""

    thickness_inches: float = 10.0 / 72.0

    def __post_init__(self):
        self._positive(self.thickness_inches, "thickness_inches")

    @staticmethod
    def _positive(value, name):
        if not math.isfinite(value) or value <= 0:
            raise ValueError(f"{name} must be finite and positive")
        return float(value)

    def figure_fraction(self, placed_extent_inches):
        """Fraction of figure width for a vertical bar, height for a top strip."""
        extent = self._positive(placed_extent_inches, "placed_extent_inches")
        if self.thickness_inches >= extent:
            raise ValueError("Legend thickness must be smaller than image placement")
        return self.thickness_inches / extent

    def source_pixels(self, source_extent_pixels, placed_extent_inches):
        """Floating source-pixel thickness; keep precision until rasterization."""
        pixels = self._positive(source_extent_pixels, "source_extent_pixels")
        return pixels * self.figure_fraction(placed_extent_inches)

    def matplotlib_points(self, figure_extent_inches, placed_extent_inches):
        """Line/patch thickness in source-figure points for a scaled placement."""
        extent = self._positive(figure_extent_inches, "figure_extent_inches")
        return 72.0 * extent * self.figure_fraction(placed_extent_inches)

    def vertical_axes(self, left, bottom, height, *, placed_width_inches):
        """Matplotlib ``fig.add_axes`` rectangle for any vertical legend strip."""
        return [left, bottom, self.figure_fraction(placed_width_inches), height]

    def horizontal_axes(self, left, bottom, width, *, placed_height_inches):
        """Matplotlib ``fig.add_axes`` rectangle for a horizontal region strip."""
        return [left, bottom, width, self.figure_fraction(placed_height_inches)]


PHYSICAL_POSTER_LEGENDS = PrintedLegendStyle()


@dataclass(frozen=True)
class PrintedTypographyStyle:
    """Typography in final printed units; independent of source plot scaling."""
    caption_css_pixels: float = 26.0
    axis_title_points: float = 15.0
    tick_points: float = 13.5
    method_css_pixels: float = 18.0
    filename_css_pixels: float = 22.0
    family: str = "RPI Geist"

    def source_points(self, printed_points, source_extent_inches, placed_extent_inches):
        """Convert a final printed point size to Matplotlib source points."""
        for v in (printed_points, source_extent_inches, placed_extent_inches):
            if not math.isfinite(v) or v <= 0:
                raise ValueError("Font sizes and extents must be positive and finite")
        return printed_points * source_extent_inches / placed_extent_inches

    @staticmethod
    def printed_points(source_points, source_extent_inches, placed_extent_inches):
        return source_points * placed_extent_inches / source_extent_inches

    @staticmethod
    def native_points(css_pixels):
        return css_pixels * 72.0 / 96.0
