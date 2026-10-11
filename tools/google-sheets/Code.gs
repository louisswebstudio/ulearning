/**
 * UTALK Center: receives the website contact form and adds one row per request.
 *
 * Setup (once): open the Google Sheet > Extensions > Apps Script, paste this file,
 * change TOKEN, then Deploy > New deployment > Web app
 * (Execute as: Me, Who has access: Anyone). Paste the web app URL and the same TOKEN
 * in WordPress > Settings > UTALK Google Sheets. Steps: docs/GOOGLE_SHEETS.md
 */

// Same secret as in WordPress. Stops strangers who find the URL from adding rows.
const TOKEN = 'CHANGE-ME-TO-A-LONG-RANDOM-SECRET';
const SHEET_NAME = 'Demandes';
const HEADERS = ['Date', 'Nom', 'Téléphone', 'Email', 'Langue', 'Page'];

function doPost(e) {
  const p = (e && e.parameter) || {};
  if (p.token !== TOKEN) return reply({ ok: false, error: 'token' });

  const lock = LockService.getScriptLock(); // two forms at the same second: no lost row
  lock.waitLock(10000);
  try {
    const book = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = book.getSheetByName(SHEET_NAME) || book.insertSheet(SHEET_NAME);
    if (sheet.getLastRow() === 0) {
      sheet.appendRow(HEADERS);
      sheet.getRange(1, 1, 1, HEADERS.length).setFontWeight('bold');
      sheet.setFrozenRows(1);
    }
    sheet.appendRow([new Date(), clean(p.nom), clean(p.telephone), clean(p.email), clean(p.langue), clean(p.page)]);
  } finally {
    lock.releaseLock();
  }
  return reply({ ok: true });
}

// A form value starting with = + - @ would run as a formula in the sheet: store it as text.
function clean(value) {
  const v = String(value || '').slice(0, 500);
  return /^[=+\-@]/.test(v) ? "'" + v : v;
}

function reply(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
