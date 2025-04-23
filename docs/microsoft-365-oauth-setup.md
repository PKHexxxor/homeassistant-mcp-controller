# Setting up Microsoft 365 OAuth for MCP Controller

This guide will walk you through the process of setting up OAuth authentication for Microsoft 365 in the MCP Controller integration.

## 1. Create an Azure App Registration

1. Go to the [Azure Portal](https://portal.azure.com)
2. Navigate to "Azure Active Directory" > "App registrations"
3. Click "New registration"
4. Enter the following details:
   - Name: "Home Assistant MCP Controller" (or any name you prefer)
   - Supported account types: "Accounts in this organizational directory only" (for organizational accounts) or "Personal Microsoft accounts only" (for personal accounts)
   - Redirect URI: Select "Web" and enter `https://your-home-assistant-url:8123/api/mcp_controller/m365_oauth_callback`
     - Replace `your-home-assistant-url` with your actual Home Assistant URL
     - Make sure to use HTTPS if your Home Assistant uses it
5. Click "Register"

## 2. Configure API Permissions

1. In your new app registration, go to "API permissions"
2. Click "Add a permission"
3. Select "Microsoft Graph"
4. Choose "Delegated permissions"
5. Add the following permissions:
   - User.Read (for basic profile)
   - Mail.Read (for email access)
   - Calendars.Read (for calendar access)
   - Files.Read (for OneDrive access)
6. Click "Add permissions"
7. Click "Grant admin consent" if this is an organizational account (may require admin privileges)

## 3. Create Client Secret

1. Go to "Certificates & secrets"
2. Under "Client secrets", click "New client secret"
3. Add a description and select an expiration period
4. Click "Add"
5. **IMPORTANT**: Copy the secret value immediately - you won't be able to see it again!

## 4. Get Application ID

1. Go to the "Overview" page of your app registration
2. Copy the "Application (client) ID" - you'll need this for Home Assistant

## 5. Configure Home Assistant

1. Go to Home Assistant > Settings > Devices & Services
2. Click "Add Integration" and search for "MCP Controller"
3. Select "Microsoft 365" as the service type
4. Enter a name for your Microsoft 365 connection
5. Enter the Application (client) ID and client secret you obtained from Azure
6. Click "Submit"

## 6. Authenticate with Microsoft

1. Go to Developer Tools > Services in Home Assistant
2. Select the `mcp_controller.m365_login` service
3. Enter your service name in the "Service Name" field
4. Click "Call Service"
5. A browser window will open with the Microsoft login page
6. Sign in with your Microsoft account
7. Grant the requested permissions
8. The browser window will close automatically after successful authentication

## 7. Using Microsoft 365 Services

After successful authentication, you can use the following services:

- `mcp_controller.m365_list_emails` - Lists recent emails
- `mcp_controller.m365_list_calendar_events` - Lists upcoming calendar events

## Troubleshooting

If you encounter authentication issues:

1. Check that your redirect URI is correctly configured in Azure
2. Ensure your Home Assistant URL is accessible externally if using remote authentication
3. Verify that the correct permissions are granted in Azure
4. Try forcing a new login by setting the "force" parameter to true when calling the login service
5. Check the Home Assistant logs for detailed error messages

## Security Considerations

- The client secret should be kept confidential
- Authentication tokens are stored in memory and not persisted to disk
- Consider setting a reasonable expiration period for the client secret
- Review the permissions granted to ensure they match your needs