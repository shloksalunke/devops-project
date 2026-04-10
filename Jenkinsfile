pipeline {
    agent any

    environment {
        CI = 'true'
        NODE_ENV = 'production'

        // 🔐 Pull SECRET_KEY securely from Jenkins Credentials Store
        SECRET_KEY = credentials('SECRET_KEY')
    }

    stages {

        // ── 1. CHECKOUT ──────────────────────────────────────────────
        stage('Checkout Code') {
            steps {
                echo 'Cloning repository from GitHub...'
                git branch: 'main',
                    url: 'https://github.com/shloksalunke/devops-project.git'
            }
        }

        // ── 2. BACKEND SETUP ─────────────────────────────────────────
        stage('Backend: Setup') {
            steps {
                dir('backend') {
                    echo 'Setting up Python virtual environment...'
                    bat '''
                    "C:\\Users\\shlok\\AppData\\Local\\Programs\\Python\\Python312\\python.exe" -m venv venv
                    venv\\Scripts\\python.exe -m pip install --upgrade pip
                    venv\\Scripts\\pip.exe install -r requirements.txt
                    echo Backend setup completed
                    '''
                }
            }
        }

        // ── 3. FRONTEND BUILD ────────────────────────────────────────
        stage('Frontend: Build') {
            steps {
                dir('frontend') {
                    echo 'Installing dependencies and building frontend...'
                    bat '''
                    npm install
                    npm run build
                    '''
                }
            }
        }

        // ── 4. DOCKER BUILD ──────────────────────────────────────────
        stage('Docker: Build') {
            steps {
                echo 'Building Docker images using production compose file...'
                bat 'docker-compose -f docker-compose.prod.yml build'
            }
        }

        // ── 5. DOCKER RUN ────────────────────────────────────────────
        stage('Docker: Run') {
            steps {
                echo 'Starting containers — SECRET_KEY injected from Jenkins credentials...'
                bat '''
                docker-compose -f docker-compose.prod.yml down --volumes
                docker-compose -f docker-compose.prod.yml up -d
                '''
            }
        }

        // ── 6. DB MIGRATION ──────────────────────────────────────────
        stage('Docker: Migrate DB') {
            steps {
                echo 'Running Alembic migrations on fresh database...'
                bat '''
                ping 127.0.0.1 -n 12 > nul
                docker-compose -f docker-compose.prod.yml exec -T api alembic upgrade head
                '''
            }
        }
    }

    post {
        always {
            echo 'Pipeline execution completed.'
        }
        success {
            echo 'SUCCESS ✅: CampusRide Backend + Frontend + Docker running!'
        }
        failure {
            echo 'FAILED ❌: Check logs above for details.'
        }
    }
}
