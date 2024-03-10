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
            "additional_dependencies": PCBoolean,
            "affected_individuals": PCBoolean,
            "affected_market_sectors": PCBoolean,
            "blackbox_external_model_access": PCBoolean,
            "broader_environmental_impact": PCBoolean,
            "capabilities_demonstration": PCBoolean,
            "capabilities_description": PCBoolean,
            "carbon_emissions": PCBoolean,
            "centralized_documentation_for_downstream_use": PCBoolean,
            "centralized_model_documentation": PCBoolean,
            "change_log": PCBoolean,
            "compute_hardware": PCBoolean,
            "compute_usage": PCBoolean,
            "core_frameworks": PCBoolean,
            "data_augmentation": PCBoolean,
            "data_copyright_status": PCBoolean,
            "data_creators_": PCBoolean,
            "data_curation": PCBoolean,
            "data_license_status": PCBoolean,
            "data_size": PCBoolean,
            "data_source_selection": PCBoolean,
            "data_sources": PCBoolean,
            "deprecation_policy": PCBoolean,
            "development_duration": PCBoolean,
            "direct_external_data_access": PCBoolean,
            "distribution_channels": PCBoolean,
            "documentation_for_responsible_downstream_use": PCBoolean,
            "downstream_applications": PCBoolean,
            "employment_of_data_laborers": PCBoolean,
            "energy_usage": PCBoolean,
            "evaluation_of_capabilities": PCBoolean,
            "external_model_access_protocol": PCBoolean,
            "external_reproducibility_of_capabilities_evaluation": PCBoolean,
            "external_reproducibility_of_intentional_harm_evaluation": PCBoolean,
            "external_reproducibility_of_mitigations_evaluation": PCBoolean,
            "external_reproducibility_of_trustworthiness_evaluation": PCBoolean,
            "external_reproducibility_of_unintentional_harm_evaluation": PCBoolean,
            "feedback_mechanism": PCBoolean,
            "feedback_summary": PCBoolean,
            "full_external_model_access": PCBoolean,
            "geographic_distribution_of_data_laborers": PCBoolean,
            "geographic_statistics": PCBoolean,
            "government_inquiries": PCBoolean,
            "hardware_owner": PCBoolean,
            "harmful_data_filtration": PCBoolean,
            "inference_compute_evaluation": PCBoolean,
            "inference_duration_evaluation": PCBoolean,
            "input_modality": PCBoolean,
            "instructions_for_creating_data": PCBoolean,
            "intentional_harm_evaluation": PCBoolean,
            "interoperability_of_usage_and_model_behavior_policies": PCBoolean,
            "justification_for_enforcement_action": PCBoolean,
            "labor_protections": PCBoolean,
            "limitations_demonstration": PCBoolean,
            "limitations_description": PCBoolean,
            "machine-generated_content": PCBoolean,
            "mitigations_demonstration": PCBoolean,
            "mitigations_description": PCBoolean,
            "mitigations_evaluation": PCBoolean,
            "mitigations_for_copyright": PCBoolean,
            "mitigations_for_privacy": PCBoolean,
            "model_architecture": PCBoolean,
            "model_asset_license": PCBoolean,
            "model_behavior_policy_enforcement": PCBoolean,
            "model_components": PCBoolean,
            "model_objectives": PCBoolean,
            "model_size": PCBoolean,
            "model_stages": PCBoolean,
            "monitoring_mechanism": PCBoolean,
            "output_modality": PCBoolean,
            "permitted,_restricted,_and_prohibited_model_behaviors": PCBoolean,
            "permitted,_restricted,_and_prohibited_uses": PCBoolean,
            "permitted_and_prohibited_use_of_user_data": PCBoolean,
            "permitted_and_prohibited_users": PCBoolean,
            "personal_information_in_data": PCBoolean,
            "products_and_services": PCBoolean,
            "queryable_external_data_access": PCBoolean,
            "redress_mechanism": PCBoolean,
            "release_decision-making_protocol": PCBoolean,
            "release_process": PCBoolean,
            "risks_demonstration": PCBoolean,
            "risks_description": PCBoolean,
            "terms_of_service": PCBoolean,
            "third-party_capabilities_evaluation": PCBoolean,
            "third-party_evaluation_of_limitations": PCBoolean,
            "third-party_mitigations_evaluation": PCBoolean,
            "third-party_risks_evaluation": PCBoolean,
            "third_party_partners": PCBoolean,
            "trustworthiness_evaluation": PCBoolean,
            "unintentional_harm_evaluation": PCBoolean,
            "usage_data_access_protocol": PCBoolean,
            "usage_disclaimers": PCBoolean,
            "usage_policy_enforcement": PCBoolean,
            "usage_policy_violation_appeals_mechanism": PCBoolean,
            "usage_reports": PCBoolean,
            "use_of_human_labor": PCBoolean,
            "user_data_protection_policy": PCBoolean,
            "user_interaction_with_ai_system": PCBoolean,
            "versioning_protocol": PCBoolean,
            "wages": PCBoolean,
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
        for question, answer in self.answers.items():
            if answer == 1:
                self.score += 1

        # support for calling out to a magical LLM that can read the project repo and be asked questions

    def result(self):
        return f"FMTI -- {self.model_name}: Your score is {self.score}"
