import { test, expect } from '@playwright/test';

const ROOT_PAGE = 'http://127.0.0.1:5001/';
const NEW_SESSION_PAGE = 'http://127.0.0.1:5001/new_session';

test.describe.serial('Session Creation and Management', () => {

  test('should create, fork, create child, modify, and delete sessions', async ({ page }) => {
    test.setTimeout(240000); // Increase timeout for the entire multi-step test

    // --- PART 1: Create and Fork Session ---

    await page.goto(NEW_SESSION_PAGE);

    // Fill out the form to create the initial session
    await page.locator('input[name="purpose"]').fill('e2e test');
    await page.locator('textarea[name="background"]').fill('This is a regression test by e2e.');
    await page.locator('input[name="roles"]').fill('roles/engineer.md');
    await page.locator('input[name="references"]').fill('README.md');
    await page.locator('textarea[name="instruction"]').fill('Tell me about Flask using pipe_tools.google_web_search');
    await page.locator('input[name="multi_step_reasoning_enabled"]').check();
    await page.locator('input[name="temperature"]').fill('0.5');
    await page.locator('input[name="top_p"]').fill('1');
    await page.locator('input[name="top_k"]').fill('10');
    await page.locator('button[type="submit"]').click();

    // Wait for navigation and assert initial creation
    await page.waitForURL(/.*\/session\/.*/, { timeout: 180000 });
    await expect(page.locator('.turn')).toHaveCount(4);
    const originalSessionUrl = page.url();

    // Fork from the last turn
    page.on('dialog', dialog => dialog.accept()); // Accept any confirmation dialogs
    const turnElement = await page.locator('#turn-3');
    await turnElement.hover();
    await turnElement.locator('.fork-btn').click({force: true});
    
    // Wait for navigation to the new forked session and store its URL
    await page.waitForURL(url => url.toString() !== originalSessionUrl, { timeout: 30000 });
    await expect(page.locator('#turns-column h2')).toContainText('Fork of: e2e test');
    const forkedSessionUrl = page.url();

    // Go back to the original session to delete it
    await page.goto(originalSessionUrl);
    await page.locator('button:has-text("Delete Session")').click();
    await page.waitForURL(ROOT_PAGE);
  });

  test('Create a child session from the fork', async ({page}) => {
    await page.goto(NEW_SESSION_PAGE);
    await page.waitForLoadState('domcontentloaded');
    
    // Select the forked session as the parent
    await page.selectOption('#parent', { label: 'Fork of: e2e test', }, { force: true });
    
    // Fill in new details for the child session
    await page.locator('input[name="purpose"]').fill('Child session test');
    await page.locator('textarea[name="background"]').fill('This is a child session test.');
    await page.locator('textarea[name="instruction"]').fill('This is the first instruction for the child session.');
    await page.locator('button[type="submit"]').click();

    // Assert the new child session is created correctly
    await page.waitForURL(/.*\/session\/.*/, { timeout: 180000 });
    await expect(page.locator('#turns-column h2')).toContainText('Child session test');
  });

  test('Modify the forked session', async ({page}) => {
    await page.goto(ROOT_PAGE);
    await page.waitForLoadState('domcontentloaded');
    page.on('dialog', dialog => dialog.accept()); // Accept any confirmation dialogs
    
    await page.getByText('Fork of: e2e test').click();
    await page.waitForLoadState('domcontentloaded');
    const initialTurnCount = await page.locator('.turn').count();

    // Delete the last turn
    const lastTurn = await page.locator('.turn').last();
    await lastTurn.hover();
    await lastTurn.locator('.delete-btn').click();
    await expect(page.locator('.turn')).toHaveCount(initialTurnCount - 1, { timeout: 15000 });

    // Edit the first turn
    const firstTurn = await page.locator('.turn').first();
    await firstTurn.hover();
    await firstTurn.locator('.edit-btn').click();
    
    const instructionTextarea = firstTurn.locator('textarea');
    const currentInstruction = await instructionTextarea.inputValue();
    await instructionTextarea.fill(currentInstruction + ' edited');
    
    await firstTurn.locator('button:has-text("Save")').click();

    // Assert the edit was saved
    await expect(firstTurn.locator('pre.editable')).toHaveText(/edited$/);

    // Delete the forked session
    await expect(page.locator('a').filter({hasText: 'Child session test'})).toHaveCount(1);
    await page.locator('button:has-text("Delete Session")').click();
    await page.waitForURL(ROOT_PAGE);
    await expect(page.locator('a').filter({hasText: 'Child session test'})).toHaveCount(0);
  });
});
