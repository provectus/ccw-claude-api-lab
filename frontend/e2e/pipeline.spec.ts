import { test, expect } from '@playwright/test';

/**
 * NAV Review pipeline execution E2E test.
 *
 * Requires: Backend running with ANTHROPIC_API_KEY and synthetic data.
 * Skip with: SKIP_PIPELINE=true npx playwright test
 */
test.describe('NAV Review Execution', () => {
  test.skip(
    !!process.env.SKIP_PIPELINE,
    'Skipping pipeline test (SKIP_PIPELINE=true)',
  );

  test('full NAV review from upload to completion', async ({ page }) => {
    const startTime = Date.now();

    // Step 1: Go to Upload, select scenario, and start review
    await page.goto('/upload');
    const scenarioInput = page.getByRole('combobox');
    await expect(scenarioInput).toBeVisible({ timeout: 15_000 });
    await scenarioInput.click();
    await page.getByRole('option').first().click();

    // Click "Review" button
    const reviewBtn = page.getByRole('button', { name: /Review/i });
    await expect(reviewBtn).toBeEnabled();
    await reviewBtn.click();

    // Step 2: Verify redirect to /review
    await expect(page).toHaveURL(/\/review/, { timeout: 10_000 });

    // Step 3: Wait for running state
    await expect(page.getByText(/running/i).first()).toBeVisible({ timeout: 30_000 });

    // Step 4: Wait for pipeline completion (long timeout for Claude processing)
    await expect(
      page.getByText('completed').first()
    ).toBeVisible({ timeout: 300_000 }); // 5 min max

    // Step 5: Verify stepper and panels have content
    const reasoningPanel = page.locator('.MuiAccordion-root');
    await expect(reasoningPanel.first()).toBeVisible();

    // Verify "View Review Pack" button appears on completion
    await expect(page.getByRole('button', { name: /Review Pack/i })).toBeVisible();

    // Log duration
    const duration = Math.round((Date.now() - startTime) / 1000);
    console.log(`NAV review completed in ${duration}s`);
    expect(duration).toBeLessThan(300);
  });
});
