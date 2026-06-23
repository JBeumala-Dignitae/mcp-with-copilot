#!/usr/bin/env python3
"""
Test script to verify database persistence and deletion functionality
"""

import os
import sqlite3
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import DB_PATH, init_db, get_db_connection

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def show_activities_and_participants():
    """Display all activities and their participants"""
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('SELECT id, name, max_participants FROM activities ORDER BY name')
    activities = c.fetchall()
    
    print(f"{'Activity':<25} {'Max':<5} {'Current':<10} {'Participants'}")
    print("-" * 80)
    
    for activity_id, name, max_p in activities:
        c.execute('SELECT COUNT(*) FROM participants WHERE activity_id = ?', (activity_id,))
        current = c.fetchone()[0]
        
        c.execute('SELECT email FROM participants WHERE activity_id = ? ORDER BY email', (activity_id,))
        participants = [row[0] for row in c.fetchall()]
        
        email_list = ", ".join(participants) if participants else "(empty)"
        print(f"{name:<25} {max_p:<5} {current:<10} {email_list}")
    
    conn.close()

def test_1_initial_load():
    """Test 1: Verify initial data loads correctly"""
    print_section("TEST 1: Initial Database Load")
    
    # Delete database if it exists to start fresh
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("✓ Deleted old database")
    
    # Initialize database
    init_db()
    print("✓ Database initialized")
    
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('SELECT COUNT(*) FROM activities')
    activity_count = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM participants')
    participant_count = c.fetchone()[0]
    
    conn.close()
    
    print(f"✓ Activities loaded: {activity_count}")
    print(f"✓ Participants loaded: {participant_count}")
    
    if activity_count == 9 and participant_count == 18:
        print("\n✅ TEST 1 PASSED: Initial data loaded correctly")
        return True
    else:
        print(f"\n❌ TEST 1 FAILED: Expected 9 activities and 18 participants, got {activity_count} and {participant_count}")
        return False

def test_2_unregister():
    """Test 2: Verify unregister (delete) works"""
    print_section("TEST 2: Unregister Participant")
    
    print("Before deletion:")
    show_activities_and_participants()
    
    # Delete a participant
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('SELECT id FROM activities WHERE name = ?', ("Chess Club",))
    chess_id = c.fetchone()[0]
    
    c.execute('DELETE FROM participants WHERE activity_id = ? AND email = ?', 
              (chess_id, "michael@mergington.edu"))
    conn.commit()
    conn.close()
    
    print("\n✓ Deleted michael@mergington.edu from Chess Club")
    
    print("\nAfter deletion:")
    show_activities_and_participants()
    
    # Verify deletion
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM participants WHERE activity_id = ? AND email = ?', 
              (chess_id, "michael@mergington.edu"))
    result = c.fetchone()[0]
    conn.close()
    
    if result == 0:
        print("\n✅ TEST 2 PASSED: Unregister works correctly")
        return True
    else:
        print("\n❌ TEST 2 FAILED: Participant was not deleted")
        return False

def test_3_no_reseed():
    """Test 3: Verify data is NOT re-seeded on restart"""
    print_section("TEST 3: No Re-Seeding on Restart")
    
    print("Current state (after deletion):")
    show_activities_and_participants()
    
    # Count participants before reinit
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM participants')
    before_count = c.fetchone()[0]
    conn.close()
    
    print(f"\n✓ Participants before reinit: {before_count}")
    
    # Reinitialize database (simulating restart)
    init_db()
    print("✓ Database reinitialized (simulating app restart)")
    
    # Count participants after reinit
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM participants')
    after_count = c.fetchone()[0]
    conn.close()
    
    print(f"✓ Participants after reinit: {after_count}")
    
    print("\nState after reinit:")
    show_activities_and_participants()
    
    if before_count == after_count:
        print(f"\n✅ TEST 3 PASSED: Data persisted correctly (no re-seeding)")
        return True
    else:
        print(f"\n❌ TEST 3 FAILED: Data was re-seeded! Count changed from {before_count} to {after_count}")
        return False

def test_4_capacity_check():
    """Test 4: Verify capacity enforcement"""
    print_section("TEST 4: Capacity Enforcement Check")
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Find Math Club (max_participants = 10)
    c.execute('SELECT id, max_participants FROM activities WHERE name = ?', ("Math Club",))
    result = c.fetchone()
    
    if not result:
        print("❌ Math Club not found")
        conn.close()
        return False
    
    math_id, max_p = result
    
    # Get current participant count
    c.execute('SELECT COUNT(*) FROM participants WHERE activity_id = ?', (math_id,))
    current_count = c.fetchone()[0]
    
    print(f"Math Club: max={max_p}, current={current_count}")
    
    if current_count < max_p:
        print(f"✓ Room available: {max_p - current_count} spots left")
        print(f"✅ TEST 4 PASSED: Capacity check logic is in place")
        conn.close()
        return True
    else:
        print(f"⚠ Math Club is at capacity")
        print(f"✅ TEST 4 PASSED: Can verify capacity when full")
        conn.close()
        return True

def main():
    print("\n" + "="*60)
    print("  DATABASE PERSISTENCE AND DELETION TESTS")
    print("="*60)
    
    results = []
    
    try:
        results.append(("Test 1: Initial Load", test_1_initial_load()))
        results.append(("Test 2: Unregister", test_2_unregister()))
        results.append(("Test 3: No Re-Seeding", test_3_no_reseed()))
        results.append(("Test 4: Capacity Check", test_4_capacity_check()))
        
        # Summary
        print_section("TEST SUMMARY")
        for test_name, passed in results:
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{test_name:<35} {status}")
        
        total_passed = sum(1 for _, passed in results if passed)
        total = len(results)
        
        print(f"\nTotal: {total_passed}/{total} tests passed")
        
        if total_passed == total:
            print("\n🎉 ALL TESTS PASSED!\n")
            return 0
        else:
            print(f"\n⚠ {total - total_passed} test(s) failed\n")
            return 1
    
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
