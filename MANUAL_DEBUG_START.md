# 🚑 EMERGENCY DEBUG - Manual Start

If the "Start" script isn't working or you see a blank page, please follow these steps to run everything manually. This will show us any hidden errors.

## 1. Stop Everything

Close all terminal windows and command prompts running BQS.

## 2. Start Backend (Terminal 1)

Open a new terminal (Command Prompt or PowerShell) and run:

```bash
cd C:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS\backend
uvicorn app.main:app --reload --port 8000
```
**Success check**: You should see lines like `Uvicorn running on http://0.0.0.0:8000`.

## 3. Start Frontend (Terminal 2)

Open a **separate** terminal window and run:

```bash
cd C:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS\frontend
npm run dev
```

**CRITICAL STEP**: Look at the output! It will say:
```
  VITE v5.x.x  ready in 500 ms

  ➜  Local:   http://localhost:5176/
  ➜  Network: use --host to expose
```

**Use the URL shown in YOUR terminal.** If it says `5177` or `5173`, go there instead!

## 4. Check for Errors

1. Open **Chrome/Edge Developer Tools** (Press F12).
2. Click the **Console** tab.
3. If the page is blank, **take a screenshot of the red errors** in the Console.

## Common Fixes

### "Site can't be reached"
- The frontend server isn't running. Check Terminal 2.
- You are on the wrong port. Check the "Local:" URL in Terminal 2.

### Blank White Screen
- Check the F12 Console for "ReferenceError" or "import error".
- Could be a missing package. Try running `npm install` in the frontend folder.

### "Failed to fetch" / Network Error
- Backend isn't running. Check Terminal 1.
- Backend is on wrong port. Make sure Terminal 1 says `port 8000`.

---

**If it still fails, please tell me EXACTLY what you see in the F12 Console!**
