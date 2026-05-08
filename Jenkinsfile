pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Cloning repo...'
                checkout scm
            }
        }

        stage('Start App (docker-compose)') {
            steps {
                echo 'Starting Task Orbit app + MongoDB...'
                sh '''
                    docker-compose down || true
                    docker-compose up -d --build
                    echo "Waiting for app to be ready..."
                    sleep 15
                '''
            }
        }

        stage('Build Test Image') {
            steps {
                echo 'Building Selenium test image...'
                sh 'docker build -t task-orbit-tests -f Dockerfile.test .'
            }
        }

        stage('Run Selenium Tests') {
            steps {
                echo 'Running 20 Selenium tests...'
                sh '''
                    docker rm -f task-orbit-tests || true
                    docker run --name task-orbit-tests \
                        --network host \
                        -e BASE_URL=http://localhost:3000 \
                        task-orbit-tests || true
                    docker cp task-orbit-tests:/app/test-results.xml . || true
                '''
            }
        }

        stage('Publish Test Results') {
            steps {
                junit allowEmptyResults: true, testResults: 'test-results.xml'
            }
        }
    }

    post {
        always {
            script {
                def pusherEmail = env.GIT_AUTHOR_EMAIL ?: 'qasimalik@gmail.com'
                emailext(
                    to: pusherEmail,
                    subject: "Task Orbit - Build #${env.BUILD_NUMBER}: ${currentBuild.currentResult}",
                    body: """
                        <h2>Jenkins Pipeline - Selenium Test Results</h2>
                        <p><b>Result:</b> ${currentBuild.currentResult}</p>
                        <p><b>Job:</b> ${env.JOB_NAME}</p>
                        <p><b>Build:</b> #${env.BUILD_NUMBER}</p>
                        <p><b>Triggered by:</b> ${pusherEmail}</p>
                        <p><b>Console output:</b> <a href="${env.BUILD_URL}">${env.BUILD_URL}</a></p>
                    """,
                    mimeType: 'text/html',
                    attachmentsPattern: 'test-results.xml'
                )
            }
            // Bring deployment DOWN after tests (assignment requires this)
            sh 'docker-compose down || true'
            sh 'docker rm -f task-orbit-tests || true'
        }
    }
}