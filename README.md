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

Il primo parametro è l'immagine che vogliamo convertire in normal map

Facoltativo ma consigliato
normal_strength è la profondità con cui il tracciato verrà inciso nella normal map
blur è la larghezza e di conseguenza la morbidezza con cui il tracciato verrà applicato alla normal map. 

Facoltativo
size è la grandezza (base e altezza) dell'immagine prodotta
invert può essere impostato a True quando abbiamo uno sfondo nero con un tracciato bianco

tiles = {"from": 1, "to": 4, "2d": True})
tiles = {"from": 1, "to": 4, "padding": 150})
tiles = {"from": 8, "to": 20, "offset": 0.5})
