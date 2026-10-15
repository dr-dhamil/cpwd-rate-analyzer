import streamlit as st
import pandas as pd
import datetime
from PIL import Image
import os

# Page Configuration
st.set_page_config(
    page_title="MDAS | CPWD Rate Analysis Software",
    page_icon="🏗️",
    layout="wide"
)

# Initialize Session States
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""

if 'market_rates' not in st.session_state:
    st.session_state.market_rates = pd.DataFrame([
        {
            "Col. / Code": "0367",
            "Item Name (as in DAR)": "Portland Cement (OPC-43 Grade)",
            "Rate (₹)": 5156.0,
            "Unit": "tonne",
            "GST (%)": 28.0,
            "Net Rate (₹)": 6599.68,
            "Date": "2026-04-01",
            "Vendor": "UltraTech Cement Ltd."
        },
        {
            "Col. / Code": "0982",
            "Item Name (as in DAR)": "Coarse sand (zone III)",
            "Rate (₹)": 1450.0,
            "Unit": "cum",
            "GST (%)": 5.0,
            "Net Rate (₹)": 1522.5,
            "Date": "2026-04-01",
            "Vendor": "Delhi Sands Corp"
        },
        {
            "Col. / Code": "0123",
            "Item Name (as in DAR)": "Mason 1st class",
            "Rate (₹)": 897.0,
            "Unit": "day",
            "GST (%)": 0.0,
            "Net Rate (₹)": 897.0,
            "Date": "2026-04-01",
            "Vendor": "National Labor Board"
        }
    ])

if 'custom_dsr_items' not in st.session_state:
    st.session_state.custom_dsr_items = []

if 'analysis_factors' not in st.session_state:
    st.session_state.analysis_factors = {}

if 'boq_items' not in st.session_state:
    st.session_state.boq_items = []

# Helper: Get Latest Rate, Date, and Vendor details for DSR Basic Code
def get_market_rate_details(item_name):
    df_m = st.session_state.market_rates
    filtered = df_m[df_m["Item Name (as in DAR)"].str.lower() == item_name.lower()]
    if not filtered.empty:
        latest = filtered.iloc[-1]
        return {
            "net_rate": float(latest["Net Rate (₹)"]),
            "date": str(latest["Date"]),
            "vendor": str(latest["Vendor"])
        }
    return {"net_rate": 100.0, "date": "N/A", "vendor": "N/A"}

# ==========================================
# 1ST PAGE: LOGIN WITH GOOGLE ID
# ==========================================
if not st.session_state.logged_in:
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.markdown("<h1 style='text-align: center; color: #ff4b4b;'>MDAS</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>CPWD Rate Analysis Enterprise Portal</h3>", unsafe_allow_html=True)
        
        # Display Logo if available
        if os.path.exists("mdas.jpg"):
            st.image("mdas.jpg", use_column_width=True)
        
        st.markdown("---")
        with st.form("google_login_form"):
            st.markdown("#### 🔐 Secure Authentication")
            google_email = st.text_input("Enter your Google ID / Corporate Email", placeholder="name@company.com")
            login_btn = st.form_submit_button("Sign in with Google")
            
            if login_btn:
                if google_email and ("@" in google_email):
                    st.session_state.logged_in = True
                    st.session_state.user_email = google_email
                    st.success("Authentication successful!")
                    st.rerun()
                else:
                    st.error("Please enter a valid Google ID / Email.")
    st.stop()

# ==========================================
# SIDEBAR & CORPORATE BRANDING (MDAS)
# ==========================================
st.sidebar.markdown("# 🏢 MDAS Portal")
if os.path.exists("mdas.jpg"):
    st.sidebar.image("mdas.jpg", width=180)
st.sidebar.caption(f"User: **{st.session_state.user_email}**")
st.sidebar.markdown("---")

app_page = st.sidebar.selectbox("Navigation Menu", [
    "2nd Page: Select & Create Rate Analysis", 
    "3rd Page: Market Rates Manager", 
    "Project BOQ Estimator & Report Export"
])

