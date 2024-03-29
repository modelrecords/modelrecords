import argparse
import os
import yaml
from planecards.plane_card import PlaneCard


def get_parser():
    parser = argparse.ArgumentParser(description="Planecards CLI")
    parser.add_argument(
        "--pc_dir",
        default="cards",
        type=str,
        help="Directory containing plane card YAML files",
    )
    parser.add_argument(
        "--pdf_dir",
        default=None,
        type=str,
    )
    return parser


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()

    for filename in os.listdir(args.pc_dir):
        if filename.endswith(".yaml"):
            file_path = os.path.join(args.pc_dir, filename)
            plane_card = yaml.safe_load(open(file_path, "rb"))
            model_name = os.path.splitext(filename)[0]
            pc = PlaneCard(plane_card, model_name)
            pc.parse()
            print(pc.results())
