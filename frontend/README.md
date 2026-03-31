# NM-Ride Frontend

React + TypeScript + Vite frontend for the NM-Ride shared transport and ride-sharing management application.

## Features

- Modern React with TypeScript
- Vite for fast development and building
- Tailwind CSS for styling
- shadcn/ui components
- Form handling with React Hook Form
- API integration with Axios
- Testing with Vitest and Playwright

## Getting Started

### Prerequisites

- Node.js 18+ and npm or bun
- Running NM-Ride backend on http://localhost:8000

### Installation

```bash
cd frontend
npm install
# or
bun install
```

### Development

```bash
npm run dev
# or
bun run dev
```

Application will be available at `http://localhost:3000`

### Build

```bash
npm run build
# or
bun run build
```

### Testing

```bash
# Unit tests
npm run test
# or
bun run test

# Watch mode
npm run test:watch
# or
bun run test:watch

# E2E tests
npx playwright test
```
