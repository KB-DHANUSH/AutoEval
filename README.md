# InkGrader 🖋

InkGrader is an AI-powered web application designed to automate the evaluation of handwritten documents using OCR (Optical Character Recognition) and intelligent agent systems. It provides a seamless experience for uploading scanned documents, extracting textual content, evaluating responses, and managing user authentication—all within a modern web interface.

## 🚀 Features

- 📷 OCR Integration: Extracts handwritten text using the OCR.Space API.
- 🤖 Evaluation Agents: Intelligent agents analyze and score extracted content.
- 🔐 User Authentication: Secure login/logout with JWT-based authentication.
- 📦 Modular Backend: Flask-based API with organized modules for OCR, Auth, Database, and Evaluation.
- 💻 Modern Frontend: Built with React + Vite for fast, responsive UI.
- 🌐 Cross-Origin Support: Enabled via CORS for frontend-backend communication.

---

## Installation

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd InkGrader-main/backend
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the Flask server:
   ```bash
   python app.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd ../demo-frontend
   ```

2. Install frontend dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

## Usage

1. Start both the backend and frontend servers.
2. Open your browser and navigate to the frontend app.
3. Log in or register a new account.
4. Upload a scanned handwritten document.
5. Let the evaluation agent process and grade the content.
6. View results and feedback directly in the app.

## Technologies Used

### Backend
- Flask (REST API)
- Flask-JWT-Extended (authentication)
- Flask-CORS
- OCR.Space API (OCR services)
- Python 3

### Frontend
- React
- Vite
- ESLint

## Configuration

Before running the app, make sure to set the following environment variables:

- `OCR_API_KEY`: Your OCR.Space API key for OCR functionality.
- `SECRET_KEY`: A secret key for Flask JWT authentication.

You can create a `.env` file and add these variables:
```bash
OCR_API_KEY=your_api_key_here
SECRET_KEY=your_secret_key_here
```

## Acknowledgments

- OCR.Space for their free OCR API.
- Flask for the backend framework.
- React and Vite for the frontend tools.
- The contributors and open-source community for making this project possible.

## Contributing

Contributions are welcome! Feel free to fork the repository, open issues, or submit pull requests.

## License

This project is licensed under the [MIT License](https://choosealicense.com/licenses/mit/).

## Contact

For any inquiries, please reach out to us at:
