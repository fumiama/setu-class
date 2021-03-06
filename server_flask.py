#!/usr/bin/env python3
from base14.base14 import init_dll_in
from gevent import pywsgi
from flask import Flask, request
from urllib.request import unquote, quote
import sys, os
from base14 import init_dll_in
from classify import init_model, predict_url
# from classify import predict_data
from config import TRAINED_MODEL_NOR, TRAINED_MODEL_ERO
from io import BytesIO
from img import get_dhash_b14, save_img

app = Flask(__name__)
# MAXBUFFSZ = 16*1024*1024
img_dir = ""
invalid_img_dir = ""

def get_arg(key: str) -> str:
	return request.args.get(key)

@app.route("/dice", methods=['GET'])
def dice() -> dict:
	global img_dir
	loli = get_arg("loli") == "true"
	url = "" if loli else unquote(get_arg("url"))
	noimg = get_arg("noimg") == "true"
	clsnum = get_arg("class")
	newcls = clsnum == "9"
	nopredict = clsnum == "0"
	r18 = get_arg("r18") == "true"
	c, d = predict_url(url, loli, newcls, r18, nopredict)
	if len(d) > 0:
		dh = get_dhash_b14(d)
		if loli:
			r = save_img(d, img_dir)
			if r["stat"] == "exist": dh = r["img"]
		else: save_img(d, invalid_img_dir)
		if noimg: return {"img": dh, "class": c}
		else: return d, 200, {"Content-Type": "image/webp", "Class": c, "DHash": quote(dh)}

'''
@app.route("/classdat", methods=['POST'])
def upload() -> dict:
	length = int(request.headers.get('Content-Length'))
	print("准备接收:", length, "bytes")
	if length < MAXBUFFSZ:
		data = request.get_data()
		return {"img": get_dhash_b14(data), "class": predict_data(BytesIO(data))}
	else:
		data = request.stream.read(length)
		return {"img": get_dhash_b14(data), "class": predict_data(BytesIO(data))}

@app.route("/classform", methods=['POST'])
def upform() -> dict:
	re = []
	for f in request.files.getlist("img"):
		re.append({"name":f.filename, "img": get_dhash_b14(f), "class": predict_data(f)})
	return {"result": re}
'''

def flush_io() -> None:
	sys.stdout.flush()
	sys.stderr.flush()

def handle_client():
	global img_dir, invalid_img_dir
	host = sys.argv[1]
	port = int(sys.argv[2])
	img_dir = sys.argv[3]
	invalid_img_dir = sys.argv[4]
	if img_dir[-1] != '/': img_dir += "/"
	if invalid_img_dir[-1] != '/': invalid_img_dir += "/"
	print("Starting SC at:", host, port)
	init_dll_in('/usr/local/lib/')
	init_model(TRAINED_MODEL_NOR, TRAINED_MODEL_ERO)
	pywsgi.WSGIServer((host, port), app).serve_forever()

if __name__ == '__main__':
	if len(sys.argv) == 5: handle_client()
	else: print("Usage: <host> <port> <valid_img_save_dir> <invalid_img_save_dir>")
