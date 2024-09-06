import platform, os
from pathlib import Path

from PIL import Image
import PIL.ImageOps
import numpy
import blend_modes

import re
from lib import height2bump
from lib import seamless
from lib import tile

class Normal():
	def __init__(self):
		self.names = []

	def _get_name(self, nm = ""):
		if nm != "":
			self.names.append(str(len(self.names)) + nm)
		
		return self.names[-1]

	def _add_layer(self, background_img_raw, foreground_img_raw, mode = "normal", opacity = 1):
		#background_img_raw and foreground_img_raw must be RGBA image
		background_img_raw = background_img_raw.convert('RGBA')
		foreground_img_raw = foreground_img_raw.convert('RGBA')

		background_img = numpy.array(background_img_raw)  # Inputs to blend_modes need to be numpy arrays.
		background_img_float = background_img.astype(float)  # Inputs to blend_modes need to be floats.

		foreground_img = numpy.array(foreground_img_raw)  # Inputs to blend_modes need to be numpy arrays.
		foreground_img_float = foreground_img.astype(float)  # Inputs to blend_modes need to be floats.

		# Blend images
		if mode == "normal":
			blended_img_float = blend_modes.normal(background_img_float, foreground_img_float, opacity)
		if mode == "overlay":
			blended_img_float = blend_modes.overlay(background_img_float, foreground_img_float, opacity)

		# Convert blended image back into PIL image
		blended_img = numpy.uint8(blended_img_float)  # Image needs to be converted back to uint8 type for PIL handling.
		blended_img_raw = Image.fromarray(blended_img)  # Note that alpha channels are displayed in black by PIL by default.
														# This behavior is difficult to change (although possible).
														# If you have alpha channels in your images, then you should give
														# OpenCV a try.

		return blended_img_raw

	def _Regex(self, test_str, regex):
		ret = []
		matches = re.finditer(regex, test_str, re.MULTILINE | re.IGNORECASE | re.DOTALL)
		for matchNum, match in enumerate(matches, start=1):
			part = []
			part.append(match.group())
			for groupNum in range(0, len(match.groups())):
				groupNum = groupNum + 1
				part.append(match.group(groupNum))
			ret.append(part)
		return ret

	def _svg2image(self, size):
		if platform.system() == 'Windows':
			os.system('"C:\\Program Files\\Inkscape\\bin\\inkscape.exe" ' + self._get_name() + ' --export-area-page --export-width '+str(size)+' --export-background #ffffff -o ' + self._get_name("scaled.png"))
		else:
			os.system('flatpak run org.inkscape.Inkscape ' + self._get_name() + ' --export-area-page --export-width '+str(size)+' --export-background "#ffffff" -o ' + self._get_name("scaled.png"))

	def _make_tiles(self, input_file, output_file, tiles, tosvg = True):
		if "offset" not in tiles:
			tiles["offset"] = 0
		if tosvg:
			self._svg2image(self.size_svg)
			input_file = self._get_name()
		tile1 = tile.getTile(input_file, n_tiles = tiles["from"], offset = tiles["offset"])
		#tile1.save("TEST.png")
		tiles1 = tile.get_concat_h(tile1, tile1)
		for i in range(tiles["to"] - 2):
			tiles1 = tile.get_concat_h(tiles1, tile1)

		tiles1.save(output_file)

	def img2normal(self, image, normal_strength = 50, blur = 50, blur_cycles = 2, size = 8192, invert = False, tiles = False):
		self.names = []

		if tiles and tiles["from"] == 1:
			self.size_svg = int(size / tiles["to"])
		else:
			self.size_svg = size
		
		'''
		the first and last tile must join perfectly.
		Then I take out the central tile and repeat it.
		To extract a central tile I need at least 3 tiles
		'''
		if tiles and tiles["from"] > 1 and tiles["to"] < 3:
			tiles["to"] = 3

		#Convert image to vector with the potrace library to enlarge it without loss of quality
		print("Convert image to vector")
		#Image conversion to BMP because it is required as input format by potrace
		img = Image.open(image)
		width, height = img.size
		white = Image.new("RGBA", (width, height), (255, 255, 255, 255))

		img = img.convert('RGBA')
		img = self._add_layer(white, img, mode = "normal", opacity = 1)
		img = img.convert('RGB')
		img.save(self._get_name("bpm.bmp"))

		#Creation of the SVG file in 8k
		if platform.system() == 'Windows':
			os.system('"lib\\potrace\\Windows\\potrace.exe" --svg -W 6144pt ' + self._get_name() + ' -o ' + self._get_name("svg.svg"))
		else:
			os.system('"lib/potrace/Linux/potrace" --svg -W 6144pt ' + self._get_name() + ' -o ' + self._get_name("svg.svg"))

		if tiles and "skip" not in tiles and tiles["from"] > 1:
			#With the 8k file I can extract a single with more precision
			print("Changing the number of tiles from", tiles["from"], "to", tiles["to"])
			tilefile = "lib/cache/" + Path(image).stem + ".png"
			self._make_tiles(self._get_name(), tilefile, tiles)
			
			#If the file is reduced in size I have to regenerate an 8k image
			tiles["skip"] = True
			self.img2normal(tilefile, normal_strength, blur, blur_cycles, size, invert, tiles)
			return False

		print("Adding blur to SVG file")

		f = open("lib/base.svg", "r")
		base = f.read()
		f.close()

		f = open(self._get_name(), "r")
		path = f.read()
		f.close()

		pathsvg = '<path d="[PATH_D]" style="filter:url(#filterblur[N_LAYER])" />'

		#1px = 0.75pt
		transform = self._Regex(path, r'<g transform="translate\((.*?),(.*?)\) scale\((.*?),(.*?)\)"')
		doc_height = str(float(transform[0][2]) + ((blur * 2 * blur_cycles) * 0.75))
		tra_height = str(float(transform[0][2]) + ((blur * 2 * blur_cycles) * 0.75))

		if "2d" not in tiles:
			doc_height = str(float(transform[0][2]) + ((blur * 2 * blur_cycles) * 0.75) + ((blur * 2 * blur_cycles) * 0.75))

		layer = '''<g transform="translate(''' + transform[0][1] + ''','''+tra_height+''') scale(''' + transform[0][3] + ''',''' + transform[0][4] + ''')"
			inkscape:label="Livello [N_LAYER]"
			inkscape:groupmode="layer"
			id="layer[N_LAYER]"
			style="display:inline;filter:url(#filteroverlay)"
			sodipodi:insensitive="true">
			[PATHS]
		</g>'''

		gaussian = '''<filter
			inkscape:collect="always"
			style="color-interpolation-filters:sRGB"
			id="filterblur[N_LAYER]">
		<feGaussianBlur
			inkscape:collect="always"
			stdDeviation="[DEVIATION]"
			id="feGaussianBlur4535" />
		</filter>'''

		base = base.replace("[DOC_HEIGHT]", doc_height)

		paths = ""
		for p in self._Regex(path, r'<path d="(.*?)"'): 
			paths += pathsvg.replace("[PATH_D]", p[1]) + "\n"
		layer = layer.replace('[PATHS]', paths)

		layers = ""
		gaussians = ""
		for i in range(blur_cycles,-1,-1):
			layers += layer.replace("[N_LAYER]", str(i)) + "\n"
			gaussians += gaussian.replace("[N_LAYER]", str(i)).replace("[DEVIATION]", str(i * blur)) + "\n"

		base = base.replace("[LAYERS]", layers)
		base = base.replace("[GAUSSIANS]", gaussians)

		f = open(self._get_name("blur.svg"), "w")
		f.write(base)
		f.close()

		#os.environ['path'] += r';C:\\Program Files\\UniConvertor-2.0rc5\\dlls'

		print("Convert SVG to PNG. This can take a long time if the size and/or blur are very large.")
		self._svg2image(self.size_svg + 100)

		#pixels = img.load() # create the pixel map

		'''image = Image.open('4scaled.png')
			inverted_image = PIL.ImageOps.invert(image)
			inverted_image.save('4inverted.png')'''

		img = Image.open(self._get_name())
		if invert:
			print("Color inversion (result: from concave to convex or vice versa)")
			bgcolor = (0, 0, 0, 255)

			if img.mode == 'RGBA':
				r,g,b,a = img.split()
				rgb_image = Image.merge('RGB', (r,g,b))

				inverted_image = PIL.ImageOps.invert(rgb_image)

				r2,g2,b2 = inverted_image.split()

				final_transparent_image = Image.merge('RGBA', (r2,g2,b2,a))

				final_transparent_image.save(self._get_name("inverted.png"))
			else:
				img = PIL.ImageOps.invert(img)
				img.save(self._get_name("inverted.png"))
		else:
			bgcolor = (255, 255, 255, 255)
			img.save(self._get_name("inverted.png"))

		'''if scale_width != 0:
			print("Resize image")
			width_out, height_out = img.size
			scale_height = int((height_out / width_out) * scale_width)

			nrmbg = Image.new("RGBA", (width_out, height_out), bgcolor)
			img = img.resize((scale_width, scale_height), Image.Resampling.LANCZOS)
			nrmbg.paste(img, (int((width_out - scale_width)/2),int((height_out - scale_height)/2)))
			nrmbg.save(self._get_name("resized.png"))'''

		'''
		print("Remove background of border blur")
		img = Image.open("5inverted.png")
		blur_size = int(blur * 2 * blur_cycles)
		for x in range(img.size[0]): # for every pixel:
			for y in range(img.size[1]):
				if y <= blur_size or y >=  img.size[1] - blur_size:
					img.putpixel((x, y), bgcolor)
		img.save("6noborder.png")'''

		'''print("Add 2px border")
		img = Image.open(self._get_name())
		width, height = img.size
		nrmbg = Image.new("RGBA", (width + 4, height + 4), (255, 255, 255, 255))
		nrmbg.paste(img, (2, 2))
		nrmbg.save(self._get_name("bordered.png"))'''

		print("Normal map generation")
		result = height2bump.readHeight2Bump(self._get_name(), self._get_name('normal.png'), normal_strength) #options="tqa" 

		if tiles and tiles["from"] > 1:
			#Extracting a new single tile from the normal map. 
			#This is because the readHeight2Bump function generates a 2px border around the image which would be replicated in the pattern
			
			if "offset" not in tiles:
				tiles["offset"] = 0

			self._make_tiles(self._get_name(), self._get_name("normal_tiled.png"), {"from": tiles["to"], "to": tiles["to"], "offset": tiles["offset"]}, tosvg = False)

		print("Crop border and convert to square")
		img = Image.open(self._get_name())
		width, height = img.size
		
		if tiles and tiles["from"] > 1:
			img = img.crop((0, 4, width, height-4))
		else:
			img = img.crop((2, 4, width-2, height-4))
		width, height = img.size
		
		if width < size:
			container_size = size
		else:
			container_size = width

		if tiles and tiles["from"] == 1:
			if "padding" not in tiles:
				padding = 0
			else:
				padding = tiles["padding"]

			scale_width = self.size_svg - (padding * 2)
			scale_height = int((height / width) * scale_width)

			img = img.resize((scale_width, scale_height), Image.Resampling.LANCZOS)

			nrmbg = Image.new("RGBA", (size, size), (128, 128, 255, 255))
			
			if "2d" in tiles and tiles["2d"]:
				for i in range(tiles["to"]):
					for j in range(tiles["to"]):
						nrmbg.paste(img, (self.size_svg * j + padding, i * scale_height))
			else:
				for i in range(tiles["to"]):
					nrmbg.paste(img, (self.size_svg * i + padding, int((size - scale_height)/2)))
				
			nrmbg.save(self._get_name("normal_tiled.png"))
		else:
			nrmbg = Image.new("RGBA", (container_size, container_size), (128, 128, 255, 255))
			nrmbg.paste(img, (int((container_size - width)/2),int((container_size - height)/2)))
			nrmbg = nrmbg.resize((size, size), Image.Resampling.LANCZOS)
			nrmbg.save(self._get_name("normal_crop.png"))

		'''if tileable:
			print("Make the image seamless/tileable, scale:",int(0.005 * size))
			result = seamless.image_seamless(self._get_name(), "Normal_" + Path(image).stem + ".png", int(0.005 * size))
			#https://www.pycheung.com/checker/
			print(os.path.splitext(image)[0])
		else:'''
		img = Image.open(self._get_name())
		img.save("Normal_" + Path(image).stem + ".png")
    
		for nm in self.names:
			os.remove(nm)

		import glob
		for file in glob.glob("*scaled.png"):
			os.remove(file)

N = Normal()

N.img2normal("input/grid.png", normal_strength = 45, blur = 50, size = 4096, invert = False, tiles = {"from": 1, "to": 4, "2d": True})
N.img2normal("input/single.jpg", normal_strength = 17, blur = 150, invert = False, tiles = {"from": 1, "to": 4, "padding": 150})
N.img2normal("input/linear.jpg", normal_strength = 17, blur = 150, invert = False, tiles = {"from": 8, "to": 7, "offset": 0.5})
