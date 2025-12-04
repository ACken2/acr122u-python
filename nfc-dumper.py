import subprocess
import os
import sys
import time

# --- CONFIGURATION ---
BINARY_FOLDER = "mfoc"
TOOL_NAME = "mfoc.exe"

# Speed Tuning (Increased slightly to be safe)
PROBE_COUNT = 40  
TOLERANCE = 40    

def run_mfoc_process(tool_path, output_file, cwd, force_mode=None):
    """
    Runs MFOC and monitors output for specific card signatures and errors.
    Returns: (return_code, context)
    """
    cmd = [tool_path]
    env = os.environ.copy()

    # Handle Force Modes
    if force_mode == "1k":
        print(f"   [DEBUG] Setting MFOC_FORCE_1K=1 (Treating SAK 98 as 1K)")
        env["MFOC_FORCE_1K"] = "1"
    
    cmd.extend(["-P", str(PROBE_COUNT)])
    cmd.extend(["-T", str(TOLERANCE)])
    cmd.extend(["-O", output_file])

    print(f"\n[EXEC] Running: {' '.join(cmd)}")
    
    process = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1, 
        env=env
    )

    # Context flags to decide next steps
    context = {
        "sak_98_detected": False,
        "sak_error": False,
        "crack_failed": False
    }

    while True:
        line = process.stdout.readline()
        if not line and process.poll() is not None:
            break
        
        if line:
            sys.stdout.write(line)
            sys.stdout.flush()
            
            # 1. Detect if it's the tricky Mifare Plus (SAK 98)
            if "SAK (SEL_RES): 98" in line:
                context["sak_98_detected"] = True
                
            # 2. Detect the old "Unknown Card" error
            if "Cannot determine card type" in line:
                context["sak_error"] = True

            # 3. Detect probing failure
            if "ERROR: No success" in line:
                context["crack_failed"] = True

    return_code = process.wait()
    return return_code, context

def crack_card(output_filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tools_dir = os.path.join(script_dir, BINARY_FOLDER)
    tool_path = os.path.join(tools_dir, TOOL_NAME)
    abs_output_file = os.path.abspath(output_filename)

    if not os.path.exists(tool_path):
        print(f"Error: Could not find {TOOL_NAME} in {tools_dir}")
        return

    print(f"--- Starting Smart Key Cracking ---")
    print(f"Target: {abs_output_file}")
    print("\n[INSTRUCTION] Place the LOCKED card on the reader now.")
    time.sleep(2)

    # --- ATTEMPT 1: Standard Detection ---
    print("\n>>> Attempt 1: Standard Run")
    code, ctx = run_mfoc_process(tool_path, abs_output_file, tools_dir)

    if code == 0:
        print("\n[SUCCESS] Keys recovered on Attempt 1!")
        return

    # --- DECISION LOGIC ---
    print("\n" + "="*60)
    print(f"[ANALYSIS] Attempt 1 Failed (Code {code})")
    
    # CASE A: It detected SAK 98, tried to crack 4K, and failed (Your Chimera Case)
    if ctx["sak_98_detected"] and code != 0:
        print("[DIAGNOSIS] Card reported SAK 98 (Mifare Plus/4K) but failed.")
        print("            This is likely a 'Chimera' card (1K chip pretending to be 4K).")
        print("            The tool tried to crack non-existent sectors (16+) and timed out.")
        print(">>> ACTION: Applying Force 1K Mode...")
        print("="*60)
        time.sleep(2)
        
        code_retry, _ = run_mfoc_process(tool_path, abs_output_file, tools_dir, force_mode="1k")
        if code_retry == 0:
            print("\n[SUCCESS] Chimera Card cracked successfully (Forced 1K)!")
            return

    # CASE B: The old "Unknown Card" error (If C code wasn't patched)
    elif ctx["sak_error"]:
        print("[DIAGNOSIS] Tool could not identify card type.")
        print(">>> ACTION: Trying Force 1K Mode...")
        print("="*60)
        
        code_retry, _ = run_mfoc_process(tool_path, abs_output_file, tools_dir, force_mode="1k")
        if code_retry == 0:
            print("\n[SUCCESS] Keys recovered (Forced 1K)!")
            return

    print(f"\n[FAIL] All attempts failed.")
    if ctx["crack_failed"]:
        print("Tip: The card might be fully hard-locked (no default keys found).")
        print("     Try increasing PROBE_COUNT in the script to 50 or 100.")

if __name__ == "__main__":
    output_file = "cracked_dump.mfd"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    crack_card(output_file)