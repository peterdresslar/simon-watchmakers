import marimo

__generated_with = "0.19.11"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import altair as alt
    import pandas as pd

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Simon's Watchmakers

    Herbert Simon's *The Architecture of Complexity* (1962) is a foundational work for complexity science. The story introduces a parable of the two watchmakers---Hora and Tempus---along the way to presenting one of the most-cited arguments for why complex systems tend toward hierarchical, modular organization. While the lecture influenced theorists for every decade following its publication, current advances complexity theory and methods lend Simon's work particular resonance.

    Simon's parable begins:

    > There once were two watchmakers, named Hora and Tempus, who manufactured very fine watches. Both of them were highly regarded, and the phones in their workshops rang frequently... However, Hora prospered, while Tempus lost his shop. What was the reason?
    >
    > The watches the men made consisted of about 1000 parts each. Tempus had so constructed his so that if he had one partly assmbled and had to put it down---to answer the phone say---it immediately fell to pieces...
    >
    > Hora had designed them so that he could put together subassemblies of ten elements each. Ten of these subassemblies, again, could be put together into a larger subassembly; and as system of ten of the latter constituted the whole watch. Hence, when Hora had to... answer the phone, he lost only a sall part of his work, and he assembled his watches in only a fraction of the hours it took Tempus.
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
    p = probability_p_times_10000.value / 10000
    p
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
