# PROMPT GUIDE: writing `prompts/<ID>.md`

One file per record, with three sections. `locgen.py` sends the `## PROMPT` section **verbatim** and appends `spec/style.txt` (the shared look) and `spec/rules.txt` (frame, lettering, references, no people, counts). Don't repeat those two files in the prompt; spend the words on this record.

```markdown
# <ID> <view>
## PROMPT
...
## CHECKS
- ...
## CALLOUT PLAN
- <EXACT CALLOUT TEXT>: leader to <target>; box <region>; must not cover <...>
```

`lint` blocks spending when any of these happens:
- the title or callout text appears in PROMPT;
- an `Image N` is missing, or there is an extra one;
- there is no `4:3`;
- there is no `Physical inscriptions` line;
- CHECKS has fewer than 5 items;
- the full prompt is over 32,000 characters.

It warns about ASCII hyphens used as minus signs and about state-edit prompts that don't say "Change only".

---

## 1. PROMPT skeleton: `derive` mode (a new camera)

```
Use case: ChandRush Chapter 01 location reference plate <ID>, <what the view is> at <location>. <One sentence on what this plate establishes and which later views reuse it.>
Asset: one 4:3 landscape scenic image of an empty location, no characters.
Input images:
- Image 1: <identity, e.g. "the approved Lantern Street master, seen from Entry Court towards Food Street">. Use it for: <exact design elements and finish to carry over>. Ignore: its painted title, white annotation words and arrows; <any state or element that must not leak>.
- Image 2: ...
Camera and framing: <the register's camera, made concrete: eye height, distance, direction, angle; what sits screen-left, centre and right; what the frame edges cut; which anchors stay visible>.
Place and construction: <the register's construction, rewritten for this camera, one fitting per sentence, physical sides already converted to screen sides; materials named>.
State at this moment (exact):
1. <object>: <state>, with counts as digits and words ("exactly 4 (four)") ...
2. ...
Physical inscriptions (render exactly, nothing else): "START" on <where, what form, legible size>; "−8" ...   (or: Physical inscriptions: none)
Keep clear and visible: <the places the callouts will point to, and everything the register says must remain visible>.
Light: <the record's light: which lamps are lit, which are unlit; arches and moonline state>.
Do not show: <earlier or later states, look-alike wrong designs, leaks from the references, extra copies>.
```

## 2. PROMPT skeleton: `state-edit` mode (same camera as Image 1)

```
Use case: same-camera state change of Image 1 for ChandRush plate <ID>, <view>.
Asset: one 4:3 landscape scenic image, identical camera to Image 1.
Input images:
- Image 1: the approved plate <parent ID>. Keep its camera, framing, perspective, architecture, materials, colours, lighting and every unchanged object exactly.
Change only:
1. <change, with exact counts and positions>
2. ...
Everything else stays exactly as in Image 1, including <list the things a model might be tempted to change>.
Physical inscriptions after the change (render exactly, nothing else): ...
Keep clear and visible: ...
Do not show: <the parent's old state where it must vanish, half-done transitions>.
```

## 3. Writing rules (they decide whether the image is right first time)

1. **The register is the authority.** Use its exact values and states. When the manuscript or a reference image disagrees, follow the register. If the register contradicts itself, stop and ask.
2. **Resolve sides before writing.**
   - Street left and right are defined from Entry Court looking towards Food Street.
   - Bench left, centre and right are defined standing in the lane facing the right-wall bench.
   - A reverse view swaps the screen sides, not the physical sides.
   - Write *screen* positions for this camera ("screen-left", "on the right of the frame") and check every one against `Ref/CH01-SPATIAL-AUTHORITY-MAP-FINAL.png`.
3. **Counts:** write each count as digits and words, use "exactly", and say what is absent. Use numbered lists for states. Give one fact per sentence.
4. **Minus signs:** use the true minus sign `−` (U+2212) and spell it once ("−8, minus eight"). Never use an ASCII hyphen for a negative value.
5. **Physical inscriptions:** list every piece of real-world lettering (plates, cards, displays, stock-box fronts, carton labels) with where it sits and its form (engraved brass plate, printed card, painted letters, mechanical display). Make each large enough to read at 1024 px.
   - In wide or distant views, follow the manuscript rule: fine numbers are "too distant to read, never wrong". Ask for unreadable small marks instead of tiny text.
