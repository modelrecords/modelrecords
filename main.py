import argparse
import os
import yaml
from modelrecord.modelrecord import ModelRecord


def get_parser():
    parser = argparse.ArgumentParser(description="Unified Model Records CLI")
    parser.add_argument(
        "--mr_dir",
        default="cards",
        type=str,
        help="Directory containing record YAML files",
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

    for filename in os.listdir(args.mr_dir):
        if filename.endswith(".yaml"):
            file_path = os.path.join(args.mr_dir, filename)
            modelrecord = yaml.safe_load(open(file_path, "rb"))
            model_name = os.path.splitext(filename)[0]
            mr = ModelRecord(modelrecord, model_name)
            mr.parse()
            print(mr.results())
