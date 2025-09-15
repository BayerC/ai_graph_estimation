import gradio as gr
from fastai.vision.all import load_learner
from pathlib import Path

script_dir = Path(__file__).parent
learner = load_learner(script_dir / "export.pkl")


def predict(image):
    pred_class, pred_idx, probs = learner.predict(image)
    return pred_class


examples_dir = script_dir / "examples"
demo = gr.Interface(
    fn=predict,
    inputs="image",
    outputs="text",
    examples=[
        str(examples_dir / "linear.png"),
        str(examples_dir / "quadratic.png"),
        str(examples_dir / "cubic.png"),
    ],
)
demo.launch()
