import pandas as pd
import yaml

ORG_TO_MODEL_NAME = {
    'google': 'palm2',
    'meta': 'llama2',
    'hugging_face': 'bloomz',
    'openai': 'gpt4',
    'stability_ai': 'stable_diffusion_2',
    'anthropic': 'claude2',
    'cohere': 'command',
    'ai21_labs': 'jurassic2',
    'inflection': 'inflection1',
    'amazon': 'titan_next',
}

def generate_questions():
  df = pd.read_csv('csv/scores.csv')

  # Get the list of models. (columns after 'Indicator' and exclude 'Total')
  models = df.columns[df.columns.get_loc('Indicator') + 1: -1]

  # Iterate over each model and create a YAML file.
  for model in models:
    question_answers = {}

    # Iterate over each row in the DataFrame skip the Totals row.
    for _, row in df[:-1].iterrows():
        indicator = row['Indicator'].replace(' ', '_').lower()
        score = row[model]
        question_answers[indicator] = int(score)

    yaml_content = {
        'question_answers': question_answers,
        'question_sets': ['fmti2023']
    }

    # Use the model name instead of the org.
    model_name = ORG_TO_MODEL_NAME[model.replace(' ', '_').lower()]
    yaml_file = f"cards/{model_name}.yaml"

    with open(yaml_file, 'w') as file:
        yaml.dump(yaml_content, file, default_flow_style=False)

print("YAML files generated successfully.")

if __name__ == "__main__":
    generate_questions()
