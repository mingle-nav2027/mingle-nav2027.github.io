#!/usr/bin/env python3
"""Generate index.html and gallery.html for the MINGLE project page."""
import os, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

VIEWS = [
    ("third", "Third-person"),
    ("dashboard", "Onboard dashboard"),
    ("fpv_rgb", "Ego RGB"),
    ("fpv_depth", "Ego depth"),
    ("bev", "BEV occupancy"),
]

# name, title, family, outcome, description
SCENARIOS = [
    ("corridor_successful_trial_17m_01", "Head-on pass, 1.7 m corridor", "corridor", "success",
     "A clean head-on encounter in the wider corridor. The robot commits to one side well before the pedestrian arrives and holds that offset through the pass."),
    ("corridor_half_successful_trial_12m_01", "Head-on pass, 1.2 m corridor (trial 1)", "corridor", "partial",
     "The same behaviour in a passage barely wider than two bodies. Logged as a partial success: the robot gets through, but with far less room to spare."),
    ("corridor_half_successful_trial_12m_02", "Head-on pass, 1.2 m corridor (trial 2)", "corridor", "partial",
     "A second run of the 1.2 m head-on encounter with a different starting offset, again logged as a partial success."),
    ("corridor_failed_trial_12m_01", "Head-on pass, 1.2 m corridor — failure", "corridor", "failure",
     "A failed run in the tightest corridor. Shown as recorded: at this width the policy does not always resolve the encounter."),
    ("left_turn_corridor", "Left turn in a corridor", "turn", "success",
     "A turn taken while the pedestrian approaches, the case where a velocity tracker tends to overshoot into the wall."),
    ("corridorr_left_turn_2", "Left turn in a corridor (trial 2)", "turn", "success",
     "A second corridor turn, entered at a different speed and heading."),
    ("intersection_robot_yield", "Occluded intersection — robot yields", "intersection", "success",
     "The side corridor is hidden by the corner until late. When the pedestrian appears the robot yields by default and lets them cross first."),
    ("intersection_human_yield", "Occluded intersection — human waves the robot through", "intersection", "success",
     "The same blind corner, but the person stops and motions the robot on. The policy reads that whole-body motion and resumes walking, which a 2D position alone would not convey."),
    ("intersection_failed", "Occluded intersection — failure", "intersection", "failure",
     "A failed intersection run. The corner leaves little time between first sight of the pedestrian and the crossing point."),
    ("intersection_failed_2", "Occluded intersection — failure (long run)", "intersection", "failure",
     "A longer failed run at the blind corner, kept uncut so the full approach and recovery are visible."),
    ("overtake_obstacle_human_front", "Overtake past an obstacle, person ahead", "overtake_obs", "success",
     "The lane is narrowed by an obstacle with the pedestrian ahead of the robot. It closes on the walker and passes on the free side, drawing its arms in as the gap tightens."),
    ("overtake_obstacle_human_back", "Overtake past an obstacle, person behind", "overtake_obs", "success",
     "The same narrowed lane with the person entering from behind the robot."),
    ("overtake_obstacle_spacious", "Overtake past an obstacle, wide lane", "overtake_obs", "success",
     "The obstacle with room to spare on either side — the easier end of the overtaking family."),
    ("overtake_obstacle_very_long", "Overtake past an obstacle, long corridor", "overtake_obs", "success",
     "An extended run down the corridor, with the robot closing, passing and settling back onto its line."),
    ("overtake_slow_stop_first", "Overtake a slower walker", "overtake_slow", "success",
     "The pedestrian walks the same way at roughly a third of the robot's speed, so the robot must close, wait for room and then pass."),
    ("overtake_slow_fail", "Overtake a slower walker — failure", "overtake_slow", "failure",
     "A failed overtake of a slow walker, included so the limits of the policy are visible alongside the successes."),
    ("adversarial_corridor_blocking", "Adversarial corridor blocking", "adversarial", "stress",
     "A stress test outside the evaluation protocol: the person repeatedly steps into the robot's path instead of cooperating."),
]

