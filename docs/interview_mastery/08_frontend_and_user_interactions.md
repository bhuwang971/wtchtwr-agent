# Frontend And User Interactions

## Stack

The frontend stack is visible in [`frontend/package.json`](../../frontend/package.json):

- React 18
- TypeScript
- Vite
- Tailwind CSS
- Zustand
- React Router
- Recharts
- Deck.gl / react-map-gl
- React Markdown
- Monaco Editor

So the frontend is not a toy chat page. It is a typed SPA with multiple analysis surfaces.

## Route Map

Routes are defined in [`frontend/src/App.tsx`](../../frontend/src/App.tsx):

| Route | Page |
| --- | --- |
| `/` | `ChatPage` |
| `/dashboard` | `DashboardPage` |
| `/history` | `HistoryPage` |
| `/data-export` | `DataExportPage` |
| `/ai-metrics` | `AiMetricsPage` |

The app shell also exposes links for Slackbot, Help, and About.

## State Management

Chat-level app state is managed in [`frontend/src/store/useChat.ts`](../../frontend/src/store/useChat.ts) using Zustand.

Important state:

- `conversations`
- `activeConversation`
- `loading`
- `focusMessageId`

Important assistant payload fields carried into the UI:

- `tables`
- `summary`
- `answer_text`
- `policy`
- `rag_snippets`
- `portfolio_triage`
- `confidence`
- `trace`
- `abstained`

Why this matters:

- the frontend is built to render structured AI outputs, not just text strings

## API Layer

The typed REST client is [`frontend/src/lib/api.ts`](../../frontend/src/lib/api.ts).

It defines functions for:

- conversations
- message send
- summaries
- exports
- summary email
- dashboard filters/view
- data explorer schema/query/export
- AI metrics

This is a thin client design: most logic stays in the backend, and the frontend mostly manages UX and rendering.

## Chat UX

### Main files

- [`frontend/src/pages/Chat.tsx`](../../frontend/src/pages/Chat.tsx)
- [`frontend/src/components/ChatInput.tsx`](../../frontend/src/components/ChatInput.tsx)
- [`frontend/src/components/Message.tsx`](../../frontend/src/components/Message.tsx)

### How it feels to a user

The user types a natural-language question, sees a streamed answer, and can inspect:

- tables
- snippets
- confidence
- AI trace
- export options
- summary/email actions

### Technical wiring

`Chat.tsx`:

- maintains pending assistant state during streaming
- stores `thread_id` in local storage
- syncs final conversation payloads into Zustand
- handles special commands like `dashboard` and `slackbot`

`Message.tsx`:

- resolves assistant text from payloads
- renders markdown
- renders tables
- renders confidence pills
- renders AI trace panels

## Dashboard Page

### Main file

- [`frontend/src/pages/Dashboard.tsx`](../../frontend/src/pages/Dashboard.tsx)

### What it does

- fetches dashboard filter metadata
- fetches dashboard insights
- renders:
  - map of listings
  - occupancy cards
  - revenue cards
  - guest experience charts
  - rating distribution
  - price summary
  - host property counts

### Tech choices

- Deck.gl for mapping
- Recharts for KPI charts
- Tailwind utility styling

Why this matters:

- the product is not only chat; it also has a conventional analytics dashboard

## Data Export / Explorer Page

### Main file

- [`frontend/src/pages/DataExport.tsx`](../../frontend/src/pages/DataExport.tsx)

### What it does

- loads safe schema metadata
- lets the user choose tables/columns/filters/sorts
- previews results
- shows generated SQL
- exports data
- emails exports

### Why it exists

- not every analytics user wants a narrated answer
- some users want tabular self-serve exploration and CSV export

## History Page

### Main file

- [`frontend/src/pages/History.tsx`](../../frontend/src/pages/History.tsx)

### What it does

- lists stored conversations
- reopens a conversation
- renames a conversation
- deletes a conversation

This is useful to mention because it shows the product treats conversations as persisted work objects, not disposable chat bubbles.

## AI Metrics Page

### Main file

- [`frontend/src/pages/AiMetrics.tsx`](../../frontend/src/pages/AiMetrics.tsx)

### What it does now

- shows benchmark pack ranking
- lets the user select a pack
- shows selected pack metrics
- shows trend history
- shows failed cases and slowest cases
- shows per-case details:
  - question
  - compact output
  - SQL preview
  - assertions

This is one of the strongest interview-demo surfaces in the repo because it makes the evaluation story visible in-product.

## Summary / Email Flow

Summary actions start in [`frontend/src/pages/Chat.tsx`](../../frontend/src/pages/Chat.tsx) and call:

- [`frontend/src/lib/api.ts::summarizeConversation`](../../frontend/src/lib/api.ts)
- [`frontend/src/lib/api.ts::sendSummaryEmail`](../../frontend/src/lib/api.ts)

The UI supports:

- concise summary
- detailed summary
- emailing either summary variant

Why this matters:

- the project is built around analyst/operator workflows, not only model demos

## Export Flow

Chat-level export actions in [`frontend/src/pages/Chat.tsx`](../../frontend/src/pages/Chat.tsx) call:

- [`frontend/src/lib/api.ts::exportMessage`](../../frontend/src/lib/api.ts)

Data Explorer export calls:

- [`frontend/src/lib/api.ts::exportDataExplorer`](../../frontend/src/lib/api.ts)

Possible delivery modes from the UI:

- download
- email
- Google Drive fallback for large files (backend-controlled)

## Slack / External Interaction

The frontend does not implement a deep Slack client. It mainly exposes links/commands that interact with backend Slack startup/status endpoints:

- `/api/slackbot/start`
- `/api/slackbot/status`

Relevant files:

- [`frontend/src/App.tsx`](../../frontend/src/App.tsx)
- [`frontend/src/pages/Chat.tsx`](../../frontend/src/pages/Chat.tsx)

## Styling

The frontend uses Tailwind CSS, configured in:

- [`frontend/tailwind.config.js`](../../frontend/tailwind.config.js)
- [`frontend/postcss.config.js`](../../frontend/postcss.config.js)
- [`frontend/src/index.css`](../../frontend/src/index.css)

The styling approach is utility-first rather than big hand-authored CSS modules.

## Strong Frontend Design Choices

- typed API contracts
- multiple product surfaces, not just chat
- trace and confidence are visible to the user
- benchmark diagnostics surfaced inside the app

## Weak Spots To Admit

- `Chat.tsx` and `Dashboard.tsx` are large files and carry a lot of mixed concerns
- the chat page uses direct `fetch` for streaming while other API calls go through `api.ts`, so the API abstraction is not perfectly uniform
- some UI text contains minor encoding artifacts, which is cosmetic but real

