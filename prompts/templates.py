import yaml
from pathlib import Path
from langchain.prompts import PromptTemplate

def load_prompts(path: Path = Path(__file__).parent) -> dict:
    registry = {}
    for f in path.glob("*.yaml"):
        data = yaml.safe_load(f.read_text(encoding="utf-8"))
        
        # Build few-shot example blocks, if any
        few_shot = data.get("few_shot", [])
        example_blocks = []
        for ex in few_shot:
            block = (
                "Example:\n"
                f"Input:\n{ex['input'].strip()}\n\n"
                f"Output:\n{ex['output'].strip()}\n"
            )
            example_blocks.append(block)
        few_shot_section = "\n\n".join(example_blocks)

        # Combine description, few-shot examples, and main template
        parts = [
            data.get("description", "").strip(),
            few_shot_section,
            data["template"].strip()
        ]
        full_template = "\n\n".join([p for p in parts if p])

        prompt = PromptTemplate(
            input_variables=[
                "ticker", "current_price", "pct_change", "trend_30d",
                "volume", "bid_ask", "day_range", "market_cap",
                "pe_ratio", "headlines", "today"
            ],
            template=full_template
        )

        registry[f.stem] = {
            "version": data["version"],
            "description": data["description"],
            "few_shot": few_shot,   # raw examples for testing/inspection
            "prompt": prompt
        }
    return registry

PROMPTS = load_prompts()
