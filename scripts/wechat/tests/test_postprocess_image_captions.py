from scripts.wechat.postprocess_image_captions import line_to_figure


def test_line_to_figure_uses_caption_for_generic_alt_text() -> None:
    html, changed = line_to_figure("![图片](/images/example.jpg)山路尽头的家")

    assert changed is True
    assert 'alt="山路尽头的家"' in html
    assert "<figcaption>山路尽头的家</figcaption>" in html


def test_line_to_figure_preserves_specific_alt_text() -> None:
    html, changed = line_to_figure("![巫溪山景](/images/example.jpg)雨后的山")

    assert changed is True
    assert 'alt="巫溪山景"' in html
