"""Reusable native IDML primitives. Adobe InDesign is still required for actual PDF export.

No page content, layout coordinates, review result or chapter identity is supplied here.
"""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED,ZIP_STORED
from lxml import etree as E
from copy import deepcopy
from PIL import Image
import json,base64,math,sys,io
import tempfile
from type_paths import Typeface
SKILL_ROOT=Path(__file__).resolve().parents[1]
T=SKILL_ROOT/'assets'/'idml-template'
NS='http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging'
W,H=864,648
C={'ink':'32 53 68','ivory':'247 245 235','gold':'178 138 77','white':'255 255 255','silver':'226 232 236','blue':'19 39 60','navy':'13 28 50','teal':'22 60 64','plum':'48 31 49','forest':'34 55 46','dusk':'24 40 62','paleblue':'238 244 244','sage':'241 245 239','brasslight':'217 192 148'}
def xml(p):return E.parse(str(T/p)).getroot()
sp0=xml('Spreads/Spread_ud6.xml');sp=sp0.find('Spread')
page_template=deepcopy(sp.find('Page'));tf_template=deepcopy(sp.find('TextFrame'));rect_template=deepcopy(sp.find('Rectangle'))
story_template=xml('Stories/Story_u185.xml')
class Book:
 def __init__(self,outline=False,*,artwork_dir,font_dir,document_name,report_dir=None,
              page_size=(W,H),margins=(24,24,24,24),bleed=(0,0,0,0),palette=None,blend_space="RGB"):
  self.artwork_dir=Path(artwork_dir);self.font_dir=Path(font_dir) if font_dir is not None else None;self.report_dir=Path(report_dir) if report_dir else None
  self.document_name=str(document_name);self._saved=False
  self.width,self.height=page_size
  self.margins=margins
  self.bleed=bleed
  self.page_transform=f'1 0 0 1 {-self.width/2:g} {-self.height/2:g}'
  self.outline=outline;self.typefaces={f:Typeface(self.font_dir/n) for f,n in [('Source Serif 4','SourceSerif4-Regular.otf'),('Source Sans 3','SourceSans3-Regular.otf'),('Source Sans 3 Semibold','SourceSans3-Semibold.otf'),('Source Serif 4 Semibold','SourceSerif4-Semibold.otf'),('DejaVu Sans','DejaVuSans.ttf')]} if self.font_dir is not None else {}
  self.type_report=[]
  self.parts={str(p.relative_to(T)):p.read_bytes() for p in T.rglob('*') if p.is_file() and not str(p.relative_to(T)).startswith(('Spreads/','Stories/','META-INF/metadata'))}
  self.dm=xml('designmap.xml');self.uid=3000;self.stories=[];self.spreads=[];self.report=[]
  for x in list(self.dm):
   if E.QName(x).localname in ('Spread','Story','Section'):self.dm.remove(x)
  self.dm.set('Name',self.document_name);self.dm.set('StoryList','');self.dm.set('ActiveLayer','ud3')
  pref=xml('Resources/Preferences.xml');dp=pref.find('DocumentPreference')
  pref.find('TransparencyPreference').set('BlendingSpace',blend_space)
  dp.set('PageHeight',str(self.height));dp.set('PageWidth',str(self.width))
  dp.set('PagesPerDocument','1');dp.set('FacingPages','false');dp.set('DocumentBleedUniformSize','false')
  for attr,value in zip(('Top','InsideOrLeft','Bottom','OutsideOrRight'),self.bleed):
   dp.set('DocumentBleed'+attr+'Offset',str(value))
  self.parts['Resources/Preferences.xml']=self.serialize(pref)
  gr=xml('Resources/Graphic.xml')
  for name,val in (C if palette is None else palette).items():
   values=val.split() if isinstance(val,str) else val
   space='RGB' if len(values)==3 else 'CMYK'
   E.SubElement(gr,'Color',Self='Color/CH_'+name,Name='CH_'+name,Model='Process',Space=space,ColorValue=' '.join(map(str,values)))
  self.parts['Resources/Graphic.xml']=self.serialize(gr)
  if self.font_dir is None:
   return
  # Static font metadata is not a font availability/preflight certificate.
  fonts=xml('Resources/Fonts.xml')
  for i,f in enumerate(['Source Serif 4','Source Sans 3']):
   fam=E.SubElement(fonts,'FontFamily',Self=f'ch_font_{i}',Name=f)
   E.SubElement(fam,'Font',Self=f'ch_font_{i}_regular',FontFamily=f,Name=f+' Regular',PostScriptName=f.replace(' ','')+'-Regular',FontStyleName='Regular',FontType='OpenTypeCFF',FullName=f+' Regular',Status='Installed',WritingScript='0')
  for i,f in enumerate(['Source Serif 4','Source Sans 3']):
   fam=fonts.find("FontFamily[@Self='ch_font_"+str(i)+"']")
   E.SubElement(fam,'Font',Self=f'ch_font_{i}_semibold',FontFamily=f,Name=f+' Semibold',PostScriptName=f.replace(' ','')+'-Semibold',FontStyleName='Semibold',FontType='OpenTypeCFF',FullName=f+' Semibold',Status='Installed',WritingScript='0')
  fam=E.SubElement(fonts,'FontFamily',Self='ch_math_fallback',Name='DejaVu Sans')
  E.SubElement(fam,'Font',Self='ch_math_fallback_book',FontFamily='DejaVu Sans',Name='DejaVu Sans Book',PostScriptName='DejaVuSans',FontStyleName='Book',FontType='TrueType',FullName='DejaVu Sans',Status='Installed',WritingScript='0')
  self.parts['Resources/Fonts.xml']=self.serialize(fonts)
 def serialize(self,r):return E.tostring(r,encoding='UTF-8',xml_declaration=True,pretty_print=True)
 def id(self,p='ch'):
  self.uid+=1;return p+str(self.uid)
 def newpage(self,n):
  self.n=n;root=E.Element('{'+NS+'}Spread',nsmap={'idPkg':NS},DOMVersion='21.5');self.spread=E.SubElement(root,'Spread',Self=self.id('spread'),PageCount='1',BindingLocation='0',AllowPageShuffle='false',ItemTransform='1 0 0 1 0 0')
  pg=deepcopy(page_template)
  for k,v in {'Self':f'ch_page_{n}','Name':str(n),'GeometricBounds':f'0 0 {self.height} {self.width}','ItemTransform':self.page_transform,'AppliedMaster':'n','AppliedAlternateLayout':'n'}.items():pg.set(k,v)
  margin=pg.find('MarginPreference')
  margin.set('ColumnsPositions',f'0 {self.width-self.margins[1]-self.margins[3]}')
  for k,value in zip(('Top','Left','Bottom','Right'),self.margins):margin.set(k,str(value))
  self.spread.append(pg);self.spreads.append(root)
 def geom(self,item,x,y,w,h):
  item.set('ItemTransform',f'1 0 0 1 {x-self.width/2} {y-self.height/2}')
  props=item.find('Properties');old=props.find('PathGeometry')
  if old is not None:props.remove(old)
  pa=E.SubElement(E.SubElement(E.SubElement(props,'PathGeometry'),'GeometryPathType',PathOpen='false'),'PathPointArray')
  for xx,yy in [(0,0),(0,h),(w,h),(w,0)]:
   s=f'{xx} {yy}';E.SubElement(pa,'PathPointType',Anchor=s,LeftDirection=s,RightDirection=s)
 def add(self,it):
  it.set('ItemLayer',getattr(self,'current_layer','ud3'));self.spread.append(it)
 def box(self,x,y,w,h,fill='ivory',stroke='gold',weight=.65,radius=0):
  r=deepcopy(rect_template);r.set('Self',self.id());r.set('ContentType','Unassigned');r.set('FillColor','Color/CH_'+fill if fill else 'Swatch/None');r.set('StrokeColor','Color/CH_'+stroke if stroke else 'Swatch/None');r.set('StrokeWeight',str(weight))
  for e in list(r):
   if e.tag not in ['Properties']:r.remove(e)
  self.geom(r,x,y,w,h)
  if radius:
   for c in ['TopLeft','TopRight','BottomLeft','BottomRight']:r.set(c+'CornerOption','RoundedCorner');r.set(c+'CornerRadius',str(radius))
  self.add(r);return r
 def image(self,filename,x,y,w,h,fit='contain',crop_top=0,panel='',focal_y=.5,focal_x=.5):
  path=self.artwork_dir/filename;px,py=Image.open(path).size
  if fit not in ('contain','cover'):raise ValueError('Use contain or cover, never stretch')
  if not (0<=crop_top<py):raise ValueError('Invalid top crop')
  if min(w,h)<=0:raise ValueError('Image frame must have positive dimensions')
  if not (0<=focal_x<=1 and 0<=focal_y<=1):raise ValueError('Focal coordinates must be between 0 and 1')
  s=(min if fit=='contain' else max)(w/px,h/(py-crop_top))
  rw,rh=px*s,py*s;ox=(w-rw)*focal_x;oy=(h-rh)*focal_y
  if crop_top:oy=-crop_top*s  # A top crop anchors the remaining image at the frame top.
  r=deepcopy(rect_template);r.set('Self',self.id());r.set('StrokeWeight','.6');r.set('StrokeColor','Color/CH_ink');r.set('FillColor','Swatch/None');r.set('Name',panel or filename)
  self.geom(r,x,y,w,h)
  im=r.find('Image');im.set('Self',self.id());im.set('ImageTypeName','$ID/PNG');im.set('ActualPpi','72 72');im.set('EffectivePpi',f'{72/s} {72/s}');im.set('ItemTransform',f'{s} 0 0 {s} {ox} {oy}')
  buf=io.BytesIO();src=Image.open(path);src.convert('RGBA' if 'A' in src.getbands() else 'RGB').save(buf,format='PNG')
  im.find('Properties/Contents').text=base64.encodebytes(buf.getvalue()).decode()
  gb=im.find('.//GraphicBounds');gb.set('Left','0');gb.set('Top','0');gb.set('Right',str(px));gb.set('Bottom',str(py))
  link=im.find('Link');link.set('Self',self.id());link.set('LinkResourceURI','file:'+filename);link.set('LinkResourceFormat','$ID/PNG');link.set('StoredState','Embedded')
  for k in ['LinkImportStamp','LinkResourceSize','LinkImportModificationTime','LinkImportTime']:
   link.attrib.pop(k,None)
  self.add(r);self.report.append({'page':self.n,'panel':panel,'file':filename,'pixels':[px,py],'frame_pt':[x,y,w,h],'effective_ppi':round(72/s,1)})
 def fallback_runs(self,text,runs):
  refined=[]
  for run in (runs or [{'text':text}]):
   for ch in run['text']:
    style={k:v for k,v in run.items() if k!='text'}
    if ch=='∛':style['font']='DejaVu Sans';style['bold']=False
    if refined and {k:v for k,v in refined[-1].items() if k!='text'}==style:refined[-1]['text']+=ch
    else:refined.append(dict(style,text=ch))
  return refined
 def layout_text(self,text,font,size,width,runs=None):
  runs=self.fallback_runs(text,runs)
  import re
  chars=[]
  for run in (runs or [{'text':text}]):
   unknown=set(run)-{'text','font','bold','no_break','italic','vertical_alignment','underline'}
   if unknown:raise ValueError('Unsupported run fields: '+str(sorted(unknown)))
   f=run.get('font',font)
   if run.get('bold') and not f.endswith('Semibold'):f+=' Semibold'
   if f not in self.typefaces:raise ValueError('Missing configured font: '+f)
   if run.get('italic') or run.get('vertical_alignment') or run.get('underline'):raise ValueError('Unsupported source styling; extend renderer explicitly, do not drop it')
   for c in run['text']:
    if c not in '\n\r\t' and ord(c) not in self.typefaces[f].cmap:raise ValueError('Missing glyph '+repr(c)+' in '+f)
   chars += [(c,f) for c in run['text']]
  assert ''.join(c for c,f in chars)==text
  keep=[];chunk=''
  for rr in (runs or []):
   if rr.get('no_break'):chunk+=rr['text']
   elif chunk:keep.append(chunk);chunk=''
  if chunk:keep.append(chunk)
  prefix='|'.join(re.escape(q) for q in keep)
  if prefix:prefix+='|'
  rows=[];line=[];pending=[];linew=0;idx=0
  # Keep signed values and sign-pair explanations together when prose wraps.
  for token in re.findall(prefix+r'(?:negative|positive)\s+\d+[.,]?|[+−]\s+\(−?\d+\)|[+−]\s+\d+[.,]?|\S+|\s+',text):
   cc=chars[idx:idx+len(token)];idx+=len(token)
   if '\n' in token:
    rows.append((line,True))
    rows.extend([([],True)]*(token.count('\n')-1));line=[];pending=[];linew=0
   elif token.isspace():pending=cc
   else:
    tw=sum(self.typefaces[f].width(c,size) for c,f in cc)
    if tw>width+.1:raise ValueError('Unbreakable text wider than frame: '+repr(token))
    sw=sum(self.typefaces[f].width(c,size) for c,f in pending) if line else 0
    if line and linew+sw+tw>width:
     rows.append((line,False));line=[];linew=0;pending=[];sw=0
    if line:line+=pending
    line+=cc;linew+=sw+tw;pending=[]
  rows.append((line,True));return rows
 def text(self,text,x,y,w,h,size=14,font='Source Serif 4',color='ink',leading=18,fill=None,padding=0,align='LeftAlign',label='',runs=None):
  runs=self.fallback_runs(text,runs)
  if fill:self.box(x,y,w,h,fill=fill,stroke='gold',weight=.55,radius=5)
  sid=self.id('story');root=deepcopy(story_template);st=root.find('Story');st.set('Self',sid)
  for e in list(st):
   if e.tag=='ParagraphStyleRange':st.remove(e)
  para=None
  for run in (runs or [{'text':text}]):
   unknown=set(run)-{'text','font','bold','no_break','italic','vertical_alignment','underline'}
   if unknown:raise ValueError('Unsupported run fields: '+str(sorted(unknown)))
   f=run.get('font',font)
   if run.get('bold') and not f.endswith('Semibold'):f+=' Semibold'
   for j,piece in enumerate(run['text'].split('\n')):
    if para is None:para=E.SubElement(st,'ParagraphStyleRange',AppliedParagraphStyle='ParagraphStyle/$ID/NormalParagraphStyle',Hyphenation='false',Justification=align,SpaceAfter='5')
    cr=E.SubElement(para,'CharacterStyleRange',AppliedCharacterStyle='CharacterStyle/$ID/[No character style]',FillColor='Color/CH_'+color,PointSize=str(size),FontStyle=('Book' if f=='DejaVu Sans' else 'Semibold' if f.endswith('Semibold') else 'Regular'),StrokeWeight='0')
    if run.get('no_break'):cr.set('NoBreak','true')
    props=E.SubElement(cr,'Properties');E.SubElement(props,'Leading',type='unit').text=str(leading);E.SubElement(props,'AppliedFont',type='string').text=f.removesuffix(' Semibold')
    E.SubElement(cr,'Content').text=piece
    if j<len(run['text'].split('\n'))-1:E.SubElement(cr,'Br');para=None
  self.stories.append((sid,root))
  tf=deepcopy(tf_template);tf.set('Self',self.id('frame'));tf.set('ParentStory',sid);tf.set('Name',label or 'Editable text');tf.set('FillColor','Swatch/None');tf.set('StrokeColor','Swatch/None');tf.set('StrokeWeight','0')
  self.geom(tf,x,y,w,h if self.outline else h+12);pr=tf.find('TextFramePreference');pr.set('TextColumnFixedWidth',str(w));pr.set('FirstBaselineOffset','AscentOffset');pr.set('MinimumFirstBaselineOffset','0')
  for t in pr.findall('Properties/InsetSpacing/ListItem'):t.text=str(padding)
  if self.outline:tf.set('Visible','false');tf.set('Nonprinting','true')
  self.add(tf)
  lines=self.layout_text(text,font,size,w-padding*2,runs);base=y+padding+size;end=base
  pgs={}
  for line,last in lines:
   lw=sum(self.typefaces[f].width(c,size) for c,f in line);xx=x+padding
   if align=='CenterAlign':xx=x+(w-lw)/2
   if align=='RightAlign':xx=x+w-padding-lw
   for c,f in line:
    pg=pgs.setdefault(f,E.Element('PathGeometry'));self.typefaces[f].draw(c,size,xx,base,pg);xx+=self.typefaces[f].width(c,size)
   end=base+size*.25;base+=leading+(5 if last else 0)
  if end>y+h-padding+.1:raise ValueError(f'Text overflow page {self.n}: {label} needs {end-y:.1f}; box {h}')
  self.type_report.append({'page':self.n,'label':label,'text':text,'font':font,'size':size,'runs':runs,'lines':[''.join(c for c,f in l) for l,t in lines],'box_pt':[x,y,w,h],'bottom_pt':end})
  if self.outline:
   for f,pg in pgs.items():
    poly=E.Element('Polygon',Self=self.id('type'),ContentType='Unassigned',ItemLayer='ud3',FillColor='Color/CH_'+color,StrokeColor='Swatch/None',StrokeWeight='0',ItemTransform=self.page_transform,Name='Exact font outlines: '+label)
    E.SubElement(poly,'Properties').append(pg);self.add(poly)
 def path(self,points,color='gold',weight=.65,closed=False,fill=None):
  poly=E.Element('Polygon',Self=self.id('ornament'),ContentType='Unassigned',ItemLayer='ud3',FillColor='Color/CH_'+fill if fill else 'Swatch/None',StrokeColor='Color/CH_'+color if color else 'Swatch/None',StrokeWeight=str(weight),ItemTransform=self.page_transform,Name='Editable vector path')
  arr=E.SubElement(E.SubElement(E.SubElement(E.SubElement(poly,'Properties'),'PathGeometry'),'GeometryPathType',PathOpen='false' if closed else 'true'),'PathPointArray')
  for x,y in points:
   q=f'{x} {y}';E.SubElement(arr,'PathPointType',Anchor=q,LeftDirection=q,RightDirection=q)
  self.add(poly)
 def ring(self,cx,cy,r,color='gold',weight=.65):
  self.path([(cx+r*math.cos(i*math.pi/24),cy+r*math.sin(i*math.pi/24)) for i in range(48)],color,weight,True)
 def star(self,cx,cy,r=3):
  self.path([(cx+(r if i%2==0 else r*.26)*math.sin(i*math.pi/4),cy-(r if i%2==0 else r*.26)*math.cos(i*math.pi/4)) for i in range(8)],'gold',.4,True,'gold')
 def save(self,path):
  if self._saved:raise ValueError('Create a fresh Book for each saved source revision')
  if not self.spreads:raise ValueError('Cannot save an empty document')
  for n,r in enumerate(self.spreads,1):
   p=f'Spreads/CH_Page_{n:03}.xml';self.parts[p]=self.serialize(r);E.SubElement(self.dm,'{'+NS+'}Spread',src=p)
  self.dm.set('StoryList',' '.join(i for i,r in self.stories))
  for i,r in self.stories:
   p=f'Stories/{i}.xml';self.parts[p]=self.serialize(r);E.SubElement(self.dm,'{'+NS+'}Story',src=p)
  sec=E.SubElement(self.dm,'Section',Self='ch_section',Length=str(len(self.spreads)),AlternateLayoutLength=str(len(self.spreads)),AlternateLayout=self.document_name,Name='',ContinueNumbering='true',IncludeSectionPrefix='false',Marker='',PageStart=self.spreads[0].find('Spread/Page').get('Self'),SectionPrefix='')
  E.SubElement(E.SubElement(sec,'Properties'),'PageNumberStyle',type='enumeration').text='Arabic'
  pref=E.fromstring(self.parts['Resources/Preferences.xml']);pref.find('DocumentPreference').set('PagesPerDocument',str(len(self.spreads)));self.parts['Resources/Preferences.xml']=self.serialize(pref)
  self.parts['designmap.xml']=self.serialize(self.dm).replace(b'?>',b'?>\n<?aid style="50" type="document" readerVersion="6.0" featureSet="1025" product="21.5(73)" ?>',1)
  path=Path(path)
  with tempfile.NamedTemporaryFile(dir=path.parent,suffix='.idml',delete=False) as temp:
   staged=Path(temp.name)
  try:
   with ZipFile(staged,'w',ZIP_DEFLATED) as z:
    z.writestr('mimetype','application/vnd.adobe.indesign-idml-package',compress_type=ZIP_STORED)
    for k,v in self.parts.items():
     if k!='mimetype':z.writestr(k,v)
   with ZipFile(staged) as z:
    if z.testzip() is not None:raise ValueError('Invalid IDML archive')
   staged.replace(path)
  finally:
   staged.unlink(missing_ok=True)
  self._saved=True
  if self.report_dir:
   self.report_dir.mkdir(parents=True,exist_ok=True)
   (self.report_dir/(path.stem+'-image-resolution.json')).write_text(json.dumps(self.report,indent=2))
   (self.report_dir/(path.stem+'-typesetting.json')).write_text(json.dumps(self.type_report,ensure_ascii=False,indent=2))
