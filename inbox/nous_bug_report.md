# [Bug] Android App: Corr3xt Email/Google Sign-In Returns 404 — `/oauth/start` Endpoint Not Found

**App:** com.nousresearch.hermesagent v0.13.112  
**Device:** Samsung Galaxy Note 20 Ultra (SM-N986U), Android 13  
**Plan:** Plus — $21.74 of $22 credits remaining, renews 2026-06-21  
**Date:** 2026-05-28

---

## Summary

The Hermes Agent Android app generates a valid-looking OAuth URL pointing to `portal.nousresearch.com/oauth/start` for both email and Google sign-in flows. That endpoint returns **HTTP 404**. Sign-in is completely broken — there is no workaround inside the app.

---

## Steps to Reproduce

1. Install Hermes Agent v0.13.112 on Android 13
2. Launch app → Sign In screen
3. Enter Corr3xt URL: `https://portal.nousresearch.com`
4. Tap **Refresh** → email and Google sign-in buttons activate
5. Tap either sign-in method
6. App opens browser/WebView with the following URL:

```
https://portal.nousresearch.com/oauth/start
  ?method=email
  &provider=email
  &client=hermes-android
  &callback_contract=v1
  &redirect_uri=hermesagent%3A%2F%2Fauth%2Fcallback
  &state=4cfb10ad-eda9-4d62-b22a-40c7c38ea53e
  &lang=en
  &locale=en
  &ui_locales=en
```

**Result:** Browser returns `404 Not Found`  
**Expected:** OAuth sign-in page loads, user authenticates, app receives token via `hermesagent://auth/callback`

---

## Endpoint Probe Results

```
GET https://portal.nousresearch.com/oauth/start   → 404 Not Found
GET https://portal.nousresearch.com/oauth/auth    → 429 Too Many Requests (endpoint exists, rate-limited)
GET https://auth.nousresearch.com/                → 403 Forbidden
```

The `/oauth/auth` endpoint exists and responds (even if rate-limited). The `/oauth/start` endpoint — the one the Android client calls — does not exist for `client=hermes-android`.

---

## Impact

- **Blocker:** Cannot log in to the Android app at all
- **Subscription waste:** Paying $20/month with $21.74 in credits that can only be used via Nous Chat (browser) — which is **shutting down July 1, 2026**
- **Timeline:** After July 1, there will be no working way to use the subscription if the Android app sign-in remains broken

---

## What I've Tried

- Left the Corr3xt URL field blank (week-long blocker — unclear field label)
- Tried `https://corr3xt.nousresearch.com` — no such host
- Tried `https://auth.nousresearch.com` — 403, buttons don't activate
- Cleared app data, reinstalled — same result
- Confirmed portal.nousresearch.com is the correct Corr3xt URL (sign-in buttons activate after Refresh)
- Both email and Google flows hit the same `/oauth/start` → 404

---

## Requests

1. **Deploy `/oauth/start`** on `portal.nousresearch.com` for `client=hermes-android`, or
2. **Update the app** to use the correct endpoint path (if `/oauth/auth` is the right one), or
3. **Provide a temporary workaround** — e.g., generate an API token via portal that can be pasted into the app to bypass OAuth, or
4. **Clarify the timeline** for when Android sign-in will be fixed given the Nous Chat shutdown on July 1

---

## Device Info

| Field | Value |
|-------|-------|
| Device | Samsung Galaxy Note 20 Ultra (SM-N986U) |
| Android | 13 |
| App version | 0.13.112 (Alpha) |
| Architecture | arm64-v8a |
| Corr3xt URL used | https://portal.nousresearch.com |
| Account | gsunnylive35@gmail.com |
| Plan | Plus — active, renews 2026-06-21 |
