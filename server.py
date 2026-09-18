#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nekich Search - Retro 2014 Google Clone
Features:
- Pure HTTP support (optimized for IE6 and vintage browsers)
- No gbar & No extra tabs (clean retro interface)
- Clean compact pagination (no giant Gooooooogle letters)
- SVG search button
- 5 Larger Rotating Ad Banners (Inori Aizawa, LunaStore, Renaissance, FaeroFM, faero.top)
- Pages: /about (О компании), /advertising (Реклама), /settings (Настройки с отключением рекламы), /privacy, /terms, /business
- Dynamic copyright (2026-текущий год) across all pages
- Custom authentic retro Google 404 error page
- Standard library only (zero external dependencies)
- True AST Template Engine
"""

import http.server
import socketserver
import urllib.request
import urllib.parse
import ssl
import re
import html
import time
import os
import random
import json
import threading
import argparse
from http import cookies

# 5 Rotating Ad Banners
BANNERS = [
    {
        "name": "Inori Aizawa",
        "caption": "Inori Aizawa - Let's explore the web!",
        "img_url": "http://faero.top/ad/inori.png",
        "target_url": "http://inori.faero.top"
    },
    {
        "name": "LunaStore",
        "caption": "LunaStore - Лучший магазин приложений для старых ПК (работает даже на IE6)",
        "img_url": "http://faero.top/ad/ls_rek.png",
        "target_url": "http://lunastore.app"
    },
    {
        "name": "Renaissance",
        "caption": "Renaissance - мессенджер основанный на движке Агента@Mail.RU",
        "img_url": "http://faero.top/ad/mrim.jpg",
        "target_url": "http://mrim.su"
    },
    {
        "name": "FaeroFM",
        "caption": "FaeroFM - Old hits. Good memories.",
        "img_url": "http://faero.top/ad/faerofm.png",
        "target_url": "http://fm.faero.top"
    },
    {
        "name": "faero.top",
        "caption": "faero.top - Подари вторую жизнь своему браузеру из нулевых!",
        "img_url": "http://faero.top/ad/faero.png",
        "target_url": "http://faero.top"
    }
]

banner_lock = threading.Lock()
banner_counter = 0
banner_cache = {}

def get_copyright_years():
    """Returns formatted copyright string (2026-текущий год)."""
    cur_year = time.strftime("%Y")
    if cur_year == "2026":
        return "2026"
    return f"2026-{cur_year}"


def get_banner_by_index(idx):
    """Fetches and caches banner image bytes by banner index."""
    idx = idx % len(BANNERS)
    banner_info = BANNERS[idx]
    url = banner_info["img_url"]

    now = time.time()
    if url in banner_cache:
        data, cached_at = banner_cache[url]
        if now - cached_at < 300:
            return data

    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=8) as resp:
            data = resp.read()
            banner_cache[url] = (data, now)
            return data
    except Exception as e:
        print(f"[Banner Error] Could not fetch {url}: {e}")
        if url in banner_cache:
            return banner_cache[url][0]
        return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x00\x00\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82'


def get_next_banner_info():
    """Rotates to next banner and returns (index, banner_dict)."""
    global banner_counter
    with banner_lock:
        idx = banner_counter % len(BANNERS)
        banner_counter += 1
        return idx, BANNERS[idx]


def fetch_duckduckgo_results(query, page=1):
    """Fetches web search results with DuckDuckGo API, HTML parser, and robust fallback."""
    results = []
    zero_click = None
    ctx = ssl.create_default_context()

    # 1. DuckDuckGo Instant Answer API
    try:
        api_url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json&no_html=0&skip_disambig=0"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=6) as r:
            ddg_json = json.loads(r.read().decode("utf-8"))
            if ddg_json.get("Heading") and ddg_json.get("Abstract"):
                zero_click = {
                    "title": ddg_json["Heading"],
                    "url": ddg_json.get("AbstractURL", f"https://duckduckgo.com/?q={urllib.parse.quote(query)}"),
                    "snippet": ddg_json["Abstract"]
                }
            for topic in ddg_json.get("RelatedTopics", []):
                if "Topics" in topic:
                    for sub in topic["Topics"]:
                        if "FirstURL" in sub and "Text" in sub:
                            first_url = sub["FirstURL"]
                            text = sub["Text"]
                            title_part = text.split(" - ")[0] if " - " in text else text[:50]
                            results.append({
                                "title": title_part,
                                "url": first_url,
                                "display_url": first_url,
                                "snippet": text
                            })
                elif "FirstURL" in topic and "Text" in topic:
                    first_url = topic["FirstURL"]
                    text = topic["Text"]
                    title_part = text.split(" - ")[0] if " - " in text else text[:50]
                    results.append({
                        "title": title_part,
                        "url": first_url,
                        "display_url": first_url,
                        "snippet": text
                    })
    except Exception:
        pass

    # 2. DuckDuckGo HTML parser
    if len(results) < 5:
        try:
            url = "https://html.duckduckgo.com/html/"
            data = {"q": query}
            if page > 1:
                data["s"] = str((page - 1) * 30)
                data["dc"] = str((page - 1) * 30 + 1)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            encoded_data = urllib.parse.urlencode(data).encode("utf-8")
            req = urllib.request.Request(url, data=encoded_data, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=8) as resp:
                html_content = resp.read().decode("utf-8", errors="ignore")

            items = re.findall(r'<div class="result results_links results_links_deep web-result\s*">(.*?)<div class="clear"></div>\s*</div>', html_content, re.DOTALL)
            if not items:
                items = re.findall(r'<div class="links_main links_deep result__body">(.*?)<div class="clear"></div>', html_content, re.DOTALL)

            for item in items:
                title_m = re.search(r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', item, re.DOTALL)
                if not title_m:
                    title_m = re.search(r'<h2 class="result__title">\s*<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', item, re.DOTALL)
                snippet_m = re.search(r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>', item, re.DOTALL)
                if not snippet_m:
                    snippet_m = re.search(r'<div[^>]*class="result__snippet"[^>]*>(.*?)</div>', item, re.DOTALL)
                url_display_m = re.search(r'<a[^>]*class="result__url"[^>]*>(.*?)</a>', item, re.DOTALL)

                if title_m:
                    raw_url = title_m.group(1)
                    raw_title = title_m.group(2)
                    real_url = raw_url
                    if "uddg=" in raw_url:
                        parsed_q = urllib.parse.parse_qs(urllib.parse.urlparse(raw_url).query)
                        if "uddg" in parsed_q:
                            real_url = parsed_q["uddg"][0]
                    elif raw_url.startswith("//duckduckgo.com/l/?") or raw_url.startswith("/l/?"):
                        parsed_q = urllib.parse.parse_qs(urllib.parse.urlparse("https:" + raw_url).query)
                        if "uddg" in parsed_q:
                            real_url = parsed_q["uddg"][0]

                    clean_title = html.unescape(re.sub(r'<[^>]+>', '', raw_title)).strip()
                    clean_snippet = ""
                    if snippet_m:
                        clean_snippet = html.unescape(snippet_m.group(1)).strip()
                        clean_snippet = re.sub(r'<(?!/?(b|em|strong)\b)[^>]+>', '', clean_snippet)

                    clean_display_url = html.unescape(re.sub(r'<[^>]+>', '', url_display_m.group(1))).strip() if url_display_m else real_url
                    results.append({
                        "title": clean_title,
                        "url": real_url,
                        "display_url": clean_display_url,
                        "snippet": clean_snippet
                    })
        except Exception:
            pass

    # 3. Wikipedia OpenSearch fallback
    if len(results) < 2:
        try:
            wiki_url = f"https://ru.wikipedia.org/w/api.php?action=opensearch&search={urllib.parse.quote(query)}&limit=10&namespace=0&format=json"
            req = urllib.request.Request(wiki_url, headers={"User-Agent": "NekichSearch/1.0"})
            with urllib.request.urlopen(req, context=ctx, timeout=5) as r:
                wdata = json.loads(r.read().decode("utf-8"))
                if len(wdata) >= 4 and wdata[1]:
                    for i in range(len(wdata[1])):
                        t = wdata[1][i]
                        sn = wdata[2][i] if i < len(wdata[2]) else ""
                        u = wdata[3][i] if i < len(wdata[3]) else ""
                        if u:
                            results.append({
                                "title": t,
                                "url": u,
                                "display_url": u,
                                "snippet": sn
                            })
        except Exception:
            pass

    return {"zero_click": zero_click, "results": results}


# ---------------------------------------------------------
# Robust AST Template Engine (Zero external dependencies)
# ---------------------------------------------------------

class Node:
    pass

class TextNode(Node):
    def __init__(self, text):
        self.text = text
    def render(self, ctx):
        return self.text

class VarNode(Node):
    def __init__(self, expr):
        self.expr = expr.strip()
    def render(self, ctx):
        expr = self.expr
        if '.' in expr and not any(op in expr for op in [' ', '+', '-', '*', '/', '(', ')']):
            parts = expr.split('.')
            val = ctx.get(parts[0], '')
            for p in parts[1:]:
                if isinstance(val, dict):
                    val = val.get(p, '')
                else:
                    val = getattr(val, p, '')
            return str(val) if val is not None else ''
        try:
            val = eval(expr, {"__builtins__": {}}, ctx)
            return str(val) if val is not None else ''
        except Exception:
            return str(ctx.get(expr, ''))

class IfNode(Node):
    def __init__(self, condition, true_nodes, false_nodes=None):
        self.condition = condition.strip()
        self.true_nodes = true_nodes
        self.false_nodes = false_nodes or []
    def render(self, ctx):
        cond_val = False
        try:
            cond_val = bool(eval(self.condition, {"__builtins__": {}}, ctx))
        except Exception:
            cond_val = bool(ctx.get(self.condition, False))
            
        nodes = self.true_nodes if cond_val else self.false_nodes
        return "".join(n.render(ctx) for n in nodes)

class ForNode(Node):
    def __init__(self, item_var, list_var, children):
        self.item_var = item_var.strip()
        self.list_var = list_var.strip()
        self.children = children
    def render(self, ctx):
        items = ctx.get(self.list_var, [])
        out = []
        for it in items:
            sub_ctx = ctx.copy()
            sub_ctx[self.item_var] = it
            for child in self.children:
                out.append(child.render(sub_ctx))
        return "".join(out)

def parse_template(template_str):
    tokens = re.split(r'({[{%].*?[}%]})', template_str, flags=re.DOTALL)
    
    def parse_nodes(token_iter, stop_tags):
        nodes = []
        for token in token_iter:
            if not token:
                continue
            if token.startswith('{{') and token.endswith('}}'):
                expr = token[2:-2]
                nodes.append(VarNode(expr))
            elif token.startswith('{%') and token.endswith('%}'):
                tag_content = token[2:-2].strip()
                parts = tag_content.split()
                if not parts:
                    continue
                tag_name = parts[0]
                
                if tag_name in stop_tags:
                    return nodes, tag_name
                    
                if tag_name == 'if':
                    condition = tag_content[2:].strip()
                    true_nodes, end_tag = parse_nodes(token_iter, ['else', 'endif'])
                    false_nodes = []
                    if end_tag == 'else':
                        false_nodes, _ = parse_nodes(token_iter, ['endif'])
                    nodes.append(IfNode(condition, true_nodes, false_nodes))
                    
                elif tag_name == 'for':
                    item_var = parts[1]
                    list_var = parts[3]
                    children, _ = parse_nodes(token_iter, ['endfor'])
                    nodes.append(ForNode(item_var, list_var, children))
            else:
                nodes.append(TextNode(token))
        return nodes, None

    nodes, _ = parse_nodes(iter(tokens), [])
    return nodes

def render_template(template_str, context):
    nodes = parse_template(template_str)
    return "".join(n.render(context) for n in nodes)


class NekichSearchHandler(http.server.BaseHTTPRequestHandler):
    """HTTP Request Handler for Nekich Search."""

    server_version = "NekichSearch/3.5"

    def get_cookies(self):
        """Parses request cookies."""
        cookie_header = self.headers.get("Cookie")
        if not cookie_header:
            return {}
        c = cookies.SimpleCookie()
        try:
            c.load(cookie_header)
            return {k: v.value for k, v in c.items()}
        except Exception:
            return {}

    def is_ads_disabled(self):
        """Checks whether ads are disabled in cookies."""
        cks = self.get_cookies()
        return cks.get("ads_disabled") == "1"

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        raw_path = parsed.path
        path = raw_path.rstrip("/") if raw_path != "/" else "/"
        query_params = urllib.parse.parse_qs(parsed.query)

        # Root Favicon
        if path == "/favicon.ico":
            self.serve_static("favicon.ico")
            return

        # 1. Homepage
        if path in ["", "/", "/index.html", "/index.htm"]:
            self.serve_homepage()
            return

        # 2. Search endpoint
        if path == "/search":
            self.serve_search(query_params)
            return

        # 3. About page (О компании)
        if path in ["/about", "/about.html", "/intl/ru/about.html", "/intl/en/about.html"]:
            self.serve_about()
            return

        # 4. Advertising page (Реклама)
        if path in ["/advertising", "/advertising.html", "/ads", "/intl/ru/ads"]:
            self.serve_advertising()
            return

        # 5. Settings page (Настройки)
        if path in ["/settings", "/settings.html", "/preferences", "/preferences.html"]:
            self.serve_settings(saved=False)
            return

        # 6. Privacy page (Конфиденциальность)
        if path in ["/privacy", "/privacy.html", "/intl/ru/policies/privacy"]:
            self.serve_privacy()
            return

        # 7. Terms page (Условия)
        if path in ["/terms", "/terms.html", "/intl/ru/policies/terms"]:
            self.serve_terms()
            return

        # 8. Business page (Для бизнеса)
        if path in ["/business", "/business.html", "/services", "/services.html"]:
            self.serve_business()
            return

        # 9. Help / Feedback
        if path in ["/help", "/help.html", "/feedback", "/support"]:
            self.serve_about()
            return

        # 10. Rotating Ad Banner endpoint
        if path == "/ad/banner.png":
            self.serve_banner(query_params)
            return

        # 11. Static files
        if path.startswith("/static/"):
            self.serve_static(path[8:])
            return

        # 12. Custom Retro 404 Error Page
        self.serve_404(raw_path)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        raw_path = parsed.path
        path = raw_path.rstrip("/") if raw_path != "/" else "/"

        if path in ["/settings", "/settings.html", "/preferences"]:
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length).decode("utf-8", errors="ignore")
            params = urllib.parse.parse_qs(post_data)
            ads_disabled_val = params.get("ads_disabled", ["0"])[0]

            self.serve_settings(saved=True, set_ads_disabled=(ads_disabled_val == "1"))
            return

        self.serve_404(raw_path)

    def serve_homepage(self):
        try:
            with open("templates/index.html", "r", encoding="utf-8") as f:
                template_str = f.read()
            context = {"copyright_years": get_copyright_years()}
            rendered = render_template(template_str, context)
            body = rendered.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception:
            self.serve_404("/")

    def serve_about(self):
        try:
            with open("templates/about.html", "r", encoding="utf-8") as f:
                template_str = f.read()
            context = {"copyright_years": get_copyright_years()}
            rendered = render_template(template_str, context)
            body = rendered.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception:
            self.serve_404("/about")

    def serve_advertising(self):
        try:
            with open("templates/advertising.html", "r", encoding="utf-8") as f:
                template_str = f.read()
            context = {"copyright_years": get_copyright_years()}
            rendered = render_template(template_str, context)
            body = rendered.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception:
            self.serve_404("/advertising")

    def serve_privacy(self):
        try:
            with open("templates/privacy.html", "r", encoding="utf-8") as f:
                template_str = f.read()
            context = {"copyright_years": get_copyright_years()}
            rendered = render_template(template_str, context)
            body = rendered.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception:
            self.serve_404("/privacy")

    def serve_terms(self):
        try:
            with open("templates/terms.html", "r", encoding="utf-8") as f:
                template_str = f.read()
            context = {"copyright_years": get_copyright_years()}
            rendered = render_template(template_str, context)
            body = rendered.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception:
            self.serve_404("/terms")

    def serve_business(self):
        try:
            with open("templates/business.html", "r", encoding="utf-8") as f:
                template_str = f.read()
            context = {"copyright_years": get_copyright_years()}
            rendered = render_template(template_str, context)
            body = rendered.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception:
            self.serve_404("/business")

    def serve_settings(self, saved=False, set_ads_disabled=None):
        if set_ads_disabled is not None:
            ads_disabled = set_ads_disabled
        else:
            ads_disabled = self.is_ads_disabled()

        context = {
            "saved": saved,
            "ads_disabled": ads_disabled,
            "copyright_years": get_copyright_years()
        }

        try:
            with open("templates/settings.html", "r", encoding="utf-8") as f:
                template_str = f.read()

            rendered = render_template(template_str, context)
            body = rendered.encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            if set_ads_disabled is not None:
                cookie_val = "1" if set_ads_disabled else "0"
                self.send_header("Set-Cookie", f"ads_disabled={cookie_val}; Path=/; Max-Age=31536000")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception:
            self.serve_404("/settings")

    def serve_search(self, query_params):
        query = query_params.get("q", [""])[0].strip()
        btn_lucky = "btnI" in query_params

        if not query:
            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()
            return

        try:
            page = int(query_params.get("p", ["1"])[0])
            if page < 1:
                page = 1
        except ValueError:
            page = 1

        start_time = time.time()
        search_data = fetch_duckduckgo_results(query, page)
        results = search_data["results"]
        zero_click = search_data["zero_click"]
        count = len(results)

        if btn_lucky and results:
            first_url = results[0]["url"]
            self.send_response(302)
            self.send_header("Location", first_url)
            self.end_headers()
            return

        elapsed = round(time.time() - start_time, 2)
        if elapsed < 0.05:
            elapsed = 0.12

        total_pages = 10 if count > 0 else 1
        pages = list(range(1, min(11, total_pages + 1)))

        approx_total = 1250000 + (len(query) * 87400) + random.randint(100, 9999)
        total_results_fmt = f"{approx_total:,}".replace(",", " ")

        b_idx, banner = get_next_banner_info()
        ads_disabled = self.is_ads_disabled()

        context = {
            "query": query,
            "query_encoded": urllib.parse.quote_plus(query),
            "zero_click": zero_click,
            "results": results,
            "total_results_fmt": total_results_fmt,
            "elapsed_time": f"{elapsed:.2f}".replace(".", ","),
            "current_page": page,
            "total_pages": total_pages,
            "pages": pages,
            "ads_disabled": ads_disabled,
            "banner_idx": b_idx,
            "banner_name": banner["name"],
            "banner_caption": banner["caption"],
            "banner_target": banner["target_url"],
            "copyright_years": get_copyright_years(),
            "timestamp": int(time.time() * 1000)
        }

        try:
            with open("templates/search.html", "r", encoding="utf-8") as f:
                template_str = f.read()

            rendered = render_template(template_str, context)
            body = rendered.encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception:
            self.serve_404("/search")

    def serve_banner(self, query_params):
        """Serves alternating banner directly over HTTP."""
        b_param = query_params.get("b", [None])[0]
        try:
            if b_param is not None:
                idx = int(b_param)
            else:
                idx, _ = get_next_banner_info()
        except ValueError:
            idx = 0

        data = get_banner_by_index(idx)
        content_type = "image/jpeg" if BANNERS[idx % len(BANNERS)]["img_url"].endswith(".jpg") else "image/png"

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def serve_static(self, rel_path):
        """Serves static assets."""
        file_path = os.path.join("static", rel_path)
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            self.serve_404("/static/" + rel_path)
            return

        content_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".ico": "image/x-icon",
            ".css": "text/css; charset=utf-8",
            ".html": "text/html; charset=utf-8",
            ".js": "application/javascript",
            ".svg": "image/svg+xml"
        }

        ext = os.path.splitext(file_path)[1].lower()
        content_type = content_types.get(ext, "application/octet-stream")

        try:
            with open(file_path, "rb") as f:
                data = f.read()

            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except Exception:
            self.serve_404("/static/" + rel_path)

    def serve_404(self, requested_path):
        """Renders authentic retro Google 404 error page."""
        try:
            with open("templates/404.html", "r", encoding="utf-8") as f:
                template_str = f.read()
            context = {"requested_path": requested_path}
            rendered = render_template(template_str, context)
            body = rendered.encode("utf-8")
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception:
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"<h1>404 Not Found</h1>")


class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def main():
    parser = argparse.ArgumentParser(description="Nekich Search - Retro 2014 Google Clone")
    parser.add_argument("--host", default="0.0.0.0", help="Host address to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on (default: 8080)")
    args = parser.parse_args()

    for i in range(len(BANNERS)):
        threading.Thread(target=get_banner_by_index, args=(i,), daemon=True).start()

    server_address = (args.host, args.port)
    httpd = ThreadingHTTPServer(server_address, NekichSearchHandler)
    print("=" * 60)
    print(f" Nekich Search (Retro 2014 Google) is running!")
    print(f" URL: http://localhost:{args.port}/")
    print(f" Mode: Plain HTTP (IE6 & Vintage Browser Optimized)")
    print(f" Pages: /about, /advertising, /settings, /privacy, /terms, /business")
    print(f" Banners: 5 Larger Rotating Banners with Target Redirects")
    print(f" Copyright: {get_copyright_years()}")
    print("=" * 60)
    print("Press Ctrl+C to stop the server.\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()


if __name__ == "__main__":
    main()
