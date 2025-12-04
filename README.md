# ACR122U NFC Toolkit for Windows

A robust, portable Python toolkit for reading, cracking, and cloning Mifare Classic cards using the **ACR122U** USB reader on Windows. 

This project includes pre-compiled, patched binaries of `libnfc` and `mfoc` that fix common Windows issues (missing DLLs, driver conflicts) and adds smart logic to handle **"Chimera Cards"** (1K chips masquerading as 4K).

## 📂 Project Structure

Ensure your directory looks exactly like this for the scripts to work:

```text
.
├── check-card-type.py    # Tool to identify if card is Gen 1 (Magic) or Gen 2 (CUID)
├── nfc-dumper.py         # Smart wrapper for MFOC (Cracks keys + Reads data)
├── nfc-writer.py         # Wrapper for libnfc (Writes dumps to Gen 1 cards)
├── libnfc/               # Pre-compiled libnfc tools
│   ├── nfc-mfclassic.exe
│   ├── libnfc.conf
│   └── (Required DLLs: libusb-1.0.dll, libgcc_s_seh-1.dll, etc.)
└── mfoc/                 # Pre-compiled MFOC cracker
    ├── mfoc.exe
    └── (Required DLLs)
````

## 🛠 Prerequisites

### 1\. The Drivers (Crucial\!)

The ACR122U works out-of-the-box with Windows for basic tasks, but **libnfc requires a direct USB driver**. You must replace the stock driver.

1.  Plug in your ACR122U.
2.  Download **[Zadig](https://zadig.akeo.ie/)**.
3.  Go to **Options** \> **List All Devices**.
4.  Select **"ACR122U PICC Interface"** (or Interface 0).
      * *Warning: Do not select the "Composite Parent" or generic "ACR122U" if an Interface option exists.*
5.  Select **libusbK (v3.0.7.0)** in the target box.
6.  Click **Replace Driver**.

### 2\. Python Dependencies

The scripts use standard libraries, but `check-card-type.py` requires `pyscard` to talk to the generic Windows smart card API.

```bash
pip install pyscard
```

-----

## 🚀 Usage Guide

### Step 1: Identify Your Target Card

Before cloning, you need to know if your writable card is **Gen 1** (Magic/UID changeable via backdoor) or **Gen 2** (CUID/Android compatible).

Run:

```powershell
python check-card-type.py
```

  * **Gen 2 (CUID):** Uses standard writing commands.
  * **Gen 1 (Magic):** Requires the special backdoor commands used by `nfc-writer.py`.

### Step 2: Crack & Dump a Card

Use this to read a locked card. It uses **MFOC** (Nested Attack) to recover keys.

**Smart Feature:** This script automatically detects **"Chimera Cards"** (cards that claim to be 4K but are actually 1K) and fixes the read logic on the fly to prevent crashes.

```powershell
python nfc-dumper.py my_original_card.mfd
```

  * *Note: This process can take 1-20 minutes depending on card security.*

### Step 3: Write to a Magic Card (Gen 1)

Once you have your `.mfd` dump file, use this to write it to a special "Chinese Magic Card" (Gen 1). It will overwrite the **UID (Block 0)**.

```powershell
python nfc-writer.py my_original_card.mfd
```

-----

## 🔧 Compilation Notes (For Developers)

The binaries in `./libnfc` and `./mfoc` were manually compiled on **MSYS2 MinGW64** to ensure portability.

**Key Patches Applied:**

1.  **Libnfc:**
      * CMake updated to support modern MSYS2.
      * Hardcoded `lusb0_usb.h` includes patched to `usb.h`.
2.  **MFOC:**
      * Missing `err.h` header manually implemented for Windows.
      * **Custom Logic:** Added support for `MFOC_FORCE_1K` environment variable to handle SAK 0x98 (Mifare Plus) cards correctly, preventing "Sector 16" read errors on fake 4K cards.

## ⚠️ Troubleshooting

**"No NFC device found"**

  * Did you run Zadig?
  * Try unplugging and replugging the reader.
  * Ensure no other software (like standard PC/SC middleware) is hogging the reader.

**"Silent Exit" / No Output**

  * You are likely missing a DLL in the `libnfc` or `mfoc` folder.
  * Required DLLs usually include: `libusb-1.0.dll`, `libgcc_s_seh-1.dll`, `libwinpthread-1.dll`.

**"Authentication Failed" during Write**

  * Your destination card might not be a "Gen 1 Magic Card". If it is a standard Mifare card or a Gen 2 (CUID), `nfc-mfclassic.exe` cannot overwrite Block 0.