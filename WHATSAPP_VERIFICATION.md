# WhatsApp Business Verification — Submission Package

**Prepared for:** LankaAgent / Ceyloria Holidays
**Status:** Ready to submit
**Estimated approval time:** 2–4 weeks (Twilio/Meta review)

---

## 1. Required Business Information

| Field | Value |
|---|---|
| **Legal Business Name** | Ceyloria Holidays (Pvt) Ltd |
| **Business Type** | Private Limited Company |
| **Industry** | Travel & Tourism |
| **Website** | https://ceyloria-site.vercel.app |
| **Business Address** | [Your registered address in Sri Lanka] |
| **Phone Number** | +94 77 123 4567 (or your business WhatsApp number) |
| **Email** | hello@ceyloriaholidays.com |
| **Tax ID / VAT Number** | [Your Sri Lanka VAT/TIN] |
| **Business Registration Number** | [Your Sri Lanka company registration number] |

---

## 2. Required Documents (Prepare PDFs)

| Document | Status | Notes |
|---|---|---|
| **Certificate of Incorporation** | ☐ Ready | Sri Lanka Registrar of Companies |
| **Business Registration Certificate** | ☐ Ready | Department of Registrar of Companies |
| **Tax Registration Certificate (VAT)** | ☐ Ready | Inland Revenue Department |
| **Utility Bill (Business Address)** | ☐ Ready | Electricity/Water bill < 3 months old |
| **Bank Statement** | ☐ Ready | Business account, last 3 months |
| **Director's ID/Passport** | ☐ Ready | For each director |
| **Letter of Authorization** | ☐ Ready | On company letterhead, signed by director |

---

## 3. WhatsApp Business Profile

| Field | Value |
|---|---|
| **Display Name** | Ceyloria Holidays |
| **Category** | Travel & Transportation |
| **Description** | Premium Sri Lanka tour operator — 14-day Glimpses of Ceylon tour, Ayurveda wellness, private chauffeur-guided journeys. 24/7 AI concierge support. |
| **Website** | https://ceyloria-site.vercel.app |
| **Email** | hello@ceyloriaholidays.com |
| **Address** | [Your business address] |
| **Business Hours** | Mon–Sun 8:00 AM – 10:00 PM (IST) |

---

## 4. Message Templates (Pre-approval)

### Template 1: Welcome / Opt-in
```
Name: welcome_optin
Language: en
Category: UTILITY
Header: None
Body: Welcome to Ceyloria Holidays! 🇱🇰 I'm Anuki, your AI concierge. How can I help you plan your Sri Lanka journey today?
Footer: Reply STOP to unsubscribe
Buttons: None
```

### Template 2: Quote Delivered
```
Name: quote_delivered
Language: en
Category: UTILITY
Header: None
Body: Your personalized quote is ready! {{1}} days, {{2}} travelers = ${{3}} per person (HB, double occupancy). Valid for 30 days. Want me to send the day-by-day itinerary?
Footer: Ceyloria Holidays — Premium Sri Lanka Tours
Buttons: 
  - "Yes, send itinerary" (QUICK_REPLY)
  - "Modify dates" (QUICK_REPLY)
  - "Speak to human" (QUICK_REPLY)
```

### Template 3: Booking Confirmation
```
Name: booking_confirmed
Language: en
Category: UTILITY
Header: None
Body: 🎉 Your Sri Lanka journey is confirmed! Booking reference: {{1}}. Dates: {{2}}. Total: ${{3}}. Our team will email the detailed itinerary within 2 hours. Safe travels! 🇱🇰
Footer: Ceyloria Holidays | +94 77 123 4567
Buttons: None
```

### Template 4: Pre-trip Reminder
```
Name: pretrip_reminder
Language: en
Category: UTILITY
Header: None
Body: Your Sri Lanka adventure starts in {{1}} days! 🌴 Weather looks great. Reminder: Passport valid 6+ months, Sri Lanka ETA approved, travel insurance active. Need anything? Just reply.
Footer: Ceyloria Holidays — We're here 24/7
Buttons:
  - "Check weather" (QUICK_REPLY)
  - "Contact concierge" (QUICK_REPLY)
```

