from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from datetime import datetime
import os
import json
import requests

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

def setup_ai_api():
    config = load_config()
    provider = config.get('api_provider', 'gemini')
    
    if provider == 'gemini':
        try:
            import google.generativeai as genai
        except ImportError:
            console.print(Panel.fit("[red]Google Generative AI library not installed. Run: pip install google-generativeai[/red]", title="Missing Dependency", border_style="red"))
            return False
        
        api_key = os.getenv('GEMINI_API_KEY') or config.get('gemini_api_key')
        
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
            model = genai.GenerativeModel("gemini-3.5-flash")
            test_response = model.generate_content("Hello")
            return True
        except Exception as e:
            console.print(Panel.fit(f"[red]Connection error or invalid API key: {str(e)}[/red]", title="API Error", border_style="red"))
            return False
            
    elif provider == 'openrouter':
        api_key = os.getenv('OPENROUTER_API_KEY') or config.get('openrouter_api_key')
        model_name = config.get('openrouter_model', 'anthropic/claude-sonnet-4')
        
        if not api_key:
            console.print(Panel("[bold yellow]First time using OpenRouter AI features![/bold yellow]\n[cyan]You need an OpenRouter API key[/cyan]\n[dim]Visit: https://openrouter.ai/keys[/dim]", title="OpenRouter Setup Required", border_style="yellow"))
            api_key = Prompt.ask("[bold cyan]Enter your OpenRouter API key[/bold cyan]", password=True)
            if not api_key:
                console.print(Panel.fit("[red]API key required for OpenRouter features[/red]", border_style="red"))
                return False
            config['openrouter_api_key'] = api_key
            save_config(config)
            console.print(Panel.fit("[green]OpenRouter API key saved successfully![/green]", title="Setup Complete", border_style="green"))
            
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/ameymalpurkar/Hacker_Diaries",
                "X-Title": "Hacker Diaries",
            }
            data = {
                "model": model_name,
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 500
            }
            console.print(Panel("[bold yellow]🤖 Testing OpenRouter connection...[/bold yellow]", border_style="yellow"))
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                data=json.dumps(data),
                timeout=15
            )
            if response.status_code == 200:
                return True
            else:
                console.print(Panel.fit(f"[red]OpenRouter API Error: Status {response.status_code}\n{response.text}[/red]", title="API Error", border_style="red"))
                return False
        except Exception as e:
            console.print(Panel.fit(f"[red]Connection error: {str(e)}[/red]", title="API Error", border_style="red"))
            return False
    else:
        console.print(Panel.fit(f"[red]Unknown API provider: {provider}[/red]", border_style="red"))
        return False

def setup_gemini_api():
    return setup_ai_api()

def generate_ai_content(prompt):
    config = load_config()
    provider = config.get('api_provider', 'gemini')
    
    if provider == 'gemini':
        import google.generativeai as genai
        genai.configure(api_key=os.getenv('GEMINI_API_KEY') or config.get('gemini_api_key'))
        model = genai.GenerativeModel("gemini-3.5-flash")
        response = model.generate_content(prompt)
        return response.text if hasattr(response, 'text') else str(response)
        
    elif provider == 'openrouter':
        api_key = os.getenv('OPENROUTER_API_KEY') or config.get('openrouter_api_key')
        model_name = config.get('openrouter_model', 'anthropic/claude-sonnet-4')
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/ameymalpurkar/Hacker_Diaries",
            "X-Title": "Hacker Diaries",
        }
        
        data = {
            "model": model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1500
        }
        
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            data=json.dumps(data),
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            try:
                return result['choices'][0]['message']['content']
            except (KeyError, IndexError):
                raise Exception(f"Unexpected response structure from OpenRouter: {json.dumps(result)}")
        else:
            raise Exception(f"OpenRouter API error (Status {response.status_code}): {response.text}")
    else:
        raise Exception(f"Unknown API provider: {provider}")

def ai_task_analysis():
    if not setup_gemini_api():
        return
    
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
        console.print(Panel("[bold yellow]🤖 AI is analyzing your tasks...[/bold yellow]", border_style="yellow"))
        ai_response = generate_ai_content(prompt)
        console.print(Panel(f"[bold cyan]🧠 AI Task Analysis:[/bold cyan]\n\n{ai_response}", title="AI Insights", border_style="cyan"))
    except Exception as e:
        console.print(Panel.fit(f"[red]AI analysis failed: {str(e)}[/red]", title="Error", border_style="red"))

