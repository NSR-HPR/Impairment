# NSR Sprinkler Impairment Notification Portal
**National Safety & Risk — NFPA 25 Compliant**

This repository contains the complete sprinkler system impairment notification web portal for National Safety & Risk. It is built to be deployed on Netlify with automated email notifications via Outlook.

---

## 📁 File Structure

```
nsr-impairment/
├── index.html       ← Main impairment notification form (NFPA 25 compliant)
├── success.html     ← Confirmation page shown after submission
├── NSR.png          ← NSR logo
├── netlify.toml     ← Netlify configuration
└── README.md        ← This file
```

---

## 🚀 STEP 1 — Upload to GitHub

1. Go to **https://github.com** and sign in (or create a free account)
2. Click the **"+"** button → **"New repository"**
3. Name it: `nsr-impairment-portal`
4. Set it to **Private**
5. Click **"Create repository"**
6. On the next screen, click **"uploading an existing file"**
7. Drag and drop ALL files from this folder into the upload area
8. Click **"Commit changes"**

---

## 🌐 STEP 2 — Deploy on Netlify

1. Go to **https://app.netlify.com** and sign up with your email
2. Click **"Add new site"** → **"Import an existing project"**
3. Choose **"GitHub"** and authorize Netlify to access your account
4. Select the **`nsr-impairment-portal`** repository
5. Leave all build settings as-is (the `netlify.toml` handles this)
6. Click **"Deploy site"**
7. Netlify will give you a URL like `https://nsr-impairment.netlify.app`
   - You can customize this under **Site Settings → Domain Management**

### Enable Netlify Forms
Netlify automatically detects the form. To confirm:
1. Go to your site in Netlify → **Forms** tab
2. You should see **"sprinkler-impairment"** listed after the first test submission

### Set Up Redirect After Submission
1. In Netlify, go to **Site Settings → Forms**
2. Under the form, set the **Success URL** to `/success.html`

---

## 📧 STEP 3 — Connect to Outlook via Zapier

Zapier acts as the bridge between Netlify (which captures form submissions) and Outlook (which sends the emails).

### A. Create a Free Zapier Account
Go to **https://zapier.com** and sign up.

### B. Create Zap #1 — Customer Confirmation Email

1. Click **"Create Zap"**
2. **Trigger:** Search for and select **Netlify**
   - Event: **"New Form Submission"**
   - Connect your Netlify account
   - Select your site and the form named **"sprinkler-impairment"**
   - Test the trigger (you may need to submit a test form first)
3. **Action:** Search for and select **Microsoft Outlook**
   - Event: **"Send Email"**
   - Connect your Outlook account (pnephin@natsr.com)
   - Configure the email:
     - **To:** `{{email}}` *(pulls from form's contact email field)*
     - **From:** `pnephin@natsr.com`
     - **Subject:** `[NSR] Impairment Notification Received — {{property_address}}`
     - **Body (HTML):**
       ```
       Dear {{customer_name}},

       Thank you for submitting your sprinkler system impairment notification 
       to National Safety & Risk.

       SUBMISSION DETAILS:
       ─────────────────────────────────────
       Property Address:     {{property_address}}
       Impairment Type:      {{impairment_type}}
       System/Zone Affected: {{system_affected}}
       Start Date/Time:      {{impairment_start}}
       Est. Restoration:     {{estimated_restoration}}
       ─────────────────────────────────────

       Our team has received your notification and will review it in 
       accordance with NFPA 25 requirements. You will receive a follow-up 
       email once your submission has been processed.

       For urgent matters, please contact us directly:
       Email: pnephin@natsr.com

       National Safety & Risk
       NFPA 25 Impairment Management Program
       ```
4. Click **"Publish Zap"**

### C. Create Zap #2 — Internal NSR Notification Email

1. Click **"Create Zap"**
2. **Trigger:** Same as above — Netlify → New Form Submission → sprinkler-impairment
3. **Action:** Microsoft Outlook → Send Email
   - **To:** `pnephin@natsr.com`
   - **Subject:** `🚨 NEW IMPAIRMENT: {{impairment_type}} — {{property_address}}`
   - **Body:**
     ```
     NEW SPRINKLER IMPAIRMENT NOTIFICATION RECEIVED
     ═══════════════════════════════════════════════

     CUSTOMER INFORMATION:
     Customer/Company:    {{customer_name}}
     Property Name:       {{property_name}}
     Property Address:    {{property_address}}
     Contact Name:        {{contact_name}}
     Contact Email:       {{email}}
     Contact Phone:       {{contact_phone}}

     IMPAIRMENT DETAILS:
     Type:                {{impairment_type}}
     Reason:              {{reason_for_impairment}}
     System Affected:     {{system_affected}}
     Area Affected:       {{area_affected}}
     Heads Affected:      {{heads_affected}}
     Start Date/Time:     {{impairment_start}}
     Est. Restoration:    {{estimated_restoration}}
     Description:         {{impairment_description}}

     IMPAIRMENT COORDINATOR:
     Coordinator Name:    {{coordinator_name}}
     Coordinator Phone:   {{coordinator_phone}}
     Contractor:          {{contractor_company}}
     Contractor Contact:  {{contractor_contact}}
     Contractor Phone:    {{contractor_phone}}

     NOTIFICATIONS CONFIRMED:
     Fire Department:     {{notified_fire_dept}}
     Insurance Carrier:   {{notified_insurance}}
     Alarm Company:       {{notified_alarm}}
     Building Occupants:  {{notified_occupants}}
     Fire Watch:          {{fire_watch_established}}
     Hot Work Suspended:  {{hot_work_suspended}}
     Temp Protection:     {{temp_protection_provided}}

     ADDITIONAL NOTES:
     {{additional_precautions}}
     ```
4. Click **"Publish Zap"**

---

## ✅ Testing the Full Flow

1. Open your Netlify site URL
2. Fill out the form with a test submission (use your own email as the contact)
3. Submit the form
4. Verify:
   - You are redirected to `success.html`
   - The customer confirmation email arrives in your inbox
   - The internal NSR notification email arrives at pnephin@natsr.com
5. Check **Netlify → Forms** to confirm the submission was captured

---

## 🔧 Making Updates

To update the form in the future:
1. Edit the files locally
2. Go to your GitHub repository
3. Click on the file → click the pencil (edit) icon
4. Make your changes and commit
5. Netlify will **automatically redeploy** within 30–60 seconds

---

## 📋 NFPA 25 Compliance Notes

This form captures all data required under **NFPA 25 (2023 Edition)**:
- **§ 15.2** — Impairment classification (planned vs. emergency)
- **§ 15.3** — System/zone identification and scope
- **§ 15.3.2** — Number of sprinkler heads out of service
- **§ 15.4** — Impairment Coordinator designation
- **§ 15.5** — Required notifications (fire dept, insurance, alarm company)
- **§ 15.5.2** — Fire watch establishment
- **§ 15.6** — Restoration notification (handled via follow-up)

---

## 📞 Support

For questions about this portal, contact:
**Patric Nephin** — pnephin@natsr.com
