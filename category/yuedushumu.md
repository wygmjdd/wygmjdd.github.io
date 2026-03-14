---
layout: page
title: "阅读书目"
permalink: /category/yuedushumu/
---

<ul>
{% for post in site.categories["yuedushumu"] %}
  <li><a href="{{ post.url | relative_url }}">{{ post.title }}</a> <small>{{ post.date | date: "%Y-%m-%d" }}</small></li>
{% endfor %}
</ul>
