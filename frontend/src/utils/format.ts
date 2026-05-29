/** Shared formatting utilities. */

export function formatDollars(val: number): string {
  if (Math.abs(val) >= 1e9) return `$${(val / 1e9).toFixed(2)}B`;
  if (Math.abs(val) >= 1e6) return `$${(val / 1e6).toFixed(1)}M`;
  return `$${val.toLocaleString()}`;
}

export function formatPercent(val: number, decimals = 1): string {
  return `${(val * 100).toFixed(decimals)}%`;
}

export function formatNumber(val: number): string {
  return val.toLocaleString();
}
