import { test, expect } from '@playwright/test';

test.describe('Upload Page', () => {
  test('renders heading and form', async ({ page }) => {
    await page.goto('/upload');
    await expect(page.getByRole('heading', { name: /Fund Data Upload/i })).toBeVisible();

    // File dropzone visible when no scenario selected
    await expect(page.getByText(/Upload Files/i).first()).toBeVisible();

    // Fund metadata form fields
    await expect(page.getByText(/Fund Type/i).first()).toBeVisible({ timeout: 10_000 });
  });

  test('scenario selector loads and populates form', async ({ page }) => {
    await page.goto('/upload');

    const scenarioInput = page.getByPlaceholder('Select a pre-configured demo scenario...');
    await expect(scenarioInput).toBeVisible({ timeout: 15_000 });

    // Open dropdown and select the first scenario
    await scenarioInput.click();
    const firstOption = page.getByRole('option').first();
    await expect(firstOption).toBeVisible({ timeout: 5_000 });
    await firstOption.click();

    // Scenario file list should appear
    await expect(page.getByText(/Included Files/i)).toBeVisible();

    // Dropzone should be hidden when scenario is selected
    await expect(page.getByText(/Drag & drop/i)).not.toBeVisible();
  });

  test('review button is disabled without input', async ({ page }) => {
    await page.goto('/upload');

    await expect(page.getByText(/Fund Type/i).first()).toBeVisible({ timeout: 10_000 });

    const submitBtn = page.locator('button[type="submit"]');
    await expect(submitBtn).toBeVisible();
    await expect(submitBtn).toBeDisabled();
  });

  test('review button enables after scenario selection', async ({ page }) => {
    await page.goto('/upload');

    const scenarioInput = page.getByPlaceholder('Select a pre-configured demo scenario...');
    await expect(scenarioInput).toBeVisible({ timeout: 15_000 });
    await scenarioInput.click();
    await page.getByRole('option').first().click();

    const submitBtn = page.locator('button[type="submit"]');
    await expect(submitBtn).toBeEnabled();
  });
});
