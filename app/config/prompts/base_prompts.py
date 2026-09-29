class BasePrompts:    
    @staticmethod
    def format_prompt(prompt: str, **kwargs) -> str:
        return prompt.format(**kwargs)