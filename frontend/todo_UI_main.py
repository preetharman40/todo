import streamlit as st
from api_client import ApiClient # <-- Import your new client

st.set_page_config(page_title="To-Do List")
st.header("To-Do List")

if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None

#------------------------------ Login Page ------------------------------------
def show_login_page():
    st.subheader("Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            client = ApiClient() # Create a client
            token = client.login(username, password) # Call the client method
            if token:
                st.session_state.token = token
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    st.subheader("Register")
    with st.form("register_form"):
        reg_username = st.text_input("New Username")
        reg_password = st.text_input("New Password", type="password")
        reg_submitted = st.form_submit_button("Create New Account")

        if reg_submitted:
            client = ApiClient()
            response = client.register(reg_username, reg_password)
            if response:
                st.success(f"Welcome {response.get('username')}! Please log in.")

#-----------------------------DashBoard-------------------------------
def show_main_app():
    st.write(f"Welcome {st.session_state.username} to Your DashBoard")
    
    # Create ONE client for the whole dashboard
    client = ApiClient(token=st.session_state.token)

    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.rerun()
    
    # Add task form
    st.subheader("Add a New Task")
    with st.form("new_task_form", clear_on_submit=True):
        task_title = st.text_input("Task title")
        task_description = st.text_input("Task Description")
        submitted = st.form_submit_button("Add Task")

        if submitted and task_title: # <-- FIX: Logic must require a title
            if client.create_task(task_title, task_description):
                st.success("Task Added")
                st.rerun()
        elif submitted:
            st.warning("Task Title cannot be empty")

    # Display task List
    st.subheader("Your Tasks")
    st.divider()
    
    tasks = client.get_tasks()
    if tasks is not None: # Check if the API call was successful
        if not tasks:
            st.info("You have no tasks. Add one above!")
            
        for task in tasks:
            with st.container(border=True):
                # ... (Your column and display logic is perfect, no change needed)
                col1, col2, col3 = st.columns([0.8, 0.1, 0.1])
                with col1:
                    if task['is_complete']:
                        st.success(f"✓ {task['title']}")
                    else:
                        st.error(f"✗ {task['title']}")
                with col2:
                    if st.button("Toggle", key=f"toggle_{task['id']}"):
                        client.update_task(task['id'], not task['is_complete'])
                        st.rerun()
                with col3:
                    if st.button("Del", key=f"del_{task['id']}", type="primary"):
                        client.delete_task(task['id'])
                        st.rerun()
                if task['description']:
                    with st.expander("View Description"):
                        st.write(task['description'])
    else:
        st.error("Could not load tasks. Your session may have expired.")

# --- Main App "Router" ---
if st.session_state.token is None:
    show_login_page()
else:
    show_main_app()