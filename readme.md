# 🧠 Testral — E-commerce QC Audit Agent (v0)

Testral is a **perception-first, proof-driven QC audit agent** for e-commerce websites.

This is **not full QA testing** and **not automation for checkout funnels**.  
It behaves like a **first-time visitor + QC reviewer**, sampling visible issues that break trust fast.

The system captures **screenshots**, runs **vision-based audits**, optionally removes blockers (cookie popups, modals), and saves a **step-by-step audit trail** in `audit.md`.

---

## 🎯 What This Agent Is (and Is Not)

### ✅ What it does
- Opens a website like a first-time user
- Takes screenshots section-by-section
- Uses a vision model to analyze **what is visible**
- Detects **blocking UI elements** (cookie banners, modals, age gates)
- Attempts to close blockers **only when suggested by audit**
- Scrolls progressively through the page
- Saves a **markdown audit log** with proof

### ❌ What it does NOT do
- No full functional QA
- No checkout completion
- No payment testing
- No synthetic DOM assertions
- No blind CTA spamming

---

## 🧱 System Architecture