def ai_suggest_tasks():
    if not setup_gemini_api():
        return
    
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
        console.print(Panel("[bold yellow]🤖 AI is generating task suggestions...[/bold yellow]", border_style="yellow"))
        ai_response = generate_ai_content(prompt)
        console.print(Panel(f"[bold cyan]💡 AI Task Suggestions:[/bold cyan]\n\n{ai_response}", title="AI Suggestions", border_style="cyan"))
        
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

def ai_journal_analysis():
    """Analyze journal entries for insights, patterns, and mood"""
    if not setup_gemini_api():
        return
    
    if not os.path.exists(JOURNAL_FILE):
        console.print(Panel.fit("[red]No journal entries found to analyze.[/red]", title="No Entries", border_style="red"))
        return
    
    with open(JOURNAL_FILE, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if '|' in line]
    
    if not lines:
        console.print(Panel.fit("[yellow]No journal entries to analyze.[/yellow]", title="Empty", border_style="yellow"))
        return
    
    # Prepare journal data for AI
    journal_text = ""
    entry_count = 0
    for line in lines:
        if '|' in line:
            date, entry = line.split('|', 1)
            journal_text += f"[{date}] {entry}\n"
            entry_count += 1
    
    # Limit analysis to recent entries if too many
    if entry_count > 20:
        lines = lines[-20:]  # Last 20 entries
        journal_text = ""
        for line in lines:
            date, entry = line.split('|', 1)
            journal_text += f"[{date}] {entry}\n"
        console.print(f"[dim]Analyzing your last 20 journal entries...[/dim]")
    
    prompt = f"""Analyze these journal entries and provide thoughtful insights:

{journal_text}

Please provide:
1. **Mood & Emotional Patterns**: What emotions and moods do you notice?
2. **Key Themes**: What topics or concerns appear frequently?
3. **Personal Growth**: Any signs of progress, learning, or development?
4. **Stress Indicators**: Any signs of stress, anxiety, or challenges?
5. **Positive Highlights**: What positive moments or achievements stand out?
6. **Reflection Questions**: 2-3 thoughtful questions for self-reflection
7. **Gentle Suggestions**: Supportive recommendations for wellbeing

Be empathetic, supportive, and insightful. Focus on patterns and growth opportunities."""

    try:
        console.print(Panel("[bold yellow]🤖 AI is analyzing your journal entries...[/bold yellow]", border_style="yellow"))
        ai_response = generate_ai_content(prompt)
        console.print(Panel(f"[bold cyan]📝 AI Journal Analysis:[/bold cyan]\n\n{ai_response}", title="Personal Insights", border_style="cyan"))
    except Exception as e:
        console.print(Panel.fit(f"[red]AI analysis failed: {str(e)}[/red]", title="Error", border_style="red"))

def ai_journal_mood_tracker():
    """Track mood trends over time"""
    if not setup_gemini_api():
        return
    
    if not os.path.exists(JOURNAL_FILE):
        console.print(Panel.fit("[red]No journal entries found.[/red]", title="No Entries", border_style="red"))
        return
    
    with open(JOURNAL_FILE, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if '|' in line]
    
    if not lines:
        console.print(Panel.fit("[yellow]No journal entries to analyze.[/yellow]", title="Empty", border_style="yellow"))
        return
    
    # Get recent entries for mood tracking
    recent_entries = lines[-10:] if len(lines) > 10 else lines
    journal_text = ""
    for line in recent_entries:
        if '|' in line:
            date, entry = line.split('|', 1)
            journal_text += f"[{date}] {entry}\n"
    
    prompt = f"""Analyze the mood and emotional tone in these journal entries:

{journal_text}

Please provide:
1. **Overall Mood Trend**: Is the general mood positive, neutral, or concerning?
2. **Emotional Range**: What range of emotions are expressed?
3. **Mood Patterns**: Any patterns related to time, events, or circumstances?
4. **Energy Levels**: Signs of high/low energy or motivation?
5. **Mood Score**: Rate overall wellbeing from 1-10 with explanation
6. **Recommendations**: Gentle suggestions to support emotional wellbeing

Be supportive and focus on emotional health insights."""

    try:
        console.print(Panel("[bold yellow]🤖 AI is tracking your mood patterns...[/bold yellow]", border_style="yellow"))
        ai_response = generate_ai_content(prompt)
        console.print(Panel(f"[bold magenta]💭 Mood Analysis:[/bold magenta]\n\n{ai_response}", title="Emotional Insights", border_style="magenta"))
    except Exception as e:
        console.print(Panel.fit(f"[red]Mood analysis failed: {str(e)}[/red]", title="Error", border_style="red"))

