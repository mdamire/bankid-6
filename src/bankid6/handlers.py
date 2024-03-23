
class StartParams():
    def __init__(self, **kwrags):
        self.kwargs = kwrags
    
    def clean_endUserIp(self, value):
        return True
    
    def clean_userVisibleDataFormat(self, value):
        if value is True:
            value = 'simpleMarkdownV1'
        
        return value

    def clean(self):
        cleaned_data = {}

        for key in self.kwargs.keys():
            value = self.kwargs[key]
            if value is None:
                continue

            if hasattr(self, f'clean_{key}'):
                cleaned_data[key] = str(getattr(self, f'clean_{key}')(value))
            else:
                cleaned_data[key] = str(value)
        
        return cleaned_data
    

class BankIdStartResponse():
    def __init__(self, response):
        self.response = response


def make_bankid_start_response(response):
    
    return BankIdStartResponse(response)
