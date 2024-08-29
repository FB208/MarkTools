import os
import pytest
from utils.md_util import remove_markdown_links

# pytest tests/utils/md_util_test.py::test_remove_markdown_links
def test_remove_markdown_links():
    markdown_text = "Yelp is suing Google, alleging in an antitrust lawsuit that the [tech](https://www.axios.com/technology) giant self-preferenced its own product to dominate local search and advertising markets against competitors."
    cleaned_text = remove_markdown_links(markdown_text)
    print(cleaned_text) 
    assert False