GROUPS = [
    ("corridor", "Head-on corridor encounters",
     "Two bodies in a passage barely wider than both. The policy picks a side early and shapes the body to fit the room that is left."),
    ("turn", "Corridor turns",
     "Turning while a pedestrian approaches — where a general velocity tracker overshoots into the wall at comparable speed."),
    ("intersection", "Occluded intersections",
     "A side corridor hidden by a corner until the robot is about 3 m out. The same scene produces two different social responses."),
    ("overtake_obs", "Overtaking around an obstacle",
     "A lane narrowed by furniture, with a pedestrian to get past inside the remaining space."),
    ("overtake_slow", "Overtaking a slower walker",
     "A pedestrian moving the same way at roughly 0.3 m/s, so the robot has to close and choose a moment to pass."),
    ("adversarial", "Adversarial and stress tests",
     "Encounters outside the evaluation protocol, where the person actively works against the robot."),
]

OUTCOME_LABEL = {"success": "Success", "partial": "Partial", "failure": "Failure", "stress": "Stress test"}

NAV = """  <nav class="nav">
    <div class="nav-inner">
      <a class="nav-brand" href="index.html">MINGLE</a>
      <div class="nav-links">
{links}
      </div>
    </div>
  </nav>
"""

def nav(links):
    return NAV.format(links="\n".join(
        '        <a href="%s">%s</a>' % (h, t) for h, t in links))

def head(title, desc, css_extra=""):
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<meta name="description" content="%s">
<meta property="og:title" content="%s">
<meta property="og:description" content="%s">
<meta property="og:type" content="website">
<meta property="og:image" content="https://mingle-nav2027.github.io/static/images/teaser.jpg">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>&#129302;</text></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="static/css/style.css">%s
</head>
<body>
""" % (html.escape(title), html.escape(desc), html.escape(title), html.escape(desc), css_extra)

def card(s, base_prefix="static/videos"):
    name, title, family, outcome, desc = s
    views = "\n".join(
        '            <button type="button" data-view="%s" aria-pressed="%s">%s</button>'
        % (v, "true" if i == 0 else "false", label)
        for i, (v, label) in enumerate(VIEWS))
    return """      <article class="vcard" data-base="%s/%s" data-tags="%s %s">
        <div class="vstage">
          <video muted loop playsinline preload="none" controls poster="%s/%s/third.jpg"></video>
          <span class="loading">loading</span>
        </div>
        <div class="vbody">
          <div class="vhead">
            <h3 class="vtitle">%s</h3>
            <span class="tag %s">%s</span>
          </div>
          <p class="vdesc">%s</p>
          <div class="views" role="group" aria-label="Camera view">
%s
          </div>
        </div>
      </article>""" % (base_prefix, name, family, outcome, base_prefix, name,
                       html.escape(title), outcome, OUTCOME_LABEL[outcome],
                       html.escape(desc), views)

FOOTER = """  <footer>
    <div class="wrap">
      <p>MINGLE &middot; whole-body humanoid social navigation. Page and media are part of an anonymous submission.</p>
      <p><a href="index.html">Overview</a> &middot; <a href="gallery.html">Video gallery</a> &middot; <a href="static/paper/MINGLE_ICRA2027.pdf">Paper (PDF)</a></p>
    </div>
  </footer>
  <script src="static/js/main.js"></script>
