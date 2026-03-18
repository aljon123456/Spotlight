# Google Gemini AI Setup Guide

SpotLight now supports **Google Gemini AI** for intelligent parking assistance!

## What is Gemini?

Google's Gemini is a powerful AI that can understand natural language and provide context-aware answers about parking, subscriptions, and system questions. Instead of keyword matching, users can ask complex questions like:

- "What's the difference between Premium and VIP subscriptions?"
- "Why was I assigned this parking slot?"
- "Can I get a closer parking option?"
- "How does the parking assignment system work?"

## Setup Instructions

### Step 1: Get a Google API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click **"Get API Key"** 
3. Click **"Create API Key in new project"**
4. Copy your API key (it will be displayed on the screen)

**Note**: Google provides free access to Gemini API with rate limits. You get 60 requests per minute for free!

### Step 2: Add to Environment Variables

**For Development (Local):**

Add to your `.env` file in the backend folder:
```
GEMINI_API_KEY=your_api_key_here
```

Replace `your_api_key_here` with the API key you just created.

**For Production (Render.com):**

1. Go to your Render dashboard
2. Select your service
3. Go to **Settings** → **Environment**
4. Add a new variable:
   - Key: `GEMINI_API_KEY`
   - Value: `your_api_key_here`

### Step 3: Restart the Server

After adding the environment variable, restart your backend server:

```bash
cd backend
python manage.py runserver
```

## Testing Gemini

Once configured, the AI assistant will automatically use Gemini for answering questions:

1. Open the app and log in
2. Click the **🤖 Parking AI** button
3. Ask a question like: "What are the differences between Premium and VIP?"
4. The AI should respond intelligently!

## Features Powered by Gemini

✅ **Subscription Comparison** - Understand tiers and benefits
✅ **Assignment Explanation** - Why were you assigned to a specific slot
✅ **System Information** - How the parking algorithm works
✅ **Natural Language** - Ask in your own words, get intelligent answers
✅ **Context-Aware** - AI knows about your current assignment

## Fallback Behavior

If Gemini is not configured or has any issues:
- The system will fall back to keyword-based responses
- All core functionality remains available
- Users can still ask questions using the chat widget

## Troubleshooting

**"AI assistant is not configured"**
- Make sure you added `GEMINI_API_KEY` to your environment variables
- Restart the server after adding the variable
- Check that the API key is correct (no extra spaces)

**"Rate limit exceeded"**
- Google's free tier allows 60 requests per minute
- Wait a few moments and try again
- For production, you can upgrade to a paid plan

**"Could not generate a response"**
- The API might be temporarily unavailable
- Try asking a different question
- Check that the API key is valid

## Security Notes

⚠️ **NEVER share your API key**
- Keep it in environment variables, not in code
- Don't commit `.env` file to GitHub
- Rotate your key if it's accidentally exposed

## Cost Information

- **Google Generative AI (Gemini 1.5 Pro)**: FREE for development!
  - 60 requests per minute
  - No credit card required for free tier

- **For production/high volume**:
  - $0.075 per million input tokens
  - $0.30 per million output tokens
  - You can monitor usage in Google Cloud Console

## Documentation

- [Google AI Studio](https://aistudio.google.com/)
- [Generative AI SDK for Python](https://github.com/google/generative-ai-python)
- [API Documentation](https://ai.google.dev/)
