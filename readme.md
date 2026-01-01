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
- Uses a vision model to analyze it like prompt/audit.py is saying
- Save it in audit.md
- DECIDE SHOULD CONTINUE SCROLL OR INTRACT
    - if there is something which is was webpage (cookie banners, modals, age gates)
    - if yes Attempts to close blockers **only when suggested by audit**
- Then loop from second steps until page reach end

### ❌ What it does NOT do
- No full functional QA
- No checkout completion
- No payment testing
- No synthetic DOM assertions
- No blind CTA spamming

---

## 🧱 System Architecture

