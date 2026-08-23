pipeline {
    agent any

    environment {
        APP_NAME = "addressbook-web"
        IMAGE_NAME = "local/addressbook-web:${BUILD_NUMBER}"
        SONAR_SCANNER_HOME = tool 'SonarScanner'
        SLACK_WEBHOOK = credentials('slack-webhook-url')
        TWILIO_ACCOUNT_SID = credentials('twilio-sid')
        TWILIO_AUTH_TOKEN = credentials('twilio-token')
        TWILIO_FROM = '+1234567890'
        NOTIFICATION_TO = '+0987654321'
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
                // Fails the build if High or Critical vulnerabilities are found
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
                // Slack Notification
                sh """
                    curl -X POST -H 'Content-type: application/json' \
                    --data '{"text":"✅ Jenkins Pipeline Success: ${ENV:JOB_NAME} [Build #${ENV:BUILD_NUMBER}] deployed successfully."}' \
                    ${SLACK_WEBHOOK}
                """
                // SMS Notification via Twilio API
                sh """
                    curl -X POST "https://api.twilio.com/2010-04-01/Accounts/${TWILIO_ACCOUNT_SID}/Messages.json" \
                    --data-urlencode "From=${TWILIO_FROM}" \
                    --data-urlencode "To=${NOTIFICATION_TO}" \
                    --data-urlencode "Body=CI/CD Success: ${ENV:JOB_NAME} #${ENV:BUILD_NUMBER} deployed successfully." \
                    -u "${TWILIO_ACCOUNT_SID}:${TWILIO_AUTH_TOKEN}"
                """
            }
        }
        failure {
            script {
                // Slack Failure Alert
                sh """
                    curl -X POST -H 'Content-type: application/json' \
                    --data '{"text":"❌ Jenkins Pipeline Failed: ${ENV:JOB_NAME} [Build #${ENV:BUILD_NUMBER}] failed."}' \
                    ${SLACK_WEBHOOK}
                """
                // SMS Failure Alert
                sh """
                    curl -X POST "https://api.twilio.com/2010-04-01/Accounts/${TWILIO_ACCOUNT_SID}/Messages.json" \
                    --data-urlencode "From=${TWILIO_FROM}" \
                    --data-urlencode "To=${NOTIFICATION_TO}" \
                    --data-urlencode "Body=CI/CD Failure: ${ENV:JOB_NAME} #${ENV:BUILD_NUMBER} failed." \
                    -u "${TWILIO_ACCOUNT_SID}:${TWILIO_AUTH_TOKEN}"
                """
            }
        }
    }
}
