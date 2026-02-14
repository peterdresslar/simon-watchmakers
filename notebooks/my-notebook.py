import marimo

__generated_with = "0.19.11"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    from utils.utils import coin_flip

    return (coin_flip,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Welcome to Marimo!

    This is a sample notebook. In our next cells, we will demonstrate an imported function along with a Marimo slider and control. Note that you can mouse over the imported function and view its docstring.
    """)
    return


@app.cell
def _(mo):
    control = mo.ui.slider(1, 100, value=5, label="Using this slider will update values.")
    control
    return (control,)


@app.cell
def _(coin_flip, control):
    results = coin_flip(control.value)
    results
    return (results,)


@app.cell(hide_code=True)
def _(control, mo, results):
    import altair as alt
    import pandas as pd

    df = pd.DataFrame({
        "outcome": ["Heads", "Tails"],
        "count": [int(results.sum()), int(len(results) - results.sum())]
    })

    radius = min(150, 50 + control.value)

    chart = alt.Chart(df).mark_arc(outerRadius=radius).encode(
        theta=alt.Theta("count:Q"),
        color=alt.Color("outcome:N", scale=alt.Scale(
            domain=["Heads", "Tails"],
            range=["#4CAF50", "#FF5722"]
        )),
        tooltip=["outcome", "count"]
    ).properties(
        title=f"{control.value} coin flips"
    )

    mo.ui.altair_chart(chart)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Some cool things about Marimo

    - **Reactivity**: Cells automatically re-run when their dependencies change — no need to manually re-execute downstream cells. Try moving the slider above and watch the chart update instantly.
    - **No hidden state**: Unlike Jupyter, you can't have stale variables. Delete a cell and its variables are gone. Try deleting the results cell and watch the chart cell show an error.
    - **Pure Python files**: Notebooks are stored as `.py` files, not JSON — making diffs, code review, and version control painless. Open this file in your editor to see for yourself.
    - **Run as an app**: Run `marimo run notebooks/my-notebook.py` in your terminal to view this notebook as a read-only interactive app with the code hidden.
    - **Run as a script**: Run `python notebooks/my-notebook.py` to execute the notebook top-to-bottom as a plain Python script.
    - **Built-in UI elements**: Sliders, dropdowns, tables, file uploads, and more — all reactive out of the box. Try `mo.ui` tab-completion in a cell to see what's available.
    - **Deterministic execution**: Marimo understands the dependency graph between cells, so execution order is always consistent regardless of cell position. Try rearranging cells by dragging them.
    """)
    return


if __name__ == "__main__":
    app.run()
