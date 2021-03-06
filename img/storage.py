from img import get_dhash_b14, get_dhash_b14_io, decode_dhash, hamm_img
from PIL import Image, UnidentifiedImageError
from io import BytesIO
from glob import glob
from os import path
from urllib.request import quote
from shutil import copyfileobj

def save_img(datas: bytes, image_dir: str) -> dict:
	is_converted = False
	print("Save img...")
	try:
		with Image.open(BytesIO(datas)) as img2save:
			if img2save.format != "WEBP":		#转换webp
				converted = BytesIO()
				img2save.save(converted, "WEBP")
				converted.seek(0)
				is_converted = True
	except UnidentifiedImageError:
		return {"stat": "notanimg"}
	fname = get_dhash_b14_io(converted) if is_converted else get_dhash_b14(datas)
	print("Recv file:", fname, end='')
	no_similar = True
	all_imgs_list = [name[-10:-5] for name in glob(image_dir + "*.webp")]
	this_hash = decode_dhash(fname)
	hash_len = len(this_hash)
	for img_name in all_imgs_list:
		if hamm_img(this_hash, decode_dhash(img_name), hash_len) <= 2:
			no_similar = False
			break
	if no_similar:
		print("[NEW]")
		fn = path.join(image_dir, fname + ".webp")	#生成文件存储路径
		if is_converted: converted.seek(0)
		with open(fn, 'wb') as f: copyfileobj(converted, f) if is_converted else f.write(datas)
		if is_converted: converted.close()
		return {"stat":"success", "img": fname}
	else:
		print("[OLD]")
		return {"stat":"exist", "img": img_name}