"""F1.1 — pipeline overview: question -> instrument -> result -> next question.

One banner: the report's sections as stages, the raised question on each
arrow, the frozen-rules band with the gates underneath, the cards as the
sink. Doubles as a visual table of contents; claims live in section titles.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

import figstyle as st

st.apply_rc()

NODES = [  # (x-center, section, title, subtitle)
    (0.075, "§4", "primary\ncoordinate", "blind 6-input SR\n→ recurrent $f_1$"),
    (0.215, "§5", "saturation", "$\\eta$ ladder · subsets\namplitude control"),
    (0.355, "§6", "second\ncoordinate", "residual SR → $f_2$\ninteraction test"),
    (0.495, "§7", "level sets", "joint pair is the\ncoordinate system"),
    (0.635, "§8", "decoder\nview", "agreement + the\nridge (negative)"),
    (0.775, "§9", "code\nstructure", "split, not\nduplicated"),
    (0.925, "§10", "atlas", "11 cards\n10/11 primarily\ninterpreted"),
]
QUESTIONS = [
    "does $f_1$ account\nfor the latent?",
    "what is in\nthe residual?",
    "coordinate system,\nor good fit?",
    "holds outside the\nparameter domain?",
    "property of latent,\nor of the code?",
    "",
]
GATES = [(0.215, "G1 · G2"), (0.355, "G3"), (0.495, "G4a"), (0.635, "G4b")]

fig, ax = plt.subplots(figsize=(st.FULL_W, 1.72))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")

NODE_Y, NODE_H, NODE_W = 0.42, 0.44, 0.115
for i, (xc, sec, title, sub) in enumerate(NODES):
    last = i == len(NODES) - 1
    fc = "#e8effb" if not last else "#1c5cab"
    tc = st.INK if not last else "white"
    box = FancyBboxPatch((xc - NODE_W / 2, NODE_Y - NODE_H / 2), NODE_W,
                         NODE_H, boxstyle="round,pad=0.008,rounding_size=0.012",
                         facecolor=fc, edgecolor="none", mutation_aspect=0.35)
    ax.add_patch(box)
    tl = title.splitlines()
    if len(tl) == 2:
        ax.text(xc, NODE_Y + 0.135, f"{sec}  {tl[0]}", ha="center",
                va="center", fontsize=6.6, color=tc, weight="bold")
        ax.text(xc, NODE_Y + 0.060, tl[1], ha="center", va="center",
                fontsize=6.6, color=tc, weight="bold")
    else:
        ax.text(xc, NODE_Y + 0.100, f"{sec}  {tl[0]}", ha="center",
                va="center", fontsize=6.6, color=tc, weight="bold")
    ax.text(xc, NODE_Y - 0.095, sub, ha="center", va="center", fontsize=5.4,
            color=tc if last else st.SECONDARY, linespacing=1.25)

for i in range(len(NODES) - 1):
    x0 = NODES[i][0] + NODE_W / 2 + 0.006
    x1 = NODES[i + 1][0] - NODE_W / 2 - 0.006
    ax.annotate("", (x1, NODE_Y), (x0, NODE_Y),
                arrowprops=dict(arrowstyle="-|>", color=st.SECONDARY, lw=0.9))
    if QUESTIONS[i]:
        ax.text((x0 + x1) / 2, NODE_Y + 0.315, QUESTIONS[i], ha="center",
                va="center", fontsize=5.2, style="italic",
                color=st.SECONDARY, linespacing=1.2)

# input stub
ax.text(0.004, 0.93, "two $\\beta$-VAE checkpoints · 11 latents · "
        "raw $\\theta$ only, no derived combinations (§2–§3)",
        fontsize=6.2, color=st.INK, ha="left", va="center")

# frozen-rules band; gates sit on the dotted connectors above it
band_y = 0.045
ax.add_patch(FancyBboxPatch((0.018, band_y - 0.038), 0.964, 0.082,
             boxstyle="round,pad=0.004,rounding_size=0.008",
             facecolor="none", edgecolor=st.BASELINE, linewidth=0.8,
             mutation_aspect=0.35))
ax.text(0.5, band_y + 0.003,
        "§3  rules frozen before unblinding · validated on the amplitude "
        "positive control first · every instrument ships its null (§11)",
        fontsize=5.6, color=st.SECONDARY, va="center", ha="center")
for gx, glab in GATES:
    ax.plot([gx + 0.045, gx + 0.045],
            [band_y + 0.048, NODE_Y - NODE_H / 2 - 0.015],
            color=st.BASELINE, lw=0.6, ls=(0, (2, 2)))
    ax.text(gx + 0.045, 0.168, glab, fontsize=5.6, color=st.INK,
            ha="center", va="center", weight="bold",
            bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                      edgecolor="none"))

st.save(fig, "F1_1_pipeline")
