
import { test, expect } from '@playwright/test';

// Roles based on AuthContext.tsx
const MOCK_SA = {
    id: 'sa-001',
    email: 'john.doe@company.com',
    name: 'John Doe',
    role: 'SA',
    displayRole: 'Solution Architect'
};

test.describe('Golden Path Smoke Test', () => {
    test.beforeEach(async ({ page }) => {
        // 1. Mock Authentication: Inject SA user into localStorage
        await page.addInitScript((user) => {
            window.localStorage.setItem('bqs_user', JSON.stringify(user));
        }, MOCK_SA);
    });

    test('SA Journey: Dashboard -> Opportunity -> Scoring -> Save Draft', async ({ page }) => {
        // 2. Land on Dashboard
        await page.goto('/');

        // Verify Dashboard loads (looking for SA specific content or general layout)
        await expect(page).toHaveTitle(/BQS/);
        await expect(page.getByText('Solution Architect')).toBeVisible();

        // 3. Open Opportunity
        // We assume there's at least one opportunity in the list.
        // Clicking the first 'View' or 'Detail' link.
        const firstOppLink = page.locator('button:has-text("View"), a:has-text("View")').first();
        await expect(firstOppLink).toBeVisible();
        await firstOppLink.click();

        // Verify Opportunity Details page
        await expect(page).toHaveURL(/\/opportunity\/[a-zA-Z0-9-]+/);
        await expect(page.getByText('Opportunity Details')).toBeVisible();

        // 4. Open Scoring Interface
        const scoreButton = page.getByRole('button', { name: /Score|Assessment/i });
        await expect(scoreButton).toBeVisible();
        await scoreButton.click();

        // Verify Scoring page
        await expect(page).toHaveURL(/\/score\/[a-zA-Z0-9-]+/);
        await expect(page.getByText('Strategic Fit')).toBeVisible();

        // 5. Submit Draft
        // Find a score radio/button/input (assuming 1-5 scale)
        // Looking for the first section and picking a score
        const firstSectionScore = page.locator('button:has-text("4"), input[value="4"]').first();
        await firstSectionScore.click();

        // Trigger "Save Draft"
        const saveDraftButton = page.getByRole('button', { name: /Save Draft/i });
        await expect(saveDraftButton).toBeVisible();
        await saveDraftButton.click();

        // Verify Success Toast or Message
        await expect(page.getByText(/Saved|Success/i)).toBeVisible();
    });
});
