# Vishing & Smishing Defense Platform (VSDP)

VSDP is a cutting-edge cybersecurity platform designed to detect, analyze, and mitigate voice and SMS-based fraud (Vishing and Smishing) in the Indian landscape.

## Deployment with Docker

To run the VSDP environment using Docker, follow these instructions:

### 1. Pull the Base Image
```bash
docker pull node:24-slim
```

### 2. Start a Shell Session
```bash
docker run -it --rm --entrypoint sh node:24-slim
```

### 3. Verify Environment
```bash
node -v # Expected: v24.15.0
npm -v  # Expected: 11.12.1
```

## Local Development

### Installation
```bash
npm install
```

### Run Dev Server
```bash
npm run dev
```

## Features
- **Real-time SMS Scanning**: BERT-powered analysis of suspicious messages.
- **Live Call Monitoring**: Audio waveform analysis and transcription.
- **Honeypot Baiting**: Active defense mechanisms for scammer interception.
- **Blockchain Evidence**: Tamper-proof evidence collection for legal proceedings.
- **Auto-FIR Generation**: Compliance with IT Act 2000 and DPDP Act 2023.

## Tech Stack
- **Frontend**: Next.js 14, Tailwind CSS 4, Framer Motion
- **Backend/ML**: FastAPI, BERT, Whisper, RawNet2
- **Infrastructure**: Docker, Blockchain (Hyperledger)