</body>
</html>
"""

# ----------------------------------------------------------------- index.html

FEATURED = ["corridor_successful_trial_17m_01", "intersection_robot_yield",
            "intersection_human_yield", "overtake_obstacle_human_front",
            "overtake_slow_stop_first", "adversarial_corridor_blocking"]
by_name = {s[0]: s for s in SCENARIOS}

index = head(
    "MINGLE: Whole-Body Humanoid Social Navigation",
    "MINGLE learns whole-body humanoid social navigation from paired egocentric perception and motion-captured human actions, deployed zero-shot on a Unitree G1.")

index += nav([("#abstract", "Abstract"), ("#video", "Video"), ("#method", "Method"),
              ("#hardware", "Real robot"), ("#simulation", "Simulation"),
              ("gallery.html", "All clips"), ])

index += """
  <header class="hero">
    <div class="wrap">
      <span class="venue">Anonymous submission &middot; ICRA 2027</span>
      <h1><span class="mark">MINGLE</span>: Learning Whole-Body Humanoid Social Navigation</h1>
      <p class="subtitle">from Paired Egocentric Perception and Motion-Captured Actions</p>
      <p class="authors">Anonymous Authors</p>
      <p class="affil">Paper under double-blind review &middot; all media recorded on a Unitree&nbsp;G1</p>
      <div class="btn-row">
        <a class="btn" href="static/paper/MINGLE_ICRA2027.pdf">Paper (PDF)</a>
        <a class="btn secondary" href="#video">Supplementary video</a>
        <a class="btn secondary" href="gallery.html">All 17 robot clips</a>
        <span class="btn disabled">Code &amp; dataset &mdash; coming soon</span>
      </div>
    </div>
  </header>

  <section id="teaser" style="border-top:none;padding-top:8px">
    <div class="wrap">
      <figure class="figure">
        <img src="static/images/teaser.jpg" alt="MINGLE passing a pedestrian in a 1.3 m corridor: the robot shows intention, rotates and closes its arms to make room, then resumes walking.">
        <figcaption><b>Whole-body social behaviour learned from human demonstrations.</b> A real encounter in a 1.3&nbsp;m passage, labelled with the robot's forward speed. MINGLE first commits to one side to show its intention, then slows to a stop while rotating its body and closing its arms to make room, and resumes walking once the pedestrian has passed.</figcaption>
      </figure>
    </div>
  </section>

  <section id="abstract" class="alt">
    <div class="wrap narrow">
      <h2>Abstract</h2>
      <p>Social navigation requires more than collision avoidance: a robot must move in ways people can anticipate and respond to. Existing approaches largely reduce navigation to a 2D path executed through velocity commands. For humanoids, this abstraction overlooks articulated geometry, legible whole-body motion, and biped locomotion dynamics.</p>
      <p>We propose <b>MINGLE</b>, which learns whole-body humanoid social navigation from paired human demonstrations: egocentric RGB-D records what the navigator perceives, while motion capture records the whole-body action taken in response. Using a portable capture rig, we collect <b>272 episodes</b> across five interaction families and retarget the motions to a Unitree&nbsp;G1. A geometry- and pedestrian-conditioned diffusion policy combines a history bird's-eye view of scene geometry with the pedestrian's articulated motion to predict short-horizon whole-body actions and longer-horizon navigation waypoints, executed by a general-purpose whole-body controller.</p>
      <p>Experiments in simulation and on a real Unitree&nbsp;G1 show that MINGLE improves safety and navigation efficiency over conventional velocity-based social navigation, enabling the humanoid to negotiate shared space through whole-body motion.</p>
      <div class="cards" style="margin-top:28px">
        <div class="card"><div class="num">272</div><p>demonstration episodes, 66k frames, paired egocentric RGB-D and full-body motion capture</p></div>
        <div class="card"><div class="num">29 DoF</div><p>whole-body joint targets plus root motion, predicted directly instead of a 2D twist</p></div>
      </div>
    </div>
  </section>

  <section id="video">
    <div class="wrap narrow">
      <h2>Supplementary video</h2>
      <p class="lede">Two and a half minutes covering the capture rig, the policy and the hardware results. Captioned on screen; the clip carries no audio.</p>
      <div class="vstage" style="--ar:854/480;border-radius:var(--radius);overflow:hidden;border:1px solid var(--border)">
        <video controls playsinline preload="metadata" poster="static/videos/mingle_overview.jpg" src="static/videos/mingle_overview.mp4"></video>
      </div>
      <p class="caption">This is the anonymous accompanying video submitted with the paper. Faces are blurred throughout and it has no audio track.</p>
    </div>
  </section>

  <section id="method" class="alt">
    <div class="wrap">
      <h2>How MINGLE works</h2>
      <p class="lede">Capture human social navigation, turn it into humanoid demonstrations, and learn whole-body reactions from it.</p>
      <figure class="figure">
        <img src="static/images/method.jpg" alt="MINGLE overview: demonstrations captured with a MoCap suit and chest stereo camera are retargeted to the G1; at runtime a BEV occupancy branch and an SMPL actor branch condition a diffusion transformer that denoises whole-body action chunks, selected by a critic and executed through SONIC.">
        <figcaption><b>Overview of MINGLE.</b> Human demonstrations captured with a MoCap suit and a chest-mounted stereo camera are retargeted onto the G1. At runtime the policy consumes a history BEV occupancy map and a window of estimated pedestrian pose, and denoises several 30-frame whole-body chunks in parallel. After real-time chunking and critic rating, the best chunk is executed with SONIC, giving closed-loop deployment in different scenes.</figcaption>
      </figure>
      <div class="steps">
        <div class="step">
          <div class="k">1 &middot; Capture</div>
          <h4>Human experience, recorded as it happens</h4>
          <p>One operator wearing an Xsens suit and carrying a ZED&nbsp;2i at chest height walks through corridors, doorways, intersections and overtaking encounters. No external cameras, no markers, no map &mdash; the rig can be carried into an arbitrary scene.</p>
        </div>
        <div class="step">
          <div class="k">2 &middot; Retarget</div>
          <h4>Human motion into humanoid demonstrations</h4>
          <p>The demonstrator's whole-body motion is retargeted to a 29-DoF Unitree&nbsp;G1, and the other person's articulated pose is recovered from the same egocentric video. Each episode pairs the observed scene with a robot-executable action and the motion it responds to.</p>
        </div>
        <div class="step">
          <div class="k">3 &middot; Learn</div>
          <h4>A geometry- and pedestrian-conditioned diffusion policy</h4>
          <p>A diffusion transformer denoises one-second chunks of joint targets and root motion, conditioned on a history BEV occupancy map, the pedestrian's pose tokens and the robot's own recent state. A critic scores parallel samples; SONIC tracks the winner at 50&nbsp;Hz.</p>
        </div>
      </div>
    </div>
  </section>

  <section id="hardware">
    <div class="wrap">
      <h2>On the real robot</h2>
      <p class="lede">Four interaction families on a Unitree G1, with a person walking of their own accord. Switch between the third-person camera, the onboard dashboard, and the raw egocentric streams the policy actually sees.</p>
      <div class="video-grid">
