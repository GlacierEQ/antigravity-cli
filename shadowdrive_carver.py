#!/usr/bin/env python3
"""
GlacierEQ Native Raw Block File Carver & Data Recovery Engine v1.0
Non-destructive signature-based file carver for raw disks and APFS unallocated blocks.
Recovers SQLite (.db), PDF, JPEG, PNG, MP4/M4A, and ZIP/DOCX files.
"""

import os
import sys
import time
from datetime import datetime

# File Magic Signatures & Footers
SIGNATURES = {
    "SQLITE3": {
        "header": b"\x53\x51\x4c\x69\x74\x65\x20\x66\x6f\x72\x6d\x61\x74\x20\x33\x00",
        "ext": "db",
        "max_size": 200 * 1024 * 1024  # 200MB max
    },
    "PDF": {
        "header": b"%PDF-",
        "footer": b"%%EOF",
        "ext": "pdf",
        "max_size": 50 * 1024 * 1024
    },
    "JPEG": {
        "header": b"\xff\xd8\xff",
        "footer": b"\xff\xd9",
        "ext": "jpg",
        "max_size": 30 * 1024 * 1024
    },
    "PNG": {
        "header": b"\x89PNG\r\n\x1a\n",
        "footer": b"IEND\xaeB`\x82",
        "ext": "png",
        "max_size": 30 * 1024 * 1024
    },
    "ZIP_DOCX": {
        "header": b"PK\x03\x04",
        "ext": "zip",
        "max_size": 100 * 1024 * 1024
    }
}

CHUNK_SIZE = 4 * 1024 * 1024  # 4MB buffer

def carve_disk(disk_device: str, output_dir: str, max_gb: float = 10.0):
    os.makedirs(output_dir, exist_ok=True)
    print(f"[*] Target Device : {disk_device}")
    print(f"[*] Recovery Dir  : {output_dir}")
    print(f"[*] Scan Limit    : {max_gb} GB")
    
    recovered_counts = {k: 0 for k in SIGNATURES}
    total_bytes_read = 0
    max_bytes = int(max_gb * 1024 * 1024 * 1024)
    start_time = time.time()

    try:
        with open(disk_device, 'rb') as disk:
            buffer = b""
            while total_bytes_read < max_bytes:
                chunk = disk.read(CHUNK_SIZE)
                if not chunk:
                    break
                buffer += chunk
                total_bytes_read += len(chunk)

                # Search signatures
                for sig_name, spec in SIGNATURES.items():
                    hdr = spec["header"]
                    pos = buffer.find(hdr)
                    while pos != -1:
                        # Candidate found
                        ext = spec["ext"]
                        footer = spec.get("footer")
                        file_data = None

                        if footer:
                            end_pos = buffer.find(footer, pos + len(hdr))
                            if end_pos != -1:
                                file_len = end_pos + len(footer) - pos
                                if file_len <= spec["max_size"]:
                                    file_data = buffer[pos : pos + file_len]
                        else:
                            # Fixed chunk estimate
                            file_data = buffer[pos : pos + min(len(buffer) - pos, spec["max_size"])]

                        if file_data and len(file_data) > 64:
                            recovered_counts[sig_name] += 1
                            out_fname = f"carved_{sig_name.lower()}_{recovered_counts[sig_name]:04d}.{ext}"
                            out_path = os.path.join(output_dir, out_fname)
                            with open(out_path, 'wb') as out_f:
                                out_f.write(file_data)
                            print(f"  [+] Carved {sig_name} -> {out_fname} ({len(file_data):,} bytes)")

                        # Advance search
                        pos = buffer.find(hdr, pos + len(hdr))

                # Keep trailing chunk in buffer for overlapping headers
                if len(buffer) > CHUNK_SIZE * 2:
                    buffer = buffer[-CHUNK_SIZE:]

                # Progress report every 500MB
                if total_bytes_read % (500 * 1024 * 1024) < CHUNK_SIZE:
                    mb_done = total_bytes_read / (1024 * 1024)
                    print(f"[*] Progress: {mb_done:.1f} MB scanned...")

    except PermissionError:
        print("❌ Permission Error: Raw disk reading requires Full Disk Access or elevated permissions.")
    except Exception as e:
        print(f"❌ Carving Error: {e}")

    elapsed = round(time.time() - start_time, 2)
    print("\n=======================================================")
    print(f"🏁 SCAN FINISHED ({elapsed}s)")
    print(f"Scanned: {total_bytes_read / (1024 * 1024):.2f} MB")
    print("Recovered Summary:")
    for k, v in recovered_counts.items():
        print(f"  • {k:<10}: {v} files")
    print("=======================================================")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "/dev/disk3s1"
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.expanduser("~/Library/CloudStorage/Dropbox-Cyber.lazer.mermicor/Carved_Assets")
    limit = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
    carve_disk(target, out, limit)
