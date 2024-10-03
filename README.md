
# 🗨️ Chatroom Backend

A simple chatroom backend built with FastAPI. This guide will help you get the backend running locally with Docker and Kafka.

## 🚀 Getting Started

### Prerequisites

Before starting, make sure you have the following installed on your host machine:

- **[Docker](https://docs.docker.com/get-docker/)** 🐳
- **[Docker Compose](https://docs.docker.com/compose/install/)** 📦
- **Kafka Service** 📡  
    You need a running Kafka service.

---

### 🛠️ Build and Run the Backend

1. **Clone the Repository**

   ```bash
   git clone <repository-url>
   cd chatroom-backend
   ```

2. **Build Docker Image** 🏗️  
   Use the provided `build.sh` script to create the Docker image:

   ```bash
   ./build.sh
   ```

3. **Start Docker Compose** ▶️  
   Launch the container with the following command:

   ```bash
   docker-compose up -d
   ```

   This will start the services defined in the `docker-compose.yml` file.

4. **Enter the Container** 🐧  
   Access the running container to start the backend service:

   ```bash
   docker exec -it <container_name> /bin/bash
   ```

   Replace `<container_name>` with your container's name, which you can find using:

   ```bash
   docker ps
   ```

5. **Run the Application** 🐍  
   Inside the container, navigate to the `app` directory and run the `main.py` file:

   ```bash
   python main.py
   ```

---

### 📋 Access the API Documentation

Once the backend is running, you can access the interactive API documentation by visiting:

- [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)

This will open up the **Swagger UI** for exploring the available endpoints.

---

### 🤝 Contributions

Contributions are welcome! Feel free to submit a pull request or open an issue to discuss changes.

Happy Coding! 👩‍💻👨‍💻