"""
index += "\n".join(card(by_name[n]) for n in FEATURED)
index += """
      </div>
      <p class="caption" style="margin-top:20px"><b>Every clip carries five synchronized views.</b> <i>Third-person</i> is the external recording of the trial; <i>onboard dashboard</i> combines the egocentric streams with the policy's own BEV maps and telemetry; <i>ego RGB</i> and <i>ego depth</i> are the ZED 2i streams; <i>BEV occupancy</i> is the history map the policy is conditioned on. <a href="gallery.html">See all 17 clips, including the failures &rarr;</a></p>

      <h3 style="margin-top:44px">Learned social behaviours</h3>
      <figure class="figure">
        <img src="static/images/hardware_rollout.jpg" alt="Hardware rollouts: passing in a wide corridor, an occluded intersection, overtaking around an obstacle, and overtaking a slower walker, plus the two intersection responses.">
        <figcaption><b>Whole-body social behaviours on hardware.</b> Each coloured group is one encounter type on the Unitree G1, read left to right in time: passing in a wide corridor, an occluded intersection, overtaking around an obstacle, and overtaking a slower walker. The two panels at right expand the intersection into the two responses the policy produces there &mdash; yielding by default when the pedestrian appears, and reading the person's motion as an invitation to proceed.</figcaption>
      </figure>

    </div>
  </section>

  <section id="simulation" class="alt">
    <div class="wrap">
      <h2>Simulation</h2>
      <p class="lede">The four encounter types, rebuilt from primitive geometry so the same situations can be replayed in the simulator.</p>
      <figure class="figure">
        <img src="static/images/scenarios.jpg" alt="Four simulated evaluation scenarios shown top-down: a 1.5 m corridor, a 1.5 m overtake, a 0.7 m doorway and a 1.5 m intersection.">
        <figcaption><b>Four simulated evaluation scenarios.</b> Each panel is a top-down view labelled with its passage width; the red arrow is the pedestrian's scripted walking direction. They span a head-on corridor encounter, overtaking a slow pedestrian, a crossing at an occluded intersection, and a 0.7&nbsp;m doorway that only one of the two can pass at a time.</figcaption>
      </figure>


      <div style="margin-top:36px;max-width:760px">
        <div class="vstage" style="--ar:16/9;border-radius:var(--radius);overflow:hidden;border:1px solid var(--border)">
          <video controls muted loop playsinline preload="none" poster="static/videos/sim/sim_corridor_ours.jpg" src="static/videos/sim/sim_corridor_ours.mp4"></video>
        </div>
        <p class="caption"><b>MINGLE in the simulated corridor.</b> The policy rotates its torso to make room rather than holding the centre line until the last moment.</p>
      </div>


    </div>
  </section>