6. **References:** for each image, name what to use and what to ignore.
   - The Lantern Street master has a painted title and white annotation words with arrows. **Always** tell the model to ignore them.
   - Masters show their own state and framing. Name the parts that must not leak, such as the master's crooked mirror tiles in a "completed mirror" view.
7. **Callouts are added later.** Don't name them and don't quote their text. In "Keep clear and visible", describe the regions their leaders will point at so the model leaves them open and readable (clear paving, a reachable rim, an empty shelf).
8. **Light states follow the record:**
   - **Unrestored:** main arches and the silver moonline are unlit, metallic and dark; fixed amber task lamps are on.
   - **Restored** (M01-D03, M01-D04, S06-D04, M03-D01): golden arch light on the existing architecture, and the moonline glows wherever the record says so.
9. **Empty location:** no characters, even when callouts mention children, helpers or animals.
10. **No later state in an earlier image:** the manuscript is strict about this. For example, no four −2 wheels before S01-D04, no 9×9 grid before S06-D02, and no V before S06-D04.
11. **Length:** typically 2,500–7,000 characters. Precision matters more than adjectives; the style file already carries the look.
12. **Legible inscriptions at 1K** (learned from the samples):
    - Make every inscription bearer big: give its size as a share of the frame ("each label plate about one tenth of the frame width").
    - Keep to at most three words per line.
    - Letters smaller than about 12 px at 1024 px go soft.
13. **Put every position and rest state in the numbered state list**, not only in the description: heights, which way something points, what rests on what. The model drops details that appear only in prose. For example, a cart handle described as "at waist height" in prose ended up lying on the paving.
14. **Design continuity:** when a fitting already has an approved design in this run, such as the S01-B01 controller, describe that design in every later view where the fitting is visible, even in wides. Attach the plate when the fitting is prominent.

## 4. CHECKS (the QC list for this plate)

Write 6–14 items that a reviewer can verify by zooming:
- every count;
- every inscription string;
- every on/off state;
- screen positions of the key fittings;
- continuity with each attached image;
- the masters' style;
- no lettering beyond the inscriptions;
- no people;
- 4:3 framing with the anchors the register names;
- the "remain visible" items of the register.

## 5. CALLOUT PLAN

