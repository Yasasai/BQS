# How to Run Verification

To run the status check on your terminal, please follow these steps:

1.  **Open your terminal** (Command Prompt, PowerShell, or VS Code Terminal).
2.  **Navigate to the folder**:
    ```bash
    cd "C:\Users\YasasviUpadrasta\Documents\Data Analytics\Internal Innovation\BQS"
    ```
3.  **Run the script**:
    ```bash
    python read_sync_status.py
    ```

## Important Note
I have just applied a fix to the database table `sync_meta` which was causing the "column does not exist" error.
The clean-up script (`force_reset_sync_meta.py`) and the sync job (`sync_manager.py`) are running/have run to ensure the table is correct and populated.
Please try running the command now.

*Note: The repair job is currently running in the background. If you see an error, please wait 30 seconds and try again.*
