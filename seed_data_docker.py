#!/usr/bin/env python3
"""Quick seeding script to run inside Docker"""
import sys
import os

# Add backend to path
sys.path.insert(0, '/app')

# Now run the actual seed script
exec(open('/app/scripts/database/seed_large_dataset.py').read())
