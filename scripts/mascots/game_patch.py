"""Swap the Coinpull game's hand-drawn player body for the dancing kitten sprite (jetpack left in place)."""
p = '/home/claude/throwindice/index.html'; s = open(p).read()
a = s.index(' /* feet */\n', s.index('function player(x,y,s){'))
b = s.index(' g.restore()}', a)
new = (" /* gold aura (kept) */\n"
       " const gd=s.gold>0;if(gd){const ar=g.createRadialGradient(0,-50,10,0,-50,120);ar.addColorStop(0,'rgba(255,225,80,.55)');ar.addColorStop(1,'rgba(255,225,80,0)');g.fillStyle=ar;g.beginPath();g.arc(0,-50,120,0,6.3);g.fill()}\n"
       " /* the dancing kitten from the basics page: 420-frame sheet, 8 frames wide, played at 24 fps (faster while boosting) */\n"
       " const im=window._dancerSheet||(window._dancerSheet=Object.assign(new Image(),{src:'assets/mascots/dancer-dance.webp'}));\n"
       " g.translate(0,-bob);if(im.complete&&im.naturalWidth){const C=8,N=420,fw=im.naturalWidth/C,fi=Math.floor(t*(u>0?36:24))%N,S=150;\n"
       "  g.drawImage(im,(fi%C)*fw,Math.floor(fi/C)*fw,fw,fw,-S/2,-S*.9,S,S)}\n")
s = s[:a] + new + s[b:]
open(p, 'w').write(s); print('player body replaced')
