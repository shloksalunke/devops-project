pipeline {
    agent any

    environment {
        // Defines CI environment variables 
        CI = 'true'
    }

    stages {
        stage('Checkout') {
            steps {
                // Checkout code from the configured Git repository
                checkout scm
            }
        }

        stage('Backend: Test') {
            steps {
                dir('backend') {
                    echo 'Setting up Python Environment and running Pytest...'
                    // Note: If Jenkins is running on Windows natively, change 'sh' to 'bat'
                    // and use 'venv\\Scripts\\activate' instead.
                    sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    # Run tests
                    pytest
                    '''
                }
            }
        }

        stage('Frontend: Lint, Build & Test') {
            steps {
                dir('frontend') {
                    echo 'Setting up Node Environment...'
                    // Note: If Jenkins is running on Windows natively, change 'sh' to 'bat'
                    sh '''
                    npm install
                    npm run lint
                    npm run test
                    npm run build
                    '''
                }
            }
        }

        stage('Docker: Build Images') {
            steps {
                echo 'Validating Docker Compose Build...'
                // This builds the production images locally as a validation check
                sh 'docker-compose -f docker-compose.prod.yml build'
            }
        }

        
        Optional Deployment Stage: 
        Uncomment this if you want to deploy the stack via Docker automatically after passing tests.
        
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                echo 'Deploying to Production...'
                sh 'docker-compose -f docker-compose.prod.yml up -d'
            }
        }
        
    }

    post {
        always {
            echo 'CI Pipeline has finished executing.'
            // You can add JUnit or Coverage parsers here
        }
        success {
            echo 'Build, Test, and Containerization successful! ✅'
        }
        failure {
            echo 'Pipeline failed! Please check the logs. ❌'
        }
    }
}
