import streamlit as st
import pandas as pd
import datetime

# Page Configuration
st.set_page_config(
    page_title="CPWD Rate Analysis Software | Developed by Dhamil Ahuja",
    page_icon="🏗️",
    layout="wide"
)

# Initialize Session State
if 'market_rates' not in st.session_state:
    st.session_state.market_rates = pd.DataFrame([
        {
            "Col. / Code": "M-01",
            "Item Name (as in DAR)": "Cement (OPC 43 Grade)",
            "Rate (₹)": 350.0,
            "Unit": "Bag",
            "GST (%)": 28.0,
            "Net Rate (₹)": 448.0,
            "Date": str(datetime.date.today()),
            "Vendor": "ABC Enterprises"
        },
        {
            "Col. / Code": "M-02",
            "Item Name (as in DAR)": "Coarse Sand",
            "Rate (₹)": 45.0,
            "Unit": "Cu.ft",
            "GST (%)": 5.0,
            "Net Rate (₹)": 47.25,
            "Date": str(datetime.date.today()),
            "Vendor": "Delhi Sands Ltd."
        }
    ])

if 'boq_items' not in st.session_state:
    st.session_state.boq_items = []

if 'custom_database' not in st.session_state:
    st.session_state.custom_database = []

if 'analysis_custom_factors' not in st.session_state:
    st.session_state.analysis_custom_factors = {}

# Mock Default Database mapping CPWD DSR Items
default_database = [
    {
        "item_code": "4.1.1",
        "chapter": "Chapter 4: Brick Work",
        "description": "Providing and laying brick work with class 7.5 non-modular bricks in superstructure above plinth level up to floor V level in cement mortar 1:6",
        "unit": "cum",
        "inputs": [
            {"type": "Material", "name": "Bricks (Class 7.5)", "qty": 500, "unit": "Nos", "rate": 7.0},
            {"type": "Material", "name": "Cement (OPC 43 Grade)", "qty": 0.82, "unit": "bags", "rate": 448.0},
            {"type": "Labor", "name": "Masons (Skilled)", "qty": 1.20, "unit": "Days", "rate": 650.0},
            {"type": "Labor", "name": "Unskilled Labor", "qty": 3.50, "unit": "Days", "rate": 500.0}
        ]
    }
]

def get_latest_market_rate(item_name):
    df_m = st.session_state.market_rates
    filtered = df_m[df_m["Item Name (as in DAR)"].str.lower() == item_name.lower()]
    if not filtered.empty:
        return float(filtered.iloc[-1]["Net Rate (₹)"])
    return 100.0

# Sidebar Branding & Navigation
st.sidebar.markdown("### 🏗️ CPWD Rate Analyzer")
st.sidebar.markdown("---")
# Custom Developer Branding
st.sidebar.info("💡 **Software Application**\n\n**Developed by:** Dhamil Ahuja")
st.sidebar.markdown("---")

menu = st.sidebar.selectbox("Navigation", [
    "Dashboard & Rate Analysis", 
    "Market Rates Manager (DAR)", 
    "Upload CPWD DAR/DSR File", 
    "Project BOQ Estimator"
])

