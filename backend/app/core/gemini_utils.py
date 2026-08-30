from app.core.logger import logger

def is_quota_error(error):
    error_text=str(error).lower()
    quota_keywords=[ "quota exceeded",
        "rate limit",
        "429",
        "too many requests",
        "resource exhausted"]
    return any(keyword in error_text for keyword in quota_keywords)

def log_gemini_error(operation,error):
    if is_quota_error(error):
        logger.warning(f'Gemini quota/rate limit reached'
                       f"during {operation}")
        return 'quota'
    logger.error(f'Gemini error during {operation}:{error}')
    return 'error'