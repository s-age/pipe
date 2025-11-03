import { test, expect } from "@playwright/test";

const ROOT_PAGE = "http://127.0.0.1:5001/";
const NEW_SESSION_PAGE = "http://127.0.0.1:5001/new_session";

test.describe.serial("Session Creation and Management", () => {
  test("should create, fork, create child, modify, and delete sessions", async ({
    page,
  }) => {
    // --- PART 1: Create and Fork Session ---

    await page.goto(NEW_SESSION_PAGE);

    // Fill out the form to create the initial session
    await page.locator('input[name="purpose"]').fill("e2e test");
    await page
      .locator('textarea[name="background"]')
      .fill("This is a regression test by e2e.");
    await page.locator('input[name="roles"]').fill("roles/engineer.md");
    await page.locator('input[name="references"]').fill("README.md");
    await page
      .locator('textarea[name="instruction"]')
      .fill("Tell me about Flask using pipe_tools.google_web_search");
    await page.locator('input[name="multi_step_reasoning_enabled"]').check();
    await page.locator('input[name="temperature"]').fill("0.5");
    await page.locator('input[name="top_p"]').fill("1");
    await page.locator('input[name="top_k"]').fill("10");
    await page.locator('button[type="submit"]').click();

    // Wait for navigation and assert initial creation
    await page.waitForURL(/.*\/session\/.*/, { timeout: 60000 });
    await expect(page.locator(".turn")).toHaveCount(4);
    const originalSessionUrl = page.url();

    // Fork from the last turn
    page.on("dialog", (dialog) => dialog.accept()); // Accept any confirmation dialogs
    const turnElement = await page.locator("#turn-3");
    await turnElement.hover();
    await turnElement.locator(".fork-btn").click({ force: true });

    // Wait for navigation to the new forked session and store its URL
    await page.waitForURL((url) => url.toString() !== originalSessionUrl, {
      timeout: 60000,
    });
    await expect(page.locator("#turns-column h2")).toContainText("Fork of: e2e test");

    // Go back to the original session to delete it
    await page.goto(originalSessionUrl);
    await page.locator('button:has-text("Delete Session")').click();
    await page.waitForURL(ROOT_PAGE);
  });

  test("should create a new session with various parameters, verify initial response, and edit meta-information", async ({
    page,
  }) => {
    await page.goto(NEW_SESSION_PAGE);

    // Initial values
    const initialPurpose = "Initial Session Purpose";
    const initialBackground = "Initial Session Background";
    const initialRoles = "roles/engineer.md";
    const initialReferences = "README.md";
    const initialInstruction = "Initial Session Instruction";
    const initialTemperature = "0.6";
    const initialTopP = "0.9";
    const initialTopK = "20";

    // Fill out the form with all parameters
    await page.locator('input[name="purpose"]').fill(initialPurpose);
    await page.locator('textarea[name="background"]').fill(initialBackground);
    await page.locator('input[name="roles"]').fill(initialRoles);
    await page.locator('input[name="references"]').fill(initialReferences);
    await page.locator('textarea[name="instruction"]').fill(initialInstruction);
    await page.locator('input[name="multi_step_reasoning_enabled"]').check();
    await page.locator('input[name="temperature"]').fill(initialTemperature);
    await page.locator('input[name="top_p"]').fill(initialTopP);
    await page.locator('input[name="top_k"]').fill(initialTopK);
    await page.locator('button[type="submit"]').click();

    // Verify new session URL
    await page.waitForURL(/.*\/session\/.*/, { timeout: 60000 });
    expect(page.url()).toMatch(/http:\/\/127\.0\.0\.1:5001\/session\/[a-f0-9]{64}/);
    const currentSessionUrl = page.url();

    // Verify session title
    await expect(page.locator("#turns-column h2")).toContainText(initialPurpose);

    // Verify number of turns (2: user_task, model_response)
    await expect(page.locator(".turn")).toHaveCount(2);

    // Verify user instruction
    const userInstructionTurn = page.locator(".turn.user_task");
    await expect(userInstructionTurn.locator("pre")).toContainText(initialInstruction);

    // Verify model response content
    const modelResponseTurn = page.locator(".turn.model_response");
    await expect(modelResponseTurn.locator(".rendered-markdown")).not.toBeEmpty();

    // --- Edit Meta-information ---
    const updatedPurpose = "Updated Session Purpose";
    const updatedBackground = "Updated Session Background";
    const updatedRoles = "roles/reviewer.md, roles/engineer.md";
    const updatedTemperature = "0.7";
    const updatedTopP = "0.8";
    const updatedTopK = "15";

    await page.locator('[data-field="purpose"]').fill(updatedPurpose);
    await page.locator('[data-field="background"]').fill(updatedBackground);
    await page.locator('[data-field="roles"]').fill(updatedRoles);
    await page.locator('[data-field="temperature"]').fill(updatedTemperature);
    await page.locator('[data-field="top_p"]').fill(updatedTopP);
    await page.locator('[data-field="top_k"]').fill(updatedTopK);

    page.on("dialog", (dialog) => dialog.accept()); // Accept the "Session meta saved successfully!" alert
    await page.locator("#save-meta-btn").click();

    // Reload the page and verify updated meta-information
    await page.waitForURL(currentSessionUrl, { timeout: 60000 }); // Wait for reload
    await expect(page.locator("#turns-column h2")).toContainText(updatedPurpose);
    await expect(page.locator('[data-field="purpose"]')).toHaveValue(updatedPurpose);
    await expect(page.locator('[data-field="background"]')).toHaveValue(
      updatedBackground,
    );
    await expect(page.locator('[data-field="roles"]')).toHaveValue(updatedRoles);
    await expect(page.locator('[data-field="temperature"]')).toHaveValue(
      updatedTemperature,
    );
    await expect(page.locator('[data-field="top_p"]')).toHaveValue(updatedTopP);
    await expect(page.locator('[data-field="top_k"]')).toHaveValue(updatedTopK);

    // Delete the created session for cleanup
    await page.locator('button:has-text("Delete Session")').click();
    await page.waitForURL(ROOT_PAGE);
  });

  test("Create a child session from the fork", async ({ page }) => {
    await page.goto(NEW_SESSION_PAGE);
    await page.waitForLoadState("domcontentloaded");

    // Select the forked session as the parent
    await page.selectOption("#parent", { label: "Fork of: e2e test" }, { force: true });

    // Fill in new details for the child session
    await page.locator('input[name="purpose"]').fill("Child session test");
    await page
      .locator('textarea[name="background"]')
      .fill("This is a child session test.");
    await page
      .locator('textarea[name="instruction"]')
      .fill("This is the first instruction for the child session.");
    await page.locator('button[type="submit"]').click();

    // Assert the new child session is created correctly
    await page.waitForURL(/.*\/session\/.*/, { timeout: 60000 });
    await expect(page.locator("#turns-column h2")).toContainText("Child session test");
  });

  test("Modify the forked session", async ({ page }) => {
    await page.goto(ROOT_PAGE);
    await page.waitForLoadState("domcontentloaded");
    page.on("dialog", (dialog) => dialog.accept()); // Accept any confirmation dialogs

    await page.getByText("Fork of: e2e test").first().click();
    await page.waitForLoadState("domcontentloaded");
    const initialTurnCount = await page.locator(".turn").count();

    // Delete the last turn
    const lastTurn = await page.locator(".turn").last();
    await lastTurn.hover();
    await lastTurn.locator(".delete-btn").click();
    await expect(page.locator(".turn")).toHaveCount(initialTurnCount - 1, {
      timeout: 15000,
    });

    // Edit the first turn
    const firstTurn = await page.locator(".turn").first();
    await firstTurn.hover();
    await firstTurn.locator(".edit-btn").click();

    const instructionTextarea = firstTurn.locator("textarea");
    const currentInstruction = await instructionTextarea.inputValue();
    await instructionTextarea.fill(currentInstruction + " edited");

    await firstTurn.locator('button:has-text("Save")').click();

    // Assert the edit was saved
    await expect(firstTurn.locator("pre.editable")).toHaveText(/edited$/);

    // Delete the forked session
    await expect(
      page.locator("a").filter({ hasText: "Child session test" }),
    ).toHaveCount(1);
    await page.locator('button:has-text("Delete Session")').click();
    await page.waitForURL(ROOT_PAGE);
    await expect(
      page.locator("a").filter({ hasText: "Child session test" }),
    ).toHaveCount(0);
  });

  test("should fork an existing session at a specific turn", async ({ page }) => {
    // Create a new session
    await page.goto(NEW_SESSION_PAGE);
    await page.locator('input[name="purpose"]').fill("Original Session for Fork Test");
    await page
      .locator('textarea[name="background"]')
      .fill("This session is created to test forking functionality.");
    await page.locator('input[name="roles"]').fill("roles/engineer.md");
    await page.locator('input[name="references"]').fill("README.md");
    await page
      .locator('textarea[name="instruction"]')
      .fill("Initial instruction for fork test.");
    await page.locator('button[type="submit"]').click();

    await page.waitForURL(/.*\/session\/.*/, { timeout: 60000 });
    const originalSessionUrl = page.url();
    await expect(page.locator(".turn")).toHaveCount(2); // System, User, System, Model

    // Fork from turn 1 (user instruction turn)
    page.on("dialog", (dialog) => dialog.accept());
    const turnElement = await page.locator("#turn-1"); // Assuming turn-1 is the user instruction
    await turnElement.hover();
    await turnElement.locator(".fork-btn").click({ force: true });

    // Wait for navigation to the new forked session
    await page.waitForURL((url) => url.toString() !== originalSessionUrl, {
      timeout: 60000,
    });
    const forkedSessionUrl = page.url();

    // Verify the forked session's URL, title, and number of turns
    expect(forkedSessionUrl).toMatch(
      /http:\/\/127\.0\.0\.1:5001\/session\/[a-f0-9]{64}/,
    );
    await expect(page.locator("#turns-column h2")).toContainText(
      "Fork of: Original Session for Fork Test",
    );
    await expect(page.locator(".turn")).toHaveCount(2); // System, User (forked at turn 1)

    // Cleanup: Delete both sessions
    // Delete forked session first
    await page.goto(forkedSessionUrl);
    await page.locator('button:has-text("Delete Session")').click();
    await page.waitForURL(ROOT_PAGE);

    // Delete original session
    await page.goto(originalSessionUrl);
    await page.locator('button:has-text("Delete Session")').click();
    await page.waitForURL(ROOT_PAGE);
  });
});