# 1. DASHBOARD & RATE ANALYSIS
if menu == "Dashboard & Rate Analysis":
    st.title("📊 CPWD Rate Analysis & Factor Adjustments")
    st.caption("Professional Rate Analysis System — Developed by Dhamil Ahuja")
    st.markdown("View item breakdowns, add custom material factors (wastage, cartage, extra coefficients), and analyze final rates.")

    search_query = st.text_input("🔍 Search Item by Code or Description", "")
    all_items = default_database + st.session_state.custom_database

    for item in all_items:
        icode = item['item_code']
        if search_query.lower() in icode.lower() or search_query.lower() in item['description'].lower():
            with st.expander(f"**{icode}** - {item['description']} ({item['unit']})"):
                st.write(f"**Chapter:** {item['chapter']}")
                
                if icode not in st.session_state.analysis_custom_factors:
                    st.session_state.analysis_custom_factors[icode] = []

                subtotal = 0
                table_data = []
                
                for inp in item['inputs']:
                    current_rate = get_latest_market_rate(inp['name'])
                    total_cost = inp['qty'] * current_rate
                    subtotal += total_cost
                    table_data.append({
                        "Input Type": inp['type'],
                        "Description": inp['name'],
                        "Quantity": inp['qty'],
                        "Unit": inp['unit'],
                        "Unit Rate (₹)": current_rate,
                        "Amount (₹)": round(total_cost, 2)
                    })

                for idx, factor in enumerate(st.session_state.analysis_custom_factors[icode]):
                    f_cost = factor['qty'] * factor['rate']
                    subtotal += f_cost
                    table_data.append({
                        "Input Type": f"Custom ({factor['factor_type']})",
                        "Description": factor['name'],
                        "Quantity": factor['qty'],
                        "Unit": factor['unit'],
                        "Unit Rate (₹)": factor['rate'],
                        "Amount (₹)": round(f_cost, 2)
                    })
                
                df_inputs = pd.DataFrame(table_data)
                st.table(df_inputs)

                with st.form(key=f"factor_form_{icode}"):
                    st.subheader("➕ Add Custom Factor / Material (e.g., Wastage, Cartage, Extra Haulage)")
                    f_col1, f_col2, f_col3, f_col4 = st.columns(4)
                    with f_col1:
                        f_name = st.text_input("Factor/Material Name", placeholder="e.g., Steel Wastage / Extra Cartage")
                        f_type = st.selectbox("Category", ["Wastage Factor", "Cartage / Transport", "Extra Material", "Handling Charge"], key=f"type_{icode}")
                    with f_col2:
                        f_qty = st.number_input("Quantity / Multiplier", min_value=0.001, value=1.0, step=0.1, key=f"qty_{icode}")
                        f_unit = st.text_input("Unit", value="Nos/Cum/MT", key=f"unit_{icode}")
                    with f_col3:
                        f_rate = st.number_input("Unit Rate (₹)", min_value=0.0, value=50.0, step=1.0, key=f"rate_{icode}")
                    with f_col4:
                        st.write("")
                        st.write("")
                        add_factor_btn = st.form_submit_button("Add Factor to Analysis")
                    
                    if add_factor_btn and f_name:
                        st.session_state.analysis_custom_factors[icode].append({
                            "name": f_name,
                            "factor_type": f_type,
                            "qty": f_qty,
                            "unit": f_unit,
                            "rate": f_rate
                        })
                        st.success("Factor added successfully! Refreshing...")
                        st.rerun()

                water_charges = subtotal * 0.01 
                cost_with_water = subtotal + water_charges
                cp_and_oh = cost_with_water * 0.15 
                grand_total = cost_with_water + cp_and_oh

                col1, col2, col3 = st.columns(3)
                col1.metric("Base Cost Subtotal", f"₹ {subtotal:.2f}")
                col2.metric("With Water Charges (1%)", f"₹ {cost_with_water:.2f}")
                col3.metric("Final Rate (incl. 15% OH & CP)", f"₹ {grand_total:.2f} per {item['unit']}")

                csv_export = df_inputs.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label=f"📥 Download Rate Analysis ({icode}) as CSV",
                    data=csv_export,
                    file_name=f"rate_analysis_{icode}.csv",
                    mime="text/csv",
                    key=f"download_{icode}"
                )

# 2. MARKET RATES MANAGER PAGE
elif menu == "Market Rates Manager (DAR)":
    st.title("🏷️ Latest Market Rates Manager & Historical Log")
    st.caption("Managed via CPWD DAR Database — Developed by Dhamil Ahuja")
    st.markdown("Search or pick an existing material from the dropdown to update its rate. All historical rate changes are preserved and visible below.")

    existing_materials = sorted(st.session_state.market_rates["Item Name (as in DAR)"].unique().tolist())
    selection_options = ["-- Add Brand New Material --"] + existing_materials

    selected_material_action = st.selectbox("🔍 Search / Select Existing Material to Update", selection_options)

    default_code = ""
    default_unit = ""
    default_vendor = ""
    default_rate = 100.0
    default_gst = 18.0

    if selected_material_action != "-- Add Brand New Material --":
        matched_rows = st.session_state.market_rates[st.session_state.market_rates["Item Name (as in DAR)"] == selected_material_action]
        if not matched_rows.empty:
            latest_record = matched_rows.iloc[-1]
            default_code = str(latest_record["Col. / Code"])
            default_unit = str(latest_record["Unit"])
            default_vendor = str(latest_record["Vendor"])
            default_rate = float(latest_record["Rate (₹)"])
            default_gst = float(latest_record["GST (%)"])

    with st.form("market_rate_form"):
        st.subheader("Update / Add Rate Entry")
        col1, col2, col3 = st.columns(3)
        with col1:
            col_code = st.text_input("Col. / Code (e.g., M-05)", value=default_code)
            if selected_material_action == "-- Add Brand New Material --":
                item_name = st.text_input("Item Name (as in DAR)", placeholder="Enter new material name")
            else:
                item_name = st.text_input("Item Name (as in DAR)", value=selected_material_action, disabled=True)
                item_name_val = selected_material_action
        with col2:
            base_rate = st.number_input("Base Rate (₹)", min_value=0.0, value=default_rate, step=1.0)
            unit = st.text_input("Unit (e.g., Bag, Cum, MT, Nos)", value=default_unit)
        with col3:
            gst_pct = st.number_input("GST (%)", min_value=0.0, max_value=100.0, value=default_gst, step=0.5)
            vendor = st.text_input("Vendor Name", value=default_vendor)
        
        date_procured = st.date_input("Rate Effective Date", datetime.date.today())

        submitted = st.form_submit_button("Save Rate Entry (Preserves History)")
        if submitted:
            actual_item_name = item_name if selected_material_action == "-- Add Brand New Material --" else item_name_val
            if col_code and actual_item_name:
                net_rate = base_rate + (base_rate * gst_pct / 100.0)
                new_row = {
                    "Col. / Code": col_code,
                    "Item Name (as in DAR)": actual_item_name,
                    "Rate (₹)": base_rate,
                    "Unit": unit,
                    "GST (%)": gst_pct,
                    "Net Rate (₹)": round(net_rate, 2),
                    "Date": str(date_procured),
                    "Vendor": vendor
                }
                st.session_state.market_rates = pd.concat([st.session_state.market_rates, pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"Successfully recorded new rate entry for {actual_item_name}! Old records are safely saved.")
                st.rerun()
            else:
                st.warning("Please fill in the Code and Item Name.")

    st.subheader("📜 Complete Historical Market Rates Log (All Past & Current Rates)")
    st.dataframe(st.session_state.market_rates, use_container_width=True)

    rates_csv = st.session_state.market_rates.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Complete Market Rates Log as CSV",
        data=rates_csv,
        file_name="market_rates_dar_historical.csv",
        mime="text/csv"
    )

