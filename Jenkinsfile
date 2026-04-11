pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t task-manager-app:latest .'
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    docker stop task-manager-jenkins-app || true
                    docker rm task-manager-jenkins-app || true
                    docker stop task-manager-jenkins-mongo || true
                    docker rm task-manager-jenkins-mongo || true
                    docker network create jenkins-net || true

                    docker run -d \
                        --name task-manager-jenkins-mongo \
                        --network jenkins-net \
                        -v mongo-jenkins-data:/data/db \
                        mongo:7

                    docker run -d \
                        --name task-manager-jenkins-app \
                        --network jenkins-net \
                        -p 3001:3000 \
                        -e MONGODB_URI=mongodb://task-manager-jenkins-mongo:27017/tasksdb \
                        task-manager-app:latest
                '''
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}