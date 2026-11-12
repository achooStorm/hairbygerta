"""Run the whole QA suite and write qa/REPORT.md.

    ../hairbygerta-env/venv/Scripts/python.exe qa/run_all.py
    ../hairbygerta-env/venv/Scripts/python.exe qa/run_all.py --only html,licensing
    ../hairbygerta-env/venv/Scripts/python.exe qa/run_all.py --page home,gallery --viewport phone
    ../hairbygerta-env/venv/Scripts/python.exe qa/run_all.py --base https://achoostorm.github.io/hairbygerta/

What it does
  1. Starts every check script of the suite (the seven families listed in FAMILIES below) as its own process,
     all at the same time, with the same Python. --base, --page and --viewport are handed on unchanged.
     Each script starts its own local server on its own free port (unless --base is given).
  2. Reads the report each script wrote to qa/reports/<script name>.json
     ({ok, base, generated, results: [{page, viewport, check, ok, expected, actual, evidence, owner}]}).
     The visual comparison with the Wix reference (qa/visual_compare.py) is retired since 12 November 2026
     (build contract, decision 44, because the site no longer copies the Wix look). It is listed in RETIRED_FAMILIES,
     never started, and the report says so. The script stays in the folder.
  3. Writes qa/REPORT.md (for people) and qa/reports/run_all.json (for programs).
     When a file qa/open-questions.md exists, its text is copied into the report under "Open questions".

A script that is missing, crashes, hangs, or leaves no fresh report counts as a failure of that check family
(owner QA). It never stops the other checks and never crashes this script.

Exit code
  0  every check of every family passed
  2  the licensing check found a restricted file in the site folder (SHA-256 match): hard stop, do not commit
  1  anything else (a failed check, a missing or crashed script, a wrong option)
"""
import concurrent.futures, json, os, re, signal, subprocess, sys, tempfile, threading, time

sys.dont_write_bytecode = True   # no __pycache__ in the site folder (a compiled file carries the path of this computer)
import common  # noqa: E402

# name used on the command line and in the report -> script in this folder. Order = column order in the report.
FAMILIES = (
    ("html", "check_html.py"),
    ("page", "check_page.py"),
    ("content", "check_content.py"),
    ("behavior", "check_behavior.py"),
    ("a11y", "check_a11y.py"),
    ("licensing", "licensing_check.py"),
    ("repo", "check_repo.py"),
)
# Families that are no longer run, by name -> (script, why). The script stays in the folder, --only refuses the name
# with the reason, and the report says why the family is missing.
RETIRED_FAMILIES = {
    "visual": ("visual_compare.py",
               "retired on 12 November 2026 by decision 44 of tools/CONTRACT.md. The site no longer copies the Wix look, "
               "so a measurement against the Wix reference says nothing about whether the pages are right"),
}
ALIASES = {"behaviour": "behavior", "accessibility": "a11y", "axe": "a11y", "compare": "visual", "visual_compare": "visual",
           "license": "licensing", "licence": "licensing", "licensing_check": "licensing", "text": "content",
           "repository": "repo", "folder": "repo", "check_repo": "repo"}
# Families whose report is read from qa/reports/<script name>.json and from nowhere else. qa/visual_compare.py
# used to write a second copy named visual.json. That copy is no longer written and must not be read.
SCRIPT_NAME_ONLY = ("visual",)
# Reports that no script writes any more, by file name without .json -> what to tell the reader when one is still there.
RETIRED_REPORTS = {"visual": "old second copy of visual_compare.json, no longer written or read: delete it",
                   "visual_compare": "last report of the retired visual comparison with Wix (decision 44), no longer written or read"}
# Who fixes what. Failures are listed in this order, any other owner name after these.
OWNERS = ("DESIGN", "PAGES", "INTERACTION", "CONTENT", "SEO", "ASSETS", "DEPLOY", "RUNBOOK", "QA")
SELF = "run_all"
# Requirements that no script tests, printed in every report so that a PASS is not read as covering them.
# (what, how to check it by hand)
NOT_AUTOMATED = (
    ("Visible focus on every link, button and field.",
     "Tab through each page at 1280 px and on a phone and look for the outline on every stop (qa/check_a11y.py runs axe, which does not read outlines)."),
    ("No sideways scroll at every width from 320 to 1920 px.",
     "The suite tests 390 and 1280 px only. Drag the window from 320 px upwards, slowly past 760 and 1100 px, on every page."),
    ("README.md and MIGRATION.md say the right things.",
     "The suite counts the lines of README.md and looks for em dashes, nothing else. Read both: the nine sections of the guide, its sources, and every command typed as written."),
    ("The commit guard really stops a commit.",
     "After the repository exists: python tools/licensing_check.py --install-hook, then try to commit a copy of a restricted photo. The commit has to be refused."),
    ("tools/restricted-hashes.txt covers every restricted file.",
     "Compare the fingerprints of every file in the private photo folder (and inside its zip files) with the list. Decision 30 says how many there are."),
    ("redirects-check.md.",
     "Read it against the Wix sitemaps in the tools folder: every old address is listed with where it ends on the new site. The suite tests two old booking addresses only."),
    ("The phone layout on a real phone.",
     "The suite uses a desktop browser set to the size of an iPhone 13. Open the published address on a real phone once."),
    ("The contact form opens the visitor's mail program.",
     "The suite tests the mailto address the page builds, not what a mail program does with it. Send one message from a phone and one from a computer."),
)
REPORT_MD = os.path.join(common.QA, "REPORT.md")
OPEN_QUESTIONS = os.path.join(common.QA, "open-questions.md")   # optional, copied into the report when it exists
DEFAULT_TIMEOUT = 1800   # seconds one script may run before it is stopped
TAIL_LINES = 30          # how much of a crashed script's output goes into the report
MAX_CELL = 400           # longest expected or actual value shown in a table cell (the JSON keeps the full text)
TOP_VISUAL = 10          # rows in each "biggest differences" table of the visual section (one table per width)
IMAGE_EXT = (".png", ".jpg", ".jpeg", ".webp")
# Width in px of the two viewports every check script knows (common.context_options), for sorting and for labels.
PLAIN_WIDTH = {"desktop": 1280, "phone": 390}

_RUNNING = {}            # pid -> (process, job) of the scripts that are running right now
_LOCK = threading.Lock()


# ---------------------------------------------------------------------------------------------------------------
# Text helpers: no absolute path of this computer may reach the report, and table cells must stay one line.
# ---------------------------------------------------------------------------------------------------------------

_NAME = r"[^\\/\s\"'<>|*?:,;()\[\]{}]"
_TAIL = r"(?!" + _NAME + r")((?:[\\/]+" + _NAME + r"+)*)[\\/]*"


def _rel_to_site(path):
    try:
        return os.path.relpath(path, common.SITE).replace(os.sep, "/")
    except ValueError:      # another drive
        return "<" + os.path.basename(path.rstrip("\\/")) + ">"


def _root_regex(path):
    full = os.path.abspath(path)
    parts = [re.escape(p) for p in re.split(r"[\\/]+", full) if p]
    lead = r"[\\/]+" if full.startswith(("/", "\\")) else ""
    return re.compile(lead + r"[\\/]+".join(parts) + _TAIL, re.I)


def _build_scrubbers():
    roots = {}
    for path, shown in ((common.SITE, ""), (common.ENV, None), (common.RESTRICTED, None), (common.PARENT, None),
                        (sys.prefix, None), (sys.base_prefix, "<python>"), (tempfile.gettempdir(), "<temp>"),
                        (os.path.expanduser("~"), "~")):
        if path and os.path.isabs(path) and len(os.path.abspath(path)) > 3:
            roots.setdefault(os.path.abspath(path), _rel_to_site(path) if shown is None else shown)
    out = [(_root_regex(p), shown) for p, shown in sorted(roots.items(), key=lambda kv: -len(kv[0]))]
    # Any other home folder (a short 8.3 name, another account, a path printed by a tool).
    if os.name == "nt":
        out.append((re.compile(r"[A-Za-z]:[\\/]+Users[\\/]+" + _NAME + r"+" + _TAIL, re.I), "~"))
    else:
        out.append((re.compile(r"(?<![\w.])/(?:home|Users)/" + _NAME + r"+" + _TAIL), "~"))
    return out


_SCRUBBERS = _build_scrubbers()


def scrub(text):
    """Replace every absolute path of this computer by a path relative to the site folder (forward slashes)."""
    text = str(text)
    for regex, shown in _SCRUBBERS:
        def swap(m, shown=shown):
            tail = re.sub(r"[\\/]+", "/", m.group(1) or "")
            if shown == "":
                return tail.lstrip("/") or "."
            return shown + tail
        text = regex.sub(swap, text)
    return text


def as_text(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (list, tuple)) and all(isinstance(x, str) for x in value):
        return ", ".join(value)
    try:
        return json.dumps(value, ensure_ascii=False)
    except Exception:
        return str(value)


def plural(n, one, many=None):
    return "%d %s" % (n, one if n == 1 else (many or one + "s"))


def one_line(value, limit=MAX_CELL):
    s = " ".join(scrub(as_text(value)).split())
    if limit and len(s) > limit:
        s = s[:limit].rstrip() + " [... %d more characters, see the JSON report]" % (len(s) - limit)
    return s


