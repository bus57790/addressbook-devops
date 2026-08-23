pipeline {
    agent any

    environment {
        APP_NAME = "addressbook-web"
        IMAGE_NAME = "local/addressbook-web:${env.BUILD_NUMBER}"
        SLACK_WEBHOOK = credentials('slack-webhook-url')
        // Ensure standard binary paths are available to Jenkins
        PATH = "/usr/local/bin:/usr/bin:/bin:${env.PATH}"
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

        stage('Deploy to Local Server') {
            steps {
                // Uses 'docker compose' (Docker V2 standard syntax)
                sh "docker compose down || docker-compose down"
                sh "docker compose up -d --build || docker-compose up -d --build"
            }
        }
    }

    post {
        failure {
            // Uses proper single-quoted JSON formatting for Slack payload
            sh '''
                curl -X POST -H 'Content-type: application/json' \
                  --data '{"text":"❌ Jenkins Pipeline Failed: '"$JOB_NAME"' [Build #'"$BUILD_NUMBER"'] failed."}' \
                  "$SLACK_WEBHOOK"
            '''
        }
    }
}
