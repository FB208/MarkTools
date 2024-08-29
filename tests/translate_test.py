import pytest
from services.translate_service import extract_content,translate_text,expert_translate
from app import create_app
from test_config import TestConfig

app = create_app()
app.config.from_object(TestConfig)



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

# pytest tests/translate_test.py::test_expert_translate
def test_expert_translate():
    with app.app_context():
        text = """
Google announced Wednesday that it is adding its latest image generator — Imagen 3 — to Gemini and the company will resume the creation of images that include people.

**Why it matters:** Google paused the depiction of people earlier this year after it was creating diverse, but historically inaccurate images, such as Black founding fathers.

**Driving the news:** In a blog post, Google said the more powerful image generator will be coming to Gemini over the coming days.

- Google is also gradually bringing back the ability to create images with people, albeit with new safety measures.
- Among other limitations, Google says it won't generate photorealistic images of people, won't create images that include either kids or identifiable people and will also aim to prevent depictions of "excessively gory, violent or sexual scenes."
- For now, Google is limiting such images to English prompts and to Gemini Advanced, Business and Enterprise users.
- Google is also adding support for the "Gems" feature that lets people create domain-specific versions of Gemini. Previewed at Google I/O, Gems are now available in 150 languages for that same group of paid users.
"""
        result = expert_translate(text)
        print(result)
        assert False