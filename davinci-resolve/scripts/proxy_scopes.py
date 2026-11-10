"""Local RGB-code-value proxy scopes. Never native IRE/HDR/legal certification.
Requires existing numpy/Pillow; no network or package install.
"""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
from PIL import Image,ImageDraw

def measure(rgb):
 a=np.asarray(rgb,dtype=np.uint8);assert a.ndim==3 and a.shape[2]==3
 f=a.astype(float); y=f@np.array([.2126,.7152,.0722])
 return {'width':a.shape[1],'height':a.shape[0],'channels':{c:{'min':int(a[:,:,i].min()),'max':int(a[:,:,i].max()),'mean':float(a[:,:,i].mean()),'p1_p50_p99':np.percentile(a[:,:,i],[1,50,99]).tolist(),'fraction_at_code_0':float((a[:,:,i]==0).mean()),'fraction_at_code_255':float((a[:,:,i]==255).mean())} for i,c in enumerate('RGB')},'luma709_code_mean':float(y.mean()),'luma709_code_p1_p50_p99':np.percentile(y,[1,50,99]).tolist()}

def plots(rgb,path):
 im=Image.fromarray(rgb);im.thumbnail((640,360));a=np.asarray(im);f=a.astype(float);h,w=a.shape[:2];canvas=Image.new('RGB',(1100,340),(12,12,15));d=ImageDraw.Draw(canvas)
 d.text((10,5),'RGB CODE PROXIES | not native scopes / not IRE / no HDR certification',fill='white')
 colors=[(255,80,80),(80,255,100),(90,140,255)]
 # RGB parade: pixel-column vs channel code value; max per channel to keep density legible.
 for ch,col in enumerate(colors):
  x=np.broadcast_to(np.arange(w),(h,w));yy=255-a[:,:,ch].astype(int);hist=np.zeros((256,w),float);np.add.at(hist,(yy.ravel(),x.ravel()),1)
  g=np.log1p(hist);g=g/max(g.max(),1); tile=(g[:,:,None]*np.array(col)).astype('uint8');tile=Image.fromarray(tile).resize((110,256));canvas.paste(tile,(10+ch*112,55))
 d.text((10,32),'RGB Parade 0..255',fill='white')
 # Histogram RGB overlay, normalized per channel, logarithmic counts.
 for ch,col in enumerate(colors):
  counts=np.bincount(a[:,:,ch].ravel(),minlength=256);v=np.log1p(counts);v=v/max(v.max(),1);pts=[(370+i,310-int(z*250)) for i,z in enumerate(v)];d.line(pts,fill=col,width=1)
 d.text((370,32),'RGB histogram (log density)',fill='white')
 # Rec709 Cb/Cr from full-range RGB codes; no skin-line matching / automatic correction.
 y=f@np.array([.2126,.7152,.0722]);cb=(f[:,:,2]-y)/1.8556;cr=(f[:,:,0]-y)/1.5748
 u=np.clip(np.rint(cb+128),0,255).astype(int);v=np.clip(np.rint(128-cr),0,255).astype(int);density=np.zeros((256,256),float);np.add.at(density,(v.ravel(),u.ravel()),1)
 z=np.log1p(density);z=z/max(z.max(),1);tile=np.stack([z*200,z*230,z*255],axis=-1).astype('uint8');canvas.paste(Image.fromarray(tile),(725,55));d.text((725,32),'Cb/Cr image proxy',fill='white');d.line((725+128,55,725+128,310),fill=(70,65,40));d.line((725,55+128,980,55+128),fill=(70,65,40));d.ellipse((726,56,979,309),outline=(110,100,40))
 canvas.save(path)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('input',nargs='?');ap.add_argument('--output-prefix');ap.add_argument('--space',choices=['display-rec709','display-srgb']);ap.add_argument('--rect',help='x,y,w,h fractional region');ap.add_argument('--self-test',action='store_true');args=ap.parse_args()
 if args.self_test:
  black=measure(np.zeros((2,2,3),np.uint8));white=measure(np.full((2,2,3),255,np.uint8));red=measure(np.array([[[255,0,0]]],np.uint8));gray=measure(np.full((2,2,3),128,np.uint8))
  assert black['luma709_code_mean']==0;assert abs(white['luma709_code_mean']-255)<1e-8;assert abs(red['luma709_code_mean']-255*.2126)<1e-8;assert abs(gray['luma709_code_mean']-128)<1e-8;assert white['channels']['R']['fraction_at_code_255']==1
  print(json.dumps({'self_tests':5,'status':'PASS'}));return
 if not args.input or not args.space:ap.error('input and explicit --space required; log/HDR unsupported')
 p=Path(args.input);im=Image.open(p)
 if im.mode!='RGB':raise ValueError('Require explicit RGB PNG conversion; no silent 16-bit, alpha or palette truncation')
 if args.rect:
  x,y,w,h=map(float,args.rect.split(','));assert 0<=x<1 and 0<=y<1 and w>0 and h>0 and x+w<=1 and y+h<=1;W,H=im.size;im=im.crop((int(x*W),int(y*H),int((x+w)*W),int((y+h)*H)))
 rgb=np.asarray(im);out=Path(args.output_prefix or p.with_suffix(''))
 data={'source':str(p.resolve()),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'declared_space':args.space,'region':args.rect,'classification':'8-bit RGB display-code proxy; NOT native Resolve scopes','limits':['Explicit space is an assumption supplied by operator, not auto-certified','PNG endpoint counts do not prove camera clipping or legal/broadcast/HDR compliance','Stage-light colors are not automatically neutralized; no global skin-line target','Display-sRGB uses the same approximate Rec709 primary weighting, not linear luminance or calibrated IRE'],'measurement':measure(rgb)}
 Path(str(out)+'.json').write_text(json.dumps(data,indent=2),encoding='utf-8');plots(rgb,Path(str(out)+'.png'));print(json.dumps({'json':str(out)+'.json','plot':str(out)+'.png','classification':data['classification']}))
if __name__=='__main__':main()

