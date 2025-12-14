# aionly-backend-dev

Backend server with Express, TypeScript, and TypeORM using modularized monolith architecture.

## 🏗️ Architecture

This project follows a **modularized monolith** architecture with the following structure:

```
src/
├── modules/
│   ├── auth/
│   │   ├── controllers/      # HTTP request handlers
│   │   ├── domain/           # Business logic (interactors/services)
│   │   ├── models/           # TypeORM entities
│   │   └── auth.routes.ts    # Route definitions
│   └── forums/
│       ├── controllers/
│       ├── domain/
│       └── models/
├── data-source.ts            # TypeORM configuration
└── index.ts                  # Application entry point
```

### Key Patterns

- **Interactor Pattern**: Services with a single public `run()` method handle business logic
- **OOP Approach**: Class-based controllers and services
- **TypeORM**: Object-Relational Mapping for database operations

## 🚀 Getting Started

### Prerequisites

- Node.js (v18 or higher)
- Docker & Docker Compose

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```

3. Copy environment variables:
   ```bash
   cp env.example .env
   ```

4. Start the MySQL database:
   ```bash
   docker-compose up -d
   ```

5. Start the development server:
   ```bash
   npm run dev
   ```

The server will run on `http://localhost:3000`

## 📝 Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run typeorm` - Run TypeORM CLI commands

## 🗄️ Database

The project uses PostgreSQL 17 running in Docker. The database connection is configured through environment variables:

- `DB_HOST` - Database host (default: localhost)
- `DB_PORT` - Database port (default: 5432)
- `DB_USERNAME` - Database username (default: postgres)
- `DB_PASSWORD` - Database password (default: password)
- `DB_DATABASE` - Database name (default: main)

### Managing Docker Database

Start database:
```bash
docker-compose up -d
```

Stop database:
```bash
docker-compose down
```

Stop and remove data:
```bash
docker-compose down -v
```

## 📚 API Documentation

### Interactive API Docs

The API documentation is available via Swagger UI at:
- **URL**: `http://localhost:3000/api-docs`

When the server is running, you can access the interactive API documentation in your browser. This interface allows you to:
- View all available endpoints
- See request/response schemas
- Test API calls directly from the browser

### Using with Swagger Editor

You can also view and edit the API documentation using [Swagger Editor](https://editor.swagger.io/):

1. Copy the contents of `openapi.yml` file from the project root
2. Go to https://editor.swagger.io/
3. Paste the contents into the editor
4. The documentation will be rendered on the right side

#### Protected Routes

For protected endpoints, include the JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## 🔧 Development

### Adding a New Module

1. Create module folder structure:
   ```
   src/modules/your-module/
   ├── controllers/
   ├── domain/
   └── models/
   ```

2. Create entities in `models/` (e.g., `entity-name.entity.ts`)
3. Create services in `domain/` (e.g., `create-entity.service.ts`)
4. Create controllers in `controllers/` (e.g., `your-module.controller.ts`)
5. Create routes file (e.g., `your-module.routes.ts`)
6. Register routes in `src/index.ts`

### Naming Conventions

- **Services/Interactors**: `kebab-case.service.ts` (e.g., `create-user.service.ts`)
- **Controllers**: `kebab-case.controller.ts` (e.g., `auth.controller.ts`)
- **Entities**: `kebab-case.entity.ts` (e.g., `user.entity.ts`)
- **Modules**: `kebab-case` (e.g., `auth`, `forums`)

## 📦 Technology Stack

- **Express.js** - Web framework
- **TypeScript** - Type-safe JavaScript
- **TypeORM** - ORM for database operations
- **PostgreSQL** - Relational database
- **Docker** - Containerization
- **Swagger UI** - API documentation
