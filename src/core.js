import Papa from 'papaparse';
export const MAX_BYTES = 12 * 1024 * 1024;
export const MAX_ROWS = 100000;
export function parseTransactions(text) {
  if (new TextEncoder().encode(text).length > MAX_BYTES) throw new Error('This file exceeds 12 MB. Split it into smaller batches.');
  const parsed = Papa.parse(text.replace(/^\uFEFF/, ''), { header: true, skipEmptyLines: 'greedy', transformHeader: h => h.trim().toLowerCase() });
  if (parsed.errors.length) throw new Error(`CSV could not be read: ${parsed.errors[0].message}`);
  const headers = parsed.meta.fields ?? [];
  if (parsed.meta.renamedHeaders && Object.keys(parsed.meta.renamedHeaders).length) throw new Error('CSV has duplicate column names. Give each column a unique name.');
  if (!headers.includes('score') || !headers.includes('amount')) throw new Error('Add the required score and amount columns. Optional columns: id, label (0 or 1).');
  if (!parsed.data.length) throw new Error('This file has no transactions. Add at least one row below the header.');
  if (parsed.data.length > MAX_ROWS) throw new Error('This file exceeds 100,000 rows. Split it into smaller batches.');
  const labeled = headers.includes('label'), ids = new Set();
  return parsed.data.map((row, index) => {
    const score = Number(row.score), amount = Number(row.amount);
    if (!row.score?.trim() || !row.amount?.trim() || !Number.isFinite(score) || !Number.isFinite(amount) || amount < 0) throw new Error(`Row ${index + 2}: score must be finite and amount must be a non-negative number.`);
    if (labeled && !['0', '1'].includes(row.label?.trim())) throw new Error(`Row ${index + 2}: label must be 0 or 1 on every row, or omit the label column.`);
    const id = row.id?.trim() || `row-${index + 1}`;
    if (ids.has(id)) throw new Error(`Row ${index + 2}: duplicate id. Give every transaction a unique id.`);
    ids.add(id);
    return { id, score, amount, label: labeled ? Number(row.label.trim()) : null, index };
  });
}
export function wilson(successes, total) {
  if (!total) return null;
  const z = 1.96, p = successes / total, d = 1 + z * z / total;
  const c = (p + z * z / (2 * total)) / d, r = z * Math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / d;
  return [Math.max(0, c - r), Math.min(1, c + r)];
}
export function rankTransactions(rows, strategy = 'score') {
  if (!['score', 'amount'].includes(strategy)) throw new Error('Choose score or amount ranking.');
  return [...rows].sort((a, b) => b[strategy] - a[strategy] || a.index - b.index);
}
export function summarize(ranked, k) {
  if (!Number.isInteger(k) || k < 0 || k > ranked.length) throw new Error('Review count must be a whole number within the batch size.');
  const selected = ranked.slice(0, k), labeled = ranked.length > 0 && ranked.every(r => r.label !== null);
  const fraud = labeled ? ranked.reduce((n, r) => n + r.label, 0) : null, caught = labeled ? selected.reduce((n, r) => n + r.label, 0) : null;
  return { k, fraud, caught, legitimate: labeled ? k - caught : null, missed: labeled ? fraud - caught : null,
    precision: labeled && k ? caught / k : null, recall: fraud ? caught / fraud : null,
    interval: fraud ? wilson(caught, fraud) : null, selectedAmount: selected.reduce((n, r) => n + r.amount, 0) };
}
export function profileRows(rows) {
  const strategies = ['score', 'amount'].map(id => {
    const ranked = rankTransactions(rows, id);
    let cursor = 0, caught = 0, sum = 0;
    const fraud = rows.every(r => r.label !== null) ? rows.reduce((n, r) => n + r.label, 0) : null;
    const points = Array.from({ length: 51 }, (_, step) => {
      const percent = step / 10, k = Math.floor(rows.length * percent / 100 + 1e-9);
      while (cursor < k) { const r = ranked[cursor++]; caught += r.label ?? 0; sum += r.amount; }
      return { percent, k, caught: fraud === null ? null : caught, legitimate: fraud === null ? null : k - caught,
        precision: fraud !== null && k ? caught / k : null, recall: fraud ? caught / fraud : null,
        missed: fraud === null ? null : fraud - caught, selectedAmount: sum, interval: fraud ? wilson(caught, fraud) : null };
    });
    return { id, name: id === 'score' ? 'Your risk scores' : 'Largest amount first', points };
  });
  return { rows: rows.length, fraud: rows.every(r => r.label !== null) ? rows.reduce((n, r) => n + r.label, 0) : null, strategies };
}
const safeCell = value => /^[=+\-@\t\r\n\s]/.test(String(value)) ? `'${value}` : String(value);
export function exportQueue(rows, k, strategy) {
  const ranked = rankTransactions(rows, strategy).slice(0, k);
  return Papa.unparse({ fields: ['rank', 'id', 'score', 'amount', 'label'], data: ranked.map((r, i) => [i + 1, safeCell(r.id), r.score, r.amount, r.label ?? '']) }, { escapeFormulae: true });
}
export function sampleCSV() {
  let seed = 4217;
  const random = () => { seed = (Math.imul(1664525, seed) + 1013904223) >>> 0; return seed / 4294967296; };
  const rows = Array.from({ length: 2000 }, (_, i) => {
    const label = random() < 0.025 ? 1 : 0, score = label ? 0.45 + random() * 0.55 : random() ** 3 * 0.85;
    return [`example-${String(i + 1).padStart(4, '0')}`, score.toFixed(5), (3 + random() ** 3 * 1800).toFixed(2), label];
  });
  return Papa.unparse({ fields: ['id', 'score', 'amount', 'label'], data: rows });
}
