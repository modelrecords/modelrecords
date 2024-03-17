from planecards.types import PCBoolean, PCString, PCEnum


class Survey:
    """
    A base class representing a survey.

    Attributes:
        score (int): The score of the survey.
        answers (dict): A dictionary containing survey answers.
    """

    def __init__(self, question_answers):
        """
        Initializes a Survey object.

        Args:
            question_answers (list): A list of dictionaries containing question-answer pairs.
        """
        self.score = 0
        self.answers = question_answers


class FMTI2023(Survey):
    """
    A class representing the FMTI 2023 survey.
    Inherits from Survey.

    Attributes:
        QUESTION_SET (list): A list containing the question set for the survey.
        model_name (str): The model name extracted from survey answers.
    """

    QUESTION_SET = [
        {
            "upstream_additional_dependencies": PCBoolean,
            "downstream_affected_individuals": PCBoolean,
            "downstream_affected_market_sectors": PCBoolean,
            "model_blackbox_external_model_access": PCBoolean,
            "upstream_broader_environmental_impact": PCBoolean,
            "model_capabilities_demonstration": PCBoolean,
            "model_capabilities_description": PCBoolean,
            "upstream_carbon_emissions": PCBoolean,
            "downstream_centralized_documentation_for_downstream_use": PCBoolean,
            "model_centralized_model_documentation": PCBoolean,
            "downstream_change_log": PCBoolean,
            "upstream_compute_hardware": PCBoolean,
            "upstream_compute_usage": PCBoolean,
            "upstream_core_frameworks": PCBoolean,
            "upstream_data_augmentation": PCBoolean,
            "upstream_copyrighted_data": PCBoolean,
            "upstream_data_creators": PCBoolean,
            "upstream_data_curation": PCBoolean,
            "upstream_data_license_status": PCBoolean,
            "upstream_data_size": PCBoolean,
            "upstream_data_source_selection": PCBoolean,
            "upstream_data_sources": PCBoolean,
            "downstream_deprecation_policy": PCBoolean,
            "upstream_development_duration": PCBoolean,
            "upstream_direct_external_data_access": PCBoolean,
            "downstream_distribution_channels": PCBoolean,
            "downstream_documentation_for_responsible_downstream_use": PCBoolean,
            "downstream_downstream_applications": PCBoolean,
            "upstream_employment_of_data_laborers": PCBoolean,
            "upstream_energy_usage": PCBoolean,
            "model_evaluation_of_capabilities": PCBoolean,
            "model_external_model_access_protocol": PCBoolean,
            "model_external_reproducibility_of_capabilities_evaluation": PCBoolean,
            "model_external_reproducibility_of_intentional_harm_evaluation": PCBoolean,
            "model_external_reproducibility_of_mitigations_evaluation": PCBoolean,
            "model_external_reproducibility_of_trustworthiness_evaluation": PCBoolean,
            "model_external_reproducibility_of_unintentional_harm_evaluation": PCBoolean,
            "downstream_feedback_mechanism": PCBoolean,
            "downstream_feedback_summary": PCBoolean,
            "model_full_external_model_access": PCBoolean,
            "upstream_geographic_distribution_of_data_laborers": PCBoolean,
            "downstream_geographic_statistics": PCBoolean,
            "downstream_government_inquiries": PCBoolean,
            "upstream_hardware_owner": PCBoolean,
            "upstream_harmful_data_filtration": PCBoolean,
            "model_inference_compute_evaluation": PCBoolean,
            "model_inference_duration_evaluation": PCBoolean,
            "model_input_modality": PCBoolean,
            "upstream_instructions_for_creating_data": PCBoolean,
            "model_intentional_harm_evaluation": PCBoolean,
            "downstream_interoperability_of_usage_and_model_behavior_policies": PCBoolean,
            "downstream_justification_for_enforcement_action": PCBoolean,
            "upstream_labor_protections": PCBoolean,
            "model_limitations_demonstration": PCBoolean,
            "model_limitations_description": PCBoolean,
            "downstream_detection_of_machine_generated_content": PCBoolean,
            "model_mitigations_demonstration": PCBoolean,
            "model_mitigations_description": PCBoolean,
            "model_mitigations_evaluation": PCBoolean,
            "upstream_mitigations_for_copyright": PCBoolean,
            "upstream_mitigations_for_privacy": PCBoolean,
            "model_model_architecture": PCBoolean,
            "model_asset_license": PCBoolean,
            "downstream_model_behavior_policy_enforcement": PCBoolean,
            "model_model_components": PCBoolean,
            "upstream_model_objectives": PCBoolean,
            "model_model_size": PCBoolean,
            "upstream_model_stages": PCBoolean,
            "downstream_monitoring_mechanism": PCBoolean,
            "model_output_modality": PCBoolean,
            "downstream_permitted_and_prohibited_use_of_user_data": PCBoolean,
            "downstream_permitted_and_prohibited_users": PCBoolean,
            "upstream_personal_information_in_data": PCBoolean,
            "downstream_products_and_services": PCBoolean,
            "upstream_queryable_external_data_access": PCBoolean,
            "downstream_redress_mechanism": PCBoolean,
            "downstream_release_decision_making_protocol": PCBoolean,
            "downstream_release_process": PCBoolean,
            "model_risks_demonstration": PCBoolean,
            "model_risks_description": PCBoolean,
            "downstream_terms_of_service": PCBoolean,
            "model_third_party_capabilities_evaluation": PCBoolean,
            "model_third_party_evaluation_of_limitations": PCBoolean,
            "model_third_party_mitigations_evaluation": PCBoolean,
            "model_third_party_risks_evaluation": PCBoolean,
            "upstream_third_party_partners": PCBoolean,
            "model_trustworthiness_evaluation": PCBoolean,
            "model_unintentional_harm_evaluation": PCBoolean,
            "downstream_usage_data_access_protocol": PCBoolean,
            "downstream_usage_disclaimers": PCBoolean,
            "downstream_usage_policy_enforcement": PCBoolean,
            "downstream_usage_policy_violation_appeals_mechanism": PCBoolean,
            "downstream_usage_reports": PCBoolean,
            "upstream_use_of_human_labor": PCBoolean,
            "downstream_user_data_protection_policy": PCBoolean,
            "downstream_user_interaction_with_ai_system": PCBoolean,
            "downstream_versioning_protocol": PCBoolean,
            "upstream_wages": PCBoolean,
            "downstream_permitted_restricted_and_prohibited_model_behaviors": PCBoolean,
            "downstream_permitted_restricted_and_prohibited_uses": PCBoolean,
        }
    ]

    def __init__(self, question_answers, model_name):
        """
        Initializes an FMTI2023 object.

        Args:
        question_answers (list): A list of dictionaries containing question-answer pairs.
        model_name (str): The name of the model associated with the survey.
        """
        super().__init__(question_answers)
        self.model_name = model_name

    def name(self):
        return "FMTI - 2023"

    def parse(self):
        """
        Parses the survey answers.
        """
        # validation, checking, etc.
        for question_set in self.QUESTION_SET:
            for question, _ in question_set.items():
                if question not in self.answers:
                    print(f"Question {question} not answered.")
                    continue

                answer = self.answers[question]
                if answer not in [0, 1]:
                    raise ValueError(
                        f"Answer {answer} for question {question} is not valid."
                    )

                if answer == 1:
                    self.score += 1

        # support for calling out to a magical LLM that can read the project repo and be asked questions

    def result(self):
        return f"FMTI -- {self.model_name}: Your score is {self.score}"
