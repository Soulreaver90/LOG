# Controller hand fixes of r12 gi frames. Ops: ("row", y, x, "letters"), "_" keeps the pixel;
# ("copy", src_key, y0, y1, dx, dy, mirror); ("armor", y, x, "mask/rows", {armor index: letter}).
# Letters: K outline, P/Q/R gi purple dark/mid/light, N navy, r/x sash red/dark, B/b wristband, S/s/t/u/d skin light to dark,
# h/j brown outline, o/O shoe dark/light, W white, H dark gray, . transparent.

# Revert 21.d.3: the armor body is the base idle body at screen x+8; the gi drew the sash 1 row low.
# Rows 19-23 come from the approved base idle golden (157.0.0.0), so the sash stays on row -2 into the base idle.
REVERT = {f"{s}.21.{d}.3": [("copy", "157.0.0.0", 19, 23, 8, 0, False)] for s in (158, 159) for d in (0, 1, 2)}

# Front flying 12.0.i (base, 4 frames alike). Owner 5:03 PM: the legs trail behind the head (armor gray boots,
# rows 4-9, above the hair) and the arms reach forward under the body (rows 21-28). r12 had them swapped in color:
# brown shoes and purple legs at the top, skin arms with 2-px bands and fists at the bottom, the chest V between.
SHOE = {10: "O", 11: "O", 12: "o", 13: "o", 9: "O", 2: "O"}      # armor boot grays -> gi shoe (top, far end)
PANTS = {10: "Q", 11: "Q", 12: "P", 13: "P", 9: "Q", 2: "Q"}     # boot top -> gi pants (gi shoes are shorter)
FLY = [("armorc", 4, 6, 2, 14, SHOE), ("armorc", 7, 9, 2, 14, PANTS),   # per frame: only the armor boot pixels
       ("row", 21, 3, "hs"), ("row", 21, 12, "sh"),
       ("row", 22, 2, "htSP"), ("row", 22, 11, "PSth"),
       ("row", 23, 2, "htSNPtstPNSth"),
       ("row", 24, 2, "htSh"), ("row", 24, 11, "hSth"),
       ("row", 25, 2, "hBbh"), ("row", 25, 11, "hbBh"),
       ("row", 26, 2, "hSsh"), ("row", 26, 11, "hsSh"),
       ("row", 27, 2, "htsh"), ("row", 27, 11, "hsth"),
       ("row", 28, 3, "hh"), ("row", 28, 12, "hh")]

# Lying 3.d.3 (all forms, all dirs alike). Owner 5:02 PM: the gray at the far left is his hand in front of his face
# (arm bent, catching his head); the gray at the bottom middle is his other arm lying along the body, not a foot.
# The feet are the raised one (top middle) and the far right one. The sash ran the whole torso on row 27: it now
# crosses the hip (x19-20, rows 25-27). The lower arm: skin forearm (rows 29-30, x12-16), 2-px band, skin hand.
LYING = [("row", 25, 19, "xx"), ("row", 26, 19, "rr"), ("row", 27, 12, "NPQQQPPxxQP"),
         ("row", 28, 18, "htth"),
         ("row", 29, 12, "tSSSsBSSst"),
         ("row", 30, 12, "sttttbsSth"),
         ("row", 31, 12, "hhhhhhhhh")]   # owner 5:11 PM: the arm 1 px thicker (skin rows 29-30, outline row 31)
# Base hand at the face: the band covered the whole hand. Only 2 band pixels at the wrist (x4), the rest skin.
FACE_HAND = [("row", 29, 1, "hSsBh"), ("row", 30, 2, "htb")]

