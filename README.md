# Tileable Normal Map Generator

This project provides a tool for creating tileable normal maps from black and white images. The code processes the image to generate a normal map, which is then converted to SVG format, ensuring high quality and scalability even when resized. Ideal for applications that require detailed, high-resolution textures and scalable assets.

## Quick Start

```
git clone https://github.com/iacoposk8/Tileable-Normal-Map-Generator
cd Tileable-Normal-Map-Generator
pip install blend-modes
python NormalGenerator.py
```

## Settings

Inside NormalGenerator.py there are 3 examples of how to use N.img2normal that you can modify.

N.img2normal("input/grid.png", normal_strength = 5, blur = 150, size = 4096, invert = False, tiles = {"from": 1, "to": 4, "2d": True})
N.img2normal("input/single.jpg", normal_strength = 17, blur = 150, invert = False, tiles = {"from": 1, "to": 4, "padding": 150})
N.img2normal("input/linear.jpg", normal_strength = 17, blur = 150, invert = False, tiles = {"from": 8, "to": 20, "offset": 0.5})