### Template 5: Post-trip Feedback
```
Name: posttrip_feedback
Language: en
Category: MARKETING
Header: None
Body: Welcome back! 🏠 Hope Sri Lanka left you with memories for a lifetime. Your feedback helps us craft even better journeys. Take 2 minutes? {{1}}
Footer: Ceyloria Holidays — Your story matters
Buttons:
  - "Leave review" (URL: https://ceyloria-site.vercel.app/review)
  - "Share photos" (QUICK_REPLY)
```

---

## 5. Twilio Console Setup Checklist

| Step | Action | Done |
|---|---|---|
| 1 | Buy WhatsApp-enabled number in Twilio Console | ☐ |
| 2 | Configure Messaging Service | ☐ |
| 3 | Add WhatsApp sender (Business Profile) | ☐ |
| 3a | Upload all documents (Section 2) | ☐ |
| 3b | Fill Business Profile (Section 3) | ☐ |
| 3c | Submit message templates (Section 4) | ☐ |
| 4 | Wait for Meta approval (2–4 weeks) | ☐ |
| 5 | Test inbound/outbound messages | ☐ |
| 6 | Configure webhook: `https://synthetic-flavor-boutique-zero.trycloudflare.com/webhook/whatsapp` | ☐ |
| 7 | Test end-to-end: send "hello" → receive Anuki reply | ☐ |

---

## 6. Webhook Configuration

| Setting | Value |
|---|---|
| **Webhook URL** | `https://synthetic-flavor-boutique-zero.trycloudflare.com/webhook/whatsapp` |
| **HTTP Method** | POST |
| **Content-Type** | application/json |
| **Verify Token** | [Generate random string, save in Twilio + LankaAgent env] |
| **Events** | messages, message_status, message_template_status_update |

---

## 7. Environment Variables to Set (LankaAgent)

```bash
# In .env or deployment secrets
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+94771234567
TWILIO_VERIFY_TOKEN=generate_random_string_here
TWILIO_MESSAGING_SERVICE_SID=MGxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 8. Compliance Notes (Sri Lanka)

- **Data Protection:** Comply with Sri Lanka Personal Data Protection Act (2022)
- **Opt-in:** Explicit consent required before first marketing message
- **Opt-out:** "STOP" keyword must work immediately
- **Business Hours:** Respect 8 AM – 10 PM IST for promotional messages
- **Language:** Support English, Sinhala, Tamil templates

---

## 9. Submission Timeline

| Week | Milestone |
|---|---|
| **Week 1** | Submit all documents + templates to Twilio |
| **Week 2–3** | Meta review (may request clarifications) |
| **Week 3–4** | Approval → Go live |
| **Week 4+** | Monitor, optimize, add more templates |

---

## 10. Quick Commands (Post-Approval)

```bash
# Test webhook locally
curl -X POST https://synthetic-flavor-boutique-zero.trycloudflare.com/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{"From":"whatsapp:+94771234567","Body":"hello"}'

# Send test template via Twilio CLI
twilio api:core:messages:create \
  --from "whatsapp:+94771234567" \
  --to "whatsapp:+9477XXXXXXX" \
  --content-sid "HXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
  --content-variables '{"1":"7","2":"2","3":"1261"}'
```

---

## 📞 Support Contacts

| Issue | Contact |
|---|---|
| **Twilio Support** | Console → Help → Contact Support |
| **Meta Business Support** | business.facebook.com/help |
| **Twilio WhatsApp Docs** | https://twilio.com/docs/whatsapp |
| **LankaAgent Internal** | [Your dev team contact] |

---

**Next Step:** Gather documents (Section 2), then start Twilio Console submission. Estimated 1–2 hours to prepare + submit.