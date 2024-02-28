import argparse

def get_parser():
    parser = argparse.ArgumentParser(
        description="Planecards CLI"
    )
    parser.add_argument("--pc_path", default="", type=str, help="")
    
    return parser

if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    print(vars(args))