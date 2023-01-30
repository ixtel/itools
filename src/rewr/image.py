from PIL import Image
import math


def resize_ratio(path, path_new, width=100, height=100):
	"""
	:param path:
	:param path_new:
	:param width:
	:param height:
	:return:
	"""
	im = Image.open(path)
	im.thumbnail((width, height))
	
	old_width, old_height = im.size
	
	ext = path_new.split('.')[-1].lower()
	
	# Center the image
	x1 = int(math.floor((width - old_width) / 2))
	y1 = int(math.floor((height - old_height) / 2))
	
	mode = im.mode
	if len(mode) == 1:  # L, 1
		new_background = (255, )
	elif len(mode) == 3:  # RGB
		new_background = (255, 255, 255)
	elif len(mode) == 4:  # RGBA, CMYK
		new_background = (255, 255, 255, 255)
	else:
		new_background = (255, 255, 255)
	
	if ext == 'png':
		new_image = Image.new(mode, (width, height))
	else:
		new_image = Image.new(mode, (width, height), new_background)
	
	new_image.paste(im, (x1, y1, x1 + old_width, y1 + old_height))
	new_image.save(path_new)
