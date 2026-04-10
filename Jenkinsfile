pipeline {
    agent any

    options {
        timestamps()
    }

    environment {
        APP_IMAGE = 'task-manager-app'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t ${APP_IMAGE}:${BUILD_NUMBER} .'
            }
        }

        stage('Deploy with Docker Compose') {
            steps {
                sh 'docker-compose -f docker-compose-jenkins.yml down || true'
                sh 'docker-compose -f docker-compose-jenkins.yml up -d'
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}