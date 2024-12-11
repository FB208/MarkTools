import pytest
import json
from app import create_app
from test_config import TestConfig
from services.article_service import comment, hook,rewrite ,title

# 创建Flask应用
app = create_app()
app.config.from_object(TestConfig)

content = """
Google announced Wednesday that it is adding its latest image generator — Imagen 3 — to Gemini and the company will resume the creation of images that include people.

**Why it matters:** Google paused the depiction of people earlier this year after it was creating diverse, but historically inaccurate images, such as Black founding fathers.

**Driving the news:** In a blog post, Google said the more powerful image generator will be coming to Gemini over the coming days.

- Google is also gradually bringing back the ability to create images with people, albeit with new safety measures.
- Among other limitations, Google says it won't generate photorealistic images of people, won't create images that include either kids or identifiable people and will also aim to prevent depictions of "excessively gory, violent or sexual scenes."
- For now, Google is limiting such images to English prompts and to Gemini Advanced, Business and Enterprise users.
- Google is also adding support for the "Gems" feature that lets people create domain-specific versions of Gemini. Previewed at Google I/O, Gems are now available in 150 languages for that same group of paid users.
"""
# pytest tests/article_service_test.py::test_comment
def test_comment():
    with app.app_context():
        print("Using API key:", app.config['OPENAI_API_KEY'])
        result = comment(content)
        print(result)
        assert False
        
# pytest tests/article_service_test.py::test_hook
def test_hook():
    with app.app_context():
        result = hook(content)
        print(result)
        assert False

# pytest tests/article_service_test.py::test_rewrite
def test_rewrite():
    with app.app_context():
        result = ''#rewrite_body(content)
        print(result)
        assert False
        
# pytest tests/article_service_test.py::test_title
def test_title():
    with app.app_context():
        result = title(content)
        print(result)
        assert False