"""
index += FOOTER

# --------------------------------------------------------------- gallery.html

gallery = head(
    "MINGLE — video gallery",
    "All 17 Unitree G1 hardware clips from MINGLE, each with third-person, onboard dashboard, egocentric RGB-D and BEV occupancy views.")

gallery += nav([("index.html", "Overview"), ("index.html#method", "Method"),
                ("index.html#hardware", "Real robot"), ("gallery.html", "All clips"),
                ("static/paper/MINGLE_ICRA2027.pdf", "Paper")])

gallery += """
  <header class="hero" style="padding-bottom:12px">
    <div class="wrap narrow">
      <h1 style="font-size:clamp(28px,4.4vw,42px)">Video gallery</h1>
      <p class="subtitle" style="font-size:clamp(17px,2.1vw,21px)">Every hardware clip we recorded &mdash; %d encounters on the Unitree&nbsp;G1, successes and failures alike, each with five synchronized views.</p>
    </div>
  </header>

  <section style="border-top:none;padding-top:8px">
    <div class="wrap">
      <div class="filters" role="group" aria-label="Filter clips">
        <button type="button" data-filter="all" aria-pressed="true">All</button>
        <button type="button" data-filter="corridor" aria-pressed="false">Corridor</button>
        <button type="button" data-filter="turn" aria-pressed="false">Turns</button>
        <button type="button" data-filter="intersection" aria-pressed="false">Intersection</button>
        <button type="button" data-filter="overtake_obs" aria-pressed="false">Overtake (obstacle)</button>
        <button type="button" data-filter="overtake_slow" aria-pressed="false">Overtake (slow walker)</button>
        <button type="button" data-filter="adversarial" aria-pressed="false">Adversarial</button>
        <button type="button" data-filter="success" aria-pressed="false">Successes</button>
        <button type="button" data-filter="failure" aria-pressed="false">Failures</button>
      </div>
      <p class="caption" style="margin:-16px 0 26px">
        <b>Views.</b> <i>Third-person</i> &mdash; the external recording of the trial.
        <i>Onboard dashboard</i> &mdash; egocentric streams with the policy's BEV maps and live telemetry.
        <i>Ego RGB</i> / <i>ego depth</i> &mdash; the chest-mounted ZED 2i streams.
        <i>BEV occupancy</i> &mdash; the history occupancy map the policy is conditioned on.
        The onboard views cover the interaction window, so they are shorter than the third-person recording.
      </p>
""" % len(SCENARIOS)

for key, title, sub in GROUPS:
    members = [s for s in SCENARIOS if s[2] == key]
    gallery += """
      <div data-group="%s">
        <h2 class="group-title">%s <span class="count">%d clip%s</span></h2>
        <p class="group-sub">%s</p>
        <div class="video-grid">
%s
        </div>
      </div>
""" % (key, html.escape(title), len(members), "" if len(members) == 1 else "s",
       html.escape(sub), "\n".join(card(s) for s in members))

gallery += """    </div>
  </section>

"""
gallery += FOOTER

open(os.path.join(ROOT, "index.html"), "w").write(index)
open(os.path.join(ROOT, "gallery.html"), "w").write(gallery)
print("wrote index.html (%d bytes) and gallery.html (%d bytes)" % (len(index), len(gallery)))
