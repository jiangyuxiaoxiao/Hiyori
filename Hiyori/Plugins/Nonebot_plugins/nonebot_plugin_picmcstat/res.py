from pathlib import Path

from Hiyori.Plugins.Basic_plugins.nonebot_plugin_imageutils import BuildImage

MODULE_DIR = Path(__file__).parent
RES_DIR = MODULE_DIR / "res"

GRASS_RES_PATH = RES_DIR / "grass_side_carried.png"
DIRT_RES_PATH = RES_DIR / "dirt.png"
DEFAULT_ICON_PATH = RES_DIR / "default.png"

GRASS_RES = BuildImage.open(GRASS_RES_PATH)
DIRT_RES = BuildImage.open(DIRT_RES_PATH)
DEFAULT_ICON_RES = BuildImage.open(DEFAULT_ICON_PATH)
