---
layout: page
title: "年终总结"
permalink: /category/year-end-summary/
---

<ul>
{% for post in site.categories["year-end-summary"] %}
  <li><a href="{{ post.url | relative_url }}">{{ post.title }}</a> <small>{{ post.date | date: "%Y-%m-%d" }}</small></li>
{% endfor %}
</ul>
