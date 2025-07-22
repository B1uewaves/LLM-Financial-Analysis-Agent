import json
import pytest
from prompts.templates import load_prompts

# Load the prompts registry at test‐time
PROMPTS = load_prompts()

@pytest.mark.parametrize("name", ["summary_template"])
def test_prompt_includes_markers(name):
    prompt_entry = PROMPTS[name]["prompt"]
    rendered = prompt_entry.format(input_data=json.dumps({"ticker": "GOOG"}))

    # Must include a few‐shot example
    assert "Example:" in rendered, f"{name} missing few‐shot example"

    # Must include some kind of output marker
    output_markers = ["Output:", "Now summarize:", "Now compare:", "Now forecast:"]
    assert any(marker in rendered for marker in output_markers), \
        f"{name} missing output marker (one of {output_markers})"
