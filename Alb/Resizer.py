from . import AlbException

import asyncio
import logging
import yaml

class ResizerConfigError(AlbException):
    pass

class Resizer:
    def __init__(self, x: int = None, y: int = None, quality: float = 0.7):
        if x is None:
            x = 1024

        if y is None:
            y = x

        if x < 64 or x > 8192:
            raise ResizerConfigError(f"Invalid value for x, must be between 64 and 8192: {x}")

        if y < 64 or y > 8192:
            raise ResizerConfigError(f"Invalid value for y, must be between 64 and 8192: {y}")

        if quality < 0 or quality > 1:
            raise ResizerConfigError(f"Invalid value for quality, must be between 0 and 1: {quality}")

        self.scale = f"{int(x)}x{int(y)}"
        self.quality = float(quality)

    async def process(self, source, destination):
        # ImageMagick -quality takes 0-100; self.quality is stored as 0.0-1.0
        quality_pct = str(int(self.quality * 100))
        p = await asyncio.create_subprocess_exec("convert", "-scale", self.scale, "-quality", quality_pct, source, destination)
        await p.wait()

#  convert -scale 1024x1024 -quality 70% \$< \$@
