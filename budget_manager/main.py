"""
Main entry point for the budget manager application.
"""

from .cli.commands import BudgetCLI


def main():
    """Main entry point for the CLI application."""
    BudgetCLI.run()


if __name__ == "__main__":
    main() 