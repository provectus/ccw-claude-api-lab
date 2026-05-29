import { test, expect } from '@playwright/test';

test.describe('Dashboard Page', () => {
  test('renders heading and stat cards', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();

    // Stat cards or skeleton placeholders render
    const cards = page.locator('.MuiCard-root');
    await expect(cards.first()).toBeVisible({ timeout: 15_000 });
    const count = await cards.count();
    expect(count).toBeGreaterThanOrEqual(1);
  });

  test('shows quick action buttons', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByRole('button', { name: /Upload Files/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /View Reviews/i })).toBeVisible();
  });

  test('Upload Files navigates to /upload', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: /Upload Files/i }).click();
    await expect(page).toHaveURL(/\/upload/);
  });

  test('View Reviews navigates to /review', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: /View Reviews/i }).click();
    await expect(page).toHaveURL(/\/review/);
  });
});
