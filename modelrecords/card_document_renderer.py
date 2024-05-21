import os
from jinja2 import Environment, PackageLoader, select_autoescape
from modelrecords.modelrecord import ModelRecord
from pathlib import Path


class CardDocumentRenderer:

    def __init__(
        self,
        modelrecord_model: ModelRecord,
        output_dir="output",
        output_filename="modelrecord.tex",
        pdf_cmd="pdflatex",
    ):
        self.pdf_cmd = pdf_cmd
        self.output_dir = output_dir
        self.output_filename = output_filename
        self.modelrecord_model = modelrecord_model

        env = Environment(
            loader=PackageLoader("modelrecords"),
            autoescape=select_autoescape(),
            block_start_string="\BLOCK{",
            block_end_string="}",
            variable_start_string="\VAR{",
            variable_end_string="}",
            comment_start_string="\#{",
            comment_end_string="}",
            line_statement_prefix="%%",
            line_comment_prefix="%#",
            trim_blocks=True,
        )
        self.template = env.get_template("card.tpl.tex")

    def render_tex(self):
        return self.template.render(self.modelrecord_model.results_as_dict())

    def save_pdf(self):
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        with open(f"{self.output_dir}/{self.output_filename}", "w") as f:
            f.write(self.render_tex())
        os.system(
            f"{self.pdf_cmd} --output-directory={self.output_dir} {self.output_dir}/{self.output_filename} "
        )
