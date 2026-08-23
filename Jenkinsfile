pipeline {
    agent any

    environment {
        APP_NAME = "addressbook-web"
        IMAGE_NAME = "local/addressbook-web:${env.BUILD_NUMBER}"
        SONAR_SCANNER_HOME = tool 'SonarScanner'
        SLACK_WEBHOOK = credentials('slack-webhook-url')
        
        // Uncomment Twilio environment variables if configured in Jenkins Credentials
        // TWILIO_ACCOUNT_SID = credentials('twilio-sid')
        // TWILIO_AUTH_TOKEN  = credentials('twilio-token')
        // TWILIO_FROM        = '+1234567890'
        // NOTIFICATION_TO    = '+0987654321'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/bus57790/addressbook-devops.git'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube-Server') {
                    sh """
                        ${SONAR_SCANNER_HOME}/bin/sonar-scanner \
                        -Dsonar.projectKey=${APP_NAME} \
                        -Dsonar.sources=. \
                        -Dsonar.exclusions=**/*.html
                    """
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t ${IMAGE_NAME} ."
            }
        }

        stage('Trivy Security Scan') {
            steps {
                // Scans image for vulnerabilities
                sh "trivy image --severity HIGH,CRITICAL --exit-code 1 ${IMAGE_NAME}"
            }
        }

        stage('Deploy to Local Server') {
            steps {
                sh "docker-compose down"
                sh "docker-compose up -d --build"
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        success {
            script {
                // Corrected Slack Notification variable syntax
                sh """
                    curl -X POST -H 'Content-type: application/json' \
                    --data '{"text":"✅ Jenkins Pipeline Success: ${env.JOB_NAME} [Build #${env.BUILD_NUMBER}] deployed successfully."}' \
                    ${SLACK_WEBHOOK}
                """
            }
        }
        failure {
            script {
                // Corrected Slack Failure Alert variable syntax
                sh """
                    curl -X POST -H 'Content-type: application/json' \
                    --data '{"text":"❌ Jenkins Pipeline Failed: ${env.JOB_NAME} [Build #${env.BUILD_NUMBER}] failed."}' \
                    ${SLACK_WEBHOOK}
                """
            }
        }
    }
}
