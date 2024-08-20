import pytest
from services.translate_service import extract_content,translate_text
from run import create_app

# 创建Flask应用
app = create_app()

# 测试相同文本的情况
# def test_extract_content_same_text():
#     with app.app_context():
#         old_text = "中国画，简单的线条绘制，雄伟的白鼠，金色的灯光效果，发光的眼睛，飘渺的插画风格，精致的笔触，精致的细节，流畅的线条插图"
#         new_text = "中国画，简单的线条绘制，雄伟的白鼠，金色的灯光效果，发光的眼睛，飘渺的插画风格，精致的笔触，精致的细节，流畅的线条插图"
#         result = extract_content(old_text, new_text, "zh")
#         print(result)
#         assert result == "无差异"


# 测试修改文本的情况
def test_extract_content_modified_text():
    with app.app_context():
        old_text = "中国画，简单的线条绘制，雄伟的白鼠，金色的灯光效果，发光的眼睛，飘渺的插画风格，精致的笔触，精致的细节，流畅的线条插图"
        new_text = "油画，简单的线条绘制，雄伟的白老虎，金色的灯光效果，发光的眼睛，飘渺的插画风格，精致的细节，流畅的线条插图，高清"
        expected_result = "修改过的"
        actual_result = extract_content(old_text, new_text)
        print(actual_result)
        assert False
        
# 毫无关系
def test_extract_content_error():
    with app.app_context():
        old_text = "中国画，简单的线条绘制，雄伟的白鼠，金色的灯光效果，发光的眼睛，飘渺的插画风格，精致的笔触，精致的细节，流畅的线条插图"
        new_text = "照此白底彩云间，千里江陵一日还"
        expected_result = "修改过的"
        actual_result = extract_content(old_text, new_text, "zh")
        print(actual_result)
        assert False
        
# 英文测试
def test_extract_content_en():
    with app.app_context():
        old_text = "chinese painting,simple lines drawing,Majestic white mouse,gold light effect,Glowing eyes ,an ethereal illustration style,delicate brushstrokes, exquisite details,free-flowing lines illustrations"
        new_text = "chinese painting,simple lines drawing,Majestic white tiger,gold light effect,Glowing eyes ,an ethereal illustration style,delicate brushstrokes, free-flowing lines illustrations,4K"
        expected_result = "修改过的"
        actual_result = extract_content(old_text, new_text, "zh")
        print(actual_result)
        assert False

def test_translate_text():
    with app.app_context():
        chinese_text = "中国画，简单的线条绘制，雄伟的老虎，金色的灯光效果，发光的眼睛，飘渺的插画风格，精致的笔触，精致的细节，流畅的线条插图，高清摄影"
        english_text = "chinese painting,simple lines drawing,Majestic white mouse,gold light effect,Glowing eyes ,an ethereal illustration style,delicate brushstrokes, exquisite details,free-flowing lines illustrations"
        chinese_old = "中国画，简单的线条绘制，雄伟的白鼠，金色的灯光效果，发光的眼睛，飘渺的插画风格，精致的笔触，精致的细节，流畅的线条插图"
        english_old = "chinese painting,simple lines drawing,Majestic white mouse,gold light effect,Glowing eyes ,an ethereal illustration style,delicate brushstrokes, exquisite details,free-flowing lines illustrations"
        direction = "zh_to_en"
        result = translate_text(chinese_text, english_text, chinese_old, english_old, direction)
        print(result)
        assert False