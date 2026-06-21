import { NextRequest, NextResponse } from "next/server";

// ── Config ───────────────────────────────────────────────────────────────────
const OCR_ENDPOINT =
  process.env.OCR_ENDPOINT ??
  "https://ceo.aura-intelligence.ch/api/v1/ocr-verify";
const N8N_WEBHOOK =
  process.env.N8N_LEGACY_WEBHOOK ??
  "https://aura-intelligence.ch/webhook/legacy-grant";
const MAX_BYTES = 8 * 1024 * 1024; // 8 MB — matches VerifyForm client-side limit
const ALLOWED_TYPES = new Set([
  "image/jpeg",
  "image/png",
  "image/webp",
  "application/pdf",
]);

// ── Helpers ──────────────────────────────────────────────────────────────────

/** Normalise a name for comparison: lowercase, collapse whitespace, strip punctuation */
function normaliseName(raw: string): string {
  return raw
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "") // strip diacritics
    .replace(/[^a-z\s]/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

/**
 * Fuzzy name match: accepts if every token in billingName appears in idName
 * (handles middle-name omissions & minor OCR artefacts like missing hyphen).
 * Requires at least a 2-token full match to prevent single-word passes.
 */
function namesMatch(idName: string, billingName: string): boolean {
  const idTokens = normaliseName(idName).split(" ").filter(Boolean);
  const billingTokens = normaliseName(billingName).split(" ").filter(Boolean);
  if (billingTokens.length < 2) return false;
  // Every billing token must appear somewhere in the ID name tokens
  return billingTokens.every((t) => idTokens.includes(t));
}

// ── Route handler ────────────────────────────────────────────────────────────
export async function POST(req: NextRequest) {
  let formData: FormData;
  try {
    formData = await req.formData();
  } catch {
    return NextResponse.json(
      { detail: "Invalid multipart request." },
      { status: 400 },
    );
  }

  // ── Extract fields ────────────────────────────────────────────────────────
  const fullName = (formData.get("full_name") as string | null)?.trim() ?? "";
  const email =
    (formData.get("email") as string | null)?.trim().toLowerCase() ?? "";
  const billingName =
    (formData.get("billing_name") as string | null)?.trim() ?? "";
  const country = (formData.get("country") as string | null)?.trim() ?? "";
  const reason = (formData.get("reason") as string | null)?.trim() ?? "";

  if (!fullName || !email || !billingName) {
    return NextResponse.json(
      { detail: "full_name, email, and billing_name are required." },
      { status: 400 },
    );
  }

  // ── Validate files ────────────────────────────────────────────────────────
  const idFile = formData.get("id_document") as File | null;
  const incomeFile = formData.get("income_proof") as File | null;

  if (!idFile || !incomeFile) {
    return NextResponse.json(
      { detail: "Both id_document and income_proof are required." },
      { status: 400 },
    );
  }

  for (const [fieldName, file] of [
    ["id_document", idFile],
    ["income_proof", incomeFile],
  ] as [string, File][]) {
    if (!ALLOWED_TYPES.has(file.type)) {
      return NextResponse.json(
        {
          detail: `${fieldName}: invalid file type. Allowed: JPG, PNG, WEBP, PDF.`,
        },
        { status: 400 },
      );
    }
    if (file.size > MAX_BYTES) {
      return NextResponse.json(
        { detail: `${fieldName}: file too large (max 8 MB).` },
        { status: 400 },
      );
    }
  }

  // ── Call OCR endpoint (Hetzner server) ────────────────────────────────────
  let extractedName = "";
  try {
    const ocrForm = new FormData();
    ocrForm.append("id_document", idFile);

    const ocrRes = await fetch(OCR_ENDPOINT, {
      method: "POST",
      body: ocrForm,
      signal: AbortSignal.timeout(30_000), // 30s timeout
    });

    if (!ocrRes.ok) {
      const text = await ocrRes.text();
      console.error("[legacy-grant] OCR endpoint error:", ocrRes.status, text);
      return NextResponse.json(
        {
          detail:
            "Document processing failed. Please try again or contact hello@aura-intelligence.ch",
        },
        { status: 502 },
      );
    }

    const ocrData: { extracted_name?: string } = await ocrRes.json();
    extractedName = ocrData.extracted_name ?? "";
  } catch (err) {
    console.error("[legacy-grant] OCR fetch error:", err);
    return NextResponse.json(
      { detail: "Could not reach the verification service. Please try again." },
      { status: 503 },
    );
  }

  // ── Identity Lock: name on ID must match billing name ────────────────────
  if (!extractedName || !namesMatch(extractedName, billingName)) {
    console.warn(
      `[legacy-grant] Name mismatch: extracted="${extractedName}" billing="${billingName}" email="${email}"`,
    );
    return NextResponse.json(
      {
        status: "name_mismatch",
        detail:
          `The name extracted from your ID ("${extractedName || "— could not read —"}") ` +
          `does not match your billing name ("${billingName}"). ` +
          `Please re-submit with your legal name exactly as it appears on your ID.`,
      },
      { status: 422 },
    );
  }

  // ── Forward to n8n for Stripe link generation + email ────────────────────
  try {
    const n8nPayload = {
      full_name: fullName,
      email,
      billing_name: billingName,
      country,
      reason,
      extracted_name: extractedName,
      status: "identity_verified",
      tier: "legacy-grant",
      amount_cents: 4900,
      currency: "usd",
      installments: 24,
      exports_per_mo: 25,
      submitted_at: new Date().toISOString(),
    };

    const n8nRes = await fetch(N8N_WEBHOOK, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(n8nPayload),
      signal: AbortSignal.timeout(20_000),
    });

    if (!n8nRes.ok) {
      console.error(
        "[legacy-grant] n8n webhook error:",
        n8nRes.status,
        await n8nRes.text(),
      );
      // Non-fatal: identity was verified, just n8n notification failed
      // Still return success — the team can manually send the Stripe link
    }
  } catch (err) {
    console.error("[legacy-grant] n8n fetch error:", err);
    // Non-fatal — identity verified
  }

  return NextResponse.json({ status: "approved" });
}