# 3. UPLOAD CPWD DAR/DSR FILE
elif menu == "Upload CPWD DAR/DSR File":
    st.title("📂 Upload CPWD DSR & DAR Sheets")
    st.caption("Data Uploader Module — Developed by Dhamil Ahuja")
    st.markdown("Upload your Excel schedule files to import items directly into your software database.")

    uploaded_file = st.file_uploader("Upload Excel / CSV Data File", type=["xlsx", "csv"])
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df_upload = pd.read_csv(uploaded_file)
            else:
                df_upload = pd.read_excel(uploaded_file)
            
            st.success("File uploaded successfully! Preview of data:")
            st.dataframe(df_upload.head(10), use_container_width=True)
            st.info("Your file is loaded in memory and ready to be mapped into project estimations.")
        except Exception as e:
            st.error(f"Error reading file: {e}")

# 4. PROJECT BOQ ESTIMATOR
elif menu == "Project BOQ Estimator":
    st.title("📋 Project Bill of Quantities (BOQ) Generator")
    st.caption("Project Estimation Module — Developed by Dhamil Ahuja")
    st.markdown("Build your comprehensive project estimate by combining multiple DSR items.")

    all_items = default_database + st.session_state.custom_database
    selected_item = st.selectbox("Select DSR Item", [f"{i['item_code']}: {i['description'][:60]}... ({i['unit']})" for i in all_items])
    item_code_selected = selected_item.split(":")[0]
    
    selected_obj = next(i for i in all_items if i['item_code'] == item_code_selected)

    base_sub = sum(inp['qty'] * get_latest_market_rate(inp['name']) for inp in selected_obj['inputs'])
    factor_sub = sum(f['qty'] * f['rate'] for f in st.session_state.analysis_custom_factors.get(item_code_selected, []))
    subtotal = base_sub + factor_sub
    
    final_rate = (subtotal * 1.01) * 1.15 

    quantity = st.number_input(f"Enter Quantity in {selected_obj['unit']}", min_value=1.0, value=10.0)
    
    if st.button("Add Item to Project BOQ"):
        total_amount = quantity * final_rate
        st.session_state.boq_items.append({
            "Item Code": selected_obj['item_code'],
            "Description": selected_obj['description'],
            "Unit": selected_obj['unit'],
            "Quantity": quantity,
            "Unit Rate (INR)": round(final_rate, 2),
            "Total Amount (INR)": round(total_amount, 2)
        })
        st.success("Item added to project BOQ successfully!")

    if st.session_state.boq_items:
        st.subheader("Current Project BOQ Summary")
        df_boq = pd.DataFrame(st.session_state.boq_items)
        st.dataframe(df_boq, use_container_width=True)

        project_total = df_boq["Total Amount (INR)"].sum()
        st.metric("Project Estimated Grand Total", f"₹ {project_total:,.2f}")

        boq_csv = df_boq.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Full Project BOQ as CSV",
            data=boq_csv,
            file_name="project_boq_estimate.csv",
            mime="text/csv"
        )
        
        if st.button("Clear BOQ"):
            st.session_state.boq_items = []
            st.rerun()
