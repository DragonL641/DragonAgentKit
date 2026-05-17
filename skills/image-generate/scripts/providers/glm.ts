import type { CliArgs } from "../types";

function validateBaseUrl(url: string): string {
  try {
    const parsed = new URL(url);
    if (!parsed.hostname.endsWith(".bigmodel.cn")) {
      throw new Error(`Base URL hostname "${parsed.hostname}" is not allowed. Expected: *.bigmodel.cn`);
    }
    return url;
  } catch (e) {
    if (e instanceof TypeError) throw new Error(`Invalid GLM_BASE_URL: ${url}`);
    throw e;
  }
}

export function getDefaultModel(): string {
  return process.env.GLM_IMAGE_MODEL || "glm-image";
}

function getApiKey(): string | null {
  return process.env.GLM_API_KEY || null;
}

function getBaseUrl(): string {
  const base = validateBaseUrl(process.env.GLM_BASE_URL || "https://open.bigmodel.cn/api/paas/v4");
  return base.replace(/\/+$/g, "");
}

function parseAspectRatio(ar: string): { width: number; height: number } | null {
  const match = ar.match(/^(\d+(?:\.\d+)?):(\d+(?:\.\d+)?)$/);
  if (!match) return null;
  const w = parseFloat(match[1]!);
  const h = parseFloat(match[2]!);
  if (w <= 0 || h <= 0) return null;
  return { width: w, height: h };
}

function getSizeFromAspectRatio(ar: string | null, quality: CliArgs["quality"]): string {
  const baseSize = quality === "2k" ? 1440 : 1024;

  if (!ar) return `${baseSize}x${baseSize}`;

  const parsed = parseAspectRatio(ar);
  if (!parsed) return `${baseSize}x${baseSize}`;

  const ratio = parsed.width / parsed.height;

  // GLM-Image recommended presets mapping
  if (Math.abs(ratio - 16 / 9) < 0.1) {
    return quality === "2k" ? "1728x960" : "1280x720";
  }
  if (Math.abs(ratio - 9 / 16) < 0.1) {
    return quality === "2k" ? "960x1728" : "720x1280";
  }
  if (Math.abs(ratio - 4 / 3) < 0.1) {
    return quality === "2k" ? "1472x1088" : "1024x768";
  }
  if (Math.abs(ratio - 3 / 4) < 0.1) {
    return quality === "2k" ? "1088x1472" : "768x1024";
  }
  if (Math.abs(ratio - 1) < 0.1) {
    return quality === "2k" ? "1280x1280" : "1024x1024";
  }

  // Custom ratio: compute size, round to nearest 32
  if (ratio > 1) {
    const w = Math.round((baseSize * ratio) / 32) * 32;
    return `${w}x${baseSize}`;
  }
  const h = Math.round((baseSize / ratio) / 32) * 32;
  return `${baseSize}x${h}`;
}

export async function generateImage(
  prompt: string,
  model: string,
  args: CliArgs
): Promise<Uint8Array> {
  const apiKey = getApiKey();
  if (!apiKey) throw new Error("GLM_API_KEY is required. Set it in ~/.claude/skills/image-generate.env");

  if (args.referenceImages.length > 0) {
    throw new Error(
      "Reference images are not supported with GLM provider. Use --provider google with a Gemini multimodal model."
    );
  }

  const size = args.size || getSizeFromAspectRatio(args.aspectRatio, args.quality);
  const url = `${getBaseUrl()}/images/generations`;

  const body: Record<string, string> = {
    model,
    prompt,
    size,
  };

  console.log(`Generating image with GLM (${model})...`, { size });

  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(`GLM API error (${res.status}): ${err}`);
  }

  const result = (await res.json()) as {
    data?: Array<{ url?: string; b64_json?: string }>;
  };

  const imageResult = result.data?.[0];
  if (!imageResult) {
    console.error("Response:", JSON.stringify(result, null, 2));
    throw new Error("No image in GLM response");
  }

  if (imageResult.url) {
    const imgRes = await fetch(imageResult.url);
    if (!imgRes.ok) throw new Error(`Failed to download image (${imgRes.status})`);
    const buf = await imgRes.arrayBuffer();
    return new Uint8Array(buf);
  }

  if (imageResult.b64_json) {
    return Uint8Array.from(Buffer.from(imageResult.b64_json, "base64"));
  }

  console.error("Response:", JSON.stringify(result, null, 2));
  throw new Error("No image URL or base64 data in GLM response");
}
