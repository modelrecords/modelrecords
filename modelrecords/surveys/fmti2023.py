from modelrecords.types import MRBoolean
from modelrecords.survey import Survey

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
            "upstream.additional_dependencies": MRBoolean,
            "downstream.affected_individuals": MRBoolean,
            "downstream.affected_market_sectors": MRBoolean,
            "model.blackbox_external_model_access": MRBoolean,
            "upstream.broader_environmental_impact": MRBoolean,
            "model.capabilities_demonstration": MRBoolean,
            "model.capabilities_description": MRBoolean,
            "upstream.carbon_emissions": MRBoolean,
            "downstream.centralized_documentation_for_downstream_use": MRBoolean,
            "model.centralized_model_documentation": MRBoolean,
            "downstream.change_log": MRBoolean,
            "upstream.compute_hardware": MRBoolean,
            "upstream.compute_usage": MRBoolean,
            "upstream.core_frameworks": MRBoolean,
            "upstream.data_augmentation": MRBoolean,
            "upstream.copyrighted_data": MRBoolean,
            "upstream.data_creators": MRBoolean,
            "upstream.data_curation": MRBoolean,
            "upstream.data_license_status": MRBoolean,
            "upstream.data_size": MRBoolean,
            "upstream.data_source_selection": MRBoolean,
            "upstream.data_sources": MRBoolean,
            "downstream.deprecation_policy": MRBoolean,
            "upstream.development_duration": MRBoolean,
            "upstream.direct_external_data_access": MRBoolean,
            "downstream.distribution_channels": MRBoolean,
            "downstream.documentation_for_responsible_downstream_use": MRBoolean,
            "downstream.downstream_applications": MRBoolean,
            "upstream.employment_of_data_laborers": MRBoolean,
            "upstream.energy_usage": MRBoolean,
            "model.evaluation_of_capabilities": MRBoolean,
            "model.external_model_access_protocol": MRBoolean,
            "model.external_reproducibility_of_capabilities_evaluation": MRBoolean,
            "model.external_reproducibility_of_intentional_harm_evaluation": MRBoolean,
            "model.external_reproducibility_of_mitigations_evaluation": MRBoolean,
            "model.external_reproducibility_of_trustworthiness_evaluation": MRBoolean,
            "model.external_reproducibility_of_unintentional_harm_evaluation": MRBoolean,
            "downstream.feedback_mechanism": MRBoolean,
            "downstream.feedback_summary": MRBoolean,
            "model.full_external_model_access": MRBoolean,
            "upstream.geographic_distribution_of_data_laborers": MRBoolean,
            "downstream.geographic_statistics": MRBoolean,
            "downstream.government_inquiries": MRBoolean,
            "upstream.hardware_owner": MRBoolean,
            "upstream.harmful_data_filtration": MRBoolean,
            "model.inference_compute_evaluation": MRBoolean,
            "model.inference_duration_evaluation": MRBoolean,
            "model.input_modality": MRBoolean,
            "upstream.instructions_for_creating_data": MRBoolean,
            "model.intentional_harm_evaluation": MRBoolean,
            "downstream.interoperability_of_usage_and_model_behavior_policies": MRBoolean,
            "downstream.justification_for_enforcement_action": MRBoolean,
            "upstream.labor_protections": MRBoolean,
            "model.limitations_demonstration": MRBoolean,
            "model.limitations_description": MRBoolean,
            "downstream.detection_of_machine_generated_content": MRBoolean,
            "model.mitigations_demonstration": MRBoolean,
            "model.mitigations_description": MRBoolean,
            "model.mitigations_evaluation": MRBoolean,
            "upstream.mitigations_for_copyright": MRBoolean,
            "upstream.mitigations_for_privacy": MRBoolean,
            "model.model_architecture": MRBoolean,
            "model.asset_license": MRBoolean,
            "downstream.model_behavior_policy_enforcement": MRBoolean,
            "model.model_components": MRBoolean,
            "upstream.model_objectives": MRBoolean,
            "model.model_size": MRBoolean,
            "upstream.model_stages": MRBoolean,
            "downstream.monitoring_mechanism": MRBoolean,
            "model.output_modality": MRBoolean,
            "downstream.permitted_and_prohibited_use_of_user_data": MRBoolean,
            "downstream.permitted_and_prohibited_users": MRBoolean,
            "upstream.personal_information_in_data": MRBoolean,
            "downstream.products_and_services": MRBoolean,
            "upstream.queryable_external_data_access": MRBoolean,
            "downstream.redress_mechanism": MRBoolean,
            "downstream.release_decision_making_protocol": MRBoolean,
            "downstream.release_process": MRBoolean,
            "model.risks_demonstration": MRBoolean,
            "model.risks_description": MRBoolean,
            "downstream.terms_of_service": MRBoolean,
            "model.third_party_capabilities_evaluation": MRBoolean,
            "model.third_party_evaluation_of_limitations": MRBoolean,
            "model.third_party_mitigations_evaluation": MRBoolean,
            "model.third_party_risks_evaluation": MRBoolean,
            "upstream.third_party_partners": MRBoolean,
            "model.trustworthiness_evaluation": MRBoolean,
            "model.unintentional_harm_evaluation": MRBoolean,
            "downstream.usage_data_access_protocol": MRBoolean,
            "downstream.usage_disclaimers": MRBoolean,
            "downstream.usage_policy_enforcement": MRBoolean,
            "downstream.usage_policy_violation_appeals_mechanism": MRBoolean,
            "downstream.usage_reports": MRBoolean,
            "upstream.use_of_human_labor": MRBoolean,
            "downstream.user_data_protection_policy": MRBoolean,
            "downstream.user_interaction_with_ai_system": MRBoolean,
            "downstream.versioning_protocol": MRBoolean,
            "upstream.wages": MRBoolean,
            "downstream.permitted_restricted_and_prohibited_model_behaviors": MRBoolean,
            "downstream.permitted_restricted_and_prohibited_uses": MRBoolean,
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
