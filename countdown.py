#!/usr/bin/env python3
"""
Countdown Timer Script

A beautiful countdown timer for productivity sessions, task deadlines, or general timing needs.
Can be used standalone or integrated with the task manager CLI.

Usage:
    python countdown.py 25          # 25 minutes
    python countdown.py 1:30        # 1 hour 30 minutes  
    python countdown.py 00:05:30    # 5 minutes 30 seconds
"""

import time
import sys
import argparse
from datetime import datetime, timedelta
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

console = Console()


def parse_time_input(time_str):
    """Parse various time input formats into seconds."""
    try:
        # Handle different formats
        if ':' in time_str:
            parts = time_str.split(':')
            if len(parts) == 2:  # MM:SS or HH:MM
                if int(parts[0]) > 59:  # Likely HH:MM
                    hours, minutes = map(int, parts)
                    return hours * 3600 + minutes * 60
                else:  # MM:SS
                    minutes, seconds = map(int, parts)
                    return minutes * 60 + seconds
            elif len(parts) == 3:  # HH:MM:SS
                hours, minutes, seconds = map(int, parts)
                return hours * 3600 + minutes * 60 + seconds
        else:
            # Just minutes
            minutes = int(time_str)
            return minutes * 60
    except ValueError:
        raise ValueError(f"Invalid time format: {time_str}")


def format_time(seconds):
    """Format seconds into HH:MM:SS format."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def create_countdown_display(remaining_seconds, total_seconds, message=""):
    """Create a beautiful countdown display using Rich."""
    # Calculate progress
    progress_percent = ((total_seconds - remaining_seconds) / total_seconds) * 100
    
    # Format time
    time_display = format_time(remaining_seconds)
    
    # Create main time display
    time_text = Text(time_display, style="bold cyan", justify="center")
    time_text.stylize("bold red" if remaining_seconds <= 10 else "bold cyan")
    
    # Create progress bar
    bar_width = 40
    filled = int((progress_percent / 100) * bar_width)
    empty = bar_width - filled
    progress_bar = "█" * filled + "░" * empty
    
    # Status message
    if remaining_seconds <= 10:
        status = "⚠️  ALMOST DONE!"
        status_style = "bold red blink"
    elif remaining_seconds <= 60:
        status = "🔔 Final minute"
        status_style = "bold yellow"
    else:
        status = "⏰ Timer running"
        status_style = "bold green"
    
    # Build the display
    lines = [
        "",
        Text(status, style=status_style, justify="center"),
        "",
        time_text,
        "",
        Text(f"[{progress_bar}] {progress_percent:.1f}%", justify="center"),
        "",
    ]
    
    if message:
        lines.extend([
            Text(message, style="dim", justify="center"),
            "",
        ])
    
    # Add completion percentage
    lines.append(Text(f"Elapsed: {format_time(total_seconds - remaining_seconds)}", 
                     style="dim", justify="center"))
    
    content = Text("\n").join(lines)
    
    # Choose panel style based on time remaining
    if remaining_seconds <= 10:
        panel_style = "bold red"
        title = "⚠️  COUNTDOWN TIMER ⚠️"
    elif remaining_seconds <= 60:
        panel_style = "bold yellow"
        title = "🔔 COUNTDOWN TIMER"
    else:
        panel_style = "bold cyan"
        title = "⏰ COUNTDOWN TIMER"
    
    return Panel(
        Align.center(content),
        title=title,
        border_style=panel_style,
        padding=(1, 2)
    )


def play_notification():
    """Play a simple notification sound (cross-platform)."""
    try:
        # Try different methods for different platforms
        import subprocess
        import platform
        
        system = platform.system().lower()
        if system == "darwin":  # macOS
            subprocess.run(["afplay", "/System/Library/Sounds/Glass.aiff"], 
                         capture_output=True)
        elif system == "linux":
            # Try different Linux sound methods
            for cmd in [["paplay", "/usr/share/sounds/alsa/Front_Left.wav"],
                       ["aplay", "/usr/share/sounds/alsa/Front_Left.wav"],
                       ["speaker-test", "-t", "sine", "-f", "1000", "-l", "1"]]:
                try:
                    subprocess.run(cmd, capture_output=True, timeout=2)
                    break
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue
        elif system == "windows":
            import winsound
            winsound.Beep(1000, 500)  # frequency, duration
    except:
        # Fallback: print bell character
        print("\a" * 3, end="", flush=True)


def countdown_timer(total_seconds, message=""):
    """Run the countdown timer with live display."""
    try:
        with Live(create_countdown_display(total_seconds, total_seconds, message), 
                  refresh_per_second=1, screen=True) as live:
            
            for remaining in range(total_seconds, -1, -1):
                live.update(create_countdown_display(remaining, total_seconds, message))
                
                if remaining == 0:
                    break
                    
                time.sleep(1)
        
        # Timer finished
        console.clear()
        
        # Final notification
        final_panel = Panel(
            Align.center(Text("🎉 TIME'S UP! 🎉\n\nCountdown completed!", 
                            style="bold green", justify="center")),
            title="✅ TIMER FINISHED",
            border_style="bold green",
            padding=(2, 4)
        )
        
        console.print(final_panel)
        
        # Play notification sound
        play_notification()
        
        # Show completion message
        if message:
            console.print(f"\n[bold cyan]Session:[/bold cyan] {message}")
        
        console.print(f"[dim]Completed at: {datetime.now().strftime('%H:%M:%S')}[/dim]")
        
    except KeyboardInterrupt:
        console.clear()
        console.print("\n[bold yellow]⏸️  Timer stopped by user[/bold yellow]")
        sys.exit(0)


def main():
    """Main function for standalone usage."""
    parser = argparse.ArgumentParser(
        description="Beautiful countdown timer for productivity and task management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  countdown.py 25              # 25 minutes
  countdown.py 1:30            # 1 hour 30 minutes
  countdown.py 00:05:30        # 5 minutes 30 seconds
  countdown.py 45 -m "Work session"  # 45 minutes with message
        """
    )
    
    parser.add_argument("time", help="Time duration (minutes, MM:SS, or HH:MM:SS)")
    parser.add_argument("-m", "--message", default="", help="Optional message for the timer")
    parser.add_argument("--test", action="store_true", help="Run a 5-second test timer")
    
    args = parser.parse_args()
    
    try:
        if args.test:
            total_seconds = 5
            message = "Test timer"
        else:
            total_seconds = parse_time_input(args.time)
            message = args.message
        
        if total_seconds <= 0:
            console.print("[bold red]Error:[/bold red] Time must be greater than 0")
            sys.exit(1)
        
        # Show initial info
        console.print(f"[bold green]Starting countdown:[/bold green] {format_time(total_seconds)}")
        if message:
            console.print(f"[bold cyan]Session:[/bold cyan] {message}")
        console.print("[dim]Press Ctrl+C to stop[/dim]\n")
        
        time.sleep(1)  # Brief pause before starting
        
        countdown_timer(total_seconds, message)
        
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()