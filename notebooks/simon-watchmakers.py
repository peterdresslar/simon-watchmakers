import marimo

__generated_with = "0.19.11"
app = marimo.App(width="medium")


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

    Herbert Simon's *The Architecture of Complexity* (1962) is a foundational work for complexity science. The story introduces a parable of the two watchmakers---Hora and Tempus---along the way to presenting one of the most-cited arguments for why complex systems tend toward hierarchical, modular organization. While the lecture influenced theorists for every decade following its publication, current advances complexity theory and methods lend Simon's work particular resonance.

    Simon's parable begins:

    > There once were two watchmakers, named Hora and Tempus, who manufactured very fine watches. Both of them were highly regarded, and the phones in their workshops rang frequently... However, Hora prospered, while Tempus lost his shop. What was the reason?
    >
    > The watches the men made consisted of about 1000 parts each. Tempus had so constructed his so that if he had one partly assembled and had to put it down---to answer the phone say---it immediately fell to pieces...
    >
    > Hora had designed them so that he could put together subassemblies of ten elements each. Ten of these subassemblies, again, could be put together into a larger subassembly; and a system of ten of the latter constituted the whole watch. Hence, when Hora had to... answer the phone, he lost only a small part of his work, and he assembled his watches in only a fraction of the hours it took Tempus.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    > Suppose the probability that an interruption will occur while a part is being added to an incomplete assembly is *p*. Then the probability that **Tempus** can complete a watch he has started without interruption is (1-p)^1000---a very small number unless p is .001 or less.

    > On the other hand, **Hora** has to complete 111 subassemblies... the probability that he will not be interrupted while completing any one of these is (1-p)^10... if p is about .01... then a straightforward calculation shows that it will take Tempus on the average, about 4000 times as long to assemble a watch as Hora.
    """)
    return


@app.cell
def _(mo):
    probability_p_times_10000 = mo.ui.slider(0, 1000, value=100, label="Using this slider will update probability p.")
    probability_p_times_10000
    return (probability_p_times_10000,)


@app.cell(hide_code=True)
def _(probability_p_times_10000):
    probability = probability_p_times_10000.value / 10000
    print(f"Probability p of an interruption: {probability}")
    return (probability,)


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


@app.cell
def _():
    # Visualization

    MAX_FRAME = 22222                 # Arbitrary maximum time for simulation
    BASE_TICKS_PER_FRAME = 5          # This is an inverted dt, can be adjusted for probability
    return


@app.cell
def _(Hora, K, TEMPUS_PARTS_PER_WATCH, Tempus, np, probability):
    # Simulation
    def run_watchmakers(probability):
        p = probability

        T = 1 / (1 - p)

        def S(k):
            """Leighton/Saltzer: expected steps to complete a k-step assembly."""
            return T * (T**k - 1) / (T - 1)

        hora_expected = 111 * S(K)
        tempus_expected = S(TEMPUS_PARTS_PER_WATCH)

        print(f"Analytical predictions (p={p}):")
        print(f"  Hora:   111 * S({K}) = {hora_expected:.1f} steps/watch")
        print(f"  Tempus: S({TEMPUS_PARTS_PER_WATCH}) = {tempus_expected:.1f} steps/watch")
        print(f"  Ratio:  {tempus_expected / hora_expected:.1f}x")
        print()

        # --- Hora ---
        n_target = 10000
        rng = np.random.default_rng(42)
        hora = Hora()

        while hora.watches < n_target:
            hora.step(rng, p)

        avg_hora = hora.total_steps / hora.watches
        avg_assemb = hora.all_assemblies_completed / hora.watches

        print(f"Hora: {hora.watches} watches in {hora.total_steps:,} steps")
        print(f"  Avg steps/watch:      {avg_hora:.1f}  (expected: {hora_expected:.1f})")
        print(f"  Avg assemblies/watch: {avg_assemb:.1f}  (expected: 111)")

        ratio_h = avg_hora / hora_expected
        print(f"  {'✓' if abs(ratio_h - 1.0) < 0.02 else '✗'} Sim/Analytical = {ratio_h:.4f}")
        print()

        # --- Tempus ---
        # Tempus is so slow we can't run 10000 watches; run for same number of
        # steps as Hora and see how many watches he completes.
        rng2 = np.random.default_rng(42)
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
        print(f"  Best progress: (not tracked, but expected ~{1/p:.0f} parts before reset)")
        print()

        # --- Comparison ---
        print(f"In {hora.total_steps:,} steps:")
        print(f"  Hora:   {hora.watches} watches")
        print(f"  Tempus: {tempus.watches} watches")
        if tempus.watches > 0:
            print(f"  Ratio:  {hora.watches / tempus.watches:.0f}x")
        else:
            print(f"  Ratio:  ∞  (Tempus completed zero watches)")
        print(f"  Expected ratio: {tempus_expected / hora_expected:.0f}x")

    run_watchmakers(probability)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    For reference, here is the prose of Simon (p. 470) in entirety:

    ### THE EVOLUTION OF COMPLEX SYSTEMS

    Let me introduce the topic of evolution with a parable. There once were two watchmakers, named Hora and Tempus, who manufactured very fine watches. Both of them were highly regarded, and the phones in their workshops rang frequently—new customers were constantly calling them. However, Hora prospered, while Tempus became poorer and poorer and finally lost his shop. What was the reason?

    The watches the men made consisted of about 1,000 parts each. Tempus had so constructed his that if he had one partly assembled and had to put it down to answer the phone—say it immediately fell to pieces and had to be reassembled from the elements. The better the customers liked his watches, the more they phoned him, the more difficult it became for him to find enough uninterrupted time to finish a watch.

    The watches that Hora made were no less complex than those of Tempus. But he had designed them so that he could put together subassemblies of about ten elements each. Ten of these subassemblies, again, could be put together into a larger subassembly; and a system of ten of the latter subassemblies constituted the whole watch. Hence, when Hora had to put down a partly assembled watch in order to answer the phone, he lost only a small part of his work, and he assembled his watches in only a fraction of the man-hours it took Tempus.

    It is rather easy to make a quantitative analysis of the relative difficulty of the tasks of Tempus and Hora: Suppose the probability that an interruption will occur while a part is being added to an incomplete assembly is $p$. Then the probability that Tempus can complete a watch he has started without interruption is $(1-p)^{1000}$—a very small number unless $p$ is .001 or less. Each interruption will cost, on the average, the time to assemble $1/p$ parts (the expected number assembled before interruption). On the other hand, Hora has to complete one hundred eleven sub-assemblies of ten parts each. The probability that he will not be interrupted while completing any one of these is $(1-p)^{10}$, and each interruption will cost only about the time required to assemble five parts.[^7]

    Now if $p$ is about .01—that is, there is one chance in a hundred that either watchmaker will be interrupted while adding any one part to an assembly—then a straightforward calculation shows that it will take Tempus, on the average, about four thousand times as long to assemble a watch as Hora.

    We arrive at the estimate as follows:
    1. Hora must make 111 times as many complete assemblies per watch as Tempus;
    2. but, Tempus will lose on the average 20 times as much work for each interrupted assembly as Hora [100 parts, on the average, as against 5];
    3. Tempus will complete an assembly only 44 times per million attempts $((.99)^{1000}=44 \times 10^{-6})$, while Hora will complete nine out of ten $((.99)^{10}=9\times 10^{-1})$. Hence Tempus will have to make 20,000 as many attempts per completed assembly as Hora: $(9\times 10^{-1})/(44 \times 10^{-6})=2\times 10^{4}$.

    Multiplying these three ratios, we get:
    $$
    1/111\times 100/5 \times .99^{10}/.99^{1000} = 1/111 \times 20 \times 20,000 \sim 4,000
    $$

    [Footnote 7, about which Saltzer says:  ... This is a good approximation for Hora's case, and it may be that Simon tried to explain it but the journal editors blew it. The (correct) phrase regarding Hora that "each interruption will cost only about the time to assemble five parts" has a footnote, but the footnote that appears at the bottom of the column has nothing whatever to do with the subject at hand. This is probably an editing or typesetting/proofreading goof. But because this ratio is near the heart of the calculation mistake, the editing error compounds the situation and has led several people to mistakenly believe that this ratio was calculated incorrectly. It isn't that the ratio was calculated wrong, it is the wrong ratio to calculate. Simon should have calculated for the second ratio the expected number of steps lost per assembly, rather than steps lost per interruption.]
    """)
    return


if __name__ == "__main__":
    app.run()