EDITS = {
    # Front run 13.0.3: the armor body is 13.0.1 mirrored (4 px differ, all in row 17), so mirror the gi body of 13.0.1.
    "157.13.0.3": [("copy", "157.13.0.1", 18, 31, 0, 0, True),
                   ("row", 17, 0, ".hhBhhhuuuhuth..")],
    # 13.0.0 / 13.0.2 (owner 5:04 PM): r12 is right, the arm crosses in front of the body as he charges. Only the
    # hand behind his head (the armor glove, gray at the hair edge) becomes skin.
    "157.13.0.0": [("row", 9, 14, "t"), ("row", 10, 14, "St"), ("row", 11, 15, "h")],
    "157.13.0.2": [("row", 12, 1, "t")],
    # SSJ 158: the armor body is the base armor body 1 px left (rows 19 down), so the base fixes and the owner's
    # front walk frames move in at dx -1. SSJ2 159 holds the 158 body at its own screen position (+8 when its
    # record dx is -8; 13.0.3 sits 1 px right of 158, at the base position).
    # 158.13.0.3 (owner 5:07 PM: 13.0.1 and 13.0.3 are mirrors): the SSJ armor 13.0.3 is 158 13.0.1 mirrored at
    # dx -2 (rows 17-31, 14 px differ), so mirror the SSJ gi 13.0.1 the same way, as base does at dx 0.
    "158.13.0.3": [("copy", "158.13.0.1", 18, 31, -2, 0, True), ("row", 17, 0, "hhth"),   # row 17: arm only, chin kept
                   ("row", 18, 0, "h"), ("row", 19, 0, "h")],   # owner 5:15 PM: keep the arm's 2 outline pixels the mirror pushed off the edge
    "158.1.0.0": [("copy", "157.1.0.0", 19, 31, -1, 0, False)],
    "158.1.0.2": [("copy", "157.1.0.2", 19, 31, -1, 0, False)],
    "159.13.0.3": [("copy", "157.13.0.3", 18, 31, 0, 0, False)],
    "159.1.0.0": [("copy", "158.1.0.0", 19, 31, 8, 0, False)],
    "159.1.0.2": [("copy", "158.1.0.2", 19, 31, 8, 0, False)],
    # 8.0.3 (owner 3:19 PM): keep the fist. Under the neck is bare chest: a skin V with shadow, as the front goldens.
    # The kicked foot is lifted: the armor boot (rows 26-31) is mostly the sole, so the brown shoe moves up and the
    # dark sole sits under it.
    "157.8.0.3": [("row", 20, 14, "NPtst"),
                  ("row", 21, 15, "PNtN"),
                  ("row", 26, 18, "oOo"),
                  ("row", 27, 14, "NPoOOooo"),
                  ("row", 28, 14, "ooOooN"),
                  ("row", 29, 14, "NNNNNN"),
                  ("row", 30, 15, "NNNN"),
                  ("row", 31, 16, "NN")],
    # 8.2.2 side kick: the extended leg (armor rows 19-22, boot x0-5, pants x6-12) was drawn as a skin arm.
    # Pants navy and purple, brown shoe; the white air pixels stay.
    # 8.2.2 (owner 5:27 PM, single/owner_82_1x.png, drawn 4 px right and 2 px up): the front hand rests at the hip
    # (armor brown outline and glove, rows 18-19 x10-13), and the short sash runs down to the right (x11 row 20,
    # x12-13 row 21), with the standing leg. The owner's frame is the fix, aligned to the record.
    "157.8.2.2": [("copy", "file:single/owner_82_1x.png", 0, 31, -4, 2, False)],
    # 16.2.4 flying kick, redone with the owner's 8.2.2 rules (5:31 PM): head and chin untouched (face ends row 16);
    # the front fist (armor glove, rows 12-14 x5-9) is skin, no white; the torso where the chest plate was is gi, with
    # one exposed-chest skin pixel under the chin; the sash follows the bottom of the chest plate, x11-12 on row 17
    # stepping down to x13-16 on row 18; the gi shoe is shorter than the boot (x0-2, the boot's x3-4 are pants);
    # the tucked leg keeps r12 (pants rows 22-23, shoe rows 24-25).
    "157.16.2.4": [("row", 13, 5, "hStb"),
                   ("row", 14, 5, "htShh"),
                   # owner 5:38 PM: the thigh. The armor's dark row above it (row 17 x7-10) is the dark edge; the lit
                   # armor run on row 18 (x8-12) is the top of the thigh in purple.
                   ("row", 17, 7, "NNNNxrPQtPN"),
                   ("row", 18, 0, "oOoNNNNNPQQQPrrrx"),
                   ("row", 19, 0, "oOoNPQQQQQQQQPPN"),
                   ("row", 20, 0, "oooPPPPPPPQPPPPN"),
                   ("row", 21, 0, "oooNNNNNNNNNNNNNN"),
                   # owner 5:36 PM: the tucked foot points left; its shoe is 2 px narrower and 2 px taller (x10-11, rows 22-25)
                   ("row", 22, 10, "oO"), ("row", 23, 10, "oO"), ("row", 24, 10, "ooPN")],
    **{f"157.12.0.{i}": FLY for i in range(4)},
    # 2.0.3: owner 5:03 PM, r12 is fine as is (no edit).
    # 5.0.2 (owner 4:53 PM: "that's his arm attacking"): the left arm reaches down-left from the shoulder (armor blue
    # sleeve x3-6 rows 19-23, glove rows 24-28). The gi is sleeveless: skin arm, wristband, skin fist.
    # Owner 4:55 PM: the gi covers the top of the shoulder (the armor strap row 19): one dark purple row.
    "157.5.0.2": [("row", 18, 4, "NN"),
                  ("row", 19, 3, "PPPP"),
                  *[("row", y, 3, "hSst") for y in range(20, 24)],
                  ("row", 24, 3, "hBbh"),
                  ("row", 25, 3, "hSSsh"),
                  ("row", 26, 3, "hSssh"),
                  ("row", 27, 2, "htssth"),
                  ("row", 28, 4, "hhhh")],
    **{f"{s}.3.{d}.3": LYING + (FACE_HAND if s == 157 else []) for s in (157, 158, 159) for d in (0, 1, 2)},
    # **REVERT dropped (owner 5:11 PM): keep the r12 sash of 21.d.3, 2 px below the chest point as in the other frames.
}