def cell(value, limit=MAX_CELL):
    """One Markdown table cell: one line, no absolute path, nothing that breaks the table or turns into markup."""
    s = one_line(value, limit)
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    for ch in ("\\", "|", "*", "`"):
        s = s.replace(ch, "\\" + ch)
    return s or "-"


def site_rel(path):
    """Path relative to the site folder with forward slashes (may start with ../ for the private folder)."""
    return _rel_to_site(os.path.abspath(path))


def md_link(rel):
    """Show a site-relative path; make it clickable from qa/REPORT.md when the file is inside the site folder."""
    if not rel or rel.startswith(("<", "~")) or re.match(r"^[a-z]+://", rel):
        return cell(rel)
    target = os.path.relpath(os.path.join(common.SITE, rel), common.QA).replace(os.sep, "/")
    return "[%s](%s)" % (cell(rel, 0), target.replace(" ", "%20"))


# ---------------------------------------------------------------------------------------------------------------
# Running the check scripts
# ---------------------------------------------------------------------------------------------------------------

class _Job:
    """Windows job object around one check script. Everything the script starts (its local server, the browser)
    belongs to the job, so a script that hangs is stopped as a whole and nothing is left running afterwards.
    On other systems the script gets its own process group instead. If the job cannot be made, taskkill is used."""

    def __init__(self):
        self.handle = None
        if os.name != "nt":
            return
        try:
            import ctypes
            from ctypes import wintypes

            class Basic(ctypes.Structure):
                _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64), ("PerJobUserTimeLimit", ctypes.c_int64),
                            ("LimitFlags", wintypes.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
                            ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", wintypes.DWORD),
                            ("Affinity", ctypes.c_size_t), ("PriorityClass", wintypes.DWORD),
                            ("SchedulingClass", wintypes.DWORD)]

            class Extended(ctypes.Structure):
                _fields_ = [("BasicLimitInformation", Basic), ("IoInfo", ctypes.c_uint64 * 6),
                            ("ProcessMemoryLimit", ctypes.c_size_t), ("JobMemoryLimit", ctypes.c_size_t),
                            ("PeakProcessMemoryUsed", ctypes.c_size_t), ("PeakJobMemoryUsed", ctypes.c_size_t)]

            k32 = ctypes.WinDLL("kernel32", use_last_error=True)
            ntdll = ctypes.WinDLL("ntdll")
            k32.CreateJobObjectW.restype = wintypes.HANDLE
            k32.CreateJobObjectW.argtypes = (ctypes.c_void_p, wintypes.LPCWSTR)
            k32.SetInformationJobObject.argtypes = (wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD)
            k32.AssignProcessToJobObject.argtypes = (wintypes.HANDLE, wintypes.HANDLE)
            k32.TerminateJobObject.argtypes = (wintypes.HANDLE, wintypes.UINT)
            k32.CloseHandle.argtypes = (wintypes.HANDLE,)
            ntdll.NtResumeProcess.argtypes = (wintypes.HANDLE,)
            handle = k32.CreateJobObjectW(None, None)
            if not handle:
                return
            info = Extended()
            info.BasicLimitInformation.LimitFlags = 0x2000      # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
            if not k32.SetInformationJobObject(handle, 9, ctypes.byref(info), ctypes.sizeof(info)):
                k32.CloseHandle(handle)
                return
            self._k32, self._ntdll, self.handle = k32, ntdll, handle
        except Exception:
            self.handle = None

    def popen_options(self):
        if os.name != "nt":
            return {"start_new_session": True}
        # Started suspended so that it is inside the job before it can start anything itself.
        return {"creationflags": 0x00000004} if self.handle else {}

    def adopt(self, proc):
        if os.name != "nt" or not self.handle:
            return
        try:
            if not self._k32.AssignProcessToJobObject(self.handle, int(proc._handle)):
                self._k32.CloseHandle(self.handle)      # empty job: closing it stops nothing
                self.handle = None
        finally:
            self._ntdll.NtResumeProcess(int(proc._handle))

    def kill(self, proc):
        try:
            if os.name != "nt":
                os.killpg(proc.pid, signal.SIGKILL)
            elif self.handle:
                self._k32.TerminateJobObject(self.handle, 1)
            elif proc.poll() is None:
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL, timeout=30)
        except Exception:
            pass
        try:
            if proc.poll() is None:
                proc.kill()
        except Exception:
            pass

    def close(self, proc):
        """Call when the script has ended: stops whatever it left running."""
        if os.name != "nt":
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except Exception:
                pass
        elif self.handle:
            self._k32.CloseHandle(self.handle)
            self.handle = None


def _signature(path):
    try:
        st = os.stat(path)
        return (st.st_mtime_ns, st.st_size)
    except OSError:
        return None


def report_paths(name, script):
    """Where the report of a check script may be. The rule is qa/reports/<script name>.json; a report named after
    the family (licensing_check.py writes licensing.json) is accepted too, except for the families in
    SCRIPT_NAME_ONLY (the visual report is read from visual_compare.json only)."""
    stems = [os.path.splitext(script)[0]]
    if name not in stems and name not in SCRIPT_NAME_ONLY:
        stems.append(name)
    return [os.path.join(common.REPORTS, s + ".json") for s in stems]


def run_script(name, script, passthrough, timeout, clean, verbose):
    """Run one check script to its end. Never raises: every problem is recorded in the returned dict."""
    reports = report_paths(name, script)
    run = {"name": name, "script": script, "report": reports[0], "missing": False, "timeout": False,
           "exit": None, "seconds": 0.0, "output": "", "fresh": False, "error": "", "limit": timeout}
    path = os.path.join(common.QA, script)
    if not os.path.isfile(path):
        run["missing"] = True
        print("  %-9s missing: qa/%s does not exist" % (name, script), flush=True)
        return run
    started = time.time()
    try:
        if clean:
            # A full run starts from an empty report, so results of an older version of the script cannot linger.
            for report in reports:
                try:
                    os.remove(report)
                except OSError:
                    pass
        before = {report: _signature(report) for report in reports}
        env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
        job = _Job()
        with tempfile.TemporaryFile() as out:
            proc = subprocess.Popen([sys.executable, path] + passthrough, cwd=common.SITE, stdin=subprocess.DEVNULL,
                                    stdout=out, stderr=subprocess.STDOUT, env=env, **job.popen_options())
            with _LOCK:
                _RUNNING[proc.pid] = (proc, job)
            try:
                job.adopt(proc)
                try:
                    run["exit"] = proc.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    run["timeout"] = True
                    job.kill(proc)
                    try:
                        run["exit"] = proc.wait(timeout=30)
                    except subprocess.TimeoutExpired:
                        pass
            finally:
                if proc.poll() is None:     # only when something above went wrong
                    job.kill(proc)
                job.close(proc)
                with _LOCK:
                    _RUNNING.pop(proc.pid, None)
            out.seek(0)
            run["output"] = out.read().decode("utf-8", "replace")
        fresh = [r for r in reports if _signature(r) is not None and _signature(r) != before[r]]
        if fresh:
            run["report"], run["fresh"] = fresh[0], True
        elif not os.path.isfile(run["report"]):
            run["report"] = next((r for r in reports if os.path.isfile(r)), reports[0])
    except Exception as e:      # could not start, could not read the output, ...
        run["error"] = "%s: %s" % (type(e).__name__, e)
    run["seconds"] = time.time() - started
    with _LOCK:
        state = "stopped after %d s (timeout)" % timeout if run["timeout"] else "exit code %s" % run["exit"]
        print("  %-9s %s, %.1f s%s" % (name, state, run["seconds"], "" if run["fresh"] else ", no fresh report"), flush=True)
        if verbose and run["output"].strip():
            print("".join("      | %s\n" % line for line in scrub(run["output"]).splitlines()), end="", flush=True)
    return run


def run_all_scripts(selected, passthrough, timeout, jobs, clean, verbose):
    workers = jobs if jobs and jobs > 0 else len(selected)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        futures = [pool.submit(run_script, name, script, passthrough, timeout, clean, verbose) for name, script in selected]
        try:
            return [f.result() for f in futures]
        except KeyboardInterrupt:
            for f in futures:
                f.cancel()
            with _LOCK:
                running = list(_RUNNING.values())
            for proc, job in running:
                job.kill(proc)
            raise


# ---------------------------------------------------------------------------------------------------------------
# Reading the reports
# ---------------------------------------------------------------------------------------------------------------

def page_slug(value):
    """Slug of the page an entry belongs to, or None when the entry is about the site as a whole."""
    s = str(value if value is not None else "").strip()
    if not s:
        return None
    low = s.lower()
    if low in common.PAGES:
        return low
    p = re.sub(r"^https?://[^/]+", "", low).split("?")[0].split("#")[0]
    if not p.startswith("/") and "/" not in p and "." not in p:
        return None                     # a plain word such as "site" or "all"
    if p.startswith(common.PREFIX):
        p = p[len(common.PREFIX):]
    p = p.lstrip("/")
    if p.endswith("index.html"):
        p = p[:-len("index.html")]
    for slug, rel in common.PAGES.items():
        if p == rel or (rel and p == rel.rstrip("/")):
            return slug
    return None


