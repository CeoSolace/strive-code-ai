# app/core/multimodal.py
import os
from weasyprint import HTML
from gtts import gTTS
import matplotlib.pyplot as plt
import networkx as nx
from jupyter import notebook
from typing import Dict, Any
import base64

def generate_pdf(task: Dict[str, Any]) -> Dict[str, Any]:
    title = task.get("title", "Strive-Code Output")
    code = task.get("code", "")
    explanation = task.get("explanation", "")

    html = f"""
    <h1>{title}</h1>
    <h2>Code</h2>
    <pre><code>{code}</code></pre>
    <h2>Explanation</h2>
    <p>{explanation}</p>
    """
    output_path = "/tmp/output.pdf"
    HTML(string=html).write_pdf(output_path)
    return {"pdf": _encode_file(output_path), "path": output_path}

def generate_diagram(task: Dict[str, Any]) -> Dict[str, Any]:
    code = task.get("code", "")
    kind = task.get("kind", "flow")

    G = nx.DiGraph()
    G.add_edges_from([("Start", "Process"), ("Process", "End")])
    plt.figure(figsize=(8, 6))
    nx.draw(G, with_labels=True, node_color='lightblue', node_size=2000)
    path = "/tmp/diagram.png"
    plt.savefig(path)
    plt.close()
    return {"image": _encode_file(path), "path": path}

def generate_voice(task: Dict[str, Any]) -> Dict[str, Any]:
    text = task.get("text", "Strive-Code AI speaking.")
    path = "/tmp/voice.mp3"
    tts = gTTS(text)
    tts.save(path)
    return {"audio": _encode_file(path), "path": path}

def generate_jupyter(task: Dict[str, Any]) -> Dict[str, Any]:
    code = task.get("code", "")
    explanation = task.get("explanation", "")
    nb = notebook.new_notebook()
    nb.cells.append(notebook.new_code_cell(code))
    nb.cells.append(notebook.new_markdown_cell(explanation))
    path = "/tmp/notebook.ipynb"
    notebook.write(nb, path)
    return {"notebook": _encode_file(path), "path": path}

def _encode_file(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()
