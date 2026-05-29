import { test, expect } from '@playwright/test';

test.describe('Navigation', () => {
  test('sidebar navigates to all pages', async ({ page }) => {
    await page.goto('/');

    // Dashboard → Upload
    await page.getByRole('button', { name: /Fund Data Upload/i }).click();
    await expect(page).toHaveURL(/\/upload/);

    // Upload → NAV Review
    await page.getByRole('button', { name: /NAV Review/i }).click();
    await expect(page).toHaveURL(/\/review/);

    // NAV Review → Review Pack
    await page.getByRole('button', { name: /Review Pack/i }).click();
    await expect(page).toHaveURL(/\/review-pack/);

    // Review Pack → Dashboard
    await page.getByRole('button', { name: /Dashboard/i }).click();
    await expect(page).toHaveURL('/');
  });

  test('Documentation link points to manual.html', async ({ page }) => {
    await page.goto('/');

    const docsLink = page.getByRole('link', { name: /Documentation/i });
    await expect(docsLink).toBeVisible();
    await expect(docsLink).toHaveAttribute('href', '/manual.html');
    await expect(docsLink).toHaveAttribute('target', '_blank');
  });

  test('NAV Review Analyst branding visible in sidebar', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByText('NAV Review Analyst').first()).toBeVisible();
    await expect(page.getByText('Fund Administration').first()).toBeVisible();
  });
});
