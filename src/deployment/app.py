import gradio as gr
import matplotlib.pyplot as plt
import numpy as np
import io
from PIL import Image

# curve data
x = np.linspace(-5, 5, 400)
y = 2 * x**2 + 2

# where we store clicked points (in data coords)
points_x, points_y = [], []

# fixed figure settings (important for stable pixel <-> data mapping)
FIGSIZE = (6, 4)  # inches
DPI = 100  # dots-per-inch -> figure pixels = figsize * dpi


def make_fig_and_ax():
    """Create a fig/ax with consistent DPI/size and draw the curve + points."""
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    ax.plot(x, y, "b-", linewidth=2, label="y = 2x² + 2")
    if points_x:
        ax.scatter(points_x, points_y, c="red", s=60, label="clicked points", zorder=5)
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("Click to add points")

    # Ensure the canvas is rendered so transforms and sizes are available
    fig.canvas.draw()
    return fig, ax


def fig_to_pil(fig):
    """Save fig to a PIL Image using the same DPI (so pixel dims remain stable)."""
    buf = io.BytesIO()
    # Do NOT use bbox_inches='tight' here — we want consistent mapping
    fig.savefig(buf, format="png", dpi=DPI)
    buf.seek(0)
    img = Image.open(buf).convert("RGB")
    return img


def make_plot():
    """Return PIL image for gr.Image (used as initial display and redraw)."""
    fig, ax = make_fig_and_ax()
    img = fig_to_pil(fig)
    plt.close(fig)
    return img


def add_point(evt: gr.SelectData):
    """
    evt.index -> (px, py) pixel coordinates relative to the image (origin: top-left).
    We convert to Matplotlib display coords (origin: bottom-left) then invert transData.
    """
    px, py = evt.index  # integers

    # recreate the exact same figure to get matching transforms & pixel dims
    fig, ax = make_fig_and_ax()

    # get actual figure pixel width/height (canvas dimensions)
    fig_w_px, fig_h_px = fig.canvas.get_width_height()  # (width, height)

    # convert image pixel coords (origin top-left) -> display coords (origin bottom-left)
    display_x = px
    display_y = fig_h_px - py

    # invert the data transform to get data coordinates
    data_x, data_y = ax.transData.inverted().transform((display_x, display_y))

    plt.close(fig)

    # store and redraw
    points_x.append(data_x)
    points_y.append(data_y)
    return make_plot()


with gr.Blocks() as demo:
    img = gr.Image(value=make_plot(), type="pil", label="Interactive Quadratic Curve")
    img.select(add_point, None, img)

if __name__ == "__main__":
    demo.launch()
