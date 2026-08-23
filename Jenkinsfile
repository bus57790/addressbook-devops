pipeline {
    agent any

    environment {
        APP_NAME   = "addressbook-web"
        IMAGE_NAME = "local/addressbook-web"
        PATH       = "/usr/local/bin:/usr/bin:/bin:${env.PATH}"
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
                    def scannerHome = tool 'SonarScanner'
                    withSonarQubeEnv('SonarQube-Server') {
                        sh """
                            ${scannerHome}/bin/sonar-scanner \
                            -Dsonar.projectKey=${env.APP_NAME} \
                            -Dsonar.sources=. \
                            -Dsonar.exclusions=**/*.html
                        """
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Pre-format the tag string in Groovy to avoid shell string parsing errors
                    def fullImageTag = "${env.IMAGE_NAME}:${env.BUILD_NUMBER}"
                    sh "docker build -t ${fullImageTag} ."
                }
            }
        }

        stage('Deploy to Local Server') {
            steps {
                sh 'docker compose down || docker-compose down || true'
                sh 'docker compose up -d --build || docker-compose up -d --build'
            }
        }
    }

    post {
        failure {
            withCredentials([string(credentialsId: 'slack-webhook-url', variable: 'SLACK_URL')]) {
                script {
                    // Create a valid JSON object natively in Groovy
                    def slackPayload = [
                        text: "❌ Jenkins Pipeline Failed: ${env.JOB_NAME} [Build #${env.BUILD_NUMBER}] failed."
                    ]
                    
                    // Safely write to file without bash quote stripping
                    writeJSON file: 'slack.json', json: slackPayload
                    
                    // Post via curl using payload file
                    sh 'curl -X POST -H "Content-Type: application/json" -d @slack.json "$SLACK_URL"'
                }
            }
        }
    }
}
