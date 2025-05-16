def analyze_numbers(numbers):
    down_numbers = int(''.join(map(str, numbers[0:3])))  # 合并前3位数字并转为整数
    up_numbers = int(''.join(map(str, numbers[3:6])))    # 合并中间3位数字并转为整数
    move_numbers = int(''.join(map(str, numbers[6:9])))  # 合并后3位数字并转为整数
    
    down_number = down_numbers % 8 if down_numbers % 8 != 0 else 8
    up_number = up_numbers % 8 if up_numbers % 8 != 0 else 8
    move_number = move_numbers % 6 if move_numbers % 6 != 0 else 6  # 这里应该是6不是8
    
    # 乾 兑 离 震 巽 坎 艮 坤
    gua = ["乾","兑","离","震","巽","坎","艮","坤"]
    gua_attribute = ["天","泽","火","雷","风","水","山","地"]
    ids = ['111','110','101','100','011','010','001','000']
    gid = ids[down_number-1]+ids[up_number-1]  # 索引从0开始所以要减1
    yid = f'{gid}_{move_number}'
    bgid = gid[:move_number-1] + ('0' if gid[move_number-1] == '1' else '1') + gid[move_number:]
    attribute = gua_attribute[up_number-1]+gua_attribute[down_number-1]
    return gid,yid,bgid,attribute

def get_64gua_ico(index):
    gualist = ['䷀','䷁','䷂','䷃','䷄','䷅','䷆','䷇','䷈','䷉','䷊','䷋','䷌','䷍','䷎','䷏','䷐','䷑','䷒','䷓','䷔','䷕','䷖','䷗','䷘','䷙','䷚','䷛','䷜','䷝','䷞','䷟','䷠','䷡','䷢','䷣','䷤','䷥','䷦','䷧','䷨','䷩','䷪','䷫','䷬','䷭','䷮','䷯','䷰','䷱','䷲','䷳','䷴','䷵','䷶','䷷','䷸','䷹','䷺','䷻','䷼','䷽','䷾','䷿']
    return gualist[index]
