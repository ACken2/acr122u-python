from smartcard.System import readers

def attempt_cuid_write():
    r = readers()
    if not r:
        print("No reader found.")
        return

    reader = r[0]
    conn = reader.createConnection()
    conn.connect()
    
    print(f"Connected to: {reader}")
    
    # 1. Load Authentication Keys (Default FFFFFFFFFFFF)
    # This command loads the key into the reader's volatile memory
    load_key = [0xFF, 0x82, 0x00, 0x00, 0x06, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
    conn.transmit(load_key)
    
    # 2. Authenticate Block 0 with Key A
    auth_block = [0xFF, 0x86, 0x00, 0x00, 0x05, 0x01, 0x00, 0x00, 0x60, 0x00]
    _, sw1, sw2 = conn.transmit(auth_block)
    
    if sw1 == 0x90:
        print("Authentication successful.")
    else:
        print("Authentication failed. Card might use non-default keys.")
        return

    # 3. Try to write dummy data to Block 0 (SAFE TEST)
    # We will just write the UID 11 22 33 44 (plus standard header)
    # WARNING: This changes the UID to 11 22 33 44. You can change it back later.
    # Data: UID(4) + BCC(1) + SAK(1) + ATQA(2) + Manufacturer Data(8)
    new_data = [0x11, 0x22, 0x33, 0x44, 0x44, 0x08, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    
    write_cmd = [0xFF, 0xD6, 0x00, 0x00, 0x10] + new_data
    response, sw1, sw2 = conn.transmit(write_cmd)

    if sw1 == 0x90:
        print("SUCCESS! This is a Gen 2 (CUID) card.")
        print("You can now write your dump using standard Python scripts.")
    else:
        print("WRITE FAILED (Error: %02X %02X)" % (sw1, sw2))
        print("This is likely a Gen 1 (UID) card. You need the 'Magic' commands.")

attempt_cuid_write()