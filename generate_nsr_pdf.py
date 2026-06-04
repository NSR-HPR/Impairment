/**
 * NSR Impairment PDF Generator — Netlify Serverless Function (Pure JS)
 * Path: netlify/functions/generate-pdf.mjs
 * Uses: pdfkit (pure Node.js, no Python needed)
 */

import PDFDocument from "pdfkit";

// ── Colors ───────────────────────────────────────────────────────────────────
const RED    = "#C0392B";
const DARK   = "#1A1A2E";
const MID    = "#2C3E50";
const LIGHT  = "#ECF0F1";
const ACCENT = "#E8F4F8";
const BORDER = "#BDC3C7";
const LABEL  = "#7F8C8D";
const GREEN  = "#27AE60";
const WHITE  = "#FFFFFF";

// ── Format ISO date ───────────────────────────────────────────────────────────
function fmtDate(v) {
  if (!v) return "—";
  try {
    const d = new Date(v.replace("T", " "));
    if (isNaN(d)) return v;
    return d.toLocaleString("en-US", {
      month: "long", day: "numeric", year: "numeric",
      hour: "numeric", minute: "2-digit", hour12: true,
    });
  } catch { return v; }
}

// ── Map incoming Zapier fields ────────────────────────────────────────────────
function mapFields(body) {
  const bool = (v) => v === "Yes" || v === true || v === "true";
  return {
    customer_name:         body["Data Customer Name"]         || "—",
    property_name:         body["Data Property Name"]         || "—",
    property_address:      body["Data Property Address"]      || "—",
    contact_name:          body["Data Contact Name"]          || "—",
    contact_title:         body["Data Contact Title"]         || "—",
    contact_email:         body["Data Email"]                 || "—",
    contact_phone:         body["Data Contact Phone"]         || "—",
    alt_contact_name:      body["Data Alt Contact Name"]      || "—",
    alt_contact_phone:     body["Data Alt Contact Phone"]     || "—",
    impairment_type:       body["Data Impairment Type"]       || "—",
    system_affected:       body["Data System Affected"]       || "—",
    area_affected:         body["Data Area Affected"]         || "—",
    heads_affected:        body["Data Heads Affected"]        || "—",
    reason:                body["Data Reason For Impairment"] || "—",
    impairment_start:      fmtDate(body["Data Impairment Start"]),
    est_restoration:       fmtDate(body["Data Estimated Restoration"]),
    description:           body["Data Impairment Description"] || "",
    coordinator_name:      body["Data Coordinator Name"]      || "—",
    coordinator_phone:     body["Data Coordinator Phone"]     || "—",
    contractor_company:    body["Data Contractor Company"]    || "—",
    contractor_license:    body["Data Contractor License"]    || "—",
    contractor_contact:    body["Data Contractor Contact"]    || "—",
    contractor_phone:      body["Data Contractor Phone"]      || "—",
    fire_dept:             bool(body["Data Notified Fire Dept"]),
    insurance:             bool(body["Data Notified Insurance"]),
    alarm:                 bool(body["Data Notified Alarm"]),
    occupants:             bool(body["Data Notified Occupants"]),
    fire_watch:            bool(body["Data Fire Watch Established"]),
    hot_work:              bool(body["Data Hot Work Suspended"]),
    temp_protection:       bool(body["Data Temp Protection Provided"]),
    submitted_at:          fmtDate(body["Timestamp"] || new Date().toISOString()),
  };
}

