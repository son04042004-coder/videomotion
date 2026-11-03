"""Create two isolated 4-second diagnostic clips. Uses a tone, not paid TTS."""
from pathlib import Path
import json, subprocess
from PIL import Image, ImageDraw, ImageFont
ROOT = Path(__file__).resolve().parents[1]
VIDEOS = ROOT / 'luma-video' / 'public' / 'videos'
font_path = ROOT / 'luma-video/tools/ads/fonts/BeVietnamPro-Black.ttf'
for channel in ['k1', 'k2']:
    vid = f'2000-01-01-vm-demo-{channel}'
    folder = VIDEOS / vid
    shots = VIDEOS / f'{vid}-shots'
    if folder.exists() or shots.exists():
        raise SystemExit(f'Demo already exists; back it up before a new run: {folder}')
    folder.mkdir(parents=True)
    shots.mkdir()
    for index in [1, 2]:
        im = Image.new('RGB', (1440, 1500), '#eef2f7')
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((80,100,1360,1300), radius=30, fill='white', outline='#ced6e0', width=3)
        d.text((140,190), 'VIDEOMOTION', font=ImageFont.truetype(str(font_path),80), fill='#18253b')
        d.text((140,350), f'SCENE {index}', font=ImageFont.truetype(str(font_path),65), fill='#315be3')
        d.rounded_rectangle((140,600,1100,760),radius=24,fill='#315be3')
        d.text((190,640),'VIDEO DEMO',font=ImageFont.truetype(str(font_path),50),fill='white')
        d.text((140,1000),'1080 x 1920 / 30 FPS',font=ImageFont.truetype(str(font_path),45),fill='#18253b')
        im.save(shots/f'scene{index}.png')
        (shots/f'scene{index}.json').write_text(json.dumps({'boxes':{'button':[140,600,960,160]},'prices':[]}),encoding='utf-8')
    script={'lines':['[curious] Xem thử video này.','[excited] Cùng tạo chuyển động.'],'spoken':{}}
    words=[{'text':w,'startMs':i*500,'endMs':(i+1)*500-30} for i,w in enumerate('Xem thử video này. Cùng tạo chuyển động.'.split())]
    edl={'channel':channel,'shots_dir':shots.name,'product':f'demo-{channel}',
         'shots':[{'line':i,'img':f'scene{i+1}','url':'VideoMotion demo','tab':'Demo','tabs':['Motion'],
                   'cam':[[0,720,700,1400],[1.5,720,740,1200]],'cursor':[[0,200,300],[0.5,'box:button','click']],
                   'marks':[[0.6,1.6,'box:button']],**({'trans':'flash'} if i else {})} for i in [0,1]],
         'mgs':[{'id':'intro','type':'stack','line':0,'word':'Xem','offset':0,'dur':1.0,'sfx':[['pop',0.1]],
                 'data':{'head':'THỬ CHUYỂN ĐỘNG','items':[{'icon':'film','title':'VIDEO DEMO','sub':'kiểm tra bộ dựng'}]}}],
         'thumb':{'img':'scene2','variant':'v1','tag':'VIDEO DEMO','l1':'THỬ CHUYỂN ĐỘNG','num':'2','unit':'CẢNH','sub':'khung dọc rõ nét'}}
    for name,data in [('script.json',script),('words.json',{'durationMs':4000,'words':words}),('edl.json',edl)]:
        (folder/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    (folder/'caption.txt').write_text('Cùng thử chuyển động. #video #motion #sangtao #dungvideo #demo',encoding='utf-8')
    subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','sine=frequency=440:duration=4','-ar','48000','-b:a','192k',str(folder/'voice.mp3')],check=True)
    print(vid)
