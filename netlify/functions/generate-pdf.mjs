/**
 * NSR Impairment PDF Generator — Netlify Serverless Function
 * Path: /netlify/functions/generate-pdf.mjs
 *
 * Called by Zapier (Webhooks by Zapier) with form data as JSON body.
 * Returns a base64-encoded PDF that Zapier can attach to an email.
 */

import { execSync } from "child_process";
import { writeFileSync, readFileSync, unlinkSync } from "fs";
import { tmpdir } from "os";
import { join } from "path";

// ── Field mapping: Zapier "Data X" keys → PDF script keys ────────────────────
function mapFields(body) {
  const bool = (v) => (v === "Yes" || v === true || v === "true");

  // Format ISO datetime → "June 3, 2026 at 1:31 PM"
  const fmtDate = (v) => {
    if (!v) return "—";
    try {
      const d = new Date(v.replace("T", " "));
      return d.toLocaleString("en-US", {
        month: "long", day: "numeric", year: "numeric",
        hour: "numeric", minute: "2-digit", hour12: true,
      });
    } catch { return v; }
  };

  return {
    // Section 1
    customer_name:        body["Data Customer Name"]        || "—",
    property_name:        body["Data Property Name"]        || "—",
    property_address:     body["Data Property Address"]     || "—",
    contact_name:         body["Data Contact Name"]         || "—",
    contact_title:        body["Data Contact Title"]        || "—",
    contact_email:        body["Data Email"]                || "—",
    contact_phone:        body["Data Contact Phone"]        || "—",
    alt_contact_name:     body["Data Alt Contact Name"]     || "—",
    alt_contact_phone:    body["Data Alt Contact Phone"]    || "—",
    // Section 2
    impairment_type:      body["Data Impairment Type"]      || "—",
    system_affected:      body["Data System Affected"]      || "—",
    area_affected:        body["Data Area Affected"]        || "—",
    heads_affected:       body["Data Heads Affected"]       || "—",
    reason_for_impairment:body["Data Reason For Impairment"]|| "—",
    impairment_start:     fmtDate(body["Data Impairment Start"]),
    estimated_restoration:fmtDate(body["Data Estimated Restoration"]),
    impairment_description:body["Data Impairment Description"] || "",
    // Section 3
    coordinator_name:     body["Data Coordinator Name"]     || "—",
    coordinator_phone:    body["Data Coordinator Phone"]    || "—",
    contractor_company:   body["Data Contractor Company"]   || "—",
    contractor_license:   body["Data Contractor License"]   || "—",
    contractor_contact:   body["Data Contractor Contact"]   || "—",
    contractor_phone:     body["Data Contractor Phone"]     || "—",
    // Section 4 checkboxes
    fire_dept_notified:       bool(body["Data Notified Fire Dept"]),
    insurance_notified:       bool(body["Data Notified Insurance"]),
    alarm_company_notified:   bool(body["Data Notified Alarm"]),
    occupants_notified:       bool(body["Data Notified Occupants"]),
    fire_watch_established:   bool(body["Data Fire Watch Established"]),
    hot_work_suspended:       bool(body["Data Hot Work Suspended"]),
    temp_protection_provided: bool(body["Data Temp Protection Provided"]),
    // Meta
    submitted_at: fmtDate(body["Timestamp"] || new Date().toISOString()),
  };
}

export default async (req) => {
  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "POST only" }), { status: 405 });
  }

  let body;
  try {
    body = await req.json();
  } catch {
    return new Response(JSON.stringify({ error: "Invalid JSON body" }), { status: 400 });
  }

  const data = mapFields(body);

  // Write data to a temp JSON file for the Python script to read
  const tmpJson = join(tmpdir(), `nsr-${Date.now()}.json`);
  const tmpPdf  = join(tmpdir(), `nsr-${Date.now()}.pdf`);

  try {
    writeFileSync(tmpJson, JSON.stringify(data));
    execSync(`python3 /var/task/generate_nsr_pdf.py ${tmpJson} ${tmpPdf}`, {
      timeout: 30000,
    });
    const pdfBytes = readFileSync(tmpPdf);
    const base64   = pdfBytes.toString("base64");

    return new Response(
      JSON.stringify({
        success: true,
        pdf_base64: base64,
        filename: `NSR-Impairment-${data.customer_name.replace(/\s+/g, "-")}-${Date.now()}.pdf`,
        customer_name: data.customer_name,
        contact_email: data.contact_email,
      }),
      {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }
    );
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), { status: 500 });
  } finally {
    try { unlinkSync(tmpJson); } catch {}
    try { unlinkSync(tmpPdf);  } catch {}
  }
};

export const config = { path: "/api/generate-pdf" };
