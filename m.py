from rich.console import Console
from rich.table import Table
from rich import box

no_inner_edge = box.Box(
    "╭──╮\n"
    "│  │\n"
    "├─┼┤\n"
    "│  │\n"
    "├─┼┤\n"
    "├─┼┤\n"
    "│  │\n"
    "╰──╯\n"
)
table = Table(title="Star Wars Movies", box=no_inner_edge, show_header=False)

table.add_column()
table.add_column()

table.add_row(*["Dec 20, 2019", "Star Wars: The Rise of Skywalker"])
table.add_row("May 25, 2018", "Solo: A Star Wars Story")
table.add_row("Dec 15, 2017", "Star Wars Ep. V111: The Last Jedi")
table.add_row("Dec 16, 2016", "Rogue One: A Star Wars Story")

console = Console()
console.print(table)