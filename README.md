# Mimic AI

An AI agent that mimics a person's behavior and can text for them on WhatsApp. Upload your WhatsApp chat exports to train the AI to mimic your texting style.

## Features

- 📱 WhatsApp-like chat interface
- 🤖 AI mode toggle for automated responses
- 📄 Upload WhatsApp chat exports (.txt files)
- 💬 Real-time chat interface
- 🎨 Modern, responsive design

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

1. Install dependencies:
```bash
npm install
```

2. Run the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

## How to Export WhatsApp Chats

1. Open WhatsApp on your phone
2. Go to the chat you want to export
3. Tap the three dots menu (Android) or chat name (iOS)
4. Select "More" → "Export chat"
5. Choose "Without Media"
6. Save the .txt file
7. Upload it in the Mimic AI interface

## Next Steps

- [ ] Parse WhatsApp chat exports to extract conversation data
- [ ] Train AI model on user's texting patterns
- [ ] Integrate AI API for generating responses
- [ ] Add WhatsApp integration for sending messages
- [ ] Implement user authentication
- [ ] Add chat history and persistence

## Tech Stack

- Next.js 14
- React 18
- TypeScript
- Tailwind CSS

## License

MIT