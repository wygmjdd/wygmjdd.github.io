---
layout: page
title: "三十分钟日记"
permalink: /category/30min-diary/
---

<ul>
{% for post in site.categories["30min-diary"] %}
  <li><a href="{{ post.url | relative_url }}">{{ post.title }}</a> <small>{{ post.date | date: "%Y-%m-%d" }}</small></li>
{% endfor %}
</ul>
