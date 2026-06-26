#!/usr/bin/env python3
"""Pull all pages for a doc# list via the Worker (UA fix + retry-on-throttle).
Usage: python3 pull_docs.py <doclist.txt> <outdir> [max_pages]
"""
import sys, os, time, urllib.request, urllib.error, ssl

doclist, outdir = sys.argv[1], sys.argv[2]
maxp = int(sys.argv[3]) if len(sys.argv) > 3 else 8
os.makedirs(outdir, exist_ok=True)
KEY = open("/tmp/netr_proxy_key").read().strip()
W = "https://netr-thumb.kaiescobar09.workers.dev"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
CTX = ssl.create_default_context()

def fetch(d, p):
    for att in range(6):
        try:
            req = urllib.request.Request("%s/thumb/%s/%s" % (W, d, p),
                                         headers={"X-Auth": KEY, "User-Agent": UA})
            with urllib.request.urlopen(req, timeout=45, context=CTX) as r:
                up = r.headers.get("X-Upstream-Status", str(r.status)); b = r.read()
                if b[:4] == b"\x89PNG" and len(b) > 5000:
                    return ("ok", b)
                if up == "429":
                    time.sleep(1.5 * (att + 1)); continue
                if up == "500":
                    return ("end", None)
                return ("up" + up, None)
        except urllib.error.HTTPError as e:
            if e.code in (429, 403):
                time.sleep(1.5 * (att + 1)); continue
            return ("e%d" % e.code, None)
        except Exception:
            time.sleep(1.0 * (att + 1))
    return ("retry_out", None)

docs = [d.strip() for d in open(doclist) if d.strip()]
done_docs = 0; pages = 0
for i, d in enumerate(docs):
    for p in range(1, maxp + 1):
        o = os.path.join(outdir, "%s_%s.png" % (d, p))
        if os.path.exists(o):
            pages += 1; continue
        st, b = fetch(d, p)
        if st == "ok":
            open(o, "wb").write(b); pages += 1
        elif st == "end":
            break
    done_docs += 1
    if done_docs % 20 == 0:
        print("pulled %d/%d docs, %d pages" % (done_docs, len(docs), pages), flush=True)
print("DONE pulled %d docs, %d pages -> %s" % (done_docs, pages, outdir), flush=True)
