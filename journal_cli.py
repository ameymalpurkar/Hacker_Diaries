from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from datetime import datetime
import os

JOURNAL_FILE = 'journal.txt'
TASK_FILE = 'tasks.txt'
console = Console()

# Special code word to activate the CLI
ACTIVATION_CODE = "secret"

def add_entry():
    entries_input = Prompt.ask("[bold cyan]Enter your journal entries (comma separated for multiple)[/bold cyan]")
    entries = [e.strip() for e in entries_input.split(',') if e.strip()]
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    with open(JOURNAL_FILE, 'a', encoding='utf-8') as f:
        for entry_text in entries:
            f.write(f'{timestamp}|{entry_text}\n')
    console.print(Panel.fit(f"[green]{len(entries)} Entry(ies) added![/green]", title="Success", border_style="green"))

def show_entries():
    if not os.path.exists(JOURNAL_FILE):
        console.print(Panel.fit("[red]No journal entries found.[/red]", title="Oops!", border_style="red"))
        return
    table = Table(title="Your Journal Entries", show_lines=True, header_style="bold magenta")
    table.add_column("Date", style="cyan", width=18)
    table.add_column("Entry", style="white")
    with open(JOURNAL_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        if not lines:
            console.print(Panel.fit("[yellow]No journal entries yet.[/yellow]", title="Empty", border_style="yellow"))
            return
        for line in lines:
            if '|' in line:
                date, entry = line.strip().split('|', 1)
                table.add_row(date, entry)
    console.print(table)

def delete_entry():
    if not os.path.exists(JOURNAL_FILE):
        console.print(Panel.fit("[red]No journal entries found.[/red]", title="Oops!", border_style="red"))
        return
    with open(JOURNAL_FILE, 'r', encoding='utf-8') as f:
        lines = [line for line in f if '|' in line]
    if not lines:
        console.print(Panel.fit("[yellow]No journal entries yet.[/yellow]", title="Empty", border_style="yellow"))
        return
    table = Table(title="[bold green]Select Entry(ies) to Delete[/bold green]", show_lines=True, header_style="bold green", style="bold bright_green")
    table.add_column("No.", style="bold bright_green", width=5)
    table.add_column("Date", style="bold bright_green", width=18)
    table.add_column("Entry", style="bold bright_green")
    for idx, line in enumerate(lines, 1):
        date, entry = line.strip().split('|', 1)
        table.add_row(str(idx), date, entry)
    console.print(table)
    choices = Prompt.ask("[bold bright_green]Enter entry numbers to delete (comma separated)[/bold bright_green]", default="1")
    try:
        indices = sorted(set(int(i.strip()) for i in choices.split(',') if i.strip()), reverse=True)
        for idx in indices:
            if 1 <= idx <= len(lines):
                del lines[idx - 1]
        with open(JOURNAL_FILE, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        console.print(Panel.fit(f"[green]Deleted entries: {', '.join(map(str, indices))}![/green]", title="Deleted", border_style="green"))
    except ValueError:
        console.print(Panel.fit("[red]Invalid input.[/red]", title="Error", border_style="red"))

def add_task():
    tasks_input = Prompt.ask("[bold cyan]Enter your tasks (comma separated for multiple)[/bold cyan]")
    priority = Prompt.ask("[bold yellow]Priority (high/medium/low)[/bold yellow]", choices=["high", "medium", "low"], default="medium")
    tasks = [t.strip() for t in tasks_input.split(',') if t.strip()]
    with open(TASK_FILE, 'a', encoding='utf-8') as f:
        for task in tasks:
            f.write(f'{priority}|{task}|not done\n')
    console.print(Panel.fit(f"[green]{len(tasks)} Task(s) added with {priority} priority![/green]", title="Task Added", border_style="green"))

def show_tasks():
    if not os.path.exists(TASK_FILE):
        console.print(Panel.fit("[red]No tasks found.[/red]", title="Oops!", border_style="red"))
        return
    table = Table(title="[bold bright_green]Your Tasks[/bold bright_green]", show_lines=True, header_style="bold bright_green")
    table.add_column("No.", style="bold bright_green", width=5)
    table.add_column("Priority", style="bold yellow", width=10)
    table.add_column("Task", style="white")
    table.add_column("Status", style="bold cyan", width=10)
    with open(TASK_FILE, 'r', encoding='utf-8') as f:
        lines = [line for line in f if line.count('|') == 2]
    if not lines:
        console.print(Panel.fit("[yellow]No tasks yet.[/yellow]", title="Empty", border_style="yellow"))
        return
    for idx, line in enumerate(lines, 1):
        try:
            priority, task, status = line.strip().split('|', 2)
        except ValueError:
            continue  # skip malformed lines
        table.add_row(str(idx), priority, task, status)
    console.print(table)

def delete_task():
    if not os.path.exists(TASK_FILE):
        console.print(Panel.fit("[red]No tasks found.[/red]", title="Oops!", border_style="red"))
        return
    show_tasks()
    with open(TASK_FILE, 'r', encoding='utf-8') as f:
        lines = [line for line in f if line.count('|') == 2]
    choices = Prompt.ask("[bold bright_green]Enter task numbers to delete (comma separated)[/bold bright_green]", default="1")
    try:
        indices = sorted(set(int(i.strip()) for i in choices.split(',') if i.strip()), reverse=True)
        for idx in indices:
            if 1 <= idx <= len(lines):
                del lines[idx - 1]
        with open(TASK_FILE, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        console.print(Panel.fit(f"[green]Deleted tasks: {', '.join(map(str, indices))}![/green]", title="Deleted", border_style="green"))
    except ValueError:
        console.print(Panel.fit("[red]Invalid input.[/red]", title="Error", border_style="red"))

def mark_task_done():
    if not os.path.exists(TASK_FILE):
        console.print(Panel.fit("[red]No tasks found.[/red]", title="Oops!", border_style="red"))
        return
    with open(TASK_FILE, 'r', encoding='utf-8') as f:
        lines = [line for line in f if line.count('|') == 2]
    not_done_lines = [line for line in lines if line.strip().endswith('|not done')]
    if not not_done_lines:
        console.print(Panel.fit("[yellow]No incomplete tasks to mark as done.[/yellow]", title="All Done", border_style="yellow"))
        return
    table = Table(title="[bold bright_green]Mark Task(s) as Done[/bold bright_green]", show_lines=True, header_style="bold bright_green")
    table.add_column("No.", style="bold bright_green", width=5)
    table.add_column("Priority", style="bold yellow", width=10)
    table.add_column("Task", style="white")
    for idx, line in enumerate(not_done_lines, 1):
        priority, task, status = line.strip().split('|', 2)
        table.add_row(str(idx), priority, task)
    console.print(table)
    choices = Prompt.ask("[bold bright_green]Enter task numbers to mark as done (comma separated)[/bold bright_green]", default="1")
    try:
        indices = sorted(set(int(i.strip()) for i in choices.split(',') if i.strip()), reverse=True)
        for idx in indices:
            if 1 <= idx <= len(not_done_lines):
                full_idx = lines.index(not_done_lines[idx - 1])
                priority, task, _ = lines[full_idx].strip().split('|', 2)
                lines[full_idx] = f'{priority}|{task}|done\n'
        with open(TASK_FILE, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        console.print(Panel.fit(f"[green]Marked as done: {', '.join(map(str, indices))}![/green]", title="Done", border_style="green"))
    except ValueError:
        console.print(Panel.fit("[red]Invalid input.[/red]", title="Error", border_style="red"))

def prioritise_task():
    if not os.path.exists(TASK_FILE):
        console.print(Panel.fit("[red]No tasks found.[/red]", title="Oops!", border_style="red"))
        return
    show_tasks()
    with open(TASK_FILE, 'r', encoding='utf-8') as f:
        lines = [line for line in f if line.count('|') == 2]
    choices = Prompt.ask("[bold bright_green]Enter task numbers to prioritise (comma separated)[/bold bright_green]", default="1")
    try:
        indices = sorted(set(int(i.strip()) for i in choices.split(',') if i.strip()))
        for idx in indices:
            if 1 <= idx <= len(lines):
                _, task, status = lines[idx - 1].strip().split('|', 2)
                new_priority = Prompt.ask("[bold yellow]New Priority (high/medium/low)[/bold yellow]", choices=["high", "medium", "low"], default="medium")
                lines[idx - 1] = f'{new_priority}|{task}|{status}\n'
        with open(TASK_FILE, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        console.print(Panel.fit(f"[green]Prioritised tasks: {', '.join(map(str, indices))}![/green]", title="Prioritised", border_style="green"))
    except ValueError:
        console.print(Panel.fit("[red]Invalid input.[/red]", title="Error", border_style="red"))

def task_manager():
    while True:
        action = Prompt.ask("[bold bright_green]Task Manager: add, show, delete, prioritise, done, back[/bold bright_green]", choices=["add", "show", "delete", "prioritise", "done", "back"], default="show")
        if action == "add":
            add_task()
        elif action == "show":
            show_tasks()
        elif action == "delete":
            delete_task()
        elif action == "prioritise":
            prioritise_task()
        elif action == "done":
            mark_task_done()
        elif action == "back":
            break

def main():
    import sys
    hacker_banner = """
[bold bright_green]██╗  ██╗ █████╗  ██████╗██╗  ██╗███████╗██████╗     ██████╗  █████╗ ██╗██████╗ ██╗███████╗
██║  ██║██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗    ██╔══██╗██╔══██╗██║██╔══██╗██║██╔════╝
███████║███████║██║     █████╔╝ █████╗  ██████╔╝    ██████╔╝███████║██║██║  ██║██║███████╗
██╔══██║██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗    ██╔═══╝ ██╔══██║██║██║  ██║██║╚════██║
██║  ██║██║  ██║╚██████╗██║  ██╗███████╗██║  ██║    ██║     ██║  ██║██║██████╔╝██║███████║
╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝    ╚═╝     ╚═╝  ╚═╝╚═╝╚═════╝ ╚═╝╚══════╝
[/bold bright_green]
"""
    if len(sys.argv) < 2 or sys.argv[1] != ACTIVATION_CODE:
        return
    console.print(Panel("[bold bright_green]HACKER DIARIES[/bold bright_green]", border_style="bright_green"))
    console.print(hacker_banner)
    while True:
        if len(sys.argv) >= 3:
            # If command is provided in the initial call, use it first
            command = sys.argv[2].lower()
            sys.argv = sys.argv[:2]  # Remove the command so it doesn't repeat
        else:
            command = Prompt.ask("[bold bright_green]Enter command (add, show, delete, exit, 404 to quit)[/bold bright_green]", default="show").lower()
        if command == "add":
            add_entry()
        elif command == "show":
            show_entries()
        elif command == "delete":
            delete_entry()
        elif command == "exit":
            console.print("[bold bright_green]Goodbye, hacker![/bold bright_green]")
        elif command == "404":
            console.print("[bold red]Session terminated. 404 Not Found.[/bold red]")
            break
        elif command == "task":
            task_manager()
        else:
            console.print(Panel(f"[red]Unknown command: {command}[/red]", border_style="red"))

if __name__ == '__main__':
    main()
