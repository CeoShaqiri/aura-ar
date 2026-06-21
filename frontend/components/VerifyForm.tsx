"use client";

import { useState, useRef, type ChangeEvent, type FormEvent } from "react";

// ── File validation ──────────────────────────────────────────────────────────
const ALLOWED_TYPES = [
  "image/jpeg",
  "image/png",
  "image/webp",
  "application/pdf",
];
const MAX_BYTES = 8 * 1024 * 1024; // 8 MB per file
const ALLOWED_LABEL = "JPG, PNG, WEBP or PDF · max 8 MB";

function validateFile(file: File): string | null {
  if (!ALLOWED_TYPES.includes(file.type))
    return `Invalid file type. ${ALLOWED_LABEL}`;
  if (file.size > MAX_BYTES) return "File too large. Max 8 MB.";
  return null;
}

// ── Sub-components ──────────────────────────────────────────────────────────
function FieldLabel({ children }: { children: React.ReactNode }) {
  return (
    <label className="block text-[10px] tracking-[0.4em] uppercase text-white/30 mb-2">
      {children}
    </label>
  );
}

function TextInput({
  name,
  placeholder,
  value,
  onChange,
  required,
  type = "text",
}: {
  name: string;
  placeholder: string;
  value: string;
  onChange: (v: string) => void;
  required?: boolean;
  type?: string;
}) {
  return (
    <input
      name={name}
      type={type}
      placeholder={placeholder}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      required={required}
      autoComplete="off"
      className="w-full bg-white/[0.04] border border-white/[0.08] rounded-xl px-4 py-3 text-white text-sm placeholder-white/20 outline-none focus:border-[#AC7B78]/50 focus:bg-white/[0.06] transition-all"
    />
  );
}

function FileUploadBox({
  label,
  hint,
  accept,
  file,
  onChange,
  error,
}: {
  label: string;
  hint: string;
  accept: string;
  file: File | null;
  onChange: (f: File | null) => void;
  error?: string;
}) {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.files?.[0] ?? null);
  };

  return (
    <div>
      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        className="w-full rounded-xl border border-dashed border-white/[0.12] bg-white/[0.03] py-8 px-5 text-center transition-all duration-200 hover:border-[#AC7B78]/40 hover:bg-white/[0.05] focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#AC7B78]/50"
        aria-label={`Upload ${label}`}
      >
        {file ? (
          <div className="flex flex-col items-center gap-2">
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              aria-hidden
            >
              <polygon
                points="12,2 22,12 12,22 2,12"
                stroke="#AC7B78"
                strokeWidth="1.2"
                fill="rgba(172,123,120,0.12)"
              />
              <polyline
                points="8,12 11,15 16,9"
                stroke="#AC7B78"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                fill="none"
              />
            </svg>
            <span className="text-[#AC7B78] text-xs tracking-wide">
              {file.name}
            </span>
            <span className="text-white/20 text-[10px]">
              {(file.size / 1024).toFixed(0)} KB · Click to replace
            </span>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3">
            <svg
              width="28"
              height="28"
              viewBox="0 0 28 28"
              fill="none"
              className="opacity-30"
              aria-hidden
            >
              <rect
                x="4"
                y="4"
                width="20"
                height="20"
                rx="4"
                stroke="white"
                strokeWidth="1.2"
              />
              <path
                d="M14 18V10M10 14l4-4 4 4"
                stroke="white"
                strokeWidth="1.2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <div>
              <p className="text-white/50 text-sm">{label}</p>
              <p className="text-white/20 text-[10px] mt-0.5">{hint}</p>
            </div>
          </div>
        )}
      </button>
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        className="sr-only"
        onChange={handleChange}
        tabIndex={-1}
        aria-hidden
      />
      {error && <p className="mt-1.5 text-red-400 text-[11px]">{error}</p>}
    </div>
  );
}

// ── Status states ────────────────────────────────────────────────────────────
type FormState = "idle" | "submitting" | "success" | "rejected" | "error";

