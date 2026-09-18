import urllib.request
import threading
import time
import socketserver
import http.server
from server import NekichSearchHandler, ThreadingHTTPServer, BANNERS, get_copyright_years

def run_tests():
    port = 8899
    server = ThreadingHTTPServer(("127.0.0.1", port), NekichSearchHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"Test server started on port {port}")
    time.sleep(0.5)

    base_url = f"http://127.0.0.1:{port}"
    cpy = get_copyright_years()

    # 1. Test Copyright on All Pages
    print(f"\n--- Test 1: Dynamic Copyright ({cpy}) ---")
    pages = ["/", "/about", "/advertising", "/settings", "/privacy", "/terms", "/business", "/search?q=test"]
    for p in pages:
        with urllib.request.urlopen(f"{base_url}{p}") as resp:
            assert resp.status == 200
            content = resp.read().decode("utf-8")
            assert cpy in content
            print(f"  Page {p} contains copyright '{cpy}' -> OK")
    print("[OK] Dynamic copyright verified across all pages!")

    # 2. Test CSS Larger Banner Rules
    print("\n--- Test 2: Larger Banner CSS ---")
    with urllib.request.urlopen(f"{base_url}/static/style.css") as resp:
        assert resp.status == 200
        css = resp.read().decode("utf-8")
        assert "width: 350px;" in css or "max-width: 320px;" in css
        print("[OK] Larger banner CSS rules verified!")

    # 3. Test 5 Banners
    print("\n--- Test 3: 5 Rotating Banners ---")
    for i, b in enumerate(BANNERS):
        with urllib.request.urlopen(f"{base_url}/ad/banner.png?b={i}") as resp:
            assert resp.status == 200
            data = resp.read()
            assert len(data) > 1000
            print(f"  Banner {i+1} ({b['name']}): {len(data)} bytes -> OK")
    print("[OK] All 5 banners loaded properly!")

    # Shutdown
    server.shutdown()
    server.server_close()
    print("\n==========================================")
    print(" ALL TESTS PASSED SUCCESSFULLY! ")
    print("==========================================")

if __name__ == "__main__":
    run_tests()
