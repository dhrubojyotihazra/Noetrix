/**
 * Token segmentation and keyword highlighting utilities.
 * Adapted clean-room from Resume-Matcher regex boundary pattern.
 */

export interface TextSegment {
  text: string;
  isMatch: boolean;
}

export function segmentTextByKeywords(
  text: string,
  keywords: string[]
): TextSegment[] {
  if (!text || !keywords || keywords.length === 0) {
    return [{ text: text || "", isMatch: false }];
  }

  // Filter non-empty lowercased keywords
  const cleanKws = keywords
    .map((k) => k.trim().toLowerCase())
    .filter((k) => k.length > 1);

  if (cleanKws.length === 0) {
    return [{ text, isMatch: false }];
  }

  // Create escaped alternation regex pattern
  const escaped = cleanKws.map((k) => k.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
  const regex = new RegExp(`(\\b(?:${escaped.join("|")})\\b)`, "gi");

  const parts = text.split(regex);
  const segments: TextSegment[] = [];

  for (const part of parts) {
    if (!part) continue;
    const isMatch = cleanKws.includes(part.toLowerCase());
    segments.push({ text: part, isMatch });
  }

  return segments;
}
