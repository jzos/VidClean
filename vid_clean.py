#!/usr/bin/env python3
import argparse, json, subprocess as sp, shutil, sys, os
from pathlib import Path
import cv2
import numpy as np
p=argparse.ArgumentParser(description='Calibrated reverse compositing for 1080x1920 Google Vids exports.')
p.add_argument('input'); p.add_argument('output',nargs='?'); p.add_argument('--preview',action='store_true'); p.add_argument('--overwrite',action='store_true'); p.add_argument('--frame',type=int,default=0); a=p.parse_args()
for c in ('ffmpeg','ffprobe'):
 if not shutil.which(c): p.error('Missing '+c)
src=Path(a.input); dst=Path(a.output or str(src.with_name(src.stem+'_v3.mp4')))
if not src.is_file(): p.error('Input not found')
if not a.preview and src.resolve()==dst.resolve(): p.error('Output equals input')
if not a.preview and dst.exists() and not a.overwrite: p.error('Output exists; use --overwrite or another name')
if a.frame<0: p.error('Frame must be nonnegative')
info=json.loads(sp.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_streams','-of','json',str(src)]))['streams'][0]
w,h=info['width'],info['height']; fps=info['avg_frame_rate']
if (w,h)!=(1080,1920): p.error('Profile only calibrated for 1080x1920 video')
if fps=='0/0': p.error('Unknown frame rate')
profile=np.frombuffer(Path(__file__).with_name('profile.bin').read_bytes(),dtype='<f4').reshape(90,90,4)
slope=profile[:,:,:1]; offset=profile[:,:,1:]; x0,y0=855,1695; x1,y1=945,1785
print('VidClean: calibrated reverse compositing, no inpainting',flush=True)
dec=sp.Popen(['ffmpeg','-v','error','-noautorotate','-i',str(src),'-map','0:v:0','-vsync','0','-f','rawvideo','-pix_fmt','bgr24','pipe:1'],stdout=sp.PIPE)
enc=None; n=0
try:
 if not a.preview:
  enc=sp.Popen(['ffmpeg','-v','error',('-y' if a.overwrite else '-n'),'-f','rawvideo','-pix_fmt','bgr24','-s',f'{w}x{h}','-r',fps,'-i','pipe:0','-i',str(src),'-map','0:v:0','-map','1:a?','-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(dst)],stdin=sp.PIPE)
 while True:
  data=dec.stdout.read(w*h*3)
  if not data: break
  if len(data)!=w*h*3: raise RuntimeError('Incomplete decoded frame')
  frame=np.frombuffer(data,np.uint8).reshape(h,w,3).copy(); roi=frame[y0:y1,x0:x1]
  roi[:]=np.clip(np.rint((roi.astype(np.float32)-offset)/slope),0,255).astype(np.uint8)
  n+=1
  if a.preview:
   if n-1<a.frame: continue
   out=dst.with_suffix('.png')
   if out.resolve()==src.resolve(): raise RuntimeError('Preview equals input')
   if out.exists() and not a.overwrite: raise RuntimeError('Preview exists; use --overwrite')
   if not cv2.imwrite(str(out),frame): raise RuntimeError('Preview write failed')
   print('Saved:',out); break
  enc.stdin.write(frame.tobytes())
  if n%100==0: print(f'{n} frames',flush=True)
 if a.preview and n<=a.frame: raise RuntimeError("Requested frame not found")
 if not n: raise RuntimeError('No frames decoded')
 if enc:
  enc.stdin.close(); rc=enc.wait(); drc=dec.wait()
  if rc or drc: raise RuntimeError('FFmpeg failed')
  print('Saved:',dst)
finally:
 if dec.stdout: dec.stdout.close()
 if dec.poll() is None: dec.kill(); dec.wait()
 if enc and enc.poll() is None: enc.terminate(); enc.wait()
