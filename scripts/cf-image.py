#!/usr/bin/env python3
"""Generate images using Cloudflare Workers AI.

Default: flux-1-schnell (cheapest, ~173 images/day on free tier).
Pass --model to upgrade to premium models.
"""
import os
import sys
import json
import base64
import time
import requests
import argparse
from pathlib import Path

DEFAULT_MODEL = "@cf/black-forest-labs/flux-1-schnell"
JSON_MODELS = {DEFAULT_MODEL}

env_path = Path.home() / ".pi" / "agent" / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip().strip('"')
else:
    print("Error: ~/.pi/agent/.env not found", file=sys.stderr)
    sys.exit(1)

ACCOUNT_ID = os.environ["CLOUDFLARE_ID"]
API_KEY = os.environ["CLOUDFLARE_API_KEY"]
API_URL = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run"


def generate_image(prompt, model=DEFAULT_MODEL, width=1024, height=576,
                   guidance=7.5, num_steps=4, negative_prompt="", seed=None, output="output.png"):
    """Generate an image using Cloudflare Workers AI."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            if model in JSON_MODELS:
                payload = {"prompt": prompt, "width": width, "height": height,
                           "guidance": guidance, "num_steps": num_steps}
                if negative_prompt:
                    payload["negative_prompt"] = negative_prompt
                if seed is not None:
                    payload["seed"] = seed
                resp = requests.post(
                    f"{API_URL}/{model}",
                    headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                    json=payload, timeout=90,
                )
            else:
                fields = {"prompt": prompt, "width": str(width), "height": str(height),
                          "guidance": str(guidance), "num_steps": str(num_steps)}
                if negative_prompt:
                    fields["negative_prompt"] = negative_prompt
                if seed is not None:
                    fields["seed"] = str(seed)
                resp = requests.post(
                    f"{API_URL}/{model}",
                    headers={"Authorization": f"Bearer {API_KEY}"},
                    files={k: (None, v) for k, v in fields.items()}, timeout=90,
                )

            if resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", 2 ** (attempt + 1)))
                print(f"⏳ Rate limited, waiting {retry_after}s...", file=sys.stderr)
                time.sleep(retry_after)
                continue
            if resp.status_code >= 500:
                wait = 2 ** (attempt + 1)
                print(f"⏳ Server error {resp.status_code}, retrying in {wait}s...", file=sys.stderr)
                time.sleep(wait)
                continue
            resp.raise_for_status()
            data = resp.json()

            if "result" not in data or "image" not in data["result"]:
                raise ValueError(f"Missing image in response: {data.get('errors', data)}")
            img_b64 = data["result"]["image"]
            if not img_b64 or not isinstance(img_b64, str):
                raise ValueError("Empty or invalid image data")
            img_bytes = base64.b64decode(img_b64)
            if len(img_bytes) < 100:
                raise ValueError(f"Image data too small ({len(img_bytes)} bytes)")
            with open(output, "wb") as f:
                f.write(img_bytes)
            print(f"✅ Saved {output} ({len(img_bytes)} bytes)")
            return True

        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                wait = 2 ** (attempt + 1)
                print(f"⏳ Timeout, retrying in {wait}s...", file=sys.stderr)
                time.sleep(wait)
                continue
            raise
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1 and hasattr(e, "response") and e.response is not None and e.response.status_code >= 500:
                wait = 2 ** (attempt + 1)
                print(f"⏳ Request failed ({e}), retrying in {wait}s...", file=sys.stderr)
                time.sleep(wait)
                continue
            raise
    print(f"❌ Failed after {max_retries} attempts", file=sys.stderr)
    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate images with Cloudflare AI")
    parser.add_argument("prompt", help="Text description of the image")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--output", "-o", default="output.png")
    parser.add_argument("--width", type=int, default=1024)
    parser.add_argument("--height", type=int, default=576)
    parser.add_argument("--steps", type=int, default=4)
    parser.add_argument("--guidance", type=float, default=7.5)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--negative", "-n", default="")
    parser.add_argument("--fallback", action="store_true")
    args = parser.parse_args()

    if not args.prompt or len(args.prompt.strip()) == 0:
        print("❌ Error: Prompt cannot be empty", file=sys.stderr)
        sys.exit(1)
    if len(args.prompt) > 10000:
        print("❌ Error: Prompt too long", file=sys.stderr)
        sys.exit(1)
    if args.width % 32 != 0 or args.height % 32 != 0:
        print(f"❌ Error: dimensions must be multiples of 32 (got {args.width}x{args.height})", file=sys.stderr)
        sys.exit(1)

    ok = generate_image(prompt=args.prompt, model=args.model, width=args.width,
                        height=args.height, guidance=args.guidance, num_steps=args.steps,
                        negative_prompt=args.negative, seed=args.seed, output=args.output)

    if not ok and args.fallback and args.model != DEFAULT_MODEL:
        base, ext = os.path.splitext(args.output)
        fallback_output = f"{base}_fallback{ext}"
        ok = generate_image(prompt=args.prompt, model=DEFAULT_MODEL, width=args.width,
                            height=args.height, guidance=args.guidance, num_steps=args.steps,
                            negative_prompt=args.negative, seed=args.seed, output=fallback_output)
        if ok:
            print(f"💡 Fallback succeeded → {fallback_output}", file=sys.stderr)

    sys.exit(0 if ok else 1)
