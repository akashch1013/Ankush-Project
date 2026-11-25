#!/usr/bin/env python3
"""Validate one page plan and compile a portable Adobe InDesign placement script."""
import argparse
import json
import math
import os
import sys
import tempfile
from pathlib import Path, PurePosixPath, PureWindowsPath


def require(test, message):
    if not test:
        raise ValueError(message)


def number(value, label, *, minimum=None, maximum=None):
    require(isinstance(value, (float, int)) and not isinstance(value, bool)
            and math.isfinite(value), f"{label} must be a finite number")
    if minimum is not None:
        require(value >= minimum, f"{label} must be at least {minimum}")
    if maximum is not None:
        require(value <= maximum, f"{label} must be at most {maximum}")
    return value


def vector(value, length, label, **limits):
    require(isinstance(value, list) and len(value) == length, f"{label} requires {length} values")
    for scalar in value:
        number(scalar, label, **limits)
    return value


def name(value, label):
    require(isinstance(value, str) and value.strip(), f"{label} requires a non-empty string")
    return value


def asset(root, value, label):
    name(value, label)
    path = PurePosixPath(value)
    windows = PureWindowsPath(value)
    require(not path.is_absolute() and not windows.drive and "\\" not in value
            and ".." not in path.parts, f"{label} must be package-relative with forward slashes")
    resolved = (root / path).resolve()
    require(resolved.is_relative_to(root) and resolved.is_file(), f"{label} missing in package: {value}")


