import random, hashlib, requests, string
import threading
import time
import string
import signal

from io import BytesIO
from PIL import Image
import requests

# Attention, si l'image est trop grande le nombre de proofs ne sera jamais suffisant
# Pour une image de 20x20 pixels 10 threads ne sont pas suffisant

# Complètement comme on veut, il faut juste que l'image soit comprise dans le cadre
X_OFFSET = 4
Y_OFFSET = 24

# on peut lire une image en local avec, pas besoin de faire des requêtes web
# baseImg = Image.open(PATH)

print('[+] Fetching base image')
r = requests.get('https://cdn.discordapp.com/attachments/621072234538205219/693525043786940516/charmander32.png')
baseImg = Image.open(BytesIO(r.content))
baseImg = baseImg.convert('RGB')
width, height = baseImg.size
baseData = list(baseImg.getdata())

pfile = open("/home/alol/CTF/proofs.txt", 'r+') # suce

proofs = pfile.read().splitlines()
proofs = set(proofs)

# Regarde toutes les minutes l'image en ligne et modifie les pixels qui ne correspondent pas
def pixelsetter():
	while True:
		print('[+] Fetching online image')
		r = requests.get('http://pixelwar.h25.io/image')
		onlineImg = Image.open(BytesIO(r.content))
		onlineImg = onlineImg.convert('RGB')
		cropedOnlineImg = onlineImg.crop((Y_OFFSET, X_OFFSET, Y_OFFSET +width, X_OFFSET +height))
		onlineData = list(cropedOnlineImg.getdata())

		for i in range(height):
			for j in range(width):
				if bytes(baseData[i*width+j]).hex() != 'ffffff' and baseData[i*width+j] != onlineData[i*width+j]:
					while not proofs:
						print('[!!!] NO PROOFS, WAITING')
						time.sleep(10)

					# très très sale mais est ce vraiment mon problème
					done = False
					while not done:
						params = {'x':str(j + Y_OFFSET),
								'y':str(i + X_OFFSET),
								'color': bytes(baseData[i*20+j]).hex(),
								'proof': proofs.pop()}
					
						r = requests.get('http://pixelwar.h25.io/setpixel', params=params)
						if r.ok:
							print('[+] Pixel rectified, still', len(proofs), 'proofs in queue')
							done = True 
						else:
							print('[!] Failed to change pixel', r.text)
		print('[+] All done, sleeping')
		time.sleep(60)

# Calcule et cherche des hashs commençant par 000000
def computer():
	while True:
		proof = 'alol' + ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(25)])
		if hashlib.sha256(('h25'+proof).encode()).hexdigest().startswith('00000'):
			proofs.add(proof)
			print('[+] Thread found proof', proof)

# sig handler, pour sauvegarder les proofs quand on quitte
def signal_handler(sig, frame):
	print('[q] Ok, quitting')
	pfile.writelines( '\n'.join(list(proofs)) )
	pfile.close()
	exit(0)

signal.signal(signal.SIGINT, signal_handler)

print('[T] Starting pixelsetter')
t1 = threading.Thread(target=pixelsetter)
t1.start()

print('[T] Starting computer')
t2 = threading.Thread(target=computer)
t2.start()
