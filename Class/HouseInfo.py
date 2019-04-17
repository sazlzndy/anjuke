



class HouseInfo:
    """房屋id"""
    HouseInfoId='',
    """短标题"""
    Title='',
    """房屋网页详细地址"""
    URL='',
    """房屋类型 4室2厅"""
    HouseType='',
    '''面积'''
    Area='',
    """房屋类型 4室2厅"""
    Floor='',
    """年限"""
    YearOfBuild='',
    """房屋地址"""
    SpecificAddress='',
    """总价"""
    TotalPrices='',
    """单价"""
    TheUnitPrice='',
    """来源 中环地产"""
    SourceUrl='',

    """长描述"""
    LongTitle='',

    """装修"""
    Fitment='',

    """小区名称"""
    CommunityName='',


    def to_dict(self):
        pr = {}
        for name in dir(self):
            value = getattr(self, name)
            if not name.startswith('__') and not callable(value) and not name.startswith('_'):
                pr[name] = value
        return pr