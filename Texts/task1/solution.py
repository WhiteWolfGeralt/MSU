color_rgb = r'^rgb\((0|[12][0-5]{0,2})(,\s*(0|[12][0-5]{0,2})){2}\)$|^rgb\((0%|100%|[1-9][0-9]?%)(,\s*(0%|100%|[1-9][0-9]?%)){2}\)$'
color_hex = r'^#([0-9]|[a-fA-F]){6}$|^#([0-9]|[a-fA-F]){3}$'
color_hsl = r'^hsl\((0|360|[1-9][0-9]?|[12][0-9][0-9]|3[0-5][0-9])(,\s*(0%|100%|[1-9][0-9]?%)){2}\)$'

expr_var = r'(?P<variable>[A-z_]{1}[0-9A-z_]*)'
expr_num = r'(?P<number>[1-9][0-9]*(\.[1-9][0-9]*)?)'
expr_const = r'(?P<constant>(pi|e|sqrt2|ln2|ln10)(?![A-z_\d]))'
expr_func = r'(?P<function>(sin|cos|tg|ctg|tan|cot|sinh|cosh|th|cth|tanh|coth|ln|lg|log|exp|sqrt|cbrt|abs|sign)(?![A-z_\d]))'
expr_operator = r'(?P<operator>[\^*/\-+])'
expr_LP = r'(?P<left_parenthesis>\()'
expr_RP = r'(?P<right_parenthesis>\))'

date_dmy = r'(((0?[1-9]|[12][0-9]|30|31)(?P<delim>[./\-])(0?[13578]|10|12)(?P=delim)\d+)|((0?[1-9]|[12][0-9]|30)(?P<delim2>[./\-])(0?[469]|11)(?P=delim2)\d+)|((0?[1-9]|[12][0-8])(?P<delim3>[./\-])(0?2)(?P=delim3)\d+))'
date_ymd = r'((\d+(?P<delim4>[./\-])(0?[13578]|10|12)(?P=delim4)(0?[1-9]|[12][0-9]|30|31))|(\d+(?P<delim5>[./\-])(0?[469]|11)(?P=delim5)(0?[1-9]|[12][0-9]|30))|(\d+(?P<delim6>[./\-])(0?2)(?P=delim6)(0?[1-9]|[12][0-8])))'
date_dmRUSy = r'(((0?[1-9]|[12][0-9]|30|31)\s+(января|марта|мая|июля|августа|октября|декабря)\s+\d+)|((0?[1-9]|[12][0-9]|30)\s+(апреля|июня|сентября|ноября)\s+\d+)|((0?[1-9]|[12][0-8])\s+февраля\s+\d+))'
date_mENGdy = r'(((Jan(uary)?|Mar(ch)?|May|Jul(y)?|Aug(ust)?|Oct(ober)?|Dec(ember)?)\s+(0?[1-9]|[12][0-9]|30|31),\s+\d+)|((Apr(il)?|Jun(e)?|Sep(tember)?|Nov(ember)?)\s+(0?[1-9]|[12][0-9]|30),\s+\d+)|(Feb(ruary)?\s+(0?[1-9]|[12][0-8]),\s+\d+))'
date_ymENGd = r'((\d+,\s+(Jan(uary)?|Mar(ch)?|May|Jul(y)?|Aug(ust)?|Oct(ober)?|Dec(ember)?)\s+([12][0-9]|30|31|0?[1-9]))|(\d+,\s+(Apr(il)?|Jun(e)?|Sep(tember)?|Nov(ember)?)\s+([12][0-9]|30|0?[1-9]))|(\d+,\s+Feb(ruary)?\s+([12][0-8]|0?[1-9])))'


COLOR_REGEXP = '|'.join([color_rgb, color_hex, color_hsl])
PASSWORD_REGEXP = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=(?:(.)(?!\1))+$)(?=(.*(?P<special>[\^$%@#&*!?]).*(?!(?P=special))[\^$%@#&*!?])+)[A-Za-z0-9^$%@#&*!?]{8,}$'
EXPRESSION_REGEXP = '|'.join([expr_func, expr_const, expr_var, expr_num, expr_operator, expr_LP, expr_RP])
DATES_REGEXP = '|'.join([date_dmy, date_ymd, date_dmRUSy, date_ymENGd, date_mENGdy])
