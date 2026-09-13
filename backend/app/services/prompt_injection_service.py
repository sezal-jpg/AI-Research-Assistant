import re
from app.core.logger import logger

class PromptInjectionService:

    def __init__(self):
        self.injection_patterns = [
            # Instruction override attempts
            r"\bignore\s+(all\s+|any\s+|the\s+)?(previous|prior|above|earlier)\s+instructions?\b",
            r"\bdisregard\s+(all\s+|any\s+|the\s+)?(previous|prior|above|earlier)\s+instructions?\b",
            r"\bforget\s+(all\s+|any\s+|the\s+)?(previous|prior|above|earlier)\s+instructions?\b",

            # System/developer instruction manipulation
            r"\b(ignore|disregard|override|bypass)\s+(the\s+)?(system|developer)\s+(prompt|message|instructions?)\b",
            r"\bshow\s+(me\s+)?(the\s+)?system\s+prompt\b",
            r"\breveal\s+(the\s+)?(system|developer)\s+(prompt|message|instructions?)\b",
            r"\bwhat\s+(is|are)\s+(your\s+)?(system|developer)\s+(prompt|instructions?)\b",

            # Role manipulation
            r"\byou\s+are\s+now\s+(a|an)\b",
            r"\bact\s+as\s+(a|an)\b",
            r"\bpretend\s+to\s+be\b",
            r"\broleplay\s+as\b",

            # Attempts to override assistant behavior
            r"\bfrom\s+now\s+on\s+ignore\b",
            r"\bfrom\s+now\s+on\s+you\s+(must|should|will)\b",
            r"\bdo\s+not\s+follow\s+(the\s+)?(previous|original)\s+instructions?\b",

            # Prompt / policy extraction
            r"\breveal\s+(your\s+)?(hidden\s+)?instructions?\b",
            r"\bshow\s+(me\s+)?(your\s+)?(hidden\s+)?instructions?\b",
            r"\bprint\s+(your\s+)?(system\s+|hidden\s+)?instructions?\b",
        ]

    def check_prompt(self, question: str) -> dict:
        """
        Detect common prompt-injection patterns in user input.

        Returns:
            {
                "safe": bool,
                "detected": bool,
                "reason": str
            }
        """

        question = (question or "").strip()
        if not question:
            return {
                "safe": True,
                "detected": False,
                "reason": ""
            }

        normalized_question = re.sub(
            r"\s+",
            " ",
            question.lower() )

        for pattern in self.injection_patterns:
            if re.search(pattern, normalized_question):
                logger.warning(
                    "Prompt injection attempt detected"
                )

                return {
                    "safe": False,
                    "detected": True,
                    "reason": "Instruction override or prompt extraction attempt detected"
                }

        logger.info(
            "Prompt injection check passed")

        return {
            "safe": True,
            "detected": False,
            "reason": "" }

prompt_injection_service = PromptInjectionService()