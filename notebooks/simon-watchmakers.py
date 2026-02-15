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


@app.cell
def _(np, probability):
    MAX_FRAME = 22222                 # Arbitrary maximum time for simulation
    BASE_TICKS_PER_FRAME = 5          # This is an inverted dt, can be adjusted for probability
    HORA_PARTS_PER_SUB = 10           # Number of parts for each Hora component
    K = HORA_PARTS_PER_SUB            # Shorter version
    TEMPUS_PARTS_PER_WATCH = 1000     # Poor Tempus

    # Intializers

    def reset_state():
        p = probability
        ticks_per_frame = BASE_TICKS_PER_FRAME * 1
    
        hora_watches = 0
        hora_assemb = 0
        hora_sub_assemb = 0
        hora_sub_sub_assemb = 0
        hora_parts = 0
        hora_currently_working_on = 0   # 0 -->  "elements"
                                        # 1 -->  "subassemblies of ten elements each"
                                        # 2 -->  "Ten of these subassemblies could be put together into larger subassembly"
                                        # 3 -->  "a system of ten of the latter constituted the whole watch"
    
        hora_in_final_step = False
        hora_interrupts = 0
        hora_work_lost = 0
    
        tempus_watches = 0
        tempus_parts = 0
        tempus_in_final_step = False
        tempus_interrupts = 0
        tempus_work_lost = 0
    

    def run_watchmaker():
        reset_state()  # TODO we need to return state or have a state class or something
        rng = np.random.default_rng()  # Could implement a seed here

        p = probability
        ticks_per_frame = BASE_TICKS_PER_FRAME * 1
    
        hora_watches = 0
        hora_assemb = 0
        hora_sub_assemb = 0
        hora_sub_sub_assemb = 0
        hora_parts = 0
        hora_currently_working_on = 0   # 0 -->  "elements"
                                        # 1 -->  "subassemblies of ten elements each"
                                        # 2 -->  "Ten of these subassemblies could be put together into larger subassembly"
                                        # 3 -->  "a system of ten of the latter constituted the whole watch"
    
        hora_in_final_step = False
        hora_interrupts = 0
        hora_work_lost = 0
    
        tempus_watches = 0
        tempus_parts = 0
        tempus_in_final_step = False
        tempus_interrupts = 0
        tempus_work_lost = 0

        snapshots = []

        for current_tick in range(MAX_FRAME):

            print(f"Tick {current_tick} Watches {hora_watches} Assembs {hora_assemb} Sub-assemb {hora_sub_assemb} Sub-Sub {hora_sub_sub_assemb} Parts {hora_parts} Currently Working On {hora_currently_working_on} Final Step {hora_in_final_step} Hora PPS {HORA_PARTS_PER_SUB - 1}")

            # ===== HORA =====
            interrupted_h = rng.random() < p

            if interrupted_h:
                hora_interrupts += 1
                # Lose progress at whatever level we're currently working on
                if hora_currently_working_on == 0:
                    hora_work_lost += hora_parts
                    hora_parts = 0
                elif hora_currently_working_on == 1:
                    hora_work_lost += hora_sub_sub_assemb * K  # TODO explicitly track
                    hora_sub_sub_assemb = 0
                elif hora_currently_working_on == 2:
                    hora_work_lost += hora_sub_assemb * K * K
                    hora_sub_assemb = 0
                elif hora_currently_working_on == 3:
                    hora_work_lost += hora_assemb * K * K * K
                    hora_assemb = 0
                hora_in_final_step = False
                hora_currently_working_on = 0  # back to building parts

            else:
                if not hora_in_final_step:
                    # Normal increment at current level
                    if hora_currently_working_on == 0:
                        hora_parts += 1
                        if hora_parts >= K - 1:
                            hora_in_final_step = True
                    elif hora_currently_working_on == 1:
                        hora_sub_sub_assemb += 1
                        if hora_sub_sub_assemb >= K - 1:
                            hora_in_final_step = True
                    elif hora_currently_working_on == 2:
                        hora_sub_assemb += 1
                        if hora_sub_assemb >= K - 1:
                            hora_in_final_step = True
                    elif hora_currently_working_on == 3:
                        hora_assemb += 1
                        if hora_assemb >= K - 1:
                            hora_in_final_step = True

                else:
                    # We are at a step analogous to a clock rolling over a digit here
                    if hora_currently_working_on == 0:
                        hora_sub_sub_assemb += 1
                        hora_parts = 0
                    elif hora_currently_working_on == 1:
                        hora_sub_assemb += 1
                        hora_sub_sub_assemb = 0
                    elif hora_currently_working_on == 2:
                        hora_assemb += 1
                        hora_sub_assemb = 0
                    elif hora_currently_working_on == 3:
                        # do_something_hora_watch_complete()
                        hora_watches += 1
                        hora_assemb = 0

                    hora_in_final_step = False

                    # Now we have to "check those other clock digits"
                    next_level = hora_currently_working_on + 1

                    if next_level <= 2:
                        # check if the level we promoted into is now full
                        level_values = [hora_parts, hora_sub_sub_assemb, hora_sub_assemb, hora_assemb]
                        if level_values[next_level] >= K - 1:
                            # the next level is ready to promote on the next tick
                            hora_currently_working_on = next_level
                            hora_in_final_step = True
                        else:
                            # back to building parts
                            hora_currently_working_on = 0
                    elif next_level == 3:
                        if hora_assemb >= K - 1:
                            hora_currently_working_on = 3
                            hora_in_final_step = True
                        else:
                            hora_currently_working_on = 0
                    else:
                        # next_level > 3: we just completed a watch, back to parts. Ah, the grind.
                        hora_currently_working_on = 0

                    
                
    
            

    
    
    
    
    




    return (run_watchmaker,)


@app.cell
def _(run_watchmaker):
    run_watchmaker()
    return


if __name__ == "__main__":
    app.run()
