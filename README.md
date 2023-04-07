# ** DraftGPT**

This Python application listens to your Gmail inbox and generates draft responses for unread emails using OpenAI's ChatGPT API.

## **Setup**

### **Prerequisites**

- Python 3.6 or higher
- Google API client library for Python
- OpenAI Python package

You can install the required packages using the following commands:

```bash
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib openai
```

### **Google API Credentials**

1. Go to the **[Google API Console](https://console.developers.google.com/)** and sign in with your Google account.
2. Create a new project or select an existing one.
3. Click on "Enable APIs and Services" and enable the Gmail API.
4. Click on "Create credentials," and for "Which API are you using?" select "Gmail API."
5. For "Where will you be calling the API from?" choose "Desktop app."
6. Click "What credentials do I need?" and download the JSON file.
7. Save the JSON file as "credentials.json" in the same directory as the script.

**Note:** Since the app is not verified by Google, only the developer will be able to access their email using these credentials.

### **OpenAI API Key**

Replace the **`open_ai_api_key`** variable in the script with your OpenAI API key:

```
open_ai_api_key = "your_openai_api_key"
openai.api_key = open_ai_api_key
```

## **Running the Application**

Run the application using the following command:

```
python main.py
```

The application will prompt you to authorize access to your Gmail account. Follow the instructions, and once authorized, the script will start monitoring your inbox for unread emails. It will generate draft responses using ChatGPT API and create a new draft in your Gmail account for each unread email. It will then mark the email as read and continue to monitor for new emails.

The application checks for new emails every 5 minutes (300 seconds). You can modify the sleep time between checks by changing the **`time.sleep(300)`** value in the **`main()`** function.

## **Possible Improvements**

### 1. Webhooks Instead of Polling

Currently, the script checks for new emails every 5 minutes by polling the Gmail API. A more efficient approach would be to use webhooks or push notifications to receive updates whenever new emails arrive. This would minimize the number of unnecessary API calls and improve the responsiveness of the application.

To achieve this, you can use the **[Gmail API's push notifications](https://developers.google.com/gmail/api/guides/push)** feature, which sends updates to a specified Cloud Pub/Sub topic. You would need to set up a Cloud Pub/Sub topic and a webhook endpoint in your application to process incoming notifications.

### 2. Using the Whole Thread as Context

The current implementation only considers the most recent email in a thread when generating a draft response. To improve the quality and relevance of the generated responses, you can include the entire email thread as context when sending the prompt to the ChatGPT API.

To do this, you would need to retrieve all messages in the email thread and include their content in the user message in the conversation. This way, the model will have a more complete understanding of the conversation's context and can generate better responses.

### 3. Utilizing GPT-4 (when available)

As of now, this script is using the GPT-3.5-turbo model from OpenAI. When GPT-4 becomes available, you can improve the performance of the application by updating the **`generate_response`** function to use the newer model. This may result in more accurate and context-aware draft responses. To update the model, you would simply need to replace the **`model`** parameter in the **`openai.ChatCompletion.create()`** function call.

### 4. Add Filtering 

Add an intelligent email filtering to focus on specific types of emails that require responses, such as those with specific keywords or from certain senders. This can help prioritize important emails and improve the usefulness of the generated drafts.

### 5. Generate Embeddings from Past E-mails to Provide Better Context / Prompts

Index all of your old emails with an embeddings model, such as sentence or document embeddings, and use that as an additional context to improve and write drafts that sound more like your previous emails. This could help in making the AI-generated responses sound more personalized and in line with your communication style.