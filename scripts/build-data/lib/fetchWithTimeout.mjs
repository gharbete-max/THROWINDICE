// Every source layer shares one fetch helper: a hard timeout (a hung
// connection must not stall the whole pipeline) and a realistic browser
// UA (several of the free/unofficial endpoints 403 on the default Node UA).
const UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36";

export async function fetchWithTimeout(url, { timeoutMs = 8000, headers = {}, ...rest } = {}) {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const res = await fetch(url, {
      signal: ctrl.signal,
      headers: { "User-Agent": UA, Accept: "*/*", ...headers },
      ...rest,
    });
    if (!res.ok) throw new Error(`HTTP ${res.status} ${res.statusText}`);
    return res;
  } finally {
    clearTimeout(t);
  }
}
