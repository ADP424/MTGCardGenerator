import argparse
from common import process_spreadsheet
from constants import CARD_RULES_TEXT, CARD_TITLE
from log import reset_log


def main():
    reset_log()
    cards = process_spreadsheet()
    for card in cards.values():
        card.add_layer("images/frames/regular/artifact.png")
        card.metadata[CARD_RULES_TEXT] = card.metadata[CARD_RULES_TEXT]
        card.render_rules_text(card.metadata[CARD_RULES_TEXT])
        final_card = card.merge_layers()
        final_card.save(f"processed_cards/{card.metadata[CARD_TITLE]}.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate MTG cards based on the provided sheet.")
    main()
