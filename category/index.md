---
layout: page
title: "按类型"
permalink: /category/
---

按文章类型（专辑）浏览。

<ul>
{% for cat in site.categories %}
  {% assign slug = cat[0] %}
  {% assign name = site.data.categories[slug] | default: slug %}
  <li><a href="{{ '/category/' | append: slug | append: '/' | relative_url }}">{{ name }}</a>（{{ cat[1].size }} 篇）</li>
{% endfor %}
</ul>

{% if site.categories.size == 0 %}
<p>暂无分类。</p>
{% endif %}
