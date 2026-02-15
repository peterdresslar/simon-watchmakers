import marimo

__generated_with = "0.19.11"
app = marimo.App(width="medium", app_title="Tempus and Hora")


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import altair as alt
    import pandas as pd

    return mo, np


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Simon's Watchmakers

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
    In order to elucidate Simon's parable, the following code cells provide an implementation in Python. The core classes `Tempus` and `Hora` are designed to be as faithful to the prose as possible, with particular care toward making sure the core number of subassemblies, 111, is precisely reached by Hora.

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

    These are the implementing classes for both watchmakers. They will say hello.
    """)
    return


@app.cell(hide_code=True)
def _():
    HORA_PARTS_PER_SUB = 10           # Number of parts for each Hora component
    K = HORA_PARTS_PER_SUB            # Shorter version of that, matches Saltzer 1999
    TEMPUS_PARTS_PER_WATCH = 1000     # Poor Tempus

    class Hora:
        """Hora the watchmaker: builder of modular watches.

        State tracks progress at three levels, plus inventory of completed
        pieces waiting to be joined at the next level up.
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

        def step(self, rng, p):
            self.total_steps += 1
            level = self.currently_working_on

            if rng.random() < p:
                # Interrupted — lose current level's progress
                self.interrupts += 1
                progress = self._get_progress()
                self.work_lost += progress * (K ** level)
                self._set_progress(0)
                # Stay at this level — the pieces below are safe,
                # we just need to redo this assembly.

            else:
                # Successful step
                self._set_progress(self._get_progress() + 1)

                if self._get_progress() >= K:
                    # Assembly complete at this level
                    self._set_progress(0)
                    self.all_assemblies_completed += 1   # no matter the level, track an assembly to all_assemblies

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

        def step(self, rng, p):
            self.total_steps += 1

            if rng.random() < p:
                # Interrupted — lose everything
                self.interrupts += 1
                self.work_lost += self.parts
                self.parts = 0
            else:
                self.parts += 1
                if self.parts >= TEMPUS_PARTS_PER_WATCH:
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
            }



    return Hora, K, TEMPUS_PARTS_PER_WATCH, Tempus


@app.cell(hide_code=True)
def _(Hora, Tempus):
    t = Tempus()
    h = Hora()
    print(f"Hello, I am {t.name}, a linear watchmaker.")
    print(f"Hello, I am {h.name}, a modular watchmaker.")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Visualization

    Here we have a sort of *post facto* visualization, in that the data are run in advance, and then the user is invited to uses the frame slider to "scrub through" those data.
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
            label="Use this control to scrub through visualization data.",
            full_width=True,
        )
    frame_slider
    return (frame_slider,)


@app.cell(hide_code=True)
def _(K, TEMPUS_PARTS_PER_WATCH, frame_slider, mo, probability, snapshots):
    f = snapshots[frame_slider.value]
    step = f['step']
    p_disp = probability

    # --- Colors ---
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

    # --- Extract Hora state ---
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

    # --- Extract Tempus state ---
    t_parts = f['t_parts']
    t_watches = f['t_watches']
    t_interrupts = f['t_interrupts']
    t_work_lost = f['t_work_lost']

    # --- Bar widths ---
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
    """)
    return


@app.cell(hide_code=True)
def _(mo, np):
    slider_steps = 10**(np.arange(3,7)) # [1000   10000  100000 1000000]
    simulated_watches = mo.ui.slider(steps=slider_steps, value=1000, label="Using this slider will adjust the number of simulations. Very large numbers will take a long time to run.")
    sw_form = simulated_watches.form()
    sw_form
    return simulated_watches, sw_form


@app.cell(hide_code=True)
def _(simulated_watches, sw_form):
    s_w = 10000
    if sw_form.value is not None:
        s_w = sw_form.value
    print(f"Number of watches to be simulated: {simulated_watches.value}")
    return (s_w,)


@app.cell(hide_code=True)
def _(Hora, K, TEMPUS_PARTS_PER_WATCH, Tempus, np, probability, s_w):
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
        print(f"  {'✓' if abs(ratio_h - 1.0) < 0.02 else 'x'} Sim/Analytical = {ratio_h:.4f}")
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

    simulate_watchmakers(probability, s_w)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Discussion
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Prose and References

    For reference, here is the complete prose of Simon watchmakers story (p. 470):

    ### THE EVOLUTION OF COMPLEX SYSTEMS

    Let me introduce the topic of evolution with a parable. There once were two watchmakers, named Hora and Tempus, who manufactured very fine watches. Both of them were highly regarded, and the phones in their workshops rang frequently—new customers were constantly calling them. However, Hora prospered, while Tempus became poorer and poorer and finally lost his shop. What was the reason?

    The watches the men made consisted of about 1,000 parts each. Tempus had so constructed his that if he had one partly assembled and had to put it down to answer the phone—say it immediately fell to pieces and had to be reassembled from the elements. The better the customers liked his watches, the more they phoned him, the more difficult it became for him to find enough uninterrupted time to finish a watch.

    The watches that Hora made were no less complex than those of Tempus. But he had designed them so that he could put together subassemblies of about ten elements each. Ten of these subassemblies, again, could be put together into a larger subassembly; and a system of ten of the latter subassemblies constituted the whole watch. Hence, when Hora had to put down a partly assembled watch in order to answer the phone, he lost only a small part of his work, and he assembled his watches in only a fraction of the man-hours it took Tempus.

    It is rather easy to make a quantitative analysis of the relative difficulty of the tasks of Tempus and Hora: Suppose the probability that an interruption will occur while a part is being added to an incomplete assembly is $p$. Then the probability that Tempus can complete a watch he has started without interruption is $(1-p)^{1000}$—a very small number unless $p$ is .001 or less. Each interruption will cost, on the average, the time to assemble $1/p$ parts (the expected number assembled before interruption). On the other hand, Hora has to complete one hundred eleven sub-assemblies of ten parts each. The probability that he will not be interrupted while completing any one of these is $(1-p)^{10}$, and each interruption will cost only about the time required to assemble five parts.[^7]

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

    [Footnote 7 from the Simon passage, about which Saltzer says:  ... This is a good approximation for Hora's case, and it may be that Simon tried to explain it but the journal editors blew it. The (correct) phrase regarding Hora that "each interruption will cost only about the time to assemble five parts" has a footnote, but the footnote that appears at the bottom of the column has nothing whatever to do with the subject at hand. This is probably an editing or typesetting/proofreading goof. But because this ratio is near the heart of the calculation mistake, the editing error compounds the situation and has led several people to mistakenly believe that this ratio was calculated incorrectly. It isn't that the ratio was calculated wrong, it is the wrong ratio to calculate. Simon should have calculated for the second ratio the expected number of steps lost per assembly, rather than steps lost per interruption.]

    [Here, we should also reproduce another comment from Saltzer, in which he corrects Simon's ratio and acknowledges a colleague: "[W]e conclude that Hora can produce 1973 times as many watches per unit time as can Tempus. [Thanks to Chandra Boyapati for helping to find the summation error.]"]
    """)
    return


if __name__ == "__main__":
    app.run()
