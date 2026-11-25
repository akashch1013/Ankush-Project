"""Assemble a native IDML from the same single-page placement plan as the Adobe script."""
import base64
from copy import deepcopy
from urllib.parse import quote

from lxml import etree as E
from PIL import Image, UnidentifiedImageError

from native_idml import Book, rect_template, story_template, tf_template


def labelled(item, spec):
    item.set("Name", spec["id"])
    props = item.find("Properties")
    label = props.find("Label")
    if label is None:
        label = E.SubElement(props, "Label")
    for key in ("panel", "source", "role", "speaker", "tail"):
        if key in spec:
            E.SubElement(label, "KeyValuePair", Key=key, Value=spec[key])


def path_geometry(item, points, closed):
    props = item.find("Properties")
    existing = props.find("PathGeometry")
    if existing is not None:
        props.remove(existing)
    geometry = E.SubElement(props, "PathGeometry")
    path = E.SubElement(geometry, "GeometryPathType", PathOpen="false" if closed else "true")
    array = E.SubElement(path, "PathPointArray")
    for point in points:
        left, anchor, right = point if len(point) == 3 else (point, point, point)
        fields = {key: " ".join(map(str, value)) for key, value in
                  (("Anchor", anchor), ("LeftDirection", left), ("RightDirection", right))}
        E.SubElement(array, "PathPointType", **fields)


def ellipse_points(width, height):
    x, y = width / 2, height / 2
    k = 0.5522847498307936
    return [
        [[x*(1+k), 0], [x, 0], [x*(1-k), 0]],
        [[0, y*(1-k)], [0, y], [0, y*(1+k)]],
        [[x*(1-k), height], [x, height], [x*(1+k), height]],
        [[width, y*(1+k)], [width, y], [width, y*(1-k)]],
    ]


