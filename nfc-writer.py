import subprocess
import os
import sys
import time

def write_dump_to_card(dump_file):
    # --- CONFIGURATION ---
    # We define the folder name where the binaries live
    BINARY_FOLDER = "libnfc"
    TOOL_NAME = "nfc-mfclassic.exe"
    
    # Get the absolute path to the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the full path to the tools folder and the executable
    tools_dir = os.path.join(script_dir, BINARY_FOLDER)
    tool_path = os.path.join(tools_dir, TOOL_NAME)
    
    # Resolve the dump file path relative to the script (root)
    abs_dump_file = os.path.abspath(dump_file)

    # Check if the tool exists before trying to run it
    if not os.path.exists(tool_path):
        print(f"Error: Could not find {TOOL_NAME}.")
        print(f"Expected location: {tool_path}")
        print("Please create a folder named 'libnfc' next to this script and place your binaries, DLLs, and config there.")
        return

    print(f"--- Starting Write Process ---")
    print(f"Tool Path: {tool_path}")
    print(f"Dump File: {abs_dump_file}")
    print("Please place your Gen 1 (Magic) card on the reader...")
    
    while True:
        try:
            # FIX APPLIED HERE:
            # Added "u" argument to the list.
            # Order: Action (W), Key (a), UID Mode (u), Filename
            result = subprocess.run(
                [tool_path, "W", "a", "u", abs_dump_file], 
                cwd=tools_dir,
                capture_output=True, 
                text=True
            )
            
            output = result.stdout
            error = result.stderr

            # Analyze output
            if "No NFC device found" in output or "No NFC device found" in error:
                print("Reader not found. Check USB connection.")
                break
            
            # "No tag found" is standard waiting behavior
            if "No tag found" in output:
                sys.stdout.write(".")
                sys.stdout.flush()
                time.sleep(1)
                continue
            
            # If we get here, the tool attempted something
            print("\n\nCard detected! Log output:")
            print("-" * 40)
            print(output)
            if error and len(error.strip()) > 0:
                print("STDERR:", error)
            print("-" * 40)

            # Success check
            if "Done" in output:
                print("\n[SUCCESS] Write operation completed.")
                if "Writing to block 0" in output:
                    print("[INFO] Block 0 (UID) was overwritten successfully.")
            else:
                print("\n[FAIL] Write incomplete or failed.")
            
            break

        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            # Helpful debugging info
            if "WinError 2" in str(e):
                print("Debug Tip: This usually means the path to the executable is wrong.")
                print(f"Python tried to run: {tool_path}")
            break

if __name__ == "__main__":
    target_file = "my_dump.mfd" 
    
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
        
    if not os.path.exists(target_file):
        print(f"Error: Dump file '{target_file}' not found in the script directory.")
    else:
        write_dump_to_card(target_file)