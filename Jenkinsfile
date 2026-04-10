def runCommand(script, String unixCommand, String windowsCommand) {
  if (script.isUnix()) {
    script.sh unixCommand
  } else {
    script.bat windowsCommand
  }
}

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

    stage('Install Dependencies') {
      steps {
        script {
          runCommand(this, 'npm install', 'npm install')
        }
      }
    }

    stage('Verify Source') {
      steps {
        script {
          runCommand(this, 'node --check app.js', 'node --check app.js')
          runCommand(this, 'node --check models/Task.js', 'node --check models\\Task.js')
          runCommand(this, 'node --check models/User.js', 'node --check models\\User.js')
        }
      }
    }

    stage('Build Docker Image') {
      steps {
        script {
          runCommand(this, 'docker build -t ${APP_IMAGE}:${BUILD_NUMBER} .', 'docker build -t %APP_IMAGE%:%BUILD_NUMBER% .')
        }
      }
    }
  }

  post {
    always {
      cleanWs()
    }
  }
}