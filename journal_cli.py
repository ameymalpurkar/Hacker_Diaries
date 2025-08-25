from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from datetime import datetime
import os
import json

JOURNAL_FILE = 'journal.txt'
TASK_FILE = 'tasks.txt'
CONFIG_FILE = 'config.json'
console = Console()

# Special code word to activate the CLI
ACTIVATION_CODE = "secret"

# AI Configuration
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def setup_gemini_api():
    try:
        import google.generativeai as genai
    except ImportError:
        console.print(Panel.fit("[red]Google Generative AI library not installed. Run: pip install google-generativeai[/red]", title="Missing Dependency", border_style="red"))
        return False
    
    config = load_config()
    api_key = config.get('gemini_api_key')
    
    if not api_key:
        console.print(Panel("[bold yellow]First time using AI features![/bold yellow]\n[cyan]You need a Gemini API key from Google AI Studio[/cyan]\n[dim]Visit: https://makersuite.google.com/app/apikey[/dim]", title="AI Setup Required", border_style="yellow"))
        api_key = Prompt.ask("[bold cyan]Enter your Gemini API key[/bold cyan]", password=True)
        if not api_key:
            console.print(Panel.fit("[red]API key required for AI features[/red]", border_style="red"))
            return False
        config['gemini_api_key'] = api_key
        save_config(config)
        console.print(Panel.fit("[green]API key saved successfully![/green]", title="Setup Complete", border_style="green"))
    
    try:
        genai.configure(api_key=api_key)
        # Test the API key
        model = genai.GenerativeModel("gemini-pro")
        test_response = model.generate_content("Hello")
        return True
    except Exception as e:
        console.print(Panel.fit(f"[red]Invalid API key or connection error: {str(e)}[/red]", title="API Error", border_style="red"))
        # Remove invalid key
        config.pop('gemini_api_key', None)
        save_config(config)
        return False

def ai_task_analysis():
    if not setup_gemini_api():
        return
    
    import google.generativeai as genai
    
    if not os.path.exists(TASK_FILE):
        console.print(Panel.fit("[red]No tasks found to analyze.[/red]", title="No Tasks", border_style="red"))
        return
    
    with open(TASK_FILE, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.count('|') == 2]
    
    if not lines:
        console.print(Panel.fit("[yellow]No tasks to analyze.[/yellow]", title="Empty", border_style="yellow"))
        return
    
    # Prepare task data for AI
    tasks_text = ""
    for i, line in enumerate(lines, 1):
        priority, task, status = line.split('|', 2)
        tasks_text += f"{i}. [{priority.upper()}] {task} - {status}\n"
    
    prompt = f"""Analyze these tasks and provide insights:

{tasks_text}

Please provide:
1. Task summary and overview
2. Priority recommendations
3. Time management suggestions
4. Productivity insights
5. Next action recommendations

Keep the response concise and actionable."""

    try:
        config = load_config()
        genai.configure(api_key=config['gemini_api_key'])
        model = genai.GenerativeModel("gemini-pro")
        
        console.print(Panel("[bold yellow]🤖 AI is analyzing your tasks...[/bold yellow]", border_style="yellow"))
        
        response = model.generate_content(prompt)
        ai_response = response.text if hasattr(response, 'text') else str(response)
        
        console.print(Panel(f"[bold cyan]🧠 AI Task Analysis:[/bold cyan]\n\n{ai_response}", title="Gemini AI Insights", border_style="cyan"))
        
    except Exception as e:
        console.print(Panel.fit(f"[red]AI analysis failed: {str(e)}[/red]", title="Error", border_style="red"))

