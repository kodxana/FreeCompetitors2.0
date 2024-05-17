from __future__ import annotations

from pathlib import Path
from typing import *  # type: ignore

import rio

from . import pages
from . import components as comps

# Define a theme for Rio to use.
# You can modify the colors here to adapt the appearance of your app or website.
# The most important parameters are listed, but more are available! You can find
# them all in the docs
#
# https://rio.dev/docs/api/theme
theme = rio.Theme.from_colors(
    primary_color=rio.Color.from_hex("#01dffd"),
    secondary_color=rio.Color.from_hex("#0083ff"),
    background_color=rio.Color.from_hex("#121212"),
    neutral_color=rio.Color.from_hex("#1e1e1e"),
    hud_color=rio.Color.from_hex("#252525"),
    disabled_color=rio.Color.from_hex("#3a3a3a"),
    success_color=rio.Color.from_hex("#00c853"),
    warning_color=rio.Color.from_hex("#ff9800"),
    danger_color=rio.Color.from_hex("#f44336"),
    corner_radius_small=0.5,
    corner_radius_medium=1.0,
    corner_radius_large=2.0,
    heading_fill="auto",
    font=rio.Font.ROBOTO,
    monospace_font=rio.Font.ROBOTO_MONO,
    light=False,
)

# Create the Rio app
app = rio.App(
    name='testing',
    pages=[
        rio.Page(
            name="Home",
            page_url='',
            build=pages.MainPage,
        ),
    ],
    theme=theme,
    assets_dir=Path(__file__).parent / "assets",
)

if __name__ == "__main__":
    app.run()