class PageLayout:
    def __init__(self, plan, root, embedded=False):
        self.plan = plan
        self.root = root
        self.embedded = embedded
        self.keys = {name: f"sw{i}" for i, name in enumerate(plan["swatches"])}
        palette = {self.keys[name]: value for name, value in plan["swatches"].items()}
        spec = plan["page"]
        self.book = Book(artwork_dir=root, font_dir=None, document_name=spec["id"],
                         page_size=spec["size"], margins=spec.get("margins", [0]*4),
                         bleed=spec.get("bleed", [0]*4), palette=palette,
                         blend_space=spec.get("blend_space", "RGB"))
        self.book.newpage(1)
        self.layers = self.add_layers(plan["layers"])
        self.styles = self.add_styles(plan["styles"])
        self.register_fonts(plan["styles"])
        graphics = E.fromstring(self.book.parts["Resources/Graphic.xml"])
        for key, ref in self.keys.items():
            graphics.find(f"Color[@Self='Color/CH_{ref}']").set("Name", "Page | " + key)
        self.book.parts["Resources/Graphic.xml"] = self.book.serialize(graphics)

    def add_layers(self, names):
        design = self.book.dm
        base = design.find("Layer")
        base.set("Name", names[0])
        ids = {names[0]: base.get("Self")}
        for index, name in enumerate(names[1:], 1):
            layer = deepcopy(base)
            ids[name] = self.book.id("layer")
            layer.set("Self", ids[name])
            layer.set("Name", name)
            design.insert(design.index(base) + index, layer)
        design.set("ActiveLayer", ids[names[-1]])
        return ids

    def swatch(self, name):
        return "Swatch/None" if name is None else "Color/CH_" + self.keys[name]

    def type_properties(self, node, style):
        node.set("FontStyle", style["face"])
        node.set("PointSize", str(style["size"]))
        node.set("FillColor", self.swatch(style["color"]))
        props = E.SubElement(node, "Properties")
        E.SubElement(props, "Leading", type="unit").text = str(style["leading"])
        E.SubElement(props, "AppliedFont", type="string").text = style["family"]

    def register_fonts(self, styles):
        path = "Resources/Fonts.xml"
        root = E.fromstring(self.book.parts[path])
        families = {family.get("Name"): family for family in root.findall("FontFamily")}
        for style in styles.values():
            name, face = style["family"], style["face"]
            family = families.get(name)
            if family is None:
                family = E.SubElement(root, "FontFamily", Self=self.book.id("fontFamily"), Name=name)
                families[name] = family
            if not any(font.get("FontStyleName") == face for font in family.findall("Font")):
                E.SubElement(family, "Font", Self=self.book.id("font"), Name=name + " " + face,
                             FontFamily=name, FontStyleName=face, FullName=name + " " + face)
        self.book.parts[path] = self.book.serialize(root)

    def add_styles(self, styles):
        path = "Resources/Styles.xml"
        root = E.fromstring(self.book.parts[path])
        group = root.find("RootParagraphStyleGroup")
        ids = {}
        for i, (name, style) in enumerate(styles.items()):
            ids[name] = f"ParagraphStyle/pageStyle{i}"
            align = {"left":"LeftAlign", "center":"CenterAlign", "right":"RightAlign"}[style.get("align", "left")]
            node = E.SubElement(group, "ParagraphStyle", Self=ids[name], Name="Page | " + name,
                                Hyphenation="false", Justification=align,
                                SpaceAfter=str(style.get("space_after", 0)))
            self.type_properties(node, style)
        self.book.parts[path] = self.book.serialize(root)
        return ids

    def frame(self, spec):
        b = self.book
        return b.box(*spec["box"], fill=self.keys.get(spec.get("fill")),
                     stroke=self.keys.get(spec.get("stroke")),
                     weight=spec.get("weight", 1) if spec.get("stroke") else 0,
                     radius=spec.get("radius", 0))

    def shape(self, spec):
        item = self.frame(spec)
        if spec["shape"] == "ellipse":
            item.tag = "Oval"
            path_geometry(item, ellipse_points(*spec["box"][2:]), True)
        return item

    def path(self, spec):
        closed = spec.get("closed", False)
        tag = "Polygon" if closed else "GraphicLine"
        item = E.Element(tag, Self=self.book.id("path"), ContentType="Unassigned",
                         FillColor=self.swatch(spec.get("fill")), StrokeColor=self.swatch(spec.get("stroke")),
                         StrokeWeight=str(spec.get("weight", 1) if spec.get("stroke") else 0),
                         ItemTransform=self.book.page_transform)
        E.SubElement(item, "Properties")
        path_geometry(item, spec["points"], closed)
        self.book.add(item)
        return item

    def image(self, spec):
        file = self.root / spec["file"]
        try:
            original = Image.open(file)
        except (UnidentifiedImageError, OSError) as exc:
            raise ValueError(f"{file.name}: use the generated InDesign script to place this asset format") from exc
        with original as src:
            fmt = src.format
            if fmt not in ("JPEG", "PNG", "TIFF") or getattr(src, "n_frames", 1) != 1:
                raise ValueError(f"{file.name}: use the native placement script for this asset format")
            if src.getexif().get(0x0112, 1) != 1:
                raise ValueError(f"{file.name}: use the native placement script for oriented source art")
            px, py = src.size
            dpi = src.info.get("dpi", (72, 72))
            dx, dy = (v if isinstance(v, (int,float)) and v > 0 else 72 for v in dpi)
            space = "CMYK" if src.mode == "CMYK" else "RGB"
        iw, ih = px*72/dx, py*72/dy
        x, y, w, h = spec["box"]
        scale = (max if spec["fit"] == "cover" else min)(w/iw, h/ih) * spec.get("zoom", 1)
        fx, fy = spec.get("focus", [.5, .5])
        frame = deepcopy(rect_template)
        frame.set("Self", self.book.id("imageframe"))
        frame.set("StrokeColor", "Swatch/None")
        frame.set("StrokeWeight", "0")
        frame.set("FillColor", "Swatch/None")
        self.book.geom(frame, x, y, w, h)
        im = frame.find("Image")
        im.set("Self", self.book.id("graphic"))
        im.set("Space", "$ID/#Links_" + space)
        im.set("ImageTypeName", "$ID/" + fmt)
        im.set("ActualPpi", f"{dx} {dy}")
        im.set("EffectivePpi", f"{dx/scale} {dy/scale}")
        im.set("ItemTransform", f"{scale} 0 0 {scale} {(w-iw*scale)*fx} {(h-ih*scale)*fy}")
        bounds = im.find("Properties/GraphicBounds")
        for key, value in (("Left",0),("Top",0),("Right",iw),("Bottom",ih)):
            bounds.set(key, str(value))
        props = im.find("Properties")
        contents = props.find("Contents")
        if self.embedded:
            contents.text = base64.encodebytes(file.read_bytes()).decode("ascii")
        else:
            props.remove(contents)
        link = im.find("Link")
        link.set("Self", self.book.id("link"))
        link.set("LinkResourceURI", "file:" + quote(spec["file"], safe="/"))
        link.set("LinkResourceFormat", "$ID/" + fmt)
        link.set("StoredState", "Embedded" if self.embedded else "Normal")
        self.book.add(frame)
        return frame

    def text(self, spec):
        root = deepcopy(story_template)
        sid = self.book.id("story")
        story = root.find("Story")
        story.set("Self", sid)
        for node in story.findall("ParagraphStyleRange"):
            story.remove(node)
        para = None
        for run in spec.get("runs") or [{"text": spec["text"]}]:
            pieces = run["text"].replace("\r\n", "\n").replace("\r", "\n").split("\n")
            for i, piece in enumerate(pieces):
                if para is None:
                    para = E.SubElement(story, "ParagraphStyleRange", AppliedParagraphStyle=self.styles[spec["style"]])
                cr = E.SubElement(para, "CharacterStyleRange",
                                  AppliedCharacterStyle="CharacterStyle/$ID/[No character style]")
                self.type_properties(cr, self.plan["styles"][run.get("style", spec["style"])])
                if run.get("no_break"):
                    cr.set("NoBreak", "true")
                if run.get("underline"):
                    cr.set("Underline", "true")
                if run.get("position") in ("superscript", "subscript"):
                    cr.set("Position", run["position"].capitalize())
                E.SubElement(cr, "Content").text = piece
                if i+1 < len(pieces):
                    E.SubElement(cr, "Br")
                    para = None
        self.book.stories.append((sid, root))
        box = spec["box"]
        frame = deepcopy(tf_template)
        for key, value in (("Self",self.book.id("frame")), ("ParentStory",sid),
                           ("FillColor","Swatch/None"),("StrokeColor","Swatch/None"),("StrokeWeight","0")):
            frame.set(key, value)
        self.book.geom(frame, *box)
        pref = frame.find("TextFramePreference")
        inset = spec.get("inset", [0]*4)
        pref.set("TextColumnFixedWidth", str(box[2]-inset[1]-inset[3]))
        pref.set("FirstBaselineOffset", "AscentOffset")
        for element, value in zip(pref.findall("Properties/InsetSpacing/ListItem"), inset):
            element.text = str(value)
        self.book.add(frame)
        return frame

    def save(self, output):
        for item in self.plan["items"]:
            self.book.current_layer = self.layers[item["layer"]]
            native = getattr(self, item["kind"])(item)
            labelled(native, item)
        self.book.save(output)