def ai_journal_suggestions():
    """Get AI suggestions for journaling prompts and self-reflection"""
    if not setup_gemini_api():
        return
    
    # Get context from recent entries if they exist
    context = ""
    if os.path.exists(JOURNAL_FILE):
        with open(JOURNAL_FILE, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if '|' in line]
            if lines:
                recent_entries = lines[-5:]  # Last 5 entries for context
                for line in recent_entries:
                    if '|' in line:
                        date, entry = line.split('|', 1)
                        context += f"[{date}] {entry}\n"
    
    current_focus = Prompt.ask("[bold cyan]What would you like to focus on? (e.g., 'gratitude', 'goals', 'relationships', 'stress')[/bold cyan]", default="general reflection")
    
    prompt = f"""Based on this focus area: "{current_focus}"

Recent journal context:
{context if context else "No recent entries"}

Please provide:
1. **5 Thoughtful Journal Prompts** related to the focus area
2. **Self-Reflection Questions** for deeper thinking
3. **Mindfulness Suggestions** for present-moment awareness
4. **Growth Opportunities** to explore
5. **Gratitude Prompts** to appreciate positive aspects

Make the suggestions personal, meaningful, and encouraging for self-discovery."""

    try:
        console.print(Panel("[bold yellow]🤖 AI is creating personalized journal prompts...[/bold yellow]", border_style="yellow"))
        ai_response = generate_ai_content(prompt)
        console.print(Panel(f"[bold green]✨ Journal Suggestions:[/bold green]\n\n{ai_response}", title="Writing Prompts", border_style="green"))
    except Exception as e:
        console.print(Panel.fit(f"[red]Suggestion generation failed: {str(e)}[/red]", title="Error", border_style="red"))

def journal_ai_menu():
    """AI menu specifically for journal analysis"""
    console.print(Panel("[bold cyan]📝 AI Journal Assistant[/bold cyan]", border_style="cyan"))
    while True:
        choice = Prompt.ask(
            "[bold cyan]Journal AI: analyze, mood, prompts, back[/bold cyan]", 
            choices=["analyze", "mood", "prompts", "back"], 
            default="analyze"
        )
        
        if choice == "analyze":
            ai_journal_analysis()
        elif choice == "mood":
            ai_journal_mood_tracker()
        elif choice == "prompts":
            ai_journal_suggestions()
        elif choice == "back":
            break

def ai_menu():
    console.print(Panel("[bold magenta]🤖 AI Assistant Menu[/bold magenta]", border_style="magenta"))
    while True:
        choice = Prompt.ask(
            "[bold bright_green]AI Options: tasks, journal, config, back[/bold bright_green]", 
            choices=["tasks", "journal", "config", "back"], 
            default="tasks"
        )
        
        if choice == "tasks":
            # Task-focused AI submenu
            task_choice = Prompt.ask(
                "[bold yellow]Task AI: analyze, suggest, back[/bold yellow]", 
                choices=["analyze", "suggest", "back"], 
                default="analyze"
            )
            if task_choice == "analyze":
                ai_task_analysis()
            elif task_choice == "suggest":
                ai_suggest_tasks()
        elif choice == "journal":
            journal_ai_menu()
        elif choice == "config":
            config_menu()
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

