import json

from pipe.core.services.prompt_service import PromptService
from pipe.core.services.session_service import SessionService


def run(session_service: SessionService, prompt_service: PromptService):
    """
    Builds the prompt using PromptService and prints the resulting JSON.
    """
    prompt_model = prompt_service.build_prompt(session_service)

    # Determine which template to use based on api_mode
    template_name = (
        "gemini_api_prompt.j2"
        if session_service.settings.api_mode == "gemini-api"
        else "gemini_cli_prompt.j2"
    )
    template = prompt_service.jinja_env.get_template(template_name)

    # Render the template with the prompt model data
    rendered_prompt = template.render(session=prompt_model)

    # Print the rendered JSON, ensuring it's pretty-printed
    print(json.dumps(json.loads(rendered_prompt), indent=2, ensure_ascii=False))
