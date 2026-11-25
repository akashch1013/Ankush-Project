#target "indesign"
// Compiled with one validated page plan. Keep the script beside its input links.
(function () {
    var plan = /* INSERT_PAGE_PLAN */ null;
    if (!plan) { throw Error("Compile the page plan before running its placement script."); }
    var base = File($.fileName).parent;
    var originalUnits = app.scriptPreferences.measurementUnit;
    var originalUI = app.scriptPreferences.userInteractionLevel;
    var originalRange = app.pdfExportPreferences.pageRange;
    var doc, output, links, page, none;
    var layers = {}, paints = {}, styles = {}, fonts = {}, assets = {}, texts = [];
    var report = [], issues = [], assetCounter = 0;
    var paper = plan.page, zero = [0, 0, 0, 0];

    function ensureFolder(folder) {
        if (!folder.exists && !folder.create()) { throw Error("Cannot make " + folder.fsName); }
        return folder;
    }
    function nextResult() {
        var root = ensureFolder(Folder(base.fsName + "/InDesign-results"));
        var stamp = new Date().getTime(), seq = 0, folder;
        do {
            folder = Folder(root.fsName + "/" + stamp + (seq ? "-" + seq : ""));
            seq++;
        } while (folder.exists);
        return ensureFolder(folder);
    }
    function noteFile() {
        if (!output) { return; }
        var file = File(output.fsName + "/Production-check.txt");
        file.encoding = "UTF-8";
        if (!file.open("w")) { throw Error("Cannot write production check."); }
        try { file.write(report.concat(issues).join("\r\n") + "\r\n"); }
        finally { file.close(); }
    }
    function copyAsset(rel) {
        var key = ":" + rel;
        if (assets[key]) { return assets[key]; }
        var original = File(base.fsName + "/" + rel);
        if (!original.exists) { throw Error("Missing source link " + rel); }
        // Prefix on collision so identical basenames from distinct archives stay distinct.
        var target = File(links.fsName + "/" + original.name);
        while (target.exists) {
            assetCounter++;
            target = File(links.fsName + "/" + assetCounter + "-" + original.name);
        }
        if (!original.copy(target.fsName)) { throw Error("Cannot package " + rel); }
        assets[key] = target;
        report.push("Linked " + rel + " as " + target.name);
        return target;
    }
    function bounds(box) { return [box[1], box[0], box[1] + box[3], box[0] + box[2]]; }
    function paint(item, spec) {
        item.fillColor = spec.fill ? paints[":" + spec.fill] : none;
        item.strokeColor = spec.stroke ? paints[":" + spec.stroke] : none;
        item.strokeWeight = spec.stroke ? (spec.weight === undefined ? 1 : spec.weight) : 0;
    }
    function paragraphText(s) { return s.replace(/\r\n|\n|\r/g, "\r"); }

    function setPage() {
        doc = app.documents.add(false);
        var pref = doc.documentPreferences, m = paper.margins || zero, b = paper.bleed || zero;
        pref.facingPages = false;
        pref.pagesPerDocument = 1;
        page = doc.pages[0];
        page.marginPreferences.properties = {top:0, left:0, bottom:0, right:0};
        pref.pageWidth = paper.size[0];
        pref.pageHeight = paper.size[1];
        pref.documentBleedUniformSize = false;
        pref.documentBleedTopOffset = b[0];
        pref.documentBleedInsideOrLeftOffset = b[1];
        pref.documentBleedBottomOffset = b[2];
        pref.documentBleedOutsideOrRightOffset = b[3];
        page.marginPreferences.properties = {top:m[0], left:m[1], bottom:m[2], right:m[3]};
        doc.viewPreferences.horizontalMeasurementUnits = MeasurementUnits.POINTS;
        doc.viewPreferences.verticalMeasurementUnits = MeasurementUnits.POINTS;
        doc.viewPreferences.rulerOrigin = RulerOrigin.PAGE_ORIGIN;
        doc.zeroPoint = [0, 0];
        if (paper.blend_space) {
            doc.transparencyPreferences.blendingSpace = paper.blend_space === "CMYK" ? BlendingSpace.CMYK : BlendingSpace.RGB;
        }
        none = doc.swatches.itemByName("None");
    }

    function resources() {
        var i, k, layer, v, s, f, style;
        for (i = 0; i < plan.layers.length; i++) {
            k = plan.layers[i];
            layer = i ? doc.layers.add({name:k}) : doc.layers[0];
            if (i === 0) { layer.name = k; }
            layers[":" + k] = layer;
        }
        for (k in plan.swatches) {
            if (!Object.prototype.hasOwnProperty.call(plan.swatches, k)) { continue; }
            v = plan.swatches[k];
            paints[":" + k] = doc.colors.add({name:"Page | " + k, model:ColorModel.PROCESS,
                space:v.length === 3 ? ColorSpace.RGB : ColorSpace.CMYK, colorValue:v});
        }
        var alignment = {left:Justification.LEFT_ALIGN, center:Justification.CENTER_ALIGN, right:Justification.RIGHT_ALIGN};
        for (k in plan.styles) {
            if (!Object.prototype.hasOwnProperty.call(plan.styles, k)) { continue; }
            s = plan.styles[k];
            f = app.fonts.itemByName(s.family + "\t" + s.face);
            if (!f.isValid || f.status !== FontStatus.INSTALLED) {
                throw Error("Missing required font " + s.family + " / " + s.face + " for " + k);
            }
            fonts[":" + k] = f;
            style = doc.paragraphStyles.add({name:"Page | " + k, appliedFont:f, fontStyle:s.face,
                pointSize:s.size, leading:s.leading, fillColor:paints[":" + s.color],
                justification:alignment[s.align || "left"], spaceAfter:s.space_after || 0,
                hyphenation:false});
            styles[":" + k] = style;
        }
    }

    function placeImage(o, layer) {
        var frame = page.rectangles.add(layer);
        frame.geometricBounds = bounds(o.box);
        paint(frame, {});
        var file = copyAsset(o.file), graphic;
        if (/\.pdf$/i.test(o.file)) {
            var previousPage = app.pdfPlacePreferences.pageNumber;
            try {
                app.pdfPlacePreferences.pageNumber = o.asset_page || 1;
                graphic = frame.place(file)[0];
                if (graphic.pdfAttributes.pageNumber !== (o.asset_page || 1)) {
                    throw Error("The requested PDF page was not placed for " + o.id);
                }
            } finally { app.pdfPlacePreferences.pageNumber = previousPage; }
        } else { graphic = frame.place(file)[0]; }
        frame.fit(o.fit === "cover" ? FitOptions.FILL_PROPORTIONALLY : FitOptions.PROPORTIONALLY);
        frame.fit(FitOptions.CENTER_CONTENT);
        var zoom = o.zoom || 1;
        if (zoom !== 1) {
            graphic.resize(CoordinateSpaces.PASTEBOARD_COORDINATES, AnchorPoint.CENTER_ANCHOR,
                ResizeMethods.MULTIPLYING_CURRENT_DIMENSIONS_BY, [zoom, zoom]);
        }
        var f = frame.geometricBounds, g = graphic.geometricBounds, focus = o.focus || [0.5, 0.5];
        var dx = f[1] + ((f[3]-f[1]) - (g[3]-g[1])) * focus[0] - g[1];
        var dy = f[0] + ((f[2]-f[0]) - (g[2]-g[0])) * focus[1] - g[0];
        if (Math.abs(dx) + Math.abs(dy) > 0.001) { graphic.move(undefined, [dx, dy]); }
        return frame;
    }
    function placeShape(o, layer) {
        var shape = (o.shape === "ellipse" ? page.ovals : page.rectangles).add(layer);
        shape.geometricBounds = bounds(o.box);
        paint(shape, o);
        if (o.radius) {
            var corners = ["topLeft", "topRight", "bottomLeft", "bottomRight"], i;
            for (i = 0; i < corners.length; i++) {
                shape[corners[i] + "CornerOption"] = CornerOptions.ROUNDED_CORNER;
                shape[corners[i] + "CornerRadius"] = o.radius;
            }
        }
        return shape;
    }
    function placePath(o, layer) {
        var p = (o.closed ? page.polygons : page.graphicLines).add(layer);
        p.paths[0].entirePath = o.points;
        p.paths[0].pathType = o.closed ? PathType.CLOSED_PATH : PathType.OPEN_PATH;
        paint(p, o);
        return p;
    }
    function placeText(o, layer) {
        var frame = page.textFrames.add(layer);
        frame.geometricBounds = bounds(o.box);
        paint(frame, {});
        frame.textFramePreferences.insetSpacing = o.inset || zero;
        var story = frame.parentStory, runs = o.runs || [{text:o.text}], i, start, end, run, range;
        var spans = [];
        for (i = 0; i < runs.length; i++) {
            run = runs[i];
            start = story.characters.length;
            if (run.text.length) { story.insertionPoints.item(-1).contents = paragraphText(run.text); }
            end = story.characters.length;
            if (end > start) { spans.push([start, end-1, run]); }
        }
        story.paragraphs.everyItem().appliedParagraphStyle = styles[":" + o.style];
        for (i = 0; i < spans.length; i++) {
            run = spans[i][2];
            range = story.characters.itemByRange(spans[i][0], spans[i][1]);
            if (run.style) {
                var s = plan.styles[run.style];
                range.appliedFont = fonts[":" + run.style];
                range.fontStyle = s.face;
                range.pointSize = s.size;
                range.leading = s.leading;
                range.fillColor = paints[":" + s.color];
            }
            if (run.position === "superscript") { range.position = Position.SUPERSCRIPT; }
            if (run.position === "subscript") { range.position = Position.SUBSCRIPT; }
            if (run.no_break !== undefined) { range.noBreak = run.no_break; }
            if (run.underline !== undefined) { range.underline = run.underline; }
        }
        texts.push([frame, o]);
        return frame;
    }
    function run() {
        output = nextResult();
        links = ensureFolder(Folder(output.fsName + "/Links"));
        report.push("Page " + paper.id, "Adobe InDesign " + app.version);
        setPage();
        resources();
        var make = {image:placeImage, shape:placeShape, path:placePath, text:placeText};
        var i, o, item, link;
        for (i = 0; i < plan.items.length; i++) {
            o = plan.items[i];
            item = make[o.kind](o, layers[":" + o.layer]);
            item.name = o.id;
            item.insertLabel("panel", o.panel);
            if (o.source) { item.insertLabel("source", o.source); }
            if (o.speaker) { item.insertLabel("speaker", o.speaker); }
            if (o.tail) { item.insertLabel("tail", o.tail); }
        }
        doc.recompose();
        for (i = 0; i < texts.length; i++) {
            item = texts[i][0]; o = texts[i][1];
            if (item.overflows) { issues.push("Overset: " + o.id); }
            if (paragraphText(String(item.parentStory.contents)) !== paragraphText(o.text)) {
                issues.push("Copy differs: " + o.id);
            }
        }
        for (i = 0; i < doc.links.length; i++) {
            link = doc.links[i];
            if (link.status !== LinkStatus.NORMAL) { issues.push("Check linked asset: " + link.name); }
        }
        doc.save(File(output.fsName + "/Page.indd"));
        doc.exportFile(ExportFormat.INDESIGN_MARKUP, File(output.fsName + "/Page.idml"), false);
        report.push("Placed " + plan.items.length + " items. Checked " + texts.length + " text frames and " + doc.links.length + " links.");
        if (issues.length) { report.push("Correct the listed issues before the final PDF."); }
        else if (paper.pdf_preset) {
            var preset = app.pdfExportPresets.itemByName(paper.pdf_preset);
            if (!preset.isValid) { throw Error("Missing PDF preset " + paper.pdf_preset); }
            app.pdfExportPreferences.pageRange = PageRange.ALL_PAGES;
            doc.exportFile(ExportFormat.PDF_TYPE, File(output.fsName + "/Page.pdf"), false, preset);
            report.push("Native PDF exported with preset " + paper.pdf_preset + ".");
        } else { report.push("Editable source ready. Use the edition's export settings to make the final PDF."); }
    }
    try {
        app.scriptPreferences.measurementUnit = MeasurementUnits.POINTS;
        app.scriptPreferences.userInteractionLevel = UserInteractionLevels.NEVER_INTERACT;
        run();
    } catch (error) {
        issues.push("Assembly or export stopped: " + error.message);
        throw error;
    } finally {
        try { noteFile(); }
        finally {
            try { if (doc && doc.isValid) { doc.close(SaveOptions.NO); } }
            finally {
                app.pdfExportPreferences.pageRange = originalRange;
                app.scriptPreferences.measurementUnit = originalUnits;
                app.scriptPreferences.userInteractionLevel = originalUI;
            }
        }
    }
}());