// ── Build PDF → Buffer ────────────────────────────────────────────────────────
function buildPDF(d) {
  return new Promise((resolve, reject) => {
    const doc = new PDFDocument({ size: "LETTER", margin: 45, bufferPages: true });
    const chunks = [];
    doc.on("data", c => chunks.push(c));
    doc.on("end",  () => resolve(Buffer.concat(chunks)));
    doc.on("error", reject);

    const W = doc.page.width - 90; // usable width
    let y = 45;

    // ── helpers ───────────────────────────────────────────────────────────────
    const rect  = (x, iy, w, h, color) => doc.rect(x, iy, w, h).fill(color);
    const hline = (iy, color = BORDER) =>
      doc.moveTo(45, iy).lineTo(45 + W, iy).lineWidth(0.5).stroke(color);

    function sectionHeader(num, title, iy) {
      rect(45, iy, W, 22, MID);
      doc.fillColor("#AABBCC").font("Helvetica-Bold").fontSize(7)
         .text(num, 53, iy + 7);
      doc.fillColor(WHITE).font("Helvetica-Bold").fontSize(9)
         .text(title, 95, iy + 7);
      return iy + 22;
    }

    function fieldRow(rows, iy) {
      // rows = [{label, value}, ...] up to 2 per line
      const rowH = 20;
      rows.forEach((pair, pi) => {
        const x0 = 45;
        const mid = 45 + W / 2;
        const twoCol = pair.length === 2;

        // label bg
        rect(x0, iy, twoCol ? W / 2 : W, rowH, LIGHT);
        if (twoCol) rect(mid, iy, W / 2, rowH, LIGHT);

        // label text
        doc.fillColor(LABEL).font("Helvetica-Bold").fontSize(7)
           .text(pair[0].label, x0 + 6, iy + 4, { width: twoCol ? W/2 - 80 : W - 160 });
        // value text
        doc.fillColor(DARK).font("Helvetica").fontSize(8.5)
           .text(pair[0].value, x0 + twoCol ? W * 0.23 : W * 0.23, iy + 4,
                 { width: twoCol ? W * 0.27 - 10 : W * 0.75 });

        if (twoCol) {
          doc.fillColor(LABEL).font("Helvetica-Bold").fontSize(7)
             .text(pair[1].label, mid + 6, iy + 4, { width: W * 0.22 });
          doc.fillColor(DARK).font("Helvetica").fontSize(8.5)
             .text(pair[1].value, mid + W * 0.23, iy + 4, { width: W * 0.27 - 10 });
        }

        hline(iy + rowH);
        iy += rowH;
      });
      return iy;
    }

    // ── HEADER ────────────────────────────────────────────────────────────────
    rect(45, y, W, 44, RED);
    doc.fillColor(WHITE).font("Helvetica-Bold").fontSize(15)
       .text("NATIONAL SAFETY & RISK", 59, y + 8);
    doc.fillColor("#F0F0F0").font("Helvetica").fontSize(9)
       .text("Sprinkler System Impairment Notification", 59, y + 26);
    doc.fillColor("#F0F0F0").font("Helvetica").fontSize(8)
       .text(`Submitted: ${d.submitted_at}`, 59, y + 36, { width: W - 20, align: "right" });
    y += 44;

    // Banner
    rect(45, y, W, 20, ACCENT);
    doc.fillColor(MID).font("Helvetica-Bold").fontSize(8)
       .text("IMPAIRMENT NOTIFICATION SUMMARY", 57, y + 6);
    hline(y + 20);
    y += 20 + 8;

    // ── SEC 1 ─────────────────────────────────────────────────────────────────
    y = sectionHeader("SEC. 01", "Customer & Property Information", y);
    y += 2;

    // Two-column rows using direct drawing
    const LW = W * 0.22;
    const VW = W * 0.28 - 8;
    const rowH = 20;

    function twoColRow(l1, v1, l2, v2, iy) {
      const x0 = 45, x1 = 45 + W/2;
      rect(x0, iy, LW, rowH, LIGHT);
      rect(x1, iy, LW, rowH, LIGHT);
      doc.fillColor(LABEL).font("Helvetica-Bold").fontSize(7).text(l1, x0+6, iy+6, {width: LW-8, lineBreak:false});
      doc.fillColor(DARK).font("Helvetica").fontSize(8.5).text(v1||"—", x0+LW+4, iy+5, {width: VW, lineBreak:false});
      doc.fillColor(LABEL).font("Helvetica-Bold").fontSize(7).text(l2, x1+6, iy+6, {width: LW-8, lineBreak:false});
      doc.fillColor(DARK).font("Helvetica").fontSize(8.5).text(v2||"—", x1+LW+4, iy+5, {width: VW, lineBreak:false});
      hline(iy + rowH);
      return iy + rowH;
    }

    function oneColRow(label, value, iy) {
      rect(45, iy, LW, rowH, LIGHT);
      doc.fillColor(LABEL).font("Helvetica-Bold").fontSize(7).text(label, 51, iy+6, {width: LW-8, lineBreak:false});
      doc.fillColor(DARK).font("Helvetica").fontSize(8.5).text(value||"—", 45+LW+4, iy+5, {width: W-LW-8, lineBreak:false});
      hline(iy + rowH);
      return iy + rowH;
    }

    y = twoColRow("CUSTOMER / COMPANY", d.customer_name, "PROPERTY / FACILITY", d.property_name, y);
    y = oneColRow("PROPERTY ADDRESS", d.property_address, y);
    y = twoColRow("ON-SITE CONTACT", d.contact_name, "CONTACT TITLE", d.contact_title, y);
    y = twoColRow("CONTACT EMAIL", d.contact_email, "CONTACT PHONE", d.contact_phone, y);
    y = twoColRow("ALTERNATE CONTACT", d.alt_contact_name, "ALTERNATE PHONE", d.alt_contact_phone, y);
    y += 10;

    // ── SEC 2 ─────────────────────────────────────────────────────────────────
    y = sectionHeader("SEC. 02", "Impairment Classification & Details", y);
    y += 2;
    y = twoColRow("IMPAIRMENT TYPE", d.impairment_type, "SYSTEM / ZONE", d.system_affected, y);
    y = twoColRow("AREA / LOCATION", d.area_affected, "HEADS AFFECTED", d.heads_affected, y);
    y = oneColRow("REASON FOR IMPAIRMENT", d.reason, y);
    y = twoColRow("IMPAIRMENT START", d.impairment_start, "EST. RESTORATION", d.est_restoration, y);

    if (d.description) {
      y += 4;
      rect(45, y, LW, rowH, LIGHT);
      doc.fillColor(LABEL).font("Helvetica-Bold").fontSize(7).text("DESCRIPTION", 51, y+6, {width: LW-8, lineBreak:false});
      hline(y + rowH);
      y += rowH;
      rect(45, y, W, 36, WHITE);
      doc.rect(45, y, W, 36).lineWidth(0.5).stroke(BORDER);
      doc.fillColor(MID).font("Helvetica").fontSize(8.5)
         .text(d.description, 51, y+6, { width: W-12, height: 28 });
      y += 36;
    }
    y += 10;

    // ── SEC 3 ─────────────────────────────────────────────────────────────────
    y = sectionHeader("SEC. 03", "Impairment Coordinator & Contractor", y);
    y += 2;
    y = twoColRow("COORDINATOR NAME", d.coordinator_name, "COORDINATOR PHONE", d.coordinator_phone, y);
    y = twoColRow("CONTRACTOR COMPANY", d.contractor_company, "LICENSE NO.", d.contractor_license, y);
    y = twoColRow("CONTRACTOR CONTACT", d.contractor_contact, "CONTRACTOR PHONE", d.contractor_phone, y);
    y += 10;

    // ── SEC 4 ─────────────────────────────────────────────────────────────────
    y = sectionHeader("SEC. 04", "Notifications & Fire Watch Precautions", y);
    y += 2;

    const checkboxes = [
      [d.fire_dept,       "Fire Department Notified"],
      [d.insurance,       "Insurance Carrier Notified"],
      [d.alarm,           "Alarm / Monitoring Company Notified"],
      [d.occupants,       "Building Occupants Notified"],
      [d.fire_watch,      "Fire Watch Established"],
      [d.hot_work,        "Hot Work Suspended in Impaired Area"],
      [d.temp_protection, "Temporary Protection / Extinguishers Provided"],
    ];

    checkboxes.forEach(([checked, label], i) => {
      const bg = i % 2 === 0 ? ACCENT : WHITE;
      rect(45, y, W, 18, bg);
      doc.fillColor(checked ? GREEN : BORDER).font("Helvetica-Bold").fontSize(11)
         .text(checked ? "✓" : "○", 51, y + 3, { width: 16, lineBreak: false });
      doc.fillColor(checked ? DARK : LABEL).font("Helvetica").fontSize(8.5)
         .text(label, 72, y + 4, { width: W - 30, lineBreak: false });
      hline(y + 18);
      y += 18;
    });
    y += 12;

    // ── ACKNOWLEDGMENT ────────────────────────────────────────────────────────
    const ackW = W * 0.48;
    rect(45, y, ackW, 40, ACCENT);
    doc.rect(45, y, ackW, 40).lineWidth(0.5).stroke(BORDER);
    doc.fillColor(MID).font("Helvetica").fontSize(8.5)
       .text("Submitted By (Customer)", 51, y + 8);
    doc.fillColor(LABEL).font("Helvetica").fontSize(7)
       .text("Signature / Date", 51, y + 20);
    y += 52;

    // ── FOOTER ────────────────────────────────────────────────────────────────
    doc.moveTo(45, y).lineTo(45+W, y).lineWidth(0.5).stroke(BORDER);
    y += 6;
    doc.fillColor(LABEL).font("Helvetica-Oblique").fontSize(7)
       .text(
         "This document was automatically generated by the NSR Impairment Notification System upon form submission. " +
         "It serves as an official record of the impairment notification for National Safety & Risk. " +
         "Please retain this document for your records.",
         45, y, { width: W }
       );
    y += 22;
    doc.fillColor(LABEL).font("Helvetica").fontSize(7)
       .text(
         "National Safety & Risk  |  NSR Impairment Management Program  |  pnephin@natsr.com",
         45, y, { width: W, align: "center" }
       );

    doc.end();
  });
}