def config_menu():
    """Direct access to configuration options"""
    console.print(Panel("[bold cyan]⚙️ Configuration Menu[/bold cyan]", border_style="cyan"))
    while True:
        choice = Prompt.ask(
            "[bold cyan]Config Options: provider, api, model, file, reset, view, back[/bold cyan]", 
            choices=["provider", "api", "model", "file", "reset", "view", "back"], 
            default="provider"
        )
        
        if choice == "provider":
            config = load_config()
            current_provider = config.get('api_provider', 'gemini')
            console.print(f"Current AI Provider: [bold green]{current_provider}[/bold green]")
            provider = Prompt.ask(
                "[bold cyan]Select AI Provider (gemini, openrouter)[/bold cyan]",
                choices=["gemini", "openrouter"],
                default=current_provider
            )
            config['api_provider'] = provider
            save_config(config)
            console.print(Panel.fit(f"[green]AI Provider set to {provider}![/green]", title="Success", border_style="green"))
            
        elif choice == "api":
            config = load_config()
            provider = config.get('api_provider', 'gemini')
            if provider == "gemini":
                console.print(Panel("[bold yellow]Setting up Gemini AI API Key[/bold yellow]", border_style="yellow"))
                console.print("[cyan]Get your API key from: https://makersuite.google.com/app/apikey[/cyan]")
                console.print("[dim]Tip: Use Ctrl+V to paste your API key[/dim]")
                use_password = Prompt.ask("[bold cyan]Hide API key while typing? (y/n)[/bold cyan]", choices=["y", "n"], default="n")
                if use_password == "y":
                    console.print("[dim]Note: Password mode may not allow pasting in some terminals[/dim]")
                    api_key = Prompt.ask("[bold cyan]Enter your Gemini API key[/bold cyan]", password=True)
                else:
                    api_key = Prompt.ask("[bold cyan]Enter your Gemini API key (paste with Ctrl+V)[/bold cyan]")
                if api_key and api_key.strip():
                    config['gemini_api_key'] = api_key.strip()
                    save_config(config)
                    console.print(Panel.fit("[green]Gemini API key saved successfully![/green]", title="Success", border_style="green"))
                else:
                    console.print(Panel.fit("[red]No API key entered[/red]", border_style="red"))
            else:
                console.print(Panel("[bold yellow]Setting up OpenRouter API Key[/bold yellow]", border_style="yellow"))
                console.print("[cyan]Get your API key from: https://openrouter.ai/keys[/cyan]")
                console.print("[dim]Tip: Use Ctrl+V to paste your API key[/dim]")
                use_password = Prompt.ask("[bold cyan]Hide API key while typing? (y/n)[/bold cyan]", choices=["y", "n"], default="n")
                if use_password == "y":
                    console.print("[dim]Note: Password mode may not allow pasting in some terminals[/dim]")
                    api_key = Prompt.ask("[bold cyan]Enter your OpenRouter API key[/bold cyan]", password=True)
                else:
                    api_key = Prompt.ask("[bold cyan]Enter your OpenRouter API key (paste with Ctrl+V)[/bold cyan]")
                if api_key and api_key.strip():
                    config['openrouter_api_key'] = api_key.strip()
                    save_config(config)
                    console.print(Panel.fit("[green]OpenRouter API key saved successfully![/green]", title="Success", border_style="green"))
                else:
                    console.print(Panel.fit("[red]No API key entered[/red]", border_style="red"))
                    
        elif choice == "model":
            config = load_config()
            provider = config.get('api_provider', 'gemini')
            if provider == "gemini":
                console.print(Panel("[yellow]Gemini provider uses default model gemini-3.5-flash (configured in code).[/yellow]", border_style="yellow"))
            else:
                current_model = config.get('openrouter_model', 'anthropic/claude-sonnet-4')
                console.print(f"Current OpenRouter Model: [bold green]{current_model}[/bold green]")
                console.print("[cyan]Common models: anthropic/claude-sonnet-4, anthropic/claude-sonnet-4.5, anthropic/claude-sonnet-4.6, ~anthropic/claude-sonnet-latest, custom[/cyan]")
                model_choice = Prompt.ask(
                    "[bold cyan]Select OpenRouter Model[/bold cyan]",
                    choices=["anthropic/claude-sonnet-4", "anthropic/claude-sonnet-4.5", "anthropic/claude-sonnet-4.6", "~anthropic/claude-sonnet-latest", "custom"],
                    default="anthropic/claude-sonnet-4"
                )
                if model_choice == "custom":
                    model_choice = Prompt.ask("[bold cyan]Enter custom OpenRouter model name (e.g. open-or-close/model-name)[/bold cyan]")
                if model_choice and model_choice.strip():
                    config['openrouter_model'] = model_choice.strip()
                    save_config(config)
                    console.print(Panel.fit(f"[green]OpenRouter model set to {model_choice}![/green]", title="Success", border_style="green"))
                    
        elif choice == "file":
            config = load_config()
            provider = config.get('api_provider', 'gemini')
            console.print(Panel("[bold yellow]Load API Key from File[/bold yellow]", border_style="yellow"))
            console.print("[cyan]1. Create a text file named 'api_key.txt' in this directory[/cyan]")
            console.print("[cyan]2. Paste your API key into that file and save it[/cyan]")
            console.print("[cyan]3. Press Enter to load it[/cyan]")
            Prompt.ask("[dim]Press Enter when ready...[/dim]", default="")
            
            api_key_file = "api_key.txt"
            if os.path.exists(api_key_file):
                try:
                    with open(api_key_file, 'r', encoding='utf-8') as f:
                        api_key = f.read().strip()
                    if api_key:
                        if provider == "gemini":
                            config['gemini_api_key'] = api_key
                            key_type = "Gemini"
                        else:
                            config['openrouter_api_key'] = api_key
                            key_type = "OpenRouter"
                        save_config(config)
                        # Delete the file for security
                        os.remove(api_key_file)
                        console.print(Panel.fit(f"[green]{key_type} API key loaded and file deleted for security![/green]", title="Success", border_style="green"))
                    else:
                        console.print(Panel.fit("[red]API key file is empty[/red]", border_style="red"))
                except Exception as e:
                    console.print(Panel.fit(f"[red]Error reading file: {str(e)}[/red]", border_style="red"))
            else:
                console.print(Panel.fit("[red]File 'api_key.txt' not found[/red]", border_style="red"))
                
        elif choice == "reset":
            config = load_config()
            provider = config.get('api_provider', 'gemini')
            key_name = 'gemini_api_key' if provider == 'gemini' else 'openrouter_api_key'
            provider_display = 'Gemini' if provider == 'gemini' else 'OpenRouter'
            
            if config.get(key_name):
                if Prompt.ask(f"[bold yellow]Reset {provider_display} API key? (y/n)[/bold yellow]", choices=["y", "n"], default="n") == "y":
                    config.pop(key_name, None)
                    save_config(config)
                    console.print(Panel.fit(f"[green]{provider_display} API key reset successfully![/green]", border_style="green"))
            else:
                console.print(Panel.fit(f"[yellow]No {provider_display} API key configured yet.[/yellow]", border_style="yellow"))
                
        elif choice == "view":
            config = load_config()
            provider = config.get('api_provider', 'gemini')
            
            env_key_name = 'GEMINI_API_KEY' if provider == 'gemini' else 'OPENROUTER_API_KEY'
            key_name = 'gemini_api_key' if provider == 'gemini' else 'openrouter_api_key'
            key_val = os.getenv(env_key_name) or config.get(key_name)
            env_indicator = " (from env)" if os.getenv(env_key_name) else ""
            masked_key = key_val[:8] + "..." + key_val[-4:] + env_indicator if key_val and len(key_val) > 12 else ("***" + env_indicator if key_val else "Not configured")
            
            model_display = "gemini-3.5-flash (default)" if provider == "gemini" else config.get('openrouter_model', 'anthropic/claude-sonnet-4')
            
            info_panel = f"[cyan]Provider:[/cyan] [green]{provider}[/green]\n" \
                         f"[cyan]Active Model:[/cyan] [green]{model_display}[/green]\n" \
                         f"[cyan]API Key:[/cyan] [green]{masked_key}[/green]"
            
            console.print(Panel.fit(info_panel, title="Current Configuration", border_style="green"))
            
        elif choice == "back":
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
            command = Prompt.ask("[bold bright_green]Enter command (add, show, delete, task, ai, journal-ai, config, exit, 404 to quit)[/bold bright_green]", default="show").lower()
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
        elif command == "journal-ai":
            journal_ai_menu()
        elif command == "config":
            config_menu()
        else:
            console.print(Panel(f"[red]Unknown command: {command}[/red]", border_style="red"))

if __name__ == '__main__':
    main()
