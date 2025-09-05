# Overview

Giveaway Central is a web-based giveaway management platform built with Flask. The application allows users to participate in various giveaways and contests while providing administrators with tools to create, manage, and monitor giveaway activities. Users can sign in through Replit Auth, browse active giveaways, enter contests with one-click participation, and track their entry history through a personalized profile dashboard.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Web Framework Architecture
Built on Flask using a modular structure with separate files for routes, admin functionality, and models. The application follows the Model-View-Controller pattern with SQLAlchemy for ORM and Jinja2 templating for the frontend.

## Authentication System
Implements Replit Auth integration through Flask-Dance OAuth2 consumer blueprint. The authentication system includes:
- OAuth token storage in database with browser session tracking
- Flask-Login integration for session management
- Role-based access control with admin privileges
- Automatic user registration on first login

## Database Design
Uses SQLAlchemy ORM with the following core entities:
- **User**: Stores user profiles with Replit Auth integration, admin flags, and relationship to entries
- **OAuth**: Mandatory table for Replit Auth token storage with browser session keys
- **Giveaway**: Contest information including title, prize, description, dates, entry limits, and winner tracking
- **Entry**: Junction table linking users to giveaways they've participated in

## Frontend Architecture
Bootstrap 5 with dark theme provides responsive UI components. The template system includes:
- Base template with navigation and common elements
- Separate admin interface with dashboard and management tools
- User-facing pages for browsing and entering giveaways
- Custom CSS for enhanced styling and animations

## Admin Management System
Comprehensive admin panel featuring:
- Dashboard with statistics and recent activity overview
- Giveaway creation and editing capabilities
- User management with role assignment
- Entry tracking and winner selection tools

## Application Structure
- `main.py`: Application entry point
- `app.py`: Flask app initialization and database setup
- `routes.py`: Public user routes and authentication
- `admin.py`: Administrative functionality and routes
- `models.py`: Database models and relationships
- `replit_auth.py`: Authentication middleware and OAuth integration

# External Dependencies

## Authentication Service
- **Replit Auth**: OAuth2 provider for user authentication and authorization
- **Flask-Dance**: OAuth consumer integration library

## Database
- **SQLAlchemy**: ORM for database operations and model management
- Database configured through environment variable `DATABASE_URL`

## Frontend Libraries
- **Bootstrap 5**: CSS framework with dark theme variant
- **Bootstrap Icons**: Icon library for UI elements

## Python Packages
- **Flask**: Core web framework
- **Flask-Login**: User session management
- **Flask-SQLAlchemy**: Database integration
- **PyJWT**: JSON Web Token handling for authentication
- **Werkzeug**: WSGI utilities and middleware

## Environment Configuration
- `SESSION_SECRET`: Flask session encryption key
- `DATABASE_URL`: Database connection string
- Proxy fix middleware for proper HTTPS URL generation