// ── Netlify handler ───────────────────────────────────────────────────────────
export default async (req, context) => {
  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "POST only" }), { status: 405 });
  }

  let body;
  try { body = await req.json(); }
  catch { return new Response(JSON.stringify({ error: "Invalid JSON" }), { status: 400 }); }

  try {
    const { getStore } = await import("@netlify/blobs");
    const data     = mapFields(body);
    const pdfBuf   = await buildPDF(data);
    const filename = `NSR-Impairment-${data.customer_name.replace(/\s+/g,"-")}-${Date.now()}.pdf`;
    const key      = `pdfs/${filename}`;

    // Store PDF in Netlify Blobs (public)
    const store = getStore({ name: "impairment-pdfs", consistency: "strong" });
    await store.set(key, pdfBuf, {
      metadata: { contentType: "application/pdf" },
    });

    // Build public URL
    const siteUrl = "https://impairment.netlify.app";
    const pdf_url = `${siteUrl}/.netlify/blobs/${encodeURIComponent(key)}?store=impairment-pdfs`;

    return new Response(JSON.stringify({
      success:       true,
      pdf_url,
      filename,
      customer_name: data.customer_name,
      contact_email: data.contact_email,
    }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message, stack: err.stack }), { status: 500 });
  }
};

export const config = { path: "/api/generate-pdf" };
