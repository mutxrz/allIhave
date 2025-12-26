import zlib
import re

with open('chrom/anjay.py', 'r') as f:
    content = f.read()

# Find the hex string using a regular expression
match = re.search(r"fromhex('(.+)')", content)
if match:
    hex_string = match.group(1)
    # The hex string is truncated in the read_file output,
    # so we need to get the full string from the file content.
    # The truncated part is "... [truncated]".
    # We will find the start of the hex string and then take everything until the closing parenthesis.
    start_index = content.find("fromhex('") + len("fromhex('")
    end_index = content.rfind("')")
    full_hex_string = content[start_index:end_index]
    
    try:
        # The hex string is split into multiple lines, so we need to join them
        full_hex_string = full_hex_string.replace("'b'", "").replace("'", "")
        
        # Now, we need to extract the correct hex string. It is the long one in the `exec` call.
        # Let's find the `exec` call.
        exec_call_start = content.find("lllllllllIIllIIlI(llllllllllllllI(lllllllllllllll(lllllllllllllIl.fromhex('7a6c6962').decode()), lllllllllllllIl.fromhex('6465636f6d7072657373').decode())(lllllllllllllIl.fromhex(' ")
        if exec_call_start != -1:
            start_offset = exec_call_start + len("lllllllllIIllIIlI(llllllllllllllI(lllllllllllllll(lllllllllllllIl.fromhex('7a6c6962').decode()), lllllllllllllIl.fromhex('6465636f6d7072657373').decode())(lllllllllllllIl.fromhex(' ")
            end_offset = content.rfind("')))")
            
            # The long hex string is between start_offset and end_offset
            long_hex_string = content[start_offset:end_offset]
            
            # The string might contain newlines, so we remove them
            long_hex_string = long_hex_string.replace("\n", "").replace("'", "").replace("+", "").replace(" ", "")
            
            # Now we can decode and decompress
            decoded_bytes = bytes.fromhex(long_hex_string)
            decompressed_code = zlib.decompress(decoded_bytes)
            
            print(decompressed_code.decode('utf-8'))

    except Exception as e:
        print(f"An error occurred: {e}")

else:
    print("Could not find the hex string to decompress.")
