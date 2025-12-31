import json
import ollama

class VisionAuditor:
    def __init__(self, model="gemma3"):
        self.model = model

    def analyze_screenshot(self, image_path):
        prompt = """You are an ecommerce QC auditor.
Analyze the screenshot and respond ONLY in valid JSON.

{
  "blocked": true or false,
  "blocker_type": "popup | cookie | age-gate | newsletter | none",
  "close_button": {
    "exists": true or false,
    "visual_description": "what the button looks like",
    "likely_text": ["x", "close", "accept", "agree"]
  },
  "qc_issues": [
    "short bullet points describing visible credibility, UX, or clarity problems"
  ]
}

No extra text. No markdown. JSON only."""

        response = ollama.generate(
            model=self.model,
            prompt=prompt,
            images=[image_path]
        )
        
        # Parse result (simplification for v0)
        try:
            return json.loads(response['response'])
        except:
            return {"blocked": False, "qc_issues": ["Error parsing vision output"]}