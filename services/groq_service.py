import json
from groq import Groq
from prompts.image_analysis_prompt import IMAGE_ANALYSIS_SYSTEM_PROMPT
from prompts.outfit_generation_prompt import OUTFIT_SYSTEM_PROMPT
from services.image_service import encode_image_base64

# NOTE: Groq deprecates/renames models periodically.
# If you get a "model_decommissioned" error, check https://console.groq.com/docs/models
# and swap the strings below — nothing else needs to change.
VISION_MODEL = "qwen/qwen3.6-27b"
TEXT_MODEL = "openai/gpt-oss-120b"

def get_client(api_key):
    return Groq(api_key=api_key)

def analyze_clothing_image(api_key, image_path):
    client = get_client(api_key)
    b64_image = encode_image_base64(image_path)

    response = client.chat.completions.create(
        model=VISION_MODEL,
        messages=[
            {"role": "system", "content": IMAGE_ANALYSIS_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analyze this clothing item and return the JSON."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}},
                ],
            },
        ],
        temperature=0.3,
        max_tokens=500,
        reasoning_effort="none",  # forces clean JSON, no "thinking" text before it
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)

def extract_articles_from_pdf_text(api_key, pdf_text):
    client = get_client(api_key)
    prompt = f"""Extract every distinct clothing article from this text. Return ONLY a JSON array,
each element shaped like:
{{"name": "...", "category": "...", "section": "Upper/Lower/Footwear/Accessories",
"color": "...", "material": "...", "description": "..."}}

TEXT:
{pdf_text}
"""
    response = client.chat.completions.create(
        model=TEXT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=2000,
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)

def generate_outfit(api_key, user_profile, weather, occasion, wardrobe_items):
    client = get_client(api_key)
    user_context = f"""
Profile: {json.dumps(user_profile)}
Weather: {json.dumps(weather)}
Occasion: {occasion}
Available items (ONLY choose from these): {json.dumps(wardrobe_items)}
"""
    response = client.chat.completions.create(
        model=TEXT_MODEL,
        messages=[
            {"role": "system", "content": OUTFIT_SYSTEM_PROMPT},
            {"role": "user", "content": user_context},
        ],
        temperature=0.5,
        max_tokens=3000,  # v9: raised from 2000 — now asking for up to 3 full combinations
        # (each with its own reasoning dict + overall_reasoning) in one response.
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # The model's reply got cut off mid-JSON (usually because 3 combinations'
        # worth of reasoning grew too large for max_tokens). Retry once, telling
        # it to keep everything short so the whole response fits.
        retry_context = user_context + "\n\nIMPORTANT: Keep every reasoning sentence under 12 words and every overall_reasoning under 2 short sentences, so all outfit options fit in the response."
        response = client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {"role": "system", "content": OUTFIT_SYSTEM_PROMPT},
                {"role": "user", "content": retry_context},
            ],
            temperature=0.3,
            max_tokens=3000,
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)  # if this still fails, it raises and the existing
        # except-block in outfit_routes.py catches it, prints the traceback, and
        # returns the friendly "internet_error" message to the user