import type { Page } from '@playwright/test';

/** Base URL for direct API calls (bypassing nginx proxy). */
export const API_BASE = process.env.API_BASE || 'http://localhost:8000';

/**
 * Wait until the pipeline stepper shows all steps completed.
 * Polls the stepper step icons looking for all to be in "completed" state.
 */
export async function waitForPipelineComplete(
  page: Page,
  { timeout = 300_000 }: { timeout?: number } = {},
): Promise<void> {
  // Wait for the "completed" chip to appear on the pipeline status
  await page.getByRole('status').or(page.locator('.MuiChip-root')).filter({ hasText: 'completed' }).waitFor({
    state: 'visible',
    timeout,
  });
}

/**
 * Wait for any text to appear on the page (useful for loading states).
 */
export async function waitForText(
  page: Page,
  text: string,
  { timeout = 30_000 }: { timeout?: number } = {},
): Promise<void> {
  await page.getByText(text).first().waitFor({ state: 'visible', timeout });
}
