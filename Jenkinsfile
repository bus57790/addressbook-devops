pipeline {
    agent any

    environment {
        APP_NAME = "addressbook-web"
        IMAGE_NAME = "local/addressbook-web:${env.BUILD_NUMBER}"
        SLACK_WEBHOOK = credentials('slack-webhook-url')
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/bus57790/addressbook-devops.git'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                script {
                    // Resolve tool inside the stage script block
                    def scannerHome = tool 'SonarScanner'
                    withSonarQubeEnv('SonarQube-Server') {
                        sh """
                            ${scannerHome}/bin/sonar-scanner \
                            -Dsonar.projectKey=${APP_NAME} \
                            -Dsonar.sources=. \
                            -Dsonar.exclusions=**/*.html
                        """
                    }
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
            sh """
                curl -X POST -H 'Content-type: application/json' \
                --data '{"text":"✅ Jenkins Pipeline Success: ${env.JOB_NAME} [Build #${env.BUILD_NUMBER}] deployed successfully."}' \
                ${env.SLACK_WEBHOOK}
            """
        }
        failure {
            sh """
                curl -X POST -H 'Content-type: application/json' \
                --data '{"text":"❌ Jenkins Pipeline Failed: ${env.JOB_NAME} [Build #${env.BUILD_NUMBER}] failed."}' \
                ${env.SLACK_WEBHOOK}
            """
        }
    }
}
