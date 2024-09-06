from PIL import Image, ImageOps
import numpy as np
from tqdm import tqdm

def get_concat_h(im1, im2):
	dst = Image.new('RGBA', (im1.width + im2.width, im1.height))
	dst.paste(im1, (0, 0))
	dst.paste(im2, (im1.width, 0))
	return dst

#offset va da 0 a 1. un valore utile potrebbe essere 0.5 quando il centro dell'immagine non mostra un tile ma il punto esatto di fine di un tile e inizio di un altro. Con 0.5 ci spostiamo a destra di mezzo tile così da poter selezionare il tile per ineto e non un mezzo tile
def getTile(scr, n_tiles, offset = 0, tollerance = 10, debug = False):
	img = Image.open(scr)
	img = img.convert('RGBA')
	m1 = np.array(img)
	best = [-1,-1,-1]

	#se nell'immagine il pattern si ripete 6 volte potrebbe essere già sufficiente a trovare la singola piastrella
	math_size_tile = int(img.size[0] / n_tiles)
	offset = int(math_size_tile * offset)

	#se la singola piastrella è grande 100 e inseriamo una tolleranza di 10, cercheremo la miglior dimensione provando tile che vanno da 90 a 110
	if debug:
		for_tile = tqdm(range(math_size_tile - tollerance, math_size_tile + tollerance))
	else:
		for_tile = range(math_size_tile - tollerance, math_size_tile + tollerance)
	for tile_size in for_tile:
		#estraggo il tile centrale
		tile = img.crop((int((img.size[0] / 2)) - offset, 0, int((img.size[0] / 2) + tile_size - offset), img.size[1]))

		#provo a ricreare l'immagine originale concatenando il tile appena trovato
		tiles = get_concat_h(tile, tile)
		while tiles.size[0] < img.size[0] + offset:
			tiles = get_concat_h(tiles, tile)

		#i tiles non essendo multipli perfetti creeranno un immagine più grande dell'originale, così di seguito la taglio
		tiles = tiles.crop((offset, 0, img.size[0] + offset, img.size[1]))
		#tile.save("tile" + str(tile_size) + ".png")
		#tiles.save("tiles" + str(tile_size) + ".png")

		#faccio due tentativi, uno con il tile normale e uno con il tile specchiato
		for flip in range(2):
			if flip == 1:
				tiles = ImageOps.flip(tiles)
				tiles = ImageOps.mirror(tiles)

			#paragono l'immagine originale e quella generata per vedere quando sono simili
			m2 = np.array(tiles)

			score = np.mean(m1 == m2)

			#print(tile_size, score)
			#salvo il tile con la somiglianza più alta
			if score > best[1]:
				best[2] = tile_size
				best[1] = score
				best[0] = tile

		#tile.save("tile" + str(tile_size) + ".png")
		#tiles.save("tiles" + str(tile_size) + ".png")

	if debug:
		print("Finish! Size:", best[2], "px")
	return best[0]