For each register callout, give:
- its exact text;
- the leader target, taken from the register's own words;
- the box region (the register's position word, such as lower-left or right-margin);
- what the box must not cover.

`compose` draws exactly the register's texts. This plan is for placing them after the plate exists (`callouts`, `grid`, `compose`).

---

## 6. Known traps by family (from the register, the map and the masters)

**All Lantern Street plates**
- Look: deep indigo timber walls; a cream/pale stone bench top with brass edge and blue supports; pale irregular paving with a wet sheen; brass lamps; glass-globe hanging lanterns; one full moon.
- The right-wall bench runs, from Entry Court towards Food Street: **hook rack → projector kits → timing**. The cube plinth comes after the timing end, opposite the left mirror alcove.

**S01/S02: lift and controller**
- There is exactly one car and one shaft.
- The controller sits *immediately right* of the street opening when facing the lift.
- Its vertical position strip has equal unit spacing: 0 at street floor, negatives down to −8, positives above 0.
- The upper face has a card rail with distinct slots, three separate controls `START`, `HOLD`, `CANCEL LAST CHANGE`, a one-value last-change window and a small card shelf.
- Below that is a lower hinged cover with two red lamps immediately above it.
- The four thumbwheels are in one horizontal row and are visible only when the cover is open (S01-D03/D04).
  - The plate reads `TOTAL CORRECTION −8` / `FOUR EQUAL SETTINGS`.
  - The row reads +2, 0, −1, +3 before the correction and −2 ×4 after it.
- The supply cart is a low four-wheeled timber platform with brass corner straps, a rear handle and closed boxes. One upper lid carries a painted blue-and-gold lamp picture.
- Seen from the lower landing (S02), the cart stands left and the helper space is on the right.

**S03: timing bench (V10 changed the design: do not reuse Draft-02 ideas)**
- The straight rail runs **left to right along the bench** (not front-to-back), from a marked start at the left to a fixed end stop at the right.
- There is one carved bird on one short sliding platform, with a visible hinged neck.
- The **blue** catch and lamp are on the device's **left**; the **gold** catch and lamp are on the **right**.
- Cycle plates read `4` at blue and `6` at gold. There is a numbered beat strip, a start-card slot and a beat counter.
- States:

| Record | Catches | Catch lamps | Card | Counter | Bird |
|---|---|---|---|---|---|
| B01 | down | off | `6` | blank | upright at the start |
| D01 | raised | on | `12` | `12` | upright at the start |
| D02 | raised | on | `12` | `12` | at the right end stop, bowed; start empty |

**S04: projector kits**
- Stock boxes: `45 BLUE GLASS LENSES` on the left, `75 BRASS RINGS` on the right. Lenses are thick polished blue glass discs, not clips. Rings are complete brass circles.
- The sample kit (D01) has 3 lenses in a row on the left and 5 rings on the right, 3 above and 2 below, in separate padded recesses with nothing overlapping.
- The assembled head (D02) has 3 lenses in 3 mounting rings plus 2 side support rings: exactly 5 rings.

**S05: hook rack**
- Cartons, left to right: `348 HOOKS`, `355 HOOKS`, `414 HOOKS`, `525 HOOKS`.
- Wrong cards above them: `5 WORKERS`, `4 WORKERS`, `25 WORKERS`, `9 WORKERS`.
- The rack has a distinctive right brass upright. All seals are intact.
- In D01, the 414 clip is empty, with fine black dust on its pad and on the face-up `25 WORKERS` card lying flat below it. There is no V anywhere on the rack.

**S06: mirror**
- A true-square shallow brass frame, mounted low with a slight backward tilt, in the far-left alcove.
- The warm lamp is on the frame's **left**, the padded tray is **left** and the opaque crate is **right** (facing it from the lane).
- There are 81 tiles in total. The lower-right inner rim is dim and dusty, with **no V until S06-D04**.
- Moon:
  - B01 shows a fragmented reflection of one real moon.
  - D02 shows one continuous reflection.
  - D03 has the moon disc outside the reflected field.

**S07: cube station**
- 64 equal cubes: uneven narrow towers in B01, a solid 4×4×4 block from D01 on.
- Facing the plinth, the five-light panel is on the wall to its **right**, with a separate large down-pull handle beside it.
- Labels from top to bottom: `LIFT`, `RHYTHM`, `SUPPLIES`, `MIRROR`, `CUBE`.
- The flat brass cover is at the plinth's front-right corner, over the moonline joint.
- Handle states:

| Record | Handle |
|---|---|
| B01, D01, D02 | raised |
| D03 | down |
| D04 | down, if visible |

**M01: wides**
- Distant details must be readable or hidden, never wrong.
- M01-D03 is a true reverse: bench and cube are screen-left, mirror screen-right, and the moonline runs along the screen-left edge.

**M02: Gate**
- Copy the master's geometry. The service door is in the left leaf; the equipment exit is farther left beyond the pier.
- The planter is on the left and the bench on the right.
- Modest Mumbai plaster walls and balconies sit at the sides only.

**M03: Food Street**
- The intact bowl lies tipped on its side against the **lower-left outer edge** of the nearest wheel. Its rim touches the wheel without intersecting it, and there are contact shadows.
- One oversized dosa overhangs a small plate at the left counter.
- The trolley carries 16 empty cups in a 4×4 carrier.
- The two-tray table has two empty trays, with the entrance-side tray a little lower.
- The Parade opening is out of frame.
