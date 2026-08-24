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
                git branch: 'feature/testing', url: 'https://github.com/bus57790/addressbook-devops.git'
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
                sh "docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} ."
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
        always {
            cleanWs()
        }
        failure {
            withCredentials([string(credentialsId: 'slack-webhook-url', variable: 'SLACK_URL')]) {
                script {
                    def jsonText = "{\"text\":\"❌ Pipeline Failed: ${env.JOB_NAME} [Build #${env.BUILD_NUMBER}]\"}"
                    writeFile file: 'slack.json', text: jsonText
                    sh 'curl -s -X POST -H "Content-Type: application/json" -d @slack.json "$SLACK_URL"'
                }
            }
        }
    }
}
