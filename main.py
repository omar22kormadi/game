import sys
from game import Game

if __name__ == "__main__":
    use_trained_ai = "--use-trained-ai" in sys.argv
    trained_model = None

    if use_trained_ai:
        from trained_ai_player import load_trained_model
        trained_model = load_trained_model()

        if trained_model is None:
            print("\nFalling back to heuristic AI...")
            use_trained_ai = False

    game = Game(use_trained_ai=use_trained_ai, trained_model=trained_model)
    game.run()
