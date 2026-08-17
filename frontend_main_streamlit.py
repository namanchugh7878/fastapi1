import streamlit as st
import requests

# FastAPI backend (from main.py)
API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Patient Management System", layout="wide")
st.title("Patient Management System")

# Sidebar navigation
page = st.sidebar.radio(
    "Choose an action",
    ["View all patients", "Get patient by ID", "Create patient", "Edit patient", "Delete patient", "Sort patients"],
)


def get_patients():
    r = requests.get(f"{API_BASE_URL}/view", timeout=10)
    r.raise_for_status()
    return r.json()


def create_patient(payload: dict):
    r = requests.post(f"{API_BASE_URL}/create", json=payload, timeout=10)
    return r


def update_patient(patient_id: str, payload: dict):
    r = requests.put(f"{API_BASE_URL}/edit/{patient_id}", json=payload, timeout=10)
    return r


def delete_patient(patient_id: str):
    r = requests.delete(f"{API_BASE_URL}/delete/{patient_id}", timeout=10)
    return r


def sort_patients(sort_by: str, order: str):
    r = requests.get(
        f"{API_BASE_URL}/sort",
        params={"sort_by": sort_by, "order": order},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()


# Pages
if page == "View all patients":
    st.subheader("All patients")
    try:
        patients = get_patients()
        st.write(f"Total records: {len(patients)}")
        st.json(patients)
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch patients: {e}")

elif page == "Get patient by ID":
    st.subheader("Get patient")
    patient_id = st.text_input("Patient ID (e.g., P001)", value="P001")
    if st.button("Fetch"):
        try:
            r = requests.get(f"{API_BASE_URL}/patient/{patient_id}", timeout=10)
            if r.status_code == 200:
                st.json(r.json())
            else:
                st.error(f"Error {r.status_code}: {r.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")

elif page == "Create patient":
    st.subheader("Create patient")
    with st.form("create_patient_form", clear_on_submit=True):
        patient_id = st.text_input("ID", value="P001")
        name = st.text_input("Name", value="")
        city = st.text_input("City", value="")
        age = st.number_input("Age", min_value=1, max_value=119, value=30)
        gender = st.selectbox("Gender", ["male", "female", "others"])
        height = st.number_input("Height (m)", min_value=0.1, value=1.7)
        weight = st.number_input("Weight (kg)", min_value=0.1, value=65.0)

        submitted = st.form_submit_button("Create")

    if submitted:
        payload = {
            "id": patient_id,
            "name": name,
            "city": city,
            "age": age,
            "gender": gender,
            "height": height,
            "weight": weight,
        }
        try:
            r = create_patient(payload)
            if r.status_code == 201:
                st.success(r.json().get("message", "Patient created"))
            else:
                st.error(f"Error {r.status_code}: {r.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")

elif page == "Edit patient":
    st.subheader("Edit patient")
    patient_id = st.text_input("Patient ID to edit", value="P001")

    with st.form("edit_patient_form"):
        st.caption("Leave fields empty to not update them.")

        name = st.text_input("Name", value="")
        city = st.text_input("City", value="")
        age = st.number_input("Age", min_value=0, value=0, step=1)
        gender = st.selectbox("Gender", ["", "male", "female"], index=0)
        height = st.number_input("Height (m)", min_value=0.0, value=0.0, step=0.1)
        weight = st.number_input("Weight (kg)", min_value=0.0, value=0.0, step=0.1)

        submitted = st.form_submit_button("Update")

    if submitted:
        payload = {}
        if name.strip():
            payload["name"] = name
        if city.strip():
            payload["city"] = city
        if age != 0:
            payload["age"] = int(age)
        if gender.strip():
            payload["gender"] = gender
        if height != 0.0:
            payload["height"] = float(height)
        if weight != 0.0:
            payload["weight"] = float(weight)

        try:
            r = update_patient(patient_id, payload)
            if r.status_code == 200:
                st.success(r.json().get("message", "Patient updated"))
            else:
                st.error(f"Error {r.status_code}: {r.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")

elif page == "Delete patient":
    st.subheader("Delete patient")
    patient_id = st.text_input("Patient ID to delete", value="P001")

    if st.button("Delete", type="primary"):
        try:
            r = delete_patient(patient_id)
            if r.status_code == 200:
                st.success(r.json().get("message", "Patient deleted"))
            else:
                st.error(f"Error {r.status_code}: {r.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")

elif page == "Sort patients":
    st.subheader("Sort patients")
    sort_by = st.selectbox("Sort by", ["height", "weight", "bmi"], index=0)
    order = st.selectbox("Order", ["asc", "desc"], index=0)

    if st.button("Sort"):
        try:
            sorted_list = sort_patients(sort_by, order)
            st.json(sorted_list)
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")

