import json
from groq import Groq
from prompts.image_analysis_prompt import IMAGE_ANALYSIS_SYSTEM_PROMPT
from prompts.outfit_generation_prompt import OUTFIT_SYSTEM_PROMPT
from services.image_service import encode_image_base64

def get_client(api_key):
    return Groq(api_key=api_key)

def analyze_clothing_image(api_key, image_path):
    client = get_client(api_key)
    b64_image = encode_image_base64(image_path)

    response = client.chat.completions.create(
        model="qwen/qwen3.6-27b",
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
        reasoning_effort="none",
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
        model="openai/gpt-oss-120b",
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
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": OUTFIT_SYSTEM_PROMPT},
            {"role": "user", "content": user_context},
        ],
        temperature=0.5,
        max_tokens=2000,  # was 800 — too small once >10 items each need a reasoning sentence
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # The model's reply got cut off mid-JSON (usually because the reasoning
        # dict grew too large for max_tokens). Retry once, telling it to keep
        # per-item reasons very short so the whole response fits.
        retry_context = user_context + "\n\nIMPORTANT: Keep every reasoning sentence under 12 words. Keep the whole JSON response compact."
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": OUTFIT_SYSTEM_PROMPT},
                {"role": "user", "content": retry_context},
            ],
            temperature=0.3,
            max_tokens=2000,
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)  # if this still fails, it'll raise and your existing except-block in outfit_routes.py catches it and prints the traceback