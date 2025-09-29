#!/usr/bin/env python3
"""
Cleanup script voor oude manuscript outputs
"""
import os
from pathlib import Path
from datetime import datetime, timedelta

def cleanup_old_outputs(days_old=7):
    """Verwijder outputs ouder dan x dagen"""
    output_dir = Path("outputs")
    
    if not output_dir.exists():
        print("Geen outputs folder gevonden")
        return
    
    cutoff_date = datetime.now() - timedelta(days=days_old)
    
    cleaned = 0
    for file in output_dir.rglob("*"):
        if file.is_file():
            # Check file modification time
            mod_time = datetime.fromtimestamp(file.stat().st_mtime)
            if mod_time < cutoff_date:
                print(f"Verwijdering: {file}")
                file.unlink()
                cleaned += 1
    
    print(f"✅ {cleaned} oude bestanden opgeruimd")

if __name__ == "__main__":
    cleanup_old_outputs(7)  # Verwijder bestanden ouder dan 7 dagen