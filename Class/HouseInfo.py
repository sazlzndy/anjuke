



class HouseInfo:
    HouseInfoId='',
    Title='',
    URL='',
    HouseType='',
    Area='',
    Floor='',
    YearOfBuild='',
    SpecificAddress='',
    TotalPrices='',
    TheUnitPrice='',
    SourceUrl='',

    def to_dict(self):
        pr = {}
        for name in dir(self):
            value = getattr(self, name)
            if not name.startswith('__') and not callable(value) and not name.startswith('_'):
                pr[name] = value
        return pr