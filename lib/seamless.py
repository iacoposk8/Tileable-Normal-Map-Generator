#Funky seamless texture generator
#By Tim Sheerman-Chase (c) 2018
#Released under CC0 license
#https://gist.github.com/TimSC/52190fca6b1fb223e952ebf3118bde97

from __future__ import print_function
from PIL import Image

def image_seamless(input_path, output_path, margin):
	img = Image.open(input_path)
	img2 = img.convert("RGBA")
	pix2 = img2.load()

	blendMargin = margin

	#Do horizontal repeat
	imgc = img2.crop((0, 0, img.width-blendMargin, img.height))
	imgcpix = imgc.load()
	right = Image.new("RGBA", imgc.size)
	rightpix = right.load()

	for x in range(blendMargin):
		for y in range(right.height):
			pv = pix2[x+img2.width-blendMargin, y]
			alphaNorm = max(1.0-float(x)/blendMargin, 0)
			rightpix[x, y] = (pv[0], pv[1], pv[2], int(round(255.0 * alphaNorm)))
	
	imgc = Image.alpha_composite(imgc, right)

	#Do vertical repeat
	srcImg = imgc
	srcImgPix = srcImg.load()
	imgc2 = imgc.crop((0, 0, imgc.width, imgc.height-blendMargin))
	imgc2pix = imgc2.load()

	bottom = Image.new("RGBA", imgc2.size)
	bottompix = bottom.load()

	for x in range(srcImg.width):
		for y in range(blendMargin):
			pv = srcImgPix[x, y+srcImg.height-blendMargin]
			alphaNorm = max(1.0-float(y)/blendMargin, 0)
			bottompix[x, y] = (pv[0], pv[1], pv[2], int(round(255.0 * alphaNorm)))
	
	imgc3 = Image.alpha_composite(imgc2, bottom)
	imgc3.convert("RGB").save(output_path)