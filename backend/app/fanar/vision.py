"""Oryx-IVU (image/video understanding): read the Arabic text off a photographed book
page so a parent can set the day's target passage from a real book — and, in the eval
harness, read back an Oryx-IG image to check whether it rendered legible Arabic.

Uses the OpenAI vision message shape on the chat endpoint (Fanar-Oryx-IVU-2).
"""
from __future__ import annotations

import base64

from app.fanar.client import openai_client
from app.fanar.models import ORYX_IVU

EXTRACT_PROMPT = (
    "اقرأ النص العربي الظاهر في هذه الصورة واكتبه كما هو تماماً، دون أي شرح أو إضافة. "
    "إن لم يوجد نص عربي واضح فاكتب: لا يوجد نص."
)


def read_image(image_bytes: bytes, prompt: str = EXTRACT_PROMPT,
               mime: str = "image/png", model: str = ORYX_IVU,
               max_tokens: int = 400) -> str:
    """Ask Oryx-IVU a question about an image. Default prompt extracts Arabic text."""
    b64 = base64.b64encode(image_bytes).decode("ascii")
    resp = openai_client().chat.completions.create(
        model=model,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
            ],
        }],
        max_tokens=max_tokens,
        temperature=0.0,
    )
    return (resp.choices[0].message.content or "").strip()
