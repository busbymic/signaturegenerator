from flask import Flask, render_template_string, request, Response, send_from_directory
import os

app = Flask(__name__)

# Use your uploaded static/logo.png automatically when Logo URL is left blank
DEFAULT_LOGO = "/static/logo.png"

# ---------- STYLED SIGNATURE BLOCK ----------
signature_block = """
{%- set c = brand_color or '#0d6efd' -%}
<table cellpadding="0" cellspacing="0"
       style="font-family: Arial, sans-serif; color:#222; line-height:1.35;
              border-left:4px solid {{ c }}; padding-left:12px;">
  <tr>
    {% if logo_url %}
    <td valign="top" style="padding:0 12px 0 0;">
      <img src="{{ logo_url }}" alt="Logo"
           style="width:64px; height:auto; border-radius:6px; display:block;">
    </td>
    {% endif %}
    <td valign="top" style="padding:0;">
      <div style="font-weight:700; font-size:16px; margin-bottom:2px;">{{ name }}</div>
      <div style="font-size:13px; color:#555; margin-bottom:8px;">{{ position }} | {{ company }}</div>

      <div style="font-size:13px; margin-bottom:8px;">
        {% if phone %}
          <a href="tel:{{ phone }}" style="color:{{ c }}; text-decoration:none;">{{ phone }}</a>
          {% if email %}<span style="color:#aaa;"> &nbsp;|&nbsp; </span>{% endif %}
        {% endif %}
        {% if email %}
          <a href="mailto:{{ email }}" style="color:{{ c }}; text-decoration:none;">{{ email }}</a>
        {% endif %}
      </div>

      {% if facebook or instagram or linkedin or pinterest or tiktok %}
      <div style="margin-bottom:10px;">
        {% if facebook %}
          <a href="{{ facebook }}" style="text-decoration:none; margin-right:8px;">
            <img src="https://cdn-icons-png.flaticon.com/512/174/174848.png" width="18" alt="Facebook">
          </a>
        {% endif %}
        {% if instagram %}
          <a href="{{ instagram }}" style="text-decoration:none; margin-right:8px;">
            <img src="https://cdn-icons-png.flaticon.com/512/174/174855.png" width="18" alt="Instagram">
          </a>
        {% endif %}
        {% if linkedin %}
          <a href="{{ linkedin }}" style="text-decoration:none; margin-right:8px;">
            <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="18" alt="LinkedIn">
          </a>
        {% endif %}
        {% if pinterest %}
          <a href="{{ pinterest }}" style="text-decoration:none; margin-right:8px;">
            <img src="https://cdn-icons-png.flaticon.com/512/145/145808.png" width="18" alt="Pinterest">
          </a>
        {% endif %}
        {% if tiktok %}
          <a href="{{ tiktok }}" style="text-decoration:none;">
            <img src="https://cdn-icons-png.flaticon.com/512/3116/3116490.png" width="18" alt="TikTok">
          </a>
        {% endif %}
      </div>
      {% endif %}

      {% if promo %}
      <div style="display:inline-block; padding:12px 14px; border:1px solid {{ c }};
                  border-radius:8px; font-size:13px; color:#333; background:#f9f9f9; max-width:520px;">
        {{ promo | safe }}
      </div>
      {% endif %}
    </td>
  </tr>
</table>
"""

