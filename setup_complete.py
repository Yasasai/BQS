"""
Standard Setup Script for BQS. 
Uses the Self-Heal protocol for maximum reliability.
"""
from self_heal import self_heal

if __name__ == "__main__":
    print("Initializing BQS Setup...")
    self_heal()