def ai_suggest_tasks():
    if not setup_gemini_api():
        return
        
    import google.generativeai as genai
    
    # Get current tasks for context
    current_tasks = ""
    if os.path.exists(TASK_FILE):
        with open(TASK_FILE, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.count('|') == 2]
            for line in lines:
                priority, task, status = line.split('|', 2)
                current_tasks += f"- {task} ({status})\n"
    
    user_goal = Prompt.ask("[bold cyan]What are you trying to accomplish? (e.g., 'prepare for presentation', 'organize workspace')[/bold cyan]")
    
    prompt = f"""Based on this goal: "{user_goal}"

Current tasks:
{current_tasks if current_tasks else "No current tasks"}

Suggest 3-5 specific, actionable tasks that would help achieve this goal. Format each as:
- [Priority: high/medium/low] Task description

Keep tasks realistic and achievable."""

    try:
        config = load_config()
        genai.configure(api_key=config['gemini_api_key'])
        model = genai.GenerativeModel("gemini-pro")
        
        console.print(Panel("[bold yellow]🤖 AI is generating task suggestions...[/bold yellow]", border_style="yellow"))
        
        response = model.generate_content(prompt)
        ai_response = response.text if hasattr(response, 'text') else str(response)
        
        console.print(Panel(f"[bold cyan]💡 AI Task Suggestions:[/bold cyan]\n\n{ai_response}", title="Gemini AI Suggestions", border_style="cyan"))
        
        # Ask if user wants to add these tasks
        if Prompt.ask("[bold green]Would you like to add any of these suggestions as tasks? (y/n)[/bold green]", choices=["y", "n"], default="n") == "y":
            add_ai_suggested_tasks(ai_response)
            
    except Exception as e:
        console.print(Panel.fit(f"[red]AI suggestion failed: {str(e)}[/red]", title="Error", border_style="red"))

def add_ai_suggested_tasks(ai_suggestions):
    console.print(Panel("[bold cyan]Copy and paste the tasks you want to add (one per line, include priority):[/bold cyan]", border_style="cyan"))
    console.print("[dim]Example: high|Complete project proposal[/dim]")
    
    while True:
        task_input = Prompt.ask("[bold green]Enter task (priority|description) or 'done' to finish[/bold green]")
        if task_input.lower() == 'done':
            break
            
        if '|' in task_input:
            try:
                priority, task_desc = task_input.split('|', 1)
                priority = priority.strip().lower()
                task_desc = task_desc.strip()
                
                if priority in ['high', 'medium', 'low']:
                    with open(TASK_FILE, 'a', encoding='utf-8') as f:
                        f.write(f'{priority}|{task_desc}|not done\n')
                    console.print(Panel.fit(f"[green]Added: {task_desc} [{priority}][/green]", border_style="green"))
                else:
                    console.print(Panel.fit("[red]Priority must be high, medium, or low[/red]", border_style="red"))
            except:
                console.print(Panel.fit("[red]Format: priority|task description[/red]", border_style="red"))
        else:
            console.print(Panel.fit("[red]Format: priority|task description[/red]", border_style="red"))

def ai_menu():
    console.print(Panel("[bold magenta]🤖 AI Assistant Menu[/bold magenta]", border_style="magenta"))
    while True:
        choice = Prompt.ask(
            "[bold bright_green]AI Options: analyze, suggest, config, back[/bold bright_green]", 
            choices=["analyze", "suggest", "config", "back"], 
            default="analyze"
        )
        
        if choice == "analyze":
            ai_task_analysis()
        elif choice == "suggest":
            ai_suggest_tasks()
        elif choice == "config":
            config = load_config()
            if config.get('gemini_api_key'):
                if Prompt.ask("[bold yellow]Reset API key? (y/n)[/bold yellow]", choices=["y", "n"], default="n") == "y":
                    config.pop('gemini_api_key', None)
                    save_config(config)
                    console.print(Panel.fit("[green]API key reset. You'll be prompted to enter it again.[/green]", border_style="green"))
            else:
                console.print(Panel.fit("[yellow]No API key configured yet.[/yellow]", border_style="yellow"))
        elif choice == "back":
            break

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
    # Ask if user wants AI assistance
    use_ai = Prompt.ask("[bold magenta]🤖 Use AI assistance for task management? (y/n)[/bold magenta]", choices=["y", "n"], default="n")
    
    if use_ai == "y":
        ai_menu()
        return
    
    # Manual task management
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
            command = Prompt.ask("[bold bright_green]Enter command (add, show, delete, task, ai, exit, 404 to quit)[/bold bright_green]", default="show").lower()
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
        elif command == "ai":
            ai_menu()
        else:
            console.print(Panel(f"[red]Unknown command: {command}[/red]", border_style="red"))

if __name__ == '__main__':
    main()
