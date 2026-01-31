# ✅ FIXED: Port 5176 & Server Cleanup

## 🔄 Why does the port keep changing? (5173 -> 5175 -> 5176)
This happens because the **previous servers are still running** in the background. When you start a new one, it sees port 5175 is "taken" and jumps to 5176.

## 🛠️ Updates

1.  **Configured for 5176**:
    - Updated `vite.config.ts` to use port **5176**.
    - Updated `start_dashboard.bat` to open **http://localhost:5176**.

2.  **Created Cleanup Script**:
    - I made a new script: **`kill_servers.bat`**.
    - Run this to **close all running servers** and free up your ports.

## 🚀 Recommended Steps

1.  **Run `kill_servers.bat`**:
    - This will stop all the old background processes.

2.  **Run `start_dashboard.bat`**:
    - Choose **Option 5** (Start Both).
    - It should now work on **5176** (or go back to default if configured).

3.  **Access Dashboard**:
    - **`http://localhost:5176`**

Everything is updated for the new port.
