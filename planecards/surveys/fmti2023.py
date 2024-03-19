from planecards.types import PCBoolean, PCString, PCEnum
from planecards.survey import Survey

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
            "upstream.additional_dependencies": PCBoolean,
            "downstream.affected_individuals": PCBoolean,
            "downstream.affected_market_sectors": PCBoolean,
            "model.blackbox_external_model_access": PCBoolean,
            "upstream.broader_environmental_impact": PCBoolean,
            "model.capabilities_demonstration": PCBoolean,
            "model.capabilities_description": PCBoolean,
            "upstream.carbon_emissions": PCBoolean,
            "downstream.centralized_documentation_for_downstream_use": PCBoolean,
            "model.centralized_model_documentation": PCBoolean,
            "downstream.change_log": PCBoolean,
            "upstream.compute_hardware": PCBoolean,
            "upstream.compute_usage": PCBoolean,
            "upstream.core_frameworks": PCBoolean,
            "upstream.data_augmentation": PCBoolean,
            "upstream.copyrighted_data": PCBoolean,
            "upstream.data_creators": PCBoolean,
            "upstream.data_curation": PCBoolean,
            "upstream.data_license_status": PCBoolean,
            "upstream.data_size": PCBoolean,
            "upstream.data_source_selection": PCBoolean,
            "upstream.data_sources": PCBoolean,
            "downstream.deprecation_policy": PCBoolean,
            "upstream.development_duration": PCBoolean,
            "upstream.direct_external_data_access": PCBoolean,
            "downstream.distribution_channels": PCBoolean,
            "downstream.documentation_for_responsible_downstream_use": PCBoolean,
            "downstream.downstream_applications": PCBoolean,
            "upstream.employment_of_data_laborers": PCBoolean,
            "upstream.energy_usage": PCBoolean,
            "model.evaluation_of_capabilities": PCBoolean,
            "model.external_model_access_protocol": PCBoolean,
            "model.external_reproducibility_of_capabilities_evaluation": PCBoolean,
            "model.external_reproducibility_of_intentional_harm_evaluation": PCBoolean,
            "model.external_reproducibility_of_mitigations_evaluation": PCBoolean,
            "model.external_reproducibility_of_trustworthiness_evaluation": PCBoolean,
            "model.external_reproducibility_of_unintentional_harm_evaluation": PCBoolean,
            "downstream.feedback_mechanism": PCBoolean,
            "downstream.feedback_summary": PCBoolean,
            "model.full_external_model_access": PCBoolean,
            "upstream.geographic_distribution_of_data_laborers": PCBoolean,
            "downstream.geographic_statistics": PCBoolean,
            "downstream.government_inquiries": PCBoolean,
            "upstream.hardware_owner": PCBoolean,
            "upstream.harmful_data_filtration": PCBoolean,
            "model.inference_compute_evaluation": PCBoolean,
            "model.inference_duration_evaluation": PCBoolean,
            "model.input_modality": PCBoolean,
            "upstream.instructions_for_creating_data": PCBoolean,
            "model.intentional_harm_evaluation": PCBoolean,
            "downstream.interoperability_of_usage_and_model_behavior_policies": PCBoolean,
            "downstream.justification_for_enforcement_action": PCBoolean,
            "upstream.labor_protections": PCBoolean,
            "model.limitations_demonstration": PCBoolean,
            "model.limitations_description": PCBoolean,
            "downstream.detection_of_machine_generated_content": PCBoolean,
            "model.mitigations_demonstration": PCBoolean,
            "model.mitigations_description": PCBoolean,
            "model.mitigations_evaluation": PCBoolean,
            "upstream.mitigations_for_copyright": PCBoolean,
            "upstream.mitigations_for_privacy": PCBoolean,
            "model.model_architecture": PCBoolean,
            "model.asset_license": PCBoolean,
            "downstream.model_behavior_policy_enforcement": PCBoolean,
            "model.model_components": PCBoolean,
            "upstream.model_objectives": PCBoolean,
            "model.model_size": PCBoolean,
            "upstream.model_stages": PCBoolean,
            "downstream.monitoring_mechanism": PCBoolean,
            "model.output_modality": PCBoolean,
            "downstream.permitted_and_prohibited_use_of_user_data": PCBoolean,
            "downstream.permitted_and_prohibited_users": PCBoolean,
            "upstream.personal_information_in_data": PCBoolean,
            "downstream.products_and_services": PCBoolean,
            "upstream.queryable_external_data_access": PCBoolean,
            "downstream.redress_mechanism": PCBoolean,
            "downstream.release_decision_making_protocol": PCBoolean,
            "downstream.release_process": PCBoolean,
            "model.risks_demonstration": PCBoolean,
            "model.risks_description": PCBoolean,
            "downstream.terms_of_service": PCBoolean,
            "model.third_party_capabilities_evaluation": PCBoolean,
            "model.third_party_evaluation_of_limitations": PCBoolean,
            "model.third_party_mitigations_evaluation": PCBoolean,
            "model.third_party_risks_evaluation": PCBoolean,
            "upstream.third_party_partners": PCBoolean,
            "model.trustworthiness_evaluation": PCBoolean,
            "model.unintentional_harm_evaluation": PCBoolean,
            "downstream.usage_data_access_protocol": PCBoolean,
            "downstream.usage_disclaimers": PCBoolean,
            "downstream.usage_policy_enforcement": PCBoolean,
            "downstream.usage_policy_violation_appeals_mechanism": PCBoolean,
            "downstream.usage_reports": PCBoolean,
            "upstream.use_of_human_labor": PCBoolean,
            "downstream.user_data_protection_policy": PCBoolean,
            "downstream.user_interaction_with_ai_system": PCBoolean,
            "downstream.versioning_protocol": PCBoolean,
            "upstream.wages": PCBoolean,
            "downstream.permitted_restricted_and_prohibited_model_behaviors": PCBoolean,
            "downstream.permitted_restricted_and_prohibited_uses": PCBoolean,
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
