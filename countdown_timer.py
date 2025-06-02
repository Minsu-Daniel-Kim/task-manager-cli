#!/usr/bin/env python3
"""
Countdown Timer Script

A simple countdown timer that counts down from a user-specified number,
displays the countdown in real-time with colored formatting, and shows
a completion message when it reaches zero.
"""

import time
import sys


def clear_line():
    """Clear the current line in the terminal."""
    print('\r' + ' ' * 50 + '\r', end='', flush=True)


def print_colored(text, color_code):
    """Print text with specified ANSI color code."""
    print(f"\033[{color_code}m{text}\033[0m", end='', flush=True)


def countdown_timer(seconds):
    """
    Count down from the specified number of seconds.
    
    Args:
        seconds (int): The number of seconds to count down from
    """
    try:
        while seconds >= 0:
            clear_line()
            
            if seconds > 10:
                # Green for numbers > 10
                print_colored(f"⏰ Countdown: {seconds:02d} seconds", "32")
            elif seconds > 5:
                # Yellow for numbers 6-10
                print_colored(f"⏰ Countdown: {seconds:02d} seconds", "33")
            elif seconds > 0:
                # Red for numbers 1-5
                print_colored(f"⏰ Countdown: {seconds:02d} seconds", "31")
            else:
                # Bright green for completion
                clear_line()
                print_colored("🎉 TIME'S UP! 🎉", "92")
                print()
                break
            
            time.sleep(1)
            seconds -= 1
            
    except KeyboardInterrupt:
        clear_line()
        print_colored("\n⚠️ Countdown cancelled by user", "31")
        print()
        sys.exit(0)


def get_user_input():
    """Get countdown duration from user input."""
    while True:
        try:
            user_input = input("Enter countdown time in seconds: ")
            seconds = int(user_input)
            
            if seconds < 0:
                print("❌ Please enter a positive number.")
                continue
            elif seconds > 3600:  # 1 hour limit
                print("❌ Please enter a number less than 3600 (1 hour).")
                continue
            
            return seconds
            
        except ValueError:
            print("❌ Please enter a valid number.")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            sys.exit(0)


def main():
    """Main function to run the countdown timer."""
    print("🕐 Countdown Timer")
    print("==================")
    print()
    
    seconds = get_user_input()
    
    if seconds == 0:
        print_colored("🎉 Already at zero! 🎉", "92")
        print()
        return
    
    print(f"\nStarting countdown from {seconds} seconds...")
    print("Press Ctrl+C to cancel\n")
    
    countdown_timer(seconds)


if __name__ == "__main__":
    main()