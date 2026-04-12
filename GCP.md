# Adding Team Members to a Google Cloud Project (IAM)

This guide walks you through adding your project teammates to your Google Cloud Project so they have full access to shared resources like BigQuery.

> [!IMPORTANT]
> **CLASSROOM USE ONLY — Security shortcut ahead.**
> In this course, everyone on the team is being granted the **Owner** role for simplicity. In a real production application you would **never** do this. Production projects follow the principle of least privilege — each person (and each service) gets only the minimum permissions required for their specific job. Roles like Owner and Editor give broad, destructive capabilities (deleting databases, modifying billing, etc.) and should be reserved for a very small number of trusted administrators. We are bypassing these security considerations intentionally to reduce friction in a classroom setting.

---

## Prerequisites

- You must be the **Owner** of the GCP project (i.e., you created it)
- Your teammates need a Google account (their Purdue `@purdue.edu` address works)

---

## Step 1 — Open IAM & Admin

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Make sure your project is selected in the top-left dropdown
3. In the left navigation menu, click **IAM & Admin** → **IAM**

---

## Step 2 — Grant Access to a Teammate

1. Click the **+ Grant Access** button near the top of the IAM page
2. In the **New principals** field, type your teammate's Google account email address (e.g., `teammate@purdue.edu`)
3. Under **Assign roles**, click **Select a role**
4. In the search box, type `Owner`
5. Select **Owner** from the list (it appears under the *Basic* category)
6. Click **Save**

Repeat this process for each teammate.

---

## Step 3 — Confirm Access

1. Your teammate should now appear in the IAM principals list with the **Owner** role
2. Ask your teammate to navigate to [console.cloud.google.com](https://console.cloud.google.com) and confirm they can see the shared project in their project dropdown

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Teammate doesn't see the project | Make sure they are signed in with the exact email address you added |
| "Permission denied" errors | Verify the role shows as **Owner** in the IAM list, not a more restricted role |
| Can't find the project dropdown | Click the project name/ID at the very top of the console to open the project picker |
