import { test, expect } from '@playwright/test';

/**
 * Review Pack page E2E test.
 *
 * Tests verify the empty state and, when a pipeline has completed,
 * the review pack display with NAV-specific content.
 */
test.describe('Review Pack Page', () => {
  test('shows empty state when no review has run', async ({ page }) => {
    await page.goto('/review-pack');

    const emptyState = page.getByRole('heading', { name: /No Assessment Available/i });
    const reviewHeading = page.getByRole('heading', { name: /Deal Assessment|Review Pack/i });

    await expect(
      emptyState.or(reviewHeading)
    ).toBeVisible({ timeout: 15_000 });
  });

  test('empty state has upload navigation button', async ({ page }) => {
    await page.goto('/review-pack');

    const emptyState = page.getByRole('heading', { name: /No Assessment Available/i });
    const isEmpty = await emptyState.isVisible().catch(() => false);

    if (isEmpty) {
      await expect(page.getByRole('button', { name: /Upload Files/i })).toBeVisible();
    }
  });
});

/**
 * Post-pipeline review pack tests.
 * These should run AFTER the pipeline.spec.ts completes a full run.
 */
test.describe('Review Pack Page (post-pipeline)', () => {
  test.skip(
    !!process.env.SKIP_PIPELINE,
    'Skipping post-pipeline tests (SKIP_PIPELINE=true)',
  );

  test('displays review pack after pipeline completion', async ({ page }) => {
    // First complete a pipeline run
    await page.goto('/upload');
    const scenarioInput = page.getByRole('combobox');
    await expect(scenarioInput).toBeVisible({ timeout: 15_000 });
    await scenarioInput.click();
    await page.getByRole('option').first().click();

    const reviewBtn = page.getByRole('button', { name: /Review/i });
    await reviewBtn.click();

    // Wait for pipeline to complete
    await expect(page).toHaveURL(/\/review/, { timeout: 10_000 });
    await expect(
      page.getByText('completed').first()
    ).toBeVisible({ timeout: 300_000 });

    // Navigate to review pack
    await page.getByRole('button', { name: /Review Pack/i }).click();
    await expect(page).toHaveURL(/\/review-pack/);

    // Verify recommendation badge
    await expect(
      page.getByText(/APPROVE|ESCALATE|HOLD/i).first()
    ).toBeVisible({ timeout: 10_000 });

    // Confidence indicator
    await expect(page.getByText(/Confidence/i).first()).toBeVisible();

    // NAV-specific metric cards
    await expect(page.getByText('Total NAV')).toBeVisible();
    await expect(page.getByText('NAV Change')).toBeVisible();

    // Key Variances section
    await expect(page.getByText('Key Variances')).toBeVisible();

    // Exceptions section
    await expect(page.getByText('Exceptions')).toBeVisible();
  });
});
