import { expect, test } from "@playwright/test";

test("opens the terminal and navigates through core screens", async ({
  page,
}) => {
  await page.goto("/");
  await expect(page).toHaveURL(/\/terminal\/EURUSD/);
  await expect(page.getByRole("heading", { level: 1 })).toContainText("EURUSD");
  await expect(page.getByText("Demo stream")).toBeVisible({ timeout: 10_000 });

  await page.getByRole("link", { name: "Portfolio" }).click();
  await expect(page.getByRole("heading", { level: 1 })).toHaveText(
    "Portfolio balance",
  );

  await page.getByRole("link", { name: "News" }).click();
  await expect(page.getByRole("heading", { level: 1 })).toHaveText(
    "Market news",
  );

  await page.getByRole("link", { name: "Calendar" }).click();
  await expect(page.getByRole("heading", { level: 1 })).toHaveText(
    "Economic calendar",
  );
});

test("stores valid local terminal preferences", async ({ page }) => {
  await page.goto("/settings");
  await expect(
    page.getByRole("button", { name: "Save settings" }),
  ).toBeEnabled();
  await page.getByLabel("Candles kept in view").fill("350");
  await page.getByRole("button", { name: "Save settings" }).click();
  await expect(page.getByText("Settings saved on this device.")).toBeVisible();
  await expect
    .poll(() =>
      page.evaluate(() => localStorage.getItem("terminal-preferences")),
    )
    .toContain('"maxCandles":350');
});
