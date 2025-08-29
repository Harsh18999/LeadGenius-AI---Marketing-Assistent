A Flask-based web application for lead generation, company research, and personalized email outreach automation.

## Features

- **Lead Processing**:
  - Upload CSV files containing lead emails
  - Paste raw text with email addresses
  - Automatic extraction of names and domains

- **Company Research**:
  - Automated website scraping for company information
  - Important page detection (About, Services, etc.)
  - AI-powered company analysis and summary generation

- **Outreach Automation**:
  - AI-generated personalized email drafts
  - Email template management
  - Bulk email sending capabilities
  - Campaign tracking and status updates

- **AI Integration**:
  - Uses Together.ai's LLM (Llama-3.3-70B-Instruct-Turbo-Free)
  - Dynamic prompt engineering for different use cases
  - Markdown formatting for rich responses

## Technology Stack

- **Backend**: Python 3, Flask
- **Frontend**: HTML, CSS, JavaScript, Jinja2 templates
- **AI**: Together.ai API
- **Email**: SMTP (Gmail)
- **Data Processing**: Pandas, BeautifulSoup
- **Session Management**: Flask-Session

## Project Structure

```bash
LeadGenius AI/
├── app.py # Main application entry point
├── config.py # Configuration settings
├── requirements.txt # Python dependencies
├── README.md # This file
├── routes/
│ ├── init.py # Blueprint organization
│ ├── auth_routes.py # Authentication routes
│ ├── email_routes.py # Email related routes
│ ├── file_routes.py # File upload and processing routes
│ ├── llm_routes.py # LLM interaction routes
│ └── other_routes.py # other routes
├── services/
│ ├── init.py # Service exports
│ ├── email_service.py # Email sending functionality
│ ├── file_service.py # File processing functions
│ ├── llm_service.py # LLM interaction functions
│ └── web_scraper.py # Web scraping functions
├── templates/ # Flask templates
│ ├── index.html # Main page
│ ├── dashboard.html # Lead dashboard
│ └── campaign.html # Campaign management
└── static/ # Static files (CSS, JS, images)
```
## Usage Guide

1. **Upload Leads**:
   - Navigate to the home page
   - Upload a CSV file with email column or paste email addresses
   - System will process and extract company domains

2. **Review Company Information**:
   - View automatically scraped company data
   - See AI-generated summaries
   - Chat with the AI about specific companies

3. **Create Email Campaigns**:
   - Generate personalized email drafts
   - Edit subject lines and body content
   - Save drafts for future use

4. **Send Emails**:
   - Send individual test emails
   - Launch bulk email campaigns
   - Track sent emails and responses

## Troubleshooting


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
```
