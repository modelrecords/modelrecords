import argparse
import yaml
from planecards.plane_card import PlaneCard

def get_parser():
    parser = argparse.ArgumentParser(
        description="Planecards CLI"
    )
    parser.add_argument("--pc_path", default="", type=str, help="")

    return parser

if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()

    plane_card = yaml.safe_load(open(args.pc_path, 'rb'))
    pc = PlaneCard(plane_card)
    pc.parse()
    print(pc.results())
