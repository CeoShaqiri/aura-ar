import { NextRequest, NextResponse } from "next/server";
import Stripe from "stripe";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: "2025-04-30.basil",
});

const APP_URL = process.env.NEXT_PUBLIC_APP_URL ?? "http://localhost:3000";

// ── Product catalogue ────────────────────────────────────────────────────────
// These map the `tier` query param → Stripe price config.
// Once you have real Stripe Price IDs, replace the unit_amount entries with
// price_data using existing price IDs instead.
const PLANS: Record<
  string,
  {
    name: string;
    description: string;
    amount: number; // in cents
    currency: string;
    mode: Stripe.Checkout.SessionCreateParams["mode"];
    interval?: Stripe.Checkout.SessionCreateParams.LineItem.PriceData.Recurring["interval"];
    payment_methods: Stripe.Checkout.SessionCreateParams["payment_method_types"];
  }
> = {
  // ── Monthly subscriptions ──────────────────────────────────────────────
  "pro-monthly": {
    name: "Aura Pro — Monthly",
    description:
      "Dedicated Monolith Node · Unlimited AR deployments · No app required",
    amount: 49900,
    currency: "usd",
    mode: "subscription",
    interval: "month",
    payment_methods: ["card", "link"],
  },
  "agency-monthly": {
    name: "Aura Agency — Monthly",
    description: "5 Addon seats · Custom domain overlay · 5 TB model vault",
    amount: 199900,
    currency: "usd",
    mode: "subscription",
    interval: "month",
    payment_methods: ["card", "link"],
  },
  "sovereign-monthly": {
    name: "Aura Sovereign — Monthly",
    description:
      "Unlimited seats · White-label portals · 2h SLA named engineer",
    amount: 499900,
    currency: "usd",
    mode: "subscription",
    interval: "month",
    payment_methods: ["card", "link"],
  },

  // ── One-time payments ──────────────────────────────────────────────────
  "sovereign-annual": {
    name: "Aura Sovereign — Annual Pre-Pay",
    description:
      "Full year · save ~$40k vs monthly · immediate Monolith provisioning",
    amount: 1999000,
    currency: "usd",
    mode: "payment",
    payment_methods: [
      "card",
      "link",
      "klarna",
      "affirm",
      "afterpay_clearpay",
      "us_bank_account",
    ],
  },
  "sovereign-installment-1": {
    name: "Aura Sovereign — Instalment 1 of 3",
    description: "First payment of the 3-part plan · $6,999 × 3",
    amount: 699900,
    currency: "usd",
    mode: "payment",
    payment_methods: ["card", "link", "klarna", "affirm", "afterpay_clearpay"],
  },
};

export async function POST(req: NextRequest) {
  try {
    const { tier } = await req.json();

    const plan = PLANS[tier];
    if (!plan) {
      return NextResponse.json({ error: "Unknown tier" }, { status: 400 });
    }

    // Build price_data inline — no need to pre-create prices in Stripe dashboard
    const price_data: Stripe.Checkout.SessionCreateParams.LineItem.PriceData = {
      currency: plan.currency,
      unit_amount: plan.amount,
      product_data: {
        name: plan.name,
        description: plan.description,
        images: [`${APP_URL}/images/aura-og.png`],
      },
      ...(plan.mode === "subscription" && plan.interval
        ? { recurring: { interval: plan.interval } }
        : {}),
    };

    // Payment method configuration:
    //   Apple Pay and Google Pay are automatically enabled by Stripe when
    //   "card" is in payment_method_types AND the domain is registered in
    //   Stripe Dashboard → Settings → Payment methods → Wallets.
    //   No extra code is needed — Stripe's Payment Request Button handles both.

    const session = await stripe.checkout.sessions.create({
      mode: plan.mode,
      line_items: [{ price_data, quantity: 1 }],
      payment_method_types:
        plan.payment_methods as Stripe.Checkout.SessionCreateParams["payment_method_types"],
      // Allow promotion codes so you can do founder discounts
      allow_promotion_codes: true,
      // Billing address collection — needed for Klarna + Afterpay
      billing_address_collection: "required",
      success_url: `${APP_URL}/checkout/success?session_id={CHECKOUT_SESSION_ID}&tier=${tier}`,
      cancel_url: `${APP_URL}/checkout/cancel?tier=${tier}`,
      // Custom metadata — shows up in Stripe dashboard and webhooks
      metadata: {
        tier,
        product: "aura_ar",
        source: "landing_page",
      },
    });

    return NextResponse.json({ url: session.url });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Internal error";
    console.error("[Aura checkout]", message);
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
