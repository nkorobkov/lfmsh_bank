class TransactionService:
    class __TransactionService:
        pass

    instance = None

    def __init__(self, ):
        if not TransactionService.instance:
            TransactionService.instance = TransactionService.__TransactionService()

    def __getattr__(self, name):
        return getattr(self.instance, name)