// ── Main Form ────────────────────────────────────────────────────────────────
export default function VerifyForm() {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [billingName, setBillingName] = useState("");
  const [country, setCountry] = useState("");
  const [reason, setReason] = useState("");
  const [idFile, setIdFile] = useState<File | null>(null);
  const [incomeFile, setIncomeFile] = useState<File | null>(null);
  const [idError, setIdError] = useState<string | undefined>();
  const [incomeError, setIncomeError] = useState<string | undefined>();
  const [formState, setFormState] = useState<FormState>("idle");
  const [serverMessage, setServerMessage] = useState("");

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    // Client-side file validation
    let valid = true;
    if (!idFile) {
      setIdError("Please upload a photo or scan of your government-issued ID.");
      valid = false;
    } else {
      const err = validateFile(idFile);
      if (err) {
        setIdError(err);
        valid = false;
      } else setIdError(undefined);
    }
    if (!incomeFile) {
      setIncomeError("Please upload proof of student status or low-income.");
      valid = false;
    } else {
      const err = validateFile(incomeFile);
      if (err) {
        setIncomeError(err);
        valid = false;
      } else setIncomeError(undefined);
    }
    if (!valid) return;

    setFormState("submitting");

    const fd = new FormData();
    fd.append("full_name", fullName.trim());
    fd.append("email", email.trim().toLowerCase());
    fd.append("billing_name", billingName.trim());
    fd.append("country", country.trim());
    fd.append("reason", reason.trim());
    fd.append("id_document", idFile!);
    fd.append("income_proof", incomeFile!);

    try {
      const res = await fetch("/api/legacy-grant", {
        method: "POST",
        body: fd,
      });
      const data = await res.json();

      if (res.status === 200 && data.status === "approved") {
        setFormState("success");
      } else if (res.status === 422 && data.status === "name_mismatch") {
        setFormState("rejected");
        setServerMessage(
          data.detail ??
            "The name on your ID does not match your billing name.",
        );
      } else {
        setFormState("error");
        setServerMessage(
          data.detail ??
            "Something went wrong. Please try again or email hello@theaurastandard.com",
        );
      }
    } catch {
      setFormState("error");
      setServerMessage("Network error. Please try again.");
    }
  };

  // ── Post-submit states ───────────────────────────────────────────────────
  if (formState === "success") {
    return (
      <div className="glass noise rounded-3xl p-10 text-center relative overflow-hidden">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#AC7B78] to-transparent" />
        <svg
          width="48"
          height="48"
          viewBox="0 0 48 48"
          fill="none"
          className="mx-auto mb-6"
          aria-hidden
        >
          <polygon
            points="24,3 45,24 24,45 3,24"
            stroke="#AC7B78"
            strokeWidth="1.5"
            fill="rgba(172,123,120,0.1)"
          />
          <polyline
            points="16,24 21,29 32,18"
            stroke="#AC7B78"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            fill="none"
          />
        </svg>
        <p className="text-gold text-[10px] tracking-[0.5em] uppercase mb-3">
          Application received
        </p>
        <h3 className="text-2xl font-extralight text-white mb-4">
          Identity Verified.
        </h3>
        <p className="text-white/40 text-sm leading-relaxed max-w-sm mx-auto">
          Your documents are being reviewed. If your application is approved,
          you will receive a Stripe payment link at{" "}
          <strong className="text-white/60">{email}</strong> within 24 hours.
        </p>
      </div>
    );
  }

  if (formState === "rejected") {
    return (
      <div className="glass noise rounded-3xl p-10 text-center relative overflow-hidden">
        <p className="text-red-400 text-[10px] tracking-[0.5em] uppercase mb-3">
          Identity Lock — Mismatch Detected
        </p>
        <h3 className="text-2xl font-extralight text-white mb-4">
          Application Rejected.
        </h3>
        <p className="text-white/40 text-sm leading-relaxed max-w-sm mx-auto mb-6">
          {serverMessage}
        </p>
        <p className="text-white/20 text-xs">
          The name on your government ID must exactly match the billing name you
          provided. If you believe this is an error, contact{" "}
          <a href="mailto:hello@aura-intelligence.ch" className="underline">
            hello@aura-intelligence.ch
          </a>
        </p>
      </div>
    );
  }

  // ── Main form ────────────────────────────────────────────────────────────
  return (
    <form
      onSubmit={handleSubmit}
      noValidate
      className="glass noise rounded-3xl p-8 md:p-10 relative overflow-hidden"
      style={{
        boxShadow:
          "0 0 0 1px rgba(172,123,120,0.18), 0 40px 100px rgba(30,12,20,0.7)",
      }}
    >
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#AC7B78] to-transparent" />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-5">
        {/* Full Name */}
        <div>
          <FieldLabel>Full Legal Name *</FieldLabel>
          <TextInput
            name="full_name"
            placeholder="As it appears on your ID"
            value={fullName}
            onChange={setFullName}
            required
          />
        </div>

        {/* Email */}
        <div>
          <FieldLabel>Email Address *</FieldLabel>
          <TextInput
            name="email"
            type="email"
            placeholder="Where we send your payment link"
            value={email}
            onChange={setEmail}
            required
          />
        </div>

        {/* Billing Name — Identity Lock field */}
        <div>
          <FieldLabel>Billing Name on Card *</FieldLabel>
          <TextInput
            name="billing_name"
            placeholder="Must match your government ID exactly"
            value={billingName}
            onChange={setBillingName}
            required
          />
          <p className="mt-1.5 text-[10px] text-white/20 leading-relaxed">
            Identity Lock: The name on your ID will be OCR-extracted and matched
            against this field. Mismatch = auto-rejection.
          </p>
        </div>

        {/* Country */}
        <div>
          <FieldLabel>Country / Region *</FieldLabel>
          <TextInput
            name="country"
            placeholder="e.g. Germany, Brazil, Nigeria"
            value={country}
            onChange={setCountry}
            required
          />
        </div>
      </div>

      {/* Reason */}
      <div className="mb-6">
        <FieldLabel>Why are you applying? *</FieldLabel>
        <textarea
          name="reason"
          placeholder="Tell us about your work, what you create, and why the Grant matters to you. (min. 50 characters)"
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          required
          minLength={50}
          rows={4}
          className="w-full bg-white/[0.04] border border-white/[0.08] rounded-xl px-4 py-3 text-white text-sm placeholder-white/20 outline-none focus:border-[#AC7B78]/50 focus:bg-white/[0.06] transition-all resize-none"
        />
      </div>

      {/* Uploads */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-8">
        <div>
          <FieldLabel>Government-Issued ID *</FieldLabel>
          <FileUploadBox
            label="Upload ID Document"
            hint={`Passport, national ID, or driver's licence · ${ALLOWED_LABEL}`}
            accept={ALLOWED_TYPES.join(",")}
            file={idFile}
            onChange={setIdFile}
            error={idError}
          />
        </div>
        <div>
          <FieldLabel>Proof of Student / Low-Income Status *</FieldLabel>
          <FileUploadBox
            label="Upload Proof Document"
            hint={`Student enrolment letter, income statement · ${ALLOWED_LABEL}`}
            accept={ALLOWED_TYPES.join(",")}
            file={incomeFile}
            onChange={setIncomeFile}
            error={incomeError}
          />
        </div>
      </div>

      {/* Legal notice */}
      <p className="text-white/15 text-[10px] leading-relaxed mb-6">
        Your documents are processed exclusively on the Aura Monolith node
        (Hetzner, EU) via OCR for identity verification only. Files are deleted
        within 48 hours of a decision. We do not share or sell your data. By
        submitting you agree to the{" "}
        <a href="/privacy" className="underline">
          Privacy Policy
        </a>
        .
      </p>

      {/* Submit */}
      {formState === "error" && serverMessage && (
        <p className="mb-4 text-red-400 text-sm text-center">{serverMessage}</p>
      )}

      <button
        type="submit"
        disabled={formState === "submitting"}
        className="w-full py-4 rounded-full text-sm tracking-widest uppercase font-light text-[#472830] transition-all duration-300 hover:shadow-[0_0_30px_rgba(172,123,120,0.4)] disabled:opacity-50 disabled:cursor-wait"
        style={{
          background: "linear-gradient(135deg, #AC7B78, #C4948F, #AC7B78)",
        }}
      >
        {formState === "submitting"
          ? "Verifying Identity…"
          : "Submit Application"}
      </button>
    </form>
  );
}