if st.sidebar.button("🚪 Log Out"):
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.rerun()

# ==========================================
# 2ND PAGE: SELECT ITEMS & CREATE ANALYSIS
# ==========================================
if app_page == "2nd Page: Select & Create Rate Analysis":
    st.title("📊 MDAS Rate Analysis Workbench")
    st.markdown("Select CPWD DSR heads and items to run left-side rate analysis, alter factors, or create custom Non-DSR items.")

    tab_dsr, tab_nondsr = st.tabs(["📁 CPWD DSR Items Analysis", "⚙️ Non-DSR Items (MDAS Code Assignment)"])

    # STANDARD DSR ITEMS TAB
    with tab_dsr:
        st.subheader("1. Select Head & Item as per DSR")
        
        col_h1, col_h2 = st.columns(2)
        with col_h1:
            dsr_head = st.selectbox("Select Head (As per DSR)", [
                "Chapter 4: Brick Work", 
                "Chapter 5: Reinforced Cement Concrete (RCC)", 
                "Chapter 6: Steel Reinforcement",
                "Chapter 11: Surface Dressing & Earthwork"
            ])
        with col_h2:
            if "Brick Work" in dsr_head:
                dsr_items = {
                    "4.1.1": "Providing and laying brick work with class 7.5 non-modular bricks in superstructure above plinth level up to floor V level in cement mortar 1:6",
                    "4.1.2": "Providing and laying brick work with class 7.5 non-modular bricks in superstructure above plinth level up to floor V level in cement mortar 1:4"
                }
            elif "RCC" in dsr_head:
                dsr_items = {
                    "5.1.2": "Providing and laying in position plain cement concrete 1:4:8 (1 cement : 4 coarse sand : 8 graded stone aggregate 40 mm nominal size)",
                    "5.2.1": "Reinforced cement concrete work in walls (any thickness) including attached pilasters, buttresses, plinth and string courses up to floor V level"
                }
            else:
                dsr_items = {
                    "6.1.1": "Steel reinforcement for R.C.C. work including straightening, cutting, bending, placing in position and binding all complete up to plinth level - TMT bars"
                }

            selected_code = st.selectbox("Select Item (As per DSR)", list(dsr_items.keys()), format_func=lambda x: f"{x}: {dsr_items[x][:65]}...")

        st.info(f"**Item Specification:** {dsr_items[selected_code]}")

        # Default DAR / DSR coefficients mapping basic material/labor requirements
        if selected_code in ["4.1.1", "4.1.2"]:
            required_inputs = [
                {"type": "Material", "name": "Common burnt clay F.P.S. (non modular) bricks class designation 7.5", "qty": 500, "unit": "1000 Nos"},
                {"type": "Material", "name": "Portland Cement (OPC-43 Grade)", "qty": 0.04, "unit": "tonne"},
                {"type": "Material", "name": "Coarse sand (zone III)", "qty": 0.30, "unit": "cum"},
                {"type": "Labor", "name": "Mason 1st class", "qty": 1.20, "unit": "day"},
                {"type": "Labor", "name": "Beldar", "qty": 3.50, "unit": "day"}
            ]
        elif selected_code in ["5.1.2", "5.2.1"]:
            required_inputs = [
                {"type": "Material", "name": "Portland Cement (OPC-43 Grade)", "qty": 0.12, "unit": "tonne"},
                {"type": "Material", "name": "Coarse sand (zone III)", "qty": 0.45, "unit": "cum"},
                {"type": "Labor", "name": "Mason 1st class", "qty": 0.80, "unit": "day"},
                {"type": "Labor", "name": "Beldar", "qty": 3.00, "unit": "day"}
            ]
        else:
            required_inputs = [
                {"type": "Material", "name": "Mild steel round bar 12 mm dia and below", "qty": 1.05, "unit": "quintal"},
                {"type": "Labor", "name": "Blacksmith 1st class", "qty": 0.50, "unit": "day"},
                {"type": "Labor", "name": "Beldar", "qty": 0.50, "unit": "day"}
            ]

        st.markdown("---")
        st.markdown("### 📋 Left-Side Create Analysis & Alter Analysis Workbench")
        st.markdown("Basic rates are automatically pulled from latest Market Rates. Use the form below to **add or subtract factors** (wastage, cartage, deductions).")

        if selected_code not in st.session_state.analysis_factors:
            st.session_state.analysis_factors[selected_code] = []

        subtotal = 0
        analysis_table = []

        # 1. Fetch Basic Rates from DSR Codes
        for inp in required_inputs:
            details = get_market_rate_details(inp['name'])
            unit_net_rate = details["net_rate"]
            total_amt = inp['qty'] * unit_net_rate
            subtotal += total_amt
            analysis_table.append({
                "Component Type": inp['type'],
                "Item Name (As in DAR)": inp['name'],
                "Quantity": inp['qty'],
                "Unit": inp['unit'],
                "Basic Rate (Auto-Synced) (₹)": unit_net_rate,
                "Last Updated Date": details["date"],
                "Vendor Details": details["vendor"],
                "Total Amount (₹)": round(total_amt, 2)
            })

        # 2. Add or Subtract Factors
        for idx, fac in enumerate(st.session_state.analysis_factors[selected_code]):
            fac_amt = fac['qty'] * fac['rate']
            if fac['is_subtraction']:
                fac_amt = -fac_amt
            subtotal += fac_amt
            analysis_table.append({
                "Component Type": f"Factor ({fac['category']})",
                "Item Name (As in DAR)": fac['name'],
                "Quantity": fac['qty'],
                "Unit": fac['unit'],
                "Basic Rate (Auto-Synced) (₹)": fac['rate'],
                "Last Updated Date": str(datetime.date.today()),
                "Vendor Details": "MDAS Custom Factor",
                "Total Amount (₹)": round(fac_amt, 2)
            })

        df_rate_analysis = pd.DataFrame(analysis_table)
        st.dataframe(df_rate_analysis, use_container_width=True)

        # Alter Analysis Form
        with st.form(key=f"alter_analysis_form_{selected_code}"):
            st.markdown("#### ➕ Add or ➖ Subtract Factors to Analysis")
            fc1, fc2, fc3, fc4, fc5 = st.columns(5)
            with fc1:
                f_name = st.text_input("Factor Description", placeholder="e.g., Steel Wastage / Special Transport")
            with fc2:
                f_cat = st.selectbox("Category", ["Wastage Allowance", "Cartage & Freight", "Extra Coefficient", "General Deduction"])
            with fc3:
                f_qty = st.number_input("Quantity / Multiplier", value=1.0, step=0.1)
            with fc4:
                f_rate = st.number_input("Rate (₹)", value=100.0, step=10.0)
                f_sub = st.checkbox("Subtract / Deduct this Factor")
            with fc5:
                st.write("")
                st.write("")
                apply_fac = st.form_submit_button("Update Analysis")
            
            if apply_fac and f_name:
                st.session_state.analysis_factors[selected_code].append({
                    "name": f_name,
                    "category": f_cat,
                    "qty": f_qty,
                    "rate": f_rate,
                    "is_deduction": f_sub
                })
                st.success("Factor successfully updated!")
                st.rerun()

        # CPWD Final Totals
        water_chg = subtotal * 0.01
        cost_w_water = subtotal + water_chg
        cp_oh = cost_w_water * 0.15
        final_grand_total = cost_w_water + cp_oh

        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("Subtotal", f"₹ {subtotal:,.2f}")
        mc2.metric("With Water Charges (1%)", f"₹ {cost_w_water:,.2f}")
        mc3.metric("Final Rate (incl. 15% OH & CP)", f"₹ {final_grand_total:,.2f} per {dsr_items[selected_code][:15]}...")

        # Excel Download
        csv_data = df_rate_analysis.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Rate Analysis Report as Excel/CSV",
            data=csv_data,
            file_name=f"mdas_rate_analysis_{selected_code}.csv",
            mime="text/csv"
        )

    # NON-DSR ITEMS TAB
    with tab_nondsr:
        st.subheader("⚙️ Non-DSR Items Analysis & MDAS Code Assignment")
        st.markdown("Assign custom codes prefixed with `MDAS-` and map them to any standard DSR chapter head.")

        with st.form("nondsr_create_form"):
            nd_chapter = st.selectbox("Assign to DSR Head / Chapter", [
                "Chapter 4: Brick Work", 
                "Chapter 5: Reinforced Cement Concrete (RCC)", 
                "Chapter 6: Steel Reinforcement",
                "Chapter 13: Repair Works"
            ])
            nd_code = st.text_input("Custom Code", value="MDAS-01", placeholder="e.g., MDAS-CIVIL-01")
            nd_desc = st.text_area("Non-DSR Item Description", placeholder="Enter complete specifications...")
            nd_unit = st.text_input("Unit", value="cum")
            nd_rate = st.number_input("Estimated Base Rate (₹)", min_value=0.0, value=2000.0, step=50.0)

            save_nondsr = st.form_submit_button("Register Non-DSR Item")
            if save_nondsr and nd_code and nd_desc:
                st.session_state.custom_dsr_items.append({
                    "item_code": nd_code,
                    "chapter": nd_chapter,
                    "description": nd_desc,
                    "unit": nd_unit,
                    "inputs": [{"type": "Non-DSR Direct", "name": nd_desc, "qty": 1.0, "unit": nd_unit, "rate": nd_rate}]
                })
                st.success(f"Successfully created Non-DSR item code `{nd_code}` under {nd_chapter}!")

        if st.session_state.custom_dsr_items:
            st.markdown("### Registered Non-DSR Items")
            df_nondsr = pd.DataFrame(st.session_state.custom_dsr_items)
            st.dataframe(df_nondsr[["item_code", "chapter", "description", "unit"]], use_container_width=True)

