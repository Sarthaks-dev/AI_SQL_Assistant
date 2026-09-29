"""
generate_architecture_diagram.py — Architecture Diagram Generator

Generates a clean, professional architecture diagram saved as docs/architecture.png
suitable for technical reports and presentations.
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_architecture():
    docs_dir = os.path.join(os.path.dirname(__file__), "docs")
    os.makedirs(docs_dir, exist_ok=True)
    out_path = os.path.join(docs_dir, "architecture.png")

    fig, ax = plt.subplots(figsize=(14, 11), dpi=300)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 11)
    ax.axis("off")

    # Title
    ax.text(7, 10.5, "AI SQL Query Generator & Database Assistant",
            ha="center", va="center", fontsize=18, fontweight="bold", color="#1a237e")
    ax.text(7, 10.1, "System Architecture & Request Execution Flow",
            ha="center", va="center", fontsize=12, style="italic", color="#424242")

    # Helper function to draw rounded boxes
    def draw_box(x, y, w, h, text, subtext="", color="#e3f2fd", border="#1565c0", text_color="#0d47a1"):
        box = patches.FancyBboxPatch(
            (x - w / 2, y - h / 2), w, h,
            boxstyle="round,pad=0.2,rounding_size=0.15",
            facecolor=color, edgecolor=border, linewidth=2, zorder=2
        )
        ax.add_patch(box)
        if subtext:
            ax.text(x, y + 0.15, text, ha="center", va="center",
                    fontsize=11, fontweight="bold", color=text_color, zorder=3)
            ax.text(x, y - 0.2, subtext, ha="center", va="center",
                    fontsize=8.5, color="#37474f", zorder=3)
        else:
            ax.text(x, y, text, ha="center", va="center",
                    fontsize=11, fontweight="bold", color=text_color, zorder=3)

    # Helper function to draw arrows
    def draw_arrow(x1, y1, x2, y2, label="", color="#455a64", style="-|>"):
        ax.annotate(
            "", xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(arrowstyle=style, color=color, lw=2, mutation_scale=15),
            zorder=4
        )
        if label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            ax.text(mx + 0.15, my, label, fontsize=9, fontweight="bold", color=color, zorder=5)

    # 1. User
    draw_box(7, 9.2, 3.2, 0.7, "[ USER ]", "Enters Natural Language Question", "#e8eaf6", "#3f51b5", "#1a237e")

    # Arrow User -> Streamlit
    draw_arrow(7, 8.8, 7, 8.2)

    # 2. Streamlit UI
    draw_box(7, 7.8, 4.2, 0.7, "Streamlit Web UI", "Input Form, Schema Browser, Status", "#e1f5fe", "#0288d1", "#01579b")

    # Arrow Streamlit -> Groq LLM
    draw_arrow(7, 7.4, 7, 6.7, "NL Prompt + Schema")

    # 3. Groq LLM
    draw_box(7, 6.3, 3.8, 0.7, "Groq LLM Engine", "openai/gpt-oss-120b", "#ede7f6", "#7e57c2", "#311b92")

    # Arrow Groq -> SQL Generator
    draw_arrow(7, 5.9, 7, 5.2)

    # 4. SQL Generator
    draw_box(7, 4.8, 3.6, 0.7, "SQL Query Generator", "Clean & Format MySQL Query", "#f3e5f5", "#ab47bc", "#4a148c")

    # Arrow SQL Generator -> Validator
    draw_arrow(7, 4.4, 7, 3.7)

    # 5. SQL Validator (Decision Point)
    draw_box(7, 3.3, 3.8, 0.7, "SQL Safety Validator", "Keyword & Statement Inspection", "#fff8e1", "#ffa000", "#e65100")

    # Branch 1: UNSAFE -> Rejection
    draw_arrow(5.0, 3.3, 2.6, 3.3, "UNSAFE", "#c62828")
    draw_box(1.5, 3.3, 2.2, 0.7, "REJECT / BLOCK", "Security Warning", "#ffebee", "#e53935", "#b71c1c")

    # Branch 2: SAFE -> MySQL Database
    draw_arrow(7, 2.9, 7, 2.2, "SAFE (Read-Only)", "#2e7d32")
    draw_box(7, 1.8, 4.4, 0.7, "MySQL Database (ai_sales)", "customers, products, orders", "#e8f5e9", "#43a047", "#1b5e20")

    # Arrow MySQL -> Results
    draw_arrow(9.3, 1.8, 10.8, 1.8)
    draw_arrow(10.8, 1.8, 10.8, 3.0)

    # 6. Results
    draw_box(10.8, 3.5, 3.4, 0.8, "Query Results", "Pandas DataFrame", "#e0f2f1", "#00897b", "#004d40")

    # Results -> Table & Chart
    draw_arrow(10.8, 4.0, 10.8, 4.8)
    draw_box(9.2, 5.3, 2.2, 0.6, "Data Table", "Interactive Grid", "#f1f8e9", "#7cb342", "#33691e")
    draw_box(12.4, 5.3, 2.2, 0.6, "Auto Chart", "Bar / Line / Pie", "#f1f8e9", "#7cb342", "#33691e")

    # Results -> SQL Explanation
    draw_arrow(10.8, 5.7, 10.8, 6.7)
    draw_box(10.8, 7.2, 3.4, 0.7, "AI SQL Explanation", "Plain English Breakdown", "#fff3e0", "#fb8c00", "#e65100")

    # Explanation back to UI
    draw_arrow(9.0, 7.5, 9.0, 7.8)

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Architecture diagram generated: {out_path}")


if __name__ == "__main__":
    draw_architecture()
