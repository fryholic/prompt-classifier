# src/prompt_classifier/gemini_classifier.py

import os
import json
import google.generativeai as genai
from src.prompt_classifier.utils import load_api_key

def preprocess_prompt(raw_prompt: str) -> str:
    """API에 보내기 전 프롬프트를 전처리합니다."""
    tags = [tag.strip() for tag in raw_prompt.split(',') if tag.strip()]
    unique_tags = list(dict.fromkeys(tags))
    return ", ".join(unique_tags)

def classify_prompt_with_gemini(prompt: str, model_name: str = "gemini-1.5-flash") -> dict:
    """
    주어진 프롬프트를 Gemini API를 사용하여 분류하고 결과를 JSON(dict)으로 반환합니다.
    """
    try:
        api_key = load_api_key()
        genai.configure(api_key=api_key)
    except ValueError as e:
        print(f"API 키 로딩 오류: {e}")
        return {"error": str(e)}

    generation_config = {
        "response_mime_type": "application/json",
        "temperature": 0.0,
    }

    model = genai.GenerativeModel(
        model_name,
        generation_config=generation_config
    )

    instruction_prompt = """
    You are an expert AI specializing in classifying image generation prompt tags.
    Your task is to classify a given list of comma-separated tags into 9 distinct categories.
    You must follow a strict two-step process:

    **Step 1: Reasoning.**
    For each tag, you must first determine the single most appropriate category based on the detailed definitions below. You must justify your choice internally.

    **Step 2: JSON Output.**
    After analyzing all tags, consolidate your findings into a single, valid JSON object.

    # CRITICAL RULES:
    1.  **One Category Only**: Each tag must appear in ONLY ONE category. For example, 'bed sheet' is a prop, not clothing. It must only be in `background_props`.
    2.  **Weighted Tags**: Classify tags with weights (e.g., `(tag:1.2)`, `[tag]`) based on the 'tag' content. Keep the full syntax. `(beautiful face:1.1)` belongs in `body_appearance`, NOT `technical_elements`.

    # Category Definitions:
    1.  `style_artist`: Artist names, art styles, and overall aesthetic. (e.g., `artgerm`, `sketch`, `cinematic`)
    2.  `quality_rendering`: Tags related to image quality, resolution, and lighting. (e.g., `masterpiece`, `4k`, `ultra-detailed`, `ray tracing`)
    3.  `subject`: The identity, count, and species of the main character(s). **This does NOT include descriptions of their appearance.** (e.g., `1girl`, `solo`, `elf`)
    4.  `body_appearance`: Describes the physical features, body parts, and any descriptions of those parts. **This is where tags like `beautiful face`, `blue eyes`, and `braid` belong.** (e.g., `blond hair`, `huge breasts`, `ass`, `braid`)
    5.  `pose_gaze`: The subject's posture, body orientation, and gaze direction. (e.g., `looking at viewer`, `sitting`, `all fours`)
    6.  `clothing_accessories`: Any item **worn by the subject**. (e.g., `dress`, `gloves`, `necklace`, `hairband`)
    7.  `action_situation`: Specific actions the subject is performing or the overall context/situation. **'after sex' is a prime example for this category.** (e.g., `running`, `crying`, `after sex`)
    8.  `background_props`: All **inanimate objects, items, and locations** that are NOT worn by the subject. **'bed sheet' is a prime example for this category.** (e.g., `outdoors`, `on a bed`, `bed sheet`)
    9.  `technical_elements`: LoRA/LyCORIS calls or other specific model-related syntax. (e.g., `<lora:something:1>`)

    Now, analyze the following prompt and provide only the final JSON output.
    """

    processed_prompt = preprocess_prompt(prompt)

    try:
        response = model.generate_content([instruction_prompt, processed_prompt])
        return json.loads(response.text)
    except Exception as e:
        print(f"API 호출 중 오류 발생: {e}")
        return {"error": f"API Error: {e}"}