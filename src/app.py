from src.controllers.vault_controller import VaultController

def main():
    # Instantiate the brain of the app
    controller = VaultController()
    
    # Launch the execution flow
    controller.start()

if __name__ == "__main__":
    main()
