# 🎨 Visual AutoView Frontend

A modern, interactive web interface for visualizing Home Assistant automation graphs and analyzing automation performance metrics.

## 📋 Overview

The Visual AutoView frontend is built with **Lit** (lightweight web components) and **vis-network** for graph visualization. It provides an intuitive interface for:

- 📊 Visualizing automation graphs (triggers → conditions → actions)
- 🔍 Searching and filtering automations
- 📈 Analyzing performance metrics and execution patterns
- 🔗 Understanding entity relationships and dependencies
- 🎨 Customizing themes and export formats

## 🛠 Tech Stack

- **Framework:** [Lit](https://lit.dev) (Web Components)
- **Graph Visualization:** [vis-network](https://visjs.github.io/vis-network)
- **HTTP Client:** [axios](https://axios-http.com)
- **Build Tool:** [Vite](https://vitejs.dev)
- **Language:** TypeScript
- **Package Manager:** npm

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app.ts                    # Main application component
│   ├── main.ts                   # Entry point
│   ├── components/
│   │   └── graph.ts              # Graph visualization component
│   ├── views/
│   │   ├── dashboard.ts          # Main dashboard view
│   │   └── analytics.ts          # Analytics panel view
│   ├── services/
│   │   └── api.ts                # API client service
│   └── utils/
│       └── helpers.ts            # Utility functions
├── index.html                    # HTML template
├── package.json                  # Dependencies & scripts
├── tsconfig.json                 # TypeScript configuration
├── vite.config.ts                # Build configuration
└── README.md                      # This file
```

## 🚀 Getting Started

### Prerequisites

- Node.js 16+ and npm
- Home Assistant instance running the Visual AutoView integration

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

### Development

```bash
# Start development server with hot reload
npm run dev

# Access at http://localhost:5173
```

### Build

```bash
# Build for production
npm run build

# Output in dist/ directory
```

### Preview

```bash
# Preview production build locally
npm run preview
```

## 🧩 Components

### 1. Graph Visualization (`components/graph.ts`)

Interactive graph display component using vis-network.

**Features:**
- Node type coloring (triggers, conditions, actions)
- Interactive zoom and pan
- Physics-based layout
- Click and double-click events
- Fit-to-view, center, and reset operations

**Usage:**
```html
<vav-graph
  .nodes=${nodesArray}
  .edges=${edgesArray}
  interactive
  theme="light"
></vav-graph>
```

### 2. Dashboard (`views/dashboard.ts`)

Main dashboard view with automation list, details, and graph.

**Features:**
- Automation list with search
- Detailed automation information
- Export and compare actions
- Integrated graph visualization
- Loading and error states

### 3. Analytics Panel (`views/analytics.ts`)

Advanced analytics with three tabs:

**Performance Tab:**
- Execution time statistics
- Success/failure rates
- Performance timeline

**Dependencies Tab:**
- Dependency graph
- Circular dependency detection
- Dependent automations list

**Entities Tab:**
- Entity relationships
- Related automations
- Relationship strength

### 4. API Client (`services/api.ts`)

Axios-based HTTP client for backend services.

**Methods:**
- `parseAutomation()` - Parse automation YAML
- `getAutomationGraph()` - Get graph structure
- `listAutomations()` - List all automations
- `searchAutomations()` - Full-text search
- `getPerformanceMetrics()` - Get performance data
- `getDependencyGraph()` - Get dependency structure
- `getEntityRelationships()` - Get entity relationships
- And 14 more methods...

## 🎨 Styling

The frontend uses CSS custom properties for theming:

```css
--primary-color: #2196F3
--accent-color: #FF9800
--divider-color: #e0e0e0
--panel-background: #f5f5f5
--card-background: white
--text-color: #000
--secondary-text: #666
--hover-background: #f0f0f0
```

Override in your CSS:

```css
vav-app {
  --primary-color: #1976D2;
  --accent-color: #FF6F00;
}
```

## 🔧 Configuration

### Vite Configuration

Built-in Vite configuration with:
- ES2020 target
- Source maps for debugging
- CSS handling
- Basic SSL support for development

### TypeScript Configuration

Strict mode enabled for type safety:
- `strict: true`
- Decorators enabled for Lit
- ES2020 lib support

## 🧪 Testing

```bash
# Run tests (when configured)
npm run test

# Run type checking
npm run type-check

# Run linting
npm run lint
```

## 📦 Dependencies

### Production
- **lit:** ^3.0.0 - Web components framework
- **vis-network:** ^9.1.0 - Graph visualization
- **axios:** ^1.6.0 - HTTP client

### Development
- **vite:** ^5.0.0 - Build tool
- **typescript:** ^5.0.0 - Type checking
- **@vitejs/plugin-basic-ssl:** ^1.0.0 - SSL support

## 🔐 API Integration

The frontend communicates with the Home Assistant backend via HTTP endpoints:

```typescript
// Initialize API client
const api = new VisualAutoViewApi();

// Call service methods
const automations = await api.listAutomations();
const metrics = await api.getPerformanceMetrics('automation.my_automation');
```

## 🌙 Dark Mode Support

Ready for dark mode implementation via CSS custom properties:

```css
@media (prefers-color-scheme: dark) {
  vav-app {
    --text-color: #fff;
    --panel-background: #1e1e1e;
    --card-background: #2d2d2d;
  }
}
```

## 🐛 Debugging

Enable debug logging:

```typescript
// In main.ts
if (import.meta.env.DEV) {
  window.__DEBUG__ = true;
}
```

## 📚 Resources

- [Lit Documentation](https://lit.dev)
- [vis-network Documentation](https://visjs.github.io/vis-network)
- [Vite Documentation](https://vitejs.dev)
- [Home Assistant Development](https://developers.home-assistant.io)

## 📝 License

Part of Visual AutoView - Home Assistant custom integration

---

**Ready to visualize your automations!** 🚀
