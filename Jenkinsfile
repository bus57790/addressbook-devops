pipeline {
    agent any

    environment {
        APP_NAME = "addressbook-web"
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
                script {
                    def imgName = "local/addressbook-web:${env.BUILD_NUMBER}"
                    // The hyphen below is standard ASCII. 
                    sh "docker build -t ${imgName} ."
                }
            }
        }

        stage('Deploy to Local Server') {
            steps {
                sh 'docker compose down || true'
                sh 'docker compose up -d --build'
            }
        }
    }

    post {
        failure {
            withCredentials([string(credentialsId: 'slack-webhook-url', variable: 'SLACK_URL')]) {
                script {
                    // 1. Construct the payload in Groovy to avoid shell quote stripping
                    def payload = '{"text":"❌ Jenkins Pipeline Failed: ' + env.JOB_NAME + ' [Build #' + env.BUILD_NUMBER + '] failed."}'
                    
                    // 2. Write it securely to a file in the workspace
                    writeFile file: 'slack_payload.json', text: payload
                    
                    // 3. Pass the file directly to curl
                    sh 'curl -X POST -H "Content-type: application/json" -d @slack_payload.json "$SLACK_URL"'
                }
            }
        }
    }
}