# A viewport name with a width, as qa/visual_compare.py writes them: desktop-1265, desktop-1440, desktop-1920.
_WIDTH_RE = re.compile(r"^(desktop|phone)[\s_-]*w?(\d{3,4})(?:\s*px)?$")


def viewport_parts(value):
    """-> (kind, name) of a "viewport" value in a report.

    kind  "desktop" or "phone": what --viewport selects and what the two screenshot columns show.
          None for a check that needs no browser ("-") and for any name this script does not know.
    name  what the report shows: the kind itself for the two viewports every script uses (1280 x 900, iPhone 13),
          or the kind with a width for another width of the same layout, for example desktop-1440."""
    low = str(value if value is not None else "").strip().lower()
    if low in common.VIEWPORTS:
        return low, low
    if low in ("mobile", "iphone", "iphone 13"):
        return "phone", "phone"
    m = _WIDTH_RE.match(low)
    if m:
        return m.group(1), "%s-%s" % (m.group(1), m.group(2))
    return None, None


def viewport_name(value):
    """desktop or phone (for desktop-1440: desktop), or None when the value names no viewport."""
    return viewport_parts(value)[0]


def viewport_width(name):
    """The width in px a viewport name carries (desktop-1440 -> 1440), or None for a name without a width."""
    m = re.search(r"-(\d{3,4})$", viewport_parts(name)[1] or "")
    return int(m.group(1)) if m else None


def viewport_rank(name):
    """Sort key: desktop widths from narrow to wide (desktop-1265, desktop, desktop-1440, desktop-1920), then phone,
    then any other name, then "-" (no viewport)."""
    kind = viewport_name(name)
    if kind is None:
        return (3 if str(name).strip() in ("", "-") else 2, 0, str(name))
    return (0 if kind == "desktop" else 1, viewport_width(name) or PLAIN_WIDTH[kind], str(name))


def viewport_label(name):
    """A viewport name said in words, for the visual section. "" for a name this script does not know."""
    kind = viewport_name(name)
    if kind is None:
        return "a check without a viewport" if str(name).strip() in ("", "-") else ""
    width = viewport_width(name)
    if width:
        return "%s layout, %d px wide" % (kind, width)
    return "desktop layout, 1280 px wide" if kind == "desktop" else "phone layout, iPhone 13, 390 px wide"


def normalise(raw, family):
    slug = page_slug(raw.get("page"))
    vp, shown = viewport_parts(raw.get("viewport"))
    return {"family": family, "slug": slug, "page": slug or as_text(raw.get("page")).strip() or "site",
            "vp": vp, "viewport": shown or as_text(raw.get("viewport")).strip() or "-",
            "check": as_text(raw.get("check")).strip() or "(check without a name)", "ok": bool(raw.get("ok")),
            "expected": raw.get("expected"), "actual": raw.get("actual"), "evidence": raw.get("evidence"),
            "owner": as_text(raw.get("owner")).strip().upper() or "UNASSIGNED", "raw": raw}


def load_report(path):
    """-> (document, entries, problem). problem is a text when the file is not a report in the shared format."""
    try:
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
    except Exception as e:
        return None, [], "cannot read %s: %s: %s" % (site_rel(path), type(e).__name__, e)
    if not isinstance(doc, dict) or not isinstance(doc.get("results"), list):
        return None, [], "%s is not in the shared format (an object with a results list)" % site_rel(path)
    bad = [r for r in doc["results"] if not isinstance(r, dict)]
    if bad:
        return None, [], "%s has %d results that are not objects" % (site_rel(path), len(bad))
    return doc, doc["results"], ""


def in_scope(entry, pages, viewports):
    """Does the entry belong to the pages and viewports of this run? A width such as desktop-1440 belongs to desktop."""
    if entry["slug"] is not None and entry["slug"] not in pages:
        return False
    if entry["vp"] is not None and entry["vp"] not in viewports:
        return False
    return True


def judge(run, pages, viewports, full_run):
    """Turn one script run plus its report into the family result used everywhere below."""
    fam = dict(run, ran=True, doc=None, entries=[], failures=[], problems=[], base="", generated="")
    stem_json = site_rel(run["report"])
    if run["missing"]:
        fam["problems"].append("qa/%s does not exist" % run["script"])
    elif run["error"]:
        fam["problems"].append("could not run qa/%s: %s" % (run["script"], run["error"]))
    else:
        if run["timeout"]:
            fam["problems"].append("stopped after the time limit of %d seconds, the script did not finish%s"
                                   % (run["limit"], "" if run["fresh"] else " and wrote no report"))
        elif not run["fresh"]:
            fam["problems"].append("exit code %s and no fresh %s was written" % (run["exit"], stem_json))
        if run["fresh"]:
            doc, raw, problem = load_report(run["report"])
            if problem:
                fam["problems"].append(problem)
            else:
                everything = [normalise(r, run["name"]) for r in raw]
                fam["doc"] = doc
                fam["base"] = as_text(doc.get("base"))
                fam["generated"] = as_text(doc.get("generated"))
                fam["entries"] = [e for e in everything if in_scope(e, pages, viewports)]
                fam["failures"] = [e for e in fam["entries"] if not e["ok"]]
                any_failure = any(not e["ok"] for e in everything)
                allowed = (0, 1, 2) if run["name"] == "licensing" else (0, 1)
                if not run["timeout"]:
                    if run["exit"] not in allowed:
                        fam["problems"].append("exit code %s (0 or 1 expected), the script probably crashed" % run["exit"])
                    elif run["exit"] != 0 and not any_failure:
                        fam["problems"].append("exit code %s but %s lists no failed check, the script probably crashed "
                                               "after writing it" % (run["exit"], stem_json))
                    elif run["exit"] == 0 and fam["failures"]:
                        fam["problems"].append("exit code 0 although %s lists %s (exit code 1 expected)"
                                               % (stem_json, plural(len(fam["failures"]), "failed check")))
                if doc.get("ok") is False and not any_failure:
                    fam["problems"].append("%s says ok=false but lists no failed check" % stem_json)
                if full_run and not everything:
                    fam["problems"].append("%s has no results: nothing was checked" % stem_json)
    if run["missing"]:
        fam["status"] = "missing"
    elif run["timeout"]:
        fam["status"] = "timeout"
    elif fam["doc"] is None:
        fam["status"] = "crashed"
    elif fam["problems"]:
        fam["status"] = "problem"
    elif fam["failures"]:
        fam["status"] = "failed"
    else:
        fam["status"] = "passed"
    # A problem with the script itself is a failed check too, owned by QA.
    fam["harness"] = [{"family": run["name"], "slug": None, "page": "site", "vp": None, "viewport": "-",
                       "check": "qa/%s runs and reports" % run["script"], "ok": False,
                       "expected": "the script runs to its end, exits with 0 or 1 and writes a fresh %s in the shared format" % stem_json,
                       "actual": p, "evidence": 'see "Scripts that did not run cleanly" below', "owner": "QA", "raw": {}}
                      for p in fam["problems"]]
    return fam


def not_run(name, script):
    reports = report_paths(name, script)
    fam = {"name": name, "script": script, "report": next((r for r in reports if os.path.isfile(r)), reports[0]), "ran": False,
           "status": "not run", "doc": None, "entries": [], "failures": [], "problems": [], "harness": [], "exit": None,
           "seconds": 0.0, "output": "", "base": "", "generated": "", "last": ""}
    if os.path.isfile(fam["report"]):
        doc, raw, problem = load_report(fam["report"])
        if not problem:
            bad = sum(1 for r in raw if not r.get("ok"))
            fam["last"] = "last report on disk (%s): %s" % (as_text(doc.get("generated")) or "no time", "%d failed" % bad if bad else "pass")
    return fam


# ---------------------------------------------------------------------------------------------------------------
# Screenshots, licensing numbers, visual differences
# ---------------------------------------------------------------------------------------------------------------

_IMG_RE = re.compile(r"[^\s\"'<>|,;()\[\]{}]+\.(?:png|jpe?g|webp)", re.I)
_VP_WORDS = {"desktop": "desktop", "phone": "(?:phone|mobile|iphone)"}


def _strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from _strings(v)
    elif isinstance(value, (list, tuple)):
        for v in value:
            yield from _strings(v)


def evidence_images(entry):
    """Screenshots and comparison images named in an entry's evidence that really exist -> list of (site-relative
    path, absolute path). Only QA output counts (the qa folder and the private folder), not a site image a check mentions."""
    found = []
    for text in _strings(entry.get("evidence")):
        for token in _IMG_RE.findall(text):
            token = token.strip("`")
            roots = (common.SITE, common.QA, common.SHOTS, common.PRIVATE)
            candidates = [token] if os.path.isabs(token) else [os.path.join(root, token) for root in roots]
            for c in candidates:
                if os.path.isfile(c) and (_inside(c, common.QA) or _inside(c, common.PRIVATE)):
                    hit = (site_rel(c), os.path.abspath(c))
                    if hit not in found:
                        found.append(hit)
                    break
    return found


_EVIDENCE_KEYS = ("file", "line", "selector", "element", "url", "state", "rule", "note")


def _brief(value):
    """Nested evidence as one readable line: 'key: value; key: first, second, third (+4 more)'. Empty parts are left out."""
    if isinstance(value, dict):
        return "; ".join("%s: %s" % (k, _brief(v)) for k, v in value.items() if v not in (None, "", [], {}, 0, False))
    if isinstance(value, (list, tuple)):
        more = len(value) - 3
        return ", ".join(_brief(v) for v in value[:3]) + (" (+%d more)" % more if more > 0 else "")
    return as_text(value)


def evidence_text(evidence):
    """Short readable form of an evidence value (scripts give a text, a list or an object with details)."""
    if isinstance(evidence, dict):
        picked = {k: evidence[k] for k in _EVIDENCE_KEYS if evidence.get(k) not in (None, "", [], {})}
        text = _brief(picked or evidence)
    else:
        text = _brief(evidence)
    shown = {os.path.basename(rel) for rel, _full in evidence_images({"evidence": evidence})}
    rest = _IMG_RE.sub(lambda m: "" if os.path.basename(m.group(0).replace("\\", "/")) in shown else m.group(0), text)
    return text if re.search(r"\w", rest) else ""       # nothing but screenshot paths: they are shown as links instead


def list_images(folder):
    found = []
    for where, _dirs, files in os.walk(folder):
        for f in files:
            if f.lower().endswith(IMAGE_EXT):
                found.append(os.path.join(where, f))
    return found


def image_by_name(folder, images, slug, viewport):
    """The image in a folder whose name says it shows this page in this viewport, for example home-phone.png or
    visual/home-phone-full.png. A picture of the page as it loads wins over one of a state (menu open, lightbox open).

    viewport is a name as in the reports. A file name may carry a width right after the viewport word
    (home-desktop-1440-full.png, home-desktop-w1440.png). Such a picture is taken for desktop-1440 only; for the
    plain names desktop and phone it is left out, so that the 1280 px column never shows another width."""
    vp = viewport_name(viewport)
    if vp is None:
        return None
    want = viewport_width(viewport) or PLAIN_WIDTH[vp]
    word = _VP_WORDS[vp]
    sep = r"[-_. /]"
    width = r"(?P<t%%d>%s?w?(?P<w%%d>\d{3,4})(?:px)?(?=%s|$))?" % (sep, sep)
    pattern = re.compile(r"(?:^|%s)(?:%s%s%s%s|%s%s%s%s)(?:%s|$)" % (sep, re.escape(slug), sep, word, width % (1, 1),
                                                                  word, width % (2, 2), sep, re.escape(slug), sep), re.I)
    plain = re.compile(r"(?:^|%s)%s%s%s(?:%sfull(?:page)?)?$" % (sep, re.escape(slug), sep, word, sep), re.I)
    preferred = ["%s-%s" % (slug, vp), "%s-%s-full" % (slug, vp), "%s_%s" % (slug, vp), "%s_%s_full" % (slug, vp)]
    best = None
    for path in images:
        rel = os.path.relpath(path, folder).replace(os.sep, "/")
        stem = os.path.splitext(rel)[0].lower()
        m = pattern.search(stem)
        if not m:
            continue
        token = 1 if m.group("w1") else 2 if m.group("w2") else 0
        if (int(m.group("w%d" % token)) if token else PLAIN_WIDTH[vp]) != want:
            continue                        # the same page at another width
        if token:                           # rank it by its name without the width
            stem = stem[:m.start("t%d" % token)] + stem[m.end("t%d" % token):]
        if stem in preferred:
            rank = 0                        # right in the folder, named after the page and the viewport
        elif os.path.basename(stem) in preferred:
            rank = 1
        elif plain.search(stem):
            rank = 2                        # some prefix, nothing after the viewport: the page as it loads
        else:
            rank = 3                        # a state of the page
        key = (rank, len(stem), -os.path.getmtime(path))
        if best is None or key < best[0]:
            best = (key, path)
    return best[1] if best else None


def _most_named(slug, viewport, entries, folder):
    """The image inside a folder that the checks of one page in one viewport name most often as evidence, or None."""
    named = {}
    for e in entries:
        if e["slug"] == slug and e["viewport"] == viewport:
            for _rel, full in evidence_images(e):
                if _inside(full, folder):
                    named[full] = named.get(full, 0) + 1
    return max(named, key=named.get) if named else None


def _shown(path, run_started):
    if path is None:
        return ""
    note = "" if os.path.getmtime(path) >= run_started - 2 else " (from an earlier run)"
    return md_link(site_rel(path)) + note


def page_screenshot(slug, viewport, shots, entries, run_started):
    """Screenshot of one page in one viewport (a name as in the reports, desktop-1440 is its own viewport here):
    the one a check says it saved as the page screenshot, else the best match by file name in qa/screenshots,
    else any screenshot a check of that page in that viewport named."""
    path = None
    for e in entries:
        if e["slug"] == slug and e["viewport"] == viewport and "screenshot" in e["check"].lower():
            path = next((full for _rel, full in evidence_images(e) if _inside(full, common.SHOTS)), None)
            if path:
                break
    if path is None:
        path = image_by_name(common.SHOTS, shots, slug, viewport)
    if path is None:
        path = _most_named(slug, viewport, entries, common.SHOTS)
    return _shown(path, run_started)


def side_by_side(slug, viewport, private, entries, run_started):
    """The picture of our page next to the Wix reference for one page in one viewport: the best match by file name
    in the private folder, else the one the checks of that page in that viewport name. It shows the live Wix site,
    so it is only ever linked, never copied."""
    path = image_by_name(common.PRIVATE, private, slug, viewport)
    if path is None:
        path = _most_named(slug, viewport, entries, common.PRIVATE)
    return _shown(path, run_started)


def _inside(path, folder):
    try:
        return os.path.commonpath([os.path.abspath(path), os.path.abspath(folder)]) == os.path.abspath(folder)
    except ValueError:      # another drive
        return False


def failure_evidence(entry, page_shots):
    """Last column of a failed check: what the check named as evidence, and a screenshot path (the one the check
    saved, else the screenshot of that page in that viewport)."""
    parts = []
    text = evidence_text(entry.get("evidence")).strip()
    items = (entry.get("raw") or {}).get("items")       # some scripts list every offending file or element there
    if isinstance(items, list) and items:
        text = (text + ". " if text else "") + "Details: " + _brief(items)
    if text:
        parts.append(cell(text, 300))
    images = evidence_images(entry)
    if images:
        parts.append(", ".join(md_link(rel) for rel, _full in images[:3]))
    elif entry["slug"]:
        if entry["vp"] and entry["viewport"] != entry["vp"]:
            # a check at another width (desktop-1440): its own screenshot or none, never one of another width
            shot = page_shots.get((entry["slug"], entry["viewport"]))
        else:
            shot = page_shots.get((entry["slug"], entry["vp"] or "desktop")) or page_shots.get((entry["slug"], "phone"))
        if shot:
            parts.append(shot)
    return " ".join(parts) or "-"


def _dig(doc, *path):
    for key in path:
        if not isinstance(doc, dict):
            return None
        doc = doc.get(key)
    return doc