def validate(plan, root):
    require(isinstance(plan, dict), "Expected a page plan object")
    page = plan["page"]
    name(page["id"], "page.id")
    width, height = vector(page["size"], 2, "page.size")
    require(min(width, height) > 0, "Trim size must be positive")
    top, left, bottom, right = vector(page.get("margins", [0]*4), 4, "margins", minimum=0)
    require(top+bottom < height and left+right < width, "Margins must leave a live area")
    vector(page.get("bleed", [0]*4), 4, "bleed", minimum=0)
    require(page.get("blend_space", "RGB") in ("RGB", "CMYK"), "Unknown transparency blend space")
    if "pdf_preset" in page:
        name(page["pdf_preset"], "pdf_preset")

    layers = plan["layers"]
    require(isinstance(layers, list) and layers, "Supply at least one layer")
    for layer in layers:
        name(layer, "layer")
    require(len(set(layers)) == len(layers), "Duplicate layer name")
    swatches = plan["swatches"]
    styles = plan["styles"]
    require(isinstance(swatches, dict) and isinstance(styles, dict), "swatches and styles must be objects")
    for key, channels in swatches.items():
        name(key, "swatch name")
        require(isinstance(channels, list) and len(channels) in (3, 4), f"{key} requires an RGB or CMYK value")
        vector(channels, len(channels), key, minimum=0, maximum=255 if len(channels) == 3 else 100)
    for key, style in styles.items():
        name(key, "style name")
        for field in ("family", "face"):
            name(style[field], f"{key}.{field}")
        for field in ("size", "leading"):
            require(number(style[field], f"{key}.{field}") > 0, f"{key}.{field} must be positive")
        require(style["color"] in swatches, f"{key} uses an unknown text colour")
        require(style.get("align", "left") in ("left", "center", "right"), f"{key} has an unknown alignment")
        number(style.get("space_after", 0), f"{key}.space_after", minimum=0)

    items = plan["items"]
    require(isinstance(items, list) and (items or page.get("intentional_blank") is True),
            "Declare an intentional blank for a page with no items")
    by_id = {}
    speech = []
    for item in items:
        key = name(item["id"], "item.id")
        require(key not in by_id, f"Duplicate item ID: {key}")
        by_id[key] = item
        name(item["panel"], f"{key}.panel")
        require(item["layer"] in layers, f"{key} uses an unknown layer")
        kind = item["kind"]
        require(kind in ("image", "shape", "path", "text"), f"{key} has unknown kind {kind}")
        if kind != "path":
            _, _, w, h = vector(item["box"], 4, f"{key}.box")
            require(min(w, h) > 0, f"{key} requires a positive frame")
        if kind in ("shape", "path"):
            for field in ("fill", "stroke"):
                if field in item:
                    require(item[field] in swatches, f"{key}.{field} uses an unknown swatch")
            number(item.get("weight", 1), f"{key}.weight", minimum=0)
        if kind == "image":
            asset(root, item["file"], key)
            if "asset_page" in item:
                page_number = item["asset_page"]
                require(type(page_number) is int and page_number > 0 and item["file"].lower().endswith(".pdf"),
                        f"{key}.asset_page requires a positive PDF page number")
            require(item["fit"] in ("cover", "contain"), f"{key} requires cover or contain")
            vector(item.get("focus", [0.5, 0.5]), 2, f"{key}.focus", minimum=0, maximum=1)
            number(item.get("zoom", 1), f"{key}.zoom", minimum=1)
        elif kind == "shape":
            require(item["shape"] in ("rectangle", "ellipse"), f"{key} has unknown shape")
            radius = number(item.get("radius", 0), f"{key}.radius", minimum=0)
            require(radius <= min(w, h)/2 and (not radius or item["shape"] == "rectangle"),
                    f"{key} has an invalid corner radius")
        elif kind == "path":
            pts = item["points"]
            require(isinstance(pts, list) and len(pts) >= (3 if item.get("closed") else 2),
                    f"{key} has insufficient points")
            for point in pts:
                if isinstance(point, list) and len(point) == 3 and isinstance(point[0], list):
                    for handle in point:
                        vector(handle, 2, key)
                else:
                    vector(point, 2, key)
        else:
            name(item["role"], f"{key}.role")
            name(item["source"], f"{key}.source")
            require(item["style"] in styles, f"{key} uses an unknown text style")
            require(isinstance(item["text"], str), f"{key} requires exact text")
            t, l, b, r = vector(item.get("inset", [0]*4), 4, f"{key}.inset", minimum=0)
            require(l+r < w and t+b < h, f"{key}'s inset consumes its frame")
            if "runs" in item:
                runs = item["runs"]
                require(isinstance(runs, list) and all(isinstance(run["text"], str) for run in runs)
                        and "".join(run["text"] for run in runs) == item["text"],
                        f"{key}'s styled runs differ from its exact text")
                for run in runs:
                    require(run.get("style", item["style"]) in styles, f"{key} has an unknown run style")
                    require(run.get("position", "normal") in ("normal", "superscript", "subscript"),
                            f"{key} has an unknown baseline position")
            if item["role"] == "speech":
                name(item.get("speaker"), f"{key}.speaker")
                speech.append(item)
    for item in speech:
        if item.get("tailless") is True:
            require("tail" not in item, f"{item['id']} specifies both a tail and tailless")
            continue
        tail = by_id.get(item.get("tail"))
        require(tail and tail["kind"] in ("shape", "path") and tail["panel"] == item["panel"],
                f"{item['id']} needs the matching panel's balloon or tail ID")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--check", action="store_true", help="Validate without writing a script")
    parser.add_argument("--idml", action="store_true", help="Also build an editable one-page IDML from this plan")
    parser.add_argument("--embed-images", action="store_true", help="With --idml, make an additional self-contained export copy")
    args = parser.parse_args()
    require(not args.embed_images or args.idml, "--embed-images requires --idml")
    plan_path = args.plan.resolve()
    plan = json.loads(plan_path.read_text(encoding="utf-8-sig"))
    validate(plan, plan_path.parent)
    if args.check:
        print(f"Validated {len(plan['items'])} items for {plan['page']['id']}")
        return
    template = Path(__file__).resolve().parents[1] / "assets" / "place-page.jsx"
    source = template.read_text(encoding="utf-8")
    token = "/* INSERT_PAGE_PLAN */ null"
    require(source.count(token) == 1, "Placement template is missing its plan slot")
    # A JSON object literal is valid ES3 when serialized with quoted keys and ASCII escapes.
    script = source.replace(token, json.dumps(plan, ensure_ascii=True, allow_nan=False))
    out = plan_path.with_name(plan_path.stem + "-place.jsx")
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=out.parent, delete=False) as temp:
        staged = Path(temp.name)
        try:
            temp.write(script)
            temp.flush()
        except BaseException:
            staged.unlink(missing_ok=True)
            raise
    try:
        os.replace(staged, out)
    finally:
        staged.unlink(missing_ok=True)
    print(out)
    if args.idml:
        from plan_idml import PageLayout
        target = plan_path.with_name(plan_path.stem + "-editable.idml")
        PageLayout(plan, plan_path.parent).save(target)
        print(target)
        if args.embed_images:
            export = plan_path.with_name(plan_path.stem + "-embedded.idml")
            PageLayout(plan, plan_path.parent, embedded=True).save(export)
            print(export)


if __name__ == "__main__":
    try:
        main()
    except (KeyError, TypeError, ValueError, OSError) as exc:
        print(f"Page handoff: {exc}", file=sys.stderr)
        sys.exit(2)
