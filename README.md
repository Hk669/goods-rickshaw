# Logistics Platform ( Goods-RickShaw )

A scalable logistics platform for managing vehicle bookings, real-time tracking, and fleet management. This platform allows users to book transportation services, track vehicles in real-time, and provides a streamlined interface for drivers and admins to manage jobs and analyze fleet performance.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Setup and Installation](#setup-and-installation)
- [Usage](#usage)
- [Environment Variables](#environment-variables)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Deployment](#deployment)
- [License](#license)

## Features

### User Features:
- **Booking Service**: Users can book a vehicle for transporting goods by specifying pickup and drop-off locations. The booking includes vehicle type and an estimated cost.
- **Real-Time Tracking**: Users can track the driver’s location in real-time after booking.
- **Price Estimation**: Provides an upfront price estimation based on distance, vehicle type, and current demand.

### Driver Features:
- **Job Assignment**: Drivers can receive and accept booking requests, view pickup and drop-off locations, and update the job status.
- **Job Status Updates**: Drivers can update job statuses such as en route, goods collected, and delivered.

### Admin Features:
- **Fleet Management**: Admins can manage vehicles, monitor driver activity, and analyze booking data.
- **Data Analytics**: Basic analytics to track completed trips, average trip time, and driver performance.

## Tech Stack

- **Backend**: Django (Python)
- **Frontend**: HTML, CSS, JavaScript (Google Maps API)
- **Database**: SQLite (for development), PostgreSQL (for production)
- **APIs**: Google Maps JavaScript API, Google Maps Geocoding API
- **Deployment**: Docker, Elastic Beanstalk (AWS)

## Setup and Installation

### Prerequisites
- Python 3.8+
- Django 4.x
- Google Maps API Key
- Docker (optional for deployment)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Hk669/goods-rickshaw.git
   cd goods-rickshaw
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Apply migrations:
   ```bash
   python manage.py migrate
   ```

5. Run the server:
   ```bash
   python manage.py runserver
   ```

6. Access the application at `http://127.0.0.1:8000`.

## Usage

### User
- Users can register, log in, and book a vehicle by providing the pickup and drop-off location using the map interface.
- Users can track their bookings and view real-time updates on the driver’s location.

### Driver
- Drivers can log in, view available jobs, and update job statuses (e.g., en route, goods collected, delivered).
- Drivers' locations are updated periodically using GPS.

### Admin
- Admins can manage vehicles, track trips, and generate analytics reports from the admin dashboard.

## Environment Variables

To run this project, you will need to add the following environment variables to your `.env` file:

```
SECRET_KEY=your_django_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=your_database_url  # For PostgreSQL or other databases
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
```

## Project Structure

```
goods-rickshaw/
│
├── bookings/
│   ├── migrations/
│   ├── templates/
│   ├── static/
│   ├── forms.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── drivers/
│   ├── migrations/
│   ├── forms.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── users/
│   ├── migrations/
│   ├── forms.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── manage.py
├── Dockerfile
├── requirements.txt
├── README.md
├── .env
└── logistics_platform/
    ├── settings.py
    ├── urls.py
    └── wsgi.py
```

## API Endpoints

### Booking Endpoints
- **POST** `/bookings/create/`: Create a new booking.
- **GET** `/bookings/track/<id>/`: Track an existing booking.
- **POST** `/bookings/update-status/`: Update the status of a booking (driver).

### Driver Endpoints
- **POST** `/drivers/update-location/`: Update the driver's location.
- **GET** `/drivers/jobs/`: View available jobs.

### Admin Endpoints
- **GET** `/admin/dashboard/`: View fleet and booking analytics.


## Deployment

To deploy the application using Docker:

1. Build the Docker image:
   ```bash
   docker build -t logistics-platform .
   ```

2. Run the Docker container:
   ```bash
   docker run -p 8000:8000 logistics-platform
   ```

3. Deploy to AWS Elastic Beanstalk:
   - Create an Elastic Beanstalk application and environment.
   - Deploy the Docker image to Elastic Beanstalk.