# ---------- FORM (with localStorage profiles) ----------
form_html = """
<!DOCTYPE html><html><head>
  <title>Email Signature Generator</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head><body class="container py-4">
  <h1 class="mb-3">Create Your Email Signature</h1>

  <!-- Profiles bar -->
  <div class="border rounded p-3 mb-3">
    <div class="row g-2 align-items-end">
      <div class="col-md-4">
        <label class="form-label">Saved profiles</label>
        <select id="profileSelect" class="form-select"></select>
      </div>
      <div class="col-md-4">
        <label class="form-label">Profile name</label>
        <input id="profileName" class="form-control" placeholder="e.g., Gumbo Hut / Consulting / TMS">
      </div>
      <div class="col-md-4 d-flex gap-2">
        <button type="button" class="btn btn-outline-primary" onclick="saveProfile()">Save as Profile</button>
        <button type="button" class="btn btn-outline-secondary" onclick="loadProfile()">Load</button>
        <button type="button" class="btn btn-outline-danger" onclick="deleteProfile()">Delete</button>
      </div>
    </div>
    <div class="mt-2 d-flex gap-2">
      <button type="button" class="btn btn-sm btn-outline-success" onclick="saveLast()">Save Last Used</button>
      <button type="button" class="btn btn-sm btn-outline-dark" onclick="clearForm()">Clear Form</button>
    </div>
  </div>

  <form id="sigForm" method="POST" class="row g-3">
    <div class="col-md-6"><input class="form-control" name="company" placeholder="Company Name" required></div>
    <div class="col-md-6"><input class="form-control" name="name" placeholder="Your Name" required></div>
    <div class="col-md-6"><input class="form-control" name="position" placeholder="Your Position" required></div>
    <div class="col-md-6"><input class="form-control" name="phone" placeholder="Telephone Number"></div>
    <div class="col-md-6"><input class="form-control" type="email" name="email" placeholder="Email Address"></div>

    <div class="col-12"><hr></div>
    <div class="col-md-6"><input class="form-control" name="logo_url" placeholder="Logo URL (leave blank to use default)"></div>
    <div class="col-md-6"><input class="form-control" name="brand_color" placeholder="Brand color hex (e.g. #E63946)" value="#0d6efd"></div>

    <div class="col-12"><hr></div>
    <div class="col-md-2"><input class="form-control" name="facebook" placeholder="Facebook URL"></div>
    <div class="col-md-2"><input class="form-control" name="instagram" placeholder="Instagram URL"></div>
    <div class="col-md-2"><input class="form-control" name="linkedin" placeholder="LinkedIn URL"></div>
    <div class="col-md-2"><input class="form-control" name="pinterest" placeholder="Pinterest URL"></div>
    <div class="col-md-2"><input class="form-control" name="tiktok" placeholder="TikTok URL"></div>

    <div class="col-12">
      <label class="form-label fw-bold">Marketing Promotion (text or HTML)</label>
      <textarea class="form-control" name="promo" rows="5" placeholder="Paste your promo HTML or write text here..."></textarea>
      <div class="form-text">Tip: Save different promos inside profiles so you can swap fast.</div>
    </div>

    <div class="col-12">
      <button class="btn btn-primary" type="submit">Generate Signature</button>
    </div>
  </form>

  <script>
    const FIELDS = ["company","name","position","phone","email",
                    "logo_url","brand_color","facebook","instagram","linkedin","pinterest","tiktok","promo"];

    // --- helpers for localStorage
    const getLast = () => JSON.parse(localStorage.getItem("sig_last")||"{}");
    const setLast = (obj) => localStorage.setItem("sig_last", JSON.stringify(obj));

    const getProfiles = () => JSON.parse(localStorage.getItem("sig_profiles")||"{}");
    const setProfiles = (obj) => localStorage.setItem("sig_profiles", JSON.stringify(obj));

    function formToObj(){
      const o = {};
      FIELDS.forEach(id => o[id] = document.querySelector(`[name="${id}"]`).value);
      return o;
    }
    function objToForm(o){
      FIELDS.forEach(id => {
        const el = document.querySelector(`[name="${id}"]`);
        if (el && o[id] !== undefined) el.value = o[id];
      });
    }

    // auto-save as you type
    document.addEventListener("input", (e) => {
      if (!e.target.name || !FIELDS.includes(e.target.name)) return;
      const o = formToObj();
      setLast(o);
      refreshProfileSelect(); // keep dropdown up-to-date on first save
    });

    // load last used on page load
    window.addEventListener("DOMContentLoaded", () => {
      objToForm(getLast());
      refreshProfileSelect();
    });

    // buttons
    function saveLast(){
      setLast(formToObj());
      alert("Saved as ‘Last used’. It will auto-load next time.");
    }
    function clearForm(){
      FIELDS.forEach(id => document.querySelector(`[name="${id}"]`).value = "");
    }
    function refreshProfileSelect(){
      const sel = document.getElementById("profileSelect");
      const profiles = getProfiles();
      const names = Object.keys(profiles).sort();
      sel.innerHTML = names.length ? names.map(n=>`<option value="${n}">${n}</option>`).join("") : "<option>(no profiles)</option>";
    }
    function saveProfile(){
      const name = document.getElementById("profileName").value.trim();
      if (!name){ alert("Type a profile name first."); return; }
      const profiles = getProfiles();
      profiles[name] = formToObj();
      setProfiles(profiles);
      refreshProfileSelect();
      alert("Profile saved.");
    }
    function loadProfile(){
      const name = document.getElementById("profileSelect").value;
      const profiles = getProfiles();
      if (!profiles[name]){ alert("Select a saved profile first."); return; }
      objToForm(profiles[name]);
      setLast(profiles[name]);
    }
    function deleteProfile(){
      const name = document.getElementById("profileSelect").value;
      const profiles = getProfiles();
      if (!profiles[name]){ alert("Select a saved profile to delete."); return; }
      if (!confirm(`Delete profile “${name}”?`)) return;
      delete profiles[name];
      setProfiles(profiles);
      refreshProfileSelect();
    }
  </script>
</body></html>
"""

