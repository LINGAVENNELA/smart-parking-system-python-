def main():
    print("Smart Parking System")
    print("1. CLI")
    print("2. GUI")
    choice = input("Enter choice (1/2): ").strip()

    while choice not in ('1', '2'):
        print("Invalid choice. Please enter 1 or 2.")
        choice = input("Enter choice (1/2): ").strip()

    if choice == '1':
        from cli.cli_interface import run_cli
        run_cli()
    else:
        from gui.gui_main import main as run_gui_main
        run_gui_main()

if __name__ == "__main__":
    main()
