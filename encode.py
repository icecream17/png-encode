# encode.py
# Converts data in input_file into a valid PNG
#
# The data is stored in the ancillary chunk "dAtA" which PNG ignores.
# Then a cover.png file is used so that the image is valid.
# The filename is lost.
#
# Usage: python encode.py input_file.bin cover.png output.png

import sys
import struct

def crc32(data):
    import zlib
    return zlib.crc32(data) & 0xffffffff

def read_chunks(png):
    pos = 8  # skip PNG signature
    while pos < len(png):
        length = struct.unpack(">I", png[pos:pos+4])[0]
        ctype = png[pos+4:pos+8]
        data  = png[pos+8:pos+8+length]
        crc   = png[pos+8+length:pos+12+length]
        yield (ctype, data, length, crc)
        pos += 12 + length

def encode(input_file, cover_png_file, output_png_file):
    payload = open(input_file, "rb").read()
    cover   = open(cover_png_file, "rb").read()

    if cover[:8] != b"\x89PNG\r\n\x1a\n":
        raise Exception("Cover file is not a valid PNG")

    output = bytearray()
    output += cover[:8]  # PNG signature

    # Copy all existing chunks up to (but NOT including) IEND
    chunks = list(read_chunks(cover))
    for ctype, data, length, crc in chunks:
        if ctype == b"IEND":
            break
        output += struct.pack(">I", length)
        output += ctype
        output += data
        output += crc

    # Insert our custom chunk
    chunk_type = b"dAtA"
    chunk_data = payload
    output += struct.pack(">I", len(chunk_data))
    output += chunk_type
    output += chunk_data
    output += struct.pack(">I", crc32(chunk_type + chunk_data))

    # Add the original IEND chunk
    output += b"\x00\x00\x00\x00IEND\xae\x42\x60\x82"

    open(output_png_file, "wb").write(output)
    print(f"OK: data embedded in {output_png_file}")

if __name__ == "__main__":
    encode(sys.argv[1], sys.argv[2], sys.argv[3])