# ---------- PREVIEW PAGE ----------
signature_page = """
<!DOCTYPE html><html><head>
  <title>Your Email Signature</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>.code{font-family:ui-monospace,monospace}</style>
</head><body class="container py-4">
  <h2 class="mb-3">Your Email Signature</h2>
  <div class="border p-3 rounded mb-3 bg-white">{{ signature_html | safe }}</div>

  <div class="d-flex gap-2 mb-2">
    <button onclick="copyHTML()" class="btn btn-secondary">Copy HTML</button>
    <form method="POST" action="/download" class="m-0">
      {% for k,v in data.items() %}<input type="hidden" name="{{k}}" value="{{v}}">{% endfor %}
      <button class="btn btn-primary" type="submit">Download HTML</button>
    </form>
  </div>

  <textarea id="code" class="form-control code" rows="12">{{ signature_html | safe }}</textarea>

  <script>
    function copyHTML(){
      const t=document.getElementById('code'); t.select(); t.setSelectionRange(0,999999);
      navigator.clipboard.writeText(t.value).then(()=>alert('Signature HTML copied!'));
    }
  </script>
</body></html>
"""

# ---------- ROUTES ----------
FIELDS = ["company","name","position","phone","email",
          "facebook","instagram","linkedin","pinterest","tiktok",
          "promo","logo_url","brand_color"]

@app.route("/", methods=["GET","POST"])
def index():
    if request.method == "POST":
        data = {k: request.form.get(k,"").strip() for k in FIELDS}
        if not data.get("logo_url"):
            data["logo_url"] = DEFAULT_LOGO
        sig = render_template_string(signature_block, **data)
        return render_template_string(signature_page, signature_html=sig, data=data)
    return render_template_string(form_html)

@app.route("/download", methods=["POST"])
def download():
    data = {k: request.form.get(k,"").strip() for k in FIELDS}
    if not data.get("logo_url"):
        data["logo_url"] = DEFAULT_LOGO
    sig = render_template_string(signature_block, **data)
    return Response(sig, mimetype="text/html",
                    headers={"Content-Disposition":"attachment; filename=signature.html"})

# Serve /static/* files (like /static/logo.png)
@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(os.path.join(app.root_path, "static"), filename)

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)), debug=False)
