import { parseTransactions, profileRows } from './core.js';
self.onmessage = ({ data }) => {
  try { const rows = parseTransactions(data); self.postMessage({ rows, profile: profileRows(rows) }); }
  catch (error) { self.postMessage({ error: error.message }); }
};
