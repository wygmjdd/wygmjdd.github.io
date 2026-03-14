---
layout: page
title: "按时间归档"
permalink: /archive/
---

按年份与月份浏览文章。点击某年某月可跳转到该月文章列表。

{% assign by_year = site.posts | group_by_exp: "post", "post.date | date: '%Y'" %}
{% if by_year.size > 0 %}
**年份：** {% for y in by_year %}<a href="#{{ y.name }}">{{ y.name }}</a>{% unless forloop.last %} · {% endunless %}{% endfor %}
{% endif %}

{% for year_group in by_year %}
## <span id="{{ year_group.name }}">{{ year_group.name }}</span>年

{% assign by_month = year_group.items | group_by_exp: "post", "post.date | date: '%m'" %}
{% for month_group in by_month %}
### <span id="{{ year_group.name }}-{{ month_group.name }}">{{ year_group.name }}年{{ month_group.name }}月</span>

<ul>
{% for post in month_group.items %}
  <li><a href="{{ post.url | relative_url }}">{{ post.title }}</a> <small>{{ post.date | date: "%Y-%m-%d" }}</small></li>
{% endfor %}
</ul>

{% endfor %}
{% endfor %}

{% if site.posts.size == 0 %}
<p>暂无文章。</p>
{% endif %}
