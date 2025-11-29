# decode.py
# Usage: python decode.py cover.png output_file.bin
#     cover.png should be the same image used with encode.py

import sys
import struct

def read_chunks(png):
    pos = 8  # skip PNG signature
    while pos < len(png):
        length = struct.unpack(">I", png[pos:pos+4])[0]
        ctype = png[pos+4:pos+8]
        data  = png[pos+8:pos+8+length]
        yield (ctype, data)
        pos += 12 + length

def decode(stego_png_file, output_file):
    png = open(stego_png_file, "rb").read()

    for ctype, data in read_chunks(png):
        if ctype == b"dAtA":
            open(output_file, "wb").write(data)
            print(f"OK: extracted to {output_file}")
            return

    print("No dAtA chunk found!")

if __name__ == "__main__":
    decode(sys.argv[1], sys.argv[2])