# ==========================================
# 3RD PAGE: MARKET RATE MANAGER
# ==========================================
elif app_page == "3rd Page: Market Rates Manager":
    st.title("🏷️ MDAS Market Rates Manager (DSR Auto-Sync)")
    st.markdown("Select basic codes/items from DSR schedule via dropdown list, update rates, GST, unit, vendor details, and dates. These rates automatically update basic rates across all rate analyses.")

    dsr_basic_library = [
        "Portland Cement (OPC-43 Grade)",
        "White Cement",
        "Coarse sand (zone III)",
        "Fine sand (zone IV)",
        "Mild steel round bar 12 mm dia and below",
        "Mild steel round bar above 12 mm dia",
        "Twisted steel/ deformed TMT bars Fe-500D",
        "Structural steel such as tees, angles channels and R.S. joists",
        "Common burnt clay F.P.S. bricks tile class designation 10",
        "Common burnt clay F.P.S. (non modular) bricks class designation 7.5",
        "Fly ash bricks conforming to I.S. 12894",
        "Mason 1st class",
        "Blacksmith 1st class",
        "Carpenter 1st class",
        "Beldar"
    ]

    selected_mkt_item = st.selectbox("🔍 Select Item from Basic Codes of DSR", ["-- Add Brand New Material --"] + dsr_basic_library)

    default_item_val = "" if selected_mkt_item == "-- Add Brand New Material --" else selected_mkt_item

    with st.form("market_rate_form"):
        st.subheader("Update / Add Market Rate Entry")
        mc1, mc2, mc3 = st.columns(3)
        with mc1:
            item_name_ui = st.text_input("Item Name (As in DAR)", value=default_item_val)
            code_ui = st.text_input("Col. / Code", placeholder="e.g., 0367")
        with mc2:
            rate_ui = st.number_input("Rate (₹) (Base)", min_value=0.0, value=5156.0, step=10.0)
            gst_ui = st.number_input("GST (%)", min_value=0.0, max_value=100.0, value=28.0, step=0.5)
        with mc3:
            unit_ui = st.text_input("Unit", value="tonne")
            vendor_ui = st.text_input("Vendor Details", placeholder="e.g., UltraTech / ACC")
            
        date_ui = st.date_input("Date", datetime.date.today())

        submit_mkt = st.form_submit_button("💾 Save Market Rate & Auto-Sync")
        if submit_mkt and item_name_ui:
            net_rate_calc = rate_ui + (rate_ui * gst_ui / 100.0)
            new_entry = {
                "Col. / Code": code_ui,
                "Item Name (as in DAR)": item_name_ui,
                "Rate (₹)": rate_ui,
                "Unit": unit_ui,
                "GST (%)": gst_ui,
                "Net Rate (₹)": round(net_rate_calc, 2),
                "Date": str(date_ui),
                "Vendor": vendor_ui
            }
            st.session_state.market_rates = pd.concat([st.session_state.market_rates, pd.DataFrame([new_entry])], ignore_index=True)
            st.success(f"Market rate for {item_name_ui} updated successfully! All analyses will reflect the latest price, date, and vendor.")
            st.rerun()

    st.markdown("### 📜 Market Rates Master Log (With Complete History)")
    st.dataframe(st.session_state.market_rates, use_container_width=True)

    # Excel / CSV Download Facility
    mkt_download_csv = st.session_state.market_rates.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Market Rates Log as Excel/CSV",
        data=mkt_download_csv,
        file_name="mdas_market_rates_log.csv",
        mime="text/csv"
    )

