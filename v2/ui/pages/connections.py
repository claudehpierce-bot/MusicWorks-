"""MusicWorks™ V4.2 — Media Toolbox: all providers, subscriptions, and routing in one place."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from ui.components import page_header, render_html, navigate_to
from execution.provider_registry import PROVIDERS, CATEGORIES, get_provider, is_api_key_set
from execution.subscription_store import (
    get_subscription, save_subscription, is_subscription_active,
    days_until_renewal, renewal_warning, PLAN_OPTIONS, PLAN_LABELS, PLAN_COLORS, ACTIVE_PLANS
)
from execution.provider_router import (
    ROUTING_TABLE, route, get_factory_plan, is_available,
    set_override, clear_override, get_override
)


def render():
    page_header("Connections", "Media Toolbox — every provider, every subscription, one intelligent router.", "🔌")

    # ── Security note ─────────────────────────────────────────────────────────
    render_html("""
    <div class="mw-card" style="padding:1rem 1.5rem; border-left:3px solid #D4A853; margin-bottom:1.5rem;">
        <div style="font-size:13px; color:#C8C4BE; line-height:1.7;">
            <strong style="color:#D4A853;">Security:</strong>
            API keys are never stored by MusicWorks. They live in environment variables
            or Streamlit secrets. Set them in <code>.streamlit/secrets.toml</code>
            or in Streamlit Cloud → Settings → Secrets.
        </div>
    </div>
    """)

    # ── Summary stats ─────────────────────────────────────────────────────────
    ai_providers  = [p for p in PROVIDERS if p.category not in ("Publishing", "Distribution")]
    api_connected = sum(1 for p in ai_providers if p.requires_api_key and is_api_key_set(p.key))
    sub_active    = sum(1 for p in ai_providers if not p.requires_api_key and is_subscription_active(p.key))
    expiring      = [p for p in PROVIDERS if renewal_warning(p.key) is not None]
    plan_avail    = sum(1 for entry in ROUTING_TABLE.values() if route(entry.task) != "mock")

    s1, s2, s3, s4, s5 = st.columns(5)
    _stat(s1, "API Connected",    str(api_connected), "#22C55E")
    _stat(s2, "Subscriptions On", str(sub_active),    "#10B981")
    _stat(s3, "Expiring Soon",    str(len(expiring)),  "#F59E0B" if expiring else "#6A6460")
    _stat(s4, "Tasks Covered",   f"{plan_avail}/{len(ROUTING_TABLE)}", "#9B89D4")
    _stat(s5, "Total Providers",  str(len(PROVIDERS)), "#6A6460")

    st.markdown("<div style='margin-top:2rem;'></div>", unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab_tools, tab_router, tab_how = st.tabs(["🧰  Provider Library", "🔀  Routing Table", "⚙️  How to Configure"])

    # ═══════════════════════════════════════════════════════════════════════════
    with tab_tools:
        _render_provider_library()

    # ═══════════════════════════════════════════════════════════════════════════
    with tab_router:
        _render_routing_table()

    # ═══════════════════════════════════════════════════════════════════════════
    with tab_how:
        _render_how_to_configure()


# ── Provider Library ──────────────────────────────────────────────────────────

def _render_provider_library():
    for category in CATEGORIES:
        cat_providers = [p for p in PROVIDERS if p.category == category]
        render_html(f'<div class="mw-section-label">{category}</div>')

        # 3 columns per row
        for row_start in range(0, len(cat_providers), 3):
            row  = cat_providers[row_start:row_start + 3]
            cols = st.columns(max(len(row), 1))
            for col, provider in zip(cols, row):
                _render_provider_card(col, provider)

        st.markdown("<div style='margin-bottom:0.5rem;'></div>", unsafe_allow_html=True)


def _render_provider_card(col, provider):
    from execution.connections_store import record_test, test_connection, get_connection_status

    key = provider.key
    test_status = get_connection_status(key)

    # Connection status — three states for API-key providers:
    #   🟢 Connected            — key present, last test succeeded (or never tested)
    #   🟡 Configuration Error  — key present, but the last live test failed
    #   🔴 Not Connected        — no key configured at all
    if provider.requires_api_key:
        has_key = test_status["has_key"]
        last_status = test_status.get("last_status", "")
        if not has_key:
            connected = False
            status_dot, status_label, status_color = "🔴", "Not Connected", "#EF4444"
        elif last_status == "error":
            connected = True
            status_dot, status_label, status_color = "🟡", "Configuration Error", "#F59E0B"
        else:
            connected = True
            status_dot, status_label, status_color = "🟢", "Connected", "#22C55E"
    else:
        connected = is_subscription_active(key)
        status_dot   = "🟢" if connected else "🟡"
        status_label = "Active" if connected else "Not active"
        status_color = "#22C55E" if connected else "#F59E0B"

    # Subscription info
    sub   = get_subscription(key)
    plan  = sub.get("plan", "")
    rd    = sub.get("renewal_date", "")
    cred  = sub.get("credits_remaining")
    warn  = renewal_warning(key)
    days  = days_until_renewal(key)

    # Last tested
    last_tested = test_status.get("last_tested", "")
    if last_tested:
        last_tested_label = f"Last tested: {last_tested[:16].replace('T', ' ')} UTC"
        last_tested_color = "#22C55E" if test_status.get("last_status") == "connected" else "#EF4444"
    else:
        last_tested_label = "Last tested: Never"
        last_tested_color = "#6A6460"

    border_color = "#22C55E" if connected else "#2A2A2A"

    with col:
        render_html(f"""
        <div class="mw-card" style="padding:1rem; border-top:3px solid {border_color}; margin-bottom:0.5rem; min-height:230px;">
            <div style="display:flex; align-items:flex-start; gap:10px; margin-bottom:8px;">
                <span style="font-size:22px; margin-top:2px;">{provider.icon}</span>
                <div style="flex:1;">
                    <div style="font-size:14px; font-weight:700; color:#F0EDE8;">{provider.name}</div>
                    <div style="font-size:10px; color:{status_color}; font-weight:600;">{status_dot} {status_label}</div>
                </div>
            </div>
            <div style="font-size:11px; color:#8A8480; line-height:1.5; margin-bottom:8px;">{provider.description[:90]}{'…' if len(provider.description) > 90 else ''}</div>

            <div style="display:flex; flex-wrap:wrap; gap:4px; margin:6px 0 8px 0;">
                {''.join(f'<span style="background:#1E1E1E; color:#8A8480; font-size:9px; padding:2px 6px; border-radius:10px;">{cap.replace("_"," ")}</span>' for cap in provider.capabilities[:4])}
            </div>

            {f'<div style="font-size:10px; color:#6A6460;">Env: <code style="color:#9B89D4;">{provider.env_var}</code></div>' if provider.env_var else '<div style="font-size:10px; color:#6A6460;">Subscription only — no API key</div>'}
            <div style="font-size:10px; color:{last_tested_color}; margin-top:3px;">{last_tested_label}</div>

            {f'<div style="font-size:10px; margin-top:4px; color:{PLAN_COLORS.get(plan,"#6A6460")}; font-weight:600;">{PLAN_LABELS.get(plan, "")}{"  ·  " + rd[:10] if rd else ""}</div>' if plan else ""}
            {f'<div style="font-size:10px; color:{"#EF4444" if days is not None and days < 0 else "#F59E0B"};">{warn}</div>' if warn else ""}
            {f'<div style="font-size:10px; color:#8A8480;">Credits: {cred}</div>' if cred is not None else ""}

            {'<div style="margin-top:6px;"><span style="background:#F59E0B22; color:#F59E0B; font-size:9px; font-weight:600; padding:2px 8px; border-radius:10px;">🔧 Available for future integration</span></div>' if not provider.live_implemented else ''}
            {f'<div style="margin-top:6px;"><a href="{provider.provider_url}" target="_blank" style="font-size:10px; color:#9B89D4; text-decoration:none;">📄 Documentation →</a></div>' if provider.provider_url else ''}
        </div>
        """)

        # Buttons row
        b1, b2 = col.columns(2)
        with b1:
            if st.button("Test Connection", key=f"tst_{key}", use_container_width=True):
                with st.spinner(f"Testing {provider.name}…"):
                    ok, msg = test_connection(key)
                if ok:
                    st.success(f"✓ {msg[:60]}")
                else:
                    st.warning(f"⚠ {msg[:60]}")
                st.rerun()

        with b2:
            if st.button("Subscription", key=f"sub_btn_{key}", use_container_width=True):
                toggle = f"sub_open_{key}"
                st.session_state[toggle] = not st.session_state.get(toggle, False)

        # Inline subscription editor
        if st.session_state.get(f"sub_open_{key}", False):
            with st.form(f"sub_form_{key}"):
                plan_opts = [p for p in PLAN_OPTIONS if p != ""]
                current_idx = plan_opts.index(plan) if plan in plan_opts else 0
                new_plan = st.selectbox("Plan", plan_opts,
                                        format_func=lambda x: PLAN_LABELS[x],
                                        index=current_idx, key=f"sp_{key}")
                new_rd   = st.text_input("Renewal / Expiry date (YYYY-MM-DD)", value=rd, key=f"srd_{key}")
                new_cred = st.number_input("Credits remaining (leave 0 to skip)",
                                           min_value=0, value=int(cred) if cred else 0, key=f"sc_{key}")
                new_notes = st.text_input("Notes", value=sub.get("notes",""), key=f"sn_{key}")
                save_col, clear_col = st.columns(2)
                with save_col:
                    submitted = st.form_submit_button("Save", type="primary", use_container_width=True)
                with clear_col:
                    cleared = st.form_submit_button("Clear", use_container_width=True)

                if submitted:
                    save_subscription(key, new_plan, new_rd,
                                      int(new_cred) if new_cred else None,
                                      None, new_notes)
                    st.session_state.pop(f"sub_open_{key}", None)
                    st.success("Saved.")
                    st.rerun()
                if cleared:
                    save_subscription(key, "", "", None, None, "")
                    st.session_state.pop(f"sub_open_{key}", None)
                    st.rerun()


# ── Routing Table ─────────────────────────────────────────────────────────────

def _render_routing_table():
    render_html("""
    <div class="mw-card" style="padding:1rem 1.5rem; border-left:3px solid #9B89D4; margin-bottom:1.5rem;">
        <div style="font-size:13px; color:#C8C4BE; line-height:1.7;">
            MusicWorks automatically selects the best connected provider for each task.
            <strong style="color:#D4A853;">The founder never chooses the AI.</strong>
            Override any route below if you prefer a specific provider.
        </div>
    </div>
    """)

    plan = get_factory_plan()

    for entry in plan:
        task         = entry["task"]
        override_key = get_override(task)
        selected     = entry["selected_key"]
        is_mock      = entry["is_mock"]
        has_override = entry["has_override"]

        # Primary + fallback availability
        primary_avail = entry["primary_avail"]
        fb_keys       = entry["fallback_keys"]
        from execution.provider_registry import PROVIDER_MAP

        primary_prov  = PROVIDER_MAP.get(entry["primary_key"])
        fallback_names = []
        fallback_available = []
        for fb in fb_keys:
            fp = PROVIDER_MAP.get(fb)
            if fp:
                avail = is_available(fb)
                fallback_names.append((fp.name, fp.icon, avail))
                fallback_available.append(avail)

        # Color
        if is_mock:
            status_color = "#6A6460"
            status_text  = "No provider connected — mock output"
        elif has_override:
            status_color = "#9B89D4"
            status_text  = f"Override: {entry['selected_name']}"
        elif not primary_avail and any(fallback_available):
            status_color = "#F59E0B"
            status_text  = f"Fallback: {entry['selected_name']}"
        else:
            status_color = "#22C55E"
            status_text  = entry["selected_name"]

        with st.expander(
            f"{entry['icon']}  **{entry['label']}** — {entry['selected_icon']} {entry['selected_name']}",
            expanded=False
        ):
            col_info, col_override = st.columns([3, 2])

            with col_info:
                # Primary
                dot_p = "🟢" if primary_avail else "⚫"
                prov_icon = primary_prov.icon if primary_prov else ""
                render_html(f"""
                <div style="font-size:13px; color:#C8C4BE; margin-bottom:6px;">{entry['description']}</div>
                <div style="font-size:12px; margin-bottom:4px;">
                    <strong style="color:#8A8480;">Primary:</strong>
                    {prov_icon} {entry['primary_name']}
                    <span style="color:{'#22C55E' if primary_avail else '#6A6460'};">{dot_p}</span>
                </div>
                """)
                # Fallbacks
                for fname, ficon, favail in fallback_names:
                    fdot = "🟢" if favail else "⚫"
                    render_html(f"""
                    <div style="font-size:12px; margin-bottom:4px;">
                        <strong style="color:#8A8480;">Fallback:</strong>
                        {ficon} {fname}
                        <span style="color:{'#22C55E' if favail else '#6A6460'};">{fdot}</span>
                    </div>
                    """)

                render_html(f"""
                <div style="font-size:12px; margin-top:8px; color:{status_color}; font-weight:600;">
                    ▶ Active: {status_text}
                </div>
                """)

            with col_override:
                # Build options for override dropdown
                all_provider_keys = [entry["primary_key"]] + list(fb_keys)
                all_providers_in_table = [PROVIDER_MAP.get(k) for k in all_provider_keys if PROVIDER_MAP.get(k)]
                opts   = ["auto"] + [p.key for p in all_providers_in_table]
                labels = {"auto": f"Auto ({entry['selected_name']})"}
                labels.update({p.key: f"{p.icon} {p.name}" for p in all_providers_in_table})

                current_sel = override_key if override_key in opts else "auto"
                sel_idx     = opts.index(current_sel)

                new_sel = st.selectbox("Route override:", opts,
                                       format_func=lambda k: labels.get(k, k),
                                       index=sel_idx, key=f"ro_{task}")
                if st.button("Apply", key=f"ro_apply_{task}", use_container_width=True):
                    if new_sel == "auto":
                        clear_override(task)
                    else:
                        set_override(task, new_sel)
                    st.success("Routing updated.")
                    st.rerun()

                if has_override:
                    if st.button("Clear override", key=f"ro_clear_{task}", use_container_width=True):
                        clear_override(task)
                        st.rerun()

    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)
    render_html("""
    <div style="font-size:12px; color:#6A6460; line-height:1.7;">
        🟢 Connected &nbsp;·&nbsp; ⚫ Not configured &nbsp;·&nbsp;
        <span style="color:#9B89D4;">Purple</span> = founder override &nbsp;·&nbsp;
        <span style="color:#F59E0B;">Amber</span> = fallback in use &nbsp;·&nbsp;
        <span style="color:#6A6460;">Gray</span> = mock output (no provider connected)
    </div>
    """)


# ── How to Configure ─────────────────────────────────────────────────────────

def _render_how_to_configure():
    from execution.provider_registry import PROVIDERS

    render_html("""
    <div style="font-size:13px; color:#C8C4BE; line-height:1.8;">
        <strong style="color:#D4A853; font-size:15px;">Option 1 — Streamlit Cloud (recommended for deployment)</strong><br>
        Go to your app → <strong>Settings → Secrets</strong> → paste keys in TOML format.<br>

        <strong style="color:#D4A853; font-size:15px;">Option 2 — Local development</strong><br>
        Create <code>.streamlit/secrets.toml</code> in the project root with the same format below.<br><br>

        <strong style="color:#D4A853; font-size:15px;">Option 3 — Environment variables</strong><br>
        Set the same variable names in your shell, system environment, or a local <code>.env</code> file
        (see <code>.env.example</code> in the project root).<br><br>
    </div>
    """)

    # ── Complete secrets template, generated from the provider registry ────────
    # This is the single source of truth — every provider is listed here, no exceptions.
    # Uses st.code() (not raw HTML <pre>) so line breaks always render correctly.
    live_keyed    = [p for p in PROVIDERS if p.requires_api_key and p.live_implemented]
    future_keyed  = [p for p in PROVIDERS if p.requires_api_key and not p.live_implemented and p.env_var]
    sub_only      = [p for p in PROVIDERS if not p.requires_api_key and p.env_var]
    no_key        = [p for p in PROVIDERS if not p.env_var]

    def _toml_block(providers):
        width = max((len(p.env_var) for p in providers), default=0)
        return "\n".join(f'{p.env_var.ljust(width)} = "..."   # {p.name} — {p.description[:50]}' for p in providers)

    st.markdown("**🟢 Live today — connecting these activates real generation**")
    st.code(_toml_block(live_keyed), language="toml")

    st.markdown("**🔧 Available for future integration — safe to set now, no live worker uses them yet**")
    st.code(_toml_block(future_keyed), language="toml")

    st.markdown("**📎 Subscription-only tools** — no API key checked; mark the subscription active in the Provider Library above instead")
    st.code(_toml_block(sub_only), language="toml")

    render_html(f"""
    <div style="font-size:13px; color:#C8C4BE; line-height:1.8;">
        <div style="font-size:12px; color:#8A8480; margin-bottom:1rem;">
            <strong style="color:#8A8480;">No key required:</strong>
            {', '.join(p.name for p in no_key)} — {no_key[0].description if len(no_key) == 1 else "distribution metadata / URLs only, nothing to authenticate"}.
        </div>

        <strong style="color:#D4A853; font-size:15px;">Publishing &amp; newsletter platforms</strong><br>
        These enable future automated publishing. MusicWorks prepares content for manual publishing today —
        no platform keys are required for the core Media Factory to operate.<br><br>

        <strong style="color:#F59E0B; font-size:14px;">Adding a new provider in the future</strong><br>
        1. Add a <code>Provider()</code> entry to <code>provider_registry.py</code> (this page and the secrets
        template above update automatically — nothing else to edit)<br>
        2. Add it to the routing table in <code>provider_router.py</code> (primary or fallback)<br>
        3. Set <code>live_implemented=True</code> once a worker actually calls its real API<br>
        4. Set its API key in secrets
    </div>
    """)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _stat(col, label, value, color):
    with col:
        render_html(f"""
        <div class="mw-card" style="padding:1.25rem; text-align:center; border-top:3px solid {color};">
            <div style="font-size:26px; font-weight:800; color:{color};">{value}</div>
            <div style="font-size:10px; color:#8A8480; margin-top:4px; text-transform:uppercase; letter-spacing:0.5px;">{label}</div>
        </div>
        """)
