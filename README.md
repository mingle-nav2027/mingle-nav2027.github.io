# mingle-nav2027.github.io

Project page for **MINGLE: Learning Whole-Body Humanoid Social Navigation from Paired
Egocentric Perception and Motion-Captured Actions** — the site referenced from the paper
as `mingle-nav2027.github.io`.

## Pages

| File | Contents |
| --- | --- |
| `index.html` | Teaser, abstract, supplementary video, method figure, six featured hardware clips, hardware and simulation results, ablations, BibTeX |
| `gallery.html` | All 17 Unitree G1 hardware clips, grouped by interaction family, filterable by family and by outcome |

Both pages are static: no build step, no dependencies beyond the Google Fonts stylesheet.

## Layout

```
index.html
gallery.html
static/
  css/style.css          # light + dark theme, all page styling
  js/main.js             # view switching, viewport-gated playback, filters
  images/*.jpg           # paper figures, rendered from the source PDFs at 220 dpi and trimmed
  paper/MINGLE_ICRA2027.pdf
  videos/
    mingle_overview.mp4  # 2.5 min narrated supplementary video (+ .jpg poster)
    sim/                 # simulated corridor rollout
    <scenario>/          # one folder per hardware trial
      third.mp4          # external camera, face-masked (masked_tps), black bars cropped
      fpv.mp4            # chest-mounted ZED 2i RGB, face-masked (masked_fps), 568x320
      depth_bev.mp4      # ZED 2i depth stacked above the history BEV occupancy map
      *.jpg              # poster frame for each of the above
```

Every clip carries the same three view names, which is what `static/js/main.js` relies on:
a card declares `data-base="static/videos/<scenario>"` and the view buttons swap
`<base>/<view>.mp4` into the single `<video>` element. Clips only start loading when they
scroll into view, and pause when they leave, so the page opens without pulling ~80 MB.

## Source assets

Everything here is derived from `icra27_vis/`:

- **Figures** — `img_pptx_pdf/fig*/**.pdf`, rendered with
  `magick -density 220 <fig>.pdf -fuzz 2% -trim +repage -resize 2000x\> <name>.jpg`.
- **Hardware clips** — `mingle_demo_videos/<scenario>/`, using only scenarios that have
  both `masked_tps.mp4` and `masked_fps.mp4`. Those two were cropped to their picture area
  (`crop=480:480:186:0` for portrait third-person, none for landscape;
  `crop=568:320:142:80` for first-person) and re-encoded with `-crf 22`, audio stripped.
  `depth_bev` is `fpv_depth` scaled to 854x480 `vstack`ed over `bev` scaled to 854x424
  (nearest-neighbour). Posters are single frames at 35 % of each clip.
- **Simulation clip** — `img_pptx_pdf/fig4_sim_comparison/ours_exec30_default.mp4`.
- **Supplementary video** — the ICRA submission video (`ICRA27_6901_VI_i.mp4`).

The onboard views cover the interaction window only, so they are shorter than the
third-person recording of the same trial; they are not frame-synchronized with it.

## Regenerating the pages

`index.html` and `gallery.html` were generated from a small script that holds the scenario
table (title, family, outcome, caption). Editing the HTML directly is fine — it is plain
and self-contained. To add a clip, drop a new `static/videos/<scenario>/` folder with the
three views plus posters and copy an existing `<article class="vcard">` block, changing
`data-base`, `data-tags`, the title, the tag and the caption.

## Publishing

The repository name matches a GitHub Pages user/organization site, so pushing to the
default branch of `https://github.com/mingle-nav2027/mingle-nav2027.github.io` publishes
at `https://mingle-nav2027.github.io/` with no further configuration. `.nojekyll` is
present so that nothing is filtered by Jekyll.

```sh
git remote add origin git@github.com:mingle-nav2027/mingle-nav2027.github.io.git
git push -u origin main
```

Total size is about 105 MB, with the largest single file (the supplementary video) at
18 MB — well inside GitHub's limits.

## Anonymity

The page carries no author names and the paper PDF is the anonymous submission version.
Before pushing, check that the GitHub account used to publish does not identify the
authors, and that no scenario captions or telemetry files added later do either.