def _count(value):
    """A count from a report: a number, or the length of a list. None for anything else."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, list):
        return len(value)
    return None


def _find_count(doc, pattern, depth=2):
    """First count (top level first, then nested objects) whose key matches the pattern."""
    nested = []
    for key, value in doc.items():
        if key == "results":
            continue
        if re.search(pattern, str(key), re.I) and _count(value) is not None:
            return _count(value)
        if isinstance(value, dict):
            nested.append(value)
    if depth > 1:
        for value in nested:
            n = _find_count(value, pattern, depth - 1)
            if n is not None:
                return n
    return None


def _count_in_text(entries, pattern):
    for e in entries:
        for field in ("actual", "evidence", "expected"):
            m = re.search(pattern, as_text(e.get(field)), re.I)
            if m:
                return int(next(g for g in m.groups() if g).replace(",", ""))
    return None


# The name of a check that compares hashes with the restricted files, for example hash_match.
_HASH_RE = re.compile(r"hash[\s_-]*match|match.*(?:hash|sha-?256)|(?:hash|sha-?256).*(?:match|restricted)|restricted.*(?:hash|sha-?256)", re.I)


def licensing_summary(fam):
    """Numbers for the licensing section and the hard-stop decision (a SHA-256 match with a restricted file).
    Reads what qa/licensing_check.py writes (files_hashed, restricted_hashes, images_checked, images_by_class,
    counts, matches, verdict) and, so that a renamed key cannot hide a match, also looks at the failed checks
    and at the exit code."""
    info = {"files": None, "files_detail": "", "restricted": None, "images": None, "images_detail": "", "matches": None,
            "match_rows": [], "hash_failures": [], "hard_stop": False, "why": "", "own_report": "", "owner_photos": 0}
    if not fam or not fam["ran"]:
        return info
    doc = fam["doc"] or {}
    entries = [normalise(r, "licensing") for r in doc.get("results", [])] if fam["doc"] else []

    def first(*values):
        return next((v for v in values if v is not None), None)

    # The keys qa/licensing_check.py writes come first, then other spellings, then the text of its checks.
    counts = doc.get("counts") if isinstance(doc.get("counts"), dict) else doc.get("hashed")
    site = _dig(counts, "site")
    classes = doc.get("images_by_class")
    by_class = isinstance(classes, dict) and bool(classes) and all(_count(v) is not None for v in classes.values())
    info["files"] = first(
        _count(doc.get("files_hashed")), _count(_dig(counts, "site", "files")),
        _find_count(doc, r"^(site_)?files?_(hashed|checked|scanned|compared)$|^hashed_files$|^(site|working|repo)_files$"),
        _count_in_text(entries, r"([\d,]+)\s+(?:\w+\s+)?files?\s+(?:were\s+)?hashed|SHA-?256 of [^()]*\(([\d,]+) files?"))
    if isinstance(site, dict):
        info["files_detail"] = ", ".join("%d %s" % (v, str(k).replace("_", " ")) for k, v in site.items()
                                         if k != "files" and _count(v) is not None and not isinstance(v, list))
    info["restricted"] = first(
        _count(doc.get("restricted_hashes")), _count(_dig(counts, "restricted", "different_hashes_compared")),
        _find_count(doc, r"^restricted_(hashes|sha256)$|hashes_compared$"),
        _count_in_text(entries, r"([\d,]+)\s+(?:different\s+)?restricted\s+hashes"))
    info["images"] = first(
        _count(doc.get("images_checked")), sum(_count(v) for v in classes.values()) if by_class else None,
        _count(doc.get("images")) if isinstance(doc.get("images"), list) else None,
        _find_count(doc, r"^images?_(checked|tested|scanned)$|^pixels?_checked$"),
        _count_in_text(entries, r"([\d,]+)\s+(?:\w+\s+)?images?\s+(?:were\s+)?(?:checked|tested|scanned)"))
    if by_class:
        info["images_detail"] = ", ".join("%d %s" % (_count(v), k) for k, v in classes.items() if _count(v))
        # photos the owner saved over a placeholder, accepted because the manifest records them (build contract, decision 27)
        info["owner_photos"] = _count(classes.get("owner-photo")) or 0
    info["matches"] = first(
        _count(doc.get("matches")), _count(_dig(doc, "last_run", "matches")),
        _find_count(doc, r"^(hash_|sha256_|restricted_)?match(es|_count)?$"))

    info["hash_failures"] = [e for e in entries if not e["ok"] and _HASH_RE.search(e["check"])]
    if isinstance(doc.get("matches"), list):
        for m in doc["matches"]:
            if isinstance(m, dict):
                info["match_rows"].append((as_text(m.get("site") or m.get("file") or m.get("path")), as_text(m.get("restricted"))))
            else:
                info["match_rows"].append((as_text(m), ""))
    if not info["match_rows"]:
        for e in info["hash_failures"]:
            items = e["raw"].get("items")
            info["match_rows"] += [(as_text(i), "") for i in items] if isinstance(items, list) else [(as_text(e["actual"]), "")]

    usage_error = bool(re.search(r"^usage:", fam.get("output") or "", re.I | re.M))
    if info["matches"]:
        info["hard_stop"], info["why"] = True, "%s in the licensing report" % plural(info["matches"], "SHA-256 match", "SHA-256 matches")
    elif "match" in as_text(doc.get("verdict")).lower():
        info["hard_stop"], info["why"] = True, "the licensing report says %s" % as_text(doc.get("verdict"))
    elif info["hash_failures"]:
        info["hard_stop"], info["why"] = True, "%s in the licensing report" % plural(len(info["hash_failures"]), "failed hash check")
    elif fam.get("exit") == 2 and not usage_error:
        info["hard_stop"], info["why"] = True, "qa/%s ended with exit code 2, its code for a hash match" % fam["script"]
    if info["matches"] is None and info["hard_stop"]:
        info["matches"] = len(info["match_rows"]) or None
    elif info["matches"] is None and any(e["ok"] and _HASH_RE.search(e["check"]) for e in entries):
        info["matches"] = 0         # no count in the report, but its hash check ran and passed
    own = os.path.splitext(fam["report"])[0] + ".md"
    if fam.get("fresh") and os.path.isfile(own):
        info["own_report"] = site_rel(own)
    return info


_DIFF_KEYS = ("diff", "delta", "difference", "diff_px", "delta_px", "max_diff", "max_delta", "off_by", "distance",
              "mismatch", "diff_pct", "diff_percent", "percent", "score")


def _numbers(value):
    s = re.sub(r"#[0-9a-fA-F]{3,8}\b", " ", as_text(value))
    return [float(x) for x in re.findall(r"(?<![\w.])-?\d+(?:\.\d+)?", s)]


def difference(entry):
    """How far off a visual check is, for sorting: a number the script gave, else the largest gap between the
    numbers in expected and actual. None when it cannot be told."""
    raw = entry.get("raw") or {}
    for key in _DIFF_KEYS:
        v = raw.get(key)
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            return abs(float(v))
    a, b = _numbers(entry.get("expected")), _numbers(entry.get("actual"))
    if a and len(a) == len(b):
        return max(abs(x - y) for x, y in zip(a, b))
    return None


def fmt_number(n):
    if n is None:
        return "-"
    return ("%.2f" % n).rstrip("0").rstrip(".")


# ---------------------------------------------------------------------------------------------------------------
# Writing qa/REPORT.md
# ---------------------------------------------------------------------------------------------------------------

def owner_order(owners):
    known = [o for o in OWNERS if o in owners and o != "QA"]
    other = sorted(o for o in owners if o not in OWNERS)
    return known + other + (["QA"] if "QA" in owners else [])


def table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join(" --- " for _ in header) + "|"]
    out += ["| " + " | ".join(row) + " |" for row in rows]
    return out


def status_word(fam):
    if fam["status"] == "passed":
        return "pass"
    if fam["status"] == "failed":
        return "**%d failed**" % len(fam["failures"])
    if fam["status"] == "not run":
        return "not run"
    if fam["status"] == "problem":
        return "**%d failed, script problem**" % len(fam["failures"]) if fam["failures"] else "**script problem**"
    return "**%s**" % fam["status"]        # missing, crashed, timeout


def build_markdown(suite):
    families, pages, viewports = suite["families"], suite["pages"], suite["viewports"]
    ran = [f for f in families if f["ran"]]
    failures = suite["failures"]
    lic = suite["licensing"]
    lic_fam = next((f for f in families if f["name"] == "licensing"), None)
    L = []
    w = L.append

    w("# QA report: Hair & Makeup by Gerta")
    w("")
    w("Written by `qa/run_all.py`. Every path in this report is relative to the site folder.")
    w("")
    w("- Address tested: %s" % suite["address"])
    w("- Time: %s, the run took %.0f seconds" % (suite["time"], suite["seconds"]))
    w("- Pages: %s" % ("all %d" % len(pages) if suite["all_pages"] else ", ".join(pages)))
    w("- Viewports: %s" % ", ".join("%s (%s)" % (v, "1280 x 900" if v == "desktop" else "iPhone 13") for v in viewports))
    vis = next((f for f in families if f["name"] == "visual"), None)
    vis_widths = sorted({e["viewport"] for e in vis["entries"] if e["vp"]}, key=viewport_rank) if vis else []
    if any(v not in common.VIEWPORTS for v in vis_widths):
        w("- Widths of the visual comparison: %s" % ", ".join("%s (%s)" % (v, viewport_label(v)) for v in vis_widths))
    w("- Checks run: %s" % ", ".join(f["name"] for f in ran))
    skipped = [f["name"] for f in families if not f["ran"]]
    if skipped:
        w("- Checks NOT run this time: %s" % ", ".join(skipped))
    if suite.get("open_questions") is not None:
        w("- Open questions for the owner: see the section Open questions below")
    w("")
    if suite["exit_code"] == 0:
        w("**Result: PASS.** Every check of every family that was run passed (exit code 0).")
    elif suite["exit_code"] == 2:
        w("**Result: HARD STOP (exit code 2).** The licensing check found a file in the site folder that is identical to a "
          "restricted, Wix-only file (%s). Do not commit. Do not push. Tell the owner. Details under Licensing below." % lic["why"])
    else:
        bad = [f["name"] for f in ran if f["status"] != "passed"]
        w("**Result: FAIL (exit code 1).** %s in %d of %s (%s)."
          % (plural(len(failures), "failed check"), len(bad), plural(len(ran), "check family", "check families"), ", ".join(bad)))
    if lic_fam is None or not lic_fam["ran"]:
        w("")
        w("Licensing was not checked in this run. Run the full suite before any commit.")
    elif lic_fam["status"] != "passed" and suite["exit_code"] != 2:
        w("")
        w("**The licensing check did not pass or did not finish, so licensing is NOT verified. Do not commit.**")
    w("")

    # ---- check families
    w("## Check families")
    w("")
    rows = []
    for f in families:
        note = f.get("last", "") if not f["ran"] else (f["base"] or "-")
        rows.append([f["name"], "`qa/%s`" % f["script"], status_word(f), str(len(f["entries"])) if f["ran"] else "-",
                     str(len(f["failures"]) + len(f["harness"])) if f["ran"] else "-",
                     "-" if f["exit"] is None else str(f["exit"]), "%.0f" % f["seconds"] if f["ran"] else "-", cell(note)])
    L += table(["Family", "Script", "Result", "Checks", "Failed", "Exit code", "Seconds", "Address it tested"], rows)
    w("")

    # ---- pages
    w("## Pages")
    w("")
    w("One row per page. A check column says `pass`, or how many checks of that family failed on that page "
      "(all viewports together; the visual column counts every width it compares). `-` means the family has no "
      "check for that row. The screenshot columns show the page at 1280 px and on the phone.")
    w("")
    head = ["Page", "Desktop screenshot", "Phone screenshot"] + [f["name"] for f in families]

    def family_cell(f, rows_of):
        if not f["ran"]:
            return "not run"
        if f["doc"] is None:
            return "**%s**" % f["status"]
        bad = sum(1 for e in rows_of if not e["ok"])
        if bad:
            return "**%d failed**" % bad
        return "pass" if rows_of else "-"

    rows = []
    for slug in pages:
        row = [slug]
        for vp in ("desktop", "phone"):
            row.append((suite["page_shots"].get((slug, vp)) or "(none)") if vp in viewports else "not run")
        for f in families:
            row.append(family_cell(f, [e for e in f["entries"] if e["slug"] == slug]))
        rows.append(row)
    row = ["(whole site)", "-", "-"]
    for f in families:
        row.append(family_cell(f, [e for e in f["entries"] if e["slug"] is None] + f["harness"]))
    rows.append(row)
    L += table(head, rows)
    w("")

    # ---- open questions (only when qa/open-questions.md exists)
    if suite.get("open_questions") is not None:
        w("## Open questions")
        w("")
        w("Copied from %s. Not a result of a check and not counted in the result above." % md_link(site_rel(OPEN_QUESTIONS)))
        w("")
        L.extend(suite["open_questions"].split("\n"))
        w("")

    # ---- licensing
    w("## Licensing")
    w("")
    if lic_fam is None or not lic_fam["ran"]:
        w("Not run this time.")
    elif lic_fam["doc"] is None:
        w("**No result from `qa/%s`:** %s. Licensing is NOT verified." % (lic_fam["script"], "; ".join(one_line(p) for p in lic_fam["problems"]) or "no report"))
    else:
        def shown(n, detail=""):
            if n is None:
                return "not reported by the script"
            return "%d%s" % (n, " (%s)" % cell(detail, 300) if detail else "")
        if lic["hard_stop"]:
            w("**HARD STOP: a file of the site is identical to a restricted file** (%s). "
              "No commit, no push, tell the owner." % lic["why"])
        elif lic_fam["status"] == "passed" and lic["matches"] == 0:
            if lic["owner_photos"]:
                w("**Pass: zero matches.** No file of the site is identical to a restricted file. Every image that is not on "
                  "the allowed list is a placeholder or one of the %s that image-manifest.json records as the owner's own "
                  "(listed in the script's own report below). A hash proves that such a file is not one of the restricted "
                  "files, it cannot prove whose picture it is: a person looks at each new owner photo once."
                  % plural(lic["owner_photos"], "image file", "image files"))
            else:
                w("**Pass: zero matches.** No file of the site is identical to a restricted file, and every image that is "
                  "not on the allowed list is a placeholder.")
        elif lic_fam["status"] == "passed":
            w("**Pass.** Every licensing check passed. The script did not report a count of hash matches.")
        else:
            w("**Fail.** No hash match was reported, but %s failed (listed below and under their owner)."
              % plural(len(lic_fam["failures"]) + len(lic_fam["harness"]), "licensing check"))
        w("")
        w("- Site files hashed: %s" % shown(lic["files"], lic["files_detail"] and "plus " + lic["files_detail"]))
        w("- Different restricted hashes they were compared with: %s" % shown(lic["restricted"]))
        w("- Images checked: %s" % shown(lic["images"], lic["images_detail"]))
        w("- SHA-256 matches with a restricted file: %s" % shown(lic["matches"]))
        w("- Licensing checks in the report: %d, failed: %d" % (len(lic_fam["entries"]), len(lic_fam["failures"])))
        if lic["own_report"]:
            w("- The script's own, longer report: %s" % md_link(lic["own_report"]))
        if lic["hard_stop"] and lic["match_rows"]:
            w("")
            w("Matches:")
            w("")
            L += table(["File in the site folder", "Identical to (restricted)"], [[cell(a), cell(b)] for a, b in lic["match_rows"][:50]])
            if len(lic["match_rows"]) > 50:
                w("")
                w("And %d more, see %s." % (len(lic["match_rows"]) - 50, cell(site_rel(lic_fam["report"]))))
        if lic_fam["failures"]:
            w("")
            w("Failed licensing checks:")
            w("")
            L += table(["Check", "File or page", "Expected", "Actual", "Evidence", "Owner"],
                       [[cell(e["check"]), cell(e["page"]), cell(e["expected"]), cell(e["actual"]), failure_evidence(e, {}), e["owner"]]
                        for e in lic_fam["failures"]])
    w("")

    # ---- visual comparison
    w("## Visual comparison with the Wix reference")
    w("")
    if vis is None and "visual" in RETIRED_FAMILIES:
        w("Not run. `qa/%s` was %s." % RETIRED_FAMILIES["visual"])
    elif vis is None or not vis["ran"]:
        w("Not run this time.")
    elif vis["doc"] is None:
        w("**No result from `qa/%s`:** %s." % (vis["script"], "; ".join(one_line(p) for p in vis["problems"]) or "no report"))
    else:
        ranked = sorted(((difference(e), e) for e in vis["entries"]), key=lambda t: (t[1]["ok"], t[0] is None, -(t[0] or 0)))
        # One group per viewport name of the report: every width the script compared, and "-" for a check without one.
        widths = sorted({e["viewport"] for e in vis["entries"]}, key=viewport_rank)
        per_width = {name: [(d, e) for d, e in ranked if e["viewport"] == name] for name in widths}

        def biggest(pairs):
            return max((d for d, _e in pairs if d is not None), default=None)

        w("%s, %d outside the tolerance." % (plural(len(vis["entries"]), "comparison"), len(vis["failures"])))
        w("")
        if widths:
            rows = []
            for name in widths:
                bad = [(d, e) for d, e in per_width[name] if not e["ok"]]
                rows.append([cell(name), viewport_label(name) or "-", str(len(per_width[name])), "**%d**" % len(bad) if bad else "0",
                             str(len({e["slug"] for _d, e in bad if e["slug"]})), fmt_number(biggest(bad))])
            w("One row per width that was compared:")
            w("")
            L += table(["Viewport", "What it is", "Comparisons", "Outside tolerance", "Pages with a difference", "Biggest difference (px)"], rows)
            w("")
        rows = []
        for slug in pages:
            for name in widths:
                mine = [(d, e) for d, e in per_width[name] if e["slug"] == slug]
                bad = [(d, e) for d, e in mine if not e["ok"]]
                if not bad:
                    continue
                top = biggest(bad)
                rows.append((len(bad), top or 0, [slug, cell(name), str(len(mine)), "**%d**" % len(bad), fmt_number(top),
                                                  suite["side_shots"].get((slug, name)) or "-"]))
        if rows:
            rows.sort(key=lambda r: (-r[1], -r[0]))
            w("Pages with something outside the tolerance, one row per page and width, biggest difference first. The "
              "side-by-side images show the live Wix site next to ours, so they are kept outside the site folder and are "
              "never committed.")
            w("")
            L += table(["Page", "Viewport", "Comparisons", "Outside tolerance", "Biggest difference (px)", "Side by side (private)"],
                       [r[2] for r in rows])
            w("")
        if vis["failures"]:
            w("The biggest differences follow width by width, at most %d per width. Every difference is also in the list "
              "by owner below." % TOP_VISUAL)
            for name in widths:
                bad = [(d, e) for d, e in per_width[name] if not e["ok"]]
                if not bad:
                    continue
                if viewport_name(name) is None:
                    where = "in checks without a viewport" if name == "-" else "at %s" % cell(name)
                else:
                    where = "at %s (%s)" % (name, viewport_label(name))
                w("")
                w("### Biggest differences %s" % where)
                w("")
                w("%d of the %s outside the tolerance here, biggest first:" % (min(len(bad), TOP_VISUAL), plural(len(bad), "comparison")))
                w("")
                L += table(["#", "Page", "What", "Expected (Wix)", "Actual (ours)", "Difference (px)", "Evidence", "Owner"],
                           [[str(i + 1), cell(e["page"]), cell(e["check"]), cell(e["expected"], 160), cell(e["actual"], 160),
                             fmt_number(d), failure_evidence(e, suite["page_shots"]), e["owner"]] for i, (d, e) in enumerate(bad[:TOP_VISUAL])])
        else:
            w("Nothing is outside the tolerance.")
        extra = {k: v for k, v in vis["doc"].items() if k not in ("ok", "base", "generated", "results") and isinstance(v, (str, int, float))}
        if extra:
            w("")
            w("Notes from the script: " + "; ".join("%s = %s" % (cell(k), cell(v, 200)) for k, v in sorted(extra.items())))
    w("")

    # ---- failures by owner
    w("## Failed checks, grouped by who has to fix them")
    w("")
    if not failures:
        w("None.")
        w("")
    else:
        owners = owner_order({e["owner"] for e in failures})
        w("Owners: " + ", ".join("%s %d" % (o, sum(1 for e in failures if e["owner"] == o)) for o in owners)
          + ". DESIGN = stylesheet, PAGES = HTML and generator, INTERACTION = script, CONTENT = text, "
            "SEO = sitemap, robots, JSON-LD, ASSETS = images, DEPLOY = .gitignore, git and files that do not belong "
            "in the site folder, RUNBOOK = README and migration notes, QA = the check scripts themselves.")
        w("")
        order = {f["name"]: i for i, f in enumerate(families)}
        for owner in owners:
            mine = [e for e in failures if e["owner"] == owner]
            # per page: checks without a viewport first, then the desktop widths from narrow to wide, then the phone
            mine.sort(key=lambda e: (order.get(e["family"], 99), pages.index(e["slug"]) if e["slug"] in pages else len(pages),
                                     e["page"], (-1,) if e["viewport"] == "-" else viewport_rank(e["viewport"]), e["check"]))
            w("### %s (%d)" % (owner, len(mine)))
            w("")
            L += table(["Family", "Page", "Viewport", "Check", "Expected", "Actual", "Screenshot or evidence"],
                       [[e["family"], cell(e["page"]), e["viewport"], cell(e["check"]), cell(e["expected"]), cell(e["actual"]),
                         failure_evidence(e, suite["page_shots"])] for e in mine])
            w("")

    # ---- scripts with problems
    broken = [f for f in families if f["ran"] and f["problems"]]
    if broken:
        w("## Scripts that did not run cleanly")
        w("")
        for f in broken:
            w("### `qa/%s`" % f["script"])
            w("")
            for p in f["problems"]:
                w("- %s" % one_line(p, 600))
            tail = scrub(f["output"] or "").replace("```", "'''").rstrip().splitlines()[-TAIL_LINES:]
            if tail:
                w("")
                w("Last lines of its output:")
                w("")
                w("```")
                L.extend(tail)
                w("```")
            w("")

    # ---- other reports
    if suite["other_reports"]:
        w("## Other reports found in qa/reports")
        w("")
        w("Not started by `qa/run_all.py` and not counted in the result above.")
        w("")
        L += table(["Report", "Written", "Result"], [[cell(n), cell(g), r] for n, g, r in suite["other_reports"]])
        w("")

    w("## Not automated")
    w("")
    w("A pass above says nothing about these requirements. No script of the suite tests them; they were last checked by hand "
      "in the QA review rounds and have to be checked by hand again after a change that touches them.")
    w("")
    for what, how in NOT_AUTOMATED:
        w("- **%s** %s" % (what, how))
    w("")

    w("## Where the details are")
    w("")
    w("- One JSON file per check family in `qa/reports/` with every check, passed or failed, and the full expected and actual values.")
    w("- Screenshots of our site in `qa/screenshots/`.")
    w("- Anything that shows the live Wix site (reference screenshots, side-by-side images) stays outside the site folder "
      "and is never committed.")
    w("")
    return "\n".join(L)


# ---------------------------------------------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------------------------------------------

def parse_args(argv):
    names = ", ".join(n for n, _s in FAMILIES)
    # common.Parser: a wrong option ends with exit code 1, because 2 means "licensing hash match" here
    ap = common.Parser(description="Run the whole QA suite in parallel and write qa/REPORT.md.",
                       epilog="Exit code 0: everything passed. 2: the licensing check found a hash match (hard stop). 1: anything else.")
    ap.add_argument("--base", default=None, help="test this address instead of a local server, for example https://achoostorm.github.io/hairbygerta/")
    ap.add_argument("--page", default="all", help="SLUG[,SLUG] or all (default all). Slugs: " + ", ".join(common.PAGES))
    ap.add_argument("--viewport", default="both", choices=("desktop", "phone", "both"), help="default both")
    ap.add_argument("--only", default=None, help="run only these check families, NAME[,NAME]. Names: " + names)
    ap.add_argument("--jobs", type=int, default=0, help="how many scripts run at the same time (default: all of them)")
    ap.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="seconds one script may run (default %d)" % DEFAULT_TIMEOUT)
    ap.add_argument("--verbose", action="store_true", help="also print the full output of every script")
    args = ap.parse_args(argv)

    args.pages = common.cli_pages(ap, args.page)
    args.all_pages = len(args.pages) == len(common.PAGES)
    args.viewports = common.parse_viewports(args.viewport)

    by_name = {n: (n, s) for n, s in FAMILIES}
    for n, s in FAMILIES:
        by_name[os.path.splitext(s)[0]] = (n, s)
        by_name[s] = (n, s)
    retired = {}
    for n, (s, why) in RETIRED_FAMILIES.items():
        for key in (n, os.path.splitext(s)[0], s):
            retired[key] = (n, why)
    for alias, n in ALIASES.items():
        if n in RETIRED_FAMILIES:
            retired.setdefault(alias, (n, RETIRED_FAMILIES[n][1]))
        else:
            by_name.setdefault(alias, by_name[n])
    if args.only is None:
        args.selected = list(FAMILIES)
    else:
        wanted = [s.strip().lower() for s in args.only.split(",") if s.strip()]
        gone = [s for s in wanted if s in retired and s not in by_name]
        if gone:
            n, why = retired[gone[0]]
            ap.error("the check %s is not run any more, it was %s. Checks: %s" % (n, why, names))
        unknown = [s for s in wanted if s not in by_name]
        if unknown or not wanted:
            ap.error("unknown check %s. Checks: %s" % (", ".join(unknown) or "(none)", names))
        chosen = {by_name[s] for s in wanted}
        args.selected = [f for f in FAMILIES if f in chosen]
    if args.timeout <= 0:
        ap.error("--timeout must be a positive number of seconds")
    return args


def other_reports(known_stems):
    rows = []
    try:
        names = sorted(os.listdir(common.REPORTS))
    except OSError:
        return rows
    for name in names:
        stem, ext = os.path.splitext(name)
        if ext.lower() != ".json" or stem in known_stems or stem == SELF:
            continue
        doc, raw, problem = load_report(os.path.join(common.REPORTS, name))
        retired = " (%s)" % RETIRED_REPORTS[stem] if stem in RETIRED_REPORTS else ""
        if problem:
            rows.append(("qa/reports/" + name, "", "not in the shared format" + retired))
        else:
            bad = sum(1 for r in raw if not r.get("ok"))
            rows.append(("qa/reports/" + name, as_text(doc.get("generated")),
                         ("%d of %d failed" % (bad, len(raw)) if bad else "pass (%d checks)" % len(raw)) + retired))
    return rows


def _fence(line, open_fence=None):
    """Code fences of Markdown. Outside a fence: the fence this line opens, or None.
    Inside one (open_fence given): True when this line closes it."""
    m = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
    if open_fence is None:
        return m.group(1) if m and not (m.group(1)[0] == "`" and "`" in m.group(2)) else None
    return bool(m) and m.group(1)[0] == open_fence[0] and len(m.group(1)) >= len(open_fence) and not m.group(2).strip()


_HEADING = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*))?$")
_UNDERLINE = re.compile(r"^ {0,3}(=+|-+)$")
# A line that cannot be the text of an underlined heading: a quote, a table row, a list item, indented code.
_NOT_TEXT = re.compile(r"^(?: {0,3}(?:[>|]|[-*+][ \t]|\d+[.)][ \t])| {4}|\t)")


def nest_markdown(text, under=2, title="Open questions"):
    """Markdown from another file, made ready to stand under a heading of level `under` in the report.

    What is changed: line ends are made the same, a byte order mark and spaces at the end of a line are taken out,
    an absolute path of this computer is made relative (scrub), a first heading that only repeats the title of the
    section is taken out, empty lines at the start and the end are dropped, and the headings are moved down so that
    the highest one sits one level below the section heading (a heading written as a line of text with a line of
    = or - under it is written with # for that). Text inside code fences is left as it is. Nothing else is changed."""
    lines = [line.rstrip() for line in scrub(text.replace(chr(0xFEFF), "")).replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    out = []        # the lines for the report; the line of a heading holds its text only until the levels are known
    heads = {}      # index in out -> level of the heading on that line
    fence = None
    for line in lines:
        if fence is not None:                   # inside a code fence nothing is a heading
            if _fence(line, fence):
                fence = None
            out.append(line)
            continue
        fence = _fence(line)
        if fence is not None:
            out.append(line)
            continue
        m = _HEADING.match(line)
        if m:
            heads[len(out)] = len(m.group(1))
            out.append(re.sub(r"(?:^|[ \t]+)#+$", "", m.group(2) or "").strip())
            continue
        last = len(out) - 1
        if (_UNDERLINE.match(line) and last >= 0 and out[last].strip() and last not in heads
                and not _NOT_TEXT.match(out[last]) and _fence(out[last]) is None and not _UNDERLINE.match(out[last])):
            heads[last] = 1 if "=" in line else 2
            out[last] = out[last].strip()
            continue                            # the underline itself is not written
        out.append(line)

    def same(a, b):
        words = lambda s: re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()
        return words(a) == words(b)
    first = min(heads) if heads else None
    if first is not None and same(out[first], title) and not any(l.strip() for l in out[:first]):
        del heads[first]                        # the report writes this heading itself
        out[first] = None
    if heads:
        shift = max(0, under + 1 - min(heads.values()))
        for i, level in heads.items():
            out[i] = ("#" * min(6, level + shift) + " " + out[i]).rstrip()
    out = [line for line in out if line is not None]
    while out and not out[0].strip():
        out.pop(0)
    while out and not out[-1].strip():
        out.pop()
    return "\n".join(out)


def open_questions():
    """The text of qa/open-questions.md as it goes into the report, or None when there is no such file."""
    if not os.path.isfile(OPEN_QUESTIONS):
        return None
    try:
        with open(OPEN_QUESTIONS, encoding="utf-8", errors="replace") as f:
            text = nest_markdown(f.read())
    except Exception as e:      # the report is written all the same
        return "`qa/open-questions.md` is there but could not be read (%s)." % one_line(getattr(e, "strerror", None) or type(e).__name__, 200)
    return text or "`qa/open-questions.md` is there but empty."


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="backslashreplace")
        except Exception:
            pass
    args = parse_args(argv)
    started = time.time()
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    passthrough = []
    if args.base:
        passthrough += ["--base", args.base]
    if not args.all_pages:
        passthrough += ["--page", ",".join(args.pages)]
    if args.viewport != "both":
        passthrough += ["--viewport", args.viewport]
    full_run = args.all_pages and args.viewport == "both"

    print("run_all: starting %d checks at the same time (%s). pages: %s, viewports: %s, address: %s"
          % (len(args.selected), ", ".join(n for n, _s in args.selected), "all" if args.all_pages else ",".join(args.pages),
             ",".join(args.viewports), args.base or "a local server per check"), flush=True)
    os.makedirs(common.REPORTS, exist_ok=True)
    runs = run_all_scripts(args.selected, passthrough, args.timeout, args.jobs, full_run, args.verbose)

    by_name = {}
    for run in runs:
        try:
            by_name[run["name"]] = judge(run, args.pages, args.viewports, full_run)
        except Exception as e:      # a report so odd that reading it failed: a failure of that family, not of run_all
            run = dict(run, fresh=False, error="its report could not be used: %s: %s" % (type(e).__name__, e))
            by_name[run["name"]] = judge(run, args.pages, args.viewports, full_run)
    families = [by_name.get(n) or not_run(n, s) for n, s in FAMILIES]
    ran = [f for f in families if f["ran"]]
    failures = [e for f in ran for e in f["failures"] + f["harness"]]
    lic_fam = by_name.get("licensing")
    try:
        lic = licensing_summary(lic_fam)
    except Exception as e:      # a licensing report so odd that it cannot be summarised: never a pass
        lic = licensing_summary(None)
        run = dict(next(r for r in runs if r["name"] == "licensing"), fresh=False,
                   error="its report could not be summarised: %s: %s" % (type(e).__name__, e))
        if run["exit"] == 2 and not re.search(r"^usage:", run["output"] or "", re.I | re.M):
            lic["hard_stop"], lic["why"] = True, "qa/%s ended with exit code 2, its code for a hash match" % run["script"]
        by_name["licensing"] = lic_fam = judge(run, args.pages, args.viewports, full_run)
        families = [by_name.get(n) or not_run(n, s) for n, s in FAMILIES]
        ran = [f for f in families if f["ran"]]
        failures = [e for f in ran for e in f["failures"] + f["harness"]]

    if lic["hard_stop"]:
        code = 2
    elif all(f["status"] == "passed" for f in ran):
        code = 0
    else:
        code = 1

    if args.base:
        address = args.base if args.base.endswith("/") else args.base + "/"
    else:
        address = ("the site folder on this computer (%s). Each browser check serves it through its own local server "
                   "(qa/serve.py) on a free port" % common.LOCAL_BASE)
    all_entries = [e for f in ran for e in f["entries"]]
    shots = list_images(common.SHOTS)
    private = list_images(common.PRIVATE)
    page_shots, side_shots = {}, {}
    # The two viewports of the run, and every other width a report names (desktop-1265, desktop-1440, ...).
    shown = list(args.viewports) + sorted({e["viewport"] for e in all_entries if e["vp"]} - set(args.viewports), key=viewport_rank)
    for slug in args.pages:
        for vp in shown:
            try:
                page_shots[(slug, vp)] = page_screenshot(slug, vp, shots, all_entries, started)
                side = side_by_side(slug, vp, private, all_entries, started)
                if side:
                    side_shots[(slug, vp)] = side
            except Exception:
                page_shots.setdefault((slug, vp), "")
    suite = {"families": families, "pages": args.pages, "viewports": args.viewports, "all_pages": args.all_pages,
             "failures": failures, "licensing": lic, "exit_code": code, "address": address, "time": stamp,
             "seconds": time.time() - started, "page_shots": page_shots, "side_shots": side_shots, "other_reports": [],
             "open_questions": open_questions()}

    # From here on nothing may change a hard stop (2) into another code, and a fault of run_all itself is never a pass.
    try:
        suite["other_reports"] = other_reports({os.path.splitext(os.path.basename(r))[0] for n, s in FAMILIES for r in report_paths(n, s)})
        text = build_markdown(suite)
    except Exception as e:
        import traceback
        traceback.print_exc()
        code = suite["exit_code"] = code or 1
        text = "\n".join(
            ["# QA report: Hair & Makeup by Gerta", "",
             "`qa/run_all.py` could not write the full report (%s). This is a fault of run_all itself, owner QA." % one_line("%s: %s" % (type(e).__name__, e), 300),
             "", "- Time: %s" % stamp, "- Exit code: %d%s" % (code, " (HARD STOP: licensing hash match, do not commit)" if code == 2 else ""), ""]
            + ["- %s (`qa/%s`): %s, %s" % (f["name"], f["script"], f["status"], plural(len(f["failures"]) + len(f["harness"]), "failed check")) for f in families]
            + ["", "The JSON files in `qa/reports/` hold every result.", ""])
    try:
        with open(REPORT_MD, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    except OSError as e:
        code = code or 1
        print("run_all: could not write qa/REPORT.md (%s: %s). Is the file open in another program?" % (type(e).__name__, scrub(e)), flush=True)

    results = []
    for f in ran:
        bad = len(f["failures"]) + len(f["harness"])
        if f["status"] == "passed":
            actual = "passed, %d checks" % len(f["entries"])
        elif f["problems"]:
            actual = "%s: %s" % (f["status"], "; ".join(one_line(p, 300) for p in f["problems"]))
            if f["failures"]:
                actual += "; %d of %d checks failed" % (len(f["failures"]), len(f["entries"]))
        else:
            actual = "%d of %d checks failed" % (bad, len(f["entries"]))
        # One owner per entry, as in every report: the one with the most failed checks. The full split is in "owners".
        split = {}
        for e in f["failures"] + f["harness"]:
            split[e["owner"]] = split.get(e["owner"], 0) + 1
        owners = sorted(owner_order(set(split)), key=lambda o: -split[o])
        results.append({"page": common.SITE_PAGE, "viewport": common.NO_VIEWPORT, "check": "qa/%s" % f["script"], "ok": f["status"] == "passed",
                        "expected": "the script runs, writes %s and every check in it passes" % site_rel(f["report"]),
                        "actual": actual, "evidence": "qa/REPORT.md", "owner": owners[0] if owners else "QA",
                        "owners": {o: split[o] for o in owners}})
    summary = {"script": "qa/%s.py" % SELF, "exit_code": code, "report": "qa/REPORT.md", "failed_checks": len(failures), "licensing_hard_stop": lic["hard_stop"],
               "pages": args.pages, "viewports": args.viewports, "seconds": round(suite["seconds"], 1),
               "open_questions": "qa/open-questions.md" if suite["open_questions"] is not None else "",
               "families": [{"name": f["name"], "script": "qa/" + f["script"], "status": f["status"], "exit_code": f["exit"],
                             "seconds": round(f["seconds"], 1), "checks": len(f["entries"]),
                             "failed": len(f["failures"]) + len(f["harness"]), "base": f["base"]} for f in families]}
    try:
        common.save_report(SELF, results, common.report_base(args.base), summary, replace={common.SITE_PAGE})
    except Exception as e:
        print("run_all: could not write qa/reports/%s.json: %s" % (SELF, e), flush=True)

    for e in failures:
        line = "FAIL %-11s %-9s %s %s | %s | expected: %s | actual: %s" % (
            e["owner"], e["family"], e["page"], e["viewport"], one_line(e["check"], 120), one_line(e["expected"], 160), one_line(e["actual"], 160))
        print(line, flush=True)
    passed = sum(1 for f in ran if f["status"] == "passed")
    if code == 2:
        verdict = "HARD STOP, licensing hash match (%s): do not commit" % lic["why"]
    elif code == 0:
        verdict = "PASS"
    else:
        verdict = "FAIL"
    print("run_all: %s. %d of %s passed, %s, %.0f s. Report: qa/REPORT.md (exit code %d)"
          % (verdict, passed, plural(len(ran), "check family", "check families"), plural(len(failures), "failed check"), suite["seconds"], code), flush=True)
    return code


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("run_all: interrupted, the check scripts were stopped", flush=True)
        sys.exit(1)
