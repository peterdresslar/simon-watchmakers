import marimo

__generated_with = "0.19.11"
app = marimo.App(width="medium", app_title="Tempus, Hora, and Secunda")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import numpy as np
    import altair as alt
    import pandas as pd

    return mo, np


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    *Welcome! If this is your first experience with a marimo notebook, please be aware that you have many options to proceed in a way that suits your curiosity level (or lack thereof) for the Python code itself. You can switch to app mode and simply press play and work with the interactive elements below; or, you could dig into edit mode to explore and even edit the code for yourself. Regardless, all of the code is deisigned to run straight through if you start with simply the run button at the bottom right corner of your screen.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Simon's Watchmakers: Tempus, Hora, and Secunda

    *[Peter Dresslar](https://github.com/peterdresslar), 2026*

    ## Abstract

    Herbert Simon's parable of the watchmakers Hora and Tempus, introduced in The Architecture of Complexity (1962), is one of the most cited arguments for why complex systems tend toward hierarchical, modular organization. Simon's approximate ratio of 4,000x efficiency for modular over monolithic assembly has been widely repeated; however, corrections by Turney (1989) and Saltzer (1996) place it closer to 1,974x, and these corrections appear not to have been broadly absorbed. This notebook presents a computational re-examination of the parable using faithful Python simulations validated against the corrected analytical predictions. Applying Shannon entropy to the simulation, we track the information committed at each assembly event, distinguishing between provisional progress (vulnerable to interruption) and committed bits (permanently banked). This analysis surfaces a more fundamental issue: Simon's model requires an unacknowledged agent—here called Secunda—who performs instantaneous, free, uninterruptible work at every modular ratchet point, converting fragile progress into permanent structure. The number 111, which Simon gives for Hora's required subassemblies, is itself evidence: if modular joining were truly zero-cost, only 100 assembly events would occur, with higher levels completing by automatic cascade. Since Hora's entire advantage over Tempus is attributable to these ratchet events, the parable's applicability to real systems depends on a quantity the model does not address.

    ## Introduction

    Herbert Simon's [*The Architecture of Complexity*](https://link.springer.com/chapter/10.1007/978-1-4899-0718-9_31) (1962) is a foundational work for complexity science. The story introduces a parable of the two watchmakers—Hora and Tempus—along the way to presenting one of the most-cited arguments for why complex systems tend toward hierarchical, modular organization. While the lecture influenced theorists for every decade following its publication, current advances complexity theory and methods lend Simon's work particular resonance.

    Simon's parable begins (with some editing):

    > There once were two watchmakers, named Hora and Tempus, who manufactured very fine watches. Both of them were highly regarded, and the phones in their workshops rang frequently... However, Hora prospered, while Tempus lost his shop. What was the reason?
    >
    > The watches the men made consisted of about 1000 parts each. **Tempus** had so constructed his so that if he had one partly assembled and had to put it down—to answer the phone say—it immediately fell to pieces...
    >
    > **Hora** had designed them so that he could put together subassemblies of ten elements each. Ten of these subassemblies, again, could be put together into a larger subassembly; and a system of ten of the latter constituted the whole watch. Hence, when Hora had to... answer the phone, he lost only a small part of his work, and he assembled his watches in only a fraction of the hours it took Tempus.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    > Suppose the probability that an interruption will occur while a part is being added to an incomplete assembly is *p*. Then the probability that **Tempus** can complete a watch he has started without interruption is (1-p)^1000—a very small number unless p is .001 or less.

    > On the other hand, **Hora** has to complete 111 subassemblies... the probability that he will not be interrupted while completing any one of these is (1-p)^10... if p is about .01... then a straightforward calculation shows that it will take Tempus on the average, about 4000 times as long to assemble a watch as Hora.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    In order to elucidate Simon's parable, the following code presents an implementation in Python. The core classes `Tempus` and `Hora` are designed to be as faithful to the prose as possible, with particular care toward making sure the core number of subassemblies, 111, is precisely reached by Hora.

    Using these classes, we proceed with both a visualization and a simulation.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Fundamental control

    The central variable of the narrative is the probability, $p$, that the watchmakers will be interrupted on any given step in assembly. It can be adjusted with the slider below: the default of $0.01$ is taken from the story.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    probability_p_times_10000 = mo.ui.slider(0, 1000, value=100, label="Update probability p. Press submit to process updates")
    form = probability_p_times_10000.form()
    form
    return (form,)


@app.cell(hide_code=True)
def _(form):
    probability = .01
    if form.value is not None:
        probability = form.value / 10000
    print(f"Probability p of an interruption: {probability}")
    return (probability,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Core Classes

    These are the implementing classes for both watchmakers.
    """)
    return


@app.cell(hide_code=True)
def _(np):
    # Hora and Tempus

    HORA_PARTS_PER_SUB = 10           # Number of parts for each Hora component
    K = HORA_PARTS_PER_SUB            # Shorter version of that, matches Saltzer 1999
    TEMPUS_PARTS_PER_WATCH = 1000     # Poor Tempus

    def log_2T(p):
        return np.log2(1 / (1 - p))   # our "constant" information function
                                      # returns bits per step (remains constant WRT p)

    class Hora:
        """Hora the watchmaker: builder of modular watches.

        State tracks progress at three levels, plus inventory of completed
        pieces waiting to be joined at the next level up.

        There is a model problem, here, but we have kept it in order to match with published verifying sources.
        """

        def __init__(self):
            self.name = "Hora"
            # Progress within current assembly at each level (0..K-1)
            self.parts = 0          # level 0: elements
            self.subassemblies = 0     # level 1: joining subassemblies
            self.larger_subs = 0    # level 2: joining "larger" subassemblies

            # Inventory: completed pieces ready for the next level
            self.subassemblies_ready = 0       # completed subassemblies for current larger subassembly (0..10)
            self.larger_subs_ready = 0       # completed larger subassemblies for current watch (0..10)

            self.currently_working_on = 0
                # 0 -->  "elements"
                # 1 -->  "subassemblies of ten elements each"
                # 2 -->  "Ten of these subassemblies could be put together into larger subassembly"
                # 3 -->  *Not a state! Not used.
                #        "[A] system of ten of the latter constituted the whole watch"
                #        NOTE: As we can see the prose depends on the "assembly of assemblies" being entirely free.
                #        See discussion, below.

            # Counters
            self.watches = 0
            self.interrupts = 0
            self.work_lost = 0                      # parts-equivalent
            self.total_steps = 0
            self.all_assemblies_completed = 0       # assemblies at any level, about which Simon says: 
                                                    # "Hora has to complete one hundred eleven subassemblies of ten parts each"

            # === Shannon entropy states ===
            # From the prose:
            # I = -log_2(P_k) = -log_2(T^(-k)) = k * log_2(T)
            # where 
            # T = 1/(1-p)
            # and k is our K, or HORA_PARTS_PER_SUB
            #
            # committed_bits:    permanently banked, immune to interruption.
            #                    increases by K*log_2(T) each time any assembly of K steps completes. 
            #                    Entirely atributable to "Secunda" (see prose)
            #
            # provisional_bits:  current progress that would be lost on interruption.
            #                    equals (the return of) _get_progress() · log_2(T) at the active level.
            self.committed_bits = 0.0
            self.provisional_bits = 0.0

        def _get_progress(self):
            """Return current progress at the active level."""
            if self.currently_working_on == 0:
                return self.parts
            elif self.currently_working_on == 1:
                return self.subassemblies
            else:
                return self.larger_subs

        def _set_progress(self, value):
            """Set progress at the active level."""
            if self.currently_working_on == 0:
                self.parts = value
            elif self.currently_working_on == 1:
                self.subassemblies = value
            else:
                self.larger_subs = value

        def _bank_bits(self, p):
            self.committed_bits += K * log_2T(p)
            self.provisional_bits = 0.0

        def step(self, rng, p):
            self.total_steps += 1
            level = self.currently_working_on

            if rng.random() < p:
                # Interrupted — lose current level's progress. Banked progress is safe.
                self.interrupts += 1
                progress = self._get_progress()
                self.work_lost += progress * (K ** level)
                self._set_progress(0)

                self.provisional_bits = 0.0  # provisional information is lost.

            else:
                # Successful step
                new_progress = (self._get_progress() + 1)
                self._set_progress(new_progress)
                self.provisional_bits = new_progress * log_2T(p)

                if self._get_progress() >= K:
                    # Assembly complete at this level
                    self._set_progress(0)
                    self.all_assemblies_completed += 1   # no matter the level, track an assembly to all_assemblies

                    self._bank_bits(p)   # Bank the entropy

                    if level == 0:
                        # subassembly complete
                        self.subassemblies_ready += 1
                        if self.subassemblies_ready >= K:
                            # 10 subassemblies ready, switch to joining them
                            self.currently_working_on = 1

                    elif level == 1:
                        # Larger assembly complete, consume subassemb
                        self.subassemblies_ready = 0
                        self.larger_subs_ready += 1
                        if self.larger_subs_ready >= K:
                            # 10 larger subs ready, switch to joining them
                            self.currently_working_on = 2
                        else:
                            # Need more subs, back to building parts
                            self.currently_working_on = 0

                    elif level == 2:
                        # Watch complete!
                        self.larger_subs_ready = 0
                        self.watches += 1
                        self.currently_working_on = 0

            return self

        def snapshot(self):
            # return current state as a dict
            return {
                'parts': self.parts,
                'subassemblies': self.subassemblies,
                'subassemblies_ready': self.subassemblies_ready,
                'larger_subs': self.larger_subs,
                'larger_subs_ready': self.larger_subs_ready,
                'currently_working_on': self.currently_working_on,
                'watches': self.watches,
                'interrupts': self.interrupts,
                'work_lost': self.work_lost,
                'total_steps': self.total_steps,
                'all_assemblies_completed': self.all_assemblies_completed,
                'committed_bits': self.committed_bits,
                'provisional_bits': self.provisional_bits,
            }

    class Tempus:
        """Tempus the watchmaker: builder of monolithic watches.

        State tracks Tempus' progress, which is likely to be frustrated.
        """
        def __init__(self):
            self.name = "Tempus"
            self.parts = 0          # 0..TEMPUS_PARTS_PER_WATCH

            # Counters
            self.watches = 0
            self.interrupts = 0
            self.work_lost = 0      # parts lost to interruptions
            self.total_steps = 0        

            # === Shannon entropy tracking ===
            # committed_bits:    zero until a watch finishes, then jumps by
            #                    TEMPUS_PARTS_PER_WATCH × log_2(T).
            # provisional_bits:  current progress × log_2(T). Resets to zero on interruption.
            self.committed_bits = 0.0
            self.provisional_bits = 0.0

        def step(self, rng, p):
            self.total_steps += 1

            if rng.random() < p:
                # Interrupted — lose everything
                self.interrupts += 1
                self.work_lost += self.parts
                self.parts = 0
                self.provisional_bits = 0.0     # all provisional information lost

            else:
                self.parts += 1
                self.provisional_bits = self.parts * log_2T(p)
                if self.parts >= TEMPUS_PARTS_PER_WATCH:
                    # watch --> information
                    self.committed_bits += TEMPUS_PARTS_PER_WATCH * log_2T(p)   # note that this is K for Tempus
                    self.provisional_bits = 0.0
                    self.watches += 1
                    self.parts = 0

            return self

        def snapshot(self):
            # return current state as a dict
            return {
                'parts': self.parts,
                'watches': self.watches,
                'interrupts': self.interrupts,
                'work_lost': self.work_lost,
                'total_steps': self.total_steps,
                'committed_bits': self.committed_bits,
                'provisional_bits': self.provisional_bits,
            }

    t = Tempus()
    h = Hora()
    print(f"Hello, I am {t.name}, a Python implementation of a linear watchmaker.")
    print(f"Hello, I am {h.name}, a Python implementation of a modular watchmaker.")
    return Hora, K, TEMPUS_PARTS_PER_WATCH, Tempus, log_2T


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Visualization

    Here we have a *post facto* visualization, in that the data are run in advance, and then the user is invited to uses the frame slider to "scrub through" those data. Notice that Tempus takes so long to create one watch that in some randomized data generations, he fails to complete a single one.
    """)
    return


@app.cell(hide_code=True)
def _(Hora, Tempus, mo, np, probability):
    # Visualization

    def setup():
        MAX_FRAMES = 1000000
        BASE_TICKS_PER_FRAME = 5

        p_viz = probability
        rng_h = np.random.default_rng()
        rng_t = np.random.default_rng()

        hora_viz = Hora()
        tempus_viz = Tempus()

        snapshots = []

        for frame in range(MAX_FRAMES):
            for _ in range(BASE_TICKS_PER_FRAME):
                hora_viz.step(rng_h, p_viz)
                tempus_viz.step(rng_t, p_viz)

            snapshots.append({
                'frame': frame,
                'step': (frame + 1) * BASE_TICKS_PER_FRAME,
                **{f'h_{k}': v for k, v in hora_viz.snapshot().items()},
                **{f't_{k}': v for k, v in tempus_viz.snapshot().items()},
            })

        mo.md(f"Simulation complete: {MAX_FRAMES} frames × {BASE_TICKS_PER_FRAME} ticks = **{MAX_FRAMES * BASE_TICKS_PER_FRAME:,}** total steps at p={p_viz}")
        return snapshots, MAX_FRAMES

    snapshots, MAX_FRAMES = setup()
    if len(snapshots) > 0:
        print("Visualization data ready.")
    return MAX_FRAMES, snapshots


@app.cell(hide_code=True)
def _(MAX_FRAMES, mo):
    frame_slider = mo.ui.slider(
            start=0, stop=MAX_FRAMES - 1, step=1, value=1 - 1,
            label="Use this control to scrub through visualization data (Note that the notebook cells must first be run).",
            full_width=True,
        )
    frame_slider
    return (frame_slider,)


@app.cell(hide_code=True)
def _(
    K,
    TEMPUS_PARTS_PER_WATCH,
    entropy_switch,
    frame_slider,
    log_2T,
    mo,
    probability,
    snapshots,
):
    f = snapshots[frame_slider.value]
    step = f['step']
    p_disp = probability

    # === Colors ===
    HORA_BLUE = "#4c78a8"
    HORA_ACTIVE = "#6fa8dc"
    HORA_DONE = "#2d5a8a"
    TEMPUS_RED = "#e45756"
    BAR_BG = "#3a3a3e"
    LABEL = "#999"

    def bar(frac, color, w, h=22, active=False):
        pct = max(0, min(100, frac * 100))
        brd = f"2px solid {color}" if active else "1px solid #555"
        return (
            f'<div style="display:inline-block;width:{w}px;height:{h}px;'
            f'background:{BAR_BG};border-radius:3px;border:{brd};'
            f'overflow:hidden;margin:1px;vertical-align:middle;">'
            f'<div style="width:{pct}%;height:100%;background:{color};'
            f'border-radius:2px;"></div></div>'
        )

    def entropy_bar(committed, provisional, max_val, color, prov_color, w, h=10):
        c_pct = max(0, min(100, (committed / max_val) * 100))
        p_pct = max(0, min(100, (provisional / max_val) * 100))
        return (
            f'<div style="display:inline-block;width:{w}px;height:{h}px;'
            f'background:{BAR_BG};border-radius:2px;border:1px solid #555;'
            f'overflow:hidden;margin:1px;vertical-align:middle;position:relative;">'
            f'<div style="width:{c_pct}%;height:100%;background:{color};'
            f'position:absolute;left:0;top:0;"></div>'
            f'<div style="width:{p_pct}%;height:100%;background:{prov_color};'
            f'position:absolute;left:{c_pct}%;top:0;opacity:0.5;"></div>'
            f'</div>'
        )

    def segments(filled, total, color_on, w, h=22, active_idx=-1):
        seg_w = max(4, (w - total * 2) // total)
        out = ''
        for i in range(total):
            c = color_on if i < filled else BAR_BG
            brd = f"2px solid {HORA_ACTIVE}" if i == active_idx else "1px solid #555"
            out += (
                f'<div style="display:inline-block;width:{seg_w}px;height:{h}px;'
                f'background:{c};border-radius:2px;border:{brd};margin:1px;"></div>'
            )
        return out

    def watches_display(count, color):
        if count == 0:
            return '<span style="color:#555;font-size:24px;">—</span>'
        if count <= 30:
            return f'<span style="font-size:20px;">{"⌚" * count}</span>'
        return f'<span style="font-size:20px;">⌚ × {count}</span>'

    # === Extract Hora state ===
    h_parts = f['h_parts']
    h_subassemblies = f['h_subassemblies']
    h_subassemblies_ready = f['h_subassemblies_ready']
    h_larger_subs = f['h_larger_subs']
    h_larger_subs_ready = f['h_larger_subs_ready']
    h_working = f['h_currently_working_on']
    h_watches = f['h_watches']
    h_interrupts = f['h_interrupts']
    h_work_lost = f['h_work_lost']
    h_assemb = f['h_all_assemblies_completed']

    # === Extract Tempus state ===
    t_parts = f['t_parts']
    t_watches = f['t_watches']
    t_interrupts = f['t_interrupts']
    t_work_lost = f['t_work_lost']

    # === Bar widths ===
    W = 600  # total bar area width
    parts_bar_w = max(60, W // 5)
    seg_bar_w = W - parts_bar_w - 140  # room for label + parts bar

    # Hora level 0: segments = completed sub-assemblies ready, plus active parts bar
    # But we need to show WHERE in the hierarchy Hora is.
    # Row 1: sub-assembly inventory (sub_assembs_ready segments) + current parts bar
    # Row 2: larger-sub inventory (larger_subs_ready segments) + current sub-assembly joining bar (if working_on==1)
    # Row 3: assembly joining bar (if working_on==2)

    # Active bar depends on currently_working_on
    parts_active = (h_working == 0)
    sub_active = (h_working == 1)
    larger_active = (h_working == 2)

    # === Entropy bars (only if entropy_switch.value) ===
    entropy_html = ""
    if entropy_switch.value:
        h_committed = f.get('h_committed_bits', 0)
        h_provisional = f.get('h_provisional_bits', 0)
        t_committed = f.get('t_committed_bits', 0)
        t_provisional = f.get('t_provisional_bits', 0)

        # Per-watch committed: modulo one watch's worth of bits
        bits_per_hora_watch = 111 * K * log_2T(p_disp)
        bits_per_tempus_watch = TEMPUS_PARTS_PER_WATCH * log_2T(p_disp)

        h_committed_this_watch = h_committed % bits_per_hora_watch
        t_committed_this_watch = t_committed % bits_per_tempus_watch

        max_bits = max(bits_per_hora_watch, bits_per_tempus_watch)
        full_w = seg_bar_w + parts_bar_w + 20  # match Tempus bar width

        entropy_html = f"""
        <div style="margin-top:8px;padding-top:6px;border-top:1px solid #333;">
            <div style="font-size:10px;color:{LABEL};margin-bottom:4px;">
                Shannon entropy (committed + provisional toward current watch)</div>
            <div style="margin-bottom:3px;display:flex;align-items:center;">
                <span style="font-size:10px;color:{LABEL};width:130px;flex-shrink:0;">
                    Hora:</span>
                {entropy_bar(h_committed_this_watch, h_provisional, max_bits, HORA_BLUE, HORA_ACTIVE, full_w)}
                <span style="font-size:10px;color:{LABEL};margin-left:4px;">
                    {h_committed_this_watch:.2f} + {h_provisional:.3f} bits</span>
            </div>
            <div style="margin-bottom:3px;display:flex;align-items:center;">
                <span style="font-size:10px;color:{LABEL};width:130px;flex-shrink:0;">
                    Tempus:</span>
                {entropy_bar(t_committed_this_watch, t_provisional, max_bits, TEMPUS_RED, '#ff9999', full_w)}
                <span style="font-size:10px;color:{LABEL};margin-left:4px;">
                    {t_committed_this_watch:.2f} + {t_provisional:.3f} bits</span>
            </div>
        </div>
        """




    html = f"""
    <div style="font-family:'SF Mono','Fira Code','Cascadia Code',monospace;color:#eee;padding:16px 20px;">

        <div style="font-size:11px;color:{LABEL};margin-bottom:12px;">
            Step <b>{step:,}</b> &nbsp;|&nbsp; p = {p_disp}
            &nbsp;|&nbsp; Frame {frame_slider.value + 1:,} / {len(snapshots):,}
        </div>

        <!-- HORA -->
        <div style="margin-bottom:24px;">
            <div style="font-size:15px;font-weight:bold;color:{HORA_BLUE};margin-bottom:8px;">
                HORA
                <span style="font-weight:normal;font-size:11px;color:{LABEL};">
                    10 × 10 × 10 hierarchy &nbsp;|&nbsp; 111 assemblies/watch
                </span>
            </div>

            <!-- Row 1: subassemblies_ready + current parts progress -->
            <div style="margin-bottom:5px;display:flex;align-items:center;">
                <span style="font-size:10px;color:{LABEL};width:130px;flex-shrink:0;">
                    Subassemblies:</span>
                {segments(
                    h_subassemblies_ready, K, HORA_DONE, seg_bar_w, h=24,
                    active_idx=h_subassemblies_ready if parts_active and h_subassemblies_ready < K else -1
                )}
                <span style="margin:0 4px;font-size:10px;color:{LABEL};">←</span>
                {bar(h_parts / K, HORA_ACTIVE if parts_active else '#555', parts_bar_w, h=24, active=parts_active)}
                <span style="font-size:10px;color:{LABEL};margin-left:4px;min-width:35px;">
                    {h_parts}/{K}</span>
            </div>

            <!-- Row 2: larger_subs_ready + current sub-assembly joining progress -->
            <div style="margin-bottom:5px;display:flex;align-items:center;">
                <span style="font-size:10px;color:{LABEL};width:130px;flex-shrink:0;">
                    Larger subs:</span>
                {segments(
                    h_larger_subs_ready, K, HORA_DONE, seg_bar_w, h=24,
                    active_idx=h_larger_subs_ready if sub_active and h_larger_subs_ready < K else -1
                )}
                <span style="margin:0 4px;font-size:10px;color:{LABEL};">←</span>
                {bar(h_subassemblies / K, HORA_ACTIVE if sub_active else '#555', parts_bar_w, h=24, active=sub_active)}
                <span style="font-size:10px;color:{LABEL};margin-left:4px;min-width:35px;">
                    {h_subassemblies}/{K}</span>
            </div>

            <!-- Row 3: assembly (watch) progress -->
            <div style="margin-bottom:5px;display:flex;align-items:center;">
                <span style="font-size:10px;color:{LABEL};width:130px;flex-shrink:0;">
                    Watch assembly:</span>
                {bar(h_larger_subs / K, HORA_ACTIVE if larger_active else '#555', seg_bar_w + parts_bar_w + 20, h=24, active=larger_active)}
                <span style="font-size:10px;color:{LABEL};margin-left:4px;min-width:35px;">
                    {h_larger_subs}/{K}</span>
            </div>
        </div>

        <!-- TEMPUS -->
        <div style="margin-bottom:24px;">
            <div style="font-size:15px;font-weight:bold;color:{TEMPUS_RED};margin-bottom:8px;">
                TEMPUS
                <span style="font-weight:normal;font-size:11px;color:{LABEL};">
                    1000 parts, one long chain
                </span>
            </div>

            <div style="display:flex;align-items:center;">
                <span style="font-size:10px;color:{LABEL};width:130px;flex-shrink:0;">
                    Progress:</span>
                {bar(t_parts / TEMPUS_PARTS_PER_WATCH, TEMPUS_RED, seg_bar_w + parts_bar_w + 20, h=24, active=True)}
                <span style="font-size:10px;color:{LABEL};margin-left:4px;min-width:55px;">
                    {t_parts}/{TEMPUS_PARTS_PER_WATCH}</span>
            </div>
        </div>

        <!-- WATCH OUTPUT -->
        <div style="display:flex;gap:60px;padding-top:12px;border-top:1px solid #444;">
            <div>
                <div style="font-size:12px;color:{HORA_BLUE};margin-bottom:4px;font-weight:bold;">
                    Hora's watches</div>
                {watches_display(h_watches, HORA_BLUE)}
            </div>
            <div>
                <div style="font-size:12px;color:{TEMPUS_RED};margin-bottom:4px;font-weight:bold;">
                    Tempus's watches</div>
                {watches_display(t_watches, TEMPUS_RED)}
            </div>
        </div>

        {entropy_html}

        <!-- STATUS -->
        <div style="margin-top:12px;font-size:10px;color:{LABEL};border-top:1px solid #333;padding-top:6px;">
            Hora: {h_interrupts:,} interrupts, ~{h_work_lost:,} parts-equiv lost,
            {h_assemb:,} assemblies completed,
            working on level {h_working}
            &nbsp;|&nbsp;
            Tempus: {t_interrupts:,} interrupts, {t_work_lost:,} parts lost
        </div>

    </div>
    """

    mo.Html(html)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Simulation

    As illuminating and artful as Simon's parable of the watchmakers may be, the discourse ends with some calculations that have proven, over time, to be less than precise. This imprecision does nothing to alter the significance of the core message of the story—that modular designs in complex systems will tend to be selected over linear ones is not only generally accepted but now backed by many other lines of analysis and troves of data. In fact, *Architecture* has been and continues to be enormously widely-cited, with Google Scholar reporting more than 10,000 citations.

    However, that success means that the same headline numbers have been repeatedly mis-reported over the years.

    In his analysis, Simon seeks to answer the question: through his modular architecture, how many more watches can Hora complete than Tempus, given a specific probability (arbitrarily, $0.01$) of interruption. The entire prose including the calculations are below. Simon arrives at a specific formula concluding in an approximate value of 4,000. While the number is indeed presented as an approximation, we might observe that in the final line of his analysis:

    $$
    1/111\times 100/5 \times .99^{10}/.99^{1000} = 1/111 \times 20 \times 20,000 \sim 4,000
    $$

    it could be the equals sign that has led so many people over the years to take the number as a published certainty. It is instead off by a factor of two.

    ### Helpful Analyses

    With so many citations of the text, a complete investigation into the history of mathematical adjustments to the watchmakers math would be far beyond the scope of this work. Here, we can cite to a few examples.

    An early standout that arrives very near the precise analysis is presented in Turney (1989) in *Synthese*. He derives the ratio components that we arrive at in our simulation: 1,173.603 steps per watch for Hora and 2,316,256.508 steps for Tempus, making for the ~2000x ratio. Turney also explicitly labels Simon's error: "He appears to make the mistake of calculating $Et(p,k)$ as $Ea(p,k) · Etfa(p,k)$." As conclusive as these findings are, however, they are arrived at by means of fairly esoteric network mathematics: the beginning of the passage is separated from the final calculation by full-page diagrams. It seems possible that this quirk has prevented the absorption of the correct analysis by more of the academic world.

    A more direct and didactically helpful analysis appears in a classroom note by J. H. Saltzer (1996). We use this analysis to guide the simulation testing below. It is difficult to trace the precise origin of the analysis since, being class notes rather than a published paper, the work cites private conversations Saltzer appears to have had with MIT colleagues around the time. Still, the passage is extremely clear, converting the probability $p$ to a number of tries $T = (1/.99)$, and concluding that:

    $$
    S_k = T \cdot \frac{T^k - 1}{T - 1}
    $$

    And then,
    > "Using k = 1000 for Tempus and k = 10 for Hora (and multiplying Hora's result by 111 subassemblies) we get
         Tempus:               2316257 steps
         Hora:  10.577 * 111 =    1174 steps"

    The simulation below validates this approach.
    """)
    return


@app.cell(hide_code=True)
def _(mo, np):
    slider_steps = 10**(np.arange(3,7)) # [1000   10000  100000 1000000]
    simulated_watches = mo.ui.slider(steps=slider_steps, value=1000, label="Using this slider will adjust the number of simulations. Very large numbers will take a long time to run.")
    sw_form = simulated_watches.form()
    sw_form
    return (sw_form,)


@app.cell(hide_code=True)
def _(sw_form):
    s_w = 10000
    if sw_form.value is not None:
        s_w = sw_form.value
    print(f"Number of watches to be simulated: {s_w}")
    return (s_w,)


@app.cell(hide_code=True)
def _(
    Hora,
    K,
    TEMPUS_PARTS_PER_WATCH,
    Tempus,
    entropy_switch,
    log_2T,
    np,
    probability,
    s_w,
):
    # Simulation
    def simulate_watchmakers(probability, s_w):
        p = probability

        T = 1 / (1 - p)

        def S(k):
            """Leighton/Saltzer: expected steps to complete a k-step assembly."""
            return T * (T**k - 1) / (T - 1)

        hora_expected = 111 * S(K)  # Recall that K is parts per subassembly for Hora
        tempus_expected = S(TEMPUS_PARTS_PER_WATCH)

        print(f"Analytical predictions (p={p}):")
        print(f"  Hora:   111 * S({K}) = {hora_expected:.1f} steps/watch")
        print(f"  Tempus: S({TEMPUS_PARTS_PER_WATCH}) = {tempus_expected:.1f} steps/watch")
        print(f"  Ratio:  {tempus_expected / hora_expected:.1f}x")
        print()

        # — Hora —
        # Here we give Hora (and perhaps his daughter) 10000 watches to make for us.
        target = s_w
        rng = np.random.default_rng()  # use a seed if you would like to guarantee/replay results
        hora = Hora()

        while hora.watches < target:
            hora.step(rng, p)   # we send hora the seeded (or not) generator and the probability. hora as an object will collect all the data we need in its state variables

        avg_hora = hora.total_steps / hora.watches
        avg_assemb = hora.all_assemblies_completed / hora.watches

        print(f"Hora: {hora.watches} watches in {hora.total_steps:,} steps")
        print(f"  Avg steps/watch:      {avg_hora:.1f}  (expected: {hora_expected:.1f})")
        print(f"  Avg assemblies/watch: {avg_assemb:.1f}  (expected: 111)")

        ratio_h = avg_hora / hora_expected
        print(f"  {'Successful ' if abs(ratio_h - 1.0) < 0.02 else 'Failed '} Sim/Analytical = {ratio_h:.4f}")
        print()

        # — Tempus —
        # Tempus is so slow we can't run 10000 watches; to be keep up appearances, 
        # we'll run for same number of steps as Hora and see how many watches he completes.
        rng2 = np.random.default_rng()
        tempus = Tempus()

        for _ in range(hora.total_steps):
            tempus.step(rng2, p)

        print(f"Tempus: {tempus.watches} watches in {tempus.total_steps:,} steps")
        if tempus.watches > 0:
            avg_tempus = tempus.total_steps / tempus.watches
            print(f"  Avg steps/watch: {avg_tempus:.1f}  (expected: {tempus_expected:.1f})")
        else:
            print(f"  (zero watches — expected ~{hora.total_steps / tempus_expected:.1f} watches)")
        print(f"  Interrupts: {tempus.interrupts:,}")
        print(f"  Work lost:  {tempus.work_lost:,} parts")
        print(f"  Best progress: (not tracked, but expected ~{1/p:.0f} parts before reset)")  # TODO
        print()

        # — Comparison —
        print(f"In {hora.total_steps:,} steps:")
        print(f"  Hora:   {hora.watches} watches")
        print(f"  Tempus: {tempus.watches} watches")
        if tempus.watches > 0:
            print(f"  Ratio:  {hora.watches / tempus.watches:.0f}x")
        else:
            print(f"  Ratio:  ∞  (Tempus completed zero watches)")
        print(f"  Expected ratio: {tempus_expected / hora_expected:.0f}x")

        # === Shannon entropy summary (if entropy switch is on) ===
        if entropy_switch.value:
            log2T = log_2T(p)
            bits_per_hora_watch = 111 * K * log2T
            bits_per_tempus_watch = TEMPUS_PARTS_PER_WATCH * log2T
            print()
            print(f"Shannon entropy (H(k) = k·log₂(T), where T = 1/(1-p) = {T:.6f}):")
            print(f"  log₂(T) = {log2T:.6f} bits per step")
            print(f"  Hora commits per ratchet:  K·log₂(T) = {K * log2T:.4f} bits")
            print(f"  Hora total per watch:      111 × {K * log2T:.4f} = {bits_per_hora_watch:.4f} bits")
            print(f"  Tempus total per watch:    1000 × {log2T:.6f} = {bits_per_tempus_watch:.4f} bits")
            print()
            print(f"  Hora committed:   {hora.committed_bits:.1f} bits across {hora.watches} watches")
            print(f"    Avg per watch:  {hora.committed_bits / hora.watches:.4f}  (expected: {bits_per_hora_watch:.4f})")
            print(f"  Tempus committed: {tempus.committed_bits:.1f} bits across {tempus.watches} watches")
            print(f"    Provisional:    {tempus.provisional_bits:.4f} bits (in progress, not yet banked)")

    simulate_watchmakers(probability, s_w)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Note that the outcomes will assuredly approach the target ratio of 1974 when the simulation is run with more cycles, as can be adjusted, above. The cost of this is a longer run-time. Running the simulation confirms that Turney's calculation and Saltzer's approach are both valid, though we might note that there is a rounding error at the integer level in the Saltzer. Hora makes 1974, not 1973, watches for every one of Tempus' when $p = .01$.

    Despite the fact that corrections have been available for more than a quarter century, Simon's original approximate ratio of 4,000 appears repeatedly in modern literature: (Rivelli 2025) is a recent example, but hardly alone. In fact, a quick inquiry to modern AI chatbots about Simon's watchmakers will often get a response with the same incorrect result.

    Regardless of the uncomfortable situation of an incorrect value being cited in (likely) hundreds of referreed articles for the better part of a century, the model appears to generally work to reinforce the concepts for which it was designed. If our system is only 2000 times as efficient, rather than 4000, what does that matter? Better is better, and 2000x is way better.

    It turns out, however, that this is not the only problem with the parable of the watchmakers. Math might be the least of the worries. A more fundamental issue emerges when we ask: where does Hora's advantage actually come from? To investigate this, we turn to the subject of entropy.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Watchmakers and Entropy

    Implementing Hora as a Python class turns out to make one particular issue very clear: when Hora is assembling his parts he is vulnerable, just as is Tempus, to an interruption: yet, when he is converting his subassemblies into larger components---say, by gluing them---he is notably immune. This is such unusual arrangement in causal nature that modeling around it takes extra code to make it work.

    Can we measure what is happening when Hora "banks" a "glued" module for free? In fact, Simon himself recognizes both the problem and its signature in the paper: entropy. He addresses it in a section applying modularity to biological systems.

    > "[T]he evolution of complex systems from simple elements implies nothing, one way or the other, about the change in entropy of the entire system... The net inflow of free energy has to be supplied from the sun or some other source if the second law of thermodynamics is not to be violated.... All estimates indicate that the amount of entropy, measured in physical units, involved in the formation of a one-celled biological organism is trivially small---about $10^{-11}$ cal/degree."

    In a footnote, Simon converts this thermodynamic measure to an informational one: $10^{13}$ bits.

    ### Applying Shannon entropy to the watchmakers

    The footnote hints at Shannon entropy, rather than thermodynamic entropy, and this is our next interest. The difference in the Tempus and Hora systems does not appear step-by-step, as both watchmakers are identical at handling elements. Hora's advantage is at the step committing $k$ elements to a component assembly, and the advantage can be quantified using Shannon's equations.

    The general Shannon entropy formula gives us the information content (in bits) associated with a single event of probability $P$:

    $$
    I = −\log⁡_2P
    $$

    If we re-organize Saltzer's initial approach to the problem, we can derive a "Shannon-friendly" equation of:

    $$
    (1−p)^k=T^{−k}
    $$

    where $T$ is the "expected number of tries." As might be anticipated with such an expression, we can connect immediately into the Shannon by substitution: $P_k = (1−p)^k = T^−k$. And so:

    $$
    −log2​(1−p)k=k\log2​T
    $$

    which can further simplify to:

    $$
    I = k\log_2T
    $$

    Each successful step reduces the *uncertainty* about whether a given watch will be finished. Applying Saltzer's formula to Shannon, this uncertainty is derived as a measure in bits. The uncertainty remaining at step *k* given an *n* step assembly is:

    $$
    H(k)=−(n−k)\log⁡_2(1−p)
    $$


    ### Viewing in simulation

    These steps can be reviewed and verified through our modeling efforts.

    Toggling the switch below will adjust both the visualization and the simulation in this notebook to also compute Shannon entropy.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    entropy_switch = mo.ui.switch(label="Turn on Entropy Calculations")
    entropy_switch
    return (entropy_switch,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Once these calculations are enabled, we can see from our simulation tools that the entropy difference between Tempus and Hora is massive. Each watch is made with exactly 1000 parts, and yet the gap exists. We know for certain that information is created every time one of Hora's subassemblies is made ready and, in particular, made invulnerable to interruption. How can this happen? There are two possibilities:

    - Hora is getting the assemblage of modules for free, a tribute to his cunning design prowess. Once he has ten elements ready they are immediately joined, interlocking by merit of superb design alone.
    - Hora has help.

    As we think back to Simon's explanation, it seems somewhat clear that the first of these possibilities is what is intended by the story. The prose does not mention any specific activity of macro-assembly except the gathering of the ten elements. And, as Simon explains, this story is primarily intended as a metaphor, and in terrestrial biology extra energy, via solar radiance, is practically free. In fact, in the case of biology it is possible to imagine chemistries---Kauffman's recent autocatalytic sets come to mind (2025)---where the assembly of sets is indeed approximately free, for instance in a case where greater stability from combination serves as the "glue" keeping composites joined. Perhaps this is what Simon is considering in his story.

    However, there is a problem with this, one that becomes clear when trying to build a software class for Hora: in this case, the number of subassembly steps, 111, would be wrong in that case.

    Consider our case with free-energy, zero-effort, automatic subassembly creation. These qualities also imply: zero time. What that means is that when the tenth element is created, the subassembly immediately exists. So too, necessarily, when the tenth subassembly is created, the larger assembly exists. And then of course when the tenth larger assembly is created, we have a watch.

    What this implies, though, is an immediate, automatic cascade of assemblies from the lowest tier to the highest. Just as all the digits on a digital clock turn at once from 9:59 to 10:00, so too does the last subassembly imply the last larger assembly imply the watch. The cascading effect means 100 of these events, not 111.

    Of course, a story in which the last subcomponent immediately becomes the watch is so unrealistic as to be difficult to tell in prose. So, even though Simon commits to the idea of "free energy" in the footnote, the story he believes he is communicating about the watchmakers, to him, naturally has a hierarchy of events rather than a cascade of them. The prose may not explicitly communicate this, but the math he presents does. He communicates 111 subassembly events.

    Hora must have help.

    ## Hora's helper, Secunda

    Let us expand our story to explicitly account for Hora's competitive advantage. To do this, we introduce Secunda. For example:

    > The watches that Hora made were no less complex than those of Tempus. But he had designed them so that he could put together subassemblies of about ten elements each. Each of these was joined by his daughter Secunda—who worked quickly enough in the joining so as to never slow down the overall progress; who worked for free; and who never deigned to answer the phone while she worked. Ten of these subassemblies, again, could be put together into a larger subassembly, again by Secunda; who also made quick work of making a whole wathc a system of ten of the latter subassemblies. Hence, when Hora had to put down a partly assembled watch in order to answer the phone, he lost only a small part of his work, and he assembled his watches in only a fraction of the man-hours it took Tempus.
    >
    > That is to say, he and his daughter did.

    Now our story rings a bit more true, but it is still just a story, or an analogy. What can we know about Secunda, and how can she inform us about modularity in complex systems?

    It would be trivially easy to implement Secunda in code using a flat cost per watch, or we might conceive of a tiered system of arbitrary values. In fact, in one manner, Secunda *already exists* in the code; after all, we necessarily perform some processing to stack the subassemblies into watches. Simon may have conceived a free conversion of components to whole in theory; such a thing does not exist as a Python library!

    But, none of the actual code cost or modeled cost or whatever other approach we might think of will be particularly illuminating, as it turns out. After all, we can do sums and differences in our heads, and we can immediately see that the real value of the modularity of the system cannot be calculated without knowing Secunda's cost. As an analogy applied to other systems, Secunda will have any number of implementations and embodiments. Far from being a footnote, she is in fact the main performer of Simon's parable.

    ---

    ## WIP: Secunda, causal dominance, and meaning



    ---

    Herbert Simon was a titan of Twentieth Century complexity theory, and an extrordinary general contributor during a singular time in the history of science. He did not publish without controversy, but many of his controversies have settled, over time, in his seeming general favor. The core principle of modular design and its broad applicability have been so durable as to seem in many ways more relevant to this next century than the one in which they were authored.

    There is, nonetheless, an insufficiency in the work: and the importance of this insufficiency is magnified by the its astonishingly wide adoption. The works citing *Architecure* span myriad avenues of science, including many that that investigate human social systems, themselves far more closely attuned to cottage industries than the biological examples presented in the paper.

    One wonders if those authors, beyond the tricky task of catching the corrections of the math in later publications, have been entirely attuned in all cases to the importance of entropy to the system---if they have in each case thought to identify the Secundas to their Horas, and figured how to properly apply and quantify them. This seems a question that could be addressed rigorously and quantitatively through further investigation. With 10,000 papers and counting, the significance of the answer is potentially high.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Appendix

    For reference, here is the complete prose of Simon watchmakers story (p. 470):

    ### THE EVOLUTION OF COMPLEX SYSTEMS

    Let me introduce the topic of evolution with a parable. There once were two watchmakers, named Hora and Tempus, who manufactured very fine watches. Both of them were highly regarded, and the phones in their workshops rang frequently—new customers were constantly calling them. However, Hora prospered, while Tempus became poorer and poorer and finally lost his shop. What was the reason?

    The watches the men made consisted of about 1,000 parts each. Tempus had so constructed his that if he had one partly assembled and had to put it down to answer the phone—say it immediately fell to pieces and had to be reassembled from the elements. The better the customers liked his watches, the more they phoned him, the more difficult it became for him to find enough uninterrupted time to finish a watch.

    The watches that Hora made were no less complex than those of Tempus. But he had designed them so that he could put together subassemblies of about ten elements each. Ten of these subassemblies, again, could be put together into a larger subassembly; and a system of ten of the latter subassemblies constituted the whole watch. Hence, when Hora had to put down a partly assembled watch in order to answer the phone, he lost only a small part of his work, and he assembled his watches in only a fraction of the man-hours it took Tempus.

    It is rather easy to make a quantitative analysis of the relative difficulty of the tasks of Tempus and Hora: Suppose the probability that an interruption will occur while a part is being added to an incomplete assembly is $p$. Then the probability that Tempus can complete a watch he has started without interruption is $(1-p)^{1000}$—a very small number unless $p$ is .001 or less. Each interruption will cost, on the average, the time to assemble $1/p$ parts (the expected number assembled before interruption). On the other hand, Hora has to complete one hundred eleven sub-assemblies of ten parts each. The probability that he will not be interrupted while completing any one of these is $(1-p)^{10}$, and each interruption will cost only about the time required to assemble five parts.[^Simon's footnote: 7]

    Now if $p$ is about .01—that is, there is one chance in a hundred that either watchmaker will be interrupted while adding any one part to an assembly—then a straightforward calculation shows that it will take Tempus, on the average, about four thousand times as long to assemble a watch as Hora.

    We arrive at the estimate as follows:
    1. Hora must make 111 times as many complete assemblies per watch as Tempus; but,
    2. Tempus will lose on the average 20 times as much work for each interrupted assembly as Hora [100 parts, on the average, as against 5]; and,
    3. Tempus will complete an assembly only 44 times per million attempts $((.99)^{1000}=44 \times 10^{-6})$, while Hora will complete nine out of ten $((.99)^{10}=9\times 10^{-1})$. Hence Tempus will have to make 20,000 as many attempts per completed assembly as Hora: $(9\times 10^{-1})/(44 \times 10^{-6})=2\times 10^{4}$.

    Multiplying these three ratios, we get:

    $$
    1/111\times 100/5 \times .99^{10}/.99^{1000} = 1/111 \times 20 \times 20,000 \sim 4,000
    $$

    ---

    ### Notes

    [Footnote 7 from the Simon passage, about which Saltzer says:  ...

    > This is a good approximation for Hora's case, and it may be that Simon tried to explain it but the journal editors blew it. The (correct) phrase regarding Hora that "each interruption will cost only about the time to assemble five parts" has a footnote, but the footnote that appears at the bottom of the column has nothing whatever to do with the subject at hand. This is probably an editing or typesetting/proofreading goof. But because this ratio is near the heart of the calculation mistake, the editing error compounds the situation and has led several people to mistakenly believe that this ratio was calculated incorrectly. It isn't that the ratio was calculated wrong, it is the wrong ratio to calculate. Simon should have calculated for the second ratio the expected number of steps lost per assembly, rather than steps lost per interruption.

    ]

    [Here, we should also reproduce another comment from Saltzer, in which he corrects Simon's ratio and acknowledges a colleague: "[W]e conclude that Hora can produce 1973 times as many watches per unit time as can Tempus. [Thanks to Chandra Boyapati for helping to find the summation error.]"]

    ### References

    Kauffman, S., & Roli, A. (2025). Is the emergence of life and of agency expected? Philosophical Transactions of the Royal Society B: Biological Sciences, 380(1936), 20240283. https://doi.org/10.1098/rstb.2024.0283

    Rivelli, L. (2025). Modularity in biological thought: Sketch of a unifying theoretical framework. BioSystems, 250, 105430. https://doi.org/10.1016/j.biosystems.2025.105430

    Simon, H. A. (1962). The architecture of complexity. Proceedings of the American Philosophical Society, 106(6), 467–482. https://www.jstor.org/stable/985254

    Saltzer, J. H. (1996). 6.033 discussion suggestions (Simon complexity paper). MIT. https://web.mit.edu/saltzer/www/publications/recguides/Simon.html

    Turney, P. (1989). The architecture of complexity: A new blueprint. Synthese, 79(3), 515–542. https://doi.org/10.1007/BF00869285
    """)
    return


if __name__ == "__main__":
    app.run()
