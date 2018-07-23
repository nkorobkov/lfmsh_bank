from bank.constants.BankAPIExeptions import TransactionTypeNotSupported


class TransactionController:
    @classmethod
    def get_render_map_update(cls):
        return {}

    @classmethod
    def get_blank_form(cls, creator_username):
        pass

    @staticmethod
    def build_transaction_from_api_request(api_request_body):
        raise TransactionTypeNotSupported(api_request_body.get('trans_type'))
