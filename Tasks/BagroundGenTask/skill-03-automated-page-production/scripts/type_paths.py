from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from lxml import etree as E
from pathlib import Path
class ContourPen(BasePen):
 def __init__(self,gs):super().__init__(gs);self.contours=[];self.points=[]
 def _moveTo(self,p):self.points=[{'a':p,'l':p,'r':p}]
 def _lineTo(self,p):self.points.append({'a':p,'l':p,'r':p})
 def _curveToOne(self,a,b,c):self.points[-1]['r']=a;self.points.append({'a':c,'l':b,'r':c})
 def _closePath(self):
  if len(self.points)>1 and self.points[-1]['a']==self.points[0]['a']:
   self.points[0]['l']=self.points[-1]['l'];self.points.pop()
  self.contours.append(self.points);self.points=[]
 def _endPath(self):self._closePath()
class Typeface:
 def __init__(self,path):
  self.f=TTFont(path);self.gs=self.f.getGlyphSet();self.cmap=self.f.getBestCmap();self.upem=self.f['head'].unitsPerEm;self.hmtx=self.f['hmtx'].metrics;self.cache={}
 def width(self,text,size):return sum(self.hmtx[self.cmap.get(ord(c),'.notdef')][0] for c in text)*size/self.upem
 def lines(self,text,size,width):
  lines=[]
  for para in text.split('\n'):
   current=''
   for word in para.split():
    v=(current+' '+word).strip()
    if current and self.width(v,size)>width:lines.append((current,False));current=word
    else:current=v
   lines.append((current,True))
  return lines
 def draw(self,text,size,x,y,pathgeom):
  factor=size/self.upem
  for ch in text:
   glyph=self.cmap.get(ord(ch),'.notdef')
   if glyph not in self.cache:
    p=ContourPen(self.gs);self.gs[glyph].draw(p);self.cache[glyph]=p.contours
   for pts in self.cache[glyph]:
    arr=E.SubElement(E.SubElement(pathgeom,'GeometryPathType',PathOpen='false'),'PathPointArray')
    for pt in pts:
     cv=lambda v:f'{x+v[0]*factor:.5f} {y-v[1]*factor:.5f}'
     E.SubElement(arr,'PathPointType',Anchor=cv(pt['a']),LeftDirection=cv(pt['l']),RightDirection=cv(pt['r']))
   x+=self.hmtx[glyph][0]*factor