# ==========================================
# PROJECT BOQ ESTIMATOR & EXPORT
# ==========================================
elif app_page == "Project BOQ Estimator & Report Export":
    st.title("📋 MDAS Project Bill of Quantities (BOQ)")
    st.caption("Compiled by MDAS Engineering Team")
    st.markdown("Generate project estimates combining DSR and Non-DSR (`MDAS-`) items.")

    master_pool = [
        {"item_code": "4.1.1", "description": "Brick work class 7.5 in superstructure cm 1:6", "unit": "cum", "rate": 5400.0},
        {"item_code": "5.1.2", "description": "Plain cement concrete 1:4:8", "unit": "cum", "rate": 4850.0},
        {"item_code": "6.1.1", "description": "Steel reinforcement TMT bars Fe-500D", "unit": "quintal", "rate": 6800.0}
    ] + st.session_state.custom_dsr_items

    boq_sel = st.selectbox("Select Item for BOQ", [f"{i['item_code']}: {i['description'][:60]}... ({i['unit']})" for i in master_pool])
    sel_code = boq_sel.split(":")[0]
    matched_item = next(i for i in master_pool if i['item_code'] == sel_code)

    default_unit_rate = matched_item.get("rate", 2500.0)

    q_input = st.number_input(f"Enter Quantity in {matched_item['unit']}", min_value=1.0, value=25.0)
    r_input = st.number_input("Unit Rate (₹) [Overrideable]", value=float(default_unit_rate), step=10.0)

    if st.button("➕ Add Item to Project BOQ"):
        total_price = q_input * r_input
        st.session_state.boq_items.append({
            "Item Code": matched_item['item_code'],
            "Description": matched_item['description'],
            "Unit": matched_item['unit'],
            "Quantity": q_input,
            "Unit Rate (₹)": r_input,
            "Total Amount (₹)": round(total_price, 2)
        })
        st.success("Item added to project BOQ!")

    if st.session_state.boq_items:
        st.markdown("### Consolidated Project Estimate")
        df_project_boq = pd.DataFrame(st.session_state.boq_items)
        st.dataframe(df_project_boq, use_container_width=True)

        project_grand_total = df_project_boq["Total Amount (₹)"].sum()
        st.metric("Project BOQ Grand Total", f"₹ {project_grand_total:,.2f}")

        boq_csv_report = df_project_boq.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Full Project BOQ as Excel/CSV Report",
            data=boq_csv_report,
            file_name="mdas_project_boq_estimate.csv",
            mime="text/csv"
        )

        if st.button("Clear Project BOQ"):
            st.session_state.boq_items = []
            st.rerun()
