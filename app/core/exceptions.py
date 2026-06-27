class BaseAppException(Exception):
    """Bütün xüsusi xətalar üçün təməl sinif"""
    pass

class NotFoundException(BaseAppException):
    def __init__(self, entity_name: str):
        super().__init__(f"{entity_name} tapılmadı.")

class ValidationException(BaseAppException):
    def __init__(self, message: str):
        super().__init__(message)

class PermissionDeniedException(BaseAppException):
    def __init__(self):
        super().__init__("Sizin bu əməliyyatı yerinə yetirmək üçün icazəniz yoxdur.")
