def main():

    import argparse
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Prompt
    from datetime import datetime
    import os

    JOURNAL_FILE = 'journal.txt'
    console = Console()

    def add_entry():
        entry_text = Prompt.ask("[bold cyan]What's on your mind?[/bold cyan]")
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        with open(JOURNAL_FILE, 'a', encoding='utf-8') as f:
            f.write(f'{timestamp}|{entry_text}\n')
        console.print(Panel.fit("[green]Entry added![/green]", title="Success", border_style="green"))

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

    def main():
        parser = argparse.ArgumentParser(description='[Journaling CLI] Capture your thoughts in style!')
        parser.add_argument('-a', '--add', action='store_true', help='Add a new journal entry')
        parser.add_argument('-s', '--show', action='store_true', help='Show all journal entries')
        args = parser.parse_args()

        console.print(Panel("[bold magenta]Welcome to the Journaling CLI![/bold magenta]", border_style="magenta"))

        if args.add:
            add_entry()
        elif args.show:
            show_entries()
        else:
            # Default: prompt user for action
            action = Prompt.ask("[bold cyan]What would you like to do?[/bold cyan]", choices=["add", "show", "exit"], default="add")
            if action == "add":
                add_entry()
            elif action == "show":
                show_entries()
            else:
                console.print("[bold yellow]Goodbye![/bold yellow]")

    if __name__ == '__main__':
        main()
