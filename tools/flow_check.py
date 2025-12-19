import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
import streamlit as st
from app_assisted import parse_text_dictionary, endpoint_auto_treatment, endpoint_validate_and_continue, change_current_index

# Prepare a small DataFrame with non-consecutive IDs
ids = [1, 3, 7, 20, 56, 100, 250, 400]
texts = ["Probleme reseau"] * len(ids)

df = pd.DataFrame({"ID": ids, "texte": texts})
current = {"df": df, "id_col": "ID", "txt_col": "texte", "sheet": "test_sheet", "question": "Q1"}

# Set session state minimal environment
st.session_state["all_sheets"] = [current]
st.session_state["current_sheet_idx"] = 0
st.session_state["processed_sheets"] = []

# Use the sample dictionary parsed from tools/parse_test (we'll paste partial)
text = '''1 Indisponibilité totale du réseau 1, 27, 37, 296, 306, 384, 414
2 Réseau instable / coupures fréquentes 3, 10, 30, 59
3 Mauvaise couverture 56, 138
'''

codebook = parse_text_dictionary(text)
print("Parsed codebook:")
print(codebook)

# Run automatic treatment
res = endpoint_auto_treatment(current, 0, codebook, max_codes=2)
print("Auto treatment result:", res)

# Check manual result
print("Result manual frame in session state key result_manual_0 present?", f"result_manual_0" in st.session_state)
if f"result_manual_0" in st.session_state:
    print(st.session_state[f"result_manual_0"].head())

# Simulate user editing: use result_manual as edited_df
edited_df = st.session_state.get(f"result_manual_0") if f"result_manual_0" in st.session_state else st.session_state.get(f"result_auto_0")

# Validate and continue
val = endpoint_validate_and_continue(current, 0, edited_df, codebook)
print("Validate and continue returned:", val)
print("Processed sheets:", st.session_state.get("processed_sheets"))
print("Current sheet idx:", st.session_state.get("current_sheet_idx"))
