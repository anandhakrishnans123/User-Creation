import streamlit as st
import nest_asyncio
import asyncio
from playwright.async_api import async_playwright

# Apply nest_asyncio to allow nested async functions
nest_asyncio.apply()

st.title("User Management Automation")

# Get user credentials and target URL through Streamlit inputs
email = st.text_input("Enter your email:")
password = st.text_input("Enter your password:", type="password")
n = st.number_input("Enter the number of users to be added:", min_value=1, step=1)
target_url = "https://samesg.samcorporate.com/app/yxaaxdxgnwkuxi6sqxgxvt6ntp1/page/manage/users/list"

# Generate a list of email addresses dynamically
email_list = [f'anandhakrishnan+{i}@samcorporate.com' for i in range(n)]

# Define static user role and entity name
user_role_value = 'role A'  # Replace with actual role value from the dropdown
entity_name = 'IMPLEMENTATION'  # Replace with actual entity name

# Button to start automation
start_process = st.button("Start User Addition Process")

async def attempt_login(page):
    try:
        # Step 0: Clear cookies before login attempt
        await page.context.clear_cookies()

        # Step 1: Go to the login page
        await page.goto('https://samesg.samcorporate.com/')

        # Step 2: Wait for the "Login" button to be visible
        await page.wait_for_selector('text=Login', timeout=60000)
        await page.click('text=Login')

        # Step 3: Wait for the login page to load
        await page.wait_for_url('**/login', timeout=60000)

        # Step 4: Fill in the email and password
        await page.fill('input[name="email"]', email)
        await page.fill('input[name="password"]', password)

        # Step 5: Click the login button and wait for navigation
        await page.click('button[type="submit"]')

        # Step 6: Wait for the page to load after login
        await page.wait_for_load_state('networkidle', timeout=60000)

        # Step 7: Check if login was successful
        current_url = page.url
        if 'login' in current_url:
            st.error("Login failed: Still on the login page or redirected to login page.")
            return False  # Login failed
        else:
            st.success("LOGIN SUCCESSFUL!")
            for new_user_email in email_list:
                # Navigate to the target page
                await page.goto(target_url)
                await page.wait_for_load_state('networkidle', timeout=60000)

                # Step 8: Click the "Invite" button
                await page.wait_for_selector('text=Invite', timeout=60000)
                await page.click('text=Invite')

                # Step 9: Interact with the dropdowns and fill in the details
                await page.select_option('select#workspaceUserRoleId', user_role_value)
                await page.fill('input#react-select-3-input', entity_name)
                await page.keyboard.press('Enter')

                await page.fill('input#email', new_user_email)

                # Step 10: Click the 'Add User' button
                await page.click('button[type="submit"]:has-text("Add User")')

                # Wait for success indication
                await page.wait_for_load_state('networkidle', timeout=60000)

                st.success(f"New user {new_user_email} added successfully.")
            return True

    except Exception as e:
        st.error(f"Error during login attempt: {e}")
        return False

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Run in non-headless mode for debugging
        context = await browser.new_context()
        page = await context.new_page()

        # Attempt login and add users
        await attempt_login(page)

        # Close the page and browser when done
        await page.close()
        await browser.close()

if start_process:
    asyncio.run(main())
