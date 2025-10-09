# 🎵 Band Manager

A comprehensive full-stack application for managing bands, events, venues, and members. Built with modern technologies and deployed to production.

## 🌐 Live Application

- **Frontend**: [https://bandmanager.tcbarzyk.dev](https://bandmanager.tcbarzyk.dev)
- **Backend API**: [https://bandmanager.api.tcbarzyk.dev](https://bandmanager.api.tcbarzyk.dev)

## ✨ Features

### 🎤 Band Management
- Create and manage multiple bands
- Invite members with join codes
- Role-based permissions (admin, member)
- Band member management

### 📅 Event Management
- Schedule band performances and rehearsals
- Track event details (date, time, description)
- Link events to specific venues
- Event CRUD operations for band members

### 🏟️ Venue Management
- Create and manage performance venues
- Store venue details (name, location, capacity)
- Associate venues with events
- Venue database for reuse across events

### 👥 User Management
- Secure user authentication with Supabase
- User profiles with customizable information
- Multi-band membership support
- Protected routes and API endpoints

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Authentication**: Supabase Auth
- **HTTP Client**: Fetch API
- **Deployment**: Vercel

### Backend
- **Framework**: FastAPI (Python)
- **Database**: Supabase PostgreSQL with SQLAlchemy (Async)
- **Authentication**: Supabase Auth + JWT
- **ORM**: SQLAlchemy with Alembic migrations
- **API Documentation**: Automatic OpenAPI/Swagger
- **Deployment**: DigitalOcean Droplet with Nginx

### Infrastructure
- **Frontend Hosting**: Vercel
- **Backend Hosting**: DigitalOcean
- **Database**: Supabase (Managed PostgreSQL)
- **Authentication**: Supabase Auth
- **CI/CD**: GitHub Actions
- **SSL**: Let's Encrypt
- **Reverse Proxy**: Nginx

## 📁 Project Structure

```
band-manager/
├── .github/
│   └── workflows/         # GitHub Actions CI/CD pipelines
├── api/                    # FastAPI Backend
│   ├── main.py            # FastAPI application entry point
│   ├── models.py          # SQLAlchemy database models
│   ├── schemas.py         # Pydantic request/response schemas
│   ├── database.py        # Database connection and session management
│   ├── repository.py      # Database operations and business logic
│   ├── auth.py            # Authentication middleware and utilities
│   ├── alembic/           # Database migrations
│   ├── tests/             # API tests
│   └── requirements.txt   # Python dependencies
├── web/band-manager/      # Next.js Frontend
│   ├── app/               # Next.js app directory
│   │   ├── components/    # Reusable React components
│   │   ├── auth/          # Authentication pages
│   │   ├── bands/         # Band management pages
│   │   └── dashboard/     # Dashboard pages
│   ├── contexts/          # React contexts (Auth)
│   ├── lib/               # Utilities and API client
│   └── package.json       # Node.js dependencies
├── docs/                  # Documentation
├── infra/                 # Infrastructure configurations
└── README.md              # This file
```

## 📊 API Documentation

The API provides comprehensive endpoints for managing bands, events, venues, and users. Full documentation is available at:

- **Development**: `http://localhost:8000/docs`
- **Production**: `https://bandmanager.api.tcbarzyk.dev/docs`

### Key Endpoints

#### Authentication
- `GET /auth/me` - Get current user profile
- `PUT /auth/me` - Update current user profile

#### Bands
- `POST /bands` - Create a new band
- `GET /my/bands` - Get current user's bands
- `GET /bands/{id}` - Get band details
- `POST /bands/join/{code}` - Join band with code

#### Events
- `POST /bands/{id}/events` - Create event for band
- `GET /bands/{id}/events` - Get band events
- `PUT /events/{id}` - Update event
- `DELETE /events/{id}` - Delete event

#### Venues
- `POST /bands/{id}/venues` - Create venue for band
- `GET /bands/{id}/venues` - Get band venues
- `PUT /venues/{id}` - Update venue
- `DELETE /venues/{id}` - Delete venue

## 🔒 Security Features

- **JWT Authentication** with Supabase
- **CORS Configuration** for cross-origin requests
- **Input Validation** with Pydantic schemas
- **SQL Injection Protection** with SQLAlchemy ORM
- **Rate Limiting** and security headers
- **HTTPS/SSL** in production
- **Environment Variable** protection


## 🚀 Getting Started

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.9+
- **Supabase** account (for database and authentication)

### Environment Variables

#### Backend (.env)
```bash
# Supabase Database (get from Supabase dashboard)
DATABASE_URL=postgresql://postgres:[password]@[host]:[port]/postgres

# Supabase Authentication (get from Supabase dashboard)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_JWT_SECRET=your_supabase_jwt_secret
```

#### Frontend (.env.local)
```bash
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Local Development Setup

#### 1. Clone the Repository
```bash
git clone https://github.com/tcbarzyk/band-manager.git
cd band-manager
```

#### 2. Backend Setup
```bash
cd api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the development server
python main.py
# Or use uvicorn directly:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

#### 3. Frontend Setup
```bash
cd web/band-manager

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Database Setup

#### 1. Supabase Setup
1. Create a [Supabase](https://supabase.com) account
2. Create a new project
3. Go to **Settings > Database** to get your connection string
4. Go to **Settings > API** to get your project URL and anon key
5. Go to **Settings > Auth** to configure authentication providers

#### 2. Environment Configuration
```bash
# Get these values from your Supabase dashboard:
# Settings > Database > Connection string (URI)
DATABASE_URL=postgresql://postgres:[password]@[host]:[port]/postgres

# Settings > API
SUPABASE_URL=https://[project-id].supabase.co
SUPABASE_KEY=[anon-key]
SUPABASE_JWT_SECRET=[jwt-secret]
```

#### 3. Run Migrations
```bash
cd api
# The database tables will be created automatically via SQLAlchemy
alembic upgrade head
```

## 🔄 CI/CD Pipeline

This project uses **GitHub Actions** for deployment automation.

### Deployment Strategy

- **Frontend (Vercel)**: Automatic deployment on push to `main` branch via Vercel GitHub integration
- **Backend (DigitalOcean)**: Deployment using GitHub Actions for automated server updates

### Workflow Overview

The CI/CD pipeline handles:
- Automated backend deployment to DigitalOcean droplet
- Environment variable management
- Service restarts and health checks

## 🌐 Production Deployment

### Backend Deployment (DigitalOcean)

#### 1. Server Setup
```bash
# Create DigitalOcean droplet (Ubuntu 22.04)
# SSH into your server

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv nginx postgresql-client -y

# Install Node.js (for any build tools)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### 2. Application Deployment
```bash
# Clone repository
git clone https://github.com/tcbarzyk/band-manager.git
cd band-manager/api

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
sudo nano /etc/environment
# Add your production environment variables

# Run migrations
alembic upgrade head
```

#### 3. Process Manager (PM2 or systemd)
```bash
# Install PM2
sudo npm install -g pm2

# Start application
pm2 start "uvicorn main:app --host 0.0.0.0 --port 8000" --name band-manager-api

# Save PM2 configuration
pm2 save
pm2 startup
```

#### 4. Nginx Configuration
```nginx
server {
    server_name bandmanager.api.tcbarzyk.dev;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Proxy to FastAPI
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }

    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/bandmanager.api.tcbarzyk.dev/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/bandmanager.api.tcbarzyk.dev/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}

server {
    if ($host = bandmanager.api.tcbarzyk.dev) {
        return 301 https://$host$request_uri;
    }
    
    listen 80;
    server_name bandmanager.api.tcbarzyk.dev;
    return 404;
}
```

#### 5. SSL Certificate
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d bandmanager.api.tcbarzyk.dev
```

### Frontend Deployment (Vercel)

#### 1. Vercel CLI Setup
```bash
npm install -g vercel
```

#### 2. Deploy
```bash
cd web/band-manager

# Login to Vercel
vercel login

# Deploy
vercel --prod

# Configure environment variables in Vercel dashboard
# Set NEXT_PUBLIC_API_URL to your production API URL
```

#### 3. Custom Domain
- Add your custom domain in Vercel dashboard
- Configure DNS to point to Vercel

## 🧪 Testing

### Backend Tests
```bash
cd api
python -m pytest tests/ -v
```

## 🚧 Troubleshooting

### Common Issues

#### CORS Errors
If you encounter CORS errors in production:
1. Ensure your frontend domain is in the CORS allowed origins
2. Check that credentials are properly configured
3. Verify no duplicate CORS headers from reverse proxy

#### Database Connection Issues
```bash
# Test Supabase connection
# Go to Supabase dashboard > Settings > Database > Connection pooler
# Use the connection string provided there

# Verify environment variables
echo $DATABASE_URL
echo $SUPABASE_URL
```

#### Authentication Issues
1. Verify Supabase configuration
2. Check JWT secret matches between frontend and backend
3. Ensure cookies/tokens are properly set

## 📈 Future Enhancements

- [ ] Mobile app (React Native)
- [ ] Real-time notifications
- [ ] Calendar integration
- [ ] File upload for band photos
- [ ] Payment integration for events
- [ ] Analytics dashboard
- [ ] Email notifications
- [ ] Advanced reporting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Teddy Barzyk**
- GitHub: [@tcbarzyk](https://github.com/tcbarzyk)
- Website: [tcbarzyk.dev](https://tcbarzyk.dev)

## 🙏 Acknowledgments

- FastAPI for the excellent Python web framework
- Next.js for the powerful React framework
- Supabase for authentication and database services
- Vercel and DigitalOcean for hosting platforms
- Github Copilot for assisting in debugging and feature